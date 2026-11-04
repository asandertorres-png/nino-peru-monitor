"""Panel presupuestal de las universidades publicas del Peru desde el SIAF.

Insumo del diseno de investigacion en investigacion/diseno-absorcion-canon.md:
ejecucion de inversion por pliego universitario, fuente de financiamiento y
proyecto, con corte mensual.

Fuente: Portal de Datos Abiertos del MEF, dataset "Presupuesto y Ejecucion de
Gasto" (SIAF). Un CSV anual con todas las metas presupuestales de los tres
niveles de gobierno. Pesa varios GB (9.5 millones de filas en 2026): se lee en
streaming y solo se conservan las filas de pliegos universitarios.

Salidas (en investigacion/datos/):
  panel_universidades_{anio}.csv   agregado por anio, mes, pliego, rubro,
                                   tipo de actividad o proyecto y generica
  proyectos_universidades_{anio}.csv  agregado por anio, pliego, rubro y proyecto
  panel_universidades_{anio}.json  metadatos: encabezado real, filas leidas,
                                   pliegos encontrados, controles

Uso:
    python3 investigacion/panel_universidades.py --anio 2026
    python3 investigacion/panel_universidades.py --inspeccionar   # encabezado y muestra, no escribe
    python3 investigacion/panel_universidades.py --archivo x.csv  # CSV local (pruebas)
    opciones: --max-filas N  --salida DIR

SEMANTICA DEL ARCHIVO (confirmada contra el archivo real de 2026 por
scripts/gasto.py): cada fila es el **movimiento del mes**. El PIM inicial
aparece en el mes "00" y cada modificacion posterior en el mes en que se
incorporo; el devengado es flujo mensual. Por eso el acumulado anual es la suma
de todos los meses, y por eso el panel conserva el mes como clave: permite
fechar las incorporaciones de PIM y calcular que fraccion del presupuesto se
incorporo tarde en el anio, variable que separa un problema de programacion de
uno de capacidad de ejecucion.

ADVERTENCIA: los nombres de columna de pliego, fuente de financiamiento, rubro y
tipo de actividad o proyecto no estan confirmados contra el archivo real. Correr
primero --inspeccionar y ajustar COLUMNAS si hace falta. El JSON de salida
registra que nombre se uso para cada campo.
"""

import argparse
import csv
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA_POR_DEFECTO = RAIZ / "investigacion" / "datos"
LIMA = timezone(timedelta(hours=-5))

URL_CKAN = "https://datosabiertos.mef.gob.pe/api/3/action/package_show?id={id}"
IDS_DATASET = ["presupuesto-y-ejecucion-de-gasto", "presupuesto-y-ejecución-de-gasto"]
URL_ARCHIVO_SUPUESTA = "https://fs.datosabiertos.mef.gob.pe/datastorefiles/{anio}-Gasto-Diario.csv"
CABECERAS = {"User-Agent": "investigacion-academica (datos abiertos, uso no comercial)"}

