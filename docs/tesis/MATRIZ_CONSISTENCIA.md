# Matriz de consistencia metodológica

La matriz que exige el formato de tesis peruano: problema, objetivo, hipótesis,
variables y metodología, alineados fila por fila. Su función no es decorativa —
**es una prueba de coherencia**. Si una fila no cierra, el diseño tiene un
defecto, y la matriz sirve justamente para encontrarlo antes que el jurado.

---

## 1. Un ajuste que la matriz obligó a hacer

Al armarla apareció una inconsistencia en el protocolo que conviene explicar,
porque es el tipo de cosa que un jurado detecta de inmediato.

Los objetivos específicos del protocolo eran cinco, y **el primero era
"construir el panel y validar la réplica del ICEN"**. Ese no es un objetivo de
investigación: **es una tarea metodológica**. No tiene problema que lo origine
ni hipótesis que lo responda, así que en la matriz dejaba una fila con dos
celdas vacías.

La corrección: **construir el panel pasa a la columna de metodología**, que es
donde corresponde, y los objetivos específicos quedan en **cuatro**, cada uno
con su problema y su hipótesis. Nada se pierde —la construcción del panel sigue
siendo la tarea previa— pero la matriz cierra.

También se redujo el conjunto de hipótesis a las que la matriz simplificada
sostiene. La asimetría del shock y la dependencia del nivel de existencias
**no entran como hipótesis específicas**: pasan a ser análisis de robustez, tal
como quedó en [OPERACIONALIZACION.md](OPERACIONALIZACION.md) §3.

## 2. Matriz de consistencia

### Fila general

| | |
|---|---|
| **Problema general** | ¿En qué medida el Niño del Pacífico central (ONI) y el Niño costero (ICEN) tienen efectos distintos sobre la inflación de alimentos de las ciudades del Perú, y cómo varía esa diferencia entre regiones, en el periodo 2010–2026? |
| **Objetivo general** | Estimar y comparar el efecto del Niño del Pacífico central y del Niño costero sobre la inflación de alimentos a nivel de ciudad, identificando su heterogeneidad regional, 2010–2026. |
| **Hipótesis general** | Ambos fenómenos elevan la inflación de alimentos, pero su efecto **no es el mismo**: el Niño costero tiene mayor efecto que el del Pacífico central en las ciudades de la costa norte, y la magnitud difiere entre regiones según la exposición económica de cada ciudad y su régimen de impacto climático. |

### Filas específicas

| # | Problema específico | Objetivo específico | Hipótesis específica | Indicadores |
|---|---|---|---|---|
| **1** | ¿Cuál es el efecto de las anomalías climáticas locales sobre la inflación de alimentos de las ciudades del Perú? | Estimar el efecto de las anomalías locales de precipitación y temperatura sobre la inflación de alimentos por ciudad | Las anomalías climáticas locales elevan la inflación de alimentos, con el efecto máximo dentro de los doce meses posteriores al shock | 1, 2, 7, 8 |
| **2** | ¿Cuál de los dos índices oceánicos —ONI o ICEN— explica mejor la inflación de alimentos de las ciudades del Perú? | Comparar el poder explicativo del ONI y del ICEN-réplica sobre la inflación de alimentos por ciudad | El ICEN tiene mayor poder explicativo que el ONI en las ciudades de la costa norte, y el ONI no lo supera en ninguna región costera | 3, 4, 7, 8 |
| **3** | ¿Cómo difiere el efecto entre regiones según la exposición económica de cada ciudad? | Determinar la heterogeneidad regional del efecto según la exposición económica de cada ciudad | El efecto es mayor donde la participación del sector agropecuario y pesquero y el peso del alimento en la canasta son mayores, y puede **diferir en signo** entre la costa norte y la sierra sur | 5, 6, 1, 2 |
| **4** | ¿La integración de los mercados de alimentos entre ciudades disminuye durante los episodios? | Evaluar si la integración de los mercados de alimentos entre ciudades se reduce durante los episodios | La integración disminuye durante los episodios, porque el fenómeno eleva los costos de transacción al dañar la infraestructura de transporte | 10, 3, 4 |

Los números de la última columna remiten a los 10 indicadores de la matriz de
operacionalización simplificada.

## 3. Metodología

