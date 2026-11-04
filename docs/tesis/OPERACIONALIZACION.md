# Operacionalización de variables

Matriz de dimensiones e indicadores para las dos variables del diseño. El
criterio que ordena todo el documento es el que el autor impuso, y es correcto:

> **Las dimensiones deben ser de ciencia económica, no de ciencia física.**

Esto no es una preferencia de estilo. Si las dimensiones de la variable
independiente son "precipitación", "temperatura" y "temperatura superficial del
mar", la tesis **deja de ser de economía y pasa a ser de climatología aplicada**,
y un jurado de economía tiene razón en objetarlo. La solución no es disfrazar los
nombres: es **definir la variable como un objeto económico** y relegar los datos
climáticos a la condición de *indicadores* de una de sus dimensiones.

La diferencia, en una línea:

| Formulación | Variable independiente | Problema |
|---|---|---|
| Incorrecta | "El fenómeno El Niño", con dimensiones precipitación, temperatura y TSM | Es climatología. No hay categoría económica en ninguna dimensión |
| **Correcta** | **Shock exógeno de oferta de origen ENSO**, con dimensiones de magnitud, signo, persistencia, anticipación y exposición económica | Cada dimensión es una categoría de teoría económica; el dato climático es solo el indicador de la primera |

---

## 1. Variable independiente (X)

### Definición conceptual

> **Shock exógeno de oferta de origen ENSO:** perturbación no anticipada por la
> economía peruana, originada en la variabilidad del Pacífico tropical, que
> desplaza la función de oferta agropecuaria y pesquera regional y eleva los
> costos de transacción del comercio interregional.

Tres decisiones contenidas en esa definición:

1. **"Shock de oferta"** y no "fenómeno climático": es la categoría económica.
   Es la lectura que hacen el BCRP (DT 008-2025) y el BIS (WP 1276) para el Perú,
   y Tol (2021) la formaliza situando el clima en la frontera de producción y los
   shocks meteorológicos como **fuente de ineficiencia**.
2. **"Exógeno"**: es el supuesto de identificación, no un adorno. El Pacífico
   tropical no responde a la economía peruana.
3. **"y eleva los costos de transacción"**: incorpora el segundo canal
   (McNew 1996). Sin esa cláusula, la definición pierde la mitad del mecanismo.

### Dimensiones

| # | Dimensión | Categoría económica que la sostiene | Indicador | Unidad | Fuente |
|---|---|---|---|---|---|
| **D1** | **Magnitud del shock** | Tamaño de la perturbación de oferta | Anomalía mensual estandarizada de precipitación y de temperatura respecto de la normal 1991–2020 | Desviaciones estándar (σ) | ERA5 / ERA5-Land vía Open-Meteo |
| **D2** | **Signo del shock** | Déficit frente a excedente de oferta; **asimetría** por restricción de inventarios | Exceso de lluvia / exceso de calor / déficit hídrico, en variables separadas | σ, con signo | ERA5 |
| **D3** | **Persistencia** | Agotamiento de existencias; duración del desplazamiento de la oferta | Meses consecutivos más allá del umbral; shock acumulado a 3, 6 y 12 meses | Número de meses; σ acumuladas | ERA5, ONI, ICEN-réplica |
| **D4** | **Anticipación (contenido informativo)** | Formación de expectativas; conjunto de información de los agentes | ONI e ICEN-réplica rezagados; **fecha de los pronunciamientos del ENFEN**; antelación respecto de la realización local | Índice en °C; días de antelación | NOAA/CPC; comunicados del ENFEN |
| **D5** | **Exposición económica** | Estructura productiva y de consumo; incidencia del shock | (a) Participación de agropecuario y pesca en el VAB departamental; (b) **participación del alimento en la canasta del IPC de la ciudad**; (c) conectividad con zonas productoras | Porcentaje; indicador de distancia o conectividad | INEI; estructura de ponderaciones del IPC |
| **D6** | **Posición en el calendario productivo** | Posición de inventarios; momento del ciclo de cosecha | Interacción del shock con la fase del calendario agrícola de la zona abastecedora | Categórica | Calendario de siembras y cosechas (MIDAGRI) |

**D5 es la dimensión decisiva para la objeción del jurado.** Es la que convierte
un shock físico en un shock económico: dos ciudades con idéntica anomalía
climática sufren shocks económicos distintos si difieren en la estructura de su
canasta y en su dependencia de la producción local. Furceri et al. (2016)
identifican la **participación del alimento en la canasta** como el mecanismo que
explica por qué el traspaso es mayor en economías emergentes; Balié, Magrini y
Morales Opazo (2016) muestran que las consecuencias dependen del peso del consumo
de alimentos en el gasto total, de la participación de los cereales en el
presupuesto alimentario, de la sustitución entre alimentos y del número relativo
de vendedores netos frente a compradores netos.

