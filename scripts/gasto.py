"""Gasto publico en el Programa Presupuestal 0068 ("Reduccion de la
vulnerabilidad y atencion de emergencias por desastres") por departamento.

Fuente: Portal de Datos Abiertos del MEF, dataset "Presupuesto y Ejecucion de
Gasto" (SIAF): un CSV anual con todas las metas presupuestales de los tres
niveles de gobierno y sus montos PIA, PIM, certificado, comprometido,
devengado y girado, actualizado a diario. Pesa varios GB: se lee en streaming
y solo se conservan las filas del PP 0068. No se guarda nada mas en disco.

Capa de **insumo**, no de resultado: dice cuanto se asigno y cuanto se
devengo en el programa que financia prevencion y atencion de desastres (todos
los peligros, no solo El Nino). Ver docs/METODOLOGIA.md.

Uso:
    PYTHONPATH=scripts python3 scripts/gasto.py                  # calcula y escribe data/gasto_pp0068.json
    PYTHONPATH=scripts python3 scripts/gasto.py --inspeccionar   # imprime recursos, encabezado y muestra; no escribe
    PYTHONPATH=scripts python3 scripts/gasto.py --archivo x.csv  # lee un CSV local (pruebas)
    opciones: --anio 2026  --max-filas N
"""

import csv
import io
import json
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from config import POBLACION_CENSO_2017, DEPARTAMENTOS

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "data" / "gasto_pp0068.json"
LIMA = timezone(timedelta(hours=-5))

PROGRAMA = "0068"
URL_CKAN = "https://datosabiertos.mef.gob.pe/api/3/action/package_show?id={id}"
IDS_DATASET = ["presupuesto-y-ejecucion-de-gasto", "presupuesto-y-ejecución-de-gasto"]
# Si el API CKAN no responde, se prueba la ruta donde el portal aloja los archivos
URL_ARCHIVO_SUPUESTA = "https://fs.datosabiertos.mef.gob.pe/datastorefiles/{anio}-Gasto-Diario.csv"
CABECERAS = {"User-Agent": "nino-peru-monitor (datos abiertos, uso no comercial)"}

# Candidatos de nombre por columna, en orden de preferencia. El encabezado real
# se confirma con --inspeccionar y se registra en el JSON de salida.
COLUMNAS = {
    "programa": ["PROGRAMA_PPTO", "PROGRAMA_PPTAL", "PROGRAMA_PRESUPUESTAL", "PROGRAMA"],
    "programa_nombre": ["PROGRAMA_PPTO_NOMBRE", "PROGRAMA_PPTAL_NOMBRE", "PROGRAMA_NOMBRE", "NOMBRE_PROGRAMA"],
    "departamento_nombre": ["DEPARTAMENTO_META_NOMBRE", "DEPARTAMENTO_NOMBRE", "NOMBRE_DEPARTAMENTO",
                            "DEPARTAMENTO_EJECUTORA_NOMBRE"],
    "departamento": ["DEPARTAMENTO_META", "DEPARTAMENTO", "DEPARTAMENTO_EJECUTORA"],
    "nivel_gobierno": ["NIVEL_GOBIERNO_NOMBRE", "NIVEL_GOBIERNO"],
    "anio": ["ANO_EJE", "ANIO_EJE", "ANO", "ANIO"],
    "mes": ["MES_EJE", "MES"],
    "pia": ["MONTO_PIA", "PIA"],
    "pim": ["MONTO_PIM", "PIM"],
    "certificado": ["MONTO_CERTIFICADO", "CERTIFICADO"],
    "comprometido": ["MONTO_COMPROMETIDO", "COMPROMETIDO"],
    "devengado": ["MONTO_DEVENGADO", "DEVENGADO"],
    "girado": ["MONTO_GIRADO", "GIRADO"],
}
OBLIGATORIAS = ("programa", "pim", "devengado")

