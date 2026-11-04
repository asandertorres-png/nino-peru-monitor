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
| **Técnicas de análisis** | Modelos de panel con efectos fijos de ciudad y de tiempo; proyecciones locales (Jordà, 2005) para la función impulso-respuesta; errores estándar de Driscoll–Kraay y bootstrap *wild cluster* |
| **Procesamiento** | Python, con el código y los datos derivados versionados en repositorio público |

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

- Dell, M., Jones, B. y Olken, B. (2014). What Do We Learn from the Weather?
  The New Climate-Economy Literature. *Journal of Economic Literature* 52(3).
- Driscoll, J. y Kraay, A. (1998). Consistent Covariance Matrix Estimation with
  Spatially Dependent Panel Data. *Review of Economics and Statistics* 80(4).
- Hsiang, S. (2016). Climate Econometrics. NBER Working Paper.
- Jordà, Ò. (2005). Estimation and Inference of Impulse Responses by Local
  Projections. *American Economic Review* 95(1).

El resto del aparato bibliográfico está en [MARCO_TEORICO.md](MARCO_TEORICO.md)
§10 y [ANTECEDENTES.md](ANTECEDENTES.md) §8.
