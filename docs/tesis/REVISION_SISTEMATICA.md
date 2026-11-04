# Propuesta de revisión sistemática

Protocolo para una revisión sistemática sobre el efecto de los shocks de El
Niño–Oscilación del Sur en los precios de alimentos, con énfasis en la escala
espacial de la evidencia.

Se rige por dos estándares, no uno: **PRISMA 2020** (Page et al., 2021) para el
reporte, y las **guías de MAER-Net** (Havránek et al., 2020; Cook et al., 2026)
para lo específico de economía. PRISMA solo no basta: fue escrito pensando en
ensayos clínicos y no cubre lo que una síntesis de evidencia económica necesita.

---

## 1. Un dato que condiciona todo el diseño

Antes del protocolo conviene conocer esto, porque cambia dónde hay que poner el
esfuerzo.

Bartoš et al. (2022) examinaron más de 68 000 metaanálisis con más de 700 000
estimaciones en medicina, ciencias ambientales, psicología y economía.
Encontraron que **los metaanálisis en economía son los más contaminados por
sesgo de selección de publicaciones** de los cuatro campos. Tras ajustar por ese
sesgo, la probabilidad mediana de que exista un efecto **cayó de 99,9 % a
29,7 %** en economía, y el tamaño del efecto mediano se redujo de d = 0,20 a
d = 0,07.

Léase despacio: en economía, **siete de cada diez efectos que la literatura da
por establecidos podrían no existir** una vez corregido el sesgo de publicación.

Dos consecuencias para esta propuesta:

1. **La literatura gris no es opcional.** Documentos de trabajo, informes
   institucionales y tesis deben incluirse deliberadamente, porque son
   justamente los que contienen los resultados no significativos que las
   revistas rechazan. Excluirlos garantiza reproducir el sesgo.
2. **La evaluación del riesgo de sesgo de publicación es parte central del
   trabajo**, no un apéndice (§8).

## 2. Alcance: dos opciones, y cuál conviene

| | **Opción A — Revisión sistemática cualitativa** | **Opción B — Revisión sistemática con metaanálisis** |
|---|---|---|
| Qué produce | Síntesis narrativa estructurada de la evidencia | Estimación cuantitativa del efecto medio y de sus moderadores |
| Estándar | PRISMA 2020 | PRISMA 2020 + MAER-Net |
| Esfuerzo | 10–12 semanas | 20–30 semanas |
| Requisito crítico | Ninguno adicional | Que los estudios reporten **efectos comparables con su error estándar**, lo que en esta literatura es dudoso: conviven elasticidades, respuestas a 1σ, dummies de evento y funciones impulso-respuesta |
| Riesgo | Bajo | Alto: puede descubrirse en la semana 12 que no hay suficientes estimaciones homogeneizables |
| **Recomendación** | **Para la tesis de pregrado** | Como producto posterior, o si la extracción revela ≥ 30 estimaciones comparables |

**Recomendación: empezar por A, con la extracción diseñada de modo que B sea
posible después sin repetir el trabajo.** La ficha de extracción de §7 ya
incluye los campos que un metaanálisis exigiría; si al terminar la extracción
hay material suficiente, B es un paso incremental y no un proyecto nuevo.

## 3. Pregunta de la revisión

Formulada con el esquema PECO adaptado a economía:

| Componente | Definición |
|---|---|
| **Población** | Mercados de alimentos, a cualquier escala: país, región, ciudad o mercado local |
| **Exposición** | Shocks de ENSO, medidos por índices oceánicos (ONI, ICEN, SOI, MEI) o por anomalías climáticas locales atribuibles al fenómeno |
| **Comparación** | Periodos o unidades sin shock, o condiciones normales |
| **Resultado** | Precios de alimentos: nivel, inflación, volatilidad o transmisión |

> **Pregunta principal.** ¿Cuál es el efecto de los shocks de ENSO sobre los
> precios de alimentos, y cómo varía ese efecto según la escala espacial a la
> que se mide?

