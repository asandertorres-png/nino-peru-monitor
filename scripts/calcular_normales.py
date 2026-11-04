"""Calcula las normales climaticas 1991-2020 por departamento o por provincia.

    PYTHONPATH=scripts python3 scripts/calcular_normales.py                    # 25 departamentos
    PYTHONPATH=scripts python3 scripts/calcular_normales.py --nivel provincia  # 195 provincias

Se ejecuta UNA SOLA VEZ (o cada varios anios). El resultado se versiona en
data/normales.json (o data/normales_provincias.json) y el flujo periodico solo
lo lee. Fuente: reanalisis ERA5 via la API de archivo de Open-Meteo (para
provincias, ERA5-Land, de ~9 km, ver MODELO_ARCHIVO en config.py).

La corrida es lenta por diseno: varios puntos por peticion, en tramos de 5
anios, con pausas para no chocar con el limite de uso de la API publica. Si se
corta, el avance queda en un checkpoint y la siguiente invocacion retoma;
--reiniciar lo descarta.

Unidades sin informacion: si la API no devuelve serie para un punto (o la
devuelve incompleta), esa unidad se registra en "sin_datos" con el motivo y
la corrida sigue. No se inventa ningun valor.
"""
import calendar
import json
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from clima_api import ErrorApi, pedir_lote, rate_limits_vistos
from config import API_ARCHIVO, MODELO_ARCHIVO, NORMAL_FIN, NORMAL_INICIO
from niveles import clave, nivel_desde_argv, rutas, unidades

RAIZ = Path(__file__).resolve().parent.parent

BLOQUE_ANIOS = 5  # la API corta transferencias muy largas: se pide por tramos
LOTE = {"departamento": 5, "provincia": 10}  # puntos por peticion

# Pausas de cortesia. La API publica tolera mal la consulta seguida, y el
# costo de una pausa larga es mucho menor que el de un 429 a mitad de corrida.
PAUSA_TRAMO = 8          # s entre tramos de un mismo lote
PAUSA_LOTE = 25          # s entre lotes
PAUSA_EXTRA_POR_429 = 30 # s que se suman a la pausa por cada 429 acumulado
PAUSA_LOTE_MAX = 300

# Un mes-anio entra en la normal de lluvia si tiene al menos esta fraccion de
# sus dias; su acumulado se escala al largo completo del mes.
COBERTURA_MINIMA_MES = 0.9

MESES = [f"{m:02d}" for m in range(1, 13)]
VARIABLES = ("precipitation_sum", "temperature_2m_max", "temperature_2m_min")


def _dias_esperados():
    ini = date.fromisoformat(NORMAL_INICIO)
    fin = date.fromisoformat(NORMAL_FIN)
    return (fin - ini).days + 1


def _pausa_entre_lotes():
    return min(PAUSA_LOTE_MAX,
               PAUSA_LOTE + PAUSA_EXTRA_POR_429 * rate_limits_vistos())


def _params(a, b, nivel):
    p = {
        "start_date": f"{a}-01-01",
        "end_date": f"{b}-12-31",
        "daily": ",".join(VARIABLES),
        "timezone": "America/Lima",
    }
    if MODELO_ARCHIVO.get(nivel):
        p["models"] = MODELO_ARCHIVO[nivel]
    return p


def _pedir_tramo(puntos, a, b, nivel):
    """Devuelve (resultados, errores) alineados con puntos. Si el lote entero
    falla por un error de pedido, reintenta punto por punto para que una
    coordenada mala no arrastre a las demas."""
    try:
        return pedir_lote(API_ARCHIVO, _params(a, b, nivel), puntos), [None] * len(puntos)
    except ErrorApi as e:
        if len(puntos) == 1:
            return [None], [str(e)]
        print(f"    lote fallo ({e}); reintento punto por punto", flush=True)
    resultados, errores = [], []
    for p in puntos:
        try:
            resultados.append(pedir_lote(API_ARCHIVO, _params(a, b, nivel), [p])[0])
            errores.append(None)
        except ErrorApi as e:
            resultados.append(None)
            errores.append(str(e))
        time.sleep(PAUSA_TRAMO)
    return resultados, errores


