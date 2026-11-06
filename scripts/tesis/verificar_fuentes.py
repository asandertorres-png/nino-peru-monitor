#!/usr/bin/env python3
"""Verifica que las fuentes de los 10 indicadores de la tesis existan.

Prueba cada fuente contra el servidor real y emite un veredicto por indicador.
No inventa ni sustituye nada: si una fuente no responde, lo dice.

POR QUE EXISTE ESTE ARCHIVO
---------------------------
La matriz de operacionalizacion declara 10 indicadores y, para varios, la
disponibilidad del dato estaba marcada como "no verificada". Verificarla a mano
es lento y se desactualiza. Esto la verifica en una corrida.

DONDE CORRERLO
--------------
Necesita salida a internet hacia archive-api.open-meteo.com,
www.cpc.ncep.noaa.gov, estadisticas.bcrp.gob.pe y www.inei.gob.pe. Si la red
donde se corre bloquea alguno, el script lo reporta como BLOQUEADO y no como
inexistente: son cosas distintas y no deben confundirse.

    python scripts/tesis/verificar_fuentes.py
    python scripts/tesis/verificar_fuentes.py --buscar-ipc-ciudades

Tambien hay un workflow manual: pestania Actions, "Verificar fuentes de la
tesis". El runner de GitHub si tiene salida a esos hosts, como lo prueba el
flujo diario del monitor.

Codigo de salida: 0 si ninguna fuente BLOQUEANTE fallo, 1 si alguna fallo.
"""

import argparse
import json
import socket
import ssl
import sys
import urllib.error
import urllib.request

TIEMPO_LIMITE = 45
AGENTE = "monitor-nino-peru/verificador-tesis (investigacion academica)"

OK = "OK"
VACIO = "RESPONDE PERO SIN EL DATO"
BLOQUEADO = "BLOQUEADO POR LA RED"
FALLO = "FALLO"


def _pedir(url, limite_bytes=None):
    """Devuelve (estado, texto_o_mensaje). Nunca lanza."""
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    try:
        with urllib.request.urlopen(peticion, timeout=TIEMPO_LIMITE) as r:
            crudo = r.read(limite_bytes) if limite_bytes else r.read()
    except urllib.error.HTTPError as e:
        return FALLO, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        motivo = str(e.reason)
        if any(s in motivo for s in ("Name or service not known", "nodename nor servname",
                                     "Temporary failure in name resolution",
                                     "Tunnel connection failed", "403")):
            return BLOQUEADO, motivo
        return FALLO, motivo
    except (socket.timeout, TimeoutError):
        return FALLO, "tiempo de espera agotado"
    except ssl.SSLError as e:
        return FALLO, f"TLS: {e}"
    except Exception as e:  # red: cualquier cosa puede pasar
        return FALLO, f"{type(e).__name__}: {e}"

    for cod in ("utf-8", "latin-1"):
        try:
            return OK, crudo.decode(cod)
        except UnicodeDecodeError:
            continue
    return OK, ""


# --------------------------------------------------------------- comprobaciones

def era5_mensual():
    """Indicadores 1 y 2: serie diaria de ERA5 para un punto del Peru."""
    url = ("https://archive-api.open-meteo.com/v1/archive"
           "?latitude=-13.52&longitude=-71.97"
           "&start_date=2017-01-01&end_date=2017-03-31"
           "&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
           "&timezone=UTC")
    estado, cuerpo = _pedir(url)
    if estado != OK:
        return estado, cuerpo
    try:
        d = json.loads(cuerpo)["daily"]
    except Exception as e:
        return VACIO, f"respuesta sin 'daily': {e}"
    dias = len(d.get("time") or [])
    pp = [x for x in (d.get("precipitation_sum") or []) if x is not None]
    tx = [x for x in (d.get("temperature_2m_max") or []) if x is not None]
    if dias < 80 or not pp or not tx:
        return VACIO, f"{dias} dias, {len(pp)} con lluvia, {len(tx)} con tmax"
    return OK, (f"{dias} dias; lluvia y temperatura presentes. "
                f"Con 30 anios por punto se obtiene la media Y la desviacion "
                f"estandar por mes, que es lo que hoy falta")