| Aspecto | Definición |
|---|---|
| **Enfoque** | Cuantitativo |
| **Tipo de investigación** | Aplicada |
| **Nivel** | Explicativo |
| **Diseño** | No experimental, longitudinal de panel (ex post facto) |
| **Método** | Hipotético-deductivo |
| **Población** | Las 26 ciudades del ámbito urbano que componen el Índice de Precios al Consumidor del INEI, en el periodo enero 2010 – septiembre 2026 |
| **Muestra** | Censal: las 26 ciudades. Aproximadamente 26 × 200 = **5 200 observaciones ciudad-mes** |
| **Unidad de análisis** | La ciudad-mes |
| **Técnica de recolección** | Análisis documental de fuentes secundarias de acceso abierto |
| **Instrumento** | Ficha de registro de datos secundarios |
| **Técnicas de análisis** | Proyecciones locales en panel **con aumento de rezagos**, con efectos fijos de ciudad y de tiempo; **corrección de sesgo por jackknife de medio panel**; modelo de corrección de error con umbral para la integración de mercados; pruebas de dependencia espacial y de estabilidad de parámetros (ver §3.1) |
| **Inferencia** | **Rezagos como controles y agrupamiento en la dimensión transversal** como procedimiento principal; Driscoll–Kraay y bootstrap *wild cluster* como contraste (ver §3.1) |
| **Procesamiento** | Python, con el código y los datos derivados versionados en repositorio público |

### 3.1 Revisión de las técnicas contra los antecedentes

Las técnicas de la primera versión de esta matriz —panel con efectos fijos,
proyecciones locales y errores de Driscoll–Kraay— se eligieron desde el marco
teórico. Al contrastarlas con lo que la literatura metodológica y los
antecedentes **efectivamente usan**, aparecieron dos defectos que conviene
corregir antes de estimar, no después.

**Defecto 1. El panel con proyecciones locales tiene un sesgo que no estaba
contemplado.** Mei, Sheng y Shi (2023) muestran que la extensión natural de las
proyecciones locales a datos de panel, sustituyendo MCO por el estimador de
efectos fijos, arrastra un **sesgo de Nickell implícito**, presente *aunque la
especificación no incluya rezagos de la variable dependiente*. Ese sesgo
invalida la inferencia asintótica estándar cuando N y T son del mismo orden, y
en su aplicación a crisis financieras encuentran que el estimador de efectos
fijos **subestima** los efectos frente al corregido. Proponen el **jackknife de
medio panel** como solución simple.

> En nuestro caso N = 26 y T ≈ 200, de modo que T es mucho mayor que N y el
> sesgo es menor que en el escenario que ellos describen. Pero "menor" no es
> "nulo", la corrección es barata y su dirección —subestimación— es
> precisamente la que haría concluir que no hay efecto cuando sí lo hay. **Se
> incorpora.**

**Defecto 2. Driscoll–Kraay no es la mejor opción como procedimiento
principal.** Dos hallazgos convergen:

- Montiel Olea y Plagborg-Møller (2021, *Econometrica*) prueban que las
  proyecciones locales **con aumento de rezagos** son asintóticamente válidas
  de manera uniforme tanto con datos estacionarios como no estacionarios y para
  un rango amplio de horizontes, y que **el aumento de rezagos vuelve
  innecesario corregir los errores estándar por autocorrelación**.
- Herbst y Johannsen (2024, *Journal of Econometrics*) muestran que el sesgo de
  muestra pequeña en proyecciones locales puede llevar a que **algunos errores
  estándar robustos a autocorrelación subestimen la incertidumbre muestral**, y
  recomiendan evitarlos en este tipo de aplicación.

Y hay un trabajo escrito para exactamente nuestro caso: Almuzara y Sarto (2024)
estudian la inferencia en regresiones de panel **cuando los regresores de
interés son shocks macroeconómicos**, que es la situación de un índice oceánico
nacional en un panel de ciudades. Muestran que los residuos presentan
**dependencia transversal fuerte** y una estructura de autocorrelación inducida
solo por los adelantos del regresor, y concluyen que **incluir rezagos como
controles y luego agrupar en la dimensión transversal** da una inferencia
simple y robusta.

> **Se invierte el orden:** rezagos como controles más agrupamiento transversal
> pasa a ser el procedimiento principal; Driscoll–Kraay y el bootstrap *wild
> cluster* quedan como contraste. No se eliminan —con 26 grupos conviene
> reportar más de un procedimiento— pero dejan de ser la referencia.

**Incorporación 3. Dependencia espacial: hay que probarla, no suponerla.**
Baltagi y Pirotte (2010) muestran que cuando los coeficientes espaciales son
grandes, las pruebas de hipótesis basadas en estimadores de panel que ignoran
esa dependencia **pueden llevar a inferencia engañosa**. Y no es una
preocupación abstracta para nuestro objeto: Kirillov (2017) hace análisis
espacial del **IPC de alimentos** en 79 regiones rusas, 2002–2015, y encuentra
correlación espacial **estadísticamente significativa y decreciente con la
distancia**. Ahmad et al. (2019) encuentran dependencia espacial significativa
en la inflación regional de Indonesia.

