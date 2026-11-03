"""Verifica que el archivo de normales sea un producto completo y plausible.

    PYTHONPATH=scripts python3 scripts/verificar_normales.py
    PYTHONPATH=scripts python3 scripts/verificar_normales.py --nivel provincia

No reemplaza el juicio experto: solo atrapa los errores gruesos que una
descarga cortada o un cruce de coordenadas dejarian pasar. Devuelve codigo de
salida 1 si algo falla, para poder encadenarlo en el flujo automatico.

Controles:
  1. Estructura: todas las unidades del nivel con 12 meses y tres variables.
     Las unidades listadas en "sin_datos" (con motivo) se aceptan como aviso
     mientras no pasen de FRACCION_SIN_DATOS_MAX.
  2. Rangos fisicos, y tmax > tmin en todos los meses.
  3. Plausibilidad climatica:
     - la selva de Loreto debe ser mucho mas lluviosa que el desierto de Ica;
     - en la sierra el maximo de lluvia debe caer entre diciembre y marzo
       (todas las unidades en departamentos; al menos FRACCION_SIERRA_MIN en
       provincias, el resto se lista como aviso).
"""
import json
import sys
from pathlib import Path

from config import DEPARTAMENTOS
from niveles import clave, nivel_desde_argv, rutas, unidades

MESES = [f"{m:02d}" for m in range(1, 13)]
MESES_LLUVIOSOS_SIERRA = {"12", "01", "02", "03"}
VARIABLES = ("precipitacion_mensual_mm", "tmax_media_c", "tmin_media_c")
FRACCION_SIN_DATOS_MAX = 0.2   # mas que esto ya no es "algunas sin datos"
FRACCION_SIERRA_MIN = 0.9      # provincias de sierra con maximo en dic-mar

RANGO = {
    "precipitacion_mensual_mm": (0.0, 1500.0),
    "tmax_media_c": (-10.0, 45.0),
    "tmin_media_c": (-25.0, 35.0),
}


def anual(normales, k):
    return sum(normales[k][m]["precipitacion_mensual_mm"] for m in MESES)


def mes_mas_lluvioso(normales, k):
    return max(MESES, key=lambda m: normales[k][m]["precipitacion_mensual_mm"])


def _departamento(nivel, u):
    return u["nombre"] if nivel == "departamento" else u["departamento"]


