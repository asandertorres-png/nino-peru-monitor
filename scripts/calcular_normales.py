"""Calcula las normales climaticas 1991-2020 por departamento.

Se ejecuta UNA SOLA VEZ (o cada varios anios). El resultado se versiona en
data/normales.json y el flujo diario solo lo lee. Fuente: reanalisis ERA5 via
la API de archivo de Open-Meteo.

La corrida es lenta por diseno: son 25 departamentos x 6 tramos de 5 anios,
con pausas entre pedidos para no chocar con el limite de uso de la API
publica. Contando reintentos puede tomar entre 30 y 90 minutos.

Si la corrida se corta, el avance queda en data/.normales_parcial.json y la
siguiente invocacion retoma desde el departamento que faltaba. Con
--reiniciar se descarta ese avance y se empieza de cero.
"""
import calendar
import json
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from clima_api import pedir_json, rate_limits_vistos
from config import API_ARCHIVO, DEPARTAMENTOS, NORMAL_FIN, NORMAL_INICIO

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "normales.json"
PARCIAL = RAIZ / "data" / ".normales_parcial.json"

BLOQUE_ANIOS = 5  # la API corta transferencias muy largas: se pide por tramos

# Pausas de cortesia. La API publica tolera mal la consulta seguida, y el
# costo de una pausa larga es mucho menor que el de un 429 a mitad de corrida.
PAUSA_TRAMO = 8          # s entre tramos de un mismo departamento
PAUSA_DEPARTAMENTO = 25  # s entre departamentos
PAUSA_EXTRA_POR_429 = 30 # s que se suman a la pausa por cada 429 acumulado
PAUSA_DEPARTAMENTO_MAX = 300

# Un mes-anio entra en la normal de lluvia si tiene al menos esta fraccion de
# sus dias; su acumulado se escala al largo completo del mes. Meses con menos
# cobertura se descartan: escalarlos amplificaria el hueco.
COBERTURA_MINIMA_MES = 0.9

MESES = [f"{m:02d}" for m in range(1, 13)]


def _dias_esperados():
    """Dias calendario del periodo de normales, para detectar series cortas."""
    ini = date.fromisoformat(NORMAL_INICIO)
    fin = date.fromisoformat(NORMAL_FIN)
    return (fin - ini).days + 1


def _pausa_entre_departamentos():
    """Pausa adaptativa: crece con los 429 que ya devolvio la API."""
    return min(PAUSA_DEPARTAMENTO_MAX,
               PAUSA_DEPARTAMENTO + PAUSA_EXTRA_POR_429 * rate_limits_vistos())


def pedir(lat, lon):
    """Descarga la serie diaria completa en tramos y los concatena."""
    anio_ini, anio_fin = int(NORMAL_INICIO[:4]), int(NORMAL_FIN[:4])
    acumulado = {"time": [], "precipitation_sum": [],
                 "temperature_2m_max": [], "temperature_2m_min": []}

    a = anio_ini
    while a <= anio_fin:
        b = min(a + BLOQUE_ANIOS - 1, anio_fin)
        datos = pedir_json(API_ARCHIVO, {
            "latitude": lat,
            "longitude": lon,
            "start_date": f"{a}-01-01",
            "end_date": f"{b}-12-31",
            "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
            "timezone": "America/Lima",
        })
        if "daily" not in datos:
            raise RuntimeError(f"respuesta sin bloque 'daily' para {a}-{b}")
        for clave in acumulado:
            acumulado[clave].extend(datos["daily"][clave])
        print(f"    {a}-{b} listo ({len(datos['daily']['time'])} dias)",
              flush=True)
        if b < anio_fin:
            time.sleep(PAUSA_TRAMO)
        a = b + 1

    faltan = _dias_esperados() - len(acumulado["time"])
    if faltan > 0:
        raise RuntimeError(
            f"serie incompleta: faltan {faltan} dias de "
            f"{_dias_esperados()} esperados")
    return {"daily": acumulado}


