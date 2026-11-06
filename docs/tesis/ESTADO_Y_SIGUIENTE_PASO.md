# Estado del proyecto y siguiente paso

**Punto de entrada.** Si se abre una sesión nueva —local o en la nube— este es
el documento que hay que leer primero. Resume dónde está todo, qué quedó
confirmado, qué no, y cuál es la siguiente tarea.

Última actualización: 6 de noviembre de 2026.
Rama de trabajo: `claude/awesome-maxwell-x9r2sz`.

---

## 1. Qué es esto

Dos cosas en un mismo repositorio:

1. **El monitor** (`scripts/`, `docs/index.html`, `data/`): mapa de anomalías
   climáticas del Perú que se actualiza solo cada 6 horas. Funciona y está
   publicado.
2. **La tesis** (`docs/tesis/`, `scripts/tesis/`): trabajo metodológico de una
   tesis de pregrado en economía que usa la infraestructura del monitor. **Sin
   datos todavía.**

**Título:** *Niño del Pacífico central y Niño costero: efecto diferenciado
sobre la inflación de alimentos en 26 ciudades del Perú, 2010–2026*.

## 2. Qué quedó confirmado con datos reales

Verificado el 4 de noviembre de 2026 corriendo
`python scripts/tesis/verificar_fuentes.py` en la máquina del autor, que sí
tiene salida a internet (el entorno de la nube la tiene bloqueada).

| Indicador | Fuente | Resultado |
|---|---|---|
| **1, 2** Anomalías de lluvia y temperatura | ERA5 vía Open-Meteo | ✅ Responde con lluvia y temperatura |
| **3** ONI | NOAA/CPC | ✅ **921 trimestres, 1950–2026.** El repositorio guarda solo desde 2021 |
| **4** ICEN-réplica | NOAA/CPC, `ersst5.nino.mth.91-20.ascii` | ✅ **918 meses con columnas de Niño 1+2.** La réplica es calculable |
| ref | API del BCRP | ✅ Operativa |

**Esto desbloquea el título.** El ICEN-réplica deja de ser una apuesta: la
fuente está localizada y el cálculo es mecánico.

## 3. Qué sigue sin confirmar

| Indicador | Estado |
|---|---|
| **5** VAB departamental | 🟡 El portal del INEI responde, pero eso no prueba que el dato sea descargable |
| **6** Ponderaciones del IPC por ciudad | 🟠 Sin verificar. Si solo existen para Lima, el indicador no varía entre ciudades |
| **7, 8** IPC de alimentos por ciudad | 🔴 **Es lo que decide el diseño.** Ver §4 |

## 4. La pregunta abierta, y las dos trampas que ya costaron dos iteraciones

El verificador busca en el catálogo del BCRP series de IPC por ciudad. **Dio
falso positivo dos veces**, y conviene conocerlas para no repetirlas:

**Trampa 1, corregida.** Buscaba las palabras en la fila completa y por
subcadena. Resultado: «precios al consumidor» coincidía con la *metodología*
del tipo de cambio real —que se calcula con ratios de IPC— y, peor, **«ica» es
subcadena de «estadística», «metodológica» y «República»**, así que casi toda
fila coincidía con la ciudad de Ica. Daba 188 coincidencias falsas.

**Trampa 2, corregida.** Tras arreglar lo anterior, informó «134 nombran una
ciudad, 37 mencionan alimentos». Pero **todas las ciudades eran Lima
Metropolitana** —la serie nacional de referencia, no un panel de 26
ciudades— y las 37 de alimentos decían **«IPC Sin Alimentos y Energía»**, que
son medidas subyacentes que los **excluyen**.

El verificador ahora cuenta **ciudades distintas** y descarta las series del
tipo «sin alimentos». **Falta correrlo con el catálogo real** y leer cuál de
los tres escenarios da:

| Escenario | Qué significa | Qué hacer |
|---|---|---|
| Una sola ciudad (Lima) | El BCRP solo publica la referencia nacional | Ir a los boletines del INEI, que publican por ciudad y gran grupo **en PDF**. Cambia el costo de la semana 3 |
| Varias ciudades, sin desagregar alimentos | Hay IPC general por ciudad | Plan B del protocolo: IPC general como dependiente, y declararlo |
| Varias ciudades con alimentos | Mejor caso | Los indicadores 7 y 8 salen de la API del BCRP |

```bash
python scripts/tesis/verificar_fuentes.py --buscar-ipc-ciudades
```

## 5. La siguiente tarea, y por qué es esa

**Tarea 0: persistir el panel climático mensual.**

`scripts/calcular_normales.py` descarga 30 años de serie diaria por punto y
acumula `lluvia[(anio, mes)]` —que **es** el panel— antes de colapsarlo al
promedio de los 30 años. Son **9 000 observaciones mes-departamento calculadas
y descartadas** en el último paso, y 70 200 mes-provincia cuando se corra ese
nivel. La descarga es la parte costosa y ya se hace.

Dos detalles de implementación:

1. La precipitación sale gratis: ya está indexada por `(anio, mes)`.
2. La temperatura **no**: `tmax[mes]` y `tmin[mes]` se indexan solo por mes del
   año y mezclan los 30 años. Hay que re-indexarlos a `(anio, mes)`. Son dos
   líneas y tampoco cuesta una petición extra.