> **Preguntas secundarias.** (a) ¿La evidencia distingue entre el Pacífico
> central y el Pacífico oriental? (b) ¿Qué proporción de los estudios estima a
> escala subnacional? (c) ¿Qué métodos predominan y cómo han cambiado?
> (d) ¿Hay señales de sesgo de publicación?

**Por qué esta pregunta y no otra.** La segunda pregunta secundaria **es la
brecha de la tesis**. Si la revisión confirma que la proporción de estudios
subnacionales es baja, la justificación deja de ser una afirmación del autor y
pasa a ser un hallazgo documentado y cuantificado. Esa es la razón de hacer la
revisión en lugar de una reseña narrativa.

## 4. Registro del protocolo

PROSPERO solo acepta revisiones con desenlaces en salud, de modo que **no es la
vía para esta**. La alternativa es **OSF Registries** (osf.io/registries), que
admite protocolos de ciencias sociales y emite un identificador con fecha.

Registrar antes de empezar no es trámite: es lo que impide la práctica de
ajustar los criterios de inclusión después de ver los resultados. Afonso et al.
(2023) sostienen que, dado lo difícil que es detectar el sesgo de publicación a
posteriori, **las estrategias preventivas —registro previo, declaración de
desviaciones, reporte de todos los hallazgos— son la solución más eficiente**.

## 5. Criterios de elegibilidad

**Se incluye** el estudio que cumple todo lo siguiente:

1. Es **empírico y cuantitativo**: estima una relación con datos, no la simula
   ni la postula.
2. La exposición es un **índice de ENSO o una anomalía climática** atribuida al
   fenómeno.
3. El resultado es un **precio de alimentos** o un índice que lo contenga.
4. Reporta un **efecto identificable**: coeficiente, elasticidad, variación
   porcentual o función impulso-respuesta.
5. Está en **español, inglés o portugués**.
6. Publicado entre **1990 y 2026**.

**Se excluye:**

1. Estudios **agronómicos o climatológicos sin resultado de precios** (miden
   rendimientos o lluvia, no precios). *Nota: para el marco teórico de la tesis
   sí sirven, pero no para esta revisión; conviene registrarlos aparte.*
2. Simulaciones o proyecciones **sin estimación empírica**.
3. Editoriales, notas de prensa y documentos de divulgación.
4. Estudios cuyo texto completo no sea accesible tras solicitarlo al autor.

**Se incluye deliberadamente literatura gris:** documentos de trabajo de bancos
centrales y organismos multilaterales, informes técnicos y tesis de posgrado.
Por el motivo de §1.

## 6. Fuentes de información y estrategia de búsqueda

### 6.1 Fuentes

| Tipo | Fuentes |
|---|---|
| Bases bibliográficas | Scopus, Web of Science, EconLit, ScienceDirect, JSTOR |
| Economía específicas | RePEc/IDEAS, NBER, SSRN |
| **Iberoamericanas** | **SciELO, Redalyc, Latindex** |
| **Tesis peruanas** | **ALICIA (CONCYTEC) y RENATI (SUNEDU)** |
| Institucionales | BCRP, BID, CEPAL, FAO, FMI, Banco Mundial, IFPRI |
| Complementaria | Google Scholar (primeras 200 entradas) y **búsqueda en las referencias de los estudios incluidos** |

> **Las dos filas en negrita son las que una búsqueda convencional omite, y son
> decisivas aquí.** Una estrategia solo en inglés y solo en Scopus dejaría fuera
> buena parte de la evidencia latinoamericana y toda la producción de tesis
> peruanas, que es justamente la evidencia regional que la tesis necesita. Ese
> sesgo idiomático es un defecto frecuente y perfectamente evitable.

### 6.2 Cadenas de búsqueda

**Bases en inglés** (adaptar la sintaxis de truncamiento a cada base):

```
("El Nino" OR "El Niño" OR "La Nina" OR "La Niña" OR ENSO
  OR "Southern Oscillation" OR "Oceanic Nino Index" OR "coastal El Nino"
  OR "sea surface temperature anomal*")
AND
("food price*" OR "food inflation" OR "consumer price*" OR "price index"
  OR "agricultural price*" OR "price transmission" OR "commodity price*")
AND
(empiric* OR estimat* OR panel OR regression OR "impulse response"
  OR econometric*)
```

