"""Indice de precios al consumidor (IPC) por ciudad: variacion mensual del IPC
general y del grupo alimentos y bebidas en las ciudades principales del Peru,
con la anomalia frente al promedio historico del mismo mes.

Fuente: INEI (IPC de Lima Metropolitana y de las ciudades principales), tomado
del API abierto de BCRPData, que republica esas series mensuales sin clave:
    https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigos}/json/{inicio}/{fin}
Catalogo de series (para ubicar los codigos):
    https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata

Capa de **efecto**: el precio de los alimentos es el canal mas directo de un
evento El Nino hacia los hogares. Es descriptiva: el IPC responde tambien a
combustibles, tipo de cambio y oferta; no hay atribucion causal.

Uso:
    PYTHONPATH=scripts python3 scripts/ipc.py --inspeccionar   # lista las series candidatas del catalogo y prueba el API
    PYTHONPATH=scripts python3 scripts/ipc.py                  # escribe data/ipc_ciudades.json
    PYTHONPATH=scripts python3 scripts/ipc.py --archivo x.json # usa una respuesta guardada del API (pruebas)
"""

import csv
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import mean, pstdev

from config import DEPARTAMENTOS

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "data" / "ipc_ciudades.json"
LIMA = timezone(timedelta(hours=-5))

URL_METADATA = "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata"
URL_API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigos}/json/{inicio}/{fin}"
CABECERAS = {"User-Agent": "nino-peru-monitor (datos abiertos, uso no comercial)"}
ANIO_INICIO = 2012            # inicio de la ventana historica para el promedio por mes
ANIOS_BASE = (2012, 2024)     # promedio y desviacion del mismo mes del calendario
MESES_SERIE = 36              # meses que se publican por ciudad
LOTE_CODIGOS = 12             # codigos por peticion al API

# Ciudad -> departamento del monitor, y codigos BCRP de la variacion mensual
# del IPC general y de alimentos y bebidas. Los codigos se confirman con
# --inspeccionar (catalogo del BCRP) y se completan aqui.
CIUDADES = {
    # "Lima": {"departamento": "Lima", "general": "PN01273PM", "alimentos": None},
}
PATRONES_CATALOGO = [r"precios al consumidor", r"\bIPC\b", r"indice de precios", r"inflaci"]
MESES_ABR = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "set": 9,
             "oct": 10, "nov": 11, "dic": 12}


# ---- utilidades --------------------------------------------------------------
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def descargar(url, intentos=5, timeout=120):
    ultimo = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers=CABECERAS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            ultimo = exc
            if exc.code < 500 and exc.code != 429:
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            ultimo = exc
        espera = 10 * 2 ** i
        print(f"  reintento en {espera} s ({ultimo})", flush=True)
        time.sleep(espera)
    raise RuntimeError(f"sin respuesta de {url}: {ultimo}")


def decodificar(b):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", "replace")