### Sustento de la medición (y las trampas que hay que evitar)

Auffhammer et al. (2013, *REEP*) es la referencia obligada: revisan las bases de
datos meteorológicas que usan los economistas, **los errores más comunes que
cometen** y cinco trampas específicas al usar datos meteorológicos históricos
como variables explicativas. Hay que leerlo antes de construir D1, no después.

Tres lecciones de medición que esta literatura impone:

1. **El promedio esconde el extremo.** Bellon y Massetti (2022, FMI) construyen
   164 variables meteorológicas con sus rezagos a partir de datos diarios de 30
   km y seleccionan un subconjunto parsimonioso con LASSO; encuentran que la
   fracción de la variación del PBI explicada por el clima es **mucho mayor** que
   la que implicaban los promedios anuales. Nuestro panel es mensual, lo que ya
   mitiga parte del problema, pero D1 **no debe reducirse al promedio mensual**.
2. **Más allá de la media.** Winter et al. (2026) estiman el efecto de las
   anomalías de temperatura considerando **toda la distribución** —media,
   volatilidad, asimetría y curtosis— y concluyen que los estudios centrados solo
   en la media **subestiman sustancialmente** el impacto. Kim et al. (2021, 2025)
   construyen índices de clima severo que **siguen cambios en la distribución** de
   temperaturas extremas, lluvia intensa, sequía y viento, y encuentran efectos
   persistentes hasta 20 meses que **elevan la inflación**.
3. **La ponderación importa.** Arango-Castillo et al. (2025) estiman el efecto de
   anomalías de temperatura y precipitación sobre la inflación mexicana con un
   panel regional, usando desviaciones **ponderadas por población** respecto de la
   norma calculada con media móvil de 30 años, y combinando panel ARDL con
   proyecciones locales. Encuentran que en el corto plazo no hay efecto
   estadístico y que en el largo plazo solo la precipitación importa. Es el
   antecedente metodológico más cercano a nuestra especificación, con un resultado
   que **conviene tener presente como posibilidad**: el efecto puede no aparecer.

### Advertencia: la tríada del IPCC no es ciencia económica

Muchas tesis peruanas operacionalizan un fenómeno climático con las dimensiones
**exposición, sensibilidad y capacidad adaptativa**. Ese esquema viene de la
ciencia de la vulnerabilidad, no de la economía, y usarlo tal cual es
precisamente el error que este documento evita. Pero tiene **traducción
económica**, y conviene conocerla para responder si el jurado la pide:

| Categoría del IPCC | Equivalente económico | Cómo se mide aquí |
|---|---|---|
| Exposición | Estructura productiva y de consumo | D5 |
| Sensibilidad | **Elasticidades** (de oferta, de demanda, de traspaso) | Coeficientes estimados, no variables |
| Capacidad adaptativa | Posibilidades de **sustitución, almacenamiento y acceso al mercado** | D6, integración espacial (Y-D5) |

Nótese el punto importante: **la sensibilidad no es una dimensión de la variable,
es un parámetro a estimar.** Meterla como dimensión es un error lógico, porque
convierte el resultado de la tesis en un insumo de la tesis. Ojeda-Joya et al.
(2026) usan el vocabulario de exposición y sensibilidad en un journal de
economía, pero lo operacionalizan con índices de ventaja comparativa revelada:
es decir, lo traducen a categorías económicas, exactamente como aquí.

---

## 2. Variable dependiente (Y)

### Definición conceptual

> **Precios de alimentos al consumidor en el ámbito urbano:** nivel y dinámica
> del precio de la canasta de alimentos que enfrenta el consumidor urbano de cada
> ciudad, medido por el índice de precios al consumidor del grupo de alimentos.

### Dimensiones

Aquí no hay que inventar nada: la economía agrícola **ya tiene una estructura
dimensional establecida** para los precios de alimentos, y es explícita.

von Braun y Tadesse (2012) la enuncian sin ambigüedad: el análisis de precios de
commodities debe **distinguir tres tipos de cambio de precio — tendencias,
volatilidad y picos —**, donde las tendencias importan en el largo plazo y la
volatilidad y los picos en el corto y mediano plazo; y observan que los tres
crecen con el tiempo y **están fuertemente correlacionados entre sí**.
Díaz-Bonilla (2016) desarrolla el punto conceptual y de medición: los efectos de
cambios en la tendencia del precio **son distintos** de los efectos de cambios en
la volatilidad alrededor de esa tendencia, y conviene diferenciar tendencias,
ciclos y eventos de corto plazo, incluidos picos y caídas.

A esas tres se suman dos que salen de los pilares IV y V del marco teórico:

