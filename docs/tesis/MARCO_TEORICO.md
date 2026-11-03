# Marco teórico

Construido sobre literatura verificada, no sobre autoridad recordada. Cada
pilar se incluye por una razón: **genera una predicción contrastable con
nuestros datos**. Un marco teórico que no restringe la especificación empírica
es decoración, y en una tesis se nota.

Dos resultados de esta revisión **modifican hipótesis** del
[PROTOCOLO.md](PROTOCOLO.md): el canal de expectativas (§4) obliga a
reformular H1, y la teoría de integración espacial (§5) convierte H2 de
conjetura en predicción con mecanismo. Está marcado donde ocurre.

---

## 1. La arquitectura: una cadena, no un modelo

No existe un modelo único que vaya del océano al IPC. Lo que hay es una cadena
de cuatro eslabones, y **cada eslabón tiene su propia teoría**:

```
ENSO                anomalía climática      oferta                 precio        IPC de
(océano, exógeno) → local (lluvia, temp) → agropecuaria local → regional → alimentos urbano
      │                      │                      │                  │            │
      §6                     §2                     §3                 §5           §6
             identificación        almacenamiento       integración      traspaso
                                   y expectativas        espacial         al IPC
```

Presentar la cadena así tiene una ventaja metodológica: deja ver que la tesis
estima la **forma reducida de toda la cadena**, no un eslabón. Eso es una
limitación (no se descompone el canal) y a la vez la razón de que el diseño sea
creíble (el primer eslabón es exógeno).

---

## 2. Pilar I — El clima como variación identificadora

**Qué aporta.** El fundamento de por qué una regresión de precios sobre clima
puede leerse causalmente.

Hsiang (2016) formaliza la relación entre clima y tiempo meteorológico desde
una perspectiva econométrica y deriva **las condiciones bajo las cuales la
variación meteorológica identifica exactamente los efectos del clima**. Dell,
Jones y Olken (2014) establecen el diseño de referencia: explotar variación
exógena en el tiempo dentro de una misma unidad espacial permite identificar
la amplitud de canales, los **efectos heterogéneos entre tipos de localidad**
y los efectos no lineales. Kolstad y Moore (2019) revisan y comparan las
alternativas: corte transversal, panel lineal y no lineal, diferencias largas y
partición de la variación.

Blanc y Schlenker (2017) explican por qué el panel es apropiado: los efectos
fijos de grupo absorben toda la variación invariante en el tiempo, de modo que
la estimación descansa en **desviaciones del clima respecto de su media, que
son aleatorias y exógenas**.

**Tres advertencias que esta literatura impone y que hay que acatar:**

1. **Atenuación por error de medición.** Blanc y Schlenker (2017) advierten que
   los efectos fijos de grupo absorben buena parte de la señal de las variables
   climáticas, de modo que **la razón señal-ruido cae** y el ruido en la
   construcción de la variable climática produce **sesgo hacia abajo en los
   coeficientes**.

   > Esto es el fundamento teórico de la brecha 4 de
   > [BRECHAS.md](BRECHAS.md): representar un departamento entero con el punto
   > de su capital **es** error de medición, y la teoría predice el signo del
   > sesgo —hacia cero—. No es una limitación a disculpar: es una hipótesis
   > contrastable, y tenemos los dos niveles de agregación para contrastarla.

2. **El panel estima una mezcla de corto y largo plazo.** Mérel y Gammans
   (2018) muestran que las estimaciones de panel son una **combinación convexa**
   de los coeficientes de corto y largo plazo, y que la asimetría de los datos
   climáticos condicional a la localidad puede sesgarlas **en cualquier
   dirección**. Ghanem et al. (2026) añaden que comparar diferencias largas con
   efectos fijos para medir adaptación puede ser engañoso, porque ninguno de los
   dos estimadores es consistente para su parámetro buscado.

   Para esta tesis el efecto de interés **es** el de corto plazo (respuesta de
   precios a un shock), así que la objeción de adaptación pesa poco. Pero hay
   que decirlo explícitamente en lugar de ignorarla.