def descargar_lote(puntos, nivel):
    """Serie diaria completa para cada punto del lote.
    Devuelve lista de (datos | None, motivo | None, elevacion)."""
    anio_ini, anio_fin = int(NORMAL_INICIO[:4]), int(NORMAL_FIN[:4])
    acum = [{"time": [], **{v: [] for v in VARIABLES}} for _ in puntos]
    motivo = [None] * len(puntos)
    elev = [None] * len(puntos)

    a = anio_ini
    while a <= anio_fin:
        b = min(a + BLOQUE_ANIOS - 1, anio_fin)
        res, err = _pedir_tramo(puntos, a, b, nivel)
        for i, (r, e) in enumerate(zip(res, err)):
            if motivo[i]:
                continue
            if e or not r or "daily" not in r:
                motivo[i] = e or f"respuesta sin bloque 'daily' en {a}-{b}"
                continue
            if elev[i] is None:
                elev[i] = r.get("elevation")
            for k in acum[i]:
                acum[i][k].extend(r["daily"].get(k) or [])
        print(f"    {a}-{b} listo", flush=True)
        if b < anio_fin:
            time.sleep(PAUSA_TRAMO)
        a = b + 1

    salida = []
    for i in range(len(puntos)):
        if motivo[i]:
            salida.append((None, motivo[i], elev[i]))
            continue
        faltan = _dias_esperados() - len(acum[i]["time"])
        if faltan > 0:
            salida.append((None, f"serie incompleta: faltan {faltan} dias", elev[i]))
            continue
        salida.append(({"daily": acum[i]}, None, elev[i]))
    return salida


def serie_mensual(datos):
    """Serie mensual completa del periodo: por 'AAAA-MM', el acumulado de lluvia
    (escalado al mes completo si cubre >= 90 % de los dias; None si no) y la
    media de tmax. Es el insumo del analisis de sensibilidad al ENSO: la normal
    sola no permite cruzar cada mes con el ONI de ese mes."""
    lluvia = defaultdict(float); dias = defaultdict(int); tmax = defaultdict(list)
    d = datos["daily"]
    for fecha, pp, tx in zip(d["time"], d["precipitation_sum"], d["temperature_2m_max"]):
        k = fecha[:7]
        if pp is not None:
            lluvia[k] += pp; dias[k] += 1
        if tx is not None:
            tmax[k].append(tx)
    serie = {}
    for k in sorted(set(lluvia) | set(tmax)):
        anio, mes = int(k[:4]), int(k[5:7])
        largo = calendar.monthrange(anio, mes)[1]
        pp = round(lluvia[k] * largo / dias[k], 1) if dias[k] >= COBERTURA_MINIMA_MES * largo else None
        tx = round(sum(tmax[k]) / len(tmax[k]), 2) if tmax[k] else None
        serie[k] = [pp, tx]
    return serie


def normales_mensuales(datos):
    """Por mes del anio: precipitacion mensual media (media de acumulados
    mensuales, solo meses con cobertura >= 90 %, escalados al mes completo) y
    media de maximas y minimas diarias. Lanza RuntimeError si un mes no tiene
    datos suficientes."""
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


def _cargar_parcial(ruta, reiniciar):
    vacio = {"normales": {}, "unidades": {}, "sin_datos": {}, "series": {}}
    if reiniciar or not ruta.exists():
        return vacio
    try:
        previo = json.loads(ruta.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"aviso: no pude leer {ruta.name} ({e}); empiezo de cero")
        return vacio
    if "normales" not in previo:  # formato anterior: solo el dict de normales
        previo = {"normales": previo, "unidades": {}, "sin_datos": {}}
    previo.setdefault("series", {})
    hechos = len(previo["normales"]) + len(previo["sin_datos"])
    if hechos:
        print(f"retomo avance previo: {hechos} unidades ya procesadas")
    return previo


