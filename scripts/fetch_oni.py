"""Descarga el ONI (trimestral) y la TSM semanal de la region Nino 3.4 (NOAA/CPC).

- ONI: media movil trimestral de la anomalia de TSM en Nino 3.4, base 1991-2020.
  Se actualiza una vez al mes. Es el indicador oficial de la NOAA.
- TSM semanal Nino 3.4 (archivo wksst): valor de la semana mas reciente. Se
  actualiza los lunes. Es mas fresco que el ONI, pero no es el ONI.

Para el Peru conviene complementarlo con el ICEN del ENFEN (region Nino 1+2),
que captura mejor el Nino costero; ver docs/METODOLOGIA.md.

Advertencia sobre el archivo semanal: el orden de columnas del archivo
wksst no se pudo verificar al escribir este script (el servidor de la NOAA no
era accesible desde el entorno de desarrollo). Por eso parsear_semanal() valida
los valores con rangos fisicos y, si no encajan, no publica la TSM semanal:
deja null y el motivo en semanal_error. Antes de confiar en el valor, comprobar
una vez con: curl -sS URL_WKSST | tail -5
"""
import json
import re
from pathlib import Path

from clima_api import descargar
from config import URL_ONI, URL_WKSST, clasificar_oni

RAIZ = Path(__file__).resolve().parent.parent

# Supuesto a verificar: tras la fecha, los valores vienen por region en el
# orden SST / anomalia para Nino 1+2, Nino 3, Nino 3.4 y Nino 4. Con ese orden,
# la SST de 3.4 es el indice 4 y su anomalia el 5.
IDX_SST_34, IDX_ANOM_34 = 4, 5
N_COLUMNAS_MIN = 8
_FILA_FECHA = re.compile(r"^\s*(\d{2}-[A-Za-z]{3}-\d{4})\s+(.*\S)\s*$")


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
        try:
            nums = [float(x) for x in m.group(2).split()]
        except ValueError:
            continue
        if len(nums) >= N_COLUMNAS_MIN:
            filas.append((m.group(1), nums))
    if not filas:
        raise ValueError("no encontre filas con fecha y valores numericos")

    fecha, nums = filas[-1]
    sst, anom = nums[IDX_SST_34], nums[IDX_ANOM_34]
    # Guardas de plausibilidad: si el orden de columnas no es el supuesto, la
    # SST no caera en 20-33 °C o la anomalia no sera de pocos grados.
    if not 20.0 <= sst <= 33.0:
        raise ValueError(f"SST Nino 3.4 implausible ({sst}); revisar columnas")
    if not -6.0 <= anom <= 6.0:
        raise ValueError(f"anomalia Nino 3.4 implausible ({anom}); revisar columnas")
    return {"semana_hasta": fecha, "tsm": sst, "anomalia": anom,
            "fuente": "NOAA CPC - wksst, Nino 3.4 semanal (base 1991-2020)"}


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
        print(f"TSM semanal Nino 3.4 al {semanal['semana_hasta']}: "
              f"{semanal['anomalia']:+.2f} °C")


if __name__ == "__main__":
    main()
