# Modelo económico

Lo que faltaba. El marco teórico tenía los pilares, pero discursivos: ninguno
terminaba en una ecuación de la que saliera la especificación empírica. Sin
eso, el trabajo se lee como estadística aplicada sobre un tema climático, y no
como economía.

Este documento cierra esa brecha: un modelo de equilibrio parcial, simple y
transparente, del que se derivan **las tres predicciones que la tesis
contrasta** y la ecuación que efectivamente se estima. No pretende ser un
aporte teórico: pretende que las hipótesis tengan de dónde salir.

---

## 1. El mercado de alimentos de una ciudad

Ciudad `c`, mes `t`. Variables en logaritmos salvo donde se indique.

**Oferta local.** Una parte del alimento que consume la ciudad se produce en su
zona de influencia:

> qˢ_ct = α_c + η_S · p_ct − **γ_c · a_ct**

- `η_S > 0`: elasticidad precio de la oferta local.
- `a_ct ≥ 0`: **magnitud del shock climático adverso**, en desviaciones
  estándar respecto de la normal 1991–2020. Es el indicador 1 de la matriz de
  operacionalización.
- `γ_c > 0`: **sensibilidad de la producción local al shock**. Es el parámetro
  que la exposición económica aproxima.

**Demanda.**

> qᵈ_ct = δ_c − η_D · p_ct + ψ · y_ct

- `η_D > 0`: elasticidad precio de la demanda. **Para alimentos es baja**, y
  esa inelasticidad es la razón por la que el precio, y no la cantidad, absorbe
  el ajuste. De aquí sale la justificación económica de que la variable
  dependiente sea el IPC de **alimentos** y no el general.

**Comercio con el resto del país.** La ciudad importa del resto del país cuando
la brecha de precios supera el costo de transacción:

> m_ct = φ_ct · (p_ct − p̄_t − τ_ct)  si p_ct − p̄_t > τ_ct,  y  m_ct = 0 en caso contrario

- `p̄_t`: precio nacional de referencia.
- `τ_ct`: **costo unitario de transacción** (transporte, mermas, tiempo).
- `φ_ct ≥ 0`: **grado de integración del mercado**, es decir cuánto responde el
  flujo comercial a la brecha de precios.
- La condición `p_ct − p̄_t > τ_ct` **es la banda neutral** de Goodwin y Piggott
  (2001): dentro de ella no hay arbitraje y la ciudad queda, de hecho, en
  autarquía.

**Equilibrio.** Igualando oferta más importaciones a demanda:

> **p_ct = [ δ_c − α_c + ψ·y_ct + γ_c·a_ct + φ_ct·(p̄_t + τ_ct) ] / (η_S + η_D + φ_ct)**

## 2. Estática comparativa: de dónde salen las hipótesis

Las cuatro derivadas que siguen **son** las hipótesis de la tesis. No se
postularon y luego se buscó teoría: salen de la ecuación de arriba.

### (i) El efecto del shock sobre el precio

> **∂p_ct / ∂a_ct = γ_c / (η_S + η_D + φ_ct) > 0**

Un shock climático adverso eleva el precio local. **Y el denominador dice por
qué el efecto es mayor en alimentos:** con demanda inelástica, `η_D` es
pequeño, el denominador es pequeño y el mismo shock produce un movimiento de
precio mayor que en un bien con demanda elástica. → **Hipótesis específica 1.**

### (ii) El efecto crece con la exposición económica

> **∂²p_ct / ∂a_ct ∂γ_c = 1 / (η_S + η_D + φ_ct) > 0**

Cuanto más sensible es la producción local al clima, mayor el efecto sobre el
precio. `γ_c` no se observa, pero se aproxima con la **participación del sector
agropecuario y pesquero en el VAB departamental** (indicador 5): donde el
primario pesa más, la producción local pesa más en el abastecimiento y el
shock muerde más. → **Hipótesis específica 3.**