# Candidatos de nombre por columna, en orden de preferencia.
COLUMNAS = {
    "anio": ["ANO_EJE", "ANIO_EJE", "ANO", "ANIO"],
    "mes": ["MES_EJE", "MES"],
    "sector": ["SECTOR"],
    "sector_nombre": ["SECTOR_NOMBRE", "NOMBRE_SECTOR"],
    "pliego": ["PLIEGO"],
    "pliego_nombre": ["PLIEGO_NOMBRE", "NOMBRE_PLIEGO"],
    "ejecutora": ["EJECUTORA", "UNIDAD_EJECUTORA"],
    "ejecutora_nombre": ["EJECUTORA_NOMBRE", "UNIDAD_EJECUTORA_NOMBRE", "NOMBRE_EJECUTORA"],
    "departamento_nombre": ["DEPARTAMENTO_META_NOMBRE", "DEPARTAMENTO_EJECUTORA_NOMBRE",
                            "DEPARTAMENTO_NOMBRE"],
    "fuente": ["FUENTE_FINANC", "FUENTE_FINANCIAMIENTO", "FUENTE_FINANC_CODIGO"],
    "fuente_nombre": ["FUENTE_FINANC_NOMBRE", "FUENTE_FINANCIAMIENTO_NOMBRE"],
    "rubro": ["RUBRO"],
    "rubro_nombre": ["RUBRO_NOMBRE", "NOMBRE_RUBRO"],
    "categoria_gasto": ["CATEGORIA_GASTO", "CATEGORIA"],
    "generica": ["GENERICA"],
    "generica_nombre": ["GENERICA_NOMBRE", "NOMBRE_GENERICA"],
    "tipo_act_proy": ["TIPO_ACT_PROY", "TIPO_ACTIVIDAD_PROYECTO"],
    "producto_proyecto": ["PRODUCTO_PROYECTO", "PROYECTO", "PRODUCTO_PROY"],
    "producto_proyecto_nombre": ["PRODUCTO_PROYECTO_NOMBRE", "PROYECTO_NOMBRE"],
    "funcion": ["FUNCION"],
    "pia": ["MONTO_PIA", "PIA"],
    "pim": ["MONTO_PIM", "PIM"],
    "certificado": ["MONTO_CERTIFICADO", "CERTIFICADO"],
    "comprometido": ["MONTO_COMPROMETIDO", "COMPROMETIDO"],
    "devengado": ["MONTO_DEVENGADO", "DEVENGADO"],
    "girado": ["MONTO_GIRADO", "GIRADO"],
}
OBLIGATORIAS = ("pliego_nombre", "pim", "devengado")
MONTOS = ("pia", "pim", "certificado", "comprometido", "devengado", "girado")

# Un pliego universitario: el nombre dice "UNIVERSIDAD" o abrevia "U.N."
# (el SIAF usa ambas formas segun el anio).
PATRON_UNIVERSIDAD = re.compile(r"\bUNIVERSIDAD\b|^U\.?\s*N\.?(\s|$)")


# ---- utilidades --------------------------------------------------------------
def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn")


def es_universidad(nombre):
    return bool(PATRON_UNIVERSIDAD.search(sin_tildes(nombre).upper().strip()))


def numero(s):
    """Monto del SIAF a float. Tolera coma decimal y separador de miles."""
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


def descargar(url, intentos=5, timeout=120):
    """Respuesta HTTP en streaming, con reintentos ante 5xx y fallos de red."""
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


def url_del_anio(anio):
    """URL del CSV anual: primero por el API CKAN, si no por la ruta conocida."""
    for id_ in IDS_DATASET:
        try:
            with descargar(URL_CKAN.format(id=urllib.request.quote(id_))) as r:
                doc = json.loads(r.read().decode("utf-8", "replace"))
        except Exception as exc:
            print(f"  CKAN {id_}: {exc}", flush=True)
            continue
        for rec in (doc.get("result") or {}).get("resources") or []:
            nombre = sin_tildes(rec.get("name") or "").lower()
            url = (rec.get("url") or "")
            if str(anio) in nombre + url.lower() and "gasto" in nombre and "ingreso" not in nombre:
                return url
    return URL_ARCHIVO_SUPUESTA.format(anio=anio)


def decodificar(raw):
    try:
        return raw.decode("utf-8").lstrip("\ufeff")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def lineas(resp, url):
    """Itera lineas de texto de una respuesta HTTP, o de un zip con un CSV."""
    if url.lower().endswith(".zip"):
        tmp = SALIDA_POR_DEFECTO / ".tmp.zip"
        tmp.parent.mkdir(parents=True, exist_ok=True)
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


def filas_csv(lineas_iter):
    """Encabezado normalizado, delimitador inferido y lector listo.

    El MEF ha usado "|", ";" y "," segun el anio: se infiere contando
    separadores en la primera linea, igual que scripts/gasto.py.
    """
    primera = next(lineas_iter)
    delim = max((",", ";", "|", "\t"), key=primera.count)
    lector = csv.reader(_concat(primera, lineas_iter), delimiter=delim)
    encabezado = [c.strip().strip('"').upper() for c in next(lector)]
    return encabezado, delim, lector


def _concat(primera, resto):
    yield primera
    yield from resto


