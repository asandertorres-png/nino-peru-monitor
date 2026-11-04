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
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CABECERAS = {"User-Agent": "nino-peru-monitor (datos abiertos, uso no comercial)"}

# Raices de servicios ArcGIS REST que podrian tener la red vial o las emergencias
# Segunda ronda: la IDEP responde (capas 8, 9 y 10 del MTC); Provias y el
# geoportal del MTC no (timeout / 403). SIGRID tiene carpetas FEN, INDECI y
# sigrid que conviene listar. El mapa de alertas de Sutran vive en
# gis.sutran.gob.pe y hay que ver a que servicio le pide los datos.
# Tercera ronda: la Red Vial Nacional de la IDEP son 11 multilineas enormes
# (61 MB una sola): se prueba la generalizacion del servidor (maxAllowableOffset)
# para ver a que tamano queda el pais entero. SIGRID expone el mapa operativo
# del COEN para el FEN 2026-27 (sectores/COEN_FEN_2027) con capas MTC, puntos
# criticos e intervenciones: se describen con conteo y muestra. El mapa de
# Sutran sirve HTTPS con certificado autofirmado, que no se acepta; se prueba
# si responde por HTTP plano.
COEN = "https://sigrid.cenepred.gob.pe/arcgis/rest/services/sectores/COEN_FEN_2027/MapServer"
RAICES_ARCGIS = [f"{COEN}/{i}" for i in (3, 24, 25, 55, 56, 52, 27, 30, 16, 21)]
CAPAS_RED = [f"{COEN}/{i}" for i in (3, 24, 25, 55, 52)]
RED_NACIONAL = "https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer/10"
OVERPASS = "https://overpass-api.de/api/interpreter"
PAGINAS = [
    "https://gis.sutran.gob.pe/alerta_sutran/",
]
# Certificado del mapa de Sutran (autofirmado), fijado en el repositorio tras
# leerlo con openssl en la inspeccion: la verificacion TLS sigue activa, pero
# contra ese certificado concreto y solo para ese host.
CERT_SUTRAN = RAIZ / "scripts" / "certs" / "gis_sutran.pem"
SALIDA_RED = RAIZ / "docs" / "vias_principales.geojson"
SALIDA_BLOQUEOS = RAIZ / "data" / "vias_bloqueadas.json"
OFFSET_RED = 0.005   # generalizacion del servidor (grados, ~500 m): 220 KB para todo el pais


def pedir(url, timeout=60, datos=None):
    req = urllib.request.Request(url, headers=CABECERAS, data=datos)
    ctx = None
    if "gis.sutran.gob.pe" in url and CERT_SUTRAN.exists():
        import ssl
        ctx = ssl.create_default_context(cafile=str(CERT_SUTRAN))
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read()


def certificado_sutran():
    """Imprime el certificado que presenta gis.sutran.gob.pe (solo lectura, con openssl)."""
    import subprocess
    try:
        out = subprocess.run(["openssl", "s_client", "-connect", "gis.sutran.gob.pe:443", "-servername", "gis.sutran.gob.pe", "-showcerts"],
                             input="", capture_output=True, text=True, timeout=40).stdout
    except Exception as e:
        print(f"    openssl: {e}", flush=True)
        return
    import re as _re
    certs = _re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", out, _re.S)
    print(f"    certificados presentados: {len(certs)}", flush=True)
    for line in out.splitlines():
        if line.strip().startswith(("subject=", "issuer=", "Verify return code", "depth=")):
            print("    " + line.strip()[:160], flush=True)
    for c in certs:
        try:
            det = subprocess.run(["openssl", "x509", "-noout", "-subject", "-issuer", "-dates", "-fingerprint", "-sha256"],
                                 input=c, capture_output=True, text=True, timeout=20).stdout
            print("    " + det.replace("\n", " | ")[:400], flush=True)
        except Exception:
            pass
        print(c, flush=True)


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
    if doc.get("fields"):
        partes.append("fields: " + ", ".join(f"{f.get('name')}({(f.get('type') or '')[13:]})" for f in doc["fields"][:40]))
    for k in ("subLayers", "parentLayer"):
        if doc.get(k):
            partes.append(f"{k}={json.dumps(doc[k], ensure_ascii=False)[:200]}")
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