UBIGEO_DEPARTAMENTO = {
    "01": "Amazonas", "02": "Ancash", "03": "Apurimac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huanuco",
    "11": "Ica", "12": "Junin", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martin", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}


# ---- utilidades --------------------------------------------------------------
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


NOMBRES = {sin_tildes(d["nombre"]).upper(): d["nombre"] for d in DEPARTAMENTOS}


def departamento_desde(nombre, codigo):
    """Nombre del departamento del monitor, o None si la fila no cae en uno de los 25."""
    if nombre:
        n = sin_tildes(nombre).upper().strip()
        if "CALLAO" in n:
            return "Callao"
        if n in NOMBRES:
            return NOMBRES[n]
        for k, v in NOMBRES.items():   # p. ej. "LIMA METROPOLITANA", "ANCASH "
            if n.startswith(k) and k not in ("LIMA",):
                return v
        if n.startswith("LIMA"):
            return "Lima"
    if codigo:
        c = str(codigo).strip()
        if c.isdigit():
            c = c.zfill(2)[:2] if len(c) <= 2 else c[:2]
            return UBIGEO_DEPARTAMENTO.get(c)
    return None


def numero(s):
    if s is None:
        return 0.0
    s = str(s).strip().replace(" ", "")
    if not s:
        return 0.0
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    elif "," in s and "." in s:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def codigo_programa(s):
    s = str(s or "").strip()
    if not s:
        return ""
    if s.isdigit():
        return s.zfill(4)
    return s.upper()


def descargar(url, intentos=5, timeout=120):
    """Abre una respuesta HTTP en streaming, con reintentos ante 5xx y fallos de red."""
    ultimo = None
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers=CABECERAS)
            return urllib.request.urlopen(req, timeout=timeout)
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


def leer_json(url):
    with descargar(url) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ---- descubrimiento del recurso ---------------------------------------------
def listar_recursos():
    for id_ in IDS_DATASET:
        try:
            doc = leer_json(URL_CKAN.format(id=urllib.request.quote(id_)))
        except Exception as exc:
            print(f"  CKAN {id_}: {exc}", flush=True)
            continue
        res = (doc.get("result") or {}).get("resources") or []
        if res:
            return [{"nombre": r.get("name"), "url": r.get("url"), "formato": r.get("format"),
                     "tamano": r.get("size"), "modificado": r.get("last_modified") or r.get("created")}
                    for r in res]
    return []


def elegir_recurso(recursos, anio):
    """El CSV de gasto diario del anio: nombre con el anio y 'gasto', sin 'devengado' ni 'diccionario'."""
    def puntaje(r):
        n = sin_tildes(r.get("nombre") or "").lower()
        u = (r.get("url") or "").lower()
        if str(anio) not in n and str(anio) not in u:
            return -1
        if "diccionario" in n or "ingreso" in n:
            return -1
        p = 0
        p += 3 if "gasto" in n else 0
        p += 2 if "diario" in n else 0
        p -= 2 if "devengado" in n else 0
        p += 1 if u.endswith(".csv") else 0
        return p
    candidatos = sorted(recursos, key=puntaje, reverse=True)
    return candidatos[0] if candidatos and puntaje(candidatos[0]) > 0 else None


# ---- lectura en streaming ----------------------------------------------------
def lineas(resp, url):
    """Itera lineas de texto de una respuesta HTTP (o de un zip con un CSV adentro)."""
    if url.lower().endswith(".zip"):
        print("  recurso en zip: se descarga a un temporal", flush=True)
        tmp = RAIZ / "data" / ".gasto_tmp.zip"
        with open(tmp, "wb") as f:
            while True:
                b = resp.read(1 << 20)
                if not b:
                    break
                f.write(b)
        z = zipfile.ZipFile(tmp)
        nombre = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        with z.open(nombre) as f:
            for raw in io.BufferedReader(f):
                yield decodificar(raw)
        tmp.unlink(missing_ok=True)
        return
    for raw in io.BufferedReader(resp, 1 << 20):
        yield decodificar(raw)


def decodificar(raw):
    try:
        return raw.decode("utf-8").lstrip("﻿")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def filas_csv(lineas_iter):
    primera = next(lineas_iter)
    delim = max((",", ";", "|", "\t"), key=primera.count)
    lector = csv.reader(_concat(primera, lineas_iter), delimiter=delim)
    encabezado = [c.strip().strip('"').upper() for c in next(lector)]
    return encabezado, delim, lector


def _concat(primera, resto):
    yield primera
    yield from resto


def resolver_columnas(encabezado):
    pos = {}
    for clave, candidatos in COLUMNAS.items():
        for c in candidatos:
            if c in encabezado:
                pos[clave] = encabezado.index(c)
                break
    faltan = [c for c in OBLIGATORIAS if c not in pos]
    if faltan:
        raise SystemExit(f"no se encontraron columnas para {faltan} en el encabezado: {encabezado}")
    if "departamento" not in pos and "departamento_nombre" not in pos:
        raise SystemExit(f"no hay columna de departamento en el encabezado: {encabezado}")
    return pos


