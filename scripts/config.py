"""Configuracion base: departamentos del Peru y parametros del monitor."""

# Normales climaticas de referencia (periodo estandar OMM)
NORMAL_INICIO = "1991-01-01"
NORMAL_FIN = "2020-12-31"

# Umbrales ONI (NOAA/CPC) para clasificar el estado de ENSO
UMBRALES_ONI = [
    (2.0, "El Nino muy fuerte"),
    (1.5, "El Nino fuerte"),
    (1.0, "El Nino moderado"),
    (0.5, "El Nino debil"),
    (-0.5, "Neutro"),
    (-1.0, "La Nina debil"),
    (-1.5, "La Nina moderada"),
    (-99, "La Nina fuerte"),
]

# 25 departamentos (incluye Callao). Coordenadas de la capital departamental.
# 'zona' agrupa por regimen de impacto de El Nino en el Peru:
#   costa_norte  -> lluvias e inundaciones intensas en fase calida
#   costa_centro_sur -> deficit de lluvia, anomalia termica marina
#   sierra_norte / sierra_sur -> deficit o exceso segun altitud y latitud
#   selva -> respuesta mas debil y rezagada
DEPARTAMENTOS = [
    {"nombre": "Amazonas",       "capital": "Chachapoyas",      "lat": -6.23,  "lon": -77.87, "zona": "selva"},
    {"nombre": "Ancash",         "capital": "Huaraz",           "lat": -9.53,  "lon": -77.53, "zona": "sierra_norte"},
    {"nombre": "Apurimac",       "capital": "Abancay",          "lat": -13.63, "lon": -72.88, "zona": "sierra_sur"},
    {"nombre": "Arequipa",       "capital": "Arequipa",         "lat": -16.41, "lon": -71.54, "zona": "sierra_sur"},
    {"nombre": "Ayacucho",       "capital": "Ayacucho",         "lat": -13.16, "lon": -74.22, "zona": "sierra_sur"},
    {"nombre": "Cajamarca",      "capital": "Cajamarca",        "lat": -7.16,  "lon": -78.51, "zona": "sierra_norte"},
    {"nombre": "Callao",         "capital": "Callao",           "lat": -12.05, "lon": -77.12, "zona": "costa_centro_sur"},
    {"nombre": "Cusco",          "capital": "Cusco",            "lat": -13.52, "lon": -71.97, "zona": "sierra_sur"},
    {"nombre": "Huancavelica",   "capital": "Huancavelica",     "lat": -12.79, "lon": -74.97, "zona": "sierra_sur"},
    {"nombre": "Huanuco",        "capital": "Huanuco",          "lat": -9.93,  "lon": -76.24, "zona": "sierra_norte"},
    {"nombre": "Ica",            "capital": "Ica",              "lat": -14.07, "lon": -75.73, "zona": "costa_centro_sur"},
    {"nombre": "Junin",          "capital": "Huancayo",         "lat": -12.07, "lon": -75.21, "zona": "sierra_sur"},
    {"nombre": "La Libertad",    "capital": "Trujillo",         "lat": -8.11,  "lon": -79.03, "zona": "costa_norte"},
    {"nombre": "Lambayeque",     "capital": "Chiclayo",         "lat": -6.77,  "lon": -79.84, "zona": "costa_norte"},
    {"nombre": "Lima",           "capital": "Lima",             "lat": -12.05, "lon": -77.04, "zona": "costa_centro_sur"},
    {"nombre": "Loreto",         "capital": "Iquitos",          "lat": -3.75,  "lon": -73.25, "zona": "selva"},
    {"nombre": "Madre de Dios",  "capital": "Puerto Maldonado", "lat": -12.60, "lon": -69.19, "zona": "selva"},
    {"nombre": "Moquegua",       "capital": "Moquegua",         "lat": -17.19, "lon": -70.93, "zona": "costa_centro_sur"},
    {"nombre": "Pasco",          "capital": "Cerro de Pasco",   "lat": -10.68, "lon": -76.26, "zona": "sierra_norte"},
    {"nombre": "Piura",          "capital": "Piura",            "lat": -5.19,  "lon": -80.63, "zona": "costa_norte"},
    {"nombre": "Puno",           "capital": "Puno",             "lat": -15.84, "lon": -70.03, "zona": "sierra_sur"},
    {"nombre": "San Martin",     "capital": "Moyobamba",        "lat": -6.03,  "lon": -76.97, "zona": "selva"},
    {"nombre": "Tacna",          "capital": "Tacna",            "lat": -18.01, "lon": -70.25, "zona": "costa_centro_sur"},
    {"nombre": "Tumbes",         "capital": "Tumbes",           "lat": -3.57,  "lon": -80.46, "zona": "costa_norte"},
    {"nombre": "Ucayali",        "capital": "Pucallpa",         "lat": -8.38,  "lon": -74.55, "zona": "selva"},
]