def geometria_muestra(url_capa):
    """Una geometria en WGS84 y en GeoJSON, para saber que formatos acepta el servicio."""
    salida = []
    for params in ({"f": "geojson", "outSR": "4326"}, {"f": "json", "outSR": "4326"}):
        q = url_capa + "/query?" + urllib.parse.urlencode({"where": "1=1", "outFields": "cCodRuta,NOMBDEP", "resultRecordCount": "1",
                                                           "returnGeometry": "true", **params})
        try:
            st, ct, b = pedir(q)
            t = b.decode("utf-8", "replace")
            salida.append(f"{params['f']}: {len(b)} bytes :: {t[:260]}")
        except Exception as e:
            salida.append(f"{params['f']}: error {e}")
    return " || ".join(salida)


def listar_servicios(raiz):
    """Lista los servicios de una carpeta ArcGIS y las capas de cada uno (nombres)."""
    try:
        st, ct, b = pedir(raiz + "?f=json")
        doc = json.loads(b.decode("utf-8", "replace"))
    except Exception as e:
        print(f"    error: {e}", flush=True)
        return
    for svc in doc.get("services", [])[:60]:
        nombre, tipo = svc.get("name"), svc.get("type")
        base = raiz.rsplit("/services", 1)[0] + "/services/" + nombre + "/" + tipo
        try:
            st, ct, b = pedir(base + "?f=json", timeout=40)
            d = json.loads(b.decode("utf-8", "replace"))
            capas = ", ".join(f"{l.get('id')}:{l.get('name')}" for l in d.get("layers", [])[:40])
            print(f"    {nombre} ({tipo}) capas[{len(d.get('layers', []))}]: {capas[:600]}", flush=True)
        except Exception as e:
            print(f"    {nombre} ({tipo}): error {e}", flush=True)
        time.sleep(0.3)


def tamano_generalizado(url_capa, offset):
    """Descarga toda la capa generalizada por el servidor y reporta tamano y rasgos."""
    q = url_capa + "/query?" + urllib.parse.urlencode({"where": "1=1", "outFields": "cCodRuta,Departamen,Tramo,Tipo_Super,CAT_VIAL",
                                                       "returnGeometry": "true", "outSR": "4326", "f": "geojson",
                                                       "maxAllowableOffset": str(offset), "geometryPrecision": "4"})
    t0 = time.time()
    try:
        st, ct, b = pedir(q, timeout=600)
    except Exception as e:
        return f"offset {offset}: error {e}"
    try:
        doc = json.loads(b.decode("utf-8", "replace"))
        feats = doc.get("features", [])
        partes = sum(len(f["geometry"]["coordinates"]) if f.get("geometry", {}).get("type") == "MultiLineString" else 1 for f in feats)
        vertices = sum(sum(len(l) for l in f["geometry"]["coordinates"]) if f["geometry"]["type"] == "MultiLineString" else len(f["geometry"]["coordinates"]) for f in feats if f.get("geometry"))
        props = [f.get("properties") for f in feats[:3]]
        return f"offset {offset}: {len(b):,} bytes, {len(feats)} rasgos, {partes:,} partes, {vertices:,} vertices, {time.time() - t0:.0f} s, props: {json.dumps(props, ensure_ascii=False)[:300]}"
    except Exception as e:
        return f"offset {offset}: {len(b):,} bytes pero no es GeoJSON ({e}): {b[:200]!r}"