def periodo(nombre):
    """'Ene.2024' / 'Ene24' / '2024-01' -> (anio, mes) o None."""
    s = sin_tildes(str(nombre)).strip().lower()
    m = re.match(r"^([a-z]{3})\.?\s*(\d{2,4})$", s)
    if m and m.group(1) in MESES_ABR:
        a = int(m.group(2)); a = a + 2000 if a < 100 else a
        return a, MESES_ABR[m.group(1)]
    m = re.match(r"^(\d{4})-?(\d{1,2})$", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def numero(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


# ---- catalogo ----------------------------------------------------------------
def inspeccionar_catalogo():
    print(f"descargando catalogo: {URL_METADATA}", flush=True)
    texto = decodificar(descargar(URL_METADATA, timeout=300))
    primera = texto.splitlines()[0] if texto else ""
    delim = max((";", ",", "\t", "|"), key=primera.count)
    filas = list(csv.reader(io.StringIO(texto), delimiter=delim))
    enc = [c.strip() for c in filas[0]]
    print(f"catalogo: {len(filas) - 1:,} filas, delimitador {delim!r}, columnas: {' | '.join(enc)}", flush=True)
    idx = {sin_tildes(c).lower(): i for i, c in enumerate(enc)}
    i_cod = next((i for k, i in idx.items() if "codigo" in k), 0)
    i_nom = next((i for k, i in idx.items() if "nombre" in k), 2)
    i_grp = next((i for k, i in idx.items() if "grupo" in k), 1)
    i_frec = next((i for k, i in idx.items() if "frecuencia" in k), None)
    i_ini = next((i for k, i in idx.items() if "inicio" in k), None)
    i_fin = next((i for k, i in idx.items() if "fin" in k and "inicio" not in k), None)
    i_geo = next((i for k, i in idx.items() if "geograf" in k), None)
    i_cat = next((i for k, i in idx.items() if "categoria" in k), None)
    ciudades = [sin_tildes(c).lower() for c in ("Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", "Huancayo", "Iquitos",
                "Tacna", "Puno", "Tumbes", "Ica", "Chimbote", "Huaraz", "Cajamarca", "Pucallpa", "Moquegua", "Ayacucho",
                "Huanuco", "Abancay", "Chachapoyas", "Moyobamba", "Cerro de Pasco", "Puerto Maldonado", "Huancavelica", "Callao")]
    col = lambda f, i: f[i] if i is not None and i < len(f) else ""
    encontradas, muestra_region = [], []
    for f in filas[1:]:
        if len(f) <= max(i_cod, i_nom, i_grp):
            continue
        # se busca en toda la fila: el nombre de la ciudad puede venir en la columna de geografia o en la categoria
        texto_fila = sin_tildes(" ".join(f)).lower()
        geo = col(f, i_geo)
        es_ciudad = any(re.search(r"\b" + re.escape(c) + r"\b", texto_fila) for c in ciudades)
        frec = col(f, i_frec)
        if any(re.search(p.lower(), texto_fila) for p in PATRONES_CATALOGO):
            if frec and "mensual" not in sin_tildes(frec).lower():
                continue
            # Lima Metropolitana ya se conoce: lo que interesa son las demas ciudades
            es_regional = es_ciudad and "lima metropolitana" not in texto_fila
            encontradas.append((es_regional, f[i_cod], col(f, i_cat)[:40], f[i_grp][:70], f[i_nom][:110], geo[:30], frec,
                                col(f, i_ini), col(f, i_fin)))
        elif es_ciudad and geo and "peru" not in sin_tildes(geo).lower() and len(muestra_region) < 25:
            muestra_region.append((f[i_cod], col(f, i_cat)[:40], f[i_grp][:60], f[i_nom][:80], geo[:30], frec))
    encontradas.sort(key=lambda x: (not x[0], x[3], x[4]))
    print(f"series mensuales de precios/inflacion: {len(encontradas)} (primero las regionales, fuera de Lima Metropolitana)", flush=True)
    for e in encontradas[:400]:
        print(f"  {'R' if e[0] else ' '} {e[1]} | {e[2]} | {e[3]} | {e[4]} | geo={e[5]} | {e[6]} | {e[7]} - {e[8]}", flush=True)
    print(f"muestra de series regionales de cualquier tema (para ver como nombra el BCRP a las regiones): {len(muestra_region)}", flush=True)
    for m in muestra_region:
        print(f"    {m[0]} | {m[1]} | {m[2]} | {m[3]} | geo={m[4]} | {m[5]}", flush=True)
    geos = {}
    for f in filas[1:]:
        g = col(f, i_geo)
        if g:
            geos[g] = geos.get(g, 0) + 1
    print("valores de la columna de geografia:", ", ".join(f"{g}={n}" for g, n in sorted(geos.items(), key=lambda x: -x[1])[:40]), flush=True)
    return encontradas


# El catalogo del BCRP solo trae el IPC de Lima Metropolitana: las ciudades las
# publica el INEI. Estas paginas se revisan en busca de archivos descargables.
PAGINAS_INEI = [
    "https://m.inei.gob.pe/estadisticas/indice-tematico/price-indexes/",
    "https://www.inei.gob.pe/estadisticas/indice-tematico/price-indexes/",
    "https://m.inei.gob.pe/estadisticas/indice-tematico/economia/",
    "https://m.inei.gob.pe/biblioteca-virtual/boletines/informe-de-precios/1/",
    "https://www.inei.gob.pe/biblioteca-virtual/boletines/informe-de-precios/1/",
    "http://webapp.inei.gob.pe:8080/sirtod-series/",
    "https://systems.inei.gob.pe/SIRTOD/",
    "https://www.datosabiertos.gob.pe/api/3/action/package_search?q=indice%20precios%20consumidor%20ciudades&rows=10",
    "https://www.datosabiertos.gob.pe/dataset?q=IPC+ciudades",
]


def inspeccionar_inei():
    print("== fuentes INEI (archivos descargables con IPC por ciudad) ==", flush=True)
    for url in PAGINAS_INEI:
        try:
            b = descargar(url, intentos=2, timeout=60)
        except Exception as exc:
            print(f"- {url}: error {exc}", flush=True)
            continue
        t = decodificar(b)
        tl = sin_tildes(t).lower()
        print(f"- {url}: {len(b):,} bytes", flush=True)
        if url.endswith("rows=10"):
            print("    " + t[:1500].replace("\n", " "), flush=True)
            continue
        enlaces = re.findall(r'href=["\']([^"\']+)["\']', t)
        interesantes = [e for e in enlaces if re.search(r"\.(xlsx?|csv|zip)(\?|$)", e, re.I)]
        con_pista = [e for e in interesantes if re.search(r"ciud|precio|ipc|cap27|cap_27|indice", sin_tildes(e).lower())]
        print(f"    enlaces: {len(enlaces)}, descargables: {len(interesantes)}, con pista de precios/ciudades: {len(con_pista)}", flush=True)
        for e in (con_pista or interesantes)[:60]:
            # el texto cercano al enlace ayuda a saber que cuadro es
            i = t.find(e)
            contexto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t[max(0, i - 220):i + len(e) + 120]))
            print(f"      {e}  ::  {contexto[:160]}", flush=True)
        for pista in ("sirtod", "api/", "series/", "exportar", "json"):
            i = tl.find(pista)
            if i >= 0:
                print(f"    pista '{pista}': ..." + re.sub(r"\s+", " ", t[max(0, i - 120):i + 160]) + "...", flush=True)