### (iii) El efecto decrece con la integración del mercado

> **∂²p_ct / ∂a_ct ∂φ_ct = − γ_c / (η_S + η_D + φ_ct)² < 0**

**Esta es la derivada más importante del modelo.** Un mercado bien integrado
amortigua el shock local, porque el resto del país compensa el faltante. Uno
segmentado no.

Y aquí está el doble mecanismo del Niño costero, que en el marco teórico se
afirmaba y aquí queda derivado: el fenómeno **sube τ** y, al cortar vías,
**baja φ**. Las dos cosas empujan el precio local en la misma dirección:

> **∂p_ct / ∂τ_ct = φ_ct / (η_S + η_D + φ_ct) > 0**

→ **Hipótesis específica 4** (la integración cae durante el evento) y el
mecanismo de la **hipótesis general**.

### (iv) Almacenamiento: por qué la respuesta no es lineal

Con inventarios `I_ct`, el shock efectivo sobre el mercado no es `a_ct` sino
`a_ct − ΔI_ct`: el stock amortigua. Pero la restricción de no negatividad
`I_ct ≥ 0` hace que ese amortiguamiento **desaparezca de golpe** cuando las
existencias se agotan. De ahí la convexidad y la asimetría: el mismo shock
produce respuestas muy distintas según el nivel de stock (Wright y Williams,
1982; Cafiero et al., 2014). → **Análisis de robustez**, no hipótesis
específica, por la simplificación de la matriz.

### (v) Del precio de alimentos al índice general

> π^gen_ct = w_c · π^alim_ct + (1 − w_c) · π^resto_ct

donde `w_c` es el **peso del alimento en la canasta de la ciudad**, el
indicador 6. El traspaso al índice general es proporcional a ese peso, y por
eso es mayor en economías —y en ciudades— donde el alimento pesa más. Es el
mecanismo que Furceri et al. (2016) identifican entre países, aplicado entre
ciudades.

## 3. Del modelo a la ecuación que se estima

El modelo es estático; la realidad tiene rezagos de producción y expectativas.
Tomando diferencias, permitiendo dinámica y agregando efectos fijos:

> **π_ct = μ_c + δ_t + Σ_k β_k · a_c,t−k + Σ_k θ_k · (ENSO_{t−k} × E_c) + u_ct**

donde `π_ct` es la inflación mensual de alimentos de la ciudad, `μ_c` y `δ_t`
los efectos fijos de ciudad y de periodo, `E_c` la exposición económica y

> **β_k ≈ γ_c / (η_S + η_D + φ_c)** distribuido entre rezagos.

La versión de proyecciones locales estima esa misma relación horizonte por
horizonte, para trazar la función impulso-respuesta.

**Advertencia de identificación que hay que escribir en la tesis.** El
coeficiente `β` es un **compuesto** de cuatro parámetros estructurales: la
sensibilidad productiva `γ`, las dos elasticidades `η_S` y `η_D`, y la
integración `φ`. **El diseño no los separa.** Por lo tanto la tesis no puede
afirmar "la elasticidad precio de la oferta agrícola es X": solo puede afirmar
cuánto se mueve el precio ante el shock, y cómo esa respuesta varía con la
exposición y con la integración. Confundir el coeficiente reducido con un
parámetro estructural es el error que esta sección existe para evitar.

## 4. Interpretación económica de los resultados

Un coeficiente sin traducción económica no dice nada. Estas son las tres
lecturas que la tesis debe reportar.

**(a) En puntos porcentuales.** Como `a` está en desviaciones estándar y `π` en
porcentaje, `β_k` es una **semielasticidad**: un shock de una desviación
estándar eleva la inflación mensual de alimentos en `β_k` puntos porcentuales
`k` meses después. El efecto acumulado a `h` meses es `Σ_{k≤h} β_k`.

