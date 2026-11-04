# Antecedentes

Organizado en los tres niveles que pide el formato de tesis peruano
—internacional, nacional, local— más una sección de tesis previas. Cada entrada
declara **qué hizo** y **qué dejó abierto**, porque un antecedente que solo se
resume no sirve para construir la brecha.

**Dos advertencias de honestidad antes de empezar.**

1. **Esta búsqueda obliga a corregir el reclamo de originalidad.** Aparecieron
   antecedentes peruanos que no estaban en la primera revisión y que ocupan
   parte del terreno que la tesis reclamaba. Está marcado en §6, y no se
   disimula.
2. **Dos fuentes no se pudieron verificar en original.** La política de red de
   la sesión donde se redactó este documento bloquea `www.bcrp.gob.pe` y
   `repositorio.pucp.edu.pe`. Las entradas correspondientes están marcadas
   **⚠️ sin verificar en fuente primaria** y deben confirmarse antes de citarlas
   en la tesis.

---

> **Propuesta de revisión sistemática.** Este capítulo se construyó con
> búsquedas temáticas, no con un protocolo sistemático. La propuesta para
> hacerlo de forma sistemática —con PRISMA 2020 y las guías de MAER-Net,
> incluida la literatura gris y las fuentes iberoamericanas— está en
> [REVISION_SISTEMATICA.md](REVISION_SISTEMATICA.md). Si se ejecuta, la
> brecha de escala espacial dejaría de ser una afirmación del autor y pasaría
> a ser un hallazgo cuantificado.

> **Versión en matriz.** Los 21 antecedentes de este documento están también
> como tabla —autor y año, título, metodología, resultados principales y
> aporte o vacío que deja— en
> `docs/tesis/Matrices_antecedentes_marco_teorico.docx`, que genera
> `scripts/tesis/matrices_teoricas_docx.js`. Si se agrega un antecedente
> aquí, hay que agregarlo también en ese script.

## 1. Antecedentes internacionales

### 1.1 ENSO e inflación, evidencia global

**Yilmazkuday (2025). *El Niño, La Niña and Inflation*.**
Datos mensuales de ENSO, **188 países, 1970–2023**, con **proyecciones locales**,
efectos fijos de país y tendencias temporales específicas por país, sobre
inflación general, de energía, de alimentos, al productor y subyacente.

- **Resultado central, y es contraintuitivo:** los shocks hacia condiciones
  **tipo La Niña** elevan todas las medidas de inflación, con el mayor efecto en
  energía, seguido de **alimentos**.
- Los países **en desarrollo** se ven más afectados precisamente en la
  **inflación de alimentos**.
- Los efectos **han crecido con el tiempo**, y el aumento es más evidente en
  alimentos y subyacente.
- **Qué deja abierto:** es un panel de países. No dice nada de la variación
  *dentro* de un país, ni distingue el Pacífico central del oriental.
- **Por qué importa para esta tesis:** respalda la elección de proyecciones
  locales y de la inflación de alimentos como variable, y **advierte contra
  suponer el signo**: la fase fría también puede ser inflacionaria. Converge con
  Borrallo et al. (2024), que cuestionan el supuesto Niño-sube / Niña-baja.

**Cashin, Mohaddes y Raissi (2015). *Fair Weather or Foul? The Macroeconomic
Effects of El Niño*.** Marco dinámico multipaís, 21 modelos país/región,
1979Q2–2013Q1; considera exposiciones directas e indirectas. Es el antecedente
macro clásico. **Deja abierto** todo lo subnacional.

**Gallegati et al. (2026, *PLOS Climate*) y Solomou et al. (2025, *Climate
Research*).** Introducen la **"diversidad de ENSO"**: los tipos de Pacífico
central (CP) y oriental (EP) difieren en estructura espacial, intensidad y
perfil temporal, y sus efectos sobre la inflación nacional **no son los mismos**.
GVAR y wavelets. **Deja abierto:** la distinción se estima entre países; nunca
entre regiones de un mismo país. Es el antecedente directo de H3.

### 1.2 ENSO y precios de alimentos, con heterogeneidad y asimetría

**Emediegwu (2024, *Environmental and Resource Economics*).** Más de **1 100
mercados en 36 países** de África subsahariana, modelos STAR variables en el
tiempo. ENSO afecta cerca de la mitad de los precios considerados, con
asimetría fuerte y persistencia; hay una división geográfica y por producto, y
concluye que la respuesta debe ser **subregional, no regional**. **Es el
antecedente metodológico de la asimetría (H4) y del argumento de
desagregación.**

