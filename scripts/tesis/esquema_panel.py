#!/usr/bin/env python3
"""Esquema del panel de la tesis: matriz de datos, plantilla y validador.

Una sola definicion del esquema sirve para tres cosas, de modo que no puedan
desalinearse entre si:

  1. la MATRIZ DE DATOS que va en el documento de tesis;
  2. la PLANTILLA CSV con la que se arma el panel;
  3. el VALIDADOR que revisa un panel ya armado antes de estimar.

Uso:
    python scripts/tesis/esquema_panel.py --plantilla
        escribe docs/tesis/plantilla_panel.csv y docs/tesis/esquema_panel.json

    python scripts/tesis/esquema_panel.py --validar data/tesis/panel.csv
        revisa un panel contra el esquema y devuelve 1 si hay problemas

La unidad de observacion es la CIUDAD-MES. El panel va en formato largo: una
fila por ciudad y mes, nunca una columna por mes.
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter

# Numero esperado de unidades y de periodos
CIUDADES = 26
PERIODO_INICIO = "2010-01"
PERIODO_FIN = "2026-09"

# Cada campo: (orden, nombre, etiqueta, tipo, escala, rango, fuente, indicador)
#   tipo:  texto | entero | decimal
#   rango: descripcion legible del dominio valido; None si no aplica
CAMPOS = [
    # ---------------------------------------------------- identificacion
    # Los NOMBRES de campo van sin tildes a proposito: son nombres de columna.
    # Las etiquetas y descripciones si llevan tildes, porque son texto del
    # documento de tesis.
    (1, "ciudad_id", "Código de ciudad", "entero", "Nominal",
     "1 a 26", "Asignado por el autor", "–"),
    (2, "ciudad", "Nombre de la ciudad", "texto", "Nominal",
     "26 nombres válidos", "INEI, IPC de 26 ciudades", "–"),
    (3, "ubigeo", "Código UBIGEO de la ciudad", "texto", "Nominal",
     "6 dígitos", "INEI", "–"),
    (4, "departamento", "Departamento al que pertenece", "texto", "Nominal",
     "25 departamentos", "INEI", "–"),
    (5, "zona", "Régimen de impacto climático", "texto", "Nominal",
     "costa_norte, costa_centro_sur, sierra_norte, sierra_sur, selva",
     "scripts/config.py del monitor", "–"),
    (6, "lat", "Latitud del punto de la ciudad", "decimal", "Razón",
     "−18,5 a −3,5", "GeoJSON / config del monitor", "–"),
    (7, "lon", "Longitud del punto de la ciudad", "decimal", "Razón",
     "−81,5 a −68,5", "GeoJSON / config del monitor", "–"),
    (8, "anio", "Año del periodo", "entero", "Intervalo",
     "2010 a 2026", "Derivado", "–"),
    (9, "mes", "Mes del periodo", "entero", "Intervalo",
     "1 a 12", "Derivado", "–"),
    (10, "periodo", "Periodo en formato AAAA-MM", "texto", "Ordinal",
     f"{PERIODO_INICIO} a {PERIODO_FIN}", "Derivado", "–"),

    # ---------------------------------------------------- variable X
    (11, "anom_pp", "Anomalía estandarizada de precipitación", "decimal", "Razón",
     "aprox. −4 a 4 desviaciones estándar", "ERA5 vía Open-Meteo", "1"),
    (12, "anom_tx", "Anomalía estandarizada de temperatura máxima", "decimal", "Razón",
     "aprox. −4 a 4 desviaciones estándar", "ERA5 vía Open-Meteo", "2"),
    (13, "oni", "Índice ONI, región Niño 3.4", "decimal", "Razón",
     "−3,0 a 3,0 °C", "NOAA/CPC", "3"),
    (14, "icen_rep", "ICEN-réplica, región Niño 1+2", "decimal", "Razón",
     "−4,0 a 5,0 °C", "NOAA/CPC, calculado", "4"),
    (15, "exp_vab_prim", "Peso de agropecuario y pesca en el VAB departamental",
     "decimal", "Razón", "0 a 100 %", "INEI, cuentas departamentales", "5"),
    (16, "exp_peso_alim", "Peso del alimento en la canasta del IPC de la ciudad",
     "decimal", "Razón", "0 a 100 %", "INEI, ponderaciones del IPC", "6"),

    # ---------------------------------------------------- variable Y
    (17, "ipc_alim", "Índice de precios de alimentos de la ciudad", "decimal", "Razón",
     "mayor que 0; base diciembre 2021 = 100", "INEI", "base de 7 a 10"),
    (18, "infl_alim_m", "Variación mensual del IPC de alimentos", "decimal", "Razón",
     "aprox. −20 a 20 %", "Derivado de ipc_alim", "7"),
    (19, "infl_alim_12", "Variación a doce meses del IPC de alimentos", "decimal", "Razón",
     "aprox. −30 a 60 %", "Derivado de ipc_alim", "8"),
    (20, "volat_12", "Desviación estándar móvil de 12 meses de infl_alim_m",
     "decimal", "Razón", "mayor o igual que 0", "Derivado de infl_alim_m", "9"),
    (21, "integr_media", "Correlación media de infl_alim_m con las demás ciudades",
     "decimal", "Razón", "−1 a 1", "Derivado de infl_alim_m", "10"),

    # ---------------------------------------------------- auxiliares
    (22, "ipc_general", "Índice de precios al consumidor general de la ciudad",
     "decimal", "Razón", "mayor que 0", "INEI", "auxiliar"),
    (23, "normal_pp_mm", "Normal mensual de precipitación, 1991–2020", "decimal", "Razón",
     "mayor o igual que 0 mm", "ERA5, calculado", "auxiliar"),
    (24, "sigma_pp_mm", "Desviación estándar de la precipitación mensual, 1991–2020",
     "decimal", "Razón", "mayor o igual que 0 mm", "ERA5, calculado", "auxiliar"),
    (25, "anios_normal", "Años utilizados en la normal de ese mes", "entero", "Razón",
     "0 a 30", "ERA5, calculado", "control de calidad"),
    (26, "base_ipc", "Base del índice en ese periodo", "texto", "Nominal",
     "2009 o dic2021", "INEI", "control de empalme"),
    (27, "fuente_ipc", "De dónde se obtuvo el dato de IPC", "texto", "Nominal",
     "serie, boletin_pdf o imputado", "Registro del autor", "trazabilidad"),
]

ENCABEZADOS = [c[1] for c in CAMPOS]
POR_NOMBRE = {c[1]: c for c in CAMPOS}

ZONAS = {"costa_norte", "costa_centro_sur", "sierra_norte", "sierra_sur", "selva"}
BASES = {"2009", "dic2021"}
FUENTES_IPC = {"serie", "boletin_pdf", "imputado"}

# Campos que NO pueden venir vacios en una fila utilizable
OBLIGATORIOS = ["ciudad_id", "ciudad", "departamento", "zona", "anio", "mes", "periodo"]


def _periodos_esperados():
    ai, mi = (int(x) for x in PERIODO_INICIO.split("-"))
    af, mf = (int(x) for x in PERIODO_FIN.split("-"))
    salida, a, m = [], ai, mi
    while (a, m) <= (af, mf):
        salida.append(f"{a:04d}-{m:02d}")
        m += 1
        if m == 13:
            a, m = a + 1, 1
    return salida


# ----------------------------------------------------------------- plantilla

def escribir_plantilla(raiz):
    destino_csv = os.path.join(raiz, "docs", "tesis", "plantilla_panel.csv")
    destino_json = os.path.join(raiz, "docs", "tesis", "esquema_panel.json")
    os.makedirs(os.path.dirname(destino_csv), exist_ok=True)

    with open(destino_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(ENCABEZADOS)

    esquema = {
        "unidad_de_observacion": "ciudad-mes",
        "formato": "largo: una fila por ciudad y periodo",
        "ciudades": CIUDADES,
        "periodo_inicio": PERIODO_INICIO,
        "periodo_fin": PERIODO_FIN,
        "periodos": len(_periodos_esperados()),
        "filas_esperadas": CIUDADES * len(_periodos_esperados()),
        "campos": [
            {"orden": c[0], "nombre": c[1], "etiqueta": c[2], "tipo": c[3],
             "escala": c[4], "rango": c[5], "fuente": c[6], "indicador": c[7]}
            for c in CAMPOS
        ],
    }
    with open(destino_json, "w", encoding="utf-8") as f:
        json.dump(esquema, f, ensure_ascii=False, indent=1)

    print(f"{len(CAMPOS)} campos -> {destino_csv}")
    print(f"{esquema['filas_esperadas']} filas esperadas "
          f"({CIUDADES} ciudades x {esquema['periodos']} periodos) -> {destino_json}")


# ----------------------------------------------------------------- validador

def validar(ruta):
    if not os.path.exists(ruta):
        print(f"No existe el archivo: {ruta}")
        return 1

    with open(ruta, encoding="utf-8-sig", newline="") as f:
        muestra = f.read(4096)
        f.seek(0)
        sep = ";" if muestra.count(";") >= muestra.count(",") else ","
        filas = list(csv.DictReader(f, delimiter=sep))

    problemas, avisos = [], []

    # --- estructura
    if not filas:
        print("El archivo no tiene filas de datos.")
        return 1
    faltan = [c for c in ENCABEZADOS if c not in filas[0]]
    sobran = [c for c in filas[0] if c not in ENCABEZADOS]
    if faltan:
        problemas.append(f"faltan {len(faltan)} columnas: {', '.join(faltan[:8])}"
                         + ("..." if len(faltan) > 8 else ""))
    if sobran:
        avisos.append(f"columnas no previstas: {', '.join(sobran[:8])}")

    # --- completitud del panel
    esperados = set(_periodos_esperados())
    llaves = Counter((f.get("ciudad_id", ""), f.get("periodo", "")) for f in filas)
    duplicadas = [k for k, n in llaves.items() if n > 1]
    if duplicadas:
        problemas.append(f"{len(duplicadas)} combinaciones ciudad-periodo duplicadas; "
                         f"ejemplo {duplicadas[0]}")

    ciudades = {f.get("ciudad_id") for f in filas if f.get("ciudad_id")}
    if len(ciudades) != CIUDADES:
        avisos.append(f"{len(ciudades)} ciudades distintas y se esperaban {CIUDADES}")

    periodos = {f.get("periodo") for f in filas if f.get("periodo")}
    fuera = periodos - esperados
    if fuera:
        problemas.append(f"{len(fuera)} periodos fuera del rango declarado; "
                         f"ejemplo {sorted(fuera)[0]}")
    huecos = CIUDADES * len(esperados) - len(filas)
    if huecos > 0:
        avisos.append(f"faltan {huecos} filas para un panel balanceado "
                      f"({CIUDADES} x {len(esperados)} = {CIUDADES * len(esperados)})")

    # --- tipos, dominios y vacios
    vacios = Counter()
    for i, fila in enumerate(filas, start=2):
        for campo in OBLIGATORIOS:
            if not (fila.get(campo) or "").strip():
                vacios[campo] += 1
        z = (fila.get("zona") or "").strip()
        if z and z not in ZONAS:
            problemas.append(f"fila {i}: zona no valida '{z}'")
        b = (fila.get("base_ipc") or "").strip()
        if b and b not in BASES:
            avisos.append(f"fila {i}: base_ipc no valida '{b}'")
        fu = (fila.get("fuente_ipc") or "").strip()
        if fu and fu not in FUENTES_IPC:
            avisos.append(f"fila {i}: fuente_ipc no valida '{fu}'")
        for nombre, c in POR_NOMBRE.items():
            valor = (fila.get(nombre) or "").strip()
            if not valor:
                continue
            if c[3] == "entero":
                try:
                    int(valor)
                except ValueError:
                    problemas.append(f"fila {i}: {nombre} no es entero ('{valor}')")
            elif c[3] == "decimal":
                try:
                    float(valor)
                except ValueError:
                    problemas.append(f"fila {i}: {nombre} no es decimal ('{valor}')")
        if len(problemas) > 40:
            problemas.append("... se omiten los problemas restantes")
            break

    for campo, n in vacios.items():
        problemas.append(f"{n} filas con '{campo}' vacio, que es obligatorio")

    # --- informe
    print("=" * 72)
    print(f"VALIDACION DEL PANEL: {ruta}")
    print("=" * 72)
    print(f"filas: {len(filas)}   columnas: {len(filas[0])}   "
          f"ciudades: {len(ciudades)}   periodos: {len(periodos)}")

    if avisos:
        print(f"\nAVISOS ({len(avisos)}):")
        for a in avisos[:15]:
            print(f"  - {a}")
    if problemas:
        print(f"\nPROBLEMAS ({len(problemas)}):")
        for pr in problemas[:25]:
            print(f"  - {pr}")
        print("\nUn panel con problemas no debe usarse para estimar.")
        return 1

    print("\nSin problemas. Los avisos, si los hay, no bloquean pero conviene revisarlos.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plantilla", action="store_true",
                   help="escribir la plantilla CSV y el esquema JSON")
    g.add_argument("--validar", metavar="ARCHIVO",
                   help="validar un panel ya armado contra el esquema")
    args = ap.parse_args()

    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if args.plantilla:
        escribir_plantilla(raiz)
        return 0
    return validar(args.validar)


if __name__ == "__main__":
    sys.exit(main())
