# ¿Incapacidad, disuasión o etiquetado? Tres explicaciones de la inversión no ejecutada en una universidad pública

Diseño de investigación — UNSAAC, 2012–2026

Alexander Torres Uchupe — UNSAAC, Cusco
4 de noviembre de 2026

**Estado: diseño, no resultados.** No contiene estimaciones. Cada número que el
diseño debe producir aparece como marcador `[...]`; la lista completa está en la
sección 10.

---

## 1. La pregunta

La UNSAAC devenga alrededor de un tercio de su presupuesto de inversión año tras
año, con perfiles de canon muy distintos. La lectura corriente atribuye eso a la
burocracia. El diagnóstico que hice antes la atribuía a la gestión. Las dos
respuestas comparten un defecto: suponen la explicación en lugar de contrastarla
contra alternativas que predicen el mismo resultado.

Hay tres explicaciones compatibles con un tercio de ejecución, y distinguirlas
cambia la recomendación de política por completo:

- **T1, incapacidad.** La organización no puede convertir presupuesto en obra al
  ritmo que el presupuesto exige. El costo administrativo de ejecutar es convexo
  y la capacidad es un acervo que se mueve despacio.
- **T2, disuasión por control.** No ejecutar es la respuesta racional del
  funcionario cuando el procedimiento más transparente es también el que acumula
  más pasos auditables y más responsabilidad personal. Gerardino, Litschig y
  Pomeranz (2024) documentan el mecanismo en Chile: tras una auditoría caen el
  uso de subastas y la competencia entre proveedores, porque las subastas
  soportan más del doble de controles y generan el doble de infracciones
  detectadas.
- **T3, cuña de etiquetado.** El canon solo puede financiar inversión y no puede
  pagar planilla. Si la presión de gasto está en la planilla, el valor que la
  organización asigna a un sol etiquetado es menor que el que asigna a un sol
  fungible, y el dinero se acumula sin usar.

> **Pregunta de investigación.** ¿Qué parte de la inversión no ejecutada se
> explica por congestión de la capacidad administrativa, qué parte por la
> disuasión que ejerce el régimen de control, y qué parte por el etiquetado
> legal de la renta?

Las tres compiten en el mismo diseño. El trabajo no defiende ninguna.

## 2. Lo que la pregunta exige y lo que el caso permite

La unidad de análisis es la UNSAAC: 45 escuelas profesionales, la sede del Cusco
y seis filiales. Esa elección tiene un costo y una ventaja, y conviene declarar
las dos en la introducción del artículo.

**El costo.** Con una sola institución hay una sola serie de canon. No se puede
estimar la elasticidad del gasto de capital respecto de la renta transferida,
que es el parámetro que pediría un lector interesado en la maldición de los
recursos. Ese trabajo exige el panel nacional de universidades y queda fuera.

**La ventaja.** Dentro de una institución quedan fijos el rector, la ley de
contrataciones, el régimen docente, el sistema de inversión pública y la oficina
de planificación. Todo lo que varía entre unidades y entre procesos varía con
esas cosas constantes. Las tres teorías dejan huellas distintas en esa variación
interna, y dos de ellas se contrastan mejor aquí que en un panel nacional,
porque exigen datos de expediente que solo se consiguen con acceso a la propia
institución.

**La limitación lógica que hay que respetar.** Un mal desempeño común a todas
las unidades identifica algo común a la organización, y la conducción central es
parte de ese algo. Por tanto, dentro de la UNSAAC no puedo separar la conducción
central de la norma externa, y no afirmaré haberlo hecho. Lo que sí puedo
separar es la congestión de la disuasión y del etiquetado, que es la pregunta de
la sección 1.

## 3. Marco

Una unidad $u$ de la universidad ejecuta un conjunto de proyectos y trámites.
Convertir presupuesto en obra exige insumo administrativo: formular el
expediente, aprobarlo, certificar, convocar, contratar y supervisar. Represento
el costo de ejecutar $I$ soles como $c(I; A_u, r)$, con tres propiedades.

$c$ es **convexo en $I$**: la unidad atiende varios expedientes con la misma
gente, y un expediente adicional desplaza atención de los demás. Es decreciente
en $A_u$, el acervo de capacidad administrativa de la unidad. Y es creciente en
$r$, el riesgo de responsabilidad personal que el procedimiento impone al
funcionario que firma.