**Bases en español y portugués:**

```
("El Niño" OR "La Niña" OR ENSO OR "Niño costero" OR "Oscilación del Sur"
  OR "anomalía climática" OR "choque climático")
AND
("precios de alimentos" OR "inflación de alimentos" OR "índice de precios"
  OR "precios agrícolas" OR "transmisión de precios" OR "preços dos alimentos")
```

**Cadena específica para repositorios de tesis peruanas** (que suelen tener
buscadores pobres, por lo que conviene buscar por términos sueltos):

```
"Niño costero"   ·   "fenómeno El Niño" precios   ·   ENSO inflación
"shock de oferta" clima   ·   ICEN economía
```

Cada búsqueda se registra con **fecha, base, cadena exacta y número de
resultados**, en una bitácora que va como anexo. PRISMA 2020 lo exige y sin
ella la revisión no es replicable.

## 7. Selección y extracción

### 7.1 Proceso de selección

Cuatro fases del diagrama de flujo PRISMA: identificación, cribado por título y
resumen, elegibilidad por texto completo, e inclusión. Se reporta el número de
registros en cada fase y **el motivo de cada exclusión en la fase de texto
completo**.

> **Una debilidad que hay que declarar, no esconder.** PRISMA recomienda **dos
> revisores independientes**. Una tesis de pregrado normalmente tiene uno.
> Mitigación: que el asesor criba de forma independiente **una muestra
> aleatoria del 20 %** y se reporte el **índice kappa de Cohen** como medida de
> concordancia. Es menos que el estándar, es verificable, y es mucho mejor que
> no decir nada.

### 7.2 Ficha de extracción

| Campo | Contenido |
|---|---|
| Identificación | Autores, año, título, tipo de publicación, revista o institución, DOI |
| Ámbito | País o países, escala espacial (nacional, subnacional, mercado), periodo |
| Exposición | Índice usado (ONI, ICEN, SOI, MEI, anomalía local), región oceánica, frecuencia |
| Resultado | Variable de precio, nivel de desagregación, fuente del dato |
| Método | Estimador, especificación, tratamiento de la endogeneidad, tipo de errores estándar |
| **Efecto** | **Signo, magnitud, unidad, error estándar o estadístico t, número de observaciones** |
| Heterogeneidad | ¿Reporta efectos por región, cultivo o estación? |
| Dinámica | Horizonte del efecto máximo, persistencia |
| Calidad | Exogeneidad declarada, efectos fijos, pruebas de robustez, replicabilidad |
| Declaraciones | Financiamiento, conflicto de interés, disponibilidad de datos y código |

La fila en negrita es la que habilita la Opción B. **Si no se extrae el error
estándar desde el inicio, un metaanálisis posterior obliga a releer todos los
estudios.**

## 8. Evaluación del riesgo de sesgo

### 8.1 A nivel de estudio

No existe para economía observacional un instrumento equivalente al de Cochrane
para ensayos clínicos. **La convención en economía no es puntuar calidad sino
codificar características del estudio y tratarlas como moderadores** en la
síntesis (Havránek et al., 2020). Se adopta esa convención, y las
características a codificar son: estrategia de identificación, inclusión de
efectos fijos, tratamiento de la dependencia temporal y transversal, frecuencia
de los datos, escala espacial y tipo de publicación.

### 8.2 Riesgo de sesgo de publicación

Es la parte sustantiva, por §1. Se aplican estas reglas:

- **Usar varias pruebas, nunca una.** Lin et al. (2018), sobre 28 655
  metaanálisis de la biblioteca Cochrane, encuentran **concordancia débil o
  moderada entre las pruebas** y concluyen que no debe confiarse en una sola.
- **No equiparar asimetría con sesgo de publicación.** Sterne et al. (2011)
  advierten que la asimetría del gráfico de embudo tiene otras causas posibles,
  entre ellas la heterogeneidad entre estudios.
