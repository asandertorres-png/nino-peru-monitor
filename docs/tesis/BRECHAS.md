# Brechas de investigación que atan con los datos de este repositorio

Documento de decisión. Cada brecha se evalúa contra una pregunta: **¿los datos
que este repositorio tiene o puede generar a costo conocido alcanzan para
cerrarla?** Una brecha que exige datos que no podemos conseguir no es una
brecha útil, es una excusa para no decidir.

Fecha del diagnóstico: 3 de noviembre de 2026.

---

## 1. Inventario honesto: qué hay, qué no hay

Esto se verificó archivo por archivo, no se supuso.

### Lo que está en el repositorio

| Producto | Contenido real | Alcance |
|---|---|---|
| `data/normales.json` | 25 departamentos × 12 meses: precipitación mensual, tmax, tmin, años usados | **Climatología**, no serie. 1991–2020, ERA5 |
| `data/estado.json` | 25 departamentos con anomalías, altitudes y nivel de alerta | **Una sola fecha** (2026-11-02). El flujo lo reescribe |
| `data/oni.json` | ONI trimestral | **60 observaciones, 2021-ASO a 2026-JAS.** Nada antes de 2021 |
| GeoJSON | Límites de 25 departamentos y 195 provincias | Completo |
| Código | Descarga, agregación, verificación, niveles | Funcional |

### Lo que no está

1. **No existe ningún panel histórico.** `estado.json` es una fotografía del
   presente que se sobreescribe cada 6 horas. No hay historia de anomalías.
2. **`data/normales_provincias.json` no existe.** El nivel provincial está
   implementado en código y documentado en `METODOLOGIA.md`, pero **nunca se
   corrió**. Los 195 puntos son una capacidad, no un dato.
3. **El ONI no llega antes de 2021.** El archivo de la NOAA empieza en 1950;
   nuestro producto guarda solo lo reciente.
4. **La TSM semanal está rota ahora mismo.** `oni.json` trae
   `semanal_error: "ValueError: no encontre filas con fecha y valores
   numericos"`, y `estado.json` publica `tsm_semanal: null`. El parser que
   `METODOLOGIA.md` describe como verificado contra una muestra real no está
   funcionando contra el archivo actual.
5. **No hay ninguna variable económica.** Ni una serie, ni un precio.

### El hallazgo que cambia todo

`scripts/calcular_normales.py` descarga **30 años de serie diaria** para cada
punto y, en `normales_mensuales()`, acumula `lluvia[(anio, mes)]`: el total de
precipitación de **cada año-mes concreto**, con su conteo de días presentes.
Esa estructura *es* el panel. Después lo colapsa en `totales_por_mes[mes]` y
escribe **solo el promedio** de los ~30 años.

> **El panel mensual de precipitación 1991–2020 se calcula y se tira.**

Son 25 × 360 = **9 000 observaciones mes-departamento** ya descargadas y
descartadas en el último paso, y 195 × 360 = **70 200 observaciones
mes-provincia** que se descartarían igual cuando se corra el nivel provincial.
La descarga es la parte costosa (30–90 minutos para departamentos, varias horas
para provincias); el agregado es gratis.

**Un matiz que importa para implementarlo.** La precipitación está indexada por
`(anio, mes)`, así que su panel sale de inmediato. La temperatura **no**:
`tmax[mes]` y `tmin[mes]` se indexan solo por mes del año y acumulan los días
de los 30 años juntos, de modo que la dimensión temporal de la temperatura sí
se pierde en la estructura actual. Recuperarla exige re-indexar esos dos
diccionarios a `(anio, mes)`, que es un cambio de dos líneas. **Tampoco cuesta
una sola petición extra.**

**Consecuencia operativa:** persistir esos agregados por año-mes convierte un
generador de climatología en un generador de panel climático **sin un solo
pedido extra a la API**. Extendiendo la ventana a 2026 el panel llega a 420
meses. Esto no es una tarea de la tesis: es el prerrequisito de todas las
brechas que siguen, y debe hacerse antes que nada.

Ojo con una trampa: si el panel se usa para estimar y las normales se calculan
con los mismos años, la anomalía de cada mes está construida con un promedio
que incluye a ese mes. Con 30 años el sesgo es chico, pero hay que decidirlo
explícitamente — normales con 1991–2020 y estimación en 1991–2026 lo evita en
el tramo 2021–2026, y es otra razón para extender la descarga más allá de 2020.