def normales_mensuales(datos):
    """Devuelve, por mes del anio, la precipitacion mensual media y la
    temperatura media de maximas y minimas del periodo 1991-2020.

    La normal de lluvia es la media de los acumulados mensuales de cada anio,
    no la media diaria: un mes con dias faltantes tiene un acumulado
    subestimado, asi que se usa solo si cubre al menos COBERTURA_MINIMA_MES de
    sus dias y se escala al largo completo del mes. El numero de anios que
    quedaron detras de cada normal se guarda en el JSON.
    """
    lluvia = defaultdict(float)
    dias_con_lluvia = defaultdict(int)
    tmax = defaultdict(list)
    tmin = defaultdict(list)

    d = datos["daily"]
    for fecha, pp, tx, tn in zip(d["time"], d["precipitation_sum"],
                                 d["temperature_2m_max"], d["temperature_2m_min"]):
        anio, mes = fecha[:4], fecha[5:7]
        if pp is not None:
            lluvia[(anio, mes)] += pp
            dias_con_lluvia[(anio, mes)] += 1
        if tx is not None:
            tmax[mes].append(tx)
        if tn is not None:
            tmin[mes].append(tn)

    totales_por_mes = defaultdict(list)
    for (anio, mes), total in lluvia.items():
        largo = calendar.monthrange(int(anio), int(mes))[1]
        presentes = dias_con_lluvia[(anio, mes)]
        if presentes >= COBERTURA_MINIMA_MES * largo:
            totales_por_mes[mes].append(total * largo / presentes)

    resultado = {}
    for mes in MESES:
        if not totales_por_mes[mes] or not tmax[mes] or not tmin[mes]:
            raise RuntimeError(
                f"sin datos suficientes para el mes {mes}: "
                f"{len(totales_por_mes[mes])} anios de lluvia utilizables, "
                f"{len(tmax[mes])} dias con tmax")
        resultado[mes] = {
            "precipitacion_mensual_mm": round(
                sum(totales_por_mes[mes]) / len(totales_por_mes[mes]), 2),
            "tmax_media_c": round(sum(tmax[mes]) / len(tmax[mes]), 2),
            "tmin_media_c": round(sum(tmin[mes]) / len(tmin[mes]), 2),
            "anios_usados_precipitacion": len(totales_por_mes[mes]),
        }
    return resultado


def _cargar_parcial(reiniciar):
    if reiniciar or not PARCIAL.exists():
        return {}
    try:
        previo = json.loads(PARCIAL.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"aviso: no pude leer {PARCIAL.name} ({e}); empiezo de cero")
        return {}
    if previo:
        print(f"retomo avance previo: {len(previo)} departamentos ya listos")
    return previo


def _escribir(resultado, destino):
    destino.write_text(json.dumps({
        "periodo": f"{NORMAL_INICIO[:4]}-{NORMAL_FIN[:4]}",
        "fuente": "ERA5 via Open-Meteo Archive API",
        "normales": resultado,
    }, ensure_ascii=False, indent=2))


def main():
    reiniciar = "--reiniciar" in sys.argv
    resultado = _cargar_parcial(reiniciar)

    pendientes = [d for d in DEPARTAMENTOS if d["nombre"] not in resultado]
    total = len(DEPARTAMENTOS)

    for n, dep in enumerate(pendientes, 1):
        hechos = total - len(pendientes) + n
        print(f"[{hechos}/{total}] {dep['nombre']} ({dep['capital']})...",
              flush=True)
        datos = pedir(dep["lat"], dep["lon"])
        resultado[dep["nombre"]] = normales_mensuales(datos)

        # checkpoint: una corrida de una hora no deberia perderse por un corte
        PARCIAL.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))

        if n < len(pendientes):
            pausa = _pausa_entre_departamentos()
            print(f"    pausa de {pausa}s antes del siguiente departamento",
                  flush=True)
            time.sleep(pausa)

    _escribir(resultado, DESTINO)
    PARCIAL.unlink(missing_ok=True)
    print(f"Guardado en {DESTINO} ({len(resultado)} departamentos, "
          f"{rate_limits_vistos()} HTTP 429 durante la corrida)")
    print("Verificar con: PYTHONPATH=scripts python3 scripts/verificar_normales.py")


if __name__ == "__main__":
    main()