**Bohorquez-Penuela et al. (2026).** Colombia: precios mayoristas de 40
cultivos, nueve años, redes de producción y datos granulares de lluvia y
temperatura, para separar efectos locales y transmitidos. **Es el diseño que
sería ideal para el Perú y que no tenemos datos para replicar** (ver
BRECHAS.md): lo registramos como antecedente y como límite.

**Abril et al. (2019, *AJARE*).** Relación **no lineal** entre El Niño y los
precios de alimentos en Colombia, con énfasis en el evento 2015-16.

**Botero et al. (2022, *Food Security*).** ENSO y frijol común en Colombia,
1991–2018, Prais-Winsten. **El Niño reduce rendimientos; La Niña no.** Dos
conclusiones que usamos: la precipitación tiene relación **no lineal** con
rendimientos e ingresos, por lo que deben incorporarse efectos de segundo orden;
y los **picos de precio sobrecompensan** la caída de rendimientos, de modo que
el productor puede ganar mientras el **consumidor pierde poder de compra**. Esto
último es exactamente la distinción comprador/vendedor neto que el IPC no
observa (OPERACIONALIZACION.md §2).

**Ubilava (2017, *AJAE* y *World Development*).** ENSO y dinámica de precios de
43 commodities; asimetrías en el precio del trigo. **Ahmad et al. (2019)** y
**Marpaung et al. (2019)**: paneles de inflación de 25+ provincias de Indonesia,
con **dependencia espacial significativa** en el primero.

**Letta et al. (2021, *AJAE*).** Panel distrital mensual de precios mayoristas
en India, 2004–2017: la sequía eleva precios **antes de la cosecha** y las
expectativas anticipan **más del 80 %** del impacto. **Antecedente de H1
reformulada.**

**McNew (1996, *ARER*).** Integración del maíz en el Misisipi durante la
**inundación de 1993**: mayores costos de transporte **redujeron la integración
y la transferencia de shocks entre regiones**. **Antecedente de H2 y H5.**

### 1.3 Clima e inflación regional en América Latina

**Arango-Castillo et al. (2025).** Panel regional de inflación en **México**,
con desviaciones de temperatura y precipitación **ponderadas por población**
respecto de la norma de media móvil de 30 años; panel ARDL más proyecciones
locales. **En el corto plazo no encuentran efecto estadístico**; en el largo
plazo solo la precipitación importa. **Es el antecedente metodológico más
cercano a nuestra especificación, y el recordatorio de que un coeficiente no
significativo es un resultado admisible.**

**Jalil y Tamayo (2011).** Traspaso de precios internacionales de alimentos a
inflación doméstica en Brasil, Chile, Colombia, México y **el Perú**: toma entre
**uno y seis trimestres**, es **incompleto**, y hay indicios de efectos de
segunda vuelta sobre la subyacente.

---

## 2. Antecedentes nacionales (Perú)

Ordenados por cercanía al diseño de la tesis, de más a menos.

### 2.1 Crofils, Gallic y Vermandel (2024, *Journal of Environmental Economics and Management*)

*The dynamic effects of weather shocks on agricultural production.*
DOI 10.1016/j.jeem.2024.103078.

- **Qué hace:** producción agrícola **mensual del Perú** con **proyecciones
  locales**; shock adverso medido como **exceso de calor o de lluvia**.
- **Resultados:** caída de ~**5 % mensual** en la producción agrícola **hasta
  cuatro meses consecutivos**; magnitud y duración dependen del cultivo, del
  tipo geográfico y de la estación; respuesta **mucho mayor en selva y en
  temporada de crecimiento**. A nivel macro, los shocks **elevan la inflación**
  y reducen la producción agregada.
- **Nota de discrepancia entre versiones:** el preprint (SSRN 2024) describe el
  efecto macro como recesivo con **caída** de inflación, mientras la versión
  publicada en *JEEM* reporta **alza** de inflación. **Hay que citar la versión
  publicada y revisar esa diferencia en el texto final**, porque el signo de la
  inflación es justamente nuestra variable.
- **Qué deja abierto:** la variable dependiente es producción agrícola e
  inflación **agregada**; no hay IPC por ciudad, ni distinción ONI/ICEN, ni
  canal de expectativas, ni integración de mercados.
