"""Cliente HTTP con reintentos y esperas largas para las fuentes del monitor.

La API publica de Open-Meteo corta las transferencias largas y responde HTTP
429 cuando se la consulta seguido. Todos los pedidos del proyecto (Open-Meteo
y NOAA) pasan por aqui para que la politica de reintentos sea una sola,
documentada y facil de ajustar.

Politica de espera:
  - HTTP 429 (limite de uso): espera larga y creciente -- 90s, 180s, 360s,
    720s, con tope de 900s -- respetando la cabecera Retry-After cuando la API
    la manda. Son los cortes que mas se dan al bajar 30 anios por departamento.
  - HTTP 5xx y fallos de red (timeout, conexion cortada a mitad de
    transferencia): espera moderada y creciente -- 10s, 20s, 40s, ...
  - Otros 4xx: el pedido esta mal armado, reintentar no sirve; se reporta el
    motivo que devuelve Open-Meteo y se corta.

Todas las esperas llevan un jitter de +-15% para no sincronizar reintentos.
"""
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request

INTENTOS = 8          # intentos por pedido antes de darse por vencido
ESPERA_BASE_429 = 90  # s: primera espera tras un 429
ESPERA_BASE_RED = 10  # s: primera espera ante 5xx o fallo de red
ESPERA_MAX = 900      # s: tope por reintento (15 min)
TIMEOUT = 180         # s: un tramo de 5 anios puede tardar bastante

_429_VISTOS = 0


class ErrorApi(RuntimeError):
    """Pedido que no tiene sentido reintentar, o que agoto los reintentos."""


def rate_limits_vistos() -> int:
    """Cuantos HTTP 429 acumulo el proceso. Sirve para alargar las pausas
    entre departamentos cuando la API empieza a estrangular."""
    return _429_VISTOS


def _motivo(exc: urllib.error.HTTPError) -> str:
    """Extrae el campo 'reason' del cuerpo de error de Open-Meteo."""
    try:
        cuerpo = exc.read().decode("utf-8", "replace")
    except Exception:
        return "(sin cuerpo)"
    try:
        return str(json.loads(cuerpo).get("reason", cuerpo[:200]))
    except Exception:
        return cuerpo[:200]


def _retry_after(exc: urllib.error.HTTPError):
    """Segundos pedidos por la cabecera Retry-After, si viene y es un numero."""
    cabeceras = getattr(exc, "headers", None)
    valor = cabeceras.get("Retry-After") if cabeceras else None
    if not valor:
        return None
    try:
        return max(1, int(float(str(valor).strip())))
    except (TypeError, ValueError):
        return None  # tambien puede venir como fecha HTTP; ahi usamos la nuestra


def _con_jitter(espera: int) -> int:
    return max(1, min(ESPERA_MAX, round(espera * random.uniform(0.85, 1.15))))


def descargar(url, intentos=INTENTOS, timeout=TIMEOUT, sangria="    ",
              validar=None):
    """Descarga una URL y reintenta segun la politica de arriba.

    Si se pasa `validar`, se aplica al cuerpo dentro del bucle de reintentos:
    un ValueError de `validar` (cuerpo truncado, HTML en lugar de JSON) se
    reintenta como una falla de red; un ErrorApi se propaga sin reintentar.
    """
    global _429_VISTOS
    espera_429 = ESPERA_BASE_429
    espera_red = ESPERA_BASE_RED
    ultimo = None

    for intento in range(1, intentos + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                crudo = r.read().decode("utf-8")
            return validar(crudo) if validar else crudo

        except ErrorApi:
            raise

        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code == 429:
                _429_VISTOS += 1
                espera = _retry_after(e) or espera_429
                espera_429 = min(espera_429 * 2, ESPERA_MAX)
                etiqueta = "HTTP 429 (limite de uso de la API)"
            elif 500 <= e.code < 600:
                espera = espera_red
                espera_red = min(espera_red * 2, ESPERA_MAX)
                etiqueta = f"HTTP {e.code} (falla del servidor)"
            else:
                raise ErrorApi(
                    f"HTTP {e.code}, no se reintenta: {_motivo(e)}") from e

        except Exception as e:  # timeout, conexion cortada a mitad, DNS
            ultimo = e
            espera = espera_red
            espera_red = min(espera_red * 2, ESPERA_MAX)
            etiqueta = f"{type(e).__name__}: {e}"

        if intento == intentos:
            raise ErrorApi(
                f"sin exito tras {intentos} intentos; ultimo fallo: {etiqueta}"
            ) from ultimo

        espera = _con_jitter(espera)
        print(f"{sangria}intento {intento}/{intentos} fallo -- {etiqueta}; "
              f"espero {espera}s", flush=True)
        time.sleep(espera)


def _validar_json(crudo):
    """Convierte el cuerpo en JSON. Un cuerpo que no es JSON es transitorio
    (corte o pagina de error con HTTP 200): se reintenta."""
    try:
        datos = json.loads(crudo)
    except json.JSONDecodeError as e:
        raise ValueError(f"respuesta no es JSON valido: {e}") from e
    # Open-Meteo tambien puede devolver 200 con un error dentro del cuerpo;
    # ese error es de pedido, no de red: no se reintenta.
    if isinstance(datos, dict) and datos.get("error"):
        raise ErrorApi(f"Open-Meteo: {datos.get('reason', 'error sin motivo')}")
    return datos


def pedir_json(url_base, params, intentos=INTENTOS, timeout=TIMEOUT,
               sangria="    "):
    """Pide un JSON a una API de Open-Meteo con la politica de reintentos."""
    url = f"{url_base}?{urllib.parse.urlencode(params)}"
    return descargar(url, intentos=intentos, timeout=timeout,
                     sangria=sangria, validar=_validar_json)


def pedir_lote(url_base, params_comunes, puntos, intentos=INTENTOS,
               timeout=TIMEOUT, sangria="    "):
    """Una sola peticion para varios puntos: Open-Meteo acepta listas de
    coordenadas separadas por comas y devuelve una lista de resultados en el
    mismo orden. Para un solo punto devuelve un dict; aqui se normaliza a
    lista para que el llamador no distinga casos."""
    params = dict(params_comunes)
    params["latitude"] = ",".join(str(p["lat"]) for p in puntos)
    params["longitude"] = ",".join(str(p["lon"]) for p in puntos)
    datos = pedir_json(url_base, params, intentos=intentos, timeout=timeout,
                       sangria=sangria)
    if isinstance(datos, dict):
        datos = [datos]
    if len(datos) != len(puntos):
        raise ErrorApi(f"la API devolvio {len(datos)} resultados para "
                       f"{len(puntos)} puntos")
    return datos