def noaa_oni():
    """Indicador 3: serie ONI completa de la NOAA."""
    estado, cuerpo = _pedir("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt")
    if estado != OK:
        return estado, cuerpo
    lineas = [l for l in cuerpo.splitlines() if l.strip()]
    if len(lineas) < 100:
        return VACIO, f"solo {len(lineas)} lineas"
    anios = []
    for l in lineas[1:]:
        partes = l.split()
        if len(partes) >= 2 and partes[1].isdigit():
            anios.append(int(partes[1]))
    if not anios:
        return VACIO, "no se reconocieron anios"
    return OK, (f"{len(lineas) - 1} trimestres, de {min(anios)} a {max(anios)}. "
                f"El producto del repositorio guarda solo desde 2021")


def noaa_nino12():
    """Indicador 4: anomalia mensual de TSM de la region Nino 1+2, base del ICEN."""
    candidatas = [
        "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii",
        "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.81-10.ascii",
        "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices",
    ]
    ultimo = (FALLO, "ninguna URL candidata respondio")
    for url in candidatas:
        estado, cuerpo = _pedir(url)
        if estado != OK:
            ultimo = (estado, f"{url.rsplit('/', 1)[-1]}: {cuerpo}")
            continue
        lineas = [l for l in cuerpo.splitlines() if l.strip()]
        if len(lineas) < 50:
            ultimo = (VACIO, f"{url.rsplit('/', 1)[-1]}: {len(lineas)} lineas")
            continue
        cabecera = lineas[0].upper()
        tiene_12 = "NINO1+2" in cabecera.replace(" ", "") or "ANOM" in cabecera
        return OK, (f"{url.rsplit('/', 1)[-1]}: {len(lineas) - 1} meses"
                    + ("; incluye columnas de Nino 1+2" if tiene_12 else
                       "; REVISAR a mano que traiga Nino 1+2"))
    return ultimo


def bcrp_api():
    """Referencia: que la API del BCRP responda, con el IPC nacional."""
    url = ("https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
           "PN38705PM/json/2023-1/2023-6")
    estado, cuerpo = _pedir(url)
    if estado != OK:
        return estado, cuerpo
    try:
        d = json.loads(cuerpo)
    except Exception as e:
        return VACIO, f"respuesta no es JSON: {e}"
    periodos = d.get("periods") or []
    nombres = [s.get("name", "?") for s in d.get("config", {}).get("series", [])]
    if not periodos:
        return VACIO, f"sin 'periods'; claves: {sorted(d)}"
    return OK, f"{len(periodos)} periodos; serie: {nombres[:1]}"


