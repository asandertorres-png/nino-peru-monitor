# Metodología

## Indicadores del estado del ENSO

Se muestran dos indicadores de la NOAA/CPC, y la interfaz los distingue:

- **ONI** (Oceanic Niño Index), **trimestral**: media móvil de tres meses de la
  anomalía de temperatura superficial del mar en la región Niño 3.4
  (5°N–5°S, 170°O–120°O), con base climatológica 1991–2020. Se actualiza una vez
  al mes. La NOAA considera condiciones de El Niño cuando el ONI alcanza o supera
  +0,5 °C durante cinco trimestres móviles consecutivos.
- **TSM semanal Niño 3.4**, **semanal**: anomalía de la semana más reciente del
  archivo semanal de la NOAA/CPC, que se actualiza los lunes. Es más fresca que el
  ONI, pero no es el ONI: una semana no equivale a un trimestre móvil, y un valor
  semanal alto puede no sostenerse en el ONI.

**Advertencia para el caso peruano.** Ambos miden el Pacífico central. El
fenómeno que afecta directamente a la costa peruana se monitorea con el
**ICEN** del ENFEN, construido sobre la región Niño 1+2, frente a la costa
norte. Ambos pueden divergir: el Niño costero de 2017 fue intenso en el Niño
1+2 con un Pacífico central casi neutro. Incorporar el ICEN es la tarea 1 del
proyecto; mientras tanto, el estado mostrado debe leerse como contexto global,
no como declaración sobre el Niño costero.

**Formato del archivo semanal.** Se verificó contra una muestra real del archivo
de la NOAA: columnas Niño 1+2, 3, 3.4 y 4, cada una con SST y anomalía; cada fila
lleva la fecha de la semana **centrada** en ese día. El parser toma la última fila
y rechaza el archivo si los valores no son plausibles (SST de Niño 3.4 entre 20 y
33 °C, anomalía entre −6 y +6 °C). En ese caso la TSM semanal queda sin publicar y
la interfaz lo dice.

## Frescura de los datos: esto no es tiempo real

El monitor se actualiza cada 6 horas, pero cada fuente tiene su propio rezago.
La interfaz muestra, junto a la hora de la última actualización, la fecha del
dato más reciente de cada fuente, porque no son lo mismo.

| Dato | Fuente | Rezago típico |
|---|---|---|
| Condiciones actuales (temperatura, lluvia de hoy) | API de pronóstico de Open-Meteo (`current`, `hourly`) | Horas; la API las refresca cada hora |
| Lluvia de los últimos 30 días | API de pronóstico de Open-Meteo (`past_days`) | Hasta el día anterior |
| Pronóstico a 7 días | API de pronóstico de Open-Meteo | Hoy en adelante |
| TSM semanal Niño 3.4 | NOAA/CPC, archivo semanal | Semana centrada en la fecha que indica; sale los lunes |
| ONI | NOAA/CPC | Trimestre móvil; se actualiza una vez al mes |
| Normal 1991–2020 | ERA5 vía Open-Meteo (archivo) | Climatología fija; no cambia |

Lo único cuasi-instantáneo son las condiciones actuales y el pronóstico. La
normal y el ONI no reflejan lo de hoy. Por eso la interfaz no debe sugerir más
inmediatez de la que hay: el texto de la página lo aclara.

## Anomalías departamentales

Para cada departamento se toma el punto de su capital y se consulta, en una sola
petición a la API de pronóstico de Open-Meteo:

- lluvia acumulada y temperatura máxima media de los últimos 30 días;
- lluvia acumulada de hoy hasta la hora actual, y temperatura actual;
- pronóstico de lluvia acumulada a 7 días.

Se comparan con la normal **1991–2020** —periodo estándar de la OMM— del mes en
curso, calculada con el reanálisis ERA5. La anomalía de lluvia se expresa en
porcentaje respecto de la normal (salvo en el caso de normal baja, abajo), y la
térmica en grados de diferencia.

**Fuentes distintas para normal y observación.** La normal sale del archivo ERA5,
pero la ventana de 30 días sale de la API de pronóstico (`past_days`), no del
archivo. Si esa API no devuelve ERA5 para los días pasados, la anomalía compara
dos productos distintos y su sesgo no se cancela. Pendiente: confirmar en la
documentación de Open-Meteo qué modelo sirve `past_days`, y decidir si se alinea
la ventana reciente con el archivo ERA5 (con un rezago de unos días) o se
documenta la diferencia.

La normal mensual de lluvia es la **media de los acumulados mensuales** de los
30 años del periodo, no la media diaria multiplicada por el largo del mes. Un
mes-año entra en esa media solo si la serie diaria cubre al menos el 90 % de
sus días, y su acumulado se escala al largo completo del mes; los meses con
menos cobertura se descartan. Cada normal registra en
`data/normales.json` cuántos años quedaron detrás de ella
(`anios_usados_precipitacion`), de modo que una normal construida con menos de
los 30 años del periodo quede visible y no se confunda con una completa. Las
normales térmicas son la media de las máximas y de las mínimas diarias del
mes a lo largo del periodo.

La normal mensual se escala proporcionalmente a la ventana de 30 días. Es una
aproximación: cuando la ventana cruza dos meses con regímenes de lluvia muy
distintos (típicamente el inicio y el fin de la temporada húmeda en la sierra),
introduce sesgo. Una versión posterior debería ponderar por días efectivos en
cada mes.

## Validación interna

Solo se usan controles internos, sin fuentes externas:

