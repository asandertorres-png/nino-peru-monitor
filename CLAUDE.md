# Contexto para sesiones de Claude Code

Proyecto de monitoreo del impacto regional de El Niño en el Perú.
Autor: Alexander Torres Uchupe (economista, UNSAAC, Cusco).

## Convenciones

- Español en comentarios, documentación y nombres de variables.
- Python estándar: sin dependencias externas salvo que haya razón fuerte.
  Si se agregan, van en `requirements.txt` y se usa `pip`, no `pip3`.
- Los JSON de `data/` son productos versionados: el flujo diario los reescribe.
- Nada de API keys: todas las fuentes usadas son abiertas.

## Rigor metodológico

Este proyecto puede terminar sustentando análisis académico, así que:
- Toda anomalía declara su periodo base (1991–2020) y su fuente.
- Los umbrales de alerta son provisionales y están marcados como tales.
  No presentarlos como oficiales ni equipararlos a los avisos de SENAMHI,
  ENFEN o INDECI.
- Distinguir siempre ONI (región Niño 3.4, criterio NOAA) de ICEN
  (región Niño 1+2, criterio ENFEN) — el Niño costero peruano no coincide
  necesariamente con el Niño del Pacífico central.

## Tareas pendientes de mayor envergadura

1. Incorporar el ICEN del ENFEN/IGP y mostrar ambos índices en paralelo.
2. Reemplazar el punto de la capital por una media espacial por departamento
   (grilla de puntos ponderada por superficie o por población).
3. Serie histórica: comparar el evento actual con 1982-83, 1997-98 y 2015-16
   y con el Niño costero de 2017 y 2023.
4. Capa de exposición económica: PBI agropecuario y pesquero departamental
   (INEI) para pasar de anomalía climática a impacto económico potencial.
5. Validar los umbrales de alerta contra registros de emergencias de INDECI.