La universidad dispone de recursos fungibles $R^O$ y etiquetados $R^C$, con
$w\,l \le R^O$ —el canon no paga remuneraciones— y $I \le R^C + S_{t-1}$, donde
$S_{t-1}$ es el saldo de canon arrastrado.

Cada teoría es una restricción distinta operando en el mismo problema:

| | Qué aprieta | Parámetro |
| :-- | :-- | :-- |
| T1 | la convexidad de $c$ frente a la carga simultánea | $\partial^2 c/\partial I^2 > 0$ |
| T2 | el riesgo personal del procedimiento | $\partial c/\partial r > 0$ |
| T3 | la cuña entre valores sombra, $\lambda^C < \lambda^O$ | etiquetado con planilla activa |

De ahí salen predicciones que no coinciden:

| Observable | T1 | T2 | T3 |
| :-- | :-- | :-- | :-- |
| Avance de un proyecto cuando sube la carga de *otros* proyectos de su misma unidad | cae | sin efecto | sin efecto |
| Tras una acción de control sobre la unidad | sin efecto | cae | sin efecto |
| Composición de procedimientos tras una acción de control | sin cambio | se desplaza a los menos auditables | sin cambio |
| Número de postores tras una acción de control | sin cambio | cae | sin cambio |
| Inversión con canon frente a inversión con recursos ordinarios, misma unidad y año | sin diferencia | sin diferencia | la del canon avanza menos |
| Saldos acumulados con gasto corriente racionado | moderados | moderados | grandes |
| Gasto en personal administrativo y consultoría cuando sube la renta | sube con rezago | no sube | no sube |
| Etapa donde se detiene el expediente | donde falta gente | donde hay firma con responsabilidad | no llega a programarse |

## 4. Hipótesis

- **H1 (T1).** Un proyecto adicional a cargo de la misma unidad ejecutora alarga
  el ciclo de los demás en `[MAGNITUD: __ días]`, y el efecto es no lineal:
  muerde a partir de `[UMBRAL: __ proyectos simultáneos]`.
- **H2 (T2).** Tras una acción de control, la participación de procedimientos
  competitivos en la unidad observada cae `[COEFICIENTE: __]` puntos frente a las
  no observadas, y el número de postores cae `[COEFICIENTE: __]`.
- **H3 (T2).** El tiempo de espera se concentra en las etapas que exigen firma
  con responsabilidad personal, no en las que exigen trabajo técnico.
- **H4 (T3).** A igual unidad, año y tipo de obra, la inversión financiada con
  canon avanza `[COEFICIENTE: __]` menos que la financiada con recursos
  ordinarios.
- **H5 (T3).** De la brecha de absorción, `[MAGNITUD: __ %]` corresponde a
  presupuesto incorporado en el segundo semestre y `[MAGNITUD: __ %]` a
  presupuesto disponible desde el mes 00 y no devengado.
- **H6 (matriz).** El tiempo de ciclo responde a la interacción entre capacidad
  de la unidad e intensidad de regulación externa del proceso:
  `[COEFICIENTE: __]`, e.e. `[E.E.: __]`.

## 5. Datos

### 5.1 Fuentes

| Fuente | Qué aporta | Nivel |
| :-- | :-- | :-- |
| MEF, Datos Abiertos, SIAF | PIA, PIM, certificado, comprometido, devengado, girado, con el mes de cada movimiento | pliego × mes × fuente × proyecto |
| Invierte.pe, Banco de Inversiones | CUI, viabilidad, costo actualizado, avance, unidad formuladora y ejecutora | proyecto |
| SEACE / OSCE, datos abiertos | tipo de procedimiento, fechas, postores, adjudicación, contratos | procedimiento |
| Informes del OCI de la UNSAAC | acciones de control, unidad y proceso observado, fecha, recomendaciones | informe |
| Expedientes de la UNSAAC | fechas por etapa, pasos, firmas, subsanaciones | expediente |
| TUPA y reglamentos internos | base normativa de cada requisito | requisito |
| PAP y planillas de la UNSAAC | dotación por unidad, plazas autorizadas | unidad × año |
| Compendio Estadístico y Unidad de Estadística | matrícula, egresados, graduados por escuela | escuela × año |

