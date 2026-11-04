"""Sensibilidad de la lluvia de cada unidad al ENSO, 1991-2020 (inferencial).

    PYTHONPATH=scripts python3 scripts/sensibilidad.py                    # departamentos
    PYTHONPATH=scripts python3 scripts/sensibilidad.py --nivel provincia  # cuando exista su serie

Insumos: la serie mensual 1991-2020 que guarda calcular_normales.py
(data/series_mensuales*.json), las normales, y el ONI historico de la NOAA.

Para cada unidad y cada mes del calendario:
  - anomalia de lluvia de cada anio = (lluvia del mes - normal) / normal, en %;
  - se cruza con el ONI del trimestre centrado en ese mes, con rezagos de 0 a
    3 meses (el ONI de 1 a 3 meses antes);
  - correlacion de Pearson r, pendiente (% de lluvia por °C de ONI), n, y un
    p aproximado por la transformacion z de Fisher (aproximacion normal);
  - el "mejor rezago" es el de mayor |r| con p < ALFA; si ninguno, el 0;
  - probabilidades condicionales con ese rezago: entre los anios con ONI >=
    UMBRAL_NINO, que fraccion tuvo deficit (anomalia <= DEFICIT) o exceso
    (anomalia >= EXCESO), frente a la fraccion base de los 30 anios.

Advertencias que acompanan al producto y deben acompanar cualquier uso:
30 anios son 30 observaciones por mes y apenas 4 o 5 eventos El Nino; las
correlaciones describen asociacion, no causalidad; con 12 meses x 4 rezagos
por unidad, algunas correlaciones "significativas" lo son por azar (no se
corrige por comparaciones multiples: el p es orientativo). Los meses con
normal muy baja (< UMBRAL_NORMAL_BAJA_MM) no se analizan en porcentaje.
"""
import json
import math
import sys
from datetime import date
from pathlib import Path

from config import UMBRAL_NORMAL_BAJA_MM
from niveles import clave, nivel_desde_argv, rutas, unidades

RAIZ = Path(__file__).resolve().parent.parent
CENTRO = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
          "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}
REZAGOS = (0, 1, 2, 3)
UMBRAL_NINO = 1.0   # ONI >= +1.0: El Nino moderado o mas (criterio NOAA)
DEFICIT = -20.0     # mismo umbral que el primer nivel de alerta por deficit
EXCESO = 50.0       # mismo umbral que el primer nivel de alerta por exceso
ALFA = 0.05
MESES = [f"{m:02d}" for m in range(1, 13)]


def oni_por_mes(serie):
    """{(anio, mes_central): oni} a partir de la serie de trimestres moviles."""
    return {(p["anio"], CENTRO[p["trimestre"]]): p["oni"] for p in serie if p["trimestre"] in CENTRO}


def mes_anterior(anio, mes, rezago):
    m = mes - rezago
    while m < 1:
        m += 12; anio -= 1
    return anio, m