def verificar(doc, nivel="departamento"):
    fallas, avisos = [], []
    todas = unidades(nivel)
    nombre = {clave(nivel, u): u["nombre"] for u in todas}

    if doc.get("periodo") != "1991-2020":
        fallas.append(f"el periodo base declarado es {doc.get('periodo')!r}, "
                      "se esperaba '1991-2020'")
    if not doc.get("fuente"):
        fallas.append("falta declarar la fuente")

    normales = doc.get("normales", {})
    sin_datos = doc.get("sin_datos", {})
    esperados = [clave(nivel, u) for u in todas]

    faltantes = [k for k in esperados if k not in normales and k not in sin_datos]
    sobrantes = [k for k in normales if k not in esperados]
    if faltantes:
        fallas.append(f"faltan {len(faltantes)} unidades sin motivo: "
                      + ", ".join(nombre[k] for k in faltantes[:10]))
    if sobrantes:
        fallas.append(f"unidades no reconocidas: {', '.join(sobrantes[:10])}")
    if sin_datos:
        frac = len(sin_datos) / len(esperados)
        msg = (f"{len(sin_datos)} de {len(esperados)} unidades sin datos: "
               + ", ".join(f"{nombre.get(k, k)} ({v})" for k, v in list(sin_datos.items())[:8]))
        (fallas if frac > FRACCION_SIN_DATOS_MAX else avisos).append(msg)

    for k in esperados:
        if k not in normales:
            continue
        meses = normales[k]
        ausentes = [m for m in MESES if m not in meses]
        if ausentes:
            fallas.append(f"{nombre[k]}: faltan los meses {', '.join(ausentes)}")
            continue
        for m in MESES:
            for var in VARIABLES:
                valor = meses[m].get(var)
                if not isinstance(valor, (int, float)):
                    fallas.append(f"{nombre[k]} mes {m}: {var} no es numerico ({valor!r})")
                    continue
                lo, hi = RANGO[var]
                if not lo <= valor <= hi:
                    fallas.append(f"{nombre[k]} mes {m}: {var}={valor} fuera del "
                                  f"rango plausible [{lo}, {hi}]")
            tx, tn = meses[m].get("tmax_media_c"), meses[m].get("tmin_media_c")
            if isinstance(tx, (int, float)) and isinstance(tn, (int, float)) and tx <= tn:
                fallas.append(f"{nombre[k]} mes {m}: tmax ({tx}) no supera a tmin ({tn})")
            usados = meses[m].get("anios_usados_precipitacion")
            if isinstance(usados, int) and usados < 25:
                avisos.append(f"{nombre[k]} mes {m}: la normal de lluvia usa solo "
                              f"{usados} anios de los 30 del periodo")

    if fallas:
        return fallas, avisos

    # 3: plausibilidad climatica
    def media_anual_depto(dep):
        ks = [clave(nivel, u) for u in todas
              if _departamento(nivel, u) == dep and clave(nivel, u) in normales]
        return sum(anual(normales, k) for k in ks) / len(ks) if ks else None

    pp_loreto, pp_ica = media_anual_depto("Loreto"), media_anual_depto("Ica")
    if pp_loreto is None or pp_ica is None:
        avisos.append("no se pudo contrastar Loreto con Ica (sin datos en uno de los dos)")
    else:
        if pp_loreto < 1000:
            fallas.append(f"Loreto acumula {pp_loreto:.0f} mm al anio en promedio; "
                          "la selva norte deberia pasar los 1000 mm")
        if pp_ica > 100:
            fallas.append(f"Ica acumula {pp_ica:.0f} mm al anio en promedio; el "
                          "desierto costero deberia quedar por debajo de 100 mm")
        if pp_loreto < 3 * max(pp_ica, 1.0):
            fallas.append(f"Loreto ({pp_loreto:.0f} mm) no resulta mucho mas "
                          f"lluvioso que Ica ({pp_ica:.0f} mm)")

    sierra = [clave(nivel, u) for u in todas
              if u["zona"].startswith("sierra") and clave(nivel, u) in normales]
    fuera = [k for k in sierra if mes_mas_lluvioso(normales, k) not in MESES_LLUVIOSOS_SIERRA]
    if sierra:
        if nivel == "departamento":
            for k in fuera:
                fallas.append(f"{nombre[k]} (sierra): su maximo de lluvia cae en el mes "
                              f"{mes_mas_lluvioso(normales, k)}; se espera entre diciembre y marzo")
        else:
            frac_ok = 1 - len(fuera) / len(sierra)
            msg = (f"{len(fuera)} de {len(sierra)} provincias de sierra con maximo fuera de "
                   "dic-mar: " + ", ".join(nombre[k] for k in fuera[:10]))
            (fallas if frac_ok < FRACCION_SIERRA_MIN else avisos).append(msg)

    return fallas, avisos


def main():
    nivel = nivel_desde_argv()
    archivo = rutas(nivel)["normales"]
    if not archivo.exists():
        print(f"FALLA: no existe {archivo}. Correr primero "
              f"PYTHONPATH=scripts python3 scripts/calcular_normales.py"
              f"{'' if nivel == 'departamento' else ' --nivel provincia'}")
        return 1

    doc = json.loads(archivo.read_text())
    fallas, avisos = verificar(doc, nivel)
    normales = doc.get("normales", {})
    nombre = {clave(nivel, u): u["nombre"] for u in unidades(nivel)}

    for a in avisos:
        print(f"aviso: {a}")
    if fallas:
        print(f"\n{len(fallas)} problema(s) en {archivo.name}:")
        for f in fallas:
            print(f"  - {f}")
        return 1

    print(f"{archivo.name} OK: {len(normales)} unidades x 12 meses, "
          f"periodo {doc['periodo']}, nivel {nivel}")
    orden = sorted(normales, key=lambda k: anual(normales, k), reverse=True)
    if nivel == "provincia":
        orden = orden[:8] + ["..."] + orden[-8:]
        print("\nPrecipitacion anual normal, extremos (mm):")
    else:
        print("\nPrecipitacion anual normal por departamento (mm):")
    for k in orden:
        if k == "...":
            print("  ...")
            continue
        print(f"  {nombre.get(k, k):<22} {anual(normales, k):>8.0f}   "
              f"max en mes {mes_mas_lluvioso(normales, k)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
