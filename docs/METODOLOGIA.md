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

- **ICEN** (Índice Costero El Niño) del ENFEN, **mensual**: media móvil de tres
  meses de la anomalía mensual de TSM en la región **Niño 1+2** (ERSSTv5, base
  1991–2020), publicada por el IGP. Es el índice oficial del **Niño costero**, el
  que afecta directamente a la costa peruana. Categorías ENFEN: cálida débil
  (≥ 0,4), moderada (≥ 1,0), fuerte (≥ 1,7), extraordinaria (≥ 3,0); fría débil
  (≤ −1,0), moderada (≤ −1,2), fuerte (≤ −1,4); neutro entre medio. Los valores
  de los últimos meses son **preliminares** (ICENtmp) hasta que el ENFEN los
  confirma. El archivo del IGP se interpreta de forma tolerante (filas con año,
  mes y valor); si no está accesible, la tarjeta dice "no disponible" y nada más
  cambia.

**Advertencia para el caso peruano.** El ONI y la TSM semanal miden el Pacífico
central; el ICEN mide la costa. Pueden divergir: el Niño costero de 2017 fue
intenso en el Niño 1+2 con un Pacífico central casi neutro. Con los tres
índices a la vista, el estado del Pacífico central debe leerse como contexto
global y el ICEN como la declaración sobre el Niño costero.

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
| ICEN | ENFEN/IGP | Mensual; los últimos meses son preliminares |
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

## Nivel provincial

Además de los 25 departamentos, el monitor calcula el mismo producto para las
provincias. Solo se publican las provincias **que tienen información**; las
demás aparecen en gris, con el motivo.

