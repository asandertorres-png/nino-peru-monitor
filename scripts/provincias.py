"""Provincias del Peru: punto representativo y zona de impacto por provincia.

Lee docs/peru_provincias.geojson (limites provinciales, fuente
juaneladio/peru-geojson, licencia MPL-2.0) y devuelve una lista con la misma
forma que DEPARTAMENTOS en config.py, para que calcular_normales.py y
actualizar.py trabajen igual en ambos niveles.

Punto representativo: el centroide del poligono mayor; si cae fuera (formas
concavas), se usa el vertice mas cercano al centroide. No es la capital
provincial: es un punto dentro de la provincia.

Zona: se hereda del departamento (config.py). Es PROVISIONAL: una provincia
de sierra dentro de un departamento costero hereda "costa_norte" aunque su
regimen sea de sierra. actualizar.py puede corregirla con la altitud del
modelo (ver ZONA_POR_ALTITUD), pero la asignacion fina es trabajo pendiente.
"""
import json
import unicodedata
from pathlib import Path

from config import DEPARTAMENTOS

RAIZ = Path(__file__).resolve().parent.parent
GEOJSON = RAIZ / "docs" / "peru_provincias.geojson"

# Por encima de esta altitud, una provincia de departamento costero se trata
# como sierra. Umbral provisional, por criterio.
ALTITUD_SIERRA_M = 2000


def _sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").upper().strip()


ZONA_DEPARTAMENTO = {_sin_tildes(d["nombre"]): d["zona"] for d in DEPARTAMENTOS}
NOMBRE_DEPARTAMENTO = {_sin_tildes(d["nombre"]): d["nombre"] for d in DEPARTAMENTOS}


def _anillo_exterior_mayor(geom):
    """Anillo exterior del poligono de mayor area (en grados^2, basta para
    elegir)."""
    if geom["type"] == "Polygon":
        return geom["coordinates"][0]
    return max((p[0] for p in geom["coordinates"]), key=_area)


def _area(anillo):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]):
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def _centroide(anillo):
    a = 0.0; cx = 0.0; cy = 0.0
    for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]):
        f = x1 * y2 - x2 * y1
        a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    if abs(a) < 1e-12:
        xs = [p[0] for p in anillo]; ys = [p[1] for p in anillo]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    return cx / (3 * a), cy / (3 * a)


def _dentro(x, y, anillo):
    dentro = False
    for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1]):
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                dentro = not dentro
    return dentro


def punto_representativo(geom):
    anillo = _anillo_exterior_mayor(geom)
    x, y = _centroide(anillo)
    if not _dentro(x, y, anillo):
        x, y = min(anillo, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
    return round(y, 4), round(x, 4)  # lat, lon


def zona_por_altitud(zona, lat, elevacion_m):
    """Corrige la zona heredada con la altitud del modelo, si se conoce."""
    if elevacion_m is None or elevacion_m < ALTITUD_SIERRA_M:
        return zona
    if zona.startswith("costa"):
        return "sierra_norte" if lat > -11 else "sierra_sur"
    return zona


def cargar_provincias():
    """Una entrada por ubigeo. El archivo fuente trae dos provincias partidas
    en dos poligonos, el menor con el nombre mal escrito ("PUIRA" por Piura,
    "VICTOR FAFARDO" por Victor Fajardo): se agrupan por ubigeo y el nombre y
    el punto representativo salen del poligono mayor."""
    g = json.loads(GEOJSON.read_text())
    por_ubigeo = {}
    for f in g["features"]:
        p = f["properties"]
        dep_clave = _sin_tildes(p["FIRST_NOMB"])
        if dep_clave not in ZONA_DEPARTAMENTO:
            raise RuntimeError(f"departamento no reconocido en el GeoJSON: {p['FIRST_NOMB']!r}")
        area = _area(_anillo_exterior_mayor(f["geometry"]))
        previo = por_ubigeo.get(p["FIRST_IDPR"])
        if previo and previo["_area"] >= area:
            continue  # ya tenemos el poligono mayor de este ubigeo
        lat, lon = punto_representativo(f["geometry"])
        por_ubigeo[p["FIRST_IDPR"]] = {
            "ubigeo": p["FIRST_IDPR"],
            "nombre": p["NOMBPROV"].strip().title(),
            "nombre_geo": p["NOMBPROV"],
            "departamento": NOMBRE_DEPARTAMENTO[dep_clave],
            "lat": lat,
            "lon": lon,
            "zona": ZONA_DEPARTAMENTO[dep_clave],
            "_area": area,
        }
    salida = sorted(por_ubigeo.values(), key=lambda d: d["ubigeo"])
    for d in salida:
        d.pop("_area")
    return salida


PROVINCIAS = cargar_provincias()


if __name__ == "__main__":
    for d in PROVINCIAS:
        print(f"{d['ubigeo']} {d['nombre']:<22} {d['departamento']:<14} "
              f"{d['lat']:>8.4f} {d['lon']:>9.4f} {d['zona']}")
    print(len(PROVINCIAS), "provincias")