Las seis primeras son públicas. Las dos últimas están publicadas pero
dispersas. Los expedientes exigen trabajo de campo.

### 5.2 La variable dependiente correcta

La tasa de ejecución sobre PIM es una mala variable dependiente y la descarto
como objeto a explicar. El PIM lo decide en parte la propia universidad:
incorporar saldos de ejercicios anteriores infla el denominador, de modo que
ejecutar mal un año eleva el PIM del siguiente y vuelve a producir una tasa
baja. La tasa tiene autocorrelación negativa con la ejecución pasada por
construcción. La comparación entre 30,28% en 2022 y 36,25% en 2026 no sostiene,
por eso, la conclusión de que la capacidad de absorción no cambió.

Uso en su lugar:

- **Para T1:** días de ciclo por etapa y avance financiero mensual del proyecto.
- **Para T2:** participación de procedimientos competitivos y número de postores.
- **Para T3:** devengado de inversión por fuente de financiamiento y el acervo de
  saldo no ejecutado, con la identidad $S_t = S_{t-1} + T_t - D_t + \text{ajustes}$.

### 5.3 El problema de medición que hay que resolver primero

El expediente previo encontró que el canon de la UNSAAC parece haber cambiado de
rubro: recursos determinados cayó a S/ 1,44 millones mientras donaciones y
transferencias llegó a S/ 110,37 millones, cifra cercana al canon anualizado. Es
una inferencia por coincidencia de magnitudes, no un dato.

Para H4 el asunto es crítico, porque la variable que clasifica cada proyecto
como financiado con canon es precisamente el rubro. Si la etiqueta se mueve, la
prueba de T3 se cae. La solución es no depender de la clasificación del gasto:
identificar el financiamiento por el lado del ingreso, con el canon transferido
que publica el MEF, y por el expediente de cada proyecto, que declara su fuente.
Reconciliar las dos es la primera tarea y es condición para H4 y H5.

### 5.4 Fechar cada sol: una variable que el SIAF permite y nadie usa

El archivo de gasto del MEF no es una foto anual. Cada fila es el movimiento del
mes: el PIM inicial aparece en el mes "00" y cada modificación posterior en el
mes en que se incorporó, y el devengado es flujo mensual. Entonces se puede
fechar cada sol del presupuesto.

Construyo, por año,

$$\tau_t \;=\; \frac{\sum_{m>6} \Delta \mathrm{PIM}_{tm}}{\mathrm{PIM}_t},$$

la fracción del presupuesto de inversión incorporada en el segundo semestre, y
con ella descompongo la brecha en dos partes de interpretación distinta: el
dinero que llegó tarde, que ningún procedimiento alcanza a devengar en
diciembre, y el dinero que estuvo disponible desde enero y no se ejecutó. La
segunda parte es la medida limpia del problema interno, y es la que debe ir al
numerador de cualquier afirmación sobre gestión. Sale íntegramente del SIAF, sin
pedir información a nadie. El script `investigacion/panel_universidades.py`
extrae el pliego y conserva el mes para esto.

## 6. Identificación

### 6.1 Diseño A — congestión: la prueba de T1

Nivel proyecto × mes. Estimo

$$y_{jt} \;=\; \alpha_j + \gamma_t + \beta\,L^{-j}_{u(j),t} + X_{jt}'\delta + \varepsilon_{jt},$$

donde $y_{jt}$ es el avance financiero del proyecto $j$ en el mes $t$ y
$L^{-j}_{u(j),t}$ es la carga de la unidad que lo ejecuta, medida como número y
monto de los **otros** proyectos activos a su cargo. Efectos fijos de proyecto y
de mes, y efectos de unidad por año.

La identificación viene de que la carga que enfrenta $j$ la determina el
calendario de los demás proyectos, que no depende de la dificultad propia de
$j$. La amenaza es que ese calendario responda al ciclo del canon, común a
todos: lo atajo instrumentando la carga efectiva con la carga **programada** al
inicio del año, fijada antes de observar los retrasos.

$\beta < 0$ y creciente en magnitud con el nivel de carga es la convexidad de
$c$ medida dentro de la institución. Reporto el efecto en días adicionales de
ciclo por proyecto adicional, no en estrellas.

