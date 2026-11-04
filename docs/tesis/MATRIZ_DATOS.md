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
| **Dimensión** | 26 ciudades × 201 periodos = **5 226 filas**, 27 campos | Enero 2010 a septiembre 2026 |
| **Separador y codificación** | Punto y coma, UTF-8 con BOM | Abre directo en Excel con configuración regional en español |
| **Vacíos** | Celda en blanco, **nunca 0 ni −99** | Un cero es un dato y un vacío es su ausencia; confundirlos sesga la estimación sin dejar rastro |
| **Decimales** | Punto, no coma | Para que el archivo se lea igual en Python y en Excel |

**Panel balanceado o no.** El ideal es balanceado —las 26 ciudades en los 201
meses—, pero es probable que no lo sea: si el IPC de alguna ciudad empieza
después, o si falta un mes en un boletín, el panel queda desbalanceado. **Eso
no invalida el diseño**, los estimadores de panel lo admiten; lo que invalida es
**rellenar los huecos sin decirlo**. Por eso existe el campo `fuente_ipc`, que
registra si el dato vino de una serie, de un boletín en PDF o fue imputado.

## 2. Matriz de datos

| N° | Campo | Etiqueta | Tipo | Escala | Rango válido | Fuente | Ind. |
|---|---|---|---|---|---|---|---|
| 1 | `ciudad_id` | Código de ciudad | Entero | Nominal | 1 a 26 | Asignado por el autor | – |
| 2 | `ciudad` | Nombre de la ciudad | Texto | Nominal | 26 nombres válidos | INEI | – |
| 3 | `ubigeo` | Código UBIGEO | Texto | Nominal | 6 dígitos | INEI | – |
| 4 | `departamento` | Departamento | Texto | Nominal | 25 departamentos | INEI | – |
| 5 | `zona` | Régimen de impacto climático | Texto | Nominal | costa_norte, costa_centro_sur, sierra_norte, sierra_sur, selva | `scripts/config.py` | – |
| 6 | `lat` | Latitud del punto | Decimal | Razón | −18,5 a −3,5 | GeoJSON del monitor | – |
| 7 | `lon` | Longitud del punto | Decimal | Razón | −81,5 a −68,5 | GeoJSON del monitor | – |
| 8 | `anio` | Año | Entero | Intervalo | 2010 a 2026 | Derivado | – |
| 9 | `mes` | Mes | Entero | Intervalo | 1 a 12 | Derivado | – |
| 10 | `periodo` | Periodo AAAA-MM | Texto | Ordinal | 2010-01 a 2026-09 | Derivado | – |
| 11 | `anom_pp` | Anomalía estandarizada de precipitación | Decimal | Razón | ≈ −4 a 4 σ | ERA5 vía Open-Meteo | **1** |
| 12 | `anom_tx` | Anomalía estandarizada de temperatura máxima | Decimal | Razón | ≈ −4 a 4 σ | ERA5 vía Open-Meteo | **2** |
| 13 | `oni` | Índice ONI, región Niño 3.4 | Decimal | Razón | −3,0 a 3,0 °C | NOAA/CPC | **3** |
| 14 | `icen_rep` | ICEN-réplica, región Niño 1+2 | Decimal | Razón | −4,0 a 5,0 °C | NOAA/CPC, calculado | **4** |
| 15 | `exp_vab_prim` | Peso de agropecuario y pesca en el VAB | Decimal | Razón | 0 a 100 % | INEI | **5** |
| 16 | `exp_peso_alim` | Peso del alimento en la canasta | Decimal | Razón | 0 a 100 % | INEI | **6** |
| 17 | `ipc_alim` | Índice de precios de alimentos | Decimal | Razón | > 0; base dic-2021 = 100 | INEI | base de 7 a 10 |
| 18 | `infl_alim_m` | Variación mensual del IPC de alimentos | Decimal | Razón | ≈ −20 a 20 % | Derivado | **7** |
| 19 | `infl_alim_12` | Variación a 12 meses | Decimal | Razón | ≈ −30 a 60 % | Derivado | **8** |
| 20 | `volat_12` | Desviación estándar móvil de 12 meses | Decimal | Razón | ≥ 0 | Derivado | **9** |
| 21 | `integr_media` | Correlación media con las demás ciudades | Decimal | Razón | −1 a 1 | Derivado | **10** |
| 22 | `ipc_general` | IPC general de la ciudad | Decimal | Razón | > 0 | INEI | auxiliar |
| 23 | `normal_pp_mm` | Normal mensual de precipitación 1991–2020 | Decimal | Razón | ≥ 0 mm | ERA5, calculado | auxiliar |
| 24 | `sigma_pp_mm` | Desviación estándar de la precipitación mensual | Decimal | Razón | ≥ 0 mm | ERA5, calculado | auxiliar |
| 25 | `anios_normal` | Años usados en la normal de ese mes | Entero | Razón | 0 a 30 | ERA5, calculado | control de calidad |
| 26 | `base_ipc` | Base del índice en ese periodo | Texto | Nominal | 2009 o dic2021 | INEI | control de empalme |
| 27 | `fuente_ipc` | De dónde se obtuvo el dato | Texto | Nominal | serie, boletin_pdf o imputado | Registro del autor | trazabilidad |

## 3. Los cuatro campos que no son datos sino control

Son los que distinguen un panel defendible de uno que el jurado no puede
auditar. Ninguno entra en las regresiones; todos entran en el capítulo de datos.

- **`sigma_pp_mm`** es la desviación estándar que hoy **no existe** en el
  producto del repositorio y sin la cual el indicador 1 no se puede calcular.
  Tenerla como campo propio obliga a persistirla y deja ver de inmediato si
  falta.
- **`anios_normal`** dice con cuántos de los 30 años se construyó la normal de
  ese mes. Una normal hecha con 12 años no es comparable con una hecha con 30,
  y sin este campo esa diferencia queda invisible.
- **`base_ipc`** marca si el periodo viene de la base 2009 o de la base
  diciembre 2021. Permite correr la robustez por subperiodo de base, que está
  en el protocolo.
- **`fuente_ipc`** registra si el dato salió de una serie descargada, de un
  boletín en PDF o fue imputado. **Si al final hay datos imputados, este campo
  es la diferencia entre declararlo y ocultarlo.**

## 4. Uso

Generar la plantilla y el esquema:

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