| # | Dimensión | Categoría económica | Indicador | Unidad | Fuente |
|---|---|---|---|---|---|
| **D1** | **Nivel y tendencia** | Inflación de alimentos | Variación mensual y a 12 meses del logaritmo del IPC de alimentos de la ciudad | Porcentaje | INEI (26 ciudades) |
| **D2** | **Volatilidad** | Riesgo de precio alrededor de la tendencia | Desviación estándar móvil; varianza condicional (GARCH) | Porcentaje | INEI |
| **D3** | **Picos** | Eventos extremos; régimen de agotamiento de existencias | Frecuencia y magnitud de cambios que superan un umbral de cola | Número; porcentaje | INEI |
| **D4** | **Traspaso** | *Pass-through* y efectos de segunda vuelta | Elasticidad del IPC general y del subyacente respecto del IPC de alimentos | Coeficiente | INEI, BCRP |
| **D5** | **Integración espacial** | Costos de transacción; arbitraje entre mercados | Correlación entre pares de ciudades; ancho de la banda neutral en un modelo con umbral | Coeficiente; porcentaje | INEI |

**Por qué separar D1, D2 y D3 en lugar de medir solo inflación.** No es
sofisticación gratuita: la teoría del almacenamiento predice que un shock de
oferta modifica **la distribución completa** del precio y no solo su media
(Wright y Williams 1982). Medir únicamente D1 descarta por construcción las
predicciones P1 (convexidad) y P3 (dependencia del estado) del marco teórico. Y
como von Braun y Tadesse advierten que las tres están fuertemente
correlacionadas, hay que medirlas **por separado e interpretarlas en conjunto**,
no elegir una y suponer que representa a las demás.

**Una restricción honesta sobre D4.** El traspaso es una **relación**, no un
atributo del precio de alimentos. Ponerlo como dimensión es admisible porque el
objeto de interés es la dinámica del precio dentro del sistema de precios, pero
el indicador es un coeficiente estimado, no un dato observado. Conviene decirlo
en la tesis para que no parezca un descuido.

**Lo que estas dimensiones NO permiten afirmar.** Balié, Magrini y Morales Opazo
(2016) muestran que las consecuencias de bienestar de precios **más altos** y de
precios **más volátiles** son distintas —y encuentran que el efecto de los
precios más altos supera sustancialmente el de la mayor volatilidad en el
bienestar de los agricultores, en toda la distribución de ingresos de cuatro
países—, y que todo depende de la posición de comprador o vendedor neto. El IPC
**no observa esa posición**. Por lo tanto estas cinco dimensiones miden
**precios, no bienestar**, y la tesis no debe deslizarse de una cosa a la otra.
Ya está anotado en MARCO_TEORICO.md §9, y se repite aquí porque es el desliz más
probable en la redacción final.

---

## 3. Matriz de operacionalización

Tres vistas de lo mismo, para tres usos distintos: la tabla compacta que va en
el documento de tesis (§3.1), la ficha por indicador con fórmula exacta que se
necesita para programar (§3.2 y §3.3), y el estado de verificación de cada
fuente (§3.4). El archivo
[`matriz_operacionalizacion.csv`](matriz_operacionalizacion.csv) tiene la misma
información en formato de hoja de cálculo, para pegarla como tabla en el
documento final.

**Convenciones de notación.** `c` indexa la unidad espacial (ciudad para Y,
ciudad o provincia o departamento para X), `t` el mes calendario, `m` el mes del
año (01–12) al que pertenece `t`, y `d` el departamento. El periodo base de toda
climatología es **1991–2020**, estándar de la OMM.

### 3.1 Vista compacta (la que va en el documento)

| Variable | Dimensión | Indicador | Escala | Fuente |
|---|---|---|---|---|
| **X.** Shock exógeno de oferta de origen ENSO | D1 Magnitud | X1 Anomalía estandarizada de precipitación; X2 de temperatura máxima | Razón (σ) | ERA5 / ERA5-Land |
| | D2 Signo | X3 Exceso de lluvia; X4 déficit de lluvia; X5 exceso de calor | Razón (σ) | ERA5 / ERA5-Land |
| | D3 Persistencia | X6 Racha de meses consecutivos sobre umbral; X7 shock acumulado a 3, 6 y 12 meses | Razón | ERA5, NOAA/CPC |
| | D4 Anticipación | X8 ONI rezagado; X9 ICEN-réplica rezagado; X10 aviso del ENFEN; X11 antelación del aviso | Razón; nominal; intervalo | NOAA/CPC, ENFEN |
| | D5 Exposición económica | X12 Peso de agropecuario y pesca en el VAB; X13 peso del alimento en la canasta de la ciudad; X14 sensibilidad climática estimada; X15 aislamiento respecto de zonas productoras | Razón (%) | INEI, ERA5 |
| | D6 Calendario productivo | X16 Fase del calendario agrícola de la zona abastecedora | Nominal | MIDAGRI |
| **Y.** Precios de alimentos al consumidor urbano | D1 Nivel y tendencia | Y1 Inflación mensual de alimentos; Y2 inflación a 12 meses; Y3 nivel acumulado del log del índice | Razón (%) | INEI |
| | D2 Volatilidad | Y4 Desviación estándar móvil de 12 meses; Y5 varianza condicional GARCH | Razón | INEI |
| | D3 Picos | Y6 Indicador de pico sobre el percentil 90 propio; Y7 magnitud del exceso | Nominal; razón | INEI |
| | D4 Traspaso | Y8 Elasticidad del IPC general respecto del de alimentos; Y9 ídem del subyacente | Razón | INEI, BCRP |
| | D5 Integración espacial | Y10 Correlación móvil entre pares de ciudades; Y11 ancho de la banda neutral | Razón | INEI |