- `scripts/verificar_normales.py` controla el producto antes de usarlo: que estén
  los 25 departamentos con sus 12 meses, que los valores caigan en rangos
  físicamente posibles, y tres contrastes de plausibilidad climática —que la
  selva norte sea mucho más lluviosa que el desierto de Ica, que Ica resulte
  prácticamente seca, y que en la sierra el máximo de lluvia caiga entre
  diciembre y marzo—. Es un control de errores gruesos de descarga, no una
  validación contra observaciones.
- Altitud del modelo frente a la altitud de la capital (abajo).

**Por qué no se contrasta con SENAMHI.** El visor de normales por estación de
SENAMHI no estaba disponible al revisarlo: la página devolvía error y el portal
migró a gob.pe. Además, el dataset de normales climatológicas estándar tiene
licencia CC BY-NC-ND, que no permite redistribuirlo en este repositorio. Por eso
la validación se limita a los controles internos, y una comparación con
estaciones queda como pendiente aparte, para hacerla fuera del repositorio.

## Sesgo de representación puntual: cuantificación

Un punto por departamento ignora el relieve. Para cuantificarlo, el monitor
registra en cada corrida:

- `elevacion_modelo_m`: la altitud que reporta la propia API de Open-Meteo para
  el punto de malla que usa (campo `elevation` de la respuesta);
- `altitud_capital_m`: la altitud de referencia de la capital (`config.py`);
- `diferencia_altitud_m`: la diferencia entre ambas.

Las tres quedan en `data/estado.json` para cada departamento. Una diferencia
grande indica que el punto de malla promedia un relieve distinto del que hay en
la capital: por ejemplo, en un valle que el modelo ubica en una ladera más alta
y más lluviosa. Es un indicador del tamaño del problema de representación, no
una medida del sesgo de precipitación: el sesgo de lluvia no se mide aquí.

Las altitudes de referencia de las capitales son **aproximadas**, tomadas de
referencia cartográfica, y deben verificarse contra IGN antes de citar cifras.
Los valores de diferencia por departamento se completan con la primera corrida
del flujo automático; no se citan aquí cifras que no se hayan calculado.

## Normal mensual muy baja (limitación 4, implementada)

La anomalía porcentual pierde sentido cuando la normal es casi nula. En el
desierto costero la normal mensual de lluvia es de décimas de milímetro: con
una normal de 0,4 mm en la ventana de 30 días, 5 mm de garúa darían una
anomalía de +1200 %, que el mapa pintaría como extrema aunque el acumulado sea
trivial.

Por eso, cuando la **normal mensual** está por debajo de
`UMBRAL_NORMAL_BAJA_MM` (5 mm, en `scripts/config.py`):

- no se calcula la anomalía porcentual (`anomalia_precipitacion_pct` queda nula);
- se publica la anomalía en milímetros (`anomalia_precipitacion_mm`);
- el mapa colorea esa zona por lluvia acumulada en mm, con una escala propia, y
  la leyenda lo dice;
- la lluvia no suma al nivel de alerta; solo cuenta la anomalía térmica.

El umbral es **provisional**: fijado por criterio, no calibrado. Hay que
revisarlo con datos de estaciones.

## Nivel de alerta

Escala cualitativa de 0 a 3, diferenciada por zona porque el riesgo asociado a
la fase cálida no es el mismo en todo el país: en la **costa norte** el peligro
dominante es el exceso de lluvia e inundación, mientras que en la **sierra sur
y la costa centro-sur** lo es el déficit hídrico. Un exceso térmico superior a
2 °C sobre la normal eleva el nivel en un grado.

**Estos umbrales son provisionales.** Se fijaron por criterio y no están
calibrados contra registros de daños. La tarea 5 del proyecto es validarlos
con las emergencias registradas por INDECI. Hasta entonces el mapa es una
herramienta de exploración, no un instrumento de alerta operativa.

## Limitaciones principales

1. **Representación puntual.** Un punto por departamento ignora gradientes
   altitudinales fuertes. Arequipa capital no representa el altiplano de
   Caylloma, ni Huaraz la costa de Áncash. Se cuantifica con la diferencia de
   altitud (arriba), pero no se corrige.
2. **Correlación, no causalidad.** El mapa muestra anomalías simultáneas al
   evento ENSO; no establece que el evento las haya causado. Atribuir requiere
   un diseño estadístico explícito sobre series largas.
3. **Rezagos.** El impacto de El Niño sobre la lluvia en el Perú no es
   instantáneo y varía por región; comparar el estado del océano con el clima
   del mismo mes subestima relaciones rezagadas.
4. **Normal muy baja.** Tratada en su sección: el porcentaje se reemplaza por el
   acumulado en mm cuando la normal mensual es menor a 5 mm.
5. **Fuentes distintas para normal y observación.** Ver la sección de anomalías:
   la normal sale de ERA5 y la ventana reciente de la API de pronóstico.
6. **Frescura.** La interfaz no es tiempo real (ver la sección de frescura).

## Fuentes

- NOAA Climate Prediction Center, Oceanic Niño Index (trimestral).
- NOAA Climate Prediction Center, TSM semanal de la región Niño 3.4 (archivo
  semanal, base 1991–2020).
- ERA5 (ECMWF), servido a través de la API de archivo de Open-Meteo.
- Open-Meteo, API de pronóstico: observación de los últimos 30 días, condiciones
  actuales y pronóstico a 7 días.
- Límites departamentales: datos públicos de contornos del Perú.
- Altitudes de referencia de las capitales: aproximadas, de referencia
  cartográfica; pendiente de verificar contra IGN.
