# Matriz de datos

Estructura del archivo con el que se estima. No es una lista de deseos: es el
**esquema exacto** del panel, y está definido una sola vez en
`scripts/tesis/esquema_panel.py`, que a partir de esa definición genera la
plantilla, el esquema en JSON y el validador. Así la matriz del documento y el
archivo real no pueden decir cosas distintas.

---

## 1. Decisiones de estructura

| Aspecto | Decisión | Por qué |
|---|---|---|
| **Unidad de observación** | La **ciudad-mes** | Es la unidad de la hipótesis y la del IPC |
| **Formato** | **Largo**: una fila por ciudad y periodo | El formato ancho —una columna por mes— no se puede estimar con efectos fijos sin reorganizarlo, y es la fuente más común de errores de pegado |
| **Dimensión** | **17 campos** · 26 ciudades × 201 periodos = **5 226 filas**, más una tabla auxiliar de 312 filas | Enero 2010 a septiembre 2026 |
| **Separador y codificación** | Punto y coma, UTF-8 con BOM | Abre directo en Excel con configuración regional en español |
| **Vacíos** | Celda en blanco, **nunca 0 ni −99** | Un cero es un dato y un vacío es su ausencia; confundirlos sesga la estimación sin dejar rastro |
| **Decimales** | Punto, no coma | Para que el archivo se lea igual en Python y en Excel |

**Panel balanceado o no.** El ideal es balanceado —las 26 ciudades en los 201
meses—, pero es probable que no lo sea: si el IPC de alguna ciudad empieza
después, o si falta un mes en un boletín, el panel queda desbalanceado. **Eso
no invalida el diseño**, los estimadores de panel lo admiten; lo que invalida es
**rellenar los huecos sin decirlo**. Por eso existe el campo `fuente_ipc`, que
registra si el dato vino de una serie, de un boletín en PDF o fue imputado.

**Por qué 17 campos y no 27.** La primera versión tenía 27 y se simplificó, no
solo por brevedad. Tres de los campos retirados —`normal_pp_mm`, `sigma_pp_mm`
y `anios_normal`— **no varían a nivel de ciudad-mes**: son constantes para cada
par (ciudad, mes del año), de modo que repetirlos en 5 226 filas es
denormalizar. Van en una tabla auxiliar de 26 × 12 = 312 filas que se une al
panel por (ciudad, mes). Los otros retirados —`ciudad_id`, `ubigeo`,
`departamento`, `lat`, `lon`— son atributos fijos de la ciudad y viven en
`scripts/config.py`; y `base_ipc` es función del periodo, por lo tanto
derivable. **Ninguno se perdió: cada uno está donde le corresponde.**

## 2. Matriz de datos · panel principal

| N° | Campo | Etiqueta | Tipo | Escala | Rango válido | Fuente | Ind. |
|---|---|---|---|---|---|---|---|
| 1 | `ciudad` | Nombre de la ciudad | Texto | Nominal | 26 nombres válidos | INEI | – |
| 2 | `zona` | Régimen de impacto climático | Texto | Nominal | costa_norte, costa_centro_sur, sierra_norte, sierra_sur, selva | `scripts/config.py` | – |
| 3 | `anio` | Año | Entero | Intervalo | 2010 a 2026 | Derivado | – |
| 4 | `mes` | Mes | Entero | Intervalo | 1 a 12 | Derivado | – |
| 5 | `periodo` | Periodo AAAA-MM | Texto | Ordinal | 2010-01 a 2026-09 | Derivado | – |
| 6 | `anom_pp` | Anomalía estandarizada de precipitación | Decimal | Razón | ≈ −4 a 4 σ | ERA5 | **1** |
| 7 | `anom_tx` | Anomalía estandarizada de temperatura máxima | Decimal | Razón | ≈ −4 a 4 σ | ERA5 | **2** |
| 8 | `oni` | Índice ONI, región Niño 3.4 | Decimal | Razón | −3,0 a 3,0 °C | NOAA/CPC | **3** |
| 9 | `icen_rep` | ICEN-réplica, región Niño 1+2 | Decimal | Razón | −4,0 a 5,0 °C | NOAA/CPC | **4** |
| 10 | `exp_vab_prim` | Peso de agropecuario y pesca en el VAB | Decimal | Razón | 0 a 100 % | INEI | **5** |
| 11 | `exp_peso_alim` | Peso del alimento en la canasta | Decimal | Razón | 0 a 100 % | INEI | **6** |
| 12 | `ipc_alim` | Índice de precios de alimentos | Decimal | Razón | > 0; base dic-2021 = 100 | INEI | base de 7 a 10 |
| 13 | `infl_alim_m` | Variación mensual del IPC de alimentos | Decimal | Razón | ≈ −20 a 20 % | Derivado | **7** |
| 14 | `infl_alim_12` | Variación a 12 meses | Decimal | Razón | ≈ −30 a 60 % | Derivado | **8** |
| 15 | `volat_12` | Desviación estándar móvil de 12 meses | Decimal | Razón | ≥ 0 | Derivado | **9** |
| 16 | `integr_media` | Correlación media con las demás ciudades | Decimal | Razón | −1 a 1 | Derivado | **10** |
| 17 | `fuente_ipc` | De dónde se obtuvo el dato | Texto | Nominal | serie, boletin_pdf o imputado | Registro del autor | trazabilidad |

