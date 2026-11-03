# Protocolo de tesis (pregrado, Economía — UNSAAC)

**Estado: borrador de trabajo.** Las decisiones metodológicas de este documento
están tomadas, pero dos cosas siguen sin verificar y están marcadas como tales:
la disponibilidad exacta de la serie de IPC de alimentos por ciudad (§4.1) y la
climatología base del ICEN (§4.3). Ninguna cifra de este documento es un
resultado; no hay estimaciones todavía.

**Leer antes:** [BRECHAS.md](BRECHAS.md) tiene el inventario verificado de los
datos que el repositorio tiene (y los que no), el mapeo de cada brecha de la
literatura contra esos datos, y el orden de trabajo que de ahí se desprende.
Dos diseños alternativos quedaron descartados **con cita**, no por intuición.
[MARCO_TEORICO.md](MARCO_TEORICO.md) tiene los cinco pilares teóricos y las
diez predicciones contrastables que de ellos salen; **reformuló H1 y agregó
H4b, H5 y H6**, que están abajo marcadas.
[OPERACIONALIZACION.md](OPERACIONALIZACION.md) tiene la matriz de dimensiones e
indicadores de las dos variables, con dimensiones de categoría **económica** y
no física, y su correspondencia con cada hipótesis.

---

## 1. Título propuesto

> **El Niño y el precio de los alimentos en el Perú: efectos regionales
> diferenciados sobre el IPC de 26 ciudades, 2010–2026**

Variantes según cómo quede el alcance final:

- Si se conserva la comparación ONI/ICEN como eje: *"Niño del Pacífico central
  o Niño costero? Dos índices y sus efectos sobre los precios de alimentos en
  las ciudades del Perú"*.
- Si el jurado pide un alcance más acotado: restringir a macrorregión sur.

## 2. Planteamiento del problema

El Niño–Oscilación del Sur (ENSO) actúa sobre la economía peruana como un shock
de oferta: afecta la producción agropecuaria y pesquera, la infraestructura de
transporte y, por esas dos vías, los precios de los alimentos. La literatura
disponible sobre el Perú (§3) ha estimado ese efecto **a nivel nacional y con
agregados mensuales**, tratando al país como una sola unidad.

Esa agregación esconde el hecho central del caso peruano: el mismo evento
oceánico se traduce en shocks climáticos de **signo opuesto** según la región.
En la costa norte la fase cálida trae exceso de lluvia e inundación; en la
sierra sur y la costa centro-sur, déficit hídrico. Un promedio nacional
promedia dos fenómenos distintos y puede subestimar ambos.

El problema de investigación es entonces: **el efecto de El Niño sobre los
precios de alimentos en el Perú no es un número, es una distribución
geográfica**, y esa distribución no ha sido estimada.

## 3. Brecha respecto de la literatura existente

| Trabajo | Qué hace | Qué deja abierto |
|---|---|---|
| BCRP, DT 008-2025, *ENSO and its Economic Impact in the Peruvian Economy* | Datos mensuales BCRPData 1994M1–2019M12; PBI total, primario y no primario | Agregado nacional; no desagrega por región ni se centra en precios |
| BIS WP 1276 (mismos autores/tema) | Modelo semi-estructural; ENSO como shock de oferta, respuesta del sector primario más inmediata y persistente | Agregado nacional |
| FMI WP 2025/144 | DSGE con cambio de régimen; caídas de PBI real de ~5 % en el año posterior al inicio del evento | Macro agregada, no precios regionales |
| IGP (Niño costero 2017) | VAR; pérdida de PBI menor que en eventos severos previos | Un solo evento, agregado |
| Dell, Jones & Olken (2012, 2014) | Marco canónico de paneles clima-economía con efectos fijos | No es sobre el Perú ni sobre precios de alimentos |

**Aporte de esta tesis (tres, concretos):**

1. **Desagregación regional.** Panel ciudad-mes (26 ciudades) en vez de agregado
   nacional, con anomalías climáticas locales construidas desde ERA5 con
   normales 1991–2020 propias.