> Se incorpora una **prueba de autocorrelación espacial sobre los residuos**
> (I de Moran, o el estadístico APLE que Kirillov propone como alternativa para
> estructura de panel) y, si resulta significativa, un **panel espacial** como
> robustez. Conviene notar que esto **no compite con la hipótesis específica
> 4**: allí la caída de la integración es el objeto de estudio; aquí la
> dependencia espacial es una amenaza a la inferencia. Son dos usos distintos
> del mismo hecho.

**Incorporación 4. Estabilidad de los parámetros.** Calero y Rodríguez (2026)
encuentran para el Perú que los efectos de los shocks climáticos son
**variables en el tiempo**, y que el componente de volatilidad estocástica es
esencial para el ajuste del modelo; Kim et al. (2025) encuentran efectos
despreciables al inicio de su muestra y significativos al final. Un modelo de
coeficientes constantes sobre 2010–2026 **supone lo contrario de lo que esos
trabajos documentan**.

> No corresponde a una tesis de pregrado estimar un TVP-VAR con volatilidad
> estocástica. Sí corresponde **probar la estabilidad**: pruebas de quiebre
> estructural y estimación por submuestras. Duran y Dindaroğlu (2021) hacen
> precisamente eso —quiebres de Bai–Perron y regímenes de Markov— sobre
> **26 regiones con IPC mensual**, que es casi exactamente nuestra estructura
> de datos, y además con panel espacial. Es el antecedente metodológico más
> parecido que encontré y conviene seguirlo de cerca.

#### Técnicas finales

| Objetivo | Técnica principal | Fundamento |
|---|---|---|
| Todos | Proyecciones locales en panel **con aumento de rezagos**, efectos fijos de ciudad y de tiempo | Jordà (2005); Montiel Olea y Plagborg-Møller (2021) |
| Todos | **Jackknife de medio panel** para el sesgo de Nickell | Mei, Sheng y Shi (2023) |
| Todos | Inferencia: rezagos como controles + agrupamiento transversal | Almuzara y Sarto (2024) |
| Esp. 2 | Dos estimaciones paralelas, ONI y ICEN, y comparación de ajuste por zona | Gallegati et al. (2026); Solomou et al. (2025) |
| Esp. 3 | Interacción exposición × shock, con heterogeneidad de parámetros por subregión | Ponce (2020) |
| Esp. 4 | Correlaciones móviles entre pares y **modelo de corrección de error con umbral** | Goodwin y Piggott (2001); McNew (1996) |

| Robustez | Técnica | Fundamento |
|---|---|---|
| Dependencia espacial | I de Moran o APLE sobre residuos; panel espacial (SAR/SEM) si resulta significativa | Baltagi y Pirotte (2010); Kirillov (2017) |
| Estabilidad temporal | Quiebres estructurales y estimación por submuestras | Calero y Rodríguez (2026); Duran y Dindaroğlu (2021) |
| Precisión | **Proyecciones locales suavizadas** (splines B) | Barnichon y Brownlees (2019) |
| Largo plazo | Panel ARDL como complemento | Arango-Castillo et al. (2025) |
| Dependencia transversal | Efectos comunes correlacionados o efectos fijos interactivos | Thombs (2022); Gospodinov et al. (2025) |
| Tendencias | Tendencias temporales específicas por ciudad | Yilmazkuday (2025) |

#### Lo que se revisó y se descartó, con la razón

Importa decirlo: varias técnicas de los antecedentes son buenas y **no** se
adoptan, y la razón no es que sean malas sino que exceden el alcance de una
tesis de pregrado o no responden la pregunta planteada.

| Técnica | Dónde aparece | Por qué no se adopta |
|---|---|---|
| TVP-VAR con volatilidad estocástica | Calero y Rodríguez (2026) | Fuera del alcance de pregrado. Su aporte —detectar variación temporal— se cubre con pruebas de quiebre |
| GVAR y wavelets | Gallegati et al. (2026); Solomou et al. (2025); Cashin et al. (2015) | Diseñados para paneles de países, no para ciudades de un mismo país |
| SVAR identificado por componentes independientes | Dalheimer et al. (2026) | Requiere datos de inventarios que no tenemos |
| STAR variable en el tiempo | Emediegwu (2024) | Su objeto es la asimetría, que aquí pasó a robustez |
| LASSO para seleccionar variables climáticas | Bellon y Massetti (2022) | Útil con 164 variables; nosotros usamos 10 indicadores definidos a priori |
| Enfoque ricardiano | Estudio de quinua en el Altiplano (2021) | Corte transversal; la literatura de identificación lo critica por variables omitidas |

### Por qué el diseño es no experimental y aun así permite hablar de efecto

