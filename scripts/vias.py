"""Red vial principal y vias con transito interrumpido.

Fuentes candidatas (todas abiertas, sin clave):
- Red Vial Nacional del MTC, servida como ArcGIS REST por la IDEP del IGN
  (INSTITUCIONALES/MTC/MapServer) y por Provias Nacional (giserver.proviasnac.gob.pe).
- Vias interrumpidas: Provias Nacional / Sutran / COEN-INDECI, segun lo que
  exponga un servicio consultable; --inspeccionar lo averigua en el runner.
- Respaldo para la red principal: OpenStreetMap via Overpass (motorway, trunk, primary).

Uso:
    PYTHONPATH=scripts python3 scripts/vias.py --inspeccionar   # prueba los endpoints y describe capas
    PYTHONPATH=scripts python3 scripts/vias.py                  # (pendiente) escribe docs/vias_principales.geojson y data/vias_bloqueadas.json
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CABECERAS = {"User-Agent": "nino-peru-monitor (datos abiertos, uso no comercial)"}

# Raices de servicios ArcGIS REST que podrian tener la red vial o las emergencias
RAICES_ARCGIS = [
    "https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer",
    "https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/FeatureServer",
    "https://giserver.proviasnac.gob.pe/arcgis/rest/services",
    "https://giserver.proviasnac.gob.pe/arcgis/rest/services/PROVIAS",
    "https://giserver.proviasnac.gob.pe/arcgis/rest/services/PROVIAS/MTC_Itinerario/MapServer",
    "https://sigrid.cenepred.gob.pe/arcgis/rest/services",
    "https://sigrid.cenepred.gob.pe/arcgis/rest/services/Elementos_Expuestos/MapServer/2060300",
    "https://geoportal.mtc.gob.pe/server/rest/services",
    "https://geoportal.mtc.gob.pe/arcgis/rest/services",
    "https://portal.mtc.gob.pe/arcgis/rest/services",
    "https://www.sutran.gob.pe/arcgis/rest/services",
    "https://sinpad2.indeci.gob.pe/arcgis/rest/services",
]
# Consultas de conteo sobre capas conocidas de la red vial nacional
CAPAS_RED = [
    "https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer/10",
    "https://sigrid.cenepred.gob.pe/arcgis/rest/services/Elementos_Expuestos/MapServer/2060300",
]
OVERPASS = "https://overpass-api.de/api/interpreter"
PAGINAS = [
    "https://www.gob.pe/sutran",
    "https://www.sutran.gob.pe/",
    "https://www.pvn.gob.pe/",
    "https://www.gob.pe/institucion/pvn/informes-publicaciones",
]


def pedir(url, timeout=60, datos=None):
    req = urllib.request.Request(url, headers=CABECERAS, data=datos)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def describir_json(url):
    try:
        st, ct, b = pedir(url + ("&" if "?" in url else "?") + "f=json")
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"
    except Exception as e:
        return f"error: {e}"
    try:
        doc = json.loads(b.decode("utf-8", "replace"))
    except ValueError:
        return f"{st} {ct}: no es JSON ({len(b)} bytes)"
    if "error" in doc:
        return f"error del servicio: {doc['error']}"
    partes = []
    for k in ("folders", "services", "layers", "tables"):
        if k in doc:
            items = doc[k]
            if isinstance(items, list):
                desc = [i if isinstance(i, str) else f"{i.get('id', '')}:{i.get('name', '')}({i.get('type', '')})" for i in items[:60]]
                partes.append(f"{k}[{len(items)}]: " + ", ".join(desc))
    for k in ("name", "type", "geometryType", "description", "copyrightText", "currentVersion"):
        if k in doc and doc[k]:
            partes.append(f"{k}={str(doc[k])[:120]}")
    if "fields" in doc:
        partes.append("fields: " + ", ".join(f"{f.get('name')}({f.get('type', '')[13:]})" for f in doc["fields"][:40]))
    return " | ".join(partes) if partes else json.dumps(doc)[:300]


def contar(url_capa):
    q = url_capa + "/query?" + urllib.parse.urlencode({"where": "1=1", "returnCountOnly": "true", "f": "json"})
    try:
        st, ct, b = pedir(q)
        return json.loads(b.decode("utf-8", "replace"))
    except Exception as e:
        return f"error: {e}"


def muestra(url_capa):
    q = url_capa + "/query?" + urllib.parse.urlencode({"where": "1=1", "outFields": "*", "resultRecordCount": "2",
                                                       "returnGeometry": "false", "f": "json"})
    try:
        st, ct, b = pedir(q)
        doc = json.loads(b.decode("utf-8", "replace"))
        return json.dumps(doc.get("features", [])[:2], ensure_ascii=False)[:700]
    except Exception as e:
        return f"error: {e}"


def inspeccionar():
    print("== raices ArcGIS REST ==", flush=True)
    for u in RAICES_ARCGIS:
        print(f"- {u}\n    {describir_json(u)}", flush=True)
        time.sleep(0.5)
    print("== capas conocidas de la red vial ==", flush=True)
    for u in CAPAS_RED:
        print(f"- {u}\n    conteo: {contar(u)}\n    muestra: {muestra(u)}", flush=True)
    print("== Overpass (OSM): conteo de vias principales en Peru ==", flush=True)
    consulta = '[out:json][timeout:120];area["ISO3166-1"="PE"][admin_level=2]->.pe;way["highway"~"^(motorway|trunk|primary)$"](area.pe);out count;'
    try:
        st, ct, b = pedir(OVERPASS, timeout=180, datos=urllib.parse.urlencode({"data": consulta}).encode())
        print("    " + b.decode("utf-8", "replace")[:400], flush=True)
    except Exception as e:
        print(f"    error: {e}", flush=True)
    print("== paginas institucionales (solo codigo de respuesta y pistas de mapas) ==", flush=True)
    for u in PAGINAS:
        try:
            st, ct, b = pedir(u, timeout=40)
            t = b.decode("utf-8", "replace").lower()
            pistas = [p for p in ("arcgis", "featureserver", "mapserver", "geojson", "leaflet", "mapbox", "google.com/maps", "estado de las v", "interrumpid", "bloquead") if p in t]
            print(f"- {u}: {st}, {len(b)} bytes, pistas: {pistas}", flush=True)
            for p in ("arcgis.com", "featureserver", "mapserver"):
                i = t.find(p)
                if i >= 0:
                    print("    ..." + t[max(0, i - 150):i + 150].replace("\n", " ") + "...", flush=True)
        except Exception as e:
            print(f"- {u}: error {e}", flush=True)


def main():
    if "--inspeccionar" in sys.argv:
        inspeccionar()
        print("modo inspeccion: no se escribe nada", flush=True)
        return
    raise SystemExit("el modo de calculo se completa despues de la inspeccion (ver docstring)")


if __name__ == "__main__":
    main()