### 6.2 Diseño B — control: la prueba de T2

Dos márgenes, el segundo más informativo que el primero.

**Evento de control.** Las acciones del OCI llegan a unidades y procesos
distintos en fechas distintas. Estimo efectos por grupo y período con el
estimador de Callaway y Sant'Anna (2021), con estudio de evento para verificar
tendencias previas, y contrasto con efectos fijos de dos vías, cuyo sesgo con
efectos heterogéneos documentan de Chaisemartin y D'Haultfœuille (2020).

**Composición de procedimientos.** Esta es la prueba que distingue T2 de todo lo
demás. Mido la participación de procedimientos competitivos —licitación y
concurso público— frente a los menos auditables —adjudicación simplificada,
contratación directa y compras por debajo del umbral— y el número de postores.
T1 y T3 no predicen ningún cambio de composición. T2 predice un desplazamiento
hacia el procedimiento que expone menos al funcionario, que es exactamente lo
que encuentran Gerardino, Litschig y Pomeranz (2024).

La amenaza es la selección: se audita donde ya hay problemas. Uso las
tendencias previas y, donde sea posible, la parte de la selección que sigue
reglas del plan anual de control y no la discrecionalidad del auditor.

### 6.3 Diseño C — etiquetado: la prueba de T3

Comparo, dentro de la UNSAAC, proyectos financiados con canon y proyectos
financiados con recursos ordinarios o recaudados directamente:

$$y_{jt} \;=\; \alpha_{u(j),t} + \delta\,\mathrm{Canon}_j + X_{jt}'\theta + \varepsilon_{jt},$$

con efectos fijos de unidad por año que absorben todo lo común a la unidad en el
período: el rector, la norma, el clima institucional y la capacidad. $\delta$
captura el efecto del etiquetado, no la diferencia de contexto. Controlo por
tipo de obra, función y tramo de monto, porque un laboratorio y una obra civil no
tienen la misma función de costo administrativo.

Añado la descomposición de la brecha de la sección 5.4 y la identidad de saldos,
y pruebo fungibilidad: si al subir el canon la universidad desplaza recursos
ordinarios de capital hacia gasto corriente, el etiquetado se elude en parte y
$\delta$ subestima la cuña.

### 6.4 La matriz de cuatro cuadrantes, estimada

La matriz se queda como dispositivo de presentación. Lo que se estima es su
interacción. Nivel unidad × proceso:

$$\ln T_{up} \;=\; \mu + \beta_1 A_u + \beta_2 E_p + \beta_3 (A_u \times E_p) + \varepsilon_{up},$$

con $T_{up}$ el tiempo de ciclo, $A_u$ la capacidad de la unidad y $E_p$ la
intensidad de regulación externa del proceso.

Dos exigencias de medición, que son las que hacen creíble la matriz:

**$A_u$ no puede ser la dotación efectiva**, porque asignar personal es una
decisión de gestión y entraría contaminada. Uso dotación anterior al período y
plazas autorizadas en el PAP, no las ocupadas.

**$E_p$ no puede ser mi juicio.** Codifico cada paso de cada proceso según la
norma que lo obliga, distinguiendo norma nacional de reglamento interno. La
codificación la hacen dos personas por separado y reporto el estadístico de
acuerdo. Sin eso, la variable clave del trabajo es una opinión.

$\beta_3$ es el contenido empírico de la matriz: dice si la capacidad rinde más
donde la regla deja margen. Los cuadrantes son el gráfico de ese coeficiente.

### 6.5 Descomposición de la varianza del tiempo de ciclo

Complemento de 6.4, sobre la muestra de expedientes:

$$\operatorname{Var}(\ln T_j) = \operatorname{Var}(\text{unidad}) + \operatorname{Var}(\text{proceso}) + \operatorname{Var}(\text{etapa}) + \operatorname{Var}(\text{año}) + \text{residuo}.$$