---

## 2. Qué dice la literatura (y qué deja libre)

### Internacional: el estado del arte

Hay una literatura madura de ENSO y precios, y conviene conocerla antes de
reclamar originalidad:

- **ENSO sobre precios locales de alimentos, con asimetría.** Emediegwu (2024,
  *Environmental and Resource Economics*) usa más de 1 100 mercados en 36 países
  de África subsahariana con modelos STAR variables en el tiempo; encuentra que
  ENSO afecta cerca de la mitad de los precios, con asimetría fuerte y
  persistencia, y concluye que la respuesta debe ser **subregional, no
  regional**.
- **Heterogeneidad geográfica dentro de un país diverso.** Bohorquez-Penuela
  et al. (2026) estudian Colombia con precios mayoristas de 40 cultivos, redes
  de producción y datos granulares de lluvia y temperatura. Es el trabajo más
  parecido a lo que haría sentido para el Perú, **hecho en Colombia**.
- **ENSO no lineal y precios de alimentos en Colombia.** Abril et al. (2019,
  *AJARE*).
- **Panel espacial de inflación regional.** Ahmad et al. (2019) estiman el
  efecto de El Niño sobre la inflación de 25+ provincias de Indonesia y
  encuentran **dependencia espacial significativa**: la inflación de una
  provincia depende de la de sus vecinas. Marpaung et al. (2019) hacen algo
  similar para 25 provincias indonesias, 2008–2015.
- **Proyecciones locales para shocks climáticos e inflación de alimentos.**
  Kumar et al. (2026, *Journal of Agriculture and Food Research*) para India,
  horizontes k = 0…5.
- **Asimetría y dinámica de precios de commodities.** Ubilava (2017, *AJAE* y
  *World Development*) sobre 43 commodities y sobre trigo.
- **El supuesto Niño-sube / Niña-baja está en duda.** Borrallo et al. (2024)
  lo cuestionan explícitamente.
- **"Diversidad de ENSO": Pacífico central vs Pacífico oriental.** Gallegati
  et al. (2026, *PLOS Climate*) y Solomou et al. (2025, *Climate Research*)
  distinguen los tipos CP y EP de El Niño y estiman sus efectos sobre la
  inflación nacional con GVAR y wavelets.

**Esa última línea es la clave.** La distinción CP/EP de esa literatura **es**,
en lo esencial, la distinción ONI / ICEN: Pacífico central (Niño 3.4) frente a
Pacífico oriental (Niño 1+2, frente a la costa peruana). Pero se estima
**entre países y a nivel nacional**, con modelos globales. Nadie la estima
**dentro de un país, entre regiones**.

### Perú: qué ya está hecho

Esto importa porque elimina dos de los diseños que parecían disponibles.

| Trabajo | Qué hace | Qué cierra |
|---|---|---|
| Saldarriaga (2016, BID) | Variabilidad de **temperatura** sobre productividad y precios agrícolas; ENAHO 2004–2010 + grilla 0,5° (~56 km), variación interanual **dentro de municipalidad**. Halla que las temperaturas inusualmente cálidas, no las frías, son las que dañan | Es el antecedente más cercano. Pero: **solo temperatura**, sin ENSO ni precipitación, 2004–2010, y precios **en finca**, no IPC al consumidor |
| Ramos-Sandoval et al. (2026, *Sustainability*) | Índice de Vulnerabilidad Socio-Climática con microdatos **ENAHO 2000–2018**, por grandes regiones; halla heterogeneidad fuerte (costa, Andes, Amazonía) | **Cierra buena parte del diseño de bienestar con ENAHO** |
| Malpartida y Guembes (2025, *Economía* PUCP) | **DiD** con panel de hogares 2015–2019 y **precipitación a nivel distrital**; efecto del Niño costero 2017 sobre gasto en salud y educación en la costa norte rural | Cierra el diseño "DiD del 2017 con lluvia distrital y ENAHO" |
| Briceño-Ávalos et al. (2025) | Serie nacional 1950–2023 y **panel regional 2014–2023**; PBI per cápita contra temperatura, lluvia, El Niño y La Niña. Temperatura negativa; lluvia no clara; **la duración de El Niño y La Niña resultó no significativa**; solo los Niños extraordinarios de 1957, 1972, 1983 y 1998 salen negativos | **Debilita el panel de PBI departamental anual**: con pocos años y agregación anual, el efecto no se detecta |
| Jury y Borbor-Ponce (2026, *Atmosphere*) | Sensibilidad del rendimiento de cultivos en la **sierra sur** (7–15° S, 70–77° O), 1961–2024; **La Niña favorece** cítricos, algodón, fruta y caña | Confirma que el signo puede invertirse por región y cultivo. Es climatología, no economía |
| Yglesias-González et al. (2023, *PLOS ONE*) | Primer estudio de caso del Niño costero 2017 sobre economía, salud y gobernanza; pide expresamente **análisis de riesgo a nivel local** | Descriptivo. Deja abierta la cuantificación |