Es la pregunta que el jurado va a hacer, y conviene tener la respuesta escrita.
El fenómeno ENSO se origina en la variabilidad del Pacífico tropical y **no lo
causa la economía peruana**: es exógeno al sistema que se estudia. Esa
exogeneidad, combinada con efectos fijos que absorben todo lo invariante de
cada ciudad y de cada mes, es lo que permite leer los coeficientes como efectos
y no como simples correlaciones. Es el argumento estándar de la literatura de
clima y economía (Dell, Jones y Olken, 2014; Hsiang, 2016).

Lo que la exogeneidad **no** resuelve, y que por eso se trata aparte en el
diseño: la autocorrelación del shock, su carácter común a todas las ciudades en
un mismo mes, y su posible coincidencia con otros shocks nacionales.

### Tareas previas a la estimación

No son capítulos de la tesis ni objetivos: son condiciones para que el diseño
sea ejecutable, y están listadas aquí porque la matriz las desplazó desde los
objetivos.

| # | Tarea | Por qué es previa |
|---|---|---|
| 1 | Persistir el panel climático mensual 1991–2026 a partir de las series diarias de ERA5 | Sin él no existen los indicadores 1 y 2, que son el núcleo de la variable independiente |
| 2 | Verificar la disponibilidad del IPC por ciudad y división de gasto | Decide la viabilidad del diseño: son los indicadores 7 y 8 |
| 3 | Extender la serie ONI a 1950 y corregir el parser de TSM semanal | El producto actual arranca en 2021 |
| 4 | Calcular la réplica del ICEN y validarla contra los informes del IGP | Sostiene el título y la hipótesis específica 2 |

## 4. Verificación de la coherencia

Una matriz de consistencia se valida leyéndola por columnas y comprobando que
cada fila cierre. Revisión hecha:

| Comprobación | Resultado |
|---|---|
| ¿Cada problema específico tiene un objetivo que lo responde? | Sí, los cuatro |
| ¿Cada objetivo específico tiene una hipótesis contrastable? | Sí, los cuatro |
| ¿Cada hipótesis tiene indicadores que la midan? | Sí; se indican en la última columna |
| ¿Los objetivos específicos suman el general? | Sí: efecto (1), comparación de índices (2), heterogeneidad (3) e integración (4) |
| ¿Hay objetivos sin hipótesis? | **Ya no.** Era el defecto corregido en §1 |
| ¿Hay hipótesis que la matriz de operacionalización no sustente? | **No**, tras mover asimetría y dependencia del estado a robustez |
| ¿El nivel declarado corresponde al diseño? | Sí: explicativo con panel y variación exógena |
| ¿La muestra permite contrastar las hipótesis? | Sí en tamaño (~5 200 observaciones); **con la salvedad de que 26 grupos están en el límite inferior para el agrupamiento de errores**, de ahí el bootstrap |

## 5. Referencias

- Almuzara, M. y Sarto, A. (2024). Micro Responses to Macro Shocks. *Staff
  Reports*, Federal Reserve Bank of New York.
- Baltagi, B. y Pirotte, A. (2010). Panel Data Inference Under Spatial
  Dependence. DOI 10.2139/SSRN.1805892.
- Barnichon, R. y Brownlees, C. (2019). Impulse Response Estimation by Smooth
  Local Projections. *Review of Economics and Statistics*.
- Dell, M., Jones, B. y Olken, B. (2014). What Do We Learn from the Weather?
  The New Climate-Economy Literature. *Journal of Economic Literature* 52(3).
- Duran, H. E. y Dindaroğlu, B. (2021). Regional inflation persistence in
  Turkey. *Growth and Change* 52(1). DOI 10.1111/GROW.12456.
- Herbst, E. y Johannsen, B. (2024). Bias in local projections. *Journal of
  Econometrics*.
- Kirillov, A. (2017). Inflación de precios de alimentos en las regiones de
  Rusia: análisis espacial. *Spatial Economics*. DOI 10.14530/SE.2017.4.041-058.
- Mei, Z.-W., Sheng, X.-S. y Shi, Z. (2023). Nickell bias in panel local
  projection. *Journal of International Economics*.
- Montiel Olea, J. L. y Plagborg-Møller, M. (2021). Local Projection Inference
  Is Simpler and More Robust Than You Think. *Econometrica*.
- Driscoll, J. y Kraay, A. (1998). Consistent Covariance Matrix Estimation with
  Spatially Dependent Panel Data. *Review of Economics and Statistics* 80(4).
- Hsiang, S. (2016). Climate Econometrics. NBER Working Paper.
- Jordà, Ò. (2005). Estimation and Inference of Impulse Responses by Local
  Projections. *American Economic Review* 95(1).

El resto del aparato bibliográfico está en [MARCO_TEORICO.md](MARCO_TEORICO.md)
§10 y [ANTECEDENTES.md](ANTECEDENTES.md) §8.