# ---- agregacion --------------------------------------------------------------
MONTOS = ("pia", "pim", "certificado", "comprometido", "devengado", "girado")


def acumular(pos, lector, max_filas=None, muestra=None):
    """Suma los montos del PP 0068 por departamento (y nivel de gobierno).

    Devuelve (por_departamento, otros, meses, estadisticas)."""
    por_dep, otros, por_nivel = {}, {}, {}
    meses, anios = {}, {}
    leidas = filtradas = 0
    nombre_programa = None
    g = lambda fila, k: fila[pos[k]] if k in pos and pos[k] < len(fila) else None
    for fila in lector:
        leidas += 1
        if max_filas and leidas > max_filas:
            break
        if not fila:
            continue
        if codigo_programa(g(fila, "programa")) != PROGRAMA:
            continue
        filtradas += 1
        if muestra is not None and len(muestra) < 5:
            muestra.append(fila)
        if nombre_programa is None:
            nombre_programa = g(fila, "programa_nombre")
        mes = g(fila, "mes")
        if mes is not None:
            meses[mes] = meses.get(mes, 0) + 1
        anio = g(fila, "anio")
        if anio is not None:
            anios[anio] = anios.get(anio, 0) + 1
        dep = departamento_desde(g(fila, "departamento_nombre"), g(fila, "departamento"))
        destino = por_dep if dep else otros
        clave = dep or (g(fila, "departamento_nombre") or g(fila, "departamento") or "sin dato").strip()
        d = destino.setdefault(clave, {m: 0.0 for m in MONTOS} | {"filas": 0})
        d["filas"] += 1
        for m in MONTOS:
            d[m] += numero(g(fila, m))
        nivel = (g(fila, "nivel_gobierno") or "s/d").strip()
        n = por_nivel.setdefault(nivel, {m: 0.0 for m in MONTOS})
        for m in MONTOS:
            n[m] += numero(g(fila, m))
    return por_dep, otros, por_nivel, {"filas_leidas": leidas, "filas_pp0068": filtradas,
                                      "meses": meses, "anios": anios, "programa_nombre": nombre_programa}


def armar_salida(por_dep, otros, por_nivel, est, recurso, columnas, anio, url):
    total = {m: 0.0 for m in MONTOS}
    deps = {}
    for nombre in (d["nombre"] for d in DEPARTAMENTOS):
        d = por_dep.get(nombre)
        if not d:
            deps[nombre] = {"sin_datos": True}
            continue
        pob = POBLACION_CENSO_2017.get(nombre)
        fila = {m: round(d[m], 2) for m in MONTOS}
        fila["filas"] = d["filas"]
        fila["avance_pct"] = round(d["devengado"] / d["pim"] * 100, 1) if d["pim"] > 0 else None
        fila["pim_per_capita"] = round(d["pim"] / pob, 2) if pob else None
        fila["devengado_per_capita"] = round(d["devengado"] / pob, 2) if pob else None
        deps[nombre] = fila
        for m in MONTOS:
            total[m] += d[m]
    for d in otros.values():
        for m in MONTOS:
            total[m] += d[m]
    total = {m: round(v, 2) for m, v in total.items()}
    total["avance_pct"] = round(total["devengado"] / total["pim"] * 100, 1) if total["pim"] > 0 else None
    pob_total = sum(POBLACION_CENSO_2017.values())
    total["devengado_per_capita"] = round(total["devengado"] / pob_total, 2)
    advertencias = [
        "capa de insumo, no de resultado: mide presupuesto asignado y devengado, no obras terminadas ni danio evitado",
        "el PP 0068 cubre todos los peligros (sismos, heladas, incendios, lluvias), no solo El Nino",
        "el avance porcentual favorece a quien tiene poco PIM; leerlo junto con el monto per capita",
        "departamento = donde se ejecuta la meta (DEPARTAMENTO_META); los pliegos nacionales con metas "
        "multidepartamentales o en el exterior quedan en 'otros'",
        "per capita con poblacion censada 2017 (INEI), no con proyecciones",
        "asociacion entre gasto y anomalias climaticas, si se analiza, es solo correlacion",
    ]
    return {
        "programa": PROGRAMA,
        "programa_nombre": est.get("programa_nombre"),
        "anio": anio,
        "fuente": "MEF, Portal de Datos Abiertos: Presupuesto y Ejecucion de Gasto (SIAF), archivo diario del anio",
        "url": url,
        "recurso": recurso,
        "descargado": datetime.now(LIMA).isoformat(timespec="minutes"),
        "columnas_usadas": columnas,
        "meses_en_archivo": est["meses"],
        "anios_en_archivo": est["anios"],
        "filas_leidas": est["filas_leidas"],
        "filas_pp0068": est["filas_pp0068"],
        "poblacion_fuente": "INEI, Censos Nacionales 2017 (poblacion censada por departamento)",
        "unidad": "soles corrientes",
        "total": total,
        "por_nivel_gobierno": {k: {m: round(v[m], 2) for m in MONTOS} for k, v in por_nivel.items()},
        "otros": {k: {m: round(v[m], 2) for m in MONTOS} | {"filas": v["filas"]} for k, v in otros.items()},
        "departamentos": deps,
        "advertencias": advertencias,
    }