**(b) En el índice general.** El efecto sobre la inflación general de la ciudad
es aproximadamente `w_c · Σβ_k`, con `w_c` el peso del alimento en su canasta,
y **incompleto**: Jalil y Tamayo (2011) estiman para el Perú un traspaso
parcial que toma entre uno y seis trimestres.

**(c) En soles, que es la lectura que importa.** Si el hogar promedio de la
ciudad `c` gasta `G_c` soles mensuales en alimentos, el costo mensual del shock
es aproximadamente

> **ΔG_c ≈ G_c × (Σβ_k / 100)**

y conviene expresarlo además como **porcentaje del gasto total del hogar**,
porque esa es la magnitud que un lector no econometrista entiende y la que
permite comparar entre ciudades de distinto ingreso. **Un resultado reportado
solo en coeficientes es un resultado a medio terminar.**

## 5. Implicancias de política que el modelo sostiene

Tres, y las tres salen de una derivada, no de la opinión del autor.

1. **Para la política monetaria.** Es un shock de oferta, y el manual dice
   mirar más allá de los efectos de primera vuelta salvo que haya segunda. Pero
   la heterogeneidad importa: un agregado nacional que promedia una costa norte
   inundada con una sierra sur seca **subestima ambos**, y puede llevar a no
   reaccionar donde sí correspondía.
2. **Para la focalización de transferencias.** La incidencia depende de `w_c`:
   donde el alimento pesa más en la canasta, el mismo shock de precios cuesta
   más bienestar. El peso del alimento es observable y **puede usarse para
   priorizar**.
3. **Para la infraestructura, y es la implicancia menos obvia.** Como
   `∂p_ct/∂τ_ct > 0` y `∂²p/∂a∂φ < 0`, **mantener la vía abierta es política de
   estabilización de precios**. No es una obra pública más: es el instrumento
   que reduce el coeficiente que la tesis estima. Esa conexión entre
   infraestructura vial y estabilidad de precios de alimentos es un resultado
   del modelo, no un añadido.

## 6. Lo que el modelo no hace

1. **Es equilibrio parcial.** No hay efectos sobre ingreso, empleo ni demanda
   agregada, y el coeficiente estimado los absorbe sin distinguirlos.
2. **No da bienestar.** Un alza del precio perjudica al comprador neto y
   beneficia al vendedor neto; el IPC no observa esa posición. La tesis mide
   **precios**, no bienestar, y la lectura en soles de §4(c) es un **costo
   para el consumidor urbano**, no un efecto neto sobre la sociedad.
3. **No identifica parámetros estructurales**, por lo dicho en §3.
4. **Trata `φ` y `τ` como exógenos al shock para la estática comparativa**,
   cuando en rigor el evento los mueve. Esa endogeneidad es precisamente lo que
   la hipótesis 4 contrasta, y por eso se estima aparte en lugar de suponerse.

## 7. Referencias

- Cafiero, C., Bobenrieth, E., Bobenrieth, J. y Wright, B. (2014). Maximum
  Likelihood Estimation of the Standard Commodity Storage Model. *AJAE*.
- Enke, S. (1951); Samuelson, P. (1952); Takayama, T. y Judge, G. (1964).
  Modelo de equilibrio espacial de precios.
- Furceri, D., Loungani, P., Simon, J. y Wachter, S. (2016). Global food prices
  and domestic inflation. *Oxford Economic Papers*.
- Goodwin, B. y Piggott, N. (2001). Spatial Market Integration in the Presence
  of Threshold Effects. *AJAE*.
- Jalil, M. y Tamayo Zea, E. (2011). Pass-through of International Food Prices
  to Domestic Inflation. DOI 10.13043/DYS.67.4.
- McNew, K. (1996). Spatial Market Integration: Definition, Theory and
  Evidence. *ARER*.
- Wright, B. y Williams, J. (1982). The Economic Role of Commodity Storage.
  *The Economic Journal*.
