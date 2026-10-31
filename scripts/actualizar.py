"""Construye data/estado.json: condiciones recientes por departamento,
anomalias respecto de la normal 1991-2020 y nivel de alerta.

Es el script que corre el flujo automatico diario.
"""
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from clima_api import pedir_json
from config import API_ACTUAL, DEPARTAMENTOS

RAIZ = Path(__file__).resolve().parent.parent
LIMA = timezone(timedelta(hours=-5))

VENTANA_DIAS = 30  # dias previos usados para comparar contra la normal
PAUSA_DEPARTAMENTO = 3  # s de cortesia con la API publica


def pedir(lat, lon):
    return pedir_json(API_ACTUAL, {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "timezone": "America/Lima",
        "past_days": VENTANA_DIAS,
        "forecast_days": 7,
    }, timeout=90)


def anomalia_pct(observado, normal):
    """Anomalia en % de la normal. Sin normal, o con normal cero (meses secos
    del desierto costero), el porcentaje no esta definido."""
    if normal is None or normal <= 0:
        return None
    return round((observado - normal) / normal * 100, 1)


def nivel_alerta(anom_pp, anom_temp, zona):
    """Nivel cualitativo 0-3. En costa norte el riesgo dominante en fase
    calida es el exceso de lluvia; en sierra sur y costa centro-sur, el
    deficit. Ver docs/METODOLOGIA.md: son umbrales provisionales y deben
    calibrarse con datos de SENAMHI y de emergencias de INDECI."""
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


def main():
    archivo_normales = RAIZ / "data" / "normales.json"
    if not archivo_normales.exists():
        raise SystemExit(
            f"falta {archivo_normales}: correr primero "
            "PYTHONPATH=scripts python3 scripts/calcular_normales.py")
    normales = json.loads(archivo_normales.read_text())["normales"]

    sin_normal = [d["nombre"] for d in DEPARTAMENTOS if d["nombre"] not in normales]
    if sin_normal:
        print(f"aviso: sin normal climatica para {', '.join(sin_normal)}; "
              "sus anomalias saldran nulas", flush=True)

    hoy = datetime.now(LIMA)
    mes = f"{hoy.month:02d}"

    registros = []
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
        # normal mensual escalada a la ventana usada
        pp_mes = norm.get("precipitacion_mensual_mm")
        pp_norm = pp_mes * VENTANA_DIAS / 30 if pp_mes is not None else None
        tx_norm = norm.get("tmax_media_c")

        a_pp = anomalia_pct(pp_obs, pp_norm)
        a_tx = (round(tx_obs - tx_norm, 2)
                if tx_obs is not None and tx_norm is not None else None)

        registros.append({
            **dep,
            "precipitacion_obs_mm": pp_obs,
            "precipitacion_normal_mm": (round(pp_norm, 1)
                                        if pp_norm is not None else None),
            "anomalia_precipitacion_pct": a_pp,
            "tmax_obs_c": tx_obs,
            "tmax_normal_c": tx_norm,
            "anomalia_tmax_c": a_tx,
            "pronostico_7d_mm": round(sum(
                x for x in d["precipitation_sum"][VENTANA_DIAS:] if x is not None), 1),
            "nivel_alerta": nivel_alerta(a_pp, a_tx, dep["zona"]),
        })
        time.sleep(PAUSA_DEPARTAMENTO)

    oni = json.loads((RAIZ / "data" / "oni.json").read_text())
    salida = {
        "actualizado": hoy.isoformat(timespec="minutes"),
        "ventana_dias": VENTANA_DIAS,
        "oni": oni["ultimo"],
        "departamentos": registros,
    }
    (RAIZ / "data" / "estado.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=2))
    print("data/estado.json actualizado")


if __name__ == "__main__":
    main()
