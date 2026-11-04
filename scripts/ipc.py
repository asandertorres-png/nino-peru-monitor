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
PATRONES_CATALOGO = [r"precios al consumidor", r"\bIPC\b", r"indice de precios"]
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
    ciudades = [sin_tildes(c).lower() for c in ("Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", "Huancayo", "Iquitos",
                "Tacna", "Puno", "Tumbes", "Ica", "Chimbote", "Huaraz", "Cajamarca", "Pucallpa", "Moquegua", "Ayacucho",
                "Huanuco", "Abancay", "Chachapoyas", "Moyobamba", "Cerro de Pasco", "Puerto Maldonado", "Huancavelica", "Callao")]
    encontradas = []
    for f in filas[1:]:
        if len(f) <= max(i_cod, i_nom, i_grp):
            continue
        texto_fila = sin_tildes(f"{f[i_grp]} {f[i_nom]}").lower()
        if any(re.search(p.lower(), texto_fila) for p in PATRONES_CATALOGO):
            frec = f[i_frec] if i_frec is not None and i_frec < len(f) else ""
            if frec and "mensual" not in sin_tildes(frec).lower():
                continue
            es_ciudad = any(c in texto_fila for c in ciudades)
            encontradas.append((es_ciudad, f[i_cod], f[i_grp][:70], f[i_nom][:110], frec,
                                f[i_ini] if i_ini is not None and i_ini < len(f) else "",
                                f[i_fin] if i_fin is not None and i_fin < len(f) else ""))
    encontradas.sort(key=lambda x: (not x[0], x[2], x[3]))
    print(f"series mensuales de precios al consumidor: {len(encontradas)} (primero las que nombran una ciudad)", flush=True)
    for e in encontradas[:400]:
        print(f"  {'C' if e[0] else ' '} {e[1]} | {e[2]} | {e[3]} | {e[4]} | {e[5]} - {e[6]}", flush=True)
    return encontradas


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
        encontradas = inspeccionar_catalogo()
        prueba = next((e[1] for e in encontradas if e[0]), None) or (encontradas[0][1] if encontradas else None)
        if prueba:
            try:
                inspeccionar_api(prueba)
            except Exception as exc:
                print(f"  la prueba del API fallo: {exc}", flush=True)
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
