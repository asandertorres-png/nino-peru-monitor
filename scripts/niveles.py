"""Niveles de analisis del monitor: departamento (25) y provincia (196).

Cada unidad es un dict con al menos nombre, lat, lon y zona. Los departamentos
se identifican por nombre (compatibilidad con los JSON ya publicados); las
provincias, por su codigo ubigeo de cuatro digitos.
"""
import sys
from pathlib import Path

from config import DEPARTAMENTOS

RAIZ = Path(__file__).resolve().parent.parent
NIVELES = ("departamento", "provincia")


def nivel_desde_argv(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--nivel" in argv:
        n = argv[argv.index("--nivel") + 1]
        if n not in NIVELES:
            raise SystemExit(f"--nivel debe ser uno de {NIVELES}")
        return n
    return "departamento"


def unidades(nivel):
    if nivel == "departamento":
        return DEPARTAMENTOS
    from provincias import PROVINCIAS
    return PROVINCIAS


def clave(nivel, unidad):
    return unidad["nombre"] if nivel == "departamento" else unidad["ubigeo"]


def rutas(nivel):
    sufijo = "" if nivel == "departamento" else "_provincias"
    return {
        "normales": RAIZ / "data" / f"normales{sufijo}.json",
        "parcial": RAIZ / "data" / f".normales{sufijo}_parcial.json",
        "estado": RAIZ / "data" / f"estado{sufijo}.json",
    }