def pearson(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0 or syy <= 0:
        return None
    r = sxy / math.sqrt(sxx * syy)
    pendiente = sxy / sxx
    r_c = max(-0.999999, min(0.999999, r))
    z = math.atanh(r_c) * math.sqrt(n - 3)
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return {"r": round(r, 3), "p": round(p, 4), "pendiente": round(pendiente, 2), "n": n}


def analizar_unidad(serie, normales, oni_mes, anio_ini, anio_fin):
    salida = {}
    for mm in MESES:
        m = int(mm)
        normal = normales.get(mm, {}).get("precipitacion_mensual_mm")
        if normal is None or normal < UMBRAL_NORMAL_BAJA_MM:
            salida[mm] = {"normal_baja": True}
            continue
        anomalias = {}
        for anio in range(anio_ini, anio_fin + 1):
            v = serie.get(f"{anio}-{mm}")
            if v and v[0] is not None:
                anomalias[anio] = (v[0] - normal) / normal * 100
        por_rezago = {}
        for rez in REZAGOS:
            pares = [(oni_mes[mes_anterior(a, m, rez)], an) for a, an in anomalias.items()
                     if mes_anterior(a, m, rez) in oni_mes]
            est = pearson([p[0] for p in pares], [p[1] for p in pares]) if pares else None
            if est:
                por_rezago[rez] = est
        if not por_rezago:
            salida[mm] = {"sin_datos": True}
            continue
        significativos = [(abs(e["r"]), rez) for rez, e in por_rezago.items() if e["p"] < ALFA]
        mejor = max(significativos)[1] if significativos else 0
        if mejor not in por_rezago:
            mejor = min(por_rezago)
        est = por_rezago[mejor]
        # probabilidades condicionales con el rezago elegido
        pares = [(oni_mes[mes_anterior(a, m, mejor)], an) for a, an in anomalias.items()
                 if mes_anterior(a, m, mejor) in oni_mes]
        con_nino = [an for o, an in pares if o >= UMBRAL_NINO]
        todos = [an for _, an in pares]
        cuenta = lambda vals, cond: sum(1 for v in vals if cond(v))
        salida[mm] = {
            "rezago": mejor, "r": est["r"], "p": est["p"],
            "pendiente_pct_por_c": est["pendiente"], "n": est["n"],
            "n_nino": len(con_nino),
            "deficit_con_nino": [cuenta(con_nino, lambda v: v <= DEFICIT), len(con_nino)],
            "exceso_con_nino": [cuenta(con_nino, lambda v: v >= EXCESO), len(con_nino)],
            "deficit_base": [cuenta(todos, lambda v: v <= DEFICIT), len(todos)],
            "exceso_base": [cuenta(todos, lambda v: v >= EXCESO), len(todos)],
            "por_rezago": {str(rez): [e["r"], e["p"]] for rez, e in por_rezago.items()},
        }
    return salida


def main(serie_oni=None):
    nivel = nivel_desde_argv()
    ruta = rutas(nivel)
    if not ruta["series"].exists():
        raise SystemExit(f"falta {ruta['series']}: la corrida de normales de este nivel aun no "
                         "guardo la serie mensual (calcular_normales.py la genera desde ahora)")
    series = json.loads(ruta["series"].read_text())
    normales = json.loads(ruta["normales"].read_text())["normales"]
    anio_ini, anio_fin = (int(x) for x in series["periodo"].split("-"))
    if serie_oni is None:
        from fetch_oni import descargar_oni
        serie_oni = descargar_oni()
    oni_mes = oni_por_mes(serie_oni)

    resultado = {}
    for u in unidades(nivel):
        k = clave(nivel, u)
        if k in series["series"] and k in normales:
            resultado[k] = analizar_unidad(series["series"][k], normales[k], oni_mes, anio_ini, anio_fin)

    ruta["sensibilidad"].write_text(json.dumps({
        "periodo": series["periodo"], "nivel": nivel, "modelo": series.get("modelo"),
        "generado": date.today().isoformat(),
        "metodo": ("anomalia mensual de lluvia (% de la normal) cruzada con el ONI del trimestre centrado "
                   "en el mes, rezagos 0-3; Pearson r, pendiente en % por °C, p por z de Fisher (aprox. normal); "
                   "mejor rezago = mayor |r| con p < 0.05, si no, 0"),
        "umbrales": {"oni_nino": UMBRAL_NINO, "deficit_pct": DEFICIT, "exceso_pct": EXCESO, "alfa": ALFA,
                     "normal_baja_mm": UMBRAL_NORMAL_BAJA_MM},
        "advertencias": [
            "30 anios = 30 observaciones por mes y 4-5 eventos El Nino: estimaciones con mucha incertidumbre",
            "asociacion, no causalidad",
            "sin correccion por comparaciones multiples (12 meses x 4 rezagos por unidad): el p es orientativo",
            "la lluvia proviene de reanalisis en un punto, no de estaciones",
        ],
        "oni_fuente": "NOAA CPC, ONI (trimestres moviles, mes central)",
        "unidades": resultado,
    }, ensure_ascii=False, indent=1))
    n_sig = sum(1 for u in resultado.values() for m in u.values() if m.get("p") is not None and m["p"] < ALFA)
    print(f"sensibilidad: {len(resultado)} unidades, {n_sig} pares mes-unidad con p < {ALFA} "
          f"-> {ruta['sensibilidad'].name}")


if __name__ == "__main__":
    main()
