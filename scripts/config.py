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
URL_ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"


def clasificar_oni(valor: float) -> str:
    for umbral, etiqueta in UMBRALES_ONI:
        if valor >= umbral:
            return etiqueta
    return "indeterminado"
