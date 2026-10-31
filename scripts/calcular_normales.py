"""Calcula las normales climaticas 1991-2020 por departamento.

Se ejecuta UNA SOLA VEZ (o cada varios anios). El resultado se versiona en
data/normales.json y el flujo diario solo lo lee. Fuente: reanalisis ERA5 via
la API de archivo de Open-Meteo.
"""
import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from config import API_ARCHIVO, DEPARTAMENTOS, NORMAL_FIN, NORMAL_INICIO

RAIZ = Path(__file__).resolve().parent.parent


BLOQUE_ANIOS = 5  # la API corta transferencias muy largas: se pide por tramos


def _pedir_tramo(lat, lon, inicio, fin, intentos=6):
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "start_date": inicio,
        "end_date": fin,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "timezone": "America/Lima",
    })
    url = f"{API_ARCHIVO}?{params}"
    for intento in range(1, intentos + 1):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if intento == intentos:
                raise
            # 429 = limite de la API publica: conviene esperar bastante mas
            es_429 = "429" in str(e)
            espera = (60 * intento) if es_429 else (5 * intento)
            print(f"    reintento {intento} ({type(e).__name__}), espero {espera}s",
                  flush=True)
            time.sleep(espera)


def pedir(lat, lon):
    """Descarga la serie completa en tramos y los concatena."""
    anio_ini, anio_fin = int(NORMAL_INICIO[:4]), int(NORMAL_FIN[:4])
    acumulado = {"time": [], "precipitation_sum": [],
                 "temperature_2m_max": [], "temperature_2m_min": []}

    a = anio_ini
    while a <= anio_fin:
        b = min(a + BLOQUE_ANIOS - 1, anio_fin)
        datos = _pedir_tramo(lat, lon, f"{a}-01-01", f"{b}-12-31")
        for clave in acumulado:
            acumulado[clave].extend(datos["daily"][clave])
        print(f"    {a}-{b} listo", flush=True)
        time.sleep(3)
        a = b + 1

    return {"daily": acumulado}


def normales_mensuales(datos):
    """Devuelve, por mes del anio, la precipitacion mensual media y la
    temperatura media de maximas y minimas."""
    lluvia_por_anio_mes = defaultdict(float)
    tmax = defaultdict(list)
    tmin = defaultdict(list)

    d = datos["daily"]
    for fecha, pp, tx, tn in zip(d["time"], d["precipitation_sum"],
                                 d["temperature_2m_max"], d["temperature_2m_min"]):
        anio, mes = fecha[:4], fecha[5:7]
        if pp is not None:
            lluvia_por_anio_mes[(anio, mes)] += pp
        if tx is not None:
            tmax[mes].append(tx)
        if tn is not None:
            tmin[mes].append(tn)

    lluvia_mes = defaultdict(list)
    for (_, mes), total in lluvia_por_anio_mes.items():
        lluvia_mes[mes].append(total)

    return {
        mes: {
            "precipitacion_mensual_mm": round(sum(v) / len(v), 2),
            "tmax_media_c": round(sum(tmax[mes]) / len(tmax[mes]), 2),
            "tmin_media_c": round(sum(tmin[mes]) / len(tmin[mes]), 2),
        }
        for mes, v in sorted(lluvia_mes.items())
    }


def main():
    resultado = {}
    for i, dep in enumerate(DEPARTAMENTOS, 1):
        print(f"[{i}/{len(DEPARTAMENTOS)}] {dep['nombre']}...", flush=True)
        datos = pedir(dep["lat"], dep["lon"])
        resultado[dep["nombre"]] = normales_mensuales(datos)
        time.sleep(5)  # cortesia con la API publica

    destino = RAIZ / "data" / "normales.json"
    destino.write_text(json.dumps({
        "periodo": f"{NORMAL_INICIO[:4]}-{NORMAL_FIN[:4]}",
        "fuente": "ERA5 via Open-Meteo Archive API",
        "normales": resultado,
    }, ensure_ascii=False, indent=2))
    print(f"Guardado en {destino}")


if __name__ == "__main__":
    main()