**Límites.** `docs/peru_provincias.geojson`, de
[juaneladio/peru-geojson](https://github.com/juaneladio/peru-geojson)
(licencia MPL-2.0). El archivo trae 197 polígonos: dos provincias (Piura y
Víctor Fajardo) vienen partidas en dos, con el fragmento menor mal escrito
("PUIRA", "VICTOR FAFARDO") y el mismo código ubigeo; se agrupan por ubigeo.
Quedan **195 provincias**: el archivo es anterior a la creación de Putumayo
(2014), que figura dentro de Maynas. Es un límite de la fuente, no del método.

**Punto por provincia.** No es la capital: es el centroide del polígono mayor
de cada provincia (si cae fuera, por una forma cóncava, el vértice más
cercano). Las coordenadas se calculan en `scripts/provincias.py` a partir del
GeoJSON; no hay una lista tipeada a mano.

**Modelo.** Para provincias las normales se piden a **ERA5-Land** (~9 km), no
a ERA5 (~25 km) como en departamentos: muchas provincias de costa y sierra son
más chicas que una celda de ERA5, y a esa resolución provincias vecinas
compartirían el mismo valor. ERA5-Land no cubre el mar, así que un punto
costero puede quedar sin serie: esa provincia queda registrada en `sin_datos`
con el motivo, y nunca se le inventa un valor. Por la diferencia de modelo,
**los valores provinciales y departamentales no son directamente comparables**
entre sí; cada nivel se compara con su propia normal.

**Zona de impacto.** Cada provincia hereda la zona de su departamento. Es una
asignación **provisional**: una provincia de sierra dentro de un departamento
costero heredaría "costa_norte". Para atenuarlo, si la altitud que reporta el
modelo para el punto supera los 2000 m y la zona heredada es costera, se
reclasifica como sierra (norte o sur según la latitud). El estado publica la
zona usada y la heredada, para que el cambio sea visible. La asignación fina
por provincia es trabajo pendiente.

**Verificación.** Los mismos controles internos, adaptados: las unidades en
`sin_datos` se aceptan como aviso mientras no pasen del 20 %; el contraste
Loreto frente a Ica se hace con el promedio de sus provincias; y la regla del
máximo de lluvia en diciembre–marzo debe cumplirla al menos el 90 % de las
provincias de sierra (el resto se lista como aviso, no como fallo).

## Sesgo de representación puntual: cuantificación

Un punto por departamento ignora el relieve. Para cuantificarlo, el monitor
registra en cada corrida:

- `elevacion_modelo_m`: la altitud que reporta la propia API de Open-Meteo para
  el punto de malla que usa (campo `elevation` de la respuesta);
- `altitud_capital_m`: la altitud de referencia de la capital (`config.py`);
- `diferencia_altitud_m`: modelo menos capital.

Las tres quedan en `data/estado.json` para cada departamento.

**Primera corrida (3 de noviembre de 2026), 10 capitales:**

| Capital | Diferencia de altitud (m) |
|---|---|
| Arequipa | −23 |
| Cajamarca | −47 |
| Callao | +17 |
| Cusco | −17 |
| Ica | 0 |
| La Libertad | +2 |
| Lambayeque | +4 |
| Lima | −6 |
| Moquegua | +2 |
| Tacna | +9 |

El resto de los departamentos queda en `data/estado.json` y se incorpora a esta
tabla cuando se revise la corrida completa.

**Lectura.** En estas capitales el punto de malla queda a menos de 50 m de la
altitud de la capital. La altitud, por sí sola, no explica el exceso de lluvia
de la normal ERA5 en varias capitales andinas (Cajamarca: 2619 mm/año en la
normal, un valor que la comparación con estaciones deberá confirmar o
descartar). El sesgo de precipitación, entonces, no viene solo de la altura
del punto: depende de cómo el modelo representa la lluvia en la exposición de
cada valle y en la pendiente, que la altitud no captura. Esta es una
conclusión del diagnóstico; no se corrige en el código. La diferencia en Ica
(0 m) es un resultado de redondeo y no se interpreta.

Las altitudes de referencia de las capitales son **aproximadas**, tomadas de
referencia cartográfica, y deben verificarse contra IGN antes de citar cifras.

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

La marca depende del **mes en curso**, porque usa la normal mensual. En
noviembre de 2026 quedan marcadas Callao, Ica, La Libertad, Lambayeque, Lima,
Moquegua y Tacna. Piura queda por encima del umbral en ese mes. El conjunto
cambia a lo largo del año.

## Sensibilidad al ENSO (inferencial)

`scripts/sensibilidad.py` cruza, para cada unidad y cada mes del calendario, la
anomalía de lluvia de cada año del periodo 1991–2020 (en % de la normal del
mes) con el ONI del trimestre centrado en ese mes, probando rezagos de 0 a 3
meses. Reporta la correlación de Pearson, la pendiente (% de lluvia por °C de
ONI), el número de años y un p aproximado por la transformación z de Fisher.
El rezago elegido es el de mayor |r| con p < 0,05; si ninguno lo alcanza, 0.
Con ese rezago calcula, entre los años con ONI ≥ +1,0, qué fracción tuvo
déficit (≤ −20 %) o exceso (≥ +50 %), frente a la fracción base de los 30 años.

La serie mensual que lo alimenta la guarda `calcular_normales.py` junto con las
normales (`data/series_mensuales*.json`), así que el análisis se rehace cada
vez que se recalculan las normales. El nivel provincial se analiza cuando su
corrida de normales incluya la serie.

**Qué no es.** Treinta años son treinta observaciones por mes y apenas cuatro o
cinco eventos El Niño: las estimaciones tienen mucha incertidumbre. Es
asociación, no causalidad. No se corrige por comparaciones múltiples (12 meses
× 4 rezagos por unidad), de modo que algunas correlaciones "significativas" lo
son por azar; el p es orientativo. La lluvia proviene de reanálisis en un
punto, no de estaciones. Los meses con normal muy baja no se analizan en
porcentaje. Es un insumo para plantear hipótesis, no una conclusión.

## Lectura automática

`scripts/lectura.py` escribe, en cada corrida, el texto que aparece bajo el
bloque ENSO ("Lectura automática") y lo guarda en `estado*.json` bajo
`lectura` (título, párrafos, nota, claves). Son reglas fijas sobre los índices
ya publicados: la misma entrada produce siempre el mismo texto, y los umbrales
están declarados al inicio del archivo. Es una **interpretación descriptiva**,
no un pronóstico, y no sustituye a los comunicados del ENFEN.

Qué dice cada párrafo y con qué regla:

1. **Pacífico central.** Valor y categoría del ONI (umbrales de la NOAA/CPC
   que usa el monitor), tendencia frente a tres trimestres atrás (±0,3 →
   ascenso/descenso; si no, estable), trimestres seguidos del mismo lado de
   ±0,5 frente al criterio de episodio de la NOAA (cinco), y anomalía semanal
   en Niño 3.4 frente al ONI: ±0,5 °C → "por encima / por debajo", ±1,0 °C →
   "muy por encima / muy por debajo"; dentro de ±0,5, "en línea".
2. **Costa peruana.** Valor y categoría ENFEN del ICEN, tendencia con la misma
   regla, meses de rezago del mes central respecto a la corrida, y anomalía
   semanal en Niño 1+2 frente al ICEN con los mismos cortes. Si el ICEN no
   estuvo accesible, usa la anomalía semanal y lo dice; si tampoco hay semanal,
   deja la costa como pendiente.
3. **Configuración.** Fase de cada cuenca (ONI ≥ +0,5 cálido, ≤ −0,5 frío;
   ICEN ≥ +0,4 cálido, ≤ −1,0 frío, siguiendo las categorías ENFEN) y su
   combinación en nueve casos (Niño con expresión costera, Niño costero sin
   Niño global como 2017, Niño central sin expresión costera, Niña, etc.).
   Con las cuatro regiones semanales, ubica el máximo: si está en Niño 1+2 o
   Niño 3 y la diferencia máximo–mínimo supera 1 °C, patrón de tipo oriental;
   si está en Niño 3.4 o Niño 4, patrón de tipo central; con menos de 1 °C de
   diferencia, "parejo"; con todas por debajo de 0,5 °C en valor absoluto,
   "cerca de lo normal".
4. **Momento del año.** Septiembre–diciembre: fase de desarrollo (el máximo
   del Pacífico central suele darse entre noviembre y enero; las lluvias de la
   costa norte, entre enero y abril). Enero–abril: periodo de impacto. Mayo–
   agosto: transición. Es climatología general del ENSO, no una predicción del
   evento en curso.
5. **Mapa.** Unidades en alerta moderada o alta, unidades con lluvia de 30
   días por encima de +50 % o por debajo de −30 % de su normal (las tres más
   extremas con su valor; las de normal muy baja no entran al porcentaje) y
   cuántas tienen la temperatura máxima por encima de su normal, con la
   mediana.
6. **Sensibilidad** (solo si existe `sensibilidad*.json`). Unidades cuya lluvia
   del mes en curso se asocia significativamente con el ONI (p < 0,05), con
   signo. Hereda todas las advertencias de la sección anterior.

Las analogías históricas (1982-83, 1997-98, 2017) son las configuraciones
clásicas, nombradas solo para orientar; no se afirma que el evento en curso
vaya a parecerse a ellas. El texto se regenera en cada corrida y queda en
`estado*.json` para quien consuma el JSON directamente.

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
- NOAA Climate Prediction Center, TSM semanal de las regiones Niño 1+2, 3, 3.4 y
  4 (archivo semanal, base 1991–2020).
- ENFEN/IGP, Índice Costero El Niño (ICEN), publicado como texto plano por el
  IGP.
- ERA5 (ECMWF), servido a través de la API de archivo de Open-Meteo.
- Open-Meteo, API de pronóstico: observación de los últimos 30 días, condiciones
  actuales y pronóstico a 7 días.
- Límites departamentales y provinciales: juaneladio/peru-geojson (MPL-2.0),
  derivados de los límites oficiales.
- ERA5-Land (ECMWF), vía la API de archivo de Open-Meteo, para las normales
  provinciales.
- Altitudes de referencia de las capitales: aproximadas, de referencia
  cartográfica; pendiente de verificar contra IGN.