2. **Separación explícita ONI/ICEN, a nivel subnacional.** La literatura de
   "diversidad de ENSO" (Gallegati et al. 2026; Solomou et al. 2025) ya
   establece que el Pacífico central y el oriental tienen efectos distintos
   sobre la inflación, pero lo estima **entre países y a nivel nacional**, con
   modelos globales. La literatura peruana, en cambio, trata "El Niño" como un
   solo fenómeno. Esta tesis estima la distinción **dentro del país, entre
   regiones**, en el país donde esa distinción se institucionalizó: la región
   Niño 1+2 está frente a la costa peruana y el ENFEN mantiene el ICEN
   precisamente porque los dos índices divergen. 2017 es el experimento
   natural: Niño costero intenso con Pacífico central casi neutro.
3. **Reproducibilidad.** Pipeline en Python, datos y código versionados, sin API
   keys, derivado de la infraestructura ya construida en este repositorio.

## 4. Datos

### 4.1 Variable dependiente: IPC de alimentos por ciudad

- **Fuente:** INEI, Índice de Precios al Consumidor. El INEI calcula el IPC
  para el área urbana de **26 ciudades** (24 capitales de departamento y 2 no
  capitales de alta dinámica económica), base **diciembre 2021 = 100** desde
  enero de 2022, en reemplazo de la base 2009. El cambio de base obliga a
  trabajar con la serie empalmada y a documentar el empalme (la metodología del
  INEI describe reconstrucción hacia atrás y empalme hacia adelante).