- **Es el antecedente más cercano que existe.** Validar el diseño mensual con
  proyecciones locales ya está hecho, y bien, en un journal de primer nivel del
  campo.

### 2.2 Calero y Rodríguez (2026, PUCP, Documento de Trabajo)

*Time-Varying Effects of Climate Change Shocks on Macroeconomic Fluctuations in
Peru.* DOI 10.18800/2079-8474.0558.
⚠️ Verificado por el resumen indexado; **el PDF no se pudo abrir** (host
bloqueado). Confirmar cifras antes de citar.

- **Qué hace:** TVP-VAR-SV (parámetros variables en el tiempo con volatilidad
  estocástica, Chan y Eisenstat 2018) con **dos shocks**: el fenómeno El Niño
  (ENP) y desviaciones de la temperatura media respecto de su media histórica.
- **Resultados:** **ambos operan como shocks negativos de oferta** —reducen el
  PBI, **elevan la inflación** y suben la tasa de interés—. El PBI cae 0,8 pp
  ante el ENP; **la inflación sube 0,25 pp** ante ambos shocks. Por sectores, el
  PBI primario cae 1,5 pp ante el ENP, con **−5,0 pp en pesca** y −0,8 a −1,0 pp
  en agricultura. Los efectos son **variables en el tiempo**, mayores en 1998Q2
  y **2017Q2**, y el ENP es más importante que las desviaciones de temperatura.
- **Qué deja abierto:** es agregado nacional y trimestral. No hay desagregación
  regional ni urbana, ni separación ONI/ICEN, ni precios de alimentos
  específicamente.
- **Por qué importa:** es la confirmación más reciente y rigurosa de que en el
  Perú **el canal inflacionario existe y es de oferta**. La tesis ya no tiene
  que demostrar que el efecto existe: tiene que **decir dónde y cuánto varía**.

### 2.3 BCRP, *Revista Moneda* nº 196 — exploración del impacto económico

⚠️ **Sin verificar en fuente primaria.** Lo que sigue proviene de un resumen de
buscador, no del PDF (`www.bcrp.gob.pe` bloqueado). **Es la entrada más
importante de verificar**, por lo que implica.

- Según ese resumen, el estudio mide el Niño costero con el **índice ICEN** y
  halla efectos negativos en agropecuario, pesca, manufactura, comercio y
  servicios, con efectos inflacionarios **que pesan más sobre la inflación de
  alimentos**.
- **Si eso se confirma**, entonces el uso del ICEN como regresor económico y el
  hallazgo del canal de alimentos **ya existen a nivel nacional**, y el reclamo
  de originalidad de la tesis debe reformularse (ver §6).

### 2.4 BCRP DT 008-2025 y BIS WP 1276

*ENSO and its Economic Impact in the Peruvian Economy.* Datos mensuales de
BCRPData 1994M1–2019M12; PBI total, primario y no primario; modelo
semi-estructural. ENSO deja una huella similar a un shock de oferta, con
respuesta del sector primario **más inmediata, mayor y persistente**. **Deja
abierto:** agregado nacional, sin precios regionales.

### 2.5 Saldarriaga (2016, BID)

*Efectos de la variabilidad de la temperatura en la productividad y en los
precios de los productos agrícolas: evidencia en Perú.* DOI 10.18235/0000522.

- ENAHO 2004–2010 combinada con temperaturas en grilla de 0,5° (~56 km);
  identificación por **variación interanual dentro de cada municipalidad**.
- Una desviación estándar por encima de la temperatura histórica municipal
  reduce la producción por hectárea entre **US$ 170 y US$ 190** y la
  rentabilidad entre **US$ 150 y US$ 200**; el efecto varía por zona geográfica,
  siendo la **Amazonía la más afectada**; y son las temperaturas **inusualmente
  cálidas, no las frías**, las que más dañan.
- **Deja abierto:** solo temperatura, sin ENSO ni precipitación; precios **en
  finca**, no IPC al consumidor; termina en 2010.

### 2.6 Tambet y Stopnitzky (2021, *American Journal of Agricultural Economics*)

*Climate Adaptation and Conservation Agriculture among Peruvian Farmers.*

- Tres rondas de la **Encuesta Nacional Agropecuaria (ENA)** combinadas con
  datos climáticos de largo plazo para construir **shocks georreferenciados de
  nivel y variabilidad anormal de lluvia**; maíz y papa.