- **Tratar el procedimiento FAT-PET-PEESE con cautela.** Alinaghi y Reed (2018)
  muestran que funciona bien bajo efectos fijos, pero que **se vuelve poco
  fiable cuando hay heterogeneidad de efectos entre y dentro de los estudios**,
  que es precisamente la situación de esta literatura.
- **Considerar modelos de selección y el enfoque bayesiano robusto** como
  complemento (Bartoš et al., 2022).
- **Modelar la no independencia.** Un estudio de economía reporta muchas
  estimaciones. Nakagawa et al. (2023) muestran que ignorar esa dependencia es
  un error extendido y recomiendan **modelos multinivel** en lugar de los de
  efectos aleatorios habituales.
- **Preferir la expresión «riesgo de sesgo de publicación»** en lugar de
  afirmar que el sesgo existe (Afonso et al., 2023).

## 9. Síntesis

**Opción A.** Síntesis narrativa estructurada por: escala espacial, índice
usado, signo y magnitud del efecto, horizonte y región. Se acompaña de tablas
de evidencia y de **un gráfico de burbujas de escala espacial contra año de
publicación**, que es la figura que respondería visualmente la pregunta
secundaria (b) y, por tanto, documentaría la brecha de la tesis.

**Opción B, si procede.** Metaanálisis multinivel con el efecto parcial
correlacionado como medida homogeneizada, metarregresión sobre los moderadores
codificados en §8.1, y el conjunto de pruebas de sesgo de publicación de §8.2.

## 10. Uso de inteligencia artificial y su declaración

Esto no es accesorio y conviene no omitirlo. MAER-Net adoptó en 2026 principios
específicos para el uso de IA en metaanálisis de economía (Cook et al., 2026) y
actualizó sus guías de reporte en consecuencia. **Si la revisión usa asistencia
de IA en la búsqueda, el cribado o la extracción, debe declararlo**, indicando
en qué fases, con qué herramienta y con qué verificación humana.

Texto sugerido para el apartado de métodos, que debe ajustarse a lo que
realmente se haga:

> Se empleó asistencia de inteligencia artificial en la fase de búsqueda
> exploratoria y en la identificación preliminar de literatura relevante. Toda
> referencia identificada por esa vía fue verificada manualmente contra la
> fuente primaria antes de su inclusión. El cribado por criterios de
> elegibilidad, la extracción de datos y la síntesis fueron realizados por el
> autor. Se siguen las guías de reporte de MAER-Net actualizadas para el uso de
> IA (Cook et al., 2026).

**Advertencia pertinente para este proyecto.** Parte de la literatura reunida
hasta ahora provino de búsquedas asistidas por IA, y **varias referencias no
han podido verificarse contra la fuente primaria** porque la red bloqueaba los
dominios. Esa verificación es un requisito, no una formalidad: una revisión
sistemática que cite lo que no leyó es una revisión inválida.

## 11. Cronograma, opción A

| Semanas | Actividad | Producto |
|---|---|---|
| 1 | Afinar la pregunta y los criterios; registrar el protocolo en OSF | Protocolo registrado con fecha |
| 2–3 | Ejecutar las búsquedas en todas las fuentes; bitácora | Registros identificados |
| 4 | Eliminar duplicados; cribado por título y resumen | Diagrama PRISMA, fases 1 y 2 |
| 5 | Cribado independiente del asesor sobre el 20 %; kappa | Medida de concordancia |
| 6–7 | Lectura a texto completo y decisión de elegibilidad | Diagrama PRISMA completo |
| 8–9 | Extracción de datos con la ficha de §7.2 | Matriz de evidencia |
| 10 | Codificación de características y riesgo de sesgo | Tabla de moderadores |
| 11 | Síntesis narrativa y figuras | Capítulo de resultados |
| 12 | Redacción, lista de verificación PRISMA, anexos | Documento final |

## 12. Limitaciones previsibles

1. **Un solo revisor**, mitigado parcialmente (§7.1).
2. **Sesgo idiomático residual**: tres idiomas es más que el estándar habitual,
   pero deja fuera la literatura en otros.
