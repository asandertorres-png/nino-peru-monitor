#!/usr/bin/env python3
"""Genera la matriz de operacionalizacion como CSV.

La fuente de verdad es docs/tesis/OPERACIONALIZACION.md; este script la vuelca
a hoja de calculo para pegarla como tabla en el documento de tesis. Si se
cambia una ficha en el markdown, hay que cambiarla aqui y volver a correr.

Salida: docs/tesis/matriz_operacionalizacion.csv

El separador es punto y coma y la codificacion utf-8 con BOM, que es lo que
Excel en configuracion regional en espaniol abre sin pedir importacion.

Uso:
    python scripts/tesis/matriz.py
"""

import csv
import os

CAMPOS = [
    "Variable",
    "Dimension",
    "Codigo",
    "Indicador",
    "Definicion operacional / formula",
    "Unidad",
    "Escala",
    "Fuente",
    "Periodicidad",
    "Estado de la fuente",
    "Hipotesis",
]

X = "X. Shock exogeno de oferta de origen ENSO"
Y = "Y. Precios de alimentos al consumidor urbano"

FILAS = [
    # ---------------- X: D1 magnitud ----------------
    (X, "D1 Magnitud", "X1", "Anomalia estandarizada de precipitacion",
     "A_pp(c,t) = (PP(c,t) - mu_pp(c,m)) / sigma_pp(c,m); base 1991-2020",
     "desviaciones estandar", "Razon", "ERA5 / ERA5-Land (Open-Meteo Archive)",
     "Mensual", "BLOQUEADO: sigma no existe en normales.json; requiere tarea 0",
     "H1, H2, H6"),
    (X, "D1 Magnitud", "X2", "Anomalia estandarizada de temperatura maxima",
     "A_tx(c,t) = (TX(c,t) - mu_tx(c,m)) / sigma_tx(c,m); base 1991-2020",
     "desviaciones estandar", "Razon", "ERA5 / ERA5-Land",
     "Mensual", "BLOQUEADO: tmax indexado solo por mes del anio; requiere tarea 0",
     "H1, H2, H6"),

    # ---------------- X: D2 signo ----------------
    (X, "D2 Signo", "X3", "Exceso de lluvia",
     "A_pp_pos(c,t) = max(A_pp(c,t), 0)",
     "desviaciones estandar", "Razon", "ERA5 / ERA5-Land",
     "Mensual", "BLOQUEADO: derivado de X1", "H4"),
    (X, "D2 Signo", "X4", "Deficit de lluvia",
     "A_pp_neg(c,t) = max(-A_pp(c,t), 0)",
     "desviaciones estandar", "Razon", "ERA5 / ERA5-Land",
     "Mensual", "BLOQUEADO: derivado de X1", "H4"),
    (X, "D2 Signo", "X5", "Exceso de calor",
     "A_tx_pos(c,t) = max(A_tx(c,t), 0)",
     "desviaciones estandar", "Razon", "ERA5 / ERA5-Land",
     "Mensual", "BLOQUEADO: derivado de X2", "H4"),

    # ---------------- X: D3 persistencia ----------------
    (X, "D3 Persistencia", "X6", "Racha de meses consecutivos sobre umbral",
     "Meses consecutivos terminados en t con |A(c,.)| >= 1, por signo. "
     "Umbral 1 sigma, convencional; contraste externo: criterio ENFEN de 3 meses",
     "numero de meses", "Razon", "ERA5, NOAA/CPC",
     "Mensual", "BLOQUEADO: derivado de X1 y X2", "H4b"),
    (X, "D3 Persistencia", "X7", "Shock acumulado a 3, 6 y 12 meses",
     "S_k(c,t) = suma de A(c,t-j) para j = 0..k-1, con k = 3, 6, 12",
     "desviaciones estandar acumuladas", "Razon", "ERA5, NOAA/CPC",
     "Mensual", "BLOQUEADO: derivado de X1 y X2", "H4b"),

    # ---------------- X: D4 anticipacion ----------------
    (X, "D4 Anticipacion", "X8", "ONI rezagado",
     "ONI(t-k), k = 0..12. Media movil trimestral de la anomalia de TSM de la "
     "region Nino 3.4, base 1991-2020, criterio NOAA",
     "grados Celsius", "Razon", "NOAA/CPC",
     "Mensual (trimestre movil)",
     "PARCIAL: la serie guardada arranca en 2021; extender a 1950", "H1, H3"),
    (X, "D4 Anticipacion", "X9", "ICEN-replica rezagado",
     "ICEN*(t) = (1/3) * suma de a_12(t-j) para j = 0..2, donde a_12 es la "
     "anomalia mensual de TSM de la region Nino 1+2",
     "grados Celsius", "Razon", "NOAA/CPC (indices Nino 1+2)",
     "Mensual",
     "PARCIAL: calculable; falta validar contra informes del IGP. Nombre "
     "provisional obligatorio hasta esa validacion", "H1, H3"),
    (X, "D4 Anticipacion", "X10", "Aviso del ENFEN",
     "Indicadora = 1 en el mes de un pronunciamiento que declara o eleva el "
     "estado de alerta. Unico indicador estrictamente informacional del conjunto",
     "dicotomica", "Nominal", "Comunicados oficiales del ENFEN",
     "Por evento",
     "NO VERIFICADO: disponibilidad historica y codificacion consistente", "H1"),
    (X, "D4 Anticipacion", "X11", "Antelacion del aviso",
     "Dias entre el aviso (X10 = 1) y el primer mes con |A(c,.)| >= 1 en la "
     "unidad c. Puede ser negativa, y ese caso es informativo",
     "dias", "Intervalo", "ENFEN, ERA5",
     "Por evento", "NO VERIFICADO: depende de X10", "H1"),

    # ---------------- X: D5 exposicion ----------------
    (X, "D5 Exposicion economica", "X12",
     "Peso del sector primario en el VAB departamental",
     "E1(d) = (VAB agropecuario(d) + VAB pesca(d)) / VAB total(d)",
     "porcentaje", "Razon", "INEI, cuentas nacionales departamentales",
     "Anual", "NO VERIFICADO: ruta de descarga en formato utilizable", "H2"),
    (X, "D5 Exposicion economica", "X13",
     "Peso del alimento en la canasta del IPC de la ciudad",
     "E2(c) = ponderacion de la division 01 (alimentos y bebidas no "
     "alcoholicas) en la estructura del IPC de la ciudad c",
     "porcentaje", "Razon", "INEI, estructura de ponderaciones del IPC",
     "Por cambio de base",
     "EN RIESGO: si solo existe para Lima Metropolitana no hay variacion entre "
     "ciudades; plan alternativo es el peso nacional, declarando la perdida",
     "H2"),
    (X, "D5 Exposicion economica", "X14",
     "Sensibilidad climatica estimada (exposicion continua)",
     "beta(c) de A_pp(c,tau) = alfa(c) + beta(c)*ONI(tau) + error, estimado "
     "SOLO en 1991-2020, fuera del periodo de estimacion de la tesis",
     "coeficiente", "Razon", "Derivado de ERA5 y NOAA",
     "Fijo por unidad", "BLOQUEADO: requiere el panel climatico (tarea 0)", "H2"),
    (X, "D5 Exposicion economica", "X15",
     "Aislamiento respecto de zonas productoras",
     "Distancia o indice de conectividad entre la ciudad y su principal zona "
     "abastecedora",
     "kilometros o indice", "Razon", "Por definir",
     "Fijo por unidad",
     "EN RIESGO: falta el dato de que zona abastece a cada ciudad (flujos "
     "comerciales). Sustituto admisible con supuesto declarado", "H2, H5"),

    # ---------------- X: D6 calendario ----------------
    (X, "D6 Calendario productivo", "X16",
     "Fase del calendario agricola de la zona abastecedora",
     "Categorica: siembra, crecimiento, cosecha, poscosecha. Interactua con "
     "X1-X5",
     "cuatro categorias", "Nominal",
     "MIDAGRI, calendario de siembras y cosechas",
     "Mensual", "NO VERIFICADO: depende de X15", "H4b"),

    # ---------------- Y: D1 nivel ----------------
    (Y, "D1 Nivel y tendencia", "Y1", "Inflacion mensual de alimentos",
     "pi(c,t) = ln(IPC_alim(c,t)) - ln(IPC_alim(c,t-1))",
     "porcentaje", "Razon", "INEI, IPC de 26 ciudades",
     "Mensual",
     "EN RIESGO Y DECIDE EL DISENO: que el IPC exista por ciudad y por "
     "division de gasto", "H1-H4"),
    (Y, "D1 Nivel y tendencia", "Y2", "Inflacion a 12 meses",
     "pi12(c,t) = ln(IPC_alim(c,t)) - ln(IPC_alim(c,t-12))",
     "porcentaje", "Razon", "INEI", "Mensual",
     "EN RIESGO: derivado de Y1", "H1-H4"),
    (Y, "D1 Nivel y tendencia", "Y3",
     "Nivel acumulado del log del indice",
     "p(c,t+h) - p(c,t-1), con p = ln(IPC_alim). Es la dependiente de las "
     "proyecciones locales: interesa cuanto mas caro esta el alimento h meses "
     "despues, no la tasa de ese mes",
     "logaritmo", "Razon", "INEI", "Mensual",
     "EN RIESGO: derivado de Y1", "H1, H2"),

    # ---------------- Y: D2 volatilidad ----------------
    (Y, "D2 Volatilidad", "Y4", "Desviacion estandar movil de 12 meses",
     "Desviacion estandar de pi(c,.) en la ventana de los 12 meses terminados "
     "en t",
     "porcentaje", "Razon", "Derivado de Y1", "Mensual",
     "DERIVADO: disponible en cuanto exista Y1", "H4b"),
    (Y, "D2 Volatilidad", "Y5", "Varianza condicional GARCH",
     "h(c,t) de un GARCH(1,1) sobre pi(c,t). Con T = 200 por ciudad es "
     "estimable pero justo; se reporta como contraste de Y4",
     "varianza", "Razon", "Derivado de Y1", "Mensual",
     "DERIVADO: disponible en cuanto exista Y1", "H4b"),

    # ---------------- Y: D3 picos ----------------
    (Y, "D3 Picos", "Y6", "Indicador de pico",
     "1 si pi(c,t) > percentil 90 de la distribucion PROPIA de la ciudad. El "
     "percentil es propio y no comun para no confundir ciudad volatil con mes "
     "extremo",
     "dicotomica", "Nominal", "Derivado de Y1", "Mensual",
     "DERIVADO: disponible en cuanto exista Y1", "H4b"),
    (Y, "D3 Picos", "Y7", "Magnitud del exceso sobre el percentil 90",
     "max(pi(c,t) - percentil90(pi(c,.)), 0)",
     "porcentaje", "Razon", "Derivado de Y1", "Mensual",
     "DERIVADO: disponible en cuanto exista Y1", "H4b"),

    # ---------------- Y: D4 traspaso ----------------
    (Y, "D4 Traspaso", "Y8",
     "Elasticidad del IPC general respecto del de alimentos",
     "lambda en: d ln IPC_gen(c,t) = kappa(c) + lambda * d ln IPC_alim(c,t) + "
     "controles. Referencia de magnitud: traspaso incompleto de uno a seis "
     "trimestres (Jalil y Tamayo 2011)",
     "coeficiente", "Razon", "INEI, BCRP", "Mensual",
     "NO VERIFICADO: IPC general por ciudad", "Supuesto P8"),
    (Y, "D4 Traspaso", "Y9",
     "Elasticidad del IPC subyacente respecto del de alimentos",
     "Igual que Y8 reemplazando el general por el subyacente",
     "coeficiente", "Razon", "INEI, BCRP", "Mensual",
     "EN RIESGO: el subyacente por ciudad es dudoso; si no existe se elimina",
     "Supuesto P8"),

    # ---------------- Y: D5 integracion ----------------
    (Y, "D5 Integracion espacial", "Y10",
     "Correlacion movil entre pares de ciudades",
     "Correlacion de pi entre las ciudades c y c' en la ventana de 12 meses "
     "terminada en t; se resume por ciudad como la media de sus correlaciones "
     "con las demas",
     "coeficiente", "Razon", "Derivado de Y1", "Mensual",
     "DERIVADO: no requiere ningun dato que el panel de precios no tenga ya",
     "H5"),
    (Y, "D5 Integracion espacial", "Y11", "Ancho de la banda neutral",
     "Umbral estimado en un modelo de correccion de error con umbral (TVECM) "
     "por par de ciudades. Representa los costos de transaccion",
     "porcentaje", "Razon", "Derivado de Y1 y del nivel del indice", "Mensual",
     "DERIVADO: disponible en cuanto exista Y1", "H5"),
]


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    salida = os.path.join(raiz, "docs", "tesis",
                          "matriz_operacionalizacion.csv")
    os.makedirs(os.path.dirname(salida), exist_ok=True)

    for i, fila in enumerate(FILAS):
        if len(fila) != len(CAMPOS):
            raise SystemExit(
                f"La fila {i} tiene {len(fila)} campos y se esperaban "
                f"{len(CAMPOS)}: {fila[:3]}")

    # utf-8-sig para que Excel lo abra directo; delimitador punto y coma.
    with open(salida, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        escritor.writerow(CAMPOS)
        escritor.writerows(FILAS)

    x = sum(1 for f in FILAS if f[0] == X)
    print(f"{len(FILAS)} indicadores ({x} de X, {len(FILAS) - x} de Y) -> {salida}")


if __name__ == "__main__":
    main()