Dos advertencias sobre cómo se lee. La varianza entre unidades es una **cota
superior** de lo atribuible a su conducción, nunca un punto: las unidades
difieren en el tipo de expediente que procesan, y aun condicionando queda
heterogeneidad no observada. Y la parte común a todas las unidades no identifica
la norma: identifica lo común a la organización, que incluye la conducción
central. Best, Hjort y Szakonyi (2023) atribuyen 39% de la variación de precios
en 16 millones de compras públicas rusas a los funcionarios y las organizaciones
que las gestionan; con los nombres de los responsables en el SEACE podría
intentarse la parte individual, pero exige seguir movilidad entre unidades y la
dejo como extensión.

### 6.6 Las preguntas de identificación

1. **¿Qué mecanismo generó la dispersión de cada variable explicativa?** La
   carga, el calendario de otros proyectos. El control, la programación del plan
   anual de control. El etiquetado, la ley del canon.
2. **¿Qué hay en el error?** Capacidad no observada de la unidad, rotación de
   decanos, conflictividad, complejidad del expediente.
3. **¿Por qué el error no correlaciona con la explicativa?** En A, porque la
   dificultad de un proyecto no determina el calendario de los demás. En C,
   porque los efectos fijos de unidad por año absorben lo común y el etiquetado
   lo fija una ley nacional. En B es donde el supuesto es más débil, y por eso
   la prueba de composición pesa más que la de nivel.
4. **¿Instrumento o control?** La capacidad entra como control e interacción,
   nunca como instrumento: la elige la organización.
5. **¿De dónde sale cada número?** En A, de la variación temporal de carga dentro
   de proyecto. En B, de la diferencia entre unidades observadas y no observadas.
   En C, de la comparación entre fuentes dentro de unidad y año.
6. **¿Puede ir la causalidad al revés?** En A sí: un proyecto que se atrasa
   acumula carga. De ahí la carga programada como instrumento.
7. **¿Qué controles deben estar?** Tipo de obra, monto, función, matrícula de la
   escuela. Fuera: el PIM y el gasto corriente contemporáneos, resultado de las
   mismas decisiones.

## 7. Amenazas y lo que haré con ellas

**Selección de las auditorías.** Es la amenaza principal de T2. Tendencias
previas, y apoyarme en la composición de procedimientos más que en el nivel.

**Reclasificación de fuentes.** Amenaza principal de T3. Identificar el
financiamiento por ingreso y por expediente, no por rubro de gasto.

**Pocas unidades.** Cuarenta y cinco escuelas y seis filiales, con pocos años.
Inferencia por *bootstrap* de agrupamiento salvaje y declaración honesta de
potencia.

**Costo de campo y potencia.** Medir ocho procesos en 45 unidades con 30
expedientes cada uno son más de diez mil expedientes, lo que no es viable.
Propongo un piloto de 30 expedientes en tres unidades y dos procesos para
estimar los componentes de varianza, calcular con eso el tamaño por celda y
recién entonces fijar la muestra. `[MDE: __]`, `[N por celda: __]`.

**Comparabilidad entre unidades.** Las escuelas no procesan los mismos
expedientes. Condicionar por tipo de trámite antes de leer cualquier varianza.

**Reactividad.** Pedir expedientes a una universidad con licencia por vencer
puede cambiar el comportamiento que se mide. Tomar las fechas de registros ya
existentes antes de anunciar el estudio.

## 8. Lo que el diseño debe producir

**Tabla 1.** Efecto de la carga de la unidad sobre el avance del proyecto, en
días por proyecto adicional. `[COEFICIENTE: __]`, `[E.E.: __]`.

**Tabla 2.** Efecto de la acción de control sobre nivel de ejecución,
composición de procedimientos y número de postores. `[COEFICIENTE: __]` cada uno.

**Tabla 3.** Diferencia de avance entre inversión con canon y con recursos
ordinarios, misma unidad y año. `[COEFICIENTE: __]`.

**Tabla 4.** Descomposición de la brecha: dinero incorporado tarde frente a
dinero disponible y no ejecutado. `[MAGNITUD: __ % y __ %]`.

**Tabla 5.** La matriz estimada: capacidad, regulación externa y su interacción.
`[COEFICIENTE: __]`.

**Figura 1.** Canon transferido y devengado de inversión por año, con la brecha
sombreada.

**Figura 2.** Estudio de evento de la acción de control sobre la composición de
procedimientos.