- Los agricultores **ajustan sus prácticas** según el shock: reducen
  conservación de suelos tras un año de lluvia alta pero la aumentan tras varios
  años de lluvia baja; el uso de pesticidas sube ocho puntos porcentuales tras
  un año de sequía; el fertilizante es menos sensible.
- **Por qué importa:** es evidencia peruana, en un journal de primer nivel, de
  **respuesta endógena del productor** — es decir, de la "capacidad adaptativa"
  traducida a conducta económica observable. Y señala la **ENA** como fuente
  nacional que no estábamos considerando.

### 2.7 Andrián et al. (2024, BID) y Martin (2016, BID)

*Efectos del fenómeno "El Niño" en la Región Andina: una aproximación empírica*
(DOI 10.18235/0005494) y *¡Es Niño! Impacto económico en la Región Andina*
(DOI 10.18235/0000234).

- VAR con El Niño como variable **exógena**. Andrián et al.: impactos negativos
  en crecimiento de 0,1 a 3,4 pp en 2024, con **Perú y Ecuador los más
  afectados**, e inflación que podría subir entre **0,7 y 3,5 pp**, señalando que
  **las diferencias geográficas y de estructura económica son cruciales**.
  Martin: un Niño de normal a extraordinario restaría entre **0,6 y 1,7 % del
  PBI** andino, con el Perú y Ecuador por encima de 1,5 %, y alzas del nivel de
  precios de **1 a 5 %**; incluye el recuento de daños de los "Meganiños" de
  1982-83 y 1997-98.
- **Deja abierto:** país como unidad. Pero **la frase sobre estructura económica
  es, textualmente, la justificación de esta tesis**: si la estructura importa,
  hay que medirla donde varía, y varía dentro del país.

### 2.8 Briceño-Ávalos et al. (2025) y Yglesias-González et al. (2023)

Ya reseñados en BRECHAS.md §2: panel regional 2014–2023 donde la **duración de
El Niño y La Niña no resulta significativa** (solo los extraordinarios de 1957,
1972, 1983 y 1998), y el primer estudio de caso del Niño costero 2017 sobre
economía, salud y gobernanza, que pide expresamente **análisis de riesgo a nivel
local**.

---

## 3. Antecedentes locales (sierra sur, altiplano, Cusco)

Esta es la capa que faltaba, y es la que un jurado de la UNSAAC va a pedir.
Importante: **casi toda es agronómica o climatológica, no económica.** Eso no la
descalifica —fija el mecanismo físico que la tesis supone— pero conviene decirlo
y no presentarla como evidencia económica.

### 3.1 Canedo-Rosso et al. (2020). *Drought and Agricultural Production in the Central Andes*

Sequía en los Andes centrales, generalmente impulsada por **fases cálidas de
ENSO**. Confirman relación negativa entre precipitación de verano y fase cálida,
y encuentran **menor rendimiento de quinua y papa en años de El Niño fuerte y
muy fuerte**, con foco en el Altiplano. **Es el antecedente que sostiene el
mecanismo de déficit hídrico en la sierra sur**, que en nuestro diseño es la
zona de signo potencialmente opuesto a la costa norte.

### 3.2 Arana-Ruedas et al. (2023). ENSO y sequía agrícola en el valle del Mantaro

SPEI en cuatro provincias y seis estaciones, 1990–2021: **el 70 % de los eventos
de sequía agrícola ocurrió con ENSO presente**, con correlación de severidad muy
variable (9 %–70 %). Valle del Mantaro, una de las zonas agrícolas más
importantes del país. **Antecedente de la relación ENSO → sequía → agricultura
en la sierra, con cifra.**

### 3.3 Ponce (2020, *World Development*; 2023, *Journal of Development Studies*)

Economía, y sobre los Andes peruanos:

- **2020:** variabilidad climática **intra-estacional** y diversificación de
  cultivos; combina información socioeconómica distrital de dos censos agrarios
  (1994 y 2012) con estimaciones climáticas distritales, en modelos de efectos
  fijos **que permiten heterogeneidad de parámetros por subregión**. Advierte
  sobre la sostenibilidad de la adaptación.
- **2023:** ingreso laboral no agrícola; encuentra efectos **heterogéneos entre
  subregiones** y, en particular, **ningún efecto directo entre los hogares del
  sur** —más aislados e indígenas— mientras sí lo hay en zonas frías del centro
  y norte.