**Dos conclusiones incómodas pero útiles:**

1. El diseño de **bienestar de hogares con ENAHO** está sustancialmente
   ocupado (Ramos-Sandoval 2026, Malpartida y Guembes 2025). Haberlo descartado
   fue correcto.
2. El diseño de **PBI departamental anual** tiene evidencia previa de que **no
   detecta el efecto** (Briceño-Ávalos 2025 con panel regional 2014–2023).
   Haberlo descartado también fue correcto, y ahora hay una cita que lo
   justifica en lugar de solo el argumento de potencia estadística.

---

## 3. Las brechas, ordenadas por si atan o no con nuestros datos

### Brecha 1 — ONI frente a ICEN a nivel subnacional ⭐ la más fuerte

**La brecha.** La literatura de "diversidad de ENSO" (Gallegati et al. 2026;
Solomou et al. 2025) establece que el Pacífico central y el oriental tienen
efectos macroeconómicos distintos, pero lo estima **entre países, a nivel
nacional, con modelos globales**. La literatura peruana, por su lado, trata
"El Niño" como un único fenómeno: dummies de evento (Briceño-Ávalos 2025), solo
temperatura (Saldarriaga 2016), o un solo episodio descrito
(Yglesias-González 2023). **Nadie estima el efecto diferencial de los dos
índices entre regiones de un mismo país.**

**Por qué el Perú es el caso, y no un caso cualquiera.** La región Niño 1+2
está literalmente frente a la costa peruana; el ENFEN mantiene un índice
oficial separado (ICEN) precisamente porque los dos fenómenos divergen; y 2017
es el experimento natural: Niño costero intenso con Pacífico central casi
neutro. El Perú no es un país más donde probar la distinción CP/EP: es el país
donde la distinción se institucionalizó.

**Qué de nuestros datos la cierra.** El panel ERA5 mensual 1991–2026 (que ya
está descargado y se tira, §1) da la variación climática local; la réplica del
ICEN se calcula desde los índices Niño 1+2 de la NOAA; la clasificación de
zonas de régimen ya está en `config.py`.

**Qué falta.** La variable económica, la serie ONI completa desde 1950, y la
réplica validada del ICEN.

**Veredicto: ata.** Es el eje de la tesis.

### Brecha 2 — El panel climático provincial peruano como producto

**La brecha.** Saldarriaga (2016) usó una grilla de 0,5° (~56 km) a nivel de
municipalidad para 2004–2010. No existe, publicado, un panel climático mensual
de las 195 provincias del Perú con normales 1991–2020 verificables, sesgo de
representación cuantificado y código abierto.

**Qué de nuestros datos la cierra.** Todo el código existe. ERA5-Land (~9 km)
para provincias ya está decidido y justificado en `METODOLOGIA.md` (muchas
provincias son más chicas que una celda de ERA5). Los centroides se calculan
desde el GeoJSON, no están tipeados a mano.

**Qué falta.** Correrlo. Son varias horas de descarga y nunca se hizo.

**Veredicto: ata, y es la única brecha que se cierra sin ningún dato externo.**
Es un capítulo de la tesis y, por separado, un *data paper*. Riesgo bajo, valor
alto, y es el insumo de las brechas 1, 3 y 4.

### Brecha 3 — Asimetría con inversión de signo entre regiones

**La brecha.** La asimetría cálido/frío está estudiada (Emediegwu 2024;
Ubilava 2017; Borrallo et al. 2024 cuestionando el supuesto estándar), y para
el Perú hay indicio climatológico de que La Niña **favorece** cultivos de la
sierra sur (Jury y Borbor-Ponce 2026). Pero nadie ha estimado si, **dentro del
mismo evento**, el efecto económico cambia de signo entre la costa norte
(exceso de lluvia, inundación) y la sierra sur (déficit hídrico).