def inspeccionar():
    print("== capas del mapa operativo del COEN (FEN 2027) ==", flush=True)
    for u in RAICES_ARCGIS:
        print(f"- {u}\n    {describir_json(u)}", flush=True)
        time.sleep(0.3)
    for u in CAPAS_RED:
        try:
            print(f"- {u}\n    conteo: {contar(u)}\n    muestra: {muestra(u)[:900]}", flush=True)
        except Exception as e:
            print(f"- {u}: error {e}", flush=True)
    print("== Red Vial Nacional generalizada por el servidor ==", flush=True)
    for off in (0.02, 0.005):
        print("    " + tamano_generalizado(RED_NACIONAL, off), flush=True)
    print("== Overpass (OSM): conteo de vias principales en Peru ==", flush=True)
    consulta = '[out:json][timeout:120];area["ISO3166-1"="PE"][admin_level=2]->.pe;way["highway"~"^(motorway|trunk|primary)$"](area.pe);out count;'
    try:
        st, ct, b = pedir(OVERPASS, timeout=180, datos=urllib.parse.urlencode({"data": consulta}).encode())
        print("    " + re.sub(r"\s+", " ", b.decode("utf-8", "replace"))[:700], flush=True)
    except Exception as e:
        print(f"    error: {e}", flush=True)
    print(f"== mapa de alertas de Sutran: de donde saca los datos (cert fijado: {CERT_SUTRAN.exists()}) ==", flush=True)
    patron_url = re.compile(r"""(?:https?:)?//[^\s"'<>)]+|["'](/[^"'\s<>]+\.(?:php|json|geojson|js|aspx|ashx)[^"'\s<>]*)["']""", re.I)
    for u in PAGINAS:
        try:
            st, ct, b = pedir(u, timeout=40)
        except Exception as e:
            print(f"- {u}: error {e}", flush=True)
            continue
        t = b.decode("utf-8", "replace")
        print(f"- {u}: {st}, {len(b)} bytes, {ct}", flush=True)
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', t, re.I)
        print(f"    scripts: {scripts[:25]}", flush=True)
        urls = sorted({m[0] or m[1] for m in [(x if isinstance(x, str) else x, "") for x in patron_url.findall(t)] if (m[0] or m[1])})
        print(f"    urls en el html: {[x for x in urls if 'sutran' in x or 'arcgis' in x or 'api' in x.lower() or x.endswith(('.php', '.json', '.geojson'))][:40]}", flush=True)
        # scripts propios: buscar los endpoints que consultan
        for src in scripts[:12]:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://gis.sutran.gob.pe" + src
            elif not src.startswith("http"):
                src = u.rstrip("/") + "/" + src
            if "sutran" not in src:
                continue
            try:
                st2, ct2, b2 = pedir(src, timeout=40)
                js = b2.decode("utf-8", "replace")
                enc = sorted({x if isinstance(x, str) else (x[0] or x[1]) for x in patron_url.findall(js)})
                pistas = [x for x in enc if any(k in x.lower() for k in ("sutran", "arcgis", "api", ".php", ".json", "geojson", "feature", "mapserver", "alerta", "via"))]
                print(f"    {src}: {len(b2)} bytes -> {pistas[:40]}", flush=True)
                for k in ("fetch(", "$.ajax", "$.getJSON", "XMLHttpRequest", "axios", "L.geoJSON", "esri", "FeatureLayer"):
                    i = js.find(k)
                    if i >= 0:
                        print(f"      {k}: ..." + re.sub(r"\s+", " ", js[max(0, i - 80):i + 220]) + "...", flush=True)
            except Exception as e:
                print(f"    {src}: error {e}", flush=True)


def publicar_red():
    """Red Vial Nacional generalizada (IDEP/IGN) -> docs/vias_principales.geojson."""
    q = RED_NACIONAL + "/query?" + urllib.parse.urlencode({"where": "1=1", "outFields": "cCodRuta,Departamen,Tipo_Super",
                                                            "returnGeometry": "true", "outSR": "4326", "f": "geojson",
                                                            "maxAllowableOffset": str(OFFSET_RED), "geometryPrecision": "4"})
    st, ct, b = pedir(q, timeout=600)
    doc = json.loads(b.decode("utf-8", "replace"))
    feats = doc.get("features", [])
    if not feats:
        raise SystemExit("la IDEP no devolvio rasgos de la Red Vial Nacional: no se sobrescribe")
    salida = []
    for f in feats:
        g = f.get("geometry") or {}
        if g.get("type") not in ("LineString", "MultiLineString"):
            continue
        salida.append({"type": "Feature", "properties": {"clase": "nacional", "ruta": (f.get("properties") or {}).get("cCodRuta"),
                                                          "superficie": (f.get("properties") or {}).get("Tipo_Super")}, "geometry": g})
    partes = sum(len(f["geometry"]["coordinates"]) if f["geometry"]["type"] == "MultiLineString" else 1 for f in salida)
    SALIDA_RED.write_text(json.dumps({"type": "FeatureCollection",
                                      "fuente": "MTC, Red Vial Nacional, servida por la IDEP (IGN); generalizada por el servidor",
                                      "url": RED_NACIONAL, "generalizacion_grados": OFFSET_RED, "features": salida}, ensure_ascii=False))
    print(f"{SALIDA_RED.relative_to(RAIZ)}: {len(salida)} rasgos, {partes:,} partes, {SALIDA_RED.stat().st_size:,} bytes", flush=True)


def main():
    if "--inspeccionar" in sys.argv:
        if "--red" not in sys.argv:
            print("== certificado de gis.sutran.gob.pe ==", flush=True)
            certificado_sutran()
        inspeccionar()
        print("modo inspeccion: no se escribe nada", flush=True)
        return
    publicar_red()
    print("vias bloqueadas: pendiente de una fuente consultable (ver docstring)", flush=True)


if __name__ == "__main__":
    main()