- **Por qué importa:** es el antecedente económico más próximo a la sierra sur, y
  su resultado es una advertencia directa: **el sur puede comportarse distinto, o
  no responder**. Y su diseño —efectos fijos con heterogeneidad de parámetros
  por subregión— es el que nuestra especificación B imita.

### 3.4 Imfeld et al. (2020, *International Journal of Climatology*)

Climatología y tendencias de precipitación y temperatura en los **Andes del sur
del Perú**, 1965/66–2017/18, con **datos de estación controlados y
homogeneizados** más datos en grilla. Señalan que **ENSO tiene efectos
modificadores** sobre precipitación y temperatura, y que por eso produce
tendencias mayores en las máximas.

> **Uso práctico inmediato para el repositorio:** este trabajo usa datos de
> estación homogeneizados para la sierra sur. Es un **candidato para validar
> nuestras normales ERA5 en el sur**, que es justo la validación pendiente que
> `docs/METODOLOGIA.md` declara imposible por la indisponibilidad del visor de
> SENAMHI y la licencia CC BY-NC-ND de su dataset. Vale la pena revisar si
> publican sus series o climatologías.

### 3.5 Tito et al. (2018, *Global Change Biology*) y Visscher et al. (2023)

Experimentos de campo en los Andes peruanos trasladando papa y maíz entre
altitudes: la producción cayó **más de 87 %** bajo temperaturas más cálidas,
principalmente por **nuevas plagas**, con pérdidas económicas estimadas de hasta
**US$ 2 300 por hectárea al año**. Visscher et al. encuentran que el manejo
tradicional de fertilidad **atenúa** el impacto en cultivos andinos
tradicionales. **Mecanismo biofísico del canal de oferta, con valoración
económica.**

### 3.6 Enfoque ricardiano en el Altiplano (2021, *Revista de Investigaciones Altoandinas*)

*Impacto económico del cambio climático en cultivo de quinua orgánica en la
Región del Altiplano: un enfoque ricardiano.* Encuesta a **237 agricultores** en
Cabana, Capachica e Ilave (Puno), con variables climáticas de SENAMHI Puno.
Producción media de 1 497 kg/ha e ingreso neto de 14 969 soles/ha; concluye que
el impacto de las variables agroclimáticas sobre el ingreso fue **marginal** en
la campaña 2015-2016.

- **Por qué conviene citarlo:** es antecedente **local, económico y en español**,
  publicado en una revista altoandina — exactamente el perfil que el jurado
  busca. Y su resultado marginal es otro recordatorio de que el efecto puede no
  aparecer.
- **Límite:** un corte transversal de una campaña y el enfoque ricardiano, que
  la literatura de identificación critica por sesgo de variables omitidas
  (MARCO_TEORICO.md §2).

### 3.7 Sayre et al. (2017). Parque de la Papa, Cusco

*You Can't Grow Potatoes in the Sky.* Comunidades quechuas y la Asociación ANDES
en el Parque de la Papa, con investigación participativa y conocimiento
tradicional. **Cualitativo**: sirve de contexto local y de justificación social,
no de evidencia econométrica. Útil en la introducción, no en los antecedentes
empíricos.

---

## 4. Tesis previas como antecedente

El formato peruano suele pedirlas. Lo encontrado es magro y conviene decirlo:

- **UNFV, Escuela de Posgrado.** Documento de repositorio sobre el impacto
  económico del Niño costero, con hipótesis sobre agricultura. ⚠️ **El texto
  recuperado está fragmentado y no se pudo verificar metodología ni resultados.**
  Hay que abrir el PDF completo antes de citarlo.
- **Oostdam (2017), tesis de maestría, Erasmus.** Efecto del **Índice de
  Oscilación del Sur** sobre precios de commodities alimentarios, 1980–2016,
  mensual, para cacao, café, arroz, **pescado peruano**, aceite de palma y soya.
  Encuentra efecto significativo solo en aceite de palma y **pescado peruano**
  (alza de ~0,7 % hasta tres meses después), **ningún efecto no lineal**, y un
  **efecto que decrece en el tiempo**. Útil como antecedente de tesis y porque el
  pescado peruano aparece como el canal más sensible.