PAGINA_BOLETINES = "https://www.inei.gob.pe/biblioteca-virtual/boletines/informe-de-precios/1/"
CIUDADES_INEI = ["Chachapoyas", "Huaraz", "Abancay", "Arequipa", "Ayacucho", "Cajamarca", "Cusco", "Huancavelica", "Huanuco",
                 "Ica", "Huancayo", "Trujillo", "Chiclayo", "Lima", "Iquitos", "Puerto Maldonado", "Moquegua", "Cerro de Pasco",
                 "Piura", "Puno", "Moyobamba", "Tacna", "Tumbes", "Pucallpa", "Chimbote", "Tarapoto"]


PAGINAS_PDF = [
    "https://www.inei.gob.pe/biblioteca-virtual/boletines/informe-de-precios/1/",
    "https://www.inei.gob.pe/biblioteca-virtual/boletines/informe-de-precios/",
    "https://www.inei.gob.pe/estadisticas/indice-tematico/price-indexes/",
    "https://www.inei.gob.pe/biblioteca-virtual/boletines/",
]


def listar_informes(paginas=1):
    """Filas de la biblioteca de informes de precios: fecha, titulo y URL del PDF."""
    salida = []
    for n in range(1, paginas + 1):
        url = f"https://www.inei.gob.pe/biblioteca-virtual/boletines/informe-de-precios/{n}/"
        try:
            t = decodificar(descargar(url, intentos=2, timeout=60))
        except Exception as exc:
            print(f"    {url}: error {exc}", flush=True)
            continue
        for m in re.finditer(r'<tr[^>]*class="[^"]*fila_selected[^"]*"[^>]*rel="([^"]+)"[^>]*>(.*?)</tr>', t, re.I | re.S):
            celdas = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.I | re.S)]
            href = m.group(1)
            salida.append({"url": href if href.startswith("http") else "https://www.inei.gob.pe" + href,
                           "fecha": celdas[0] if celdas else "", "titulo": celdas[1] if len(celdas) > 1 else ""})
        time.sleep(0.5)
    return salida