### 3.2 Fichas por indicador — variable X

#### D1. Magnitud del shock

**X1 — Anomalía estandarizada de precipitación.**

> A^pp_{c,t} = ( PP_{c,t} − μ^pp_{c,m} ) / σ^pp_{c,m}

donde `PP_{c,t}` es la precipitación acumulada del mes `t`, y `μ^pp_{c,m}` y
`σ^pp_{c,m}` son la media y la desviación estándar de los acumulados del mes del
año `m` sobre 1991–2020.

- **Definición operacional:** cuántas desviaciones estándar se aparta la lluvia
  del mes respecto de lo normal para ese mes en ese lugar.
- **Unidad / escala:** σ, razón. Rango esperado −3 a +3.
- **Fuente:** ERA5 (departamentos), ERA5-Land (provincias), vía la API de
  archivo de Open-Meteo.
- **Instrumento:** `scripts/calcular_normales.py` y
  `scripts/tesis/construir_panel.py`.
- **Periodicidad:** mensual.
- **⚠️ Dependencia crítica:** `data/normales.json` guarda **solo la media**
  (`precipitacion_mensual_mm`), **no la desviación estándar**. Por lo tanto
  **X1 no se puede calcular con los datos que el repositorio tiene hoy.**
  Requiere la tarea 0 (persistir el panel mes-año; ver BRECHAS.md §1), de la que
  σ sale por construcción. Esto no es un detalle administrativo: **el indicador
  principal de la variable independiente está bloqueado hasta que esa tarea se
  haga.**
- **Observación metodológica:** se usa la anomalía estandarizada y no la
  porcentual porque la porcentual se vuelve inestable donde la normal es casi
  nula —el problema del desierto costero que `docs/METODOLOGIA.md` ya documenta
  con el umbral de 5 mm—. La estandarización lo resuelve sin umbral arbitrario,
  **salvo donde σ también sea casi nula**, caso que debe reportarse aparte.

**X2 — Anomalía estandarizada de temperatura máxima.**

> A^tx_{c,t} = ( TX_{c,t} − μ^tx_{c,m} ) / σ^tx_{c,m}

con `TX_{c,t}` la media mensual de las máximas diarias. Misma unidad, fuente e
instrumento que X1. **⚠️ Misma dependencia, agravada:** en la estructura actual
del código, `tmax` y `tmin` se indexan solo por mes del año, de modo que la
dimensión temporal de la temperatura se pierde por completo (BRECHAS.md §1).

#### D2. Signo del shock

**X3 — Exceso de lluvia.** `A⁺pp_{c,t} = max( A^pp_{c,t} , 0 )`
**X4 — Déficit de lluvia.** `A⁻pp_{c,t} = max( −A^pp_{c,t} , 0 )`
**X5 — Exceso de calor.** `A⁺tx_{c,t} = max( A^tx_{c,t} , 0 )`

- **Definición operacional:** descomposición de la anomalía en sus partes
  positiva y negativa, cada una entrando como regresor separado. Si los
  coeficientes de X3 y X4 difieren en magnitud, hay asimetría (H4).
- **Escala:** razón, siempre no negativa.
- **Sustento:** la teoría del almacenamiento competitivo predice la asimetría, y
  Crofils et al. (2024) operacionalizan el shock peruano exactamente así, como
  **exceso de calor o de lluvia**.
- **Observación:** mantener los tres en la misma regresión, no estimarlos en
  regresiones separadas; si no, no se puede contrastar la igualdad de
  coeficientes.

#### D3. Persistencia

**X6 — Racha de meses consecutivos.** Número de meses consecutivos terminados en
`t` con `|A_{c,·}| ≥ 1`, por signo.

