"""Construye el estado actual por departamento o por provincia: condiciones
recientes, anomalias respecto de la normal 1991-2020, nivel de alerta y
frescura de cada fuente.

    PYTHONPATH=scripts python3 scripts/actualizar.py                    # data/estado.json
    PYTHONPATH=scripts python3 scripts/actualizar.py --nivel provincia  # data/estado_provincias.json

Es el script que corre el flujo automatico (cada 6 horas). Esto NO es tiempo
real: cada fuente tiene su propio rezago, registrado en el bloque "fuentes".
Las unidades sin normal (listadas en "sin_datos" del archivo de normales)
salen con las condiciones del dia pero sin anomalias ni alerta.
"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from clima_api import ErrorApi, pedir_lote
from config import ALTITUD_CAPITAL_M, API_ACTUAL, UMBRAL_NORMAL_BAJA_MM
from niveles import clave, nivel_desde_argv, rutas, unidades

RAIZ = Path(__file__).resolve().parent.parent
LIMA = timezone(timedelta(hours=-5))

VENTANA_DIAS = 30  # dias previos usados para comparar contra la normal
LOTE = {"departamento": 1, "provincia": 25}  # puntos por peticion
PAUSA_LOTE = 3  # s de cortesia con la API publica

PARAMS = {
    "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
    "hourly": "precipitation,temperature_2m",
    "current": "temperature_2m,precipitation",
    "timezone": "America/Lima",
    "past_days": VENTANA_DIAS,
    "forecast_days": 7,
}


def pedir(puntos):
    """Devuelve (resultado | None, motivo | None) por punto. Un lote que falla
    por error de pedido se reintenta punto por punto."""
    try:
        return [(r, None) for r in pedir_lote(API_ACTUAL, PARAMS, puntos, timeout=90)]
    except ErrorApi as e:
        if len(puntos) == 1:
            return [(None, str(e))]
        print(f"    lote fallo ({e}); reintento punto por punto", flush=True)
    salida = []
    for p in puntos:
        try:
            salida.append((pedir_lote(API_ACTUAL, PARAMS, [p], timeout=90)[0], None))
        except ErrorApi as e:
            salida.append((None, str(e)))
        time.sleep(PAUSA_LOTE)
    return salida


def anomalia_pct(observado, normal):
    """Anomalia en % de la normal. No se calcula si la normal es nula o baja:
    ver UMBRAL_NORMAL_BAJA_MM en config.py (limitacion 4 de METODOLOGIA.md)."""
    if normal is None or normal <= 0:
        return None
    return round((observado - normal) / normal * 100, 1)


def nivel_alerta(anom_pp, anom_temp, zona):
    """Nivel cualitativo 0-3. En costa norte el riesgo dominante en fase
    calida es el exceso de lluvia; en sierra sur y costa centro-sur, el
    deficit. Si la anomalia de lluvia es None (normal baja o sin normal), la
    lluvia no suma al nivel: solo cuenta la anomalia termica.
    Ver docs/METODOLOGIA.md: son umbrales provisionales."""
    riesgo = 0
    if zona == "costa_norte":
        if anom_pp is not None:
            if anom_pp > 200:
                riesgo = 3
            elif anom_pp > 100:
                riesgo = 2
            elif anom_pp > 50:
                riesgo = 1
    else:
        if anom_pp is not None:
            if anom_pp < -60:
                riesgo = 3
            elif anom_pp < -40:
                riesgo = 2
            elif anom_pp < -20:
                riesgo = 1
    if anom_temp is not None and anom_temp > 2.0:
        riesgo = min(3, riesgo + 1)
    return riesgo


def condiciones_del_dia(datos, ahora):
    """Lluvia acumulada hoy (horas ya transcurridas) y temperatura actual."""
    h = datos.get("hourly", {})
    hoy = ahora.strftime("%Y-%m-%d")
    limite = ahora.strftime("%Y-%m-%dT%H:%M")
    lluvia = [p for t, p in zip(h.get("time", []), h.get("precipitation", []))
              if t.startswith(hoy) and t <= limite and p is not None]
    cur = datos.get("current", {})
    return {
        "lluvia_hoy_mm": round(sum(lluvia), 1),
        "temperatura_actual_c": cur.get("temperature_2m"),
        "hora_condiciones": cur.get("time"),
    }


def leer_normales(nivel):
    archivo = rutas(nivel)["normales"]
    if not archivo.exists():
        raise SystemExit(
            f"falta {archivo}: correr primero PYTHONPATH=scripts python3 "
            f"scripts/calcular_normales.py"
            f"{'' if nivel == 'departamento' else ' --nivel provincia'}")
    return json.loads(archivo.read_text())


def registro(nivel, u, datos, motivo, normales, sin_datos, mes, hoy):
    k = clave(nivel, u)
    base = {**u}
    base.pop("nombre_geo", None)
    if nivel == "departamento":
        base["altitud_capital_m"] = ALTITUD_CAPITAL_M[u["nombre"]]

    if datos is None or "daily" not in datos:
        return {**base, "sin_datos": True,
                "motivo_sin_datos": motivo or "respuesta sin bloque 'daily'",
                "nivel_alerta": None}, None

    d = datos["daily"]
    pasado = slice(0, VENTANA_DIAS)
    pp = [x for x in d["precipitation_sum"][pasado] if x is not None]
    tx = [x for x in d["temperature_2m_max"][pasado] if x is not None]
    pp_obs = round(sum(pp), 1)
    tx_obs = round(sum(tx) / len(tx), 2) if tx else None

    elevacion = datos.get("elevation")
    zona = u["zona"]
    if nivel == "provincia":
        from provincias import zona_por_altitud
        zona = zona_por_altitud(zona, u["lat"], elevacion)

    norm = normales.get(k, {}).get(mes, {})
    pp_mes = norm.get("precipitacion_mensual_mm")
    pp_norm = pp_mes * VENTANA_DIAS / 30 if pp_mes is not None else None
    tx_norm = norm.get("tmax_media_c")

    normal_baja = pp_mes is not None and pp_mes < UMBRAL_NORMAL_BAJA_MM
    a_pp = None if normal_baja else anomalia_pct(pp_obs, pp_norm)
    a_pp_mm = round(pp_obs - pp_norm, 1) if pp_norm is not None else None
    a_tx = (round(tx_obs - tx_norm, 2)
            if tx_obs is not None and tx_norm is not None else None)

    fila = {
        **base,
        "zona": zona,
        "zona_heredada": u["zona"],
        "sin_normal": k in sin_datos,
        "motivo_sin_normal": sin_datos.get(k),
        "elevacion_modelo_m": elevacion,
        "precipitacion_obs_mm": pp_obs,
        "precipitacion_normal_mm": round(pp_norm, 1) if pp_norm is not None else None,
        "normal_baja": normal_baja,
        "anomalia_precipitacion_pct": a_pp,
        "anomalia_precipitacion_mm": a_pp_mm,
        "tmax_obs_c": tx_obs,
        "tmax_normal_c": tx_norm,
        "anomalia_tmax_c": a_tx,
        "pronostico_7d_mm": round(sum(
            x for x in d["precipitation_sum"][VENTANA_DIAS:] if x is not None), 1),
        **condiciones_del_dia(datos, hoy),
        "nivel_alerta": nivel_alerta(a_pp, a_tx, zona) if k in normales else None,
    }
    if nivel == "departamento":
        fila["diferencia_altitud_m"] = (round(elevacion - base["altitud_capital_m"])
                                       if elevacion is not None else None)
    fechas = {
        "observado_30d_hasta": d["time"][VENTANA_DIAS - 1],
        "pronostico_hasta": d["time"][-1],
        "condiciones_actuales": fila["hora_condiciones"],
    }
    return fila, fechas


def main():
    nivel = nivel_desde_argv()
    doc = leer_normales(nivel)
    normales, sin_datos = doc["normales"], doc.get("sin_datos", {})
    todas = unidades(nivel)
    sin_normal = [u["nombre"] for u in todas
                  if clave(nivel, u) not in normales and clave(nivel, u) not in sin_datos]
    if sin_normal:
        print(f"aviso: sin normal climatica para {', '.join(sin_normal[:10])}; "
              "sus anomalias saldran nulas", flush=True)

    hoy = datetime.now(LIMA)
    mes = f"{hoy.month:02d}"
    lote = LOTE[nivel]

    registros, ultima_fecha = [], {}
    for i in range(0, len(todas), lote):
        grupo = todas[i:i + lote]
        print(f"[{i + len(grupo)}/{len(todas)}] "
              + ", ".join(u["nombre"] for u in grupo), flush=True)
        for u, (datos, motivo) in zip(grupo, pedir(grupo)):
            fila, fechas = registro(nivel, u, datos, motivo, normales, sin_datos, mes, hoy)
            registros.append(fila)
            if fechas:
                ultima_fecha = fechas
        time.sleep(PAUSA_LOTE)

    oni = json.loads((RAIZ / "data" / "oni.json").read_text())
    ultimo_oni = oni["ultimo"]
    semanal = oni.get("semanal")
    icen = oni.get("icen")

    fuentes = {
        "normales": {
            "periodo": "1991-2020",
            "origen": doc.get("fuente", "ERA5 via Open-Meteo Archive API") + "; climatologia fija",
            "frecuencia": "se calcula una vez",
        },
        "lluvia_30_dias": {
            "hasta": ultima_fecha.get("observado_30d_hasta"),
            "origen": "API de pronostico de Open-Meteo (past_days)",
            "frecuencia": "cada 6 horas",
        },
        "condiciones_actuales": {
            "hora": ultima_fecha.get("condiciones_actuales"),
            "origen": "API de pronostico de Open-Meteo (current / hourly)",
            "frecuencia": "la API refresca cada hora",
        },
        "pronostico_7_dias": {
            "hasta": ultima_fecha.get("pronostico_hasta"),
            "origen": "API de pronostico de Open-Meteo",
            "frecuencia": "cada 6 horas",
        },
        "oni": {
            "trimestre": f"{ultimo_oni['trimestre']} {ultimo_oni['anio']}",
            "origen": "NOAA CPC, ONI",
            "frecuencia": "mensual (trimestral movil)",
        },
        "tsm_semanal": ({
            "semana_centrada": semanal["semana_centrada"],
            "origen": "NOAA CPC, Nino 3.4 semanal (semana centrada)",
            "frecuencia": "semanal, los lunes",
        } if semanal else None),
        "icen": ({
            "mes_central": f"{icen['anio']}-{icen['mes']:02d}",
            "origen": "ENFEN/IGP, ICEN (Nino 1+2)",
            "frecuencia": "mensual; los ultimos meses son preliminares",
        } if icen else None),
    }

    sin = sum(1 for r in registros if r.get("sin_datos") or r.get("sin_normal"))
    try:
        from lectura import cargar_gasto, cargar_ipc, cargar_sensibilidad, lectura_automatica
        lectura = lectura_automatica(oni, registros, nivel, hoy, cargar_sensibilidad(nivel), cargar_gasto(), cargar_ipc())
    except Exception as exc:  # la lectura nunca debe tumbar la corrida de datos
        print(f"aviso: la lectura automatica fallo ({exc}); se publica sin ella", flush=True)
        lectura = None
    salida = {
        "actualizado": hoy.isoformat(timespec="minutes"),
        "nivel": nivel,
        "ventana_dias": VENTANA_DIAS,
        "umbral_normal_baja_mm": UMBRAL_NORMAL_BAJA_MM,
        "oni": ultimo_oni,
        "tsm_semanal": semanal,
        "icen": icen,
        "icen_error": oni.get("icen_error"),
        "lectura": lectura,
        "fuentes": fuentes,
        "unidades_sin_datos": sin,
        "departamentos" if nivel == "departamento" else "provincias": registros,
    }
    destino = rutas(nivel)["estado"]
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2))
    print(f"{destino.relative_to(RAIZ)} actualizado ({len(registros)} unidades, {sin} sin datos)")


if __name__ == "__main__":
    main()