def inspeccionar_pdf():
    """El IPC por ciudad sale en el informe tecnico mensual (PDF). Se mira si el texto es parseable."""
    import shutil, subprocess, tempfile
    print("== informes tecnicos de precios del INEI (PDF) ==", flush=True)
    limpiar = lambda x: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip()
    pdfs, fichas = [], []
    # la lista de informes es una tabla: <tr class="... fila_selected" rel="/media/.../x.pdf"><td>fecha</td><td>titulo</td>
    filas = listar_informes(paginas=2)
    print(f"informes en la tabla (2 paginas): {len(filas)}", flush=True)
    for f in filas[:30]:
        print(f"    {f['fecha']} | {f['titulo'][:80]} | {f['url']}", flush=True)
    for f in filas:
        pdfs.append((f["url"], f["titulo"]))
    for pagina in ([] if filas else PAGINAS_PDF):
        try:
            t = decodificar(descargar(pagina, intentos=1, timeout=60))
        except Exception as exc:
            print(f"- {pagina}: error {exc}", flush=True)
            continue
        todos = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', t, re.I | re.S)
        # todos los PDF de la pagina, con el texto del enlace y lo que lo rodea
        for h, x in todos:
            if h.lower().split("?")[0].endswith(".pdf"):
                i = t.find(h)
                ctx = limpiar(t[max(0, i - 300):i + len(h) + 200])
                pdfs.append((h if h.startswith("http") else "https://www.inei.gob.pe" + h, limpiar(x) or ctx[:120]))
        prefijos = {}
        for h, _ in todos:
            pre = re.sub(r"[^/]+$", "", h)[:60]
            prefijos[pre] = prefijos.get(pre, 0) + 1
        print(f"- {pagina}: {len(todos)} enlaces; prefijos mas comunes: {sorted(prefijos.items(), key=lambda kv: -kv[1])[:8]}", flush=True)
        # enlaces que mencionan precios en el texto (fichas de informes), aunque no sean PDF
        for h, x in todos:
            tx = limpiar(x)
            if re.search(r"precio|ipc|inflaci", (h + " " + tx).lower()):
                fichas.append((h if h.startswith("http") else "https://www.inei.gob.pe" + h, tx))
        # como esta armada la lista de informes: contexto de cada mencion a "informe tecnico"/"precios"
        n = 0
        for m in re.finditer(r"informe\s+t[eé]cnico|variaci[oó]n de los indicadores|precios al consumidor", t, re.I):
            i = m.start()
            print(f"    ctx: ..." + re.sub(r"\s+", " ", t[max(0, i - 350):i + 250]) + "...", flush=True)
            n += 1
            if n >= 6:
                break
        scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', t, re.I)
        print(f"    scripts: {scripts[:15]}", flush=True)
        for m in re.finditer(r"<script(?![^>]*src)[^>]*>(.*?)</script>", t, re.I | re.S):
            cuerpo = m.group(1)
            if re.search(r"boletin|media/|ajax|json", cuerpo, re.I):
                print("    script inline: " + re.sub(r"\s+", " ", cuerpo)[:500], flush=True)
    # quitar repetidos conservando el orden
    vistos = set(); pdfs = [x for x in pdfs if not (x[0] in vistos or vistos.add(x[0]))]
    vistos = set(); fichas = [x for x in fichas if not (x[0] in vistos or vistos.add(x[0]))]
    print(f"PDF encontrados: {len(pdfs)}", flush=True)
    for h, x in pdfs[:40]:
        print(f"    {h} :: {x[:100]}", flush=True)
    print(f"fichas con pista de precios: {len(fichas)}", flush=True)
    for h, x in fichas[:30]:
        print(f"    {h} :: {x[:100]}", flush=True)
    # preferir un PDF cuyo nombre o texto hable de precios
    pdfs = sorted(pdfs, key=lambda hx: 0 if re.search(r"precio|ipc|inflaci", (hx[0] + " " + hx[1]).lower()) else 1)
    if not pdfs or not re.search(r"precio|ipc|inflaci", (pdfs[0][0] + " " + pdfs[0][1]).lower()):
        # seguir las fichas de precios y buscar el PDF adentro
        for h, x in fichas[:6]:
            if any(h.rstrip("/") == pg.rstrip("/") for pg in PAGINAS_PDF) or not h.startswith("http"):
                continue
            try:
                t2 = decodificar(descargar(h, intentos=1, timeout=60))
            except Exception as exc:
                print(f"    ficha {h}: error {exc}", flush=True)
                continue
            dentro = re.findall(r'href=["\']([^"\']+\.pdf)["\']', t2, re.I)
            print(f"    ficha {h}: {len(dentro)} PDF: {dentro[:5]}", flush=True)
            if dentro:
                d = dentro[0]
                pdfs = [(d if d.startswith("http") else "https://www.inei.gob.pe" + d, x)]
                break
    print(f"    PDF candidatos: {len(pdfs)}", flush=True)
    for href, txt in pdfs[:12]:
        print(f"    {href} :: {txt[:100]}", flush=True)
    # titulos en el html cerca de cada pdf (la lista suele llevar el mes)
    for m in re.finditer(r"informe[^<]{0,80}precios[^<]{0,120}", t, re.I):
        print("    titulo: " + re.sub(r"\s+", " ", m.group(0))[:160], flush=True)
        break
    if not pdfs:
        return
    url = pdfs[0][0]
    print(f"descargando el candidato: {url}", flush=True)
    try:
        b = descargar(url, intentos=2, timeout=120)
    except Exception as exc:
        print(f"    error {exc}", flush=True)
        return
    print(f"    {len(b):,} bytes; pdftotext: {shutil.which('pdftotext')}", flush=True)
    if not shutil.which("pdftotext"):
        return
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b); ruta = f.name
    texto = subprocess.run(["pdftotext", "-layout", ruta, "-"], capture_output=True, text=True, timeout=120).stdout
    lineas = texto.splitlines()
    print(f"    {len(lineas):,} lineas de texto", flush=True)
    patron = re.compile("|".join(re.escape(sin_tildes(c).lower()) for c in CIUDADES_INEI))
    for i, l in enumerate(lineas):
        ll = sin_tildes(l).lower()
        if re.search(r"ciudad|principales ciudades", ll) and ("precio" in ll or "indice" in ll or "variac" in ll):
            print(f"    [{i}] {l.strip()[:150]}", flush=True)
    n = 0
    for i, l in enumerate(lineas):
        if patron.search(sin_tildes(l).lower()) and re.search(r"-?\d+[.,]\d", l):
            print(f"    {i}: {l.rstrip()[:170]}", flush=True)
            n += 1
            if n > 90:
                break