API_ACTUAL = "https://api.open-meteo.com/v1/forecast"
API_ARCHIVO = "https://archive-api.open-meteo.com/v1/archive"

# Modelo del archivo por nivel. None = el que la API elige por defecto (ERA5,
# ~25 km), que es lo que usan las normales departamentales ya publicadas.
# Para provincias se pide ERA5-Land (~9 km): muchas provincias son mas chicas
# que una celda de ERA5. ERA5-Land no cubre el mar: un punto costero puede
# quedar sin datos y se registra como tal. Nombre del parametro pendiente de
# verificar contra la API en la primera corrida.
MODELO_ARCHIVO = {"departamento": None, "provincia": "era5_land"}
URL_ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
# TSM semanal de la region Nino 3.4 (NOAA/CPC, serie 1991-2020). Se actualiza
# los lunes. Formato del archivo pendiente de verificar: ver fetch_oni.py.
URL_WKSST = "https://www.cpc.ncep.noaa.gov/data/indices/wksst9120.for"

# ICEN (ENFEN/IGP): media movil de 3 meses de la anomalia mensual de TSM en la
# region Nino 1+2 (ERSSTv5, base 1991-2020). Es el indice oficial del Nino
# costero. El IGP lo publica como texto plano; la URL cambio de mayusculas
# entre documentos, asi que se prueban en orden. Formato interpretado de forma
# tolerante: filas con anio, mes y valor (ver fetch_oni.parsear_icen).
URLS_ICEN = [
    "http://met.igp.gob.pe/datos/ICEN.txt",
    "http://www.met.igp.gob.pe/datos/icen.txt",
]

# Categorias del ICEN segun la nota tecnica del ENFEN (2012). Los valores de
# los ultimos meses son preliminares (ICENtmp) hasta que el ENFEN los confirma.
def clasificar_icen(v: float) -> str:
    if v >= 3.0:
        return "calida extraordinaria"
    if v >= 1.7:
        return "calida fuerte"
    if v >= 1.0:
        return "calida moderada"
    if v >= 0.4:
        return "calida debil"
    if v > -1.0:
        return "neutro"
    if v > -1.2:
        return "fria debil"
    if v > -1.4:
        return "fria moderada"
    return "fria fuerte"

# Umbral PROVISIONAL de normal mensual de lluvia (mm). Por debajo, la anomalia
# porcentual no es informativa (la normal es casi nula y cualquier lluvia da
# un porcentaje enorme). En ese caso el mapa muestra el acumulado en mm y el
# nivel de alerta no usa la anomalia de lluvia. Ver docs/METODOLOGIA.md,
# limitacion 4. No calibrado: fijar con criterio y revisar con datos de
# SENAMHI cuando esten disponibles.
UMBRAL_NORMAL_BAJA_MM = 5.0

# Altitud de referencia de cada capital (m s.n.m.). Valores APROXIMADOS, de
# referencia cartografica; no son una medicion. Sirven para cuantificar cuanto
# difiere del relieve que promedia el modelo en el punto de la capital (ver
# METODOLOGIA.md, sesgo de representacion puntual). Verificar contra IGN o
# SENAMHI antes de citar cifras.
ALTITUD_CAPITAL_M = {
    "Amazonas": 2334, "Ancash": 3052, "Apurimac": 2378, "Arequipa": 2335,
    "Ayacucho": 2761, "Cajamarca": 2750, "Callao": 5, "Cusco": 3399,
    "Huancavelica": 3676, "Huanuco": 1894, "Ica": 406, "Junin": 3259,
    "La Libertad": 34, "Lambayeque": 29, "Lima": 154, "Loreto": 106,
    "Madre de Dios": 183, "Moquegua": 1410, "Pasco": 4330, "Piura": 29,
    "Puno": 3830, "San Martin": 860, "Tacna": 562, "Tumbes": 7,
    "Ucayali": 154,
}


def clasificar_oni(valor: float) -> str:
    for umbral, etiqueta in UMBRALES_ONI:
        if valor >= umbral:
            return etiqueta
    return "indeterminado"