3. **Cuidado con los efectos fijos bidireccionales.** Kropko y Kubinec (2020)
   muestran que el modelo de efectos fijos en dos vías **combina variación
   intra-unidad y transversal de un modo que vuelve los coeficientes difíciles
   de interpretar**, y que bajo la lectura habitual —un único efecto de X sobre
   Y controlando heterogeneidad de unidad y shocks de tiempo— la especificación
   está mal identificada.

   > Consecuencia directa para nosotros: la especificación A del protocolo
   > (efectos fijos de ciudad y de año-mes) debe reportarse **junto con** la
   > versión de una sola vía, y hay que decir qué variación identifica cada
   > coeficiente. No basta poner `i.ciudad i.mes_anio` y seguir.

**Inferencia.** Gospodinov et al. (2025) encuentran que **los errores estándar
agrupados en una sola dimensión producen distorsiones de tamaño** y que una
especificación aditiva de efectos fijos **no controla adecuadamente los efectos
de tiempo comunes**; usan efectos fijos interactivos con inferencia bootstrap.
Thombs (2022) muestra que, con N y T grandes, los efectos fijos con errores
robustos o corregidos por panel son sesgados ante heterogeneidad de pendientes
y dependencia transversal, y que el estimador de **efectos comunes
correlacionados** (CCE) se comporta mejor a medida que T crece.

> Nuestro panel tiene N = 26 y T ≈ 200: **T grande, N chico**. Es exactamente el
> régimen donde estas advertencias aplican. Refuerza la decisión de
> Driscoll–Kraay más bootstrap del protocolo §6.5, y añade una tarea: reportar
> también un estimador robusto a dependencia transversal (CCE o efectos fijos
> interactivos) como contraste.

## 3. Pilar II — Almacenamiento competitivo: de dónde sale la no linealidad

**Qué aporta.** La razón teórica de que el precio responda de forma **convexa,
asimétrica y dependiente del estado** a un mismo shock de oferta. Sin este
pilar, "asimetría" es una corazonada; con él, es una predicción.

El modelo de almacenamiento competitivo con expectativas racionales se remonta
a Gustafson (1958) y fue desarrollado por Wright y Williams (1982), quienes
muestran que el almacenamiento **no estabiliza la producción** —la vuelve más
variable— y modifica la distribución del precio de forma compleja en lugar de
reducir simplemente su dispersión. Deaton y Laroque (1992, 1995, 1996)
cuestionaron su relevancia empírica porque no reproducía la autocorrelación
observada de los precios; Cafiero et al. (2011) responden mostrando que con una
grilla suficientemente fina el modelo **sí** genera esos niveles de correlación
serial, y Bobenrieth et al. (2020) y Gouel et al. (2025) lo rehabilitan
incorporando tendencias y respuesta de oferta. Gouel y Legrand (2026) revisan
el estado del arte.

**El mecanismo que importa para esta tesis.** Cafiero et al. (2014) lo enuncian
con precisión: cuando no hay inventarios disponibles para amortiguar el efecto
de un shock negativo de oferta sobre el consumo, **los precios deben subir
abruptamente** para inducir el ajuste que vacía el mercado; y por eso **el mismo
shock de producción puede dar respuestas de precio muy distintas** según haya o
no existencias suficientes. Wright (2009) lo dice a escala global: cuando las
existencias agregadas caen a sus mínimos factibles, **los precios se vuelven
muy sensibles a shocks pequeños**.

**Predicciones contrastables:**

- **P1 (convexidad).** La respuesta del precio a la anomalía climática es no
  lineal: shocks grandes producen efectos más que proporcionales.
- **P2 (asimetría).** Un déficit de oferta mueve el precio más que un excedente
  equivalente, porque el almacenamiento amortigua el excedente pero la
  restricción de no negatividad de inventarios no amortigua el déficit. **Esta
  es la base teórica de H4**, que en el protocolo estaba enunciada sin
  fundamento.
- **P3 (dependencia del estado).** El efecto es mayor cuando el nivel de
  existencias es bajo. Sin datos de inventarios, admite una aproximación: el
  efecto debería ser mayor cuando el shock llega **tras una secuencia de meses
  ya desfavorables**, o fuera de la ventana inmediata post-cosecha.

Benirschka y Binkley (1995) añaden la dimensión espacial: el almacenamiento
óptimo ocurre en las **zonas productoras** y el tiempo en almacén crece con la
distancia al mercado. Relevante para el Perú, donde la distancia entre zona
productora y ciudad de consumo es grande y variable.