- **Umbral:** 1σ. Es una convención, y hay que declararla como tal; el ENFEN usa
  un criterio de **3 meses consecutivos** para declarar condiciones, lo que da
  un punto de comparación externo.
- **Escala:** razón, entero ≥ 0.

**X7 — Shock acumulado.** `S^k_{c,t} = Σ_{j=0}^{k−1} A_{c,t−j}` para k = 3, 6, 12.

- **Definición operacional:** suma de anomalías de los últimos k meses. Aproxima
  el agotamiento de inventarios, que es el mecanismo de la dependencia del
  estado (H4b).
- **Escala:** razón (σ acumuladas).

#### D4. Anticipación

**X8 — ONI rezagado.** `ONI_{t−k}`, k = 0…12.

- **Definición:** media móvil trimestral de la anomalía de TSM de la región Niño
  3.4, base 1991–2020, criterio NOAA.
- **Escala:** razón (°C). **Fuente:** NOAA/CPC. **Instrumento:**
  `scripts/fetch_oni.py`.
- **⚠️ Estado:** la serie guardada **arranca en 2021** (60 trimestres). Hay que
  extenderla a 1950, que es lo que el archivo de la NOAA ofrece.

**X9 — ICEN-réplica rezagado.** `ICEN*_t = (1/3) Σ_{j=0}^{2} a^{1+2}_{t−j}`

donde `a^{1+2}` es la anomalía mensual de TSM de la región Niño 1+2.

- **Escala:** razón (°C). **Fuente:** índices Niño 1+2 de la NOAA/CPC.
- **⚠️ Nombre provisional obligatorio:** se llama **ICEN-réplica** y no ICEN
  hasta validar contra los informes del IGP, porque la climatología base y la
  versión de ERSST que usa el ENFEN no están confirmadas (PROTOCOLO.md §4.3).

**X10 — Aviso del ENFEN.** Variable indicadora que vale 1 en el mes de un
pronunciamiento que declara o eleva el estado de alerta.

- **Escala:** nominal (dicotómica). **Fuente:** comunicados oficiales del ENFEN.
- **Por qué está en la matriz:** es el **único indicador estrictamente
  informacional** del conjunto. Mide el momento en que la señal se hace pública,
  no el estado del océano. Es lo que permite separar expectativa de realización
  (H1), siguiendo a Letta et al. (2021).
- **⚠️ No verificado:** hay que confirmar que los comunicados históricos estén
  disponibles con fecha y que el estado declarado sea codificable de forma
  consistente a lo largo del periodo.

**X11 — Antelación del aviso.** Días entre el aviso (X10 = 1) y el primer mes
con `|A_{c,·}| ≥ 1` en la unidad `c`.

- **Escala:** intervalo (días). Puede ser negativa si la anomalía local precede
  al aviso, y **ese caso es informativo**, no un error.

#### D5. Exposición económica

**X12 — Peso del sector primario en el VAB departamental.**

> E1_d = ( VAB_agropecuario_d + VAB_pesca_d ) / VAB_total_d

- **Escala:** razón (%). **Fuente:** INEI, cuentas nacionales departamentales.
- **Periodicidad:** anual, interpolada o mantenida constante dentro del año.
- **⚠️ No verificado:** existe en publicaciones; la ruta de descarga en formato
  utilizable no está confirmada.

**X13 — Peso del alimento en la canasta del IPC de la ciudad.**

> E2_c = ponderación de la división 01 (alimentos y bebidas no alcohólicas) en
> la estructura del IPC de la ciudad `c`

- **Escala:** razón (%). **Fuente:** INEI, estructura de ponderaciones del IPC.
- **Por qué importa:** Furceri et al. (2016) identifican este peso como el
  mecanismo que explica que el traspaso sea mayor en economías emergentes. Es la
  exposición **del consumidor**, complementaria a la del productor (X12).
- **⚠️ No verificado, y es el riesgo mayor de esta dimensión:** si el INEI
  publica ponderaciones solo para Lima Metropolitana, E2_c no varía entre
  ciudades y el indicador se cae. Plan alternativo declarado: usar el peso
  nacional y reconocer la pérdida de variación.

**X14 — Sensibilidad climática estimada (exposición continua).**

> β_c estimado en: A^pp_{c,τ} = α_c + β_c · ONI_τ + ε_{c,τ},  τ ∈ 1991–2020

- **Definición operacional:** cuánto responde la lluvia del lugar al índice
  oceánico, estimado **solo con el periodo de normales**, fuera del periodo de
  estimación de la tesis.
- **Escala:** razón (coeficiente). **Fuente:** derivado de ERA5 y NOAA.
- **Ventaja sobre X12 y X13:** sale de los datos y no de una clasificación por
  criterio, y al usar un periodo disjunto evita explotar dos veces la misma
  variación (PROTOCOLO.md §6.3).