- **No se encontraron tesis de la UNSAAC ni de la UNA Puno** sobre este tema en
  la búsqueda realizada. **Eso no significa que no existan:** los repositorios
  institucionales suelen no estar bien indexados en buscadores académicos. **Hay
  que buscar directamente en el repositorio de la UNSAAC y en ALICIA/RENATI**
  con los términos "Niño costero", "inflación de alimentos", "precios
  agrícolas", "shock de oferta". Es una tarea pendiente, no un hallazgo
  negativo.

---

## 5. Síntesis

| Nivel | Antecedente | Unidad | ¿Precios? | ¿ONI/ICEN separados? |
|---|---|---|---|---|
| Internacional | Yilmazkuday (2025) | 188 países | IPC alimentos | No |
| Internacional | Gallegati (2026); Solomou (2025) | Países | IPC general | **Sí (CP/EP)**, entre países |
| Internacional | Emediegwu (2024) | 1 100 mercados, 36 países | Precios locales | No |
| Internacional | Letta et al. (2021) | Distritos, India | Mayoristas | No |
| Internacional | Arango-Castillo (2025) | Regiones, México | IPC regional | No |
| Nacional | **Crofils et al. (2024)** | Regiones, Perú, mensual | Inflación agregada | No |
| Nacional | **Calero y Rodríguez (2026)** | Nacional, trimestral | Inflación | No |
| Nacional | **BCRP Moneda 196** ⚠️ | Sectorial | **Inflación de alimentos** | **ICEN** |
| Nacional | Saldarriaga (2016) | Municipalidades | Precios en finca | No |
| Nacional | Tambet y Stopnitzky (2021) | Localidades | No (prácticas) | No |
| Local | Canedo-Rosso (2020) | Altiplano | No (rendimientos) | Fases ENSO |
| Local | Ponce (2020, 2023) | Distritos andinos | No (ingresos) | No |
| **Esta tesis** | — | **26 ciudades, mensual** | **IPC alimentos por ciudad** | **Sí, dentro del país** |

La última fila es el aporte, y la columna que lo sostiene es la combinación de
las dos últimas: **nadie cruza IPC de alimentos por ciudad con los dos índices
separados.**

## 6. Corrección obligada al reclamo de originalidad

Lo que esta búsqueda cambia, dicho sin adornos:

1. **"El canal inflacionario de ENSO en el Perú no está estudiado" es falso.**
   Calero y Rodríguez (2026) lo cuantifican a nivel nacional (+0,25 pp de
   inflación) y Crofils et al. (2024) lo reportan en un *JEEM*. La tesis **no
   debe plantearse como descubrimiento del efecto**, sino como **medición de su
   distribución geográfica**.
2. **"Nadie usa el ICEN en economía" probablemente también es falso.** Si se
   confirma la nota de *Moneda* 196, el BCRP ya lo usó y ya encontró que el
   efecto pesa más en alimentos. **Hay que verificarlo antes de escribir una
   línea sobre originalidad del ICEN.** Lo que sobrevive, incluso en el peor
   caso, es la **comparación ONI frente a ICEN a nivel subnacional**, que ningún
   trabajo revisado hace.
3. **Lo que sigue intacto como aporte:**
   - desagregación a **26 ciudades** con IPC de alimentos (nadie);
   - **ONI frente a ICEN dentro del país, entre regiones** (nadie);
   - separación del canal de **expectativas** frente al de realización, usando
     los pronunciamientos fechados del ENFEN (nadie, en el Perú);
   - **integración de mercados durante el evento**, H5 (nadie, en el Perú);
   - **prueba de atenuación por agregación**, H6 (nadie, en ninguna parte de
     esta literatura).
4. **Tres advertencias de resultado posible**, todas de antecedentes reales:
   Arango-Castillo et al. (2025) no hallan efecto de corto plazo en México;
   Ponce (2023) no halla efecto directo en los hogares del **sur** peruano; y el
   estudio ricardiano del Altiplano (2021) halla impacto **marginal**. El
   protocolo debe estar escrito para que un no-resultado sea publicable.
5. **Una fuente nueva que no estábamos considerando:** la **Encuesta Nacional
   Agropecuaria (ENA)**, usada por Tambet y Stopnitzky (2021) en *AJAE*. Entra
   en la lista de verificación de datos.
6. **Una oportunidad de validación:** Imfeld et al. (2020) trabajan con datos de
   estación **homogeneizados** para los Andes del sur. Puede resolver, al menos
   parcialmente, la validación de normales que `METODOLOGIA.md` declara
   bloqueada por la indisponibilidad de SENAMHI.