def bcrp_ipc_ciudades():
    """Indicadores 7 y 8: buscar en el catalogo del BCRP series de IPC por ciudad.

    La primera version de esta funcion buscaba las palabras clave en la fila
    COMPLETA y con coincidencia de subcadena. Dio 188 falsos positivos por dos
    razones: "precios al consumidor" aparece en la METODOLOGIA de series que no
    son IPC, como el tipo de cambio real, que se calcula con ratios de IPC; y
    "ica" es subcadena de "estadistica", "metodologica" y "Republica", de modo
    que casi toda fila coincidia con la ciudad de Ica.

    Esta version busca solo en las columnas de categoria, grupo y nombre de la
    serie --no en descripcion ni metodologia-- y exige que el nombre de la
    ciudad aparezca como palabra completa.
    """
    import csv
    import io
    import re

    estado, cuerpo = _pedir(
        "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata")
    if estado != OK:
        return estado, cuerpo

    lineas = [l for l in cuerpo.splitlines() if l.strip()]
    if len(lineas) < 3:
        return VACIO, f"catalogo con {len(lineas)} lineas; parece una respuesta de error"

    sep = max((";", ",", "\t"), key=lambda s: lineas[0].count(s))
    filas = list(csv.reader(io.StringIO(cuerpo), delimiter=sep))
    if not filas:
        return VACIO, "el catalogo no se pudo leer como tabla"

    cabecera = [h.strip().lower() for h in filas[0]]
    # Solo categoria, grupo y nombre de la serie. Descripcion y metodologia
    # quedan fuera a proposito: ahi estaba el falso positivo.
    cols = [i for i, h in enumerate(cabecera)
            if any(k in h for k in ("categor", "grupo", "nombre"))]
    if not cols:
        cols = [1, 2, 3]  # posiciones del formato documentado

    CIUDADES_IPC = [
        "Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", "Cuzco",
        "Huancayo", "Iquitos", "Puno", "Tacna", "Ica", "Chimbote", "Cajamarca",
        "Ayacucho", "Abancay", "Huaraz", "Huanuco", "Huánuco", "Moquegua",
        "Moyobamba", "Pucallpa", "Puerto Maldonado", "Tumbes", "Chachapoyas",
        "Cerro de Pasco", "Huancavelica", "Callao", "Tarapoto",
    ]
    re_ciudad = re.compile(r"\b(" + "|".join(CIUDADES_IPC) + r")\b", re.IGNORECASE)
    re_ipc = re.compile(r"\bIPC\b|precios al consumidor", re.IGNORECASE)
    # "aliment" a secas daba otro falso positivo: coincide con "IPC Sin
    # Alimentos y Energia", que es inflacion subyacente y EXCLUYE los
    # alimentos, justo lo contrario de lo que la tesis necesita.
    re_alim = re.compile(r"aliment", re.IGNORECASE)
    re_sin_alim = re.compile(r"(sin|no|excluy\w*|excl\.)\s+aliment", re.IGNORECASE)

    from collections import Counter
    con_ipc, por_ciudad, alim_real, alim_excluye = [], [], [], []
    ciudades_vistas = Counter()
    for fila in filas[1:]:
        texto = " | ".join(fila[i] for i in cols if i < len(fila))
        if not re_ipc.search(texto):
            continue
        cod = fila[0] if fila else "?"
        con_ipc.append((cod, texto))
        m = re_ciudad.search(texto)
        if not m:
            continue
        por_ciudad.append((cod, texto))
        ciudades_vistas[m.group(1).title()] += 1
        if re_alim.search(texto):
            (alim_excluye if re_sin_alim.search(texto) else alim_real).append((cod, texto))

    if not por_ciudad:
        return VACIO, (
            f"{len(filas) - 1} series; {len(con_ipc)} de IPC por nombre, y "
            f"NINGUNA nombra una ciudad. El BCRP no republica el IPC por "
            f"ciudad: hay que ir al INEI")

    distintas = sorted(ciudades_vistas)
    resumen_c = ", ".join(f"{c} ({n})" for c, n in ciudades_vistas.most_common())

    # El veredicto depende de cuantas ciudades DISTINTAS hay, no de cuantas
    # series. Una sola ciudad significa la serie nacional de referencia.
    if len(distintas) <= 1:
        veredicto = (
            f"SOLO {len(distintas)} ciudad en todo el catalogo: {resumen_c}. "
            f"El BCRP publica el IPC de esa plaza como referencia nacional, no "
            f"un panel de 26 ciudades. Los indicadores 7 y 8 NO salen del BCRP: "
            f"hay que ir a los boletines del INEI")
        estado_final = VACIO
    elif not alim_real:
        veredicto = (
            f"{len(distintas)} ciudades distintas: {resumen_c}. Pero NINGUNA "
            f"serie desagrega alimentos; las {len(alim_excluye)} que mencionan "
            f"la palabra son del tipo 'Sin Alimentos y Energia', que los "
            f"EXCLUYEN. Hay IPC general por ciudad, no por grupo de gasto: se "
            f"activa el plan B del protocolo")
        estado_final = VACIO
    else:
        m3 = "\n       ".join(f"{c}  {d[:95]}" for c, d in alim_real[:8])
        veredicto = (
            f"{len(distintas)} ciudades distintas: {resumen_c}. Y {len(alim_real)} "
            f"series desagregan alimentos de verdad (descartando las "
            f"{len(alim_excluye)} del tipo 'Sin Alimentos'):\n       {m3}")
        estado_final = OK

    muestra = "\n       ".join(f"{c}  {d[:95]}" for c, d in por_ciudad[:5])
    return estado_final, (
        f"{len(con_ipc)} series de IPC por nombre, {len(por_ciudad)} nombran "
        f"alguna ciudad.\n     {veredicto}\n     Muestra de las que nombran "
        f"ciudad:\n       {muestra}")