def inspeccionar_api(codigo):
    url = URL_API.format(codigos=codigo, inicio="2024-1", fin="2024-12")
    print(f"prueba del API: {url}", flush=True)
    doc = json.loads(decodificar(descargar(url)))
    print("  config:", json.dumps(doc.get("config"), ensure_ascii=False)[:400], flush=True)
    print("  periods[:3]:", json.dumps(doc.get("periods", [])[:3], ensure_ascii=False), flush=True)


# ---- series ------------------------------------------------------------------
def pedir_series(codigos, inicio, fin):
    """Devuelve {codigo: {(anio, mes): valor}} para una lista de codigos."""
    salida = {c: {} for c in codigos}
    for i in range(0, len(codigos), LOTE_CODIGOS):
        lote = codigos[i:i + LOTE_CODIGOS]
        url = URL_API.format(codigos="-".join(lote), inicio=inicio, fin=fin)
        doc = json.loads(decodificar(descargar(url)))
        nombres = [s.get("name") for s in (doc.get("config") or {}).get("series", [])]
        if len(nombres) != len(lote):
            print(f"  aviso: pedi {len(lote)} series y el API describe {len(nombres)}", flush=True)
        for p in doc.get("periods", []):
            per = periodo(p.get("name"))
            if not per:
                continue
            for c, v in zip(lote, p.get("values", [])):
                x = numero(v)
                if x is not None:
                    salida[c][per] = x
        time.sleep(1.5)
    return salida