**Sin esto, los indicadores 1 y 2 no se pueden calcular**, porque la anomalía
estandarizada necesita la desviación estándar por unidad y mes, y
`data/normales.json` guarda solo la media.

Cuidado con una trampa: si el panel se usa para estimar y las normales se
calculan con los mismos años, la anomalía de cada mes incluye ese mes en su
propio promedio. Con 30 años el sesgo es chico, pero conviene extender la
descarga más allá de 2020 y decidirlo explícitamente.

### Después de la tarea 0

| # | Tarea | Por qué |
|---|---|---|
| 1 | Resolver el escenario de §4 | Decide la variable dependiente |
| 2 | Extender la serie ONI a 1950 y arreglar el parser de TSM semanal | El producto guarda desde 2021 y `oni.json` trae `semanal_error` |
| 3 | Calcular la réplica del ICEN y validarla contra informes del IGP | Sostiene el título |
| 4 | Correr el nivel provincial | `data/normales_provincias.json` no existe; son varias horas |

## 6. Dónde está cada cosa

### Documentos de la tesis (`docs/tesis/`)

| Archivo | Contenido |
|---|---|
| `PROTOCOLO.md` | Documento madre: título, problema, brecha, datos, hipótesis, estrategia empírica, robustez, cronograma |
| `MODELO_ECONOMICO.md` | Modelo de equilibrio parcial del que se derivan las hipótesis y la ecuación a estimar |
| `MARCO_TEORICO.md` | Seis pilares con sus predicciones contrastables |
| `ANTECEDENTES.md` | 21 trabajos en tres niveles, con lo que cada uno deja abierto |
| `BRECHAS.md` | Inventario verificado de datos y mapeo de brechas |
| `OPERACIONALIZACION.md` | Matriz simplificada (10 indicadores) y anexo técnico (27) |
| `MATRIZ_CONSISTENCIA.md` | Problema, objetivo, hipótesis, metodología y procesamiento |
| `MATRIZ_DATOS.md` | Esquema del panel |
| `SITUACION_PROBLEMATICA.md` | Capítulo I con técnica del embudo y citas APA |
| `REVISION_SISTEMATICA.md` | Protocolo PRISMA 2020 + MAER-Net |

### Entregables generados

| Archivo | Generador |
|---|---|
| `Tesis_matrices.xlsx` | `scripts/tesis/libro_excel.py` |
| `Matriz_operacionalizacion.docx` | `scripts/tesis/matriz_docx.js` (Node) |
| `Matrices_antecedentes_marco_teorico.docx` | `scripts/tesis/matrices_teoricas_docx.js` (Node) |
| `Hoja_resumen_matrices.docx` | `scripts/tesis/hoja_resumen_docx.js` (Node) |
| `Situacion_problematica_APA.docx` | generado con la skill `redaccion-apa-7` |
| `Propuesta_revision_sistematica_APA.docx` | `scripts/tesis/revision_sistematica_docx.py` |
| `plantilla_panel.csv`, `plantilla_normales.csv` | `scripts/tesis/esquema_panel.py --plantilla` |
| `matriz_operacionalizacion.csv` | `scripts/tesis/matriz.py` |

### Comandos que corren sin instalar nada

```bash
python scripts/tesis/verificar_fuentes.py
```

```bash
python scripts/tesis/esquema_panel.py --plantilla
```

```bash
python scripts/tesis/esquema_panel.py --validar data/tesis/panel.csv
```

```bash
python scripts/tesis/matriz.py
```

`libro_excel.py` necesita `openpyxl`. Los generadores `.js` necesitan Node con
el paquete `docx`. `revision_sistematica_docx.py` depende de `apa_docx.py`, que
viene con una skill y **no está en el repositorio**.

## 7. Decisiones tomadas que no conviene revisar sin motivo

Cada una costó una corrección y está documentada donde se indica:

1. **El aporte no es descubrir el efecto, es medir su distribución
   geográfica.** Calero y Rodríguez (2026) ya cuantifican el canal
   inflacionario en el Perú (+0,25 pp) y Crofils et al. (2024) lo publican en
   *JEEM*. → `ANTECEDENTES.md` §6
2. **Las hipótesis no declaran un signo único.** El indicador de anomalía
   lleva signo y el daño viene de los dos extremos según la región.
   → `MATRIZ_CONSISTENCIA.md` §2.2
3. **El tratamiento estadístico no va en la matriz de consistencia.**
   → `MATRIZ_CONSISTENCIA.md` §4
4. **La inferencia principal no es Driscoll–Kraay** sino rezagos como
   controles más agrupamiento transversal (Almuzara y Sarto, 2024), con
   jackknife de medio panel por el sesgo de Nickell (Mei et al., 2023).
   → `MATRIZ_CONSISTENCIA.md` §4.1
5. **Las dimensiones de la variable independiente son económicas, no
   físicas.** El dato climático es indicador de una sola de las seis.
   → `OPERACIONALIZACION.md` §1

## 8. Lo que falta verificar antes de citarlo

En `SITUACION_PROBLEMATICA.md` §3 hay cinco cifras que vienen de resúmenes de
buscador o notas de prensa y **no se verificaron en fuente primaria**. La más
importante: **la nota del BCRP en *Revista Moneda* 196**, que al parecer mide
el Niño costero con el ICEN y halla efectos mayores sobre la inflación de
alimentos. Si se confirma, cambia cómo se enuncia la originalidad de la tesis.