# ---- entrada -----------------------------------------------------------------
def argumento(nombre, defecto=None):
    if nombre in sys.argv:
        i = sys.argv.index(nombre)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else defecto
    return defecto


def main():
    inspeccionar = "--inspeccionar" in sys.argv
    archivo = argumento("--archivo")
    anio = int(argumento("--anio", datetime.now(LIMA).year))
    max_filas = argumento("--max-filas")
    max_filas = int(max_filas) if max_filas else (300_000 if inspeccionar else None)

    recurso, url = None, None
    if archivo:
        url = archivo
        fuente = open(archivo, "rb")
    else:
        print("recursos del dataset (CKAN):", flush=True)
        recursos = listar_recursos()
        for r in recursos:
            print(f"  - {r['nombre']} | {r['formato']} | {r['tamano']} | {r['modificado']} | {r['url']}", flush=True)
        recurso = elegir_recurso(recursos, anio)
        if recurso:
            url = recurso["url"]
        else:
            url = URL_ARCHIVO_SUPUESTA.format(anio=anio)
            print(f"  no se identifico el recurso de {anio} por CKAN; se intenta {url}", flush=True)
        print(f"descargando en streaming: {url}", flush=True)
        fuente = descargar(url, timeout=300)

    t0 = time.time()
    with fuente:
        encabezado, delim, lector = filas_csv(lineas(fuente, url))
        print(f"encabezado ({len(encabezado)} columnas, delimitador {delim!r}):", flush=True)
        print("  " + " | ".join(encabezado), flush=True)
        pos = resolver_columnas(encabezado)
        print("columnas usadas: " + ", ".join(f"{k}={encabezado[v]}" for k, v in pos.items()), flush=True)
        muestra = []
        por_dep, otros, por_nivel, est = acumular(pos, lector, max_filas, muestra)
    print(f"filas leidas: {est['filas_leidas']:,} | PP {PROGRAMA}: {est['filas_pp0068']:,} | "
          f"{time.time() - t0:.0f} s", flush=True)
    print(f"programa: {est['programa_nombre']!r} | meses: {est['meses']} | anios: {est['anios']}", flush=True)
    if inspeccionar:
        for f in muestra:
            print("  muestra: " + " | ".join(f"{encabezado[i]}={f[i]}" for i in sorted(pos.values()) if i < len(f)), flush=True)
        print("departamentos encontrados: " + ", ".join(sorted(por_dep)), flush=True)
        print("otros (no asignables): " + ", ".join(sorted(otros)), flush=True)
        print("niveles de gobierno: " + ", ".join(sorted(por_nivel)), flush=True)
        print("modo inspeccion: no se escribe nada", flush=True)
        return
    if est["filas_pp0068"] == 0:
        raise SystemExit(f"ninguna fila del PP {PROGRAMA}: no se sobrescribe la salida")
    columnas = {k: encabezado[v] for k, v in pos.items()}
    salida = armar_salida(por_dep, otros, por_nivel, est, recurso, columnas, anio, url)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=1))
    t = salida["total"]
    print(f"{SALIDA.relative_to(RAIZ)}: PIM S/ {t['pim']:,.0f}, devengado S/ {t['devengado']:,.0f} "
          f"({t['avance_pct']} %), {sum(1 for d in salida['departamentos'].values() if not d.get('sin_datos'))} "
          f"departamentos con datos, {len(otros)} rubros en 'otros'")


if __name__ == "__main__":
    main()
