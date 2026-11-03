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

## 3. Matriz de operacionalización (versión para el jurado)

| Variable | Dimensión | Indicador | Escala | Fuente |
|---|---|---|---|---|
| **X.** Shock exógeno de oferta de origen ENSO | D1 Magnitud | Anomalía mensual estandarizada de lluvia y temperatura, base 1991–2020 | Razón (σ) | ERA5 / ERA5-Land |
| | D2 Signo | Exceso de lluvia, exceso de calor, déficit hídrico (separados) | Razón (σ con signo) | ERA5 |
| | D3 Persistencia | Meses consecutivos sobre umbral; acumulado a 3, 6 y 12 meses | Razón | ERA5, NOAA |
| | D4 Anticipación | ONI, ICEN-réplica rezagados; fecha de pronunciamiento del ENFEN | Razón; intervalo | NOAA/CPC, ENFEN |
| | D5 Exposición económica | Participación de agropecuario y pesca en el VAB departamental; participación del alimento en la canasta del IPC de la ciudad | Razón (%) | INEI |
| | D6 Calendario | Fase del calendario de cosecha de la zona abastecedora | Nominal | MIDAGRI |
| **Y.** Precios de alimentos al consumidor urbano | D1 Nivel y tendencia | Variación mensual y a 12 meses del log del IPC de alimentos | Razón (%) | INEI |
| | D2 Volatilidad | Desviación estándar móvil; varianza condicional | Razón | INEI |
| | D3 Picos | Frecuencia y magnitud de cambios en la cola | Razón | INEI |
| | D4 Traspaso | Elasticidad del IPC general y subyacente respecto del de alimentos | Razón | INEI, BCRP |
| | D5 Integración espacial | Correlación entre pares de ciudades; ancho de banda neutral | Razón | INEI |

## 4. Correspondencia con las hipótesis

Si una dimensión no sirve para contrastar ninguna hipótesis, sobra. Ninguna
sobra:

| Hipótesis | Dimensiones que la contrastan |
|---|---|
| H1 (anticipación y realización) | X-D4 frente a X-D1 |
| H2 (heterogeneidad con mecanismo) | X-D5 × X-D1; Y-D5 |
| H3 (ONI frente a ICEN) | X-D4 en sus dos versiones |
| H4 (asimetría) | X-D2 |
| H4b (dependencia del estado) | X-D3, X-D6; Y-D3 |
| H5 (la integración cae en el evento) | Y-D5 |
| H6 (atenuación por agregación) | X-D1 en nivel departamental frente a provincial |

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
