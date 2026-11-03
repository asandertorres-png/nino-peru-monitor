#!/usr/bin/env python3
"""Descarga series del IPC desde la API de estadisticas del BCRP.

La API del BCRP republica series del INEI y no pide API key. Formato:

    https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigos}/json/{desde}/{hasta}

donde {codigos} son uno o varios codigos de serie separados por guion-bajo y
los periodos van como AAAA-M para series mensuales.

AVISO SOBRE EL ESTADO DE ESTE ARCHIVO
-------------------------------------
Los codigos de serie del IPC por ciudad NO estan fijados todavia: la tarea de
la semana 1 del protocolo (docs/tesis/PROTOCOLO.md, seccion 4.1) es
descubrirlos y verificar que exista la desagregacion por grupo de gasto. Para
eso existe el modo --descubrir.

Este script no se pudo ejecutar en el entorno donde fue escrito, porque la
politica de red de esa sesion rechaza estadisticas.bcrp.gob.pe. Hay que
correrlo en la maquina local o en GitHub Actions, y corregir el parser si el
formato real de la respuesta difiere del documentado. Ningun dato de salida
fue generado ni verificado.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
BASE_METADATA = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"

AGENTE = "monitor-nino-peru/tesis (investigacion academica)"
TIEMPO_LIMITE = 120


def _pedir(url):
    """Devuelve el cuerpo de la respuesta como texto."""
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    try:
        with urllib.request.urlopen(peticion, timeout=TIEMPO_LIMITE) as respuesta:
            cruda = respuesta.read()
    except urllib.error.HTTPError as error:
        raise SystemExit(f"HTTP {error.code} al pedir {url}") from error
    except urllib.error.URLError as error:
        raise SystemExit(
            f"No se pudo alcanzar {url}: {error.reason}. "
            "Verificar que la red permita estadisticas.bcrp.gob.pe."
        ) from error
    for codificacion in ("utf-8", "latin-1"):
        try:
            return cruda.decode(codificacion)
        except UnicodeDecodeError:
            continue
    raise SystemExit("No se pudo decodificar la respuesta del BCRP.")


def descubrir(terminos):
    """Lista las series del catalogo del BCRP que contienen todos los terminos.

    El catalogo es un archivo delimitado; no se asume el separador, se prueban
    los habituales y se elige el que produzca mas columnas en la cabecera.
    """
    texto = _pedir(BASE_METADATA)
    lineas = [linea for linea in texto.splitlines() if linea.strip()]
    if not lineas:
        raise SystemExit("El catalogo del BCRP vino vacio.")

    separador = max((";", ",", "\t"), key=lambda s: lineas[0].count(s))
    if lineas[0].count(separador) == 0:
        raise SystemExit(
            "No se reconocio el separador del catalogo. Revisar el formato a mano:\n"
            f"  primera linea: {lineas[0][:200]}"
        )

    buscados = [t.lower() for t in terminos]
    encontradas = 0
    print(f"# catalogo: {len(lineas) - 1} series, separador {separador!r}")
    print(f"# filtro: {' + '.join(buscados)}\n")
    for linea in lineas[1:]:
        minuscula = linea.lower()
        if all(termino in minuscula for termino in buscados):
            campos = [c.strip().strip('"') for c in linea.split(separador)]
            # El codigo de serie es el primer campo en el formato documentado;
            # se imprime la fila completa porque el orden no esta verificado.
            print(" | ".join(campos[:6]))
            encontradas += 1

    print(f"\n# {encontradas} coincidencias")
    if encontradas == 0:
        print(
            "# Sin coincidencias. Probar terminos mas cortos ('ipc', 'cusco'),\n"
            "# o revisar el catalogo directamente en el portal del BCRP."
        )


def descargar(codigos, desde, hasta, salida):
    """Descarga las series indicadas y las guarda como JSON crudo."""
    ruta = "_".join(codigos)
    url = f"{BASE_API}/{ruta}/json/{desde}/{hasta}"
    print(f"pidiendo {url}", file=sys.stderr)
    crudo = _pedir(url)

    try:
        datos = json.loads(crudo)
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"La respuesta no es JSON valido: {error}. "
            f"Primeros 300 caracteres:\n{crudo[:300]}"
        ) from error

    periodos = datos.get("periods")
    if not periodos:
        raise SystemExit(
            "La respuesta no trae el campo 'periods'. Formato inesperado; "
            f"claves presentes: {sorted(datos)}"
        )

    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    with open(salida, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=1)

    nombres = [c.get("name", "?") for c in datos.get("config", {}).get("series", [])]
    print(f"{len(periodos)} periodos, {len(nombres)} series -> {salida}")
    for nombre in nombres:
        print(f"  - {nombre}")


def main():
    analizador = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = analizador.add_subparsers(dest="modo", required=True)

    p_desc = sub.add_parser(
        "descubrir", help="buscar codigos de serie en el catalogo del BCRP"
    )
    p_desc.add_argument(
        "terminos", nargs="+", help="palabras que deben aparecer en la fila"
    )

    p_baj = sub.add_parser("descargar", help="descargar series por codigo")
    p_baj.add_argument("codigos", help="codigos separados por coma")
    p_baj.add_argument("--desde", default="2010-1", help="periodo inicial (AAAA-M)")
    p_baj.add_argument("--hasta", default="2026-9", help="periodo final (AAAA-M)")
    p_baj.add_argument(
        "--salida", default="data/tesis/ipc_crudo.json", help="archivo de salida"
    )

    args = analizador.parse_args()
    if args.modo == "descubrir":
        descubrir(args.terminos)
    else:
        codigos = [c.strip() for c in args.codigos.split(",") if c.strip()]
        if not codigos:
            raise SystemExit("No se indico ningun codigo de serie.")
        descargar(codigos, args.desde, args.hasta, args.salida)


if __name__ == "__main__":
    main()
