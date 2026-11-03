"""Construye data/estado.json: condiciones recientes por departamento,
anomalias respecto de la normal 1991-2020, nivel de alerta y frescura de cada
fuente.

Es el script que corre el flujo automatico (cada 6 horas). Esto NO es tiempo
real: cada fuente tiene su propio rezago, que queda registrado en el bloque
"fuentes" del JSON. Ver docs/METODOLOGIA.md, seccion de frescura.
"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from clima_api import pedir_json
from config import (ALTITUD_CAPITAL_M, API_ACTUAL, DEPARTAMENTOS,
                    UMBRAL_NORMAL_BAJA_MM)

RAIZ = Path(__file__).resolve().parent.parent
LIMA = timezone(timedelta(hours=-5))

VENTANA_DIAS = 30  # dias previos usados para comparar contra la normal
PAUSA_DEPARTAMENTO = 3  # s de cortesia con la API publica


def pedir(lat, lon):
    """Una sola consulta trae: agregado diario de 30 dias + 7 de pronostico,
    horario del dia en curso y condiciones actuales (la API las refresca cada
    hora). La altitud del modelo viene en el campo 'elevation'."""
    return pedir_json(API_ACTUAL, {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "hourly": "precipitation,temperature_2m",
        "current": "temperature_2m,precipitation",
        "timezone": "America/Lima",
        "past_days": VENTANA_DIAS,
        "forecast_days": 7,
    }, timeout=90)


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


def leer_normales():
    archivo = RAIZ / "data" / "normales.json"
    if not archivo.exists():
        raise SystemExit(
            f"falta {archivo}: correr primero "
            "PYTHONPATH=scripts python3 scripts/calcular_normales.py")
    return json.loads(archivo.read_text())["normales"]


def main():
    normales = leer_normales()
    sin_normal = [d["nombre"] for d in DEPARTAMENTOS if d["nombre"] not in normales]
    if sin_normal:
        print(f"aviso: sin normal climatica para {', '.join(sin_normal)}; "
              "sus anomalias saldran nulas", flush=True)

    hoy = datetime.now(LIMA)
    mes = f"{hoy.month:02d}"

    registros = []
    ultima_fecha = {}
    for i, dep in enumerate(DEPARTAMENTOS, 1):
        print(f"[{i}/{len(DEPARTAMENTOS)}] {dep['nombre']}", flush=True)
        datos = pedir(dep["lat"], dep["lon"])
        d = datos["daily"]

        pasado = slice(0, VENTANA_DIAS)
        pp = [x for x in d["precipitation_sum"][pasado] if x is not None]
        tx = [x for x in d["temperature_2m_max"][pasado] if x is not None]

        pp_obs = round(sum(pp), 1)
        tx_obs = round(sum(tx) / len(tx), 2) if tx else None

        norm = normales.get(dep["nombre"], {}).get(mes, {})
        # normal mensual de lluvia; la ventana de 30 dias equivale a un mes
        pp_mes = norm.get("precipitacion_mensual_mm")
        pp_norm = pp_mes * VENTANA_DIAS / 30 if pp_mes is not None else None
        tx_norm = norm.get("tmax_media_c")

        # Limitacion 4: con normal mensual por debajo del umbral, el porcentaje
        # no informa. Se publica el acumulado en mm y la lluvia no suma al nivel.
        normal_baja = pp_mes is not None and pp_mes < UMBRAL_NORMAL_BAJA_MM
        a_pp = None if normal_baja else anomalia_pct(pp_obs, pp_norm)
        a_pp_mm = (round(pp_obs - pp_norm, 1)
                   if pp_norm is not None else None)
        a_tx = (round(tx_obs - tx_norm, 2)
                if tx_obs is not None and tx_norm is not None else None)

        elevacion_modelo = datos.get("elevation")
        altitud_capital = ALTITUD_CAPITAL_M[dep["nombre"]]
        dia = condiciones_del_dia(datos, hoy)

        ultima_fecha = {
            "observado_30d_hasta": d["time"][VENTANA_DIAS - 1],
            "pronostico_hasta": d["time"][-1],
            "condiciones_actuales": dia["hora_condiciones"],
        }

        registros.append({
            **dep,
            "altitud_capital_m": altitud_capital,
            "elevacion_modelo_m": elevacion_modelo,
            "diferencia_altitud_m": (round(elevacion_modelo - altitud_capital)
                                     if elevacion_modelo is not None else None),
            "precipitacion_obs_mm": pp_obs,
            "precipitacion_normal_mm": (round(pp_norm, 1)
                                        if pp_norm is not None else None),
            "normal_baja": normal_baja,
            "anomalia_precipitacion_pct": a_pp,
            "anomalia_precipitacion_mm": a_pp_mm,
            "tmax_obs_c": tx_obs,
            "tmax_normal_c": tx_norm,
            "anomalia_tmax_c": a_tx,
            "pronostico_7d_mm": round(sum(
                x for x in d["precipitation_sum"][VENTANA_DIAS:] if x is not None), 1),
            **dia,
            "nivel_alerta": nivel_alerta(a_pp, a_tx, dep["zona"]),
        })
        time.sleep(PAUSA_DEPARTAMENTO)

    oni = json.loads((RAIZ / "data" / "oni.json").read_text())
    ultimo_oni = oni["ultimo"]
    semanal = oni.get("semanal")

    fuentes = {
        "normales": {
            "periodo": "1991-2020",
            "origen": "ERA5 via Open-Meteo Archive API; climatologia fija",
            "frecuencia": "se calcula una vez",
        },
        "lluvia_30_dias": {
            "hasta": ultima_fecha["observado_30d_hasta"],
            "origen": "API de pronostico de Open-Meteo (past_days)",
            "frecuencia": "cada 6 horas",
        },
        "condiciones_actuales": {
            "hora": ultima_fecha["condiciones_actuales"],
            "origen": "API de pronostico de Open-Meteo (current / hourly)",
            "frecuencia": "la API refresca cada hora",
        },
        "pronostico_7_dias": {
            "hasta": ultima_fecha["pronostico_hasta"],
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
    }

    salida = {
        "actualizado": hoy.isoformat(timespec="minutes"),
        "ventana_dias": VENTANA_DIAS,
        "umbral_normal_baja_mm": UMBRAL_NORMAL_BAJA_MM,
        "oni": ultimo_oni,
        "tsm_semanal": semanal,
        "fuentes": fuentes,
        "departamentos": registros,
    }
    (RAIZ / "data" / "estado.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2))
    print("data/estado.json actualizado")


if __name__ == "__main__":
    main()