- **Dependencia:** requiere el panel climático largo, es decir la tarea 0.

**X15 — Aislamiento respecto de zonas productoras.** Distancia o índice de
conectividad entre la ciudad y su principal zona abastecedora.

- **Escala:** razón (km o índice). **Fuente:** por definir.
- **⚠️ El dato que falta es cuál es la zona abastecedora de cada ciudad**, que es
  información de flujos comerciales que no tenemos. Sustituto admisible:
  distancia a la capital provincial agrícola de mayor producción del propio
  departamento, declarando el supuesto.
- **Sustento:** Zhu (2018) muestra que la integración de precios depende de las
  características de la red de transporte, sobre todo con restricciones de
  capacidad en los enlaces.

#### D6. Calendario productivo

**X16 — Fase del calendario agrícola.** Categórica: siembra, crecimiento,
cosecha, poscosecha, para la zona abastecedora de la ciudad en el mes `t`.

- **Escala:** nominal (cuatro categorías). **Fuente:** calendario de siembras y
  cosechas de MIDAGRI.
- **Uso:** interactúa con X1–X5. Crofils et al. (2024) encuentran que la
  respuesta es **mucho mayor cuando el shock ocurre en temporada de
  crecimiento**, y Letta et al. (2021) construyen su identificación sobre
  precisamente ese calendario.
- **⚠️ No verificado:** depende de X15 (saber qué zona abastece a cada ciudad).

### 3.3 Fichas por indicador — variable Y

#### D1. Nivel y tendencia

**Y1 — Inflación mensual de alimentos.**
> π_{c,t} = ln( IPC^{alim}_{c,t} ) − ln( IPC^{alim}_{c,t−1} )

**Y2 — Inflación a 12 meses.**
> π^{12}_{c,t} = ln( IPC^{alim}_{c,t} ) − ln( IPC^{alim}_{c,t−12} )

**Y3 — Nivel acumulado del log del índice.**
> p_{c,t+h} − p_{c,t−1}, con p = ln(IPC^{alim})

- **Escala:** razón (%). **Fuente:** INEI, IPC de 26 ciudades.
- **Y3 es la variable dependiente de las proyecciones locales**, porque la
  magnitud de interés es cuánto más caro está el alimento `h` meses después, no
  la tasa de ese mes.
- **Tratamiento del empalme:** base 2009 hasta diciembre de 2021 y base
  diciembre 2021 desde enero de 2022, con la serie empalmada según la
  metodología del INEI. La robustez se corre también por subperiodo de base.
- **⚠️ No verificado, y decide la viabilidad del diseño:** que exista el IPC
  **por ciudad y por división de gasto**. Ver PROTOCOLO.md §4.1 y su plan B.

#### D2. Volatilidad

**Y4 — Desviación estándar móvil.** Desviación estándar de π_{c,·} en la ventana
de los 12 meses terminados en `t`.

**Y5 — Varianza condicional.** `h_{c,t}` de un GARCH(1,1) sobre π_{c,t}.

- **Escala:** razón. **Fuente:** derivado de Y1.
- **Sustento:** von Braun y Tadesse (2012) y Díaz-Bonilla (2016) sostienen que
  la volatilidad es un tipo de cambio de precio distinto del nivel y debe
  medirse por separado.
- **Observación:** con T ≈ 200 por ciudad, un GARCH por ciudad es estimable pero
  justo; reportar Y4 como indicador principal y Y5 como contraste.

#### D3. Picos

**Y6 — Indicador de pico.** `1[ π_{c,t} > q_{90}( π_{c,·} ) ]`, con el percentil
calculado sobre la distribución propia de la ciudad.

**Y7 — Magnitud del exceso.** `max( π_{c,t} − q_{90}( π_{c,·} ) , 0 )`

- **Escala:** nominal dicotómica (Y6) y razón (Y7). **Fuente:** derivado de Y1.
- **Por qué el percentil es propio de cada ciudad y no común:** porque la
  distribución de inflación de alimentos difiere entre ciudades, y un umbral
  común confundiría "ciudad volátil" con "mes extremo".
- **Sustento:** von Braun y Tadesse (2012) tratan los picos como un tipo de
  cambio distinto de la volatilidad; el régimen de agotamiento de existencias de
  la teoría del almacenamiento es lo que los genera.

#### D4. Traspaso

**Y8 — Elasticidad del IPC general.** Coeficiente λ en
> Δln IPC^{gen}_{c,t} = κ_c + λ · Δln IPC^{alim}_{c,t} + controles + u_{c,t}

**Y9 — Ídem respecto del subyacente**, reemplazando el general por el
subyacente.

