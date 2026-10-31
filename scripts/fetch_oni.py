"""Descarga el indice ONI (Oceanic Nino Index) de la NOAA/CPC.

El ONI es la media movil trimestral de la anomalia de TSM en la region
Nino 3.4. Es el indicador oficial de la NOAA para declarar El Nino / La Nina.
Para el Peru conviene complementarlo con el ICEN del ENFEN (region Nino 1+2),
que captura mejor el Nino costero; ver docs/METODOLOGIA.md.
"""
import json
import urllib.request
from pathlib import Path

from config import URL_ONI, clasificar_oni

RAIZ = Path(__file__).resolve().parent.parent


def descargar_oni():
    with urllib.request.urlopen(URL_ONI, timeout=60) as r:
        texto = r.read().decode("utf-8")

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
    return serie


def main():
    serie = descargar_oni()
    ultimo = serie[-1]
    salida = {
        "fuente": "NOAA CPC - Oceanic Nino Index (region Nino 3.4)",
        "url": URL_ONI,
        "ultimo": {
            **ultimo,
            "estado": clasificar_oni(ultimo["oni"]),
        },
        "serie": serie[-60:],  # ultimos 5 anios de trimestres moviles
    }
    destino = RAIZ / "data" / "oni.json"
    destino.write_text(json.dumps(salida, ensure_ascii=False, indent=2))
    print(f"ONI {ultimo['trimestre']} {ultimo['anio']}: {ultimo['oni']:+.2f} "
          f"({salida['ultimo']['estado']})")


if __name__ == "__main__":
    main()