## 7. Tareas que este documento genera

| # | Tarea | Por qué |
|---|---|---|
| 1 | **Abrir el PDF de *Moneda* 196** y confirmar si usa ICEN y qué halla | Decide cómo se redacta la originalidad (§6.2) |
| 2 | Abrir el DT de Calero y Rodríguez (2026) y confirmar cifras | Es el antecedente nacional más reciente |
| 3 | Revisar la discrepancia de signo de inflación entre el preprint y la versión *JEEM* de Crofils et al. | El signo es nuestra variable dependiente |
| 4 | Buscar en el repositorio de la **UNSAAC** y en **ALICIA/RENATI** | El jurado pedirá tesis previas |
| 5 | Evaluar la **ENA** como fuente | Puede abrir el eslabón productor |
| 6 | Ver si Imfeld et al. (2020) publican series homogeneizadas del sur | Validación de normales |

Las tareas 1 y 2 requieren que `www.bcrp.gob.pe` y `repositorio.pucp.edu.pe`
estén permitidos en la configuración de red de la sesión, o hacerse a mano.

## 8. Referencias

Las que no se repiten aquí están en [MARCO_TEORICO.md](MARCO_TEORICO.md) §10,
[BRECHAS.md](BRECHAS.md) §5 y [OPERACIONALIZACION.md](OPERACIONALIZACION.md) §6.

- Andrián, L. et al. (2024). Efectos del fenómeno "El Niño" en la Región Andina:
  una aproximación empírica. BID. DOI 10.18235/0005494.
- Arana-Ruedas, D. P. R. et al. (2023). ENSO Influence on Agricultural Drought
  Identified by SPEI Assessment in the Peruvian Tropical Andes, Mantaro Valley.
  *Manglar*.
- Botero, H. et al. (2022). The effect of ENSO on common bean production in
  Colombia: a time series approach. *Food Security*.
- Calero, R. y Rodríguez, G. (2026). Time-Varying Effects of Climate Change
  Shocks on Macroeconomic Fluctuations in Peru. PUCP, Documento de Trabajo.
  DOI 10.18800/2079-8474.0558.
- Canedo-Rosso, C. et al. (2020). Drought and Agricultural Production in the
  Central Andes.
- Cashin, P., Mohaddes, K. y Raissi, M. (2015). Fair Weather or Foul? The
  Macroeconomic Effects of El Niño.
- Crofils, C., Gallic, E. y Vermandel, G. (2024). The dynamic effects of weather
  shocks on agricultural production. *JEEM*. DOI 10.1016/j.jeem.2024.103078.
- Imfeld, N. et al. (2020). A combined view on precipitation and temperature
  climatology and trends in the southern Andes of Peru. *International Journal
  of Climatology*.
- Martin, L. (2016). ¡Es Niño! Impacto económico en la Región Andina. BID.
  DOI 10.18235/0000234.
- Oostdam, S. J. (2017). The influence of the El Niño proxy — the "Southern
  Oscillation Index" — on food commodity prices. Tesis de maestría, Erasmus
  University Rotterdam.
- Ponce, C. (2020). Intra-seasonal climate variability and crop diversification
  strategies in the Peruvian Andes. *World Development*.
- Ponce, C. (2023). Revisiting the Determinants of Non-farm Labour Income in the
  Peruvian Andes. *The Journal of Development Studies*.
- Sayre, M. et al. (2017). You Can't Grow Potatoes in the Sky: Building
  Resilience in the Face of Climate Change in the Potato Park of Cuzco, Peru.
  *Culture, Agriculture, Food and Environment*.
- Tambet, H. y Stopnitzky, Y. (2021). Climate Adaptation and Conservation
  Agriculture among Peruvian Farmers. *American Journal of Agricultural
  Economics*.
- Tito, R. et al. (2018). Global climate change increases risk of crop yield
  losses and food insecurity in the tropical Andes. *Global Change Biology*.
- Visscher, A. M. et al. (2023). Traditional soil fertility management
  ameliorates climate change impacts on traditional Andean crops within
  smallholder farming systems. *Science of the Total Environment*.
- Yilmazkuday, H. (2025). El Niño, La Niña and Inflation.
  DOI 10.2139/ssrn.5014991.
- (2021). Impacto económico del cambio climático en cultivo de quinua orgánica
  en la Región del Altiplano: un enfoque ricardiano. *Revista de Investigaciones
  Altoandinas*.
