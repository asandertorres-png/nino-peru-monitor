# Metodología

## Indicador del estado del ENSO

Se usa el **ONI** (Oceanic Niño Index) de la NOAA/CPC: media móvil de tres
meses de la anomalía de temperatura superficial del mar en la región Niño 3.4
(5°N–5°S, 170°O–120°O), con base climatológica móvil de 30 años. La NOAA
considera condiciones de El Niño cuando el ONI alcanza o supera +0,5 °C
durante cinco trimestres móviles consecutivos.

**Advertencia para el caso peruano.** El ONI mide el Pacífico central. El
fenómeno que afecta directamente a la costa peruana se monitorea con el
**ICEN** del ENFEN, construido sobre la región Niño 1+2, frente a la costa
norte. Ambos pueden divergir: el Niño costero de 2017 fue intenso en el Niño
1+2 con un Pacífico central casi neutro. Incorporar el ICEN es la tarea 1 del
proyecto; mientras tanto, el estado mostrado debe leerse como contexto global,
no como declaración sobre el Niño costero.

## Anomalías departamentales

Para cada departamento se toma el punto de su capital y se consulta:

- lluvia acumulada y temperatura máxima media de los últimos 30 días;
- pronóstico de lluvia acumulada a 7 días.

Se comparan con la normal **1991–2020** —periodo estándar de la OMM— del mes
en curso, calculada con el reanálisis ERA5. La anomalía de lluvia se expresa
en porcentaje respecto de la normal, y la térmica en grados de diferencia.

La normal mensual se escala proporcionalmente a la ventana de 30 días. Es una
aproximación: cuando la ventana cruza dos meses con regímenes de lluvia muy
distintos (típicamente el inicio y el fin de la temporada húmeda en la sierra),
introduce sesgo. Una versión posterior debería ponderar por días efectivos en
cada mes.

## Nivel de alerta

Escala cualitativa de 0 a 3, diferenciada por zona porque el riesgo asociado a
la fase cálida no es el mismo en todo el país: en la **costa norte** el peligro
dominante es el exceso de lluvia e inundación, mientras que en la **sierra sur
y la costa centro-sur** lo es el déficit hídrico. Un exceso térmico superior a
2 °C sobre la normal eleva el nivel en un grado.

**Estos umbrales son provisionales.** Se fijaron por criterio y no están
calibrados contra registros de daños. La tarea 5 del proyecto es validarlos
con las emergencias registradas por INDECI. Hasta entonces el mapa es una
herramienta de exploración, no un instrumento de alerta operativa.

## Limitaciones principales

1. **Representación puntual.** Un punto por departamento ignora gradientes
   altitudinales fuertes. Arequipa capital no representa el altiplano de
   Caylloma, ni Huaraz la costa de Áncash.
2. **Correlación, no causalidad.** El mapa muestra anomalías simultáneas al
   evento ENSO; no establece que el evento las haya causado. Atribuir requiere
   un diseño estadístico explícito sobre series largas.
3. **Rezagos.** El impacto de El Niño sobre la lluvia en el Perú no es
   instantáneo y varía por región; comparar el estado del océano con el clima
   del mismo mes subestima relaciones rezagadas.

## Fuentes

- NOAA Climate Prediction Center, Oceanic Niño Index.
- ERA5 (ECMWF), servido a través de la API de archivo de Open-Meteo.
- Límites departamentales: datos públicos de contornos del Perú.