def _escribir(destino, nivel, estado):
    destino.write_text(json.dumps({
        "periodo": f"{NORMAL_INICIO[:4]}-{NORMAL_FIN[:4]}",
        "fuente": ("ERA5-Land via Open-Meteo Archive API"
                   if MODELO_ARCHIVO.get(nivel) == "era5_land"
                   else "ERA5 via Open-Meteo Archive API"),
        "modelo": MODELO_ARCHIVO.get(nivel) or "era5",
        "nivel": nivel,
        "normales": estado["normales"],
        "unidades": estado["unidades"],
        "sin_datos": estado["sin_datos"],
    }, ensure_ascii=False, indent=2))


def main():
    nivel = nivel_desde_argv()
    reiniciar = "--reiniciar" in sys.argv
    ruta = rutas(nivel)
    todas = unidades(nivel)
    estado = _cargar_parcial(ruta["parcial"], reiniciar)

    procesadas = set(estado["normales"]) | set(estado["sin_datos"])
    pendientes = [u for u in todas if clave(nivel, u) not in procesadas]
    total = len(todas)
    lote = LOTE[nivel]

    for i in range(0, len(pendientes), lote):
        grupo = pendientes[i:i + lote]
        hechos = total - len(pendientes) + i + len(grupo)
        nombres = ", ".join(u["nombre"] for u in grupo)
        print(f"[{hechos}/{total}] {nombres}", flush=True)

        for u, (datos, motivo, elev) in zip(grupo, descargar_lote(grupo, nivel)):
            k = clave(nivel, u)
            estado["unidades"][k] = {
                "nombre": u["nombre"], "lat": u["lat"], "lon": u["lon"],
                "zona": u["zona"], "elevacion_modelo_m": elev,
                **({"departamento": u["departamento"]} if "departamento" in u else {}),
            }
            if datos is None:
                estado["sin_datos"][k] = motivo
                print(f"    {u['nombre']}: SIN DATOS ({motivo})", flush=True)
                continue
            try:
                estado["normales"][k] = normales_mensuales(datos)
                estado["series"][k] = serie_mensual(datos)
            except RuntimeError as e:
                estado["sin_datos"][k] = str(e)
                print(f"    {u['nombre']}: SIN DATOS ({e})", flush=True)

        # checkpoint: una corrida de horas no deberia perderse por un corte
        ruta["parcial"].write_text(json.dumps(estado, ensure_ascii=False))

        if i + lote < len(pendientes):
            pausa = _pausa_entre_lotes()
            print(f"    pausa de {pausa}s antes del siguiente lote", flush=True)
            time.sleep(pausa)

    _escribir(ruta["normales"], nivel, estado)
    ruta["series"].write_text(json.dumps({
        "periodo": f"{NORMAL_INICIO[:4]}-{NORMAL_FIN[:4]}", "nivel": nivel,
        "modelo": MODELO_ARCHIVO.get(nivel) or "era5",
        "formato": "por unidad, por 'AAAA-MM': [lluvia_mensual_mm o null, tmax_media_c o null]",
        "series": estado["series"],
    }, ensure_ascii=False, separators=(",", ":")))
    ruta["parcial"].unlink(missing_ok=True)
    print(f"Guardado en {ruta['normales']} ({len(estado['normales'])} con normales, "
          f"{len(estado['sin_datos'])} sin datos, "
          f"{rate_limits_vistos()} HTTP 429 durante la corrida)")
    print(f"Verificar con: PYTHONPATH=scripts python3 scripts/verificar_normales.py"
          f"{'' if nivel == 'departamento' else ' --nivel provincia'}")


if __name__ == "__main__":
    main()
