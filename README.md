# Monitor El Niño · Perú

Mapa interactivo que muestra, departamento por departamento, cómo se están
desviando las condiciones climáticas actuales respecto de su normal
1991–2020, en el contexto del estado del ENSO (El Niño–Oscilación del Sur).
Los datos se actualizan solos todos los días mediante GitHub Actions.

## Qué hace

- Descarga el índice **ONI** de la NOAA/CPC (anomalía de TSM en la región Niño 3.4).
- Consulta, para la capital de cada uno de los 25 departamentos, la lluvia y la
  temperatura de los últimos 30 días más el pronóstico a 7 días (Open-Meteo).
- Compara esos valores con las normales climáticas 1991–2020 calculadas a
  partir del reanálisis ERA5.
- Publica `data/estado.json` y lo pinta en un mapa Leaflet con tres capas:
  nivel de alerta, anomalía de lluvia y anomalía térmica.

## Estructura

```
scripts/config.py             departamentos, umbrales y endpoints
scripts/fetch_oni.py          índice ONI de la NOAA
scripts/calcular_normales.py  normales 1991-2020 (se corre una sola vez)
scripts/actualizar.py         construye data/estado.json (corre a diario)
docs/                         sitio publicado en GitHub Pages
data/                         salidas en JSON, versionadas
.github/workflows/            automatización diaria
```

## Uso local

```bash
PYTHONPATH=scripts python scripts/calcular_normales.py   # una sola vez, ~5 min
PYTHONPATH=scripts python scripts/fetch_oni.py
PYTHONPATH=scripts python scripts/actualizar.py
python -m http.server 8000 --directory docs              # abrir localhost:8000
```

Solo necesita Python 3.9 o superior; no usa dependencias externas ni API keys.

## Publicación

En Settings → Pages, elegir "Deploy from a branch", rama `main`, carpeta `/docs`.

## Límites

Cada departamento está representado por el punto de su capital, lo que es una
simplificación fuerte en departamentos con gradiente altitudinal marcado
(Arequipa, Áncash, Cusco). Los umbrales de alerta son provisionales. Ver
[docs/METODOLOGIA.md](docs/METODOLOGIA.md).
