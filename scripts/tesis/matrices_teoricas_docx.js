/**
 * Genera el Word con la matriz de antecedentes y la matriz del marco teorico.
 *
 * Salida: docs/tesis/Matrices_antecedentes_marco_teorico.docx
 *
 * Fuente de verdad del contenido: docs/tesis/ANTECEDENTES.md y
 * docs/tesis/MARCO_TEORICO.md. Si cambia algo alli, cambiarlo aqui y
 * regenerar.
 *
 * Uso:  node scripts/tesis/matrices_teoricas_docx.js
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, TableRow,
  WidthType, ShadingType, AlignmentType, HeadingLevel, PageOrientation,
  BorderStyle,
} = require("docx");
const {
  AZUL, GRIS, GRIS_OSCURO, LETTER, MARGEN, UTIL_H,
  p, celda, encabezado, salto, tabla,
} = require("./docx_util.js");

const AUTOR = "Alexander Torres Uchupe";
const CASA = "Universidad Nacional de San Antonio Abad del Cusco";
const TITULO =
  "Niño del Pacífico central y Niño costero: efecto diferenciado sobre la " +
  "inflación de alimentos en 26 ciudades del Perú, 2010–2026";

// ------------------------------------------------- matriz de antecedentes

// [nivel, autor y anio, titulo abreviado, metodologia, resultados, aporte o vacio]
const ANTECEDENTES = [
  // --------------------------------- internacionales
  ["Internacional", "Cashin, Mohaddes y Raissi (2015)",
   "Fair Weather or Foul? The Macroeconomic Effects of El Niño",
   "Marco dinámico multipaís (GVAR), 21 modelos país o región, 1979Q2–2013Q1",
   "Estima la transmisión macroeconómica internacional de El Niño, con exposiciones directas e indirectas",
   "Antecedente macro de referencia. Deja abierto todo lo subnacional"],
  ["Internacional", "McNew (1996)",
   "Spatial Market Integration: Definition, Theory and Evidence",
   "Modelo punto-espacio de comercio interregional; maíz del Misisipi durante la inundación de 1993",
   "Los mayores costos de transporte redujeron la integración y, por esa vía, la transferencia de shocks entre regiones",
   "Funda el mecanismo de costos de transacción: sostiene la hipótesis 4 y la mitad del mecanismo de la 3"],
  ["Internacional", "Ubilava (2017)",
   "ENSO y la dinámica de precios de commodities",
   "43 precios mensuales de commodities y anomalías de TSM de la región Niño 3.4",
   "ENSO afecta la dinámica de precios, con asimetrías entre fases",
   "Funda la asimetría. No trata el IPC ni el nivel subnacional"],
  ["Internacional", "Abril et al. (2019)",
   "Relación no lineal entre El Niño y los precios de alimentos en Colombia",
   "Series de precios de alimentos; énfasis en el evento 2015-16",
   "La relación entre ENSO y precios de alimentos es no lineal",
   "Funda la no linealidad de la respuesta"],
  ["Internacional", "Letta et al. (2021)",
   "Weather shocks, traders' expectations and food prices",
   "Panel distrital mensual de precios mayoristas, India 2004–2017; explota el rezago entre la anomalía y el shock de oferta",
   "La sequía eleva los precios durante el crecimiento del cultivo, antes de la pérdida de cosecha; las expectativas anticipan más del 80 % del impacto",
   "Funda el canal de expectativas y obligó a reformular la hipótesis 1 del proyecto"],
  ["Internacional", "Emediegwu (2024)",
   "Efecto asimétrico de las anomalías climáticas globales sobre precios locales",
   "Modelos STAR variables en el tiempo; más de 1 100 mercados en 36 países de África subsahariana",
   "ENSO afecta cerca de la mitad de los precios, con asimetría fuerte y persistencia; la respuesta debe ser subregional, no regional",
   "Funda la hipótesis de asimetría y el argumento de desagregación espacial"],
  ["Internacional", "Gallegati et al. (2026); Solomou et al. (2025)",
   "Diversidad de ENSO: Pacífico central frente a Pacífico oriental",
   "GVAR y wavelets sobre inflación nacional de varios países",
   "Los tipos de Pacífico central y oriental difieren en estructura, intensidad y perfil temporal, y sus efectos sobre la inflación no son los mismos",
   "Antecedente directo del objetivo 2. Lo estima ENTRE países; esta tesis lo estima DENTRO de uno"],
  ["Internacional", "Yilmazkuday (2025)",
   "El Niño, La Niña and Inflation",
   "Proyecciones locales, 188 países, 1970–2023, con efectos fijos y tendencias por país",
   "Las condiciones tipo La Niña elevan todas las medidas de inflación; los países en desarrollo se ven más afectados en la de alimentos; los efectos crecen con el tiempo",
   "Respalda la técnica elegida y advierte contra suponer el signo del efecto"],
  ["Internacional", "Arango-Castillo et al. (2025)",
   "Anomalías de temperatura y precipitación e inflación en México",
   "Panel regional; ARDL y proyecciones locales; anomalías ponderadas por población contra la norma de 30 años",
   "Sin efecto estadístico de corto plazo; en el largo plazo solo la precipitación importa",
   "Antecedente metodológico más cercano. Advierte que un no-resultado es posible y publicable"],

  // --------------------------------- nacionales
  ["Nacional", "Saldarriaga (2016), BID",
   "Variabilidad de la temperatura, productividad y precios agrícolas en el Perú",
   "ENAHO 2004–2010 con grilla climática de 0,5°; variación interanual dentro de cada municipalidad",
   "Una desviación estándar de temperatura reduce la producción entre US$ 170 y 190 por hectárea; las temperaturas inusualmente cálidas dañan más que las frías",
   "Antecedente nacional más cercano en precios. Solo temperatura, precios en finca y hasta 2010"],
  ["Nacional", "Crofils, Gallic y Vermandel (2024), JEEM",
   "The dynamic effects of weather shocks on agricultural production",
   "Proyecciones locales sobre producción agrícola mensual del Perú; shock medido como exceso de calor o de lluvia",
   "Caída de ~5 % mensual hasta cuatro meses consecutivos; respuesta mayor en selva y en temporada de crecimiento; a nivel macro eleva la inflación",
   "El antecedente más cercano que existe. Deja abierto el IPC por ciudad, la separación ONI/ICEN y la integración de mercados"],
  ["Nacional", "Calero y Rodríguez (2026), PUCP",
   "Efectos variables en el tiempo de shocks climáticos en el Perú",
   "TVP-VAR con volatilidad estocástica; dos shocks, el fenómeno El Niño y desviaciones de temperatura",
   "Ambos operan como shocks de oferta: el PBI cae 0,8 pp y la inflación sube 0,25 pp; pesca −5,0 pp; efectos mayores en 1998Q2 y 2017Q2",
   "Confirma el canal inflacionario y obliga a replantear el aporte: ya no es descubrir el efecto sino medir su distribución"],
  ["Nacional", "BCRP DT 008-2025; BIS WP 1276",
   "ENSO and its Economic Impact in the Peruvian Economy",
   "Modelo semi-estructural; datos mensuales de BCRPData, 1994M1–2019M12",
   "ENSO deja una huella de shock de oferta; la respuesta del sector primario es más inmediata, mayor y persistente",
   "Agregado nacional, sin precios regionales"],
  ["Nacional", "Tambet y Stopnitzky (2021), AJAE",
   "Climate Adaptation and Conservation Agriculture among Peruvian Farmers",
   "Tres rondas de la Encuesta Nacional Agropecuaria con datos climáticos de largo plazo; shocks georreferenciados de lluvia anormal",
   "Los productores ajustan prácticas según el shock: menos conservación de suelos tras lluvia alta, más uso de pesticidas tras sequía",
   "Evidencia peruana de respuesta endógena del productor. Señala la ENA como fuente no considerada"],
  ["Nacional", "Andrián et al. (2024); Martin (2016), BID",
   "El Niño en la Región Andina",
   "VAR con El Niño tratado como variable exógena",
   "Crecimiento entre −0,1 y −3,4 pp, con el Perú entre los más afectados; inflación entre +0,7 y +3,5 pp. Las diferencias de estructura económica son cruciales",
   "La conclusión sobre estructura económica es, textualmente, la justificación de medir donde esa estructura varía: dentro del país"],
  ["Nacional", "Briceño-Ávalos et al. (2025)",
   "Efectos del cambio climático sobre el bienestar",
   "Serie nacional 1950–2023 y panel regional 2014–2023; MCO y método generalizado de momentos",
   "La duración de El Niño y La Niña no resulta significativa; solo los eventos extraordinarios de 1957, 1972, 1983 y 1998 salen negativos",
   "Debilita el panel departamental anual y refuerza la elección de frecuencia mensual"],

  // --------------------------------- locales
  ["Local", "Canedo-Rosso et al. (2020)",
   "Drought and Agricultural Production in the Central Andes",
   "Relación entre precipitación de verano y fases de ENSO; rendimientos de quinua y papa",
   "Menor rendimiento de quinua y papa en años de El Niño fuerte y muy fuerte; relación negativa entre lluvia de verano y fase cálida",
   "Sostiene el mecanismo de déficit hídrico en la sierra sur, que es la zona de signo potencialmente opuesto a la costa norte"],
  ["Local", "Arana-Ruedas et al. (2023)",
   "ENSO y sequía agrícola en el valle del Mantaro",
   "Índice SPEI en cuatro provincias y seis estaciones, 1990–2021, contrastado con el ONI",
   "El 70 % de los eventos de sequía agrícola ocurrió con ENSO presente; la correlación de severidad varía entre 9 % y 70 %",
   "Cuantifica el vínculo ENSO–sequía–agricultura en la sierra peruana"],
  ["Local", "Ponce (2020, World Development; 2023, JDS)",
   "Variabilidad climática intraestacional en los Andes peruanos",
   "Censos agrarios 1994 y 2012 con clima distrital; efectos fijos que permiten heterogeneidad de parámetros por subregión",
   "Efectos heterogéneos entre subregiones y, en particular, ningún efecto directo entre los hogares del sur, más aislados e indígenas",
   "Antecedente económico más próximo a la sierra sur. Su diseño inspira la especificación, y su resultado advierte de un posible no-resultado en el sur"],
  ["Local", "Imfeld et al. (2020)",
   "Climatología y tendencias en los Andes del sur del Perú",
   "Datos de estación controlados y homogeneizados más datos en grilla, 1965/66–2017/18",
   "ENSO tiene efectos modificadores sobre precipitación y temperatura, y produce tendencias mayores en las máximas",
   "Candidato para validar las normales ERA5 en el sur, que es la validación que el proyecto declara bloqueada"],
  ["Local", "Estudio ricardiano del Altiplano (2021)",
   "Impacto económico del cambio climático en la quinua orgánica, Puno",
   "Enfoque ricardiano; encuesta a 237 agricultores en Cabana, Capachica e Ilave; clima de SENAMHI Puno",
   "El impacto de las variables agroclimáticas sobre el ingreso resultó marginal en la campaña 2015-2016",
   "Antecedente local, económico y en español. Advierte de un posible no-resultado; su diseño transversal es criticable por variables omitidas"],
];

// ------------------------------------------------ matriz del marco teorico

// [pilar, teoria o enfoque, autores, postulado central, prediccion, hipotesis]
const MARCO = [
  ["I", "El clima como variación identificadora",
   "Hsiang (2016); Dell, Jones y Olken (2014); Blanc y Schlenker (2017); Mérel y Gammans (2018)",
   "La variación meteorológica dentro de una misma unidad espacial es aleatoria y exógena una vez absorbido lo invariante, de modo que permite identificar efectos y no solo correlaciones. Pero los efectos fijos absorben señal y el ruido de medición sesga los coeficientes hacia abajo",
   "P10. La agregación puntual del clima atenúa el coeficiente estimado hacia cero",
   "Supuesto de identificación y H6"],
  ["II", "Almacenamiento competitivo con expectativas racionales",
   "Wright y Williams (1982); Deaton y Laroque (1992, 1996); Cafiero et al. (2011, 2014); Gouel y Legrand (2025, 2026); Wright (2009)",
   "El inventario amortigua el excedente pero la restricción de no negatividad no amortigua el déficit. Sin existencias, el precio debe subir abruptamente para vaciar el mercado, y el mismo shock de producción da respuestas muy distintas según el nivel de stock",
   "P1. Respuesta convexa a la magnitud. P2. El déficit mueve más que el excedente. P3. El efecto es mayor con existencias bajas",
   "H4 y H4b (robustez)"],
  ["III", "Expectativas de los comerciantes y almacenamiento intraanual",
   "Letta et al. (2021)",
   "Los precios incorporan la información sobre el shock antes de que el daño físico se materialice. El rezago entre la señal pública y la realización permite separar ambos canales",
   "P4. Parte del efecto anticipa la realización del shock",
   "H1 (reformulada por este pilar)"],
  ["IV", "Equilibrio espacial de precios con costos de transacción",
   "Enke (1951); Samuelson (1952); Takayama y Judge (1964); Goodwin y Piggott (2001); McNew (1996); Roehner (1996); Zhu (2018)",
   "Los precios de regiones que comercian se mueven juntos solo mientras el diferencial supere los costos de transacción. Al elevarse esos costos, la banda neutral se ensancha, el mercado se segmenta y el shock deja de transmitirse",
   "P5. La magnitud crece con la exposición y el aislamiento. P6. La integración cae durante el evento. P7. La transmisión es no lineal",
   "H2 (mecanismo) y H5"],
  ["V", "Traspaso a la inflación y efectos de segunda vuelta",
   "Jalil y Tamayo (2011); Furceri et al. (2016); Anand, Ding y Tulin (2014)",
   "El traspaso del precio de alimentos a la inflación general es incompleto y rezagado, y es mayor donde el alimento pesa más en la canasta y las expectativas están menos ancladas",
   "P8. Traspaso incompleto, de uno a seis trimestres",
   "Justifica el IPC como variable dependiente y fija el horizonte de H1"],
  ["VI", "Diversidad de ENSO: Pacífico central y oriental",
   "Gallegati et al. (2026); Solomou et al. (2025); criterio del ENFEN para el ICEN",
   "Los tipos de El Niño del Pacífico central y del oriental difieren en estructura espacial, intensidad y perfil temporal, y por tanto sus efectos económicos no tienen por qué coincidir. El ENFEN mantiene el ICEN precisamente por esa divergencia",
   "P9. ONI e ICEN tienen efectos distintos, y la diferencia varía por región",
   "H3, que es la hipótesis que da el título"],
];

// ------------------------------------------------------------------ anchos

// Suman UTIL_H = 13680
const A_ANT = [1250, 1950, 2350, 2600, 2900, 2630];
const A_MAR = [760, 1900, 2250, 3640, 2730, 2400];

// ------------------------------------------------------------------ secciones

const seccionPortada = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 60 },
      children: [new TextRun({ text: CASA, size: 20, color: "595959", font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 400 },
      children: [new TextRun({ text: "Escuela Profesional de Economía", size: 20, color: "595959", font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 360 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: AZUL, space: 8 } },
      children: [new TextRun({
        text: "MATRIZ DE ANTECEDENTES Y MATRIZ DEL MARCO TEÓRICO",
        size: 28, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 },
      shading: { type: ShadingType.CLEAR, fill: GRIS, color: "auto" },
      border: {
        top: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
        bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
        left: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
        right: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
      },
      children: [new TextRun({ text: TITULO, size: 24, bold: true, font: "Arial" })],
    }),
    p(`Autor: ${AUTOR}`, { alineacion: AlignmentType.CENTER, tam: 20, despues: 400 }),

    p("Contenido", { negrita: true, despues: 100 }),
    p("1. Matriz de antecedentes — 21 trabajos en tres niveles: internacional, nacional y local. " +
      "Cada fila declara la metodología empleada, los resultados principales y el aporte o el vacío " +
      "que deja para esta investigación.", { despues: 100 }),
    p("2. Matriz del marco teórico — seis pilares, uno por eslabón de la cadena que va del océano " +
      "al índice de precios. Cada fila declara el postulado central, la predicción contrastable que " +
      "de él se deriva y la hipótesis que sustenta.", { despues: 240 }),

    p("Criterio de inclusión", { negrita: true, despues: 100 }),
    p("Un antecedente entra si permite situar el aporte de la tesis, y un pilar teórico entra si " +
      "genera una predicción contrastable con los datos disponibles. Los trabajos que solo ilustran " +
      "el tema, sin método ni resultado que contrastar, quedan fuera de la matriz y se mencionan en " +
      "el texto del capítulo.", { despues: 200 }),
    p("Advertencia sobre la capa local: es en su mayoría agronómica y climatológica, no económica. " +
      "Fija el mecanismo físico que la tesis supone y debe presentarse como tal, no como evidencia " +
      "económica.", { cursiva: true, tam: 20 }),
  ],
};

function filasAgrupadas(datos, anchos) {
  const filas = [];
  let nivelPrevio = null;
  datos.forEach((f, i) => {
    if (f[0] !== nivelPrevio) {
      nivelPrevio = f[0];
      filas.push(new TableRow({
        children: [celda(`ANTECEDENTES DE NIVEL ${f[0].toUpperCase()}`,
                         anchos.reduce((a, b) => a + b, 0),
                         { negrita: true, tam: 16, fondo: GRIS_OSCURO })],
      }));
    }
    const fondo = i % 2 ? GRIS : undefined;
    filas.push(new TableRow({
      children: [
        celda(f[1], anchos[1], { negrita: true, tam: 15, fondo }),
        celda(f[2], anchos[2], { tam: 14, cursiva: true, fondo }),
        celda(f[3], anchos[3], { tam: 14, fondo }),
        celda(f[4], anchos[4], { tam: 14, fondo }),
        celda(f[5], anchos[5], { tam: 14, fondo }),
      ],
    }));
  });
  return filas;
}

// Para la tabla de antecedentes se usan cinco columnas; el nivel va en fila propia.
const A_ANT5 = [0, 2050, 2550, 2800, 3100, 3180];

const seccionAntecedentes = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, spacing: { after: 60 },
      children: [new TextRun({
        text: "1. Matriz de antecedentes", size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("21 trabajos · 9 internacionales · 7 nacionales · 5 locales", { cursiva: true, tam: 18, despues: 140 }),
    tabla(A_ANT5.slice(1), [
      encabezado(["Autor y año", "Título", "Metodología", "Resultados principales",
                  "Aporte o vacío que deja"], A_ANT5.slice(1)),
      ...filasAgrupadas(ANTECEDENTES, A_ANT5),
    ]),
  ],
};

const seccionMarco = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      heading: HeadingLevel.HEADING_1, spacing: { after: 60 },
      children: [new TextRun({
        text: "2. Matriz del marco teórico", size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("6 pilares · la cadena océano → clima local → oferta → precio regional → IPC urbano",
      { cursiva: true, tam: 18, despues: 140 }),
    tabla(A_MAR, [
      encabezado(["Pilar", "Teoría o enfoque", "Autores principales", "Postulado central",
                  "Predicción contrastable", "Hipótesis que sustenta"], A_MAR),
      ...MARCO.map((f, i) => new TableRow({
        children: [
          celda(f[0], A_MAR[0], { negrita: true, tam: 17, alineacion: AlignmentType.CENTER,
                                  fondo: i % 2 ? GRIS : GRIS_OSCURO }),
          celda(f[1], A_MAR[1], { negrita: true, tam: 15, fondo: i % 2 ? GRIS : undefined }),
          celda(f[2], A_MAR[2], { tam: 13, fondo: i % 2 ? GRIS : undefined }),
          celda(f[3], A_MAR[3], { tam: 14, fondo: i % 2 ? GRIS : undefined }),
          celda(f[4], A_MAR[4], { tam: 14, fondo: i % 2 ? GRIS : undefined }),
          celda(f[5], A_MAR[5], { tam: 14, negrita: true, alineacion: AlignmentType.CENTER,
                                  fondo: i % 2 ? GRIS : undefined }),
        ],
      })),
    ]),
    p("Nota. Las predicciones P1 a P10 corresponden a la tabla de síntesis del marco teórico. " +
      "Un pilar que no genere una predicción contrastable con los datos disponibles no entra en la " +
      "matriz: sería ornamento y no fundamento.",
      { antes: 180, tam: 16 }),
  ],
};

// ------------------------------------------------------------------- documento

const doc = new Document({
  creator: AUTOR,
  title: "Matriz de antecedentes y matriz del marco teórico",
  description: TITULO,
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } },
      heading1: {
        run: { font: "Arial", size: 26, bold: true, color: AZUL },
        paragraph: { spacing: { before: 280, after: 120 }, keepNext: true },
      },
    },
  },
  sections: [seccionPortada, seccionAntecedentes, seccionMarco],
});

const salida = path.join(__dirname, "..", "..", "docs", "tesis",
                         "Matrices_antecedentes_marco_teorico.docx");

Packer.toBuffer(doc).then((buffer) => {
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  fs.writeFileSync(salida, buffer);
  console.log(`${ANTECEDENTES.length} antecedentes y ${MARCO.length} pilares -> `
              + `${salida} (${(buffer.length / 1024).toFixed(1)} KB)`);
});