Esa posibilidad es justamente lo que un promedio nacional destruye, y explica
por qué Briceño-Ávalos (2025) pudo no encontrar nada: si dos regiones se mueven
en direcciones opuestas, el agregado se cancela. **Esa es una hipótesis
contrastable, no una queja.**

**Qué de nuestros datos la cierra.** Zonas de régimen en `config.py`; la
reclasificación por altitud (>2000 m en zona costera → sierra) ya está
implementada y publica tanto la zona usada como la heredada.

**Veredicto: ata, condicionada a la variable económica.** Es la hipótesis que
hace interesante a la brecha 1, no una brecha aparte.

### Brecha 4 — Cuánto depende el resultado de cómo se agrega el clima

**La brecha.** Toda esta literatura elige una resolución espacial y no reporta
cuánto cambia el coeficiente si se elige otra. Saldarriaga usó ~56 km;
nosotros tendríamos ~9 km y dos niveles de agregación distintos.

**Qué de nuestros datos la cierra.** Esta es la brecha **más propia** del
repositorio: `estado.json` ya registra por corrida `elevacion_modelo_m`,
`altitud_capital_m` y `diferencia_altitud_m`, y la primera corrida mostró
diferencias menores a 50 m en 10 capitales — con la lectura, ya escrita en
`METODOLOGIA.md`, de que **la altitud por sí sola no explica el exceso de
lluvia de la normal ERA5** en capitales andinas. Con los dos niveles se puede
estimar el mismo modelo con el punto de la capital y con la media provincial, y
reportar la diferencia.

**Veredicto: ata.** No da una tesis sola, pero es un capítulo de robustez con
valor metodológico que casi nadie reporta. Convierte una limitación declarada
en un resultado.

### Brecha 5 — ¿Los umbrales de anomalía predicen emergencias?

**La brecha.** Yglesias-González et al. (2023) piden expresamente análisis de
riesgo a nivel local y señalan vacíos de preparación. Nadie ha contrastado si
umbrales de anomalía climática predicen las emergencias efectivamente
registradas por INDECI a nivel departamental o provincial.

**Qué de nuestros datos la cierra.** Los umbrales y los niveles de alerta ya
están en `config.py`, declarados provisionales y no calibrados.

**Qué falta.** Los registros de emergencias de INDECI, que son externos y cuya
accesibilidad no está verificada.

**Veredicto: ata a medias.** Es la tarea 5 del proyecto y un segundo capítulo
natural, pero depende de un dato que no controlamos. **No debe ser el eje de la
tesis**: si INDECI no publica lo necesario, se cae el trabajo entero. Como
capítulo secundario, en cambio, su fracaso no es fatal.

### Brechas que NO atan (y por qué decirlo importa)

- **Bienestar de hogares con ENAHO.** Ocupada: Ramos-Sandoval et al. (2026)
  con 2000–2018, Malpartida y Guembes (2025) con DiD y lluvia distrital para
  2017. Entrar ahí es competir, no aportar.
- **PBI departamental anual.** Briceño-Ávalos et al. (2025) ya reportan no
  significancia con panel regional. Repetirlo con menos años es predecible.
- **Redes de producción y precios mayoristas por cultivo.** Es lo que hace
  Bohorquez-Penuela et al. (2026) en Colombia y sería excelente para el Perú,
  pero exige precios mayoristas por cultivo y mercado que no tenemos ni
  sabemos si existen accesibles. **No atar con los datos es razón suficiente
  para no elegirla**, por buena que sea la idea.
- **Efectos sobre pesca.** Es el canal más característico del Perú y está poco
  estudiado en economía. Pero requiere desembarques por puerto y especie. Si
  esos datos aparecen accesibles en el BCRP, sube de categoría; hoy no está
  verificado.

---

## 4. Veredicto

El eje de la tesis es la **brecha 1** (ONI frente a ICEN a nivel subnacional),
con la **brecha 3** como hipótesis central (inversión de signo entre regiones),
la **brecha 2** como capítulo de datos y producto reutilizable, y la **brecha
4** como capítulo de robustez. La **brecha 5** queda como capítulo secundario
solo si INDECI publica lo necesario.

Eso no cambia el diseño del protocolo: lo **afila**. El panel ciudad-mes de IPC
de alimentos sigue siendo la variable dependiente; lo que cambia es que el
aporte se enuncia con precisión — no es "estimar el efecto de El Niño en el
Perú", es **"distinguir dos Niños que la literatura trata como uno, en el país
donde la distinción se definió, a una resolución espacial que nadie ha usado"**.