## 4. Pilar III — Expectativas: el hallazgo que obliga a reformular H1

**Qué aporta.** El eslabón que el protocolo tenía mal.

Letta et al. (2021, *AJAE*) parten de la teoría de almacenamiento
**intra-anual** y estudian un panel de precios mayoristas mensuales de
alimentos a nivel distrital en India, 2004–2017. Explotan el rezago entre una
anomalía climática y el shock de oferta correspondiente para aislar las
reacciones de precio causadas por **cambios en expectativas**. Encuentran que
las condiciones de sequía **elevan los precios durante el periodo de
crecimiento del cultivo, antes de que la pérdida de cosecha se haya
materializado**, y que las expectativas anticipan **más del 80 % del impacto
total** del precio.

> **Esto contradice H1 tal como está escrita en el protocolo** ("efecto máximo
> rezagado entre 3 y 9 meses"). Si el canal de expectativas domina, el efecto
> aparece **antes** de la cosecha, no después, y un modelo que solo mire rezagos
> post-cosecha lo atribuirá mal.

**Y para el Perú el argumento es más fuerte que en India.** El ENSO no es una
sequía sorpresiva: **se pronostica con meses de anticipación**, y el ENFEN
—comité de IMARPE, SENAMHI, DHN, IGP, INDECI y ANA— emite **pronunciamientos
oficiales fechados** sobre el estado y perspectivas del fenómeno. Es decir: hay
una **señal pública, datada y observable** que precede a la realización física
del shock.

Eso abre una posibilidad que ningún trabajo revisado explota y que nuestros
datos permiten:

> **Separar el canal de señal del canal de realización.** El índice oceánico
> (ONI, ICEN) es la señal que anticipa; la anomalía climática local de ERA5 es
> la realización. Incluir ambos permite estimar cuánto del movimiento de precios
> ocurre por anticipación y cuánto por el daño efectivo. El rezago entre uno y
> otro **es** la variación identificadora, igual que en Letta et al.

**Predicción P4.** Parte del efecto sobre precios aparece contemporáneamente o
con rezago corto respecto del índice oceánico, **antes** de que la anomalía
local se materialice, y el componente de expectativas debería ser mayor donde
los mercados están mejor informados y más integrados.

## 5. Pilar IV — Equilibrio espacial: el doble mecanismo de El Niño

**Qué aporta.** El mecanismo por el cual el efecto **cambia de magnitud y
posiblemente de signo entre regiones**, que es el corazón de la tesis.

La teoría es el modelo de equilibrio espacial de precios de
**Enke–Samuelson–Takayama–Judge** (Enke 1951; Samuelson 1952; Takayama y Judge
1964): un equilibrio parcial donde regiones separadas comercian sujetas a la
**condición de equilibrio espacial**, una forma débil de la ley de un solo
precio que establece que no hay ganancias de arbitraje entre regiones. En
teoría, cuando hay comercio entre regiones, las señales de exceso de oferta y
demanda se transfieren a los precios y estos se mueven juntos.

Pero esa transmisión **depende de los costos de transacción**, y de ahí sale lo
importante. Goodwin y Piggott (2001) modelan la integración con umbrales: existe
una **banda neutral** que representa los costos de transacción, dentro de la
cual los precios no se ajustan entre sí; con modelos de autorregresión y
cointegración con umbral encuentran ajustes **mucho más rápidos** que los que
sugieren los modelos que ignoran el umbral. McNew (1996) muestra que los precios
espaciales se relacionan de forma **no lineal**, contra la mayor parte de la
literatura que usaba modelos lineales.

**Y aquí está la cita que sostiene toda la tesis.** McNew (1996) examina la
integración del mercado de maíz a lo largo del Misisipi **durante la inundación
del Medio Oeste de 1993** y encuentra que los **mayores costos de transporte
durante ese periodo redujeron significativamente el grado de integración y, por
esa vía, disminuyeron la transferencia de shocks de exceso de demanda entre
regiones**.

> Es exactamente el mecanismo peruano, documentado en otro país y con una
> inundación. El Niño costero **no solo desplaza la oferta: destruye carretera**.
> Por lo tanto opera por **dos canales simultáneos**:
>
> 1. **Canal de oferta.** Menos producto → precio sube.
> 2. **Canal de costos de transacción.** Vías cortadas → la banda neutral se
>    ensancha → el mercado local se segmenta → el precio local sube **más** y
>    se transmite **menos** al resto del país.
>
> Los dos empujan el precio local en la misma dirección, y el segundo explica
> por qué el efecto puede ser grande localmente y pequeño en el agregado
> nacional. **Esto convierte H2 de conjetura en predicción con mecanismo**, y da
> una explicación de por qué Briceño-Ávalos et al. (2025) no detectan el efecto
> con un panel regional anual.

Roehner (1996) formaliza el arbitraje espacial bajo incertidumbre —el modelo
"Enke-Samuelson estocástico"— y analiza el efecto de costos de transporte
cambiantes sobre el volumen de comercio, **la volatilidad de precios y los
diferenciales espaciales de precio**, variables que el modelo determinista no
puede definir. Zhu (2018) muestra que la integración de precios está fuertemente
influida por las características de la red de transporte, **especialmente cuando
hay restricciones de capacidad en los enlaces**.

> Relevante de forma incómodamente literal para el Perú: buena parte de la costa
> depende de **un** eje vial. Una red con un enlace crítico es el caso límite de
> "restricción de capacidad en un enlace".

**Predicciones contrastables:**

- **P5 (heterogeneidad con mecanismo).** La magnitud del efecto crece con la
  exposición climática **y** con el aislamiento de la ciudad respecto de las
  zonas productoras.
- **P6 (segmentación endógena, nueva).** La **integración entre ciudades cae
  durante el evento**. Esto es contrastable por separado: la correlación de
  precios entre pares de ciudades, o el ancho de la banda neutral, debería
  aumentar durante los episodios. **Es una hipótesis nueva que el protocolo no
  tenía** y que no requiere ningún dato adicional al panel de precios.
- **P7 (no linealidad de la transmisión).** Los precios no se relacionan
  linealmente entre regiones; los modelos de umbral son la especificación
  correcta, no un refinamiento opcional.

## 6. Pilar V — Traspaso al IPC y efectos de segunda vuelta

**Qué aporta.** La justificación de que la variable dependiente sea el IPC de
alimentos y no un precio en finca, y el puente con la política monetaria.

Jalil y Tamayo (2011) estudian el traspaso de precios internacionales de
alimentos a la inflación doméstica en **Brasil, Chile, Colombia, México y el
Perú**: el traspaso a la inflación general toma **entre uno y seis trimestres**
según el país, **es incompleto**, y parte de la transmisión se asocia a alzas de
la inflación subyacente, tanto de forma directa como por posibles **efectos de
segunda vuelta**, lo que implica un papel para la política monetaria.

Furceri et al. (2016, *Oxford Economic Papers*) encuentran que un aumento de
10 % en la inflación internacional de alimentos eleva la inflación doméstica en
unos 0,5 puntos porcentuales al año en economías avanzadas, con efecto
**mucho mayor en economías emergentes**; lo atribuyen a la **mayor participación
de los alimentos en la canasta** y a expectativas de inflación **menos
ancladas**. Anand, Ding y Tulin (2014) estiman efectos de segunda vuelta grandes
en India, por la alta participación del alimento en el gasto y por el papel de
la inflación de alimentos **en la formación de expectativas y en la negociación
salarial**.

> Dos implicaciones para la tesis. Primera: el traspaso es **incompleto y
> rezagado**, así que no hay que esperar coeficientes de uno ni efectos
> instantáneos. Segunda: la participación del alimento en la canasta **varía
> entre ciudades peruanas**, y es por tanto una dimensión de heterogeneidad
> adicional, de naturaleza **económica y no climática**, que conviene medir y no
> confundir con la exposición al fenómeno.

## 7. Pilar VI — Por qué dos índices y no uno

No es teoría económica, pero es el supuesto físico que sostiene la pregunta.

El ONI mide la región Niño 3.4 (Pacífico central) y el ICEN la región Niño 1+2
(Pacífico oriental, frente a la costa peruana); el ENFEN mantiene el segundo
precisamente porque los fenómenos divergen, y 2017 es el caso donde divergieron.
La literatura macroeconómica de **"diversidad de ENSO"** (Gallegati et al. 2026;
Solomou et al. 2025) ya establece que los tipos de Pacífico central y oriental
difieren en estructura espacial, intensidad y perfil temporal, y que sus efectos
sobre la inflación **no son los mismos** — pero lo estima entre países.

La tesis traslada esa distinción, ya validada a escala macro, al interior del
país donde se definió.

---

## 8. Síntesis: de la teoría a la especificación

Esta tabla es el puente. Si una fila no se puede contrastar con nuestros datos,
el pilar correspondiente sobra.

| # | Predicción teórica | Pilar | Hipótesis | Qué la falsaría |
|---|---|---|---|---|
| P1 | Respuesta convexa a la magnitud del shock | Almacenamiento | H1' | Términos no lineales no significativos |
| P2 | Déficit mueve más que excedente | Almacenamiento | H4 | Simetría no rechazada |
| P3 | Efecto mayor con existencias bajas | Almacenamiento | H4b (nueva) | Sin dependencia del estado |
| P4 | Parte del efecto **anticipa** la realización | Expectativas | **H1 reformulada** | Efecto solo post-cosecha |
| P5 | Magnitud crece con exposición y aislamiento | Espacial | H2 | Heterogeneidad no significativa |
| P6 | **La integración cae durante el evento** | Espacial | **H5 (nueva)** | Integración estable |
| P7 | Transmisión no lineal, con banda neutral | Espacial | H5b | Modelos lineales suficientes |
| P8 | Traspaso incompleto y rezagado al IPC | Traspaso | — (supuesto) | Traspaso completo e inmediato |
| P9 | ONI e ICEN tienen efectos distintos por región | Diversidad ENSO | H3 | Ajuste indistinguible |
| P10 | Agregación puntual **atenúa** el coeficiente | Identificación | **H6 (nueva)** | Coeficientes iguales en ambos niveles |

### Cambios que esto impone al protocolo

1. **H1 se reformula.** De "efecto máximo rezagado 3–9 meses" a: *el efecto
   tiene un componente de anticipación, ligado al índice oceánico y a los
   pronunciamientos del ENFEN, y un componente de realización, ligado a la
   anomalía local; el primero puede dominar.* Esto cambia la especificación: el
   índice y la anomalía local entran **juntos**, no como alternativas.
2. **H4 gana fundamento y una extensión** (dependencia del estado, P3).
3. **H5 es nueva**: la integración entre ciudades cae durante el evento. Se
   contrasta solo con el panel de precios, sin datos adicionales.
4. **H6 es nueva**: el sesgo de agregación atenúa hacia cero, con signo
   predicho por la teoría. Convierte la brecha 4 en hipótesis.
5. **La inferencia se endurece**: además de Driscoll–Kraay y bootstrap, un
   estimador robusto a dependencia transversal, por el régimen T grande y N
   chico.
6. **La especificación de dos vías se reporta con cuidado**, junto con la de una
   vía, declarando qué variación identifica cada coeficiente.

## 9. Lo que la teoría NO da, y conviene no finjir que da

1. **No hay equilibrio general.** La cadena es de equilibrio parcial. Efectos
   sobre ingreso, empleo y demanda agregada quedan fuera, y el coeficiente
   estimado los absorbe sin distinguirlos.
2. **No hay bienestar.** Un alza del precio de alimentos perjudica a los hogares
   compradores netos y beneficia a los vendedores netos; el signo del efecto de
   bienestar depende de esa posición, que el IPC no observa. La tesis mide
   **precios, no bienestar**, y no debe deslizarse a conclusiones de bienestar.
3. **No se descompone el canal.** Oferta, costos de transacción y expectativas
   empujan en la misma dirección. La forma reducida los suma. Separarlos exigiría
   datos de inventarios, de estado de la red vial y de precios mayoristas por
   zona productora, que no tenemos (ver BRECHAS.md).
4. **La exogeneidad de ENSO no resuelve todo.** Resuelve que el shock no lo causa
   la economía peruana. No resuelve la autocorrelación, la dependencia espacial,
   ni la coincidencia con otros shocks nacionales.

---

## 10. Referencias

**Identificación y econometría del clima**

- Blanc, É. y Schlenker, W. (2017). The Use of Panel Models in Assessments of
  Climate Impacts on Agriculture. *Review of Environmental Economics and
  Policy*.
- Dell, M., Jones, B. y Olken, B. (2014). What Do We Learn from the Weather?
  The New Climate-Economy Literature. *Journal of Economic Literature* 52(3).
- Ghanem, D. et al. (2026). To what extent can long-differencing capture
  climate adaptation?
- Gospodinov, N. et al. (2025). The economic impact of low- and high-frequency
  temperature changes. *European Economic Review*.
- Hsiang, S. (2016). Climate Econometrics. NBER Working Paper.
- Kolstad, C. y Moore, F. (2019). Estimating the Economic Impacts of Climate
  Change Using Weather Observations. NBER Working Paper.
- Kropko, J. y Kubinec, R. (2020). Interpretation and identification of
  within-unit and cross-sectional variation in panel data models. *PLoS ONE*.
- Mérel, P. y Gammans, M. (2018). Climate Econometrics: Can the Panel Approach
  Account for Long-Run Adaptation? *American Journal of Agricultural
  Economics*.
- Thombs, R. P. (2022). A Guide to Analyzing Large N, Large T Panel Data.
  *Socius*.

**Almacenamiento competitivo y expectativas**

- Benirschka, M. y Binkley, J. (1995). Optimal Storage and Marketing Over Space
  and Time. *American Journal of Agricultural Economics*.
- Bobenrieth, E. et al. (2020). Putting the Empirical Commodity Storage Model
  Back on Track. *American Journal of Agricultural Economics*.
- Cafiero, C. et al. (2011). The empirical relevance of the competitive storage
  model. *Journal of Econometrics*.
- Cafiero, C. et al. (2014). Maximum Likelihood Estimation of the Standard
  Commodity Storage Model: Evidence from Sugar Prices. *AJAE*.
- Deaton, A. y Laroque, G. (1992, 1995, 1996). Trabajos sobre precios de
  commodities y almacenamiento, cuya crítica empírica responden Cafiero et al.
  (2011).
- Gouel, C. y Legrand, N. (2026). Storage and the Economics of Commodity Price
  Stabilization. *Annual Review of Resource Economics*.
- Gouel, C. y Legrand, N. (2025). The role of storage in commodity markets:
  Indirect inference based on grain data. *Quantitative Economics*.
- Letta, M. et al. (2021). Weather shocks, traders' expectations, and food
  prices. *American Journal of Agricultural Economics*.
- Wright, B. (2009). International Grain Reserves and Other Instruments to
  Address Volatility in Grain Markets. *World Bank Research Observer*.
- Wright, B. y Williams, J. (1982). The Economic Role of Commodity Storage.
  *The Economic Journal*.

**Equilibrio espacial e integración de mercados**

- Enke, S. (1951); Samuelson, P. (1952); Takayama, T. y Judge, G. (1964).
  Modelo de equilibrio espacial de precios.
- Goodwin, B. y Piggott, N. (2001). Spatial Market Integration in the Presence
  of Threshold Effects. *American Journal of Agricultural Economics*.
- McNew, K. (1996). Spatial Market Integration: Definition, Theory, and
  Evidence. *Agricultural and Resource Economics Review*.
  DOI 10.1017/S1068280500000010.
- Roehner, B. (1996). The Role of Transportation Costs in the Economics of
  Commodity Markets. *AJAE*. DOI 10.2307/1243707.
- Zhu, I. Y. (2018). Spatial Price Integration in Competitive Markets with
  Capacitated Transportation Networks.

**Traspaso a la inflación**

- Anand, R., Ding, D. y Tulin, V. (2014). Food Inflation in India: The Role for
  Monetary Policy. IMF.
- Furceri, D., Loungani, P., Simon, J. y Wachter, S. (2016). Global food prices
  and domestic inflation: some cross-country evidence. *Oxford Economic
  Papers*.
- Jalil, M. y Tamayo Zea, E. (2011). Pass-through of International Food Prices
  to Domestic Inflation During and After the Great Recession: Evidence from a
  Set of Latin American Economies. DOI 10.13043/DYS.67.4.

**Diversidad de ENSO y antecedentes peruanos:** en
[BRECHAS.md](BRECHAS.md) §5 y [PROTOCOLO.md](PROTOCOLO.md) §11.