- **Desagregación buscada:** división 01 de la CCIF ("Alimentos y bebidas no
  alcohólicas") por ciudad y mes.
- **⚠️ PENDIENTE DE VERIFICAR (tarea de la semana 1).** No está confirmado que
  esa desagregación (ciudad × división de gasto × mes) exista en formato
  descargable. Lo que sí está confirmado es que el boletín mensual
  *Indicadores de Precios de la Economía* publica el comportamiento del IPC en
  las ciudades con variaciones mensual, acumulada y anual. Orden de intentos:
  1. API del BCRP (`estadisticas.bcrp.gob.pe`), que republica series del INEI
     — ver `scripts/tesis/fetch_ipc.py --descubrir`;
  2. series estadísticas del portal del INEI;
  3. **plan B explícito:** si la desagregación por ciudad solo existe para el
     índice general, usar IPC general por ciudad como dependiente principal y
     IPC de alimentos nacional como contraste, y decirlo en la tesis. El diseño
     sobrevive: el canal alimentario sigue siendo identificable por la
     heterogeneidad regional, solo pierde precisión.
  4. Último recurso: extracción de los boletines mensuales en PDF. Costoso y
     propenso a error; solo si 1–3 fallan.

### 4.2 Variable climática local

Anomalías mensuales de precipitación y temperatura para el punto de cada una de
las 26 ciudades, respecto de la normal **1991–2020** (periodo estándar OMM),
calculadas con ERA5 vía la API de archivo de Open-Meteo.

Esto **reutiliza `scripts/calcular_normales.py`**, con dos cambios respecto del
monitor:

- la ventana es el **mes calendario**, no los últimos 30 días (el IPC es
  mensual, así que la unidad temporal debe coincidir);
- tanto la normal como la observación salen del **archivo ERA5**, no de la API
  de pronóstico. Esto elimina de raíz la limitación 5 de `docs/METODOLOGIA.md`
  (fuentes distintas para normal y observación): para la tesis no hay razón para
  usar `past_days`, porque no se necesita frescura, se necesita consistencia.
  **Es una mejora, no un atajo.**

Las 26 ciudades del IPC no son las 25 capitales del monitor: hay que construir
el mapeo ciudad-IPC → coordenada, reutilizando `scripts/provincias.py` para las
dos ciudades no capitales.

### 4.3 Índices de estado del océano

- **ONI**, trimestral, región Niño 3.4, base 1991–2020, NOAA/CPC. Ya
  implementado en `scripts/fetch_oni.py`.
- **ICEN**, mensual, región Niño 1+2, criterio ENFEN. **No se encontró una URL
  con la serie histórica descargable.** Sí está documentado cómo se construye:
  media móvil de tres meses de la anomalía mensual de TSM en la región Niño 1+2
  del producto ERSST de la NOAA/CPC, con los meses recientes publicados como
  versión preliminar (ICENtmp), y el criterio del ENFEN de al menos 3 meses
  consecutivos para declarar condiciones cálidas o frías.
- **Decisión:** calcular una **réplica del ICEN** desde los índices Niño 1+2 de
  la NOAA/CPC y **validarla** contra los valores que el IGP/ENFEN publica en sus
  informes técnicos. ⚠️ Pendiente de verificar: la **climatología base** que usa
  el ENFEN no es necesariamente 1991–2020, y la versión de ERSST tampoco es
  necesariamente la vigente en el archivo actual de la NOAA. Mientras eso no se
  confirme contra la nota técnica del IGP, la serie se llama **"ICEN-réplica"**
  en todo el documento y nunca "ICEN". Si la validación falla, la tesis reporta
  la discrepancia y usa la anomalía de TSM de Niño 1+2 sin el nombre ICEN.

**Regla de nomenclatura de todo el proyecto:** ONI ≠ ICEN. El Niño costero
peruano no coincide necesariamente con el Niño del Pacífico central.

### 4.4 Controles

- Precio internacional de alimentos (índice FAO o BCRPData) — shock común,
  absorbido por efectos fijos de tiempo pero necesario en las especificaciones
  sin ellos.
- Tipo de cambio nominal y precio del petróleo (canal de costos de transporte).
- Estacionalidad: dummies de mes calendario.

### 4.5 Muestra

26 ciudades × ~200 meses (2010M1–2026M9) ≈ **5 200 observaciones**. Si la serie
empalmada permite llegar a 2001, el panel sube a ~7 800. Ese tamaño es el que
justifica elegir este diseño sobre el panel departamental anual (25 × 18 = 450).

## 5. Pregunta de investigación, objetivos e hipótesis

**Pregunta central.** ¿Cuál es el efecto de los eventos El Niño sobre los
precios de alimentos en las ciudades del Perú, y en qué medida ese efecto
difiere entre regiones según el régimen de impacto climático?

**Objetivo general.** Estimar el efecto dinámico y regionalmente diferenciado de
los shocks ENSO sobre la inflación de alimentos a nivel de ciudad, 2010–2026.

**Objetivos específicos.**

1. Construir un panel ciudad-mes de inflación de alimentos y anomalías
   climáticas locales con normales 1991–2020 verificables.
2. Estimar la función impulso-respuesta de la inflación de alimentos a un shock
   ENSO, distinguiendo ONI de ICEN-réplica.
3. Contrastar la heterogeneidad del efecto entre costa norte, costa centro-sur,
   sierra y selva.
4. Evaluar si el efecto es asimétrico entre fase cálida (El Niño) y fase fría
   (La Niña).

**Hipótesis.** Cada una deriva de un pilar de
[MARCO_TEORICO.md](MARCO_TEORICO.md); la tabla de §8 de ese documento dice qué
las falsaría.

- **H1 (reformulada).** El efecto tiene **dos componentes separables**: uno de
  **anticipación**, ligado al índice oceánico y a los pronunciamientos del
  ENFEN, que opera *antes* de que el daño físico se materialice; y uno de
  **realización**, ligado a la anomalía climática local. El primero puede
  dominar. — *Motivo del cambio:* Letta et al. (2021, AJAE) muestran que en
  India las expectativas de los comerciantes anticipan **más del 80 %** del
  impacto total sobre precios, y la sequía los eleva **durante el crecimiento
  del cultivo**, antes de cualquier pérdida de cosecha. En el Perú el argumento
  es más fuerte, porque ENSO se pronostica y el ENFEN emite avisos fechados.
  **Consecuencia para la estimación: el índice oceánico y la anomalía local
  entran juntos, no como alternativas.**
- **H2.** El efecto es **heterogéneo en magnitud y posiblemente en signo** entre
  regiones. Mecanismo, ahora explícito: El Niño opera por **dos canales a la
  vez** — desplaza la oferta y **eleva los costos de transacción** al cortar
  vías, lo que ensancha la banda neutral y segmenta el mercado local. McNew
  (1996) documenta precisamente esto para el maíz del Misisipi durante la
  inundación de 1993: los mayores costos de transporte redujeron la integración
  y, por esa vía, la transferencia de shocks entre regiones.
- **H3.** El ICEN-réplica tiene **mayor poder explicativo que el ONI** para las
  ciudades de la costa norte, y el ONI no domina al ICEN en ninguna región
  costera. (Hipótesis que distingue la tesis; 2017 es el caso que la pone a
  prueba.)
- **H4.** El efecto es **asimétrico**: un déficit mueve el precio más que un
  excedente equivalente. — *Fundamento, antes ausente:* la teoría del
  almacenamiento competitivo. El inventario amortigua el excedente, pero la
  restricción de no negatividad no amortigua el déficit; Cafiero et al. (2014)
  muestran que sin existencias el precio debe subir abruptamente, y Wright
  (2009) que con existencias mínimas el precio se vuelve muy sensible a shocks
  pequeños.
- **H4b (nueva).** **Dependencia del estado:** el efecto es mayor cuando las
  existencias son bajas. Sin datos de inventarios, se aproxima por la posición
  en el calendario de cosecha y por la secuencia de meses previos
  desfavorables.
- **H5 (nueva).** **La integración entre ciudades cae durante el evento.** Es
  la contraparte observable del canal de costos de transacción, y se contrasta
  **solo con el panel de precios**, sin ningún dato adicional: la correlación
  entre pares de ciudades, o el ancho de la banda neutral de un modelo con
  umbral, debería aumentar durante los episodios.
- **H6 (nueva).** **El sesgo de agregación atenúa el coeficiente hacia cero.**
  Blanc y Schlenker (2017) advierten que los efectos fijos absorben señal
  climática y que el ruido en la variable climática sesga los coeficientes
  hacia abajo. Representar una unidad por un punto **es** ese ruido, así que la
  estimación con media provincial debería dar coeficientes **mayores en valor
  absoluto** que la del punto de la capital. Convierte la limitación de
  representación puntual en resultado.

## 6. Estrategia empírica

### 6.1 El supuesto de identificación, dicho con claridad

ENSO es un fenómeno oceánico-atmosférico del Pacífico tropical. **No lo causa
la economía peruana.** Esa exogeneidad es lo que permite leer los coeficientes
como efectos causales del shock climático sobre los precios, y es el mismo
argumento de Dell, Jones & Olken.

Lo que la exogeneidad **no** resuelve: (i) el shock está correlacionado en el
tiempo (autocorrelación), (ii) es común a todas las ciudades en un mismo mes
(dependencia espacial), (iii) puede coincidir con otros shocks nacionales. De
(i) y (ii) se derivan los errores estándar (§6.5); de (iii), la especificación
con efectos fijos de tiempo (§6.3).

### 6.2 Especificación A — clima local, el diseño limpio

$$
\pi_{c,t} \;=\; \alpha_c \;+\; \delta_t \;+\; \sum_{k=0}^{K} \beta_k \, A_{c,t-k} \;+\; \varepsilon_{c,t}
$$

con $\pi_{c,t}$ la inflación mensual de alimentos de la ciudad $c$
(primera diferencia del logaritmo del índice), $A_{c,t-k}$ la anomalía climática
local rezagada $k$ meses, $\alpha_c$ efectos fijos de ciudad y $\delta_t$
efectos fijos de año-mes. $K = 12$.

**Qué identifica:** el efecto del clima local, comparando ciudades dentro del
mismo mes. Es la especificación más defendible.

**Advertencia que hay que tener presente desde el inicio:** con $\delta_t$,
**cualquier índice nacional (ONI, ICEN) queda absorbido**, porque no varía entre
ciudades en un mes dado. La especificación A no puede estimar el efecto de
ENSO directamente. Por eso existe la B.

### 6.3 Especificación B — exposición a ENSO, el diseño que responde la pregunta

$$
\pi_{c,t} \;=\; \alpha_c \;+\; \delta_t \;+\; \sum_{k=0}^{K} \theta_k \,\bigl(\text{ENSO}_{t-k} \times E_c\bigr) \;+\; \varepsilon_{c,t}
$$

donde $E_c$ es la **exposición** de la ciudad al fenómeno. El nivel de
$\text{ENSO}_{t-k}$ lo absorbe $\delta_t$, pero la **interacción** sí se
identifica: $\theta_k$ mide cuánto más responde una ciudad expuesta que una no
expuesta.

Dos medidas de exposición, y se reportan las dos:

- $E_c$ **categórica**: la zona de régimen de impacto (costa norte, costa
  centro-sur, sierra norte, sierra sur, selva), tal como está en
  `scripts/config.py`. Transparente, pero asignada por criterio.
- $E_c$ **continua y estimada**: la sensibilidad histórica de la lluvia de la
  ciudad al índice ENSO, obtenida en una regresión previa sobre la serie
  climática 1991–2020. Más defendible porque sale de los datos, y además
  **usa solo el periodo de normales, no el periodo de estimación**, lo que evita
  que la exposición se construya con la misma variación que luego se explota.

$\text{ENSO}_{t-k}$ se corre por separado con ONI y con ICEN-réplica, y la
comparación de ajuste entre ambos es la prueba de H3.

### 6.4 Especificación C — proyecciones locales, para la dinámica

Para la función impulso-respuesta sin imponer la forma del rezago, proyecciones
locales (Jordà): una regresión por horizonte $h = 0,\dots,24$,

$$
p_{c,t+h} - p_{c,t-1} \;=\; \alpha_c^{h} \;+\; \delta_t^{h} \;+\; \theta^{h}\bigl(\text{ENSO}_t \times E_c\bigr) \;+\; \Gamma^h X_{c,t} \;+\; \varepsilon_{c,t}^{h}
$$

sobre el **nivel acumulado** del log del índice, que es la magnitud de interés
(cuánto más caro está el alimento $h$ meses después, no la tasa de ese mes). La
secuencia $\{\theta^h\}$ es la respuesta acumulada y es el gráfico central de la
tesis.

### 6.5 Inferencia

- **Errores estándar agrupados por ciudad** como base, y
- **Driscoll–Kraay** (robustos a dependencia espacial y autocorrelación) como
  especificación principal reportada, porque con un shock común a todas las
  ciudades el agrupamiento por ciudad solo no basta.
- Con 26 grupos, el agrupamiento está en el límite inferior de lo aceptable:
  reportar además **bootstrap wild cluster**.
- **Un estimador robusto a dependencia transversal** (efectos comunes
  correlacionados, o efectos fijos interactivos) como contraste. Razón: nuestro
  panel tiene N = 26 y T ≈ 200, es decir **T grande y N chico**. Thombs (2022)
  muestra que en ese régimen los efectos fijos con errores robustos son
  sesgados ante heterogeneidad de pendientes y dependencia transversal, y que
  el desempeño **empeora a medida que T crece**. Gospodinov et al. (2025)
  encuentran que agrupar en una sola dimensión produce distorsiones de tamaño y
  que **una especificación aditiva de efectos fijos no controla
  adecuadamente los efectos de tiempo comunes**.

Esto no es decoración: con un regresor común en el tiempo, errores estándar mal
especificados son el modo típico de fallo de este diseño.

**Advertencia sobre los efectos fijos en dos vías.** Kropko y Kubinec (2020)
muestran que el modelo de dos vías mezcla variación intra-unidad y transversal
de un modo que vuelve los coeficientes difíciles de interpretar, y que bajo la
lectura habitual la especificación está mal identificada. Por eso cada tabla
reporta también la versión de **una sola vía** y declara explícitamente qué
variación identifica cada coeficiente.

### 6.6 Robustez y falsación

1. **Placebo de rezagos adelantados.** Incluir $\text{ENSO}_{t+1}, \text{ENSO}_{t+6}$.
   Si el futuro del océano "explica" los precios de hoy, hay un problema de
   especificación. **Es la prueba más importante del conjunto.**
2. **Exclusión de eventos.** Re-estimar sin 2017 y sin 2023 (Niños costeros) para
   ver si el resultado depende de un episodio.
3. **Empalme de base.** Re-estimar solo con base 2009 y solo con base dic-2021.
4. **Umbral vs continuo.** El índice en forma continua y en forma de categorías
   del ENFEN/NOAA.
5. **Definición de la dependiente.** Variación mensual vs variación a 12 meses.
6. **Exposición.** Categórica vs estimada (§6.3).
7. **No usar los umbrales de alerta del monitor.** Son provisionales, fijados por
   criterio y no calibrados. No entran en la estimación.
8. **No linealidad y umbrales en la transmisión.** McNew (1996) muestra que los
   precios espaciales se relacionan de forma no lineal y Goodwin y Piggott
   (2001) que los modelos con banda neutral dan ajustes mucho más rápidos que
   los lineales. Así que el modelo lineal es el caso restringido a contrastar,
   no el punto de partida a defender.
9. **Prueba de agregación (H6).** El mismo modelo con el punto de la capital y
   con la media provincial. La teoría predice el signo de la diferencia.

## 7. Limitaciones que la tesis declara por adelantado

1. **Representación puntual.** Un punto de malla por ciudad. El IPC es urbano,
   así que el desajuste es menor que en el monitor (que pretende representar
   departamentos enteros), pero los alimentos no se producen en la ciudad donde
   se venden: el shock relevante para el precio es el de la **zona productora**,
   no el de la ciudad. Es la limitación más seria del diseño. Mitigación
   parcial: una variante donde la anomalía se promedia sobre las provincias del
   departamento, aprovechando el nivel provincial del repositorio.
2. **El canal no se descompone.** La tesis estima el efecto reducido total, sin
   separar pérdida de cosecha, transporte interrumpido y expectativas.
3. **26 grupos.** Pocos para inferencia asintótica basada en el número de
   grupos; de ahí el bootstrap.
4. **Normales ERA5 sin validar contra estaciones.** El visor de normales de
   SENAMHI no estaba disponible y su dataset tiene licencia CC BY-NC-ND, que no
   permite redistribuirlo. La validación contra estaciones queda fuera del
   repositorio y es una limitación declarada, no un supuesto escondido.
5. **ICEN-réplica.** Ver §4.3.

## 8. Estructura de capítulos

1. Introducción: problema, pregunta, aporte.
2. Marco teórico (ver [MARCO_TEORICO.md](MARCO_TEORICO.md)): la cadena océano →
   clima local → oferta → precio regional → IPC urbano, con un pilar por
   eslabón — el clima como variación identificadora, almacenamiento competitivo
   (de dónde sale la no linealidad y la asimetría), expectativas de los
   comerciantes, equilibrio espacial de precios con costos de transacción, y
   traspaso al IPC con efectos de segunda vuelta.
3. Antecedentes: la literatura de §3 y la brecha.
4. El fenómeno en el Perú: ONI, ICEN y por qué no son lo mismo. Caracterización
   de 1982-83, 1997-98, 2015-16 y los costeros 2017 y 2023.
5. Datos y construcción del panel: fuentes, normales 1991–2020, empalme del IPC,
   estadística descriptiva.
6. Estrategia empírica: §6, con el supuesto de identificación explícito.
7. Resultados: línea de base, impulso-respuesta, heterogeneidad regional,
   ONI vs ICEN, asimetría.
8. Robustez.
9. Conclusiones e implicancias de política (prudentes: el trabajo no sustenta
   un sistema de alerta).
10. Limitaciones y agenda.

Anexos: tablas completas, código, diccionario de variables.

## 9. Cronograma (12 semanas, pregrado)

| Semana | Tarea | Entregable |
|---|---|---|
| 0 | **Persistir los agregados mes-año en `calcular_normales.py`** y re-indexar tmax/tmin a `(anio, mes)`. Ver BRECHAS.md §1: el panel se calcula y se descarta, y recuperarlo no cuesta ninguna petición extra | Panel climático mensual |
| 1 | Verificar disponibilidad del IPC por ciudad y grupo (§4.1). Decidir plan A o B | Nota de decisión de datos |
| 2 | Mapeo de las 26 ciudades a coordenadas; descarga de normales mensuales ERA5. Arreglar el parser de TSM semanal (hoy devuelve error) y extender el ONI a 1950 | `data/tesis/normales_ciudades.json` |
| 3 | Descarga del IPC y construcción del panel | `data/tesis/panel.csv` |
| 4 | ICEN-réplica y su validación contra informes del IGP | `data/tesis/icen.json` + nota de validación |
| 5 | Descriptiva, gráficos, control de calidad del panel | Capítulo 5 |
| 6–7 | Especificaciones A y B | Resultados preliminares |
| 8 | Proyecciones locales | Gráfico de impulso-respuesta |
| 9 | Heterogeneidad, asimetría, ONI vs ICEN | Capítulo 7 |
| 10 | Robustez completa, con el placebo primero | Capítulo 8 |
| 11 | Redacción de capítulos 1–4 | Borrador completo |
| 12 | Revisión, anexos, reproducibilidad de punta a punta | Documento final |

El orden no es negociable en un punto: **la semana 1 decide si el diseño es
viable**. Si el IPC de alimentos por ciudad no existe en formato utilizable y el
plan B tampoco convence, se cambia de diseño antes de invertir diez semanas.

## 10. Reproducibilidad

- Python, código en `scripts/tesis/`, datos derivados en `data/tesis/`.
- El código de la tesis **sí usa dependencias externas** (pandas, statsmodels,
  linearmodels): la estimación de paneles con efectos fijos y errores Driscoll–Kraay
  no se escribe a mano de forma responsable. Es la "razón fuerte" que
  `CLAUDE.md` exige, y van con versión fijada en `requirements-tesis.txt`,
  separado de `requirements.txt` para que el monitor siga sin dependencias.
- Sin API keys: todas las fuentes son abiertas.
- **Dónde se corre:** el pipeline descarga de `estadisticas.bcrp.gob.pe`,
  `www.cpc.ncep.noaa.gov` y `archive-api.open-meteo.com`. Se corre en la máquina
  local o en GitHub Actions, igual que el monitor.

## 11. Fuentes

- INEI. *Índice de Precios al Consumidor*, 26 ciudades; base diciembre 2021 = 100
  desde enero 2022 (antes base 2009). Boletín *Indicadores de Precios de la
  Economía*; metodología del IPC de Lima Metropolitana base dic-2021.
- BCRP. *Documento de Trabajo 008-2025: ENSO and its Economic Impact in the
  Peruvian Economy*. Datos BCRPData 1994M1–2019M12.
- BIS. *Working Paper 1276: Economic activity, inflation, and monetary policy
  after extreme weather events — ENSO and its economic impact on the Peruvian
  economy*.
- FMI. *Working Paper 2025/144: Building Macroeconomic Resilience to Natural
  Disasters and Persistent Shocks*.
- IGP. Reflexiones sobre el impacto y la respuesta al Niño costero 2017 (VAR).
- Dell, M., Jones, B. y Olken, B. (2012). *Temperature Shocks and Economic
  Growth: Evidence from the Last Half Century*. AEJ: Macroeconomics.
  Replicación: openICPSR, proyecto 114251 (DOI 10.3886/E114251V1).
- Dell, M., Jones, B. y Olken, B. (2014). *What Do We Learn from the Weather?
  The New Climate-Economy Literature*. Journal of Economic Literature 52(3).
- Jordà, Ò. (2005). *Estimation and Inference of Impulse Responses by Local
  Projections*. American Economic Review 95(1).
- Driscoll, J. y Kraay, A. (1998). *Consistent Covariance Matrix Estimation with
  Spatially Dependent Panel Data*. Review of Economics and Statistics 80(4).
- NOAA/CPC. Índices ONI y de TSM de las regiones Niño; producto ERSST.
- ENFEN / IGP. Definición y criterio del ICEN (región Niño 1+2, 3 meses
  consecutivos).
- ERA5 y ERA5-Land (ECMWF), vía la API de archivo de Open-Meteo.