def inei_portal():
    """Indicadores 5, 6, 7 y 8: que el portal del INEI responda."""
    estado, cuerpo = _pedir("https://www.inei.gob.pe/estadisticas/indice-tematico/price-indexes/",
                            limite_bytes=200000)
    if estado != OK:
        return estado, cuerpo
    texto = cuerpo.lower()
    pistas = [p for p in ("precios al consumidor", "ipc", "alimentos") if p in texto]
    return OK, f"responde; menciona {pistas or 'nada reconocible'}"


COMPROBACIONES = [
    ("1, 2", "Anomalias estandarizadas de lluvia y temperatura",
     "ERA5 via Open-Meteo Archive", era5_mensual, True),
    ("3", "Indice ONI (region Nino 3.4)",
     "NOAA/CPC", noaa_oni, True),
    ("4", "ICEN-replica (region Nino 1+2)",
     "NOAA/CPC", noaa_nino12, True),
    ("ref", "API del BCRP operativa (IPC nacional)",
     "BCRP", bcrp_api, False),
    ("7, 8", "IPC de alimentos POR CIUDAD",
     "catalogo del BCRP", bcrp_ipc_ciudades, True),
    ("5, 6", "VAB departamental y ponderaciones del IPC",
     "portal del INEI", inei_portal, False),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--buscar-ipc-ciudades", action="store_true",
                    help="solo la busqueda de IPC por ciudad en el catalogo del BCRP")
    args = ap.parse_args()

    pruebas = ([c for c in COMPROBACIONES if c[0] == "7, 8"]
               if args.buscar_ipc_ciudades else COMPROBACIONES)

    print("=" * 78)
    print("VERIFICACION DE FUENTES DE LOS INDICADORES DE LA TESIS")
    print("=" * 78)

    bloqueantes_fallidos = []
    hubo_bloqueo_de_red = False

    for codigo, nombre, fuente, funcion, bloqueante in pruebas:
        print(f"\n[{codigo}] {nombre}")
        print(f"      fuente: {fuente}")
        estado, detalle = funcion()
        marca = {OK: "  OK  ", VACIO: " VACIO", BLOQUEADO: " RED  ", FALLO: " FALLO"}[estado]
        print(f"      [{marca}] {detalle}")
        if estado == BLOQUEADO:
            hubo_bloqueo_de_red = True
        if bloqueante and estado != OK:
            bloqueantes_fallidos.append((codigo, nombre, estado))

    print("\n" + "=" * 78)
    if hubo_bloqueo_de_red:
        print("AVISO: al menos una fuente quedo BLOQUEADA por la red de esta maquina.")
        print("Bloqueado no es inexistente. Correr donde haya salida a esos hosts,")
        print("o desde la pestania Actions del repositorio.")
    if bloqueantes_fallidos:
        print(f"\n{len(bloqueantes_fallidos)} fuente(s) BLOQUEANTE(S) sin confirmar:")
        for codigo, nombre, estado in bloqueantes_fallidos:
            print(f"  - [{codigo}] {nombre}: {estado}")
        print("\nRegla del proyecto: un indicador cuya fuente no se confirme se")
        print("elimina de la matriz antes de estimar; no se sustituye en silencio.")
        return 1

    print("\nTodas las fuentes bloqueantes quedaron confirmadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