3. **Heterogeneidad de medidas del efecto**, que es lo que podría impedir la
   Opción B.
4. **Acceso**: parte de la literatura gris institucional no está indexada y
   depende de la navegación directa en los repositorios.
5. **Esta revisión no resuelve el problema de datos de la tesis.** Documenta la
   brecha; no confirma que existan los indicadores. Son tareas distintas y la
   segunda sigue pendiente.

## 13. Referencias

Afonso, J., Ramirez-Campillo, R., Clemente, F. M., Büttner, F. C. y Andrade, R.
(2023). The perils of misinterpreting and misusing "publication bias" in
meta-analyses: An education review on funnel plot-based methods. *Sports
Medicine*.

Alinaghi, N. y Reed, W. R. (2018). Meta-analysis and publication bias: How well
does the FAT-PET-PEESE procedure work? *Research Synthesis Methods*.

Bartoš, F., Maier, M., Wagenmakers, E.-J., Nippold, F., Doucouliagos, H.,
Ioannidis, J. P. A., Otte, W. M., Sladekova, M., Deresssa, T. K., Bruns, S. B.,
Fanelli, D. y Stanley, T. D. (2022). Footprint of publication selection bias on
meta-analyses in medicine, environmental sciences, psychology, and economics.
*Research Synthesis Methods*.

Cook, N., Havránek, T., Irsova, Z., Stanley, T. D. y Doucouliagos, H. (2026).
Reporting guidelines for meta-analysis in economics—Updated for AI. *Journal of
Economic Surveys*.

Havránek, T., Stanley, T. D., Doucouliagos, H., Bom, P., Geyer-Klingeberg, J.,
Iwasaki, I., Reed, W. R., Rost, K. y van Aert, R. C. M. (2020). Reporting
guidelines for meta-analysis in economics. *Journal of Economic Surveys*.

Lin, L., Chu, H., Murad, M. H., Hong, C., Qu, Z., Cole, S. R. y Chen, Y.
(2018). Empirical comparison of publication bias tests in meta-analysis.
*Journal of General Internal Medicine*.

Nakagawa, S., Yang, Y., Macartney, E. L., Spake, R. y Lagisz, M. (2023).
Quantitative evidence synthesis: A practical guide on meta-analysis,
meta-regression, and publication bias tests for environmental sciences.
*Environmental Evidence*.

Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C.,
Mulrow, C. D., Shamseer, L., Tetzlaff, J. M., Akl, E. A., Brennan, S. E.,
Chou, R., Glanville, J., Grimshaw, J. M., Hróbjartsson, A., Lalu, M. M., Li, T.,
Loder, E. W., Mayo-Wilson, E., McDonald, S., … Moher, D. (2021). The PRISMA
2020 statement: An updated guideline for reporting systematic reviews. *BMJ*,
*372*, n71. https://doi.org/10.1136/bmj.n71

Stanley, T. D., Doucouliagos, H., Giles, M., Heckemeyer, J. H., Johnston,
R. J., Laroche, P., Nelson, J. P., Paldam, M., Poot, J., Pugh, G., Rosenberger,
R. S. y Rost, K. (2013). Meta-analysis of economics research reporting
guidelines. *Journal of Economic Surveys*.

Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., Terrin, N., Jones, D. R.,
Lau, J., Carpenter, J., Rücker, G., Harbord, R. M., Schmid, C. H., Tetzlaff, J.,
Deeks, J. J., Peters, J., Macaskill, P., Schwarzer, G., Duval, S., Altman,
D. G., Moher, D. y Higgins, J. P. T. (2011). Recommendations for examining and
interpreting funnel plot asymmetry in meta-analyses of randomised controlled
trials. *BMJ*, *343*, d4002. https://doi.org/10.1136/bmj.d4002

Yepes-Núñez, J. J., Urrútia, G., Romero-García, M. y Alonso-Fernández, S.
(2021). Declaración PRISMA 2020: una guía actualizada para la publicación de
revisiones sistemáticas. *Revista Española de Cardiología*, *74*(9), 790–799.
https://doi.org/10.1016/j.recesp.2021.06.016