**Los 10 indicadores de la matriz de operacionalización están todos**, más el
índice base del que se derivan cuatro de ellos y un campo de trazabilidad.

### Tabla auxiliar: normales climáticas

26 ciudades × 12 meses = **312 filas**. Se une al panel por (`ciudad`, `mes`).

| N° | Campo | Etiqueta | Tipo | Rango válido | Papel |
|---|---|---|---|---|---|
| 1 | `ciudad` | Nombre de la ciudad | Texto | 26 nombres válidos | Llave |
| 2 | `mes` | Mes del año | Entero | 1 a 12 | Llave |
| 3 | `normal_pp_mm` | Normal mensual de precipitación 1991–2020 | Decimal | ≥ 0 mm | Insumo del indicador 1 |
| 4 | `sigma_pp_mm` | Desviación estándar de la precipitación mensual | Decimal | ≥ 0 mm | Insumo del indicador 1 |
| 5 | `anios_normal` | Años usados en la normal de ese mes | Entero | 0 a 30 | Control de calidad |

## 3. Los campos que no son datos sino control

Son los que distinguen un panel defendible de uno que el jurado no puede
auditar. Ninguno entra en las regresiones; todos entran en el capítulo de datos.

- **`sigma_pp_mm`** es la desviación estándar que hoy **no existe** en el
  producto del repositorio y sin la cual el indicador 1 no se puede calcular.
  Tenerla como campo propio obliga a persistirla y deja ver de inmediato si
  falta.
- **`anios_normal`** dice con cuántos de los 30 años se construyó la normal de
  ese mes. Una normal hecha con 12 años no es comparable con una hecha con 30,
  y sin este campo esa diferencia queda invisible.
- **`fuente_ipc`** registra si el dato salió de una serie descargada, de un
  boletín en PDF o fue imputado. **Si al final hay datos imputados, este campo
  es la diferencia entre declararlo y ocultarlo.**

## 4. Uso

Generar las dos plantillas y el esquema:

```bash
python scripts/tesis/esquema_panel.py --plantilla
```

Validar el panel antes de estimar:

```bash
python scripts/tesis/esquema_panel.py --validar data/tesis/panel.csv
```

El validador revisa la estructura de columnas, las combinaciones ciudad-periodo
duplicadas, los periodos fuera de rango, los campos obligatorios vacíos, los
tipos de dato y los dominios de las variables categóricas. Devuelve 1 si hay
problemas, de modo que sirve como control previo en un flujo automatizado.

Distingue **problemas**, que bloquean, de **avisos**, que no. Un panel
desbalanceado es aviso; una zona inválida o una fila duplicada es problema.

## 5. Lo que este documento no resuelve

La matriz de datos describe **cómo debe verse** el archivo. No garantiza que
los datos existan: eso lo responde
`python scripts/tesis/verificar_fuentes.py`, y al día de hoy **ninguno de los
10 indicadores está confirmado**, porque falta persistir el panel climático y
confirmar que el INEI publique el IPC por ciudad y división de gasto.

Dicho de otro modo: la plantilla está lista para llenarse, pero todavía no
sabemos con qué.