def resolver_columnas(encabezado):
    """Mapea cada campo logico a su posicion en el encabezado normalizado."""
    usadas, idx = {}, {}
    for campo, candidatos in COLUMNAS.items():
        for c in candidatos:
            if c in encabezado:
                usadas[campo] = c
                idx[campo] = encabezado.index(c)
                break
    faltan = [c for c in OBLIGATORIAS if c not in usadas]
    if faltan:
        raise SystemExit(
            f"faltan columnas obligatorias {faltan}.\n"
            f"Encabezado real: {encabezado}\n"
            "Agregar el nombre correcto a COLUMNAS y repetir."
        )
    return usadas, idx


# ---- lectura -----------------------------------------------------------------
def leer(fuente_lineas, max_filas=None, inspeccionar=False):
    """Recorre el CSV y acumula las filas de pliegos universitarios."""
    try:
        encabezado, delim, lector = filas_csv(fuente_lineas)
    except StopIteration:
        raise SystemExit("el archivo esta vacio")

    if inspeccionar:
        print(f"delimitador: {delim!r}")
        print(f"columnas ({len(encabezado)}): {encabezado}")

    usadas, idx = resolver_columnas(encabezado)

    def val(fila, campo, pordefecto=""):
        i = idx.get(campo)
        return fila[i].strip() if i is not None and i < len(fila) else pordefecto

    panel = defaultdict(lambda: dict.fromkeys(MONTOS, 0.0))
    proyectos = defaultdict(lambda: dict.fromkeys(MONTOS, 0.0))
    pliegos = {}
    leidas = guardadas = 0
    muestra = []

    for fila in lector:
        leidas += 1
        if max_filas and leidas > max_filas:
            break
        nombre_pliego = val(fila, "pliego_nombre")
        if not es_universidad(nombre_pliego):
            continue
        guardadas += 1
        if inspeccionar and len(muestra) < 3:
            muestra.append(dict(zip(encabezado, fila)))

        codigo = val(fila, "pliego")
        pliegos.setdefault(codigo or nombre_pliego, {
            "pliego": codigo,
            "nombre": nombre_pliego,
            "sector": val(fila, "sector"),
            "departamento": val(fila, "departamento_nombre"),
        })

        clave = (
            val(fila, "anio"), val(fila, "mes"), codigo, nombre_pliego,
            val(fila, "fuente"), val(fila, "rubro"), val(fila, "rubro_nombre"),
            val(fila, "tipo_act_proy"), val(fila, "categoria_gasto"),
            val(fila, "generica"), val(fila, "generica_nombre"),
        )
        destino = panel[clave]
        for m in MONTOS:
            destino[m] += numero(val(fila, m, "0"))

        proy = val(fila, "producto_proyecto")
        if proy:
            clave_p = (val(fila, "anio"), codigo, nombre_pliego, val(fila, "rubro"),
                       val(fila, "tipo_act_proy"), proy,
                       val(fila, "producto_proyecto_nombre"))
            destino_p = proyectos[clave_p]
            for m in MONTOS:
                destino_p[m] += numero(val(fila, m, "0"))

        if leidas % 1_000_000 == 0:
            print(f"  {leidas:,} filas leidas, {guardadas:,} universitarias", flush=True)

    if inspeccionar:
        print("\nmuestra de filas universitarias:")
        for m in muestra:
            print(json.dumps(m, ensure_ascii=False, indent=1)[:1200])

    return {"panel": panel, "proyectos": proyectos, "pliegos": pliegos,
            "usadas": usadas, "encabezado": encabezado, "delimitador": delim,
            "filas_leidas": leidas, "filas_universitarias": guardadas}


# ---- escritura ---------------------------------------------------------------
CAMPOS_PANEL = ["anio", "mes", "pliego", "pliego_nombre", "fuente", "rubro",
                "rubro_nombre", "tipo_act_proy", "categoria_gasto", "generica",
                "generica_nombre"]
CAMPOS_PROY = ["anio", "pliego", "pliego_nombre", "rubro", "tipo_act_proy",
               "proyecto", "proyecto_nombre"]