def resumir(serie, hoy):
    """Ultimo dato, serie corta y anomalia frente al mismo mes de calendario (base ANIOS_BASE)."""
    if not serie:
        return None
    claves = sorted(serie)
    ult = claves[-1]
    por_mes = {}
    for (a, m), v in serie.items():
        if ANIOS_BASE[0] <= a <= ANIOS_BASE[1]:
            por_mes.setdefault(m, []).append(v)
    base = por_mes.get(ult[1], [])
    media = mean(base) if base else None
    desv = pstdev(base) if len(base) > 1 else None
    anomalia = round(serie[ult] - media, 2) if media is not None else None
    z = round((serie[ult] - media) / desv, 2) if desv else None
    # acumulado 12 meses a partir de las variaciones mensuales
    ult12 = [serie[k] for k in claves[-12:]]
    acum12 = None
    if len(ult12) == 12:
        f = 1.0
        for v in ult12:
            f *= 1 + v / 100
        acum12 = round((f - 1) * 100, 2)
    return {
        "mes": f"{ult[0]}-{ult[1]:02d}",
        "variacion_mensual_pct": serie[ult],
        "variacion_12m_pct": acum12,
        "media_mismo_mes_pct": round(media, 2) if media is not None else None,
        "anomalia_pct": anomalia,
        "z": z,
        "n_base": len(base),
        "serie": [[f"{a}-{m:02d}", serie[(a, m)]] for (a, m) in claves[-MESES_SERIE:]],
    }


def main():
    inspeccionar = "--inspeccionar" in sys.argv
    hoy = datetime.now(LIMA)
    if inspeccionar:
        if "--catalogo" in sys.argv:
            encontradas = inspeccionar_catalogo()
            prueba = next((e[1] for e in encontradas if e[0]), None) or (encontradas[0][1] if encontradas else None)
            if prueba:
                try:
                    inspeccionar_api(prueba)
                except Exception as exc:
                    print(f"  la prueba del API fallo: {exc}", flush=True)
            inspeccionar_inei()
        inspeccionar_pdf()
        print("modo inspeccion: no se escribe nada", flush=True)
        return
    if not CIUDADES:
        raise SystemExit("CIUDADES esta vacio: correr --inspeccionar, elegir los codigos del catalogo y completarlos en ipc.py")

    codigos = sorted({c for d in CIUDADES.values() for c in (d.get("general"), d.get("alimentos")) if c})
    print(f"{len(CIUDADES)} ciudades, {len(codigos)} series; pidiendo {ANIO_INICIO}-1 a {hoy.year}-12", flush=True)
    series = pedir_series(codigos, f"{ANIO_INICIO}-1", f"{hoy.year}-12")
    deps = {d["nombre"] for d in DEPARTAMENTOS}
    ciudades = {}
    for ciudad, d in CIUDADES.items():
        if d["departamento"] not in deps:
            raise SystemExit(f"{ciudad}: departamento {d['departamento']!r} no esta en config.DEPARTAMENTOS")
        fila = {"departamento": d["departamento"], "codigos": {k: d.get(k) for k in ("general", "alimentos")}}
        for k in ("general", "alimentos"):
            fila[k] = resumir(series.get(d.get(k), {}), hoy) if d.get(k) else None
        ciudades[ciudad] = fila
    con_dato = sum(1 for c in ciudades.values() if c["general"] or c["alimentos"])
    if con_dato < max(5, len(CIUDADES) // 2):
        raise SystemExit(f"solo {con_dato} ciudades con datos: no se sobrescribe la salida")
    ultimo = max((c[k]["mes"] for c in ciudades.values() for k in ("general", "alimentos") if c[k]), default=None)
    salida = {
        "fuente": "INEI, IPC de Lima Metropolitana y ciudades principales, via BCRPData (API abierto del BCRP)",
        "url_api": URL_API,
        "descargado": hoy.isoformat(timespec="minutes"),
        "ultimo_mes": ultimo,
        "base_anomalia": f"{ANIOS_BASE[0]}-{ANIOS_BASE[1]}, promedio del mismo mes del calendario",
        "unidad": "variacion porcentual mensual del indice",
        "ciudades": ciudades,
        "advertencias": [
            "la ciudad capital no representa al departamento entero",
            "el dato llega con alrededor de un mes de rezago y puede revisarse",
            "el IPC responde a combustibles, tipo de cambio y oferta, no solo al clima: descriptivo, sin atribucion causal",
            "la anomalia compara con el promedio del mismo mes en la base declarada; no es una prediccion",
        ],
    }
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1))
    print(f"{SALIDA.relative_to(RAIZ)}: {con_dato} ciudades con datos, ultimo mes {ultimo}")


if __name__ == "__main__":
    main()