### Orden de trabajo que esto impone

| # | Tarea | Por qué va en ese lugar |
|---|---|---|
| 0 | **Persistir los agregados mes-año en `calcular_normales.py`** | Sin esto no hay panel y la descarga se repite. Es un cambio chico, y es gratis |
| 1 | Verificar disponibilidad del IPC por ciudad y grupo | Decide la viabilidad del eje (ver protocolo §4.1) |
| 2 | Arreglar el parser de TSM semanal y extender el ONI a 1950 | El producto está roto ahora y la serie no alcanza |
| 3 | Correr el nivel provincial | Varias horas; cierra la brecha 2 |
| 4 | Réplica del ICEN y su validación contra el IGP | Es el regresor que distingue la tesis |

Las tareas 0 y 2 son correcciones del monitor que la tesis necesita de todos
modos: **el trabajo académico y el mantenimiento del repositorio coinciden
aquí**, y conviene hacerlas en ese orden antes de escribir una línea de
estimación.

---

## 5. Referencias

- Abril, D. S. et al. (2019). Nonlinear relationship between the weather
  phenomenon El Niño and Colombian food prices. *Australian Journal of
  Agricultural and Resource Economics*.
- Ahmad, F. et al. (2019). The Impact of El Niño on Inflation in Regional
  Indonesia: Spatial Panel Approach. *Signifikan: Jurnal Ilmu Ekonomi*.
- Bohorquez-Penuela, C. et al. (2026). Heterogeneous Effects of Weather Shocks
  on Food Prices in a Country with Diverse Agriculture.
- Borrallo, F. et al. (2024). "El Niño" and "La Niña": Revisiting the impact on
  food commodity prices and euro area consumer prices. *Documentos de Trabajo*.
- Briceño-Ávalos, H. R., More-Sánchez, V. A. y Fierro-Bravo, M. (2025). Efectos
  del cambio climático sobre el bienestar. *Prohominum*.
  DOI 10.47606/acven/ph0420.
- Emediegwu, L. (2024). Assessing the Asymmetric Effect of Global Climate
  Anomalies on Food Prices: Evidence from Local Prices. *Environmental and
  Resource Economics*.
- Gallegati, M. et al. (2026). The inflationary effects of the El Niño-Southern
  Oscillation. *PLOS Climate*.
- Jury, M. R. y Borbor-Ponce, M. (2026). Regional Climate Influence on Peru
  Agricultural Yield? *Atmosphere* 17(6), 544. DOI 10.3390/atmos17060544.
- Kumar, M. S. et al. (2026). The effect of climate shocks on food price
  inflation, India. *Journal of Agriculture and Food Research*.
- Malpartida, R. y Guembes, M. (2025). Impact of Natural Disasters on Household
  Health and Education Expenditure: Evidence from El Niño Phenomenon in Peru.
  *Economía* (PUCP). DOI 10.18800/economia.202501.003.
- Marpaung, B. et al. (2019). Analysis of El Niño Impact and the Price of Food
  Commodities on Inflation. *Jurnal Ekonomi Indonesia*.
- Ramos-Sandoval, R. et al. (2026). The Effects of Extreme Weather Events on
  the Socio-Climatic Vulnerability of Peruvian Agricultural Households.
  *Sustainability* 18(7), 3477. DOI 10.3390/su18073477.
- Saldarriaga, V. (2016). Efectos de la variabilidad de la temperatura en la
  productividad y en los precios de los productos agrícolas: evidencia en Perú.
  BID. DOI 10.18235/0000522.
- Solomou, S. et al. (2025). The macroeconomic effects of El Niño diversity: a
  GVAR approach. *Climate Research*.
- Ubilava, D. (2017). The Role of El Niño Southern Oscillation in Commodity
  Price Movement and Predictability. *AJAE*; y The ENSO Effect and Asymmetries
  in Wheat Price Dynamics. *World Development*.
- Yglesias-González, M. et al. (2023). Reflections on the impact and response
  to the Peruvian 2017 Coastal El Niño event. *PLOS ONE* 18(9), e0290767.

Antecedentes macro ya citados en `PROTOCOLO.md` §11 (BCRP DT 008-2025,
BIS WP 1276, FMI WP 2025/144, IGP, Dell-Jones-Olken, Jordà, Driscoll-Kraay) no
se repiten aquí.
