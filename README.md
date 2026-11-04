# Monitor El Niño · Perú

Mapa interactivo que muestra, departamento por departamento, cómo se están
desviando las condiciones climáticas actuales respecto de su normal
1991–2020, en el contexto del estado del ENSO (El Niño–Oscilación del Sur).
Los datos se actualizan solos cada 6 horas mediante GitHub Actions. No es tiempo
real: cada fuente tiene su propio rezago, y la interfaz muestra la fecha del dato
más reciente de cada una (ver docs/METODOLOGIA.md, sección de frescura).

## Qué hace

- Descarga el índice **ONI** de la NOAA/CPC (trimestral) y la **TSM semanal** de la
  región Niño 3.4 (semanal, los lunes).
- Consulta, para la capital de cada uno de los 25 departamentos y para un punto
  representativo de cada una de las 195 provincias, la lluvia y la temperatura
  de los últimos 30 días, las condiciones de hoy y el pronóstico a 7 días
  (Open-Meteo). Las provincias sin cobertura del modelo se muestran en gris.
- Compara esos valores con las normales climáticas 1991–2020 calculadas a
  partir del reanálisis ERA5.
- Publica `data/estado.json` y lo pinta en un mapa Leaflet con tres capas:
  nivel de alerta, anomalía de lluvia y anomalía térmica.

## Estructura

```
scripts/config.py             departamentos, umbrales y endpoints
scripts/provincias.py         provincias desde el GeoJSON: punto y zona
scripts/niveles.py            selector de nivel (departamento / provincia)
scripts/fetch_oni.py          índice ONI y TSM semanal de la NOAA
scripts/calcular_normales.py  normales 1991-2020 (se corre una sola vez)
scripts/actualizar.py         construye data/estado.json (corre cada 6 horas)
scripts/lectura.py            lectura automática del ENSO y del mapa (reglas fijas)
scripts/gasto.py              gasto del PP 0068 por departamento (MEF, SIAF; corre a diario)
scripts/ipc.py                IPC de alimentos por ciudad (INEI; corre a diario, cambia cada mes)
docs/                         sitio publicado en GitHub Pages
data/                         salidas en JSON, versionadas
.github/workflows/            automatización diaria
```

## Uso local

```bash
PYTHONPATH=scripts python scripts/calcular_normales.py   # una sola vez, 30-90 min
PYTHONPATH=scripts python scripts/verificar_normales.py  # controla el resultado
PYTHONPATH=scripts python scripts/calcular_normales.py --nivel provincia   # varias horas
PYTHONPATH=scripts python scripts/verificar_normales.py --nivel provincia
PYTHONPATH=scripts python scripts/fetch_oni.py
PYTHONPATH=scripts python scripts/actualizar.py
PYTHONPATH=scripts python scripts/actualizar.py --nivel provincia
python -m http.server 8000 --directory docs              # abrir localhost:8000
```

Solo necesita Python 3.9 o superior; no usa dependencias externas ni API keys.

`calcular_normales.py` baja 30 anios de serie diaria para cada una de las 25
capitales, en tramos de 5 anios y con pausas entre pedidos: la API de archivo
de Open-Meteo corta las transferencias largas y responde HTTP 429 cuando se la
consulta seguido. Es lento por diseno. Si la corrida se interrumpe, el avance
queda en `data/.normales_parcial.json` y la siguiente invocacion retoma donde
quedo; `--reiniciar` descarta ese avance.

Las fuentes deben estar accesibles desde la red donde se corra:
`archive-api.open-meteo.com`, `api.open-meteo.com` y `www.cpc.ncep.noaa.gov`.

## Publicación

En Settings → Pages, elegir "Deploy from a branch", rama `main`, carpeta `/docs`.

## Límites

Cada departamento está representado por el punto de su capital, lo que es una
simplificación fuerte en departamentos con gradiente altitudinal marcado
(Arequipa, Áncash, Cusco). Los umbrales de alerta son provisionales. Ver
[docs/METODOLOGIA.md](docs/METODOLOGIA.md).