def escribir_csv(ruta, campos, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(campos + list(MONTOS))
        for clave in sorted(datos):
            w.writerow(list(clave) + [round(datos[clave][m], 2) for m in MONTOS])
    return len(datos)


def controles(res):
    """Avisos sobre la calidad de lo leido. Lista vacia es buena senal."""
    avisos = []
    if not res["pliegos"]:
        avisos.append("ningun pliego universitario reconocido: revisar PATRON_UNIVERSIDAD")
    elif len(res["pliegos"]) < 30:
        avisos.append(f"solo {len(res['pliegos'])} pliegos universitarios; se esperan mas de 40")
    for campo in ("fuente", "rubro", "tipo_act_proy", "producto_proyecto"):
        if campo not in res["usadas"]:
            avisos.append(f"columna '{campo}' no encontrada: el panel queda sin esa dimension")
    total_pim = sum(v["pim"] for v in res["panel"].values())
    total_dev = sum(v["devengado"] for v in res["panel"].values())
    if total_pim <= 0:
        avisos.append("PIM total no positivo: revisar el parseo de montos")
    elif total_dev > total_pim * 1.02:
        avisos.append("devengado mayor que PIM: el archivo quiza repite el PIM por mes "
                      "en vez de registrar solo las modificaciones")
    meses = {c[1] for c in res["panel"]}
    if "00" not in meses and 0 not in meses and "0" not in meses:
        avisos.append("no hay mes '00': revisar si el PIM inicial viene en otro mes")
    return avisos


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--anio", type=int, default=datetime.now(LIMA).year)
    ap.add_argument("--archivo", help="CSV local, en vez de descargar")
    ap.add_argument("--inspeccionar", action="store_true", help="imprime encabezado y muestra; no escribe")
    ap.add_argument("--max-filas", type=int, default=None)
    ap.add_argument("--salida", default=str(SALIDA_POR_DEFECTO))
    args = ap.parse_args()

    if args.archivo:
        url = args.archivo
        print(f"leyendo {url}", flush=True)
        with open(url, encoding="utf-8", errors="replace") as f:
            res = leer(f, args.max_filas, args.inspeccionar)
    else:
        url = url_del_anio(args.anio)
        print(f"leyendo en streaming {url}", flush=True)
        with descargar(url) as resp:
            res = leer(lineas(resp, url), args.max_filas, args.inspeccionar)

    print(f"\n{res['filas_leidas']:,} filas leidas, "
          f"{res['filas_universitarias']:,} de pliegos universitarios, "
          f"{len(res['pliegos'])} pliegos")

    avisos = controles(res)
    for a in avisos:
        print(f"  AVISO: {a}")

    if args.inspeccionar:
        print("\n--inspeccionar: no se escribio nada")
        return

    salida = Path(args.salida)
    n_panel = escribir_csv(salida / f"panel_universidades_{args.anio}.csv",
                           CAMPOS_PANEL, res["panel"])
    n_proy = escribir_csv(salida / f"proyectos_universidades_{args.anio}.csv",
                          CAMPOS_PROY, res["proyectos"])

    meta = {
        "anio": args.anio,
        "fuente": "MEF, Portal de Datos Abiertos: Presupuesto y Ejecucion de Gasto (SIAF)",
        "url": url,
        "descargado": datetime.now(LIMA).isoformat(timespec="minutes"),
        "delimitador": res["delimitador"],
        "encabezado": res["encabezado"],
        "columnas_usadas": res["usadas"],
        "filas_leidas": res["filas_leidas"],
        "filas_universitarias": res["filas_universitarias"],
        "filas_panel": n_panel,
        "filas_proyectos": n_proy,
        "pliegos": sorted(res["pliegos"].values(), key=lambda p: p["nombre"]),
        "unidad": "soles corrientes",
        "controles": avisos,
    }
    ruta_meta = salida / f"panel_universidades_{args.anio}.json"
    ruta_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nescrito: {n_panel:,} filas de panel, {n_proy:,} de proyectos")
    print(f"metadatos: {ruta_meta}")


if __name__ == "__main__":
    main()