- **Escala:** razón (coeficiente). **Fuente:** INEI, BCRP.
- **Advertencia conceptual, que conviene dejar escrita en la tesis:** el traspaso
  es una **relación estimada**, no un atributo observado del precio. Entra como
  dimensión porque el objeto de interés es la dinámica del precio de alimentos
  dentro del sistema de precios, pero su indicador es un coeficiente.
- **Referencia de magnitud esperada:** Jalil y Tamayo (2011) encuentran, para un
  conjunto de economías latinoamericanas incluido el Perú, un traspaso
  **incompleto** que toma entre uno y seis trimestres.
- **⚠️ No verificado:** el IPC general por ciudad es probable; **el subyacente por
  ciudad es dudoso**. Si no existe, Y9 se elimina de la matriz.

#### D5. Integración espacial

**Y10 — Correlación móvil entre pares de ciudades.** Correlación de π entre las
ciudades `c` y `c'` en la ventana de 12 meses terminada en `t`; se resume por
ciudad como la media de sus correlaciones con las demás.

**Y11 — Ancho de la banda neutral.** Umbral estimado en un modelo de corrección
de error con umbral (TVECM) por par de ciudades.

- **Escala:** razón. **Fuente:** derivado de Y1 y del nivel del índice.
- **Sustento:** Goodwin y Piggott (2001) modelan la banda neutral como
  representación de los costos de transacción; McNew (1996) muestra que los
  costos de transporte elevados **reducen la integración y la transferencia de
  shocks entre regiones**.
- **Uso:** es el indicador que contrasta H5. Su virtud práctica es que **no
  requiere ningún dato que el panel de precios no tenga ya**.

### 3.4 Estado de verificación de cada fuente

Esta columna es la que decide qué sobrevive. La regla, ya fijada en §5: **una
dimensión cuya fuente no se confirme se elimina de la matriz antes de estimar,
no se estima con un sustituto silencioso.**

| Indicador | Estado | Qué falta |
|---|---|---|
| X1, X2 | 🔴 **Bloqueado** | σ por unidad y mes no existe en `normales.json`; requiere la tarea 0 |
| X3–X7 | 🔴 **Bloqueado** | Derivan de X1 y X2 |
| X8 | 🟡 Parcial | La serie ONI guardada arranca en 2021; extender a 1950 |
| X9 | 🟡 Parcial | Calculable desde la NOAA; falta validar contra el IGP |
| X10, X11 | 🟡 No verificado | Disponibilidad y codificación consistente de los comunicados del ENFEN |
| X12 | 🟡 No verificado | Ruta de descarga del VAB departamental |
| X13 | 🟠 **En riesgo** | Si las ponderaciones del IPC solo existen para Lima, no hay variación entre ciudades |
| X14 | 🔴 Bloqueado | Requiere la tarea 0 |
| X15, X16 | 🟠 **En riesgo** | Falta el dato de qué zona abastece a cada ciudad |
| Y1–Y3 | 🟠 **En riesgo, y decide todo** | Que el IPC exista por ciudad y por división de gasto |
| Y4–Y7, Y10, Y11 | 🟢 Derivados | Disponibles en cuanto Y1 exista |
| Y8 | 🟡 No verificado | IPC general por ciudad |
| Y9 | 🟠 En riesgo | IPC subyacente por ciudad, dudoso |

**Lectura de este cuadro.** De 27 indicadores, **ninguno es calculable hoy**: los
de X porque falta el panel climático, los de Y porque falta confirmar la fuente
del IPC desagregado. El orden de trabajo que esto impone es el mismo que ya
fijaron BRECHAS.md §4 y PROTOCOLO.md §9, y lo confirma desde otro ángulo: **la
tarea 0 y la verificación del IPC son prerrequisitos, no primeros capítulos.**

## 4. Correspondencia con las hipótesis

Si una dimensión no sirve para contrastar ninguna hipótesis, sobra. Ninguna
sobra, y los 27 indicadores cubren las siete hipótesis:

| Hipótesis | Indicadores que la contrastan | Cómo |
|---|---|---|
| **H1** anticipación frente a realización | X8, X9, X10, X11 contra X1, X2 → Y1, Y3 | Índice oceánico y aviso del ENFEN entran **junto con** la anomalía local; se compara qué componente mueve el precio y cuándo |
| **H2** heterogeneidad con mecanismo | (X12, X13, X14, X15) × (X1, X2) → Y1, Y3 | Interacción exposición × shock; el nivel del índice lo absorben los efectos fijos de tiempo |
| **H3** ONI frente a ICEN | X8 contra X9, por zona | Dos estimaciones paralelas y comparación de ajuste por región |
| **H4** asimetría | X3, X4, X5 → Y1 | Contraste de igualdad de coeficientes entre la parte positiva y la negativa |
| **H4b** dependencia del estado | X6, X7, X16 → Y4, Y5, Y6, Y7 | El efecto debe ser mayor tras rachas desfavorables y fuera de la ventana de cosecha |
| **H5** la integración cae en el evento | X8, X9 → Y10, Y11 | La correlación entre ciudades baja y la banda neutral se ensancha durante el episodio |
| **H6** atenuación por agregación | X1, X2 calculados a nivel departamental **y** provincial | El mismo modelo con las dos agregaciones; la teoría predice el signo de la diferencia |

