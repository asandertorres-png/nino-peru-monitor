"""Descarga el ONI (trimestral) y la TSM semanal de la region Nino 3.4 (NOAA/CPC).

- ONI: media movil trimestral de la anomalia de TSM en Nino 3.4, base 1991-2020.
  Se actualiza una vez al mes. Es el indicador oficial de la NOAA.
- TSM semanal Nino 3.4 (archivo wksst): valor de la semana mas reciente. Se
  actualiza los lunes. Es mas fresco que el ONI, pero no es el ONI.

Para el Peru conviene complementarlo con el ICEN del ENFEN (region Nino 1+2),
que captura mejor el Nino costero; ver docs/METODOLOGIA.md.

Formato del archivo wksst (verificado con una muestra real de la NOAA):
  - encabezado con Nino1+2, Nino3, Nino34 y Nino4, cada uno con SST y SSTA;
  - cada fila empieza con la fecha de la semana CENTRADA, como 28OCT2026;
  - los valores son de ancho fijo: la anomalia negativa va pegada a la SST
    ("24.8-0.1") y la positiva lleva espacio ("26.0 5.3"). Por eso se extraen
    con una expresion regular y no partiendo por espacios.
"""
import json
import re
from datetime import datetime
from pathlib import Path

from clima_api import descargar
from config import URL_ONI, URL_WKSST, clasificar_oni

RAIZ = Path(__file__).resolve().parent.parent

# Orden de columnas tras la fecha: SST/SSTA de Nino 1+2, 3, 3.4 y 4.
REGIONES = (("nino12", 0), ("nino3", 2), ("nino34", 4), ("nino4", 6))
IDX_SST_34, IDX_ANOM_34 = 4, 5
N_COLUMNAS_MIN = 8
_FILA_FECHA = re.compile(r"^\s*(\d{2}[A-Z]{3}\d{4})\s+(.*\S)\s*$")
_VALOR = re.compile(r"-?\d+\.\d")


def descargar_oni():
    texto = descargar(URL_ONI, timeout=60, sangria="  ")

    serie = []
    for linea in texto.strip().splitlines()[1:]:
        partes = linea.split()
        if len(partes) != 4:
            continue
        trimestre, anio, tsm, anomalia = partes
        serie.append({
            "trimestre": trimestre,
            "anio": int(anio),
            "tsm": float(tsm),
            "oni": float(anomalia),
        })
    if not serie:
        raise SystemExit(f"no pude interpretar ninguna fila de {URL_ONI}")
    return serie


def parsear_semanal(texto):
    """Devuelve la TSM semanal Nino 3.4 mas reciente, o lanza ValueError si el
    archivo no encaja con el formato supuesto o los valores no son plausibles."""
    filas = []
    for linea in texto.splitlines():
        m = _FILA_FECHA.match(linea)
        if not m:
            continue
        nums = [float(x) for x in _VALOR.findall(m.group(2))]
        if len(nums) >= N_COLUMNAS_MIN:
            filas.append((m.group(1), nums))
    if not filas:
        raise ValueError("no encontre filas con fecha y valores numericos")

    fecha_txt, nums = filas[-1]
    fecha = datetime.strptime(fecha_txt, "%d%b%Y").date().isoformat()
    # Guardas de plausibilidad: si el orden de columnas no es el supuesto, una
    # SST no caera en 15-33 °C o una anomalia no sera de pocos grados.
    regiones = {}
    for nombre, i in REGIONES:
        sst, anom = nums[i], nums[i + 1]
        if not 15.0 <= sst <= 33.0:
            raise ValueError(f"SST {nombre} implausible ({sst}); revisar columnas")
        if not -6.0 <= anom <= 6.0:
            raise ValueError(f"anomalia {nombre} implausible ({anom}); revisar columnas")
        regiones[nombre] = {"tsm": sst, "anomalia": anom}
    # tsm/anomalia a secas siguen siendo Nino 3.4 (compatibilidad con la interfaz)
    return {"semana_centrada": fecha, "tsm": nums[IDX_SST_34], "anomalia": nums[IDX_ANOM_34],
            "regiones": regiones,
            "fuente": "NOAA CPC - wksst, TSM semanal por region Nino (base 1991-2020)"}


def obtener_semanal():
    """Devuelve (dato, error). Nunca lanza: el ONI no debe caerse por esto."""
    try:
        texto = descargar(URL_WKSST, intentos=3, timeout=60, sangria="  ")
        return parsear_semanal(texto), None
    except Exception as e:  # red, formato o plausibilidad: se reporta, no se oculta
        return None, f"{type(e).__name__}: {e}"


def main():
    serie = descargar_oni()
    ultimo = serie[-1]
    semanal, semanal_error = obtener_semanal()
    if semanal_error:
        print(f"aviso: TSM semanal no publicada ({semanal_error})")
    salida = {
        "fuente": "NOAA CPC - Oceanic Nino Index (region Nino 3.4)",
        "url": URL_ONI,
        "frecuencia": "trimestral (media movil de 3 meses)",
        "ultimo": {
            **ultimo,
            "estado": clasificar_oni(ultimo["oni"]),
        },
        "semanal": semanal,
        "semanal_error": semanal_error,
        "serie": serie[-60:],  # ultimos 5 anios de trimestres moviles
    }
    destino = RAIZ / "data" / "oni.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2))
    print(f"ONI {ultimo['trimestre']} {ultimo['anio']}: {ultimo['oni']:+.2f} "
          f"({salida['ultimo']['estado']})")
    if semanal:
        r = semanal["regiones"]
        print(f"TSM semanal, semana centrada en {semanal['semana_centrada']}: "
              f"Nino 1+2 {r['nino12']['anomalia']:+.1f} | Nino 3 {r['nino3']['anomalia']:+.1f} | "
              f"Nino 3.4 {r['nino34']['anomalia']:+.1f} | Nino 4 {r['nino4']['anomalia']:+.1f} °C")


if __name__ == "__main__":
    main()
