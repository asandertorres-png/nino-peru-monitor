"""Verifica que data/normales.json sea un producto completo y plausible.

No reemplaza el juicio experto: solo atrapa los errores gruesos que una
descarga cortada o un cruce de coordenadas dejarian pasar. Devuelve codigo de
salida 1 si algo falla, para poder encadenarlo en el flujo automatico.

Controles:
  1. Estructura: 25 departamentos, 12 meses cada uno, con las tres variables.
  2. Rangos fisicos: lluvia y temperaturas dentro de lo posible en el Peru,
     y tmax > tmin en todos los meses.
  3. Plausibilidad climatica:
     - Loreto (Iquitos) debe ser mucho mas lluvioso que Ica.
     - Ica, en el desierto costero, debe ser practicamente seco.
     - En la sierra el maximo de lluvia debe caer entre diciembre y marzo.
"""
import json
import sys
from pathlib import Path

from config import DEPARTAMENTOS

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = RAIZ / "data" / "normales.json"

MESES = [f"{m:02d}" for m in range(1, 13)]
MESES_LLUVIOSOS_SIERRA = {"12", "01", "02", "03"}
VARIABLES = ("precipitacion_mensual_mm", "tmax_media_c", "tmin_media_c")

# Rangos fisicos holgados: el objetivo es atrapar basura, no afinar.
RANGO = {
    "precipitacion_mensual_mm": (0.0, 1500.0),
    "tmax_media_c": (-10.0, 45.0),
    "tmin_media_c": (-25.0, 35.0),
}


def anual(normales, dep):
    return sum(normales[dep][m]["precipitacion_mensual_mm"] for m in MESES)


def mes_mas_lluvioso(normales, dep):
    return max(MESES, key=lambda m: normales[dep][m]["precipitacion_mensual_mm"])


def verificar(doc):
    fallas = []
    avisos = []

    if doc.get("periodo") != "1991-2020":
        fallas.append(f"el periodo base declarado es {doc.get('periodo')!r}, "
                      "se esperaba '1991-2020'")
    if not doc.get("fuente"):
        fallas.append("falta declarar la fuente")

    normales = doc.get("normales", {})
    esperados = [d["nombre"] for d in DEPARTAMENTOS]

    faltantes = [d for d in esperados if d not in normales]
    sobrantes = [d for d in normales if d not in esperados]
    if faltantes:
        fallas.append(f"faltan {len(faltantes)} departamentos: "
                      f"{', '.join(faltantes)}")
    if sobrantes:
        fallas.append(f"departamentos no reconocidos: {', '.join(sobrantes)}")

    # 1 y 2: estructura y rangos
    for dep in esperados:
        if dep not in normales:
            continue
        meses = normales[dep]
        ausentes = [m for m in MESES if m not in meses]
        if ausentes:
            fallas.append(f"{dep}: faltan los meses {', '.join(ausentes)}")
            continue
        for m in MESES:
            for var in VARIABLES:
                valor = meses[m].get(var)
                if not isinstance(valor, (int, float)):
                    fallas.append(f"{dep} mes {m}: {var} no es numerico "
                                  f"({valor!r})")
                    continue
                lo, hi = RANGO[var]
                if not lo <= valor <= hi:
                    fallas.append(f"{dep} mes {m}: {var}={valor} fuera del "
                                  f"rango plausible [{lo}, {hi}]")
            tx, tn = meses[m].get("tmax_media_c"), meses[m].get("tmin_media_c")
            if isinstance(tx, (int, float)) and isinstance(tn, (int, float)):
                if tx <= tn:
                    fallas.append(f"{dep} mes {m}: tmax ({tx}) no supera a "
                                  f"tmin ({tn})")
            usados = meses[m].get("anios_usados_precipitacion")
            if isinstance(usados, int) and usados < 25:
                avisos.append(f"{dep} mes {m}: la normal de lluvia usa solo "
                              f"{usados} anios de los 30 del periodo")

    if fallas:  # sin estructura valida no tiene sentido evaluar plausibilidad
        return fallas, avisos

    # 3: plausibilidad climatica
    pp_loreto, pp_ica = anual(normales, "Loreto"), anual(normales, "Ica")
    if pp_loreto < 1000:
        fallas.append(f"Loreto (Iquitos) acumula {pp_loreto:.0f} mm al anio; "
                      "la selva norte deberia pasar los 1000 mm")
    if pp_ica > 100:
        fallas.append(f"Ica acumula {pp_ica:.0f} mm al anio; el desierto "
                      "costero deberia quedar por debajo de 100 mm")
    if pp_loreto < 3 * max(pp_ica, 1.0):
        fallas.append(f"Iquitos ({pp_loreto:.0f} mm) no resulta mucho mas "
                      f"lluvioso que Ica ({pp_ica:.0f} mm)")

    sierra = [d["nombre"] for d in DEPARTAMENTOS
              if d["zona"].startswith("sierra")]
    for dep in sierra:
        mes = mes_mas_lluvioso(normales, dep)
        if mes not in MESES_LLUVIOSOS_SIERRA:
            fallas.append(f"{dep} (sierra): su maximo de lluvia cae en el mes "
                          f"{mes}; se espera entre diciembre y marzo")

    return fallas, avisos


def main():
    if not ARCHIVO.exists():
        print(f"FALLA: no existe {ARCHIVO}. Correr primero "
              "PYTHONPATH=scripts python3 scripts/calcular_normales.py")
        return 1

    doc = json.loads(ARCHIVO.read_text())
    fallas, avisos = verificar(doc)
    normales = doc.get("normales", {})

    for a in avisos:
        print(f"aviso: {a}")
    if fallas:
        print(f"\n{len(fallas)} problema(s) en {ARCHIVO.name}:")
        for f in fallas:
            print(f"  - {f}")
        return 1

    print(f"{ARCHIVO.name} OK: {len(normales)} departamentos x 12 meses, "
          f"periodo {doc['periodo']}")
    print("\nPrecipitacion anual normal por departamento (mm):")
    orden = sorted(normales, key=lambda d: anual(normales, d), reverse=True)
    for dep in orden:
        print(f"  {dep:<15} {anual(normales, dep):>8.0f}   "
              f"max en mes {mes_mas_lluvioso(normales, dep)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