El criterio de juicio es el tamaño. Reporto cada efecto en días y en soles, y
declaro antes de estimar qué consideraría relevante: que la congestión explique
menos de una décima parte del ciclo dejaría T1 como mecanismo menor, por
estadísticamente significativa que resulte.

## 9. Qué queda fuera

No estimo la elasticidad del gasto de capital respecto de la renta: exige el
panel nacional. No separo la conducción central de la norma externa, por el
argumento de la sección 2. No mido el retorno social de la inversión
universitaria. No evalúo si el etiquetado del canon es buena política, porque no
identifico el retorno de su mejor uso alternativo.

## 10. Pendientes de completar

**Marcadores:** todos los `[COEFICIENTE: __]`, `[E.E.: __]`, `[MAGNITUD: __]`,
`[UMBRAL: __]`, `[MDE: __]` y `[N por celda: __]` de las secciones 4, 7 y 8.

**Datos por verificar en fuente primaria.** Los hosts del Estado peruano están
bloqueados en el entorno donde escribí esto, así que nada de lo que sigue está
verificado por mí:

1. Ejecución de inversión al 31-08-2026: 36,25%, S/ 33,45 de S/ 92,28 millones.
2. Ejecución de los 37 proyectos de 2022: 30,28%; canon financiando 98,21%.
3. Gasto rígido: 44,21% en 2020 y 56,73% en 2026.
4. Reclasificación del canon a donaciones y transferencias: es inferencia.
5. Serie de canon 2012–2025 del expediente previo: es **estimación** a partir de
   dos anclas. No usarla como variable explicativa.
6. Artículo exacto de la Ley 30220 que fija el mínimo de 25% de docentes a
   tiempo completo: las fuentes secundarias discrepan entre los artículos 83 y
   96, y la Ley 32551 introdujo excepciones y amplió plazos.
7. Texto vigente del numeral 6.2 del artículo 6 de la Ley 27506, modificado por
   la Ley 28077, y el límite de 50% para infraestructura.
8. `[CITA PENDIENTE: literatura peruana sobre capacidad de ejecución de
   inversión pública subnacional]`.
9. `[FUENTE DE DATOS: existencia y granularidad de los informes del OCI de la
   UNSAAC con unidad y fecha]` — sin esto, el diseño B no es viable.
10. `[FUENTE DE DATOS: nombres de columna de pliego, fuente, rubro y tipo de
    actividad en el CSV del SIAF]` — confirmar con
    `python3 investigacion/panel_universidades.py --inspeccionar`.

## Referencias

Best, M. C., Hjort, J. y Szakonyi, D. (2023). Individuals and Organizations as
Sources of State Effectiveness. *American Economic Review*, 113(8), 2121–2167.

Callaway, B. y Sant'Anna, P. H. C. (2021). Difference-in-Differences with
Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230.

Caselli, F. y Michaels, G. (2013). Do Oil Windfalls Improve Living Standards?
Evidence from Brazil. *American Economic Journal: Applied Economics*, 5(1),
208–238.

de Chaisemartin, C. y D'Haultfœuille, X. (2020). Two-Way Fixed Effects
Estimators with Heterogeneous Treatment Effects. *American Economic Review*,
110(9), 2964–2996.

Gerardino, M. P., Litschig, S. y Pomeranz, D. (2024). Distortion by Audit:
Evidence from Public Procurement. *American Economic Journal: Applied
Economics*, 16(4), 71–108.

Hines, J. R. y Thaler, R. H. (1995). Anomalies: The Flypaper Effect. *Journal of
Economic Perspectives*, 9(4), 217–226.

Loayza, N. y Rigolini, J. (2016). The Local Impact of Mining on Poverty and
Inequality: Evidence from the Commodity Boom in Peru. *World Development*, 84,
219–234.

Murillo, D. y Sardon, S. (2024). Commodity Booms, Local State Capacity, and
Development. arXiv:2411.09586.

Pebe, C., Radas, N. y Torres, J. (2017). El canon minero y el ciclo político
presupuestal en las municipalidades distritales del Perú, 2002-2011. *Revista
CEPAL*, 123, 167–185.

Rasul, I. y Rogger, D. (2018). Management of Bureaucrats and Public Service
Delivery: Evidence from the Nigerian Civil Service. *Economic Journal*,
128(608), 413–446.