### Regeneración de la matriz

`scripts/tesis/matriz.py` emite
[`matriz_operacionalizacion.csv`](matriz_operacionalizacion.csv) con los 27
indicadores y las once columnas, separado por punto y coma y en UTF-8 con BOM,
que es lo que Excel en configuración regional en español abre sin pedir
importación:

```bash
python scripts/tesis/matriz.py
```

El markdown de este documento es la fuente de verdad; si se cambia una ficha
aquí, hay que cambiarla también en el script y volver a generar el CSV.

## 5. Datos de D5 y D6: estado de verificación

Honestidad sobre lo que todavía no está confirmado, igual que en el resto de los
documentos de esta carpeta:

- **X-D5(a)**, participación de agropecuario y pesca en el VAB departamental:
  existe en publicaciones del INEI; **la ruta de descarga en formato utilizable
  no está verificada** (ver BRECHAS.md §1).
- **X-D5(b)**, participación del alimento en la canasta por ciudad: depende de
  que el INEI publique la estructura de ponderaciones **por ciudad** y no solo
  para Lima Metropolitana. **No verificado.** Si solo existe para Lima, D5(b) se
  reemplaza por el peso nacional y se declara la limitación.
- **X-D6**, calendario de cosecha por zona abastecedora: requiere además saber
  **qué zona abastece a cada ciudad**, que es un dato de flujos comerciales que no
  tenemos. Alternativa factible: usar el calendario del propio departamento y
  declarar el supuesto de autoabastecimiento parcial.
- **Y-D4**, traspaso: requiere IPC general y subyacente por ciudad. El general
  por ciudad es probable; **el subyacente por ciudad es dudoso**.

Las dimensiones cuya fuente no se confirme **se eliminan de la matriz antes de
estimar**, no se estiman con un sustituto silencioso.

## 6. Referencias

- Arango-Castillo, L. et al. (2025). The effects of temperature and rainfall
  anomalies on Mexican inflation.
- Auffhammer, M., Hsiang, S., Schlenker, W. y Sobel, A. (2013). Using Weather
  Data and Climate Model Output in Economic Analyses of Climate Change.
  *Review of Environmental Economics and Policy*.
- Balié, J., Magrini, E. y Morales Opazo, C. (2016). Cereal price shocks and
  volatility in Sub-Saharan Africa: what does really matter for farmers'
  welfare?
- Bellon, M. y Massetti, E. (2022). Estimating Macro-Fiscal Effects of Climate
  Shocks From Billions of Geospatial Weather Observations. *IMF Working Papers*.
- Crofils, C. et al. (2024). The dynamic effects of weather shocks on
  agricultural production. *Journal of Environmental Economics and Management*.
- Díaz-Bonilla, E. (2016). Volatile Volatility: Conceptual and Measurement
  Issues Related to Price Trends and Volatility.
  DOI 10.1007/978-3-319-28201-5_2.
- Kim, H. et al. (2021). Extreme Weather and the Macroeconomy. Federal Reserve
  Bank of Richmond Working Papers.
- Kim, H. et al. (2025). Severe Weather and the Macroeconomy. *American Economic
  Journal: Macroeconomics*.
- Ojeda-Joya, J. N. et al. (2026). Weather anomalies and comparative advantages
  in emerging and developing economies. *Structural Change and Economic
  Dynamics*.
- Tol, R. S. J. (2021). The Economic Impact of Weather and Climate.
- von Braun, J. y Tadesse, G. (2012). Global Food Price Volatility and Spikes:
  An Overview of Costs, Causes, and Solutions. DOI 10.22004/AG.ECON.120021.
- Winter, D. G. et al. (2026). Beyond the mean: the macroeconomic consequences
  of shifting temperature anomaly distributions. *Climatic Change*.

Las referencias de traspaso (Jalil y Tamayo 2011; Furceri et al. 2016; Anand et
al. 2014), almacenamiento (Wright y Williams 1982; Cafiero et al. 2011, 2014) y
equilibrio espacial (McNew 1996; Goodwin y Piggott 2001) están en
[MARCO_TEORICO.md](MARCO_TEORICO.md) §10.
