/**
 * Hoja resumen de una pagina: operacionalizacion, consistencia y metodologia.
 *
 * Salida: docs/tesis/Hoja_resumen_matrices.docx
 *
 * Es una plancha de revision, no un reemplazo de los documentos completos:
 * para que las tres matrices entren en una sola hoja hay que recortar texto,
 * y el recorte se nota. Las versiones completas estan en
 * docs/tesis/Matriz_operacionalizacion.docx y en los markdown de docs/tesis/.
 *
 * Uso:  node scripts/tesis/hoja_resumen_docx.js
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, TableRow,
  AlignmentType, PageOrientation, BorderStyle,
} = require("docx");
const { AZUL, GRIS, GRIS_OSCURO, LETTER, p, celda, encabezado, tabla } =
  require("./docx_util.js");

const AUTOR = "Alexander Torres Uchupe";
const CASA = "UNSAAC · Escuela Profesional de Economía";
const TITULO =
  "Niño del Pacífico central y Niño costero: efecto diferenciado sobre la " +
  "inflación de alimentos en 26 ciudades del Perú, 2010–2026";

// Margenes reducidos: la hoja tiene que entrar en una pagina.
const MARGEN = 620;
const UTIL = LETTER.height - 2 * MARGEN; // 14600 en horizontal

// --------------------------------------------------------- consistencia

const A_CON = [1000, 4200, 4200, 5200]; // 14600
const CONSISTENCIA = [
  ["General",
   "¿Cuál es el efecto diferenciado del Niño del Pacífico central (ONI) y del Niño costero (ICEN) sobre la inflación de alimentos de las ciudades del Perú, según la exposición económica de cada ciudad, 2010–2026?",
   "Determinar el efecto diferenciado del Niño del Pacífico central y del Niño costero sobre la inflación de alimentos de las ciudades del Perú, según la exposición económica de cada ciudad, 2010–2026.",
   "El efecto del Niño costero es mayor que el del Pacífico central en las ciudades de la costa norte, y la magnitud del efecto de ambos aumenta con la exposición económica de la ciudad."],
  ["Esp. 1",
   "¿Cuál es el efecto de las anomalías climáticas locales sobre la inflación de alimentos?",
   "Estimar el efecto de las anomalías locales de precipitación y temperatura sobre la inflación de alimentos por ciudad.",
   "Las anomalías locales afectan la inflación de alimentos, alcanzando su efecto máximo dentro de los dieciocho meses posteriores al shock."],
  ["Esp. 2",
   "¿Cuál de los dos índices oceánicos —ONI o ICEN— explica mejor la inflación de alimentos?",
   "Comparar el poder explicativo del ONI y del ICEN-réplica sobre la inflación de alimentos por ciudad.",
   "En las ciudades de la costa norte, el ICEN explica la inflación de alimentos mejor que el ONI."],
  ["Esp. 3",
   "¿En qué medida difiere el efecto entre regiones según la exposición económica?",
   "Contrastar la heterogeneidad regional del efecto según la exposición económica de cada ciudad.",
   "El efecto aumenta con el peso del sector primario en el VAB y del alimento en la canasta, y difiere en signo entre la costa norte y la sierra sur."],
  ["Esp. 4",
   "¿En qué medida se reduce la integración de los mercados de alimentos entre ciudades?",
   "Determinar en qué medida se reduce la integración de los mercados de alimentos entre ciudades durante los episodios.",
   "La integración de los mercados de alimentos entre las ciudades del Perú disminuye durante los episodios cálidos del ENSO."],
];

// ------------------------------------------------------ operacionalizacion

const A_OPE = [1150, 2950, 8500, 2000]; // 14600
const OPERACION = [
  ["X. Shock de oferta de origen ENSO", "D1. Magnitud del shock climático local",
   "1. Anomalía estandarizada de precipitación mensual   ·   2. Anomalía estandarizada de temperatura máxima mensual",
   "Razón (σ)"],
  ["", "D2. Estado del océano",
   "3. Índice ONI, región Niño 3.4 (Pacífico central)   ·   4. Índice ICEN-réplica, región Niño 1+2 (Niño costero)",
   "Razón (°C)"],
  ["", "D3. Exposición económica",
   "5. Participación de agropecuario y pesca en el VAB departamental   ·   6. Participación del alimento en la canasta del IPC",
   "Razón (%)"],
  ["Y. Precios de alimentos al consumidor urbano", "D1. Nivel de precios",
   "7. Variación mensual del IPC de alimentos   ·   8. Variación a doce meses del IPC de alimentos",
   "Razón (%)"],
  ["", "D2. Volatilidad",
   "9. Desviación estándar móvil de doce meses de la inflación de alimentos",
   "Razón"],
  ["", "D3. Integración de mercados",
   "10. Correlación de la inflación de alimentos con la de las demás ciudades",
   "Razón"],
];

// ---------------------------------------------------------- metodologia

const A_MET = [3650, 3650, 3650, 3650]; // 14600
const METODOLOGIA = [
  ["Diseño",
   "Enfoque cuantitativo · Tipo aplicada · Nivel explicativo · Diseño no experimental, longitudinal de panel (ex post facto) · Método hipotético-deductivo"],
  ["Población y muestra",
   "26 ciudades del ámbito urbano del IPC del INEI, enero 2010 – septiembre 2026 · Muestra censal · ≈ 5 200 observaciones · Unidad de análisis: la ciudad-mes"],
  ["Técnica e instrumento",
   "Técnica: análisis documental de fuentes secundarias de acceso abierto · Instrumento: ficha de registro de datos secundarios"],
  ["Procesamiento y análisis",
   "Proyecciones locales en panel con aumento de rezagos y efectos fijos · Jackknife de medio panel · Inferencia con agrupamiento transversal · Python"],
];

// ------------------------------------------------------------------ hoja

const T_CAB = 17;  // tamanio de cabecera de tabla, en medios puntos
const T_TXT = 17;  // tamanio del texto de tabla

function filaCon(f, i) {
  const fondo = i === 0 ? "EDEDED" : (i % 2 ? GRIS : undefined);
  return new TableRow({
    children: [
      celda(f[0], A_CON[0], { negrita: true, tam: T_TXT, alineacion: AlignmentType.CENTER,
                              fondo: i === 0 ? GRIS_OSCURO : GRIS }),
      celda(f[1], A_CON[1], { tam: T_TXT, fondo }),
      celda(f[2], A_CON[2], { tam: T_TXT, fondo }),
      celda(f[3], A_CON[3], { tam: T_TXT, fondo }),
    ],
  });
}

function filaOpe(f, i) {
  const fondo = i % 2 ? GRIS : undefined;
  return new TableRow({
    children: [
      celda(f[0], A_OPE[0], { negrita: true, tam: 15, alineacion: AlignmentType.CENTER,
                              fondo: f[0] ? GRIS_OSCURO : fondo }),
      celda(f[1], A_OPE[1], { negrita: true, tam: T_TXT, fondo }),
      celda(f[2], A_OPE[2], { tam: T_TXT, fondo }),
      celda(f[3], A_OPE[3], { tam: T_TXT, alineacion: AlignmentType.CENTER, fondo }),
    ],
  });
}

const hoja = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 20 },
      children: [new TextRun({ text: CASA, size: 17, color: "595959", font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 100 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 4 } },
      children: [new TextRun({ text: TITULO, size: 22, bold: true, color: AZUL, font: "Arial" })],
    }),

    p("MATRIZ DE CONSISTENCIA", { negrita: true, tam: 19, color: AZUL, despues: 70 }),
    tabla(A_CON, [
      encabezado(["", "Problema", "Objetivo", "Hipótesis"], A_CON),
      ...CONSISTENCIA.map(filaCon),
    ]),

    p("MATRIZ DE OPERACIONALIZACIÓN DE VARIABLES", { negrita: true, tam: 19, color: AZUL, antes: 180, despues: 70 }),
    tabla(A_OPE, [
      encabezado(["Variable", "Dimensión", "Indicadores", "Escala"], A_OPE),
      ...OPERACION.map(filaOpe),
    ]),

    p("METODOLOGÍA", { negrita: true, tam: 19, color: AZUL, antes: 180, despues: 70 }),
    tabla(A_MET, [
      new TableRow({
        children: METODOLOGIA.map((m) =>
          celda(m[0], 3650, { negrita: true, tam: T_CAB, color: "FFFFFF",
                              fondo: AZUL, alineacion: AlignmentType.CENTER })),
      }),
      new TableRow({
        children: METODOLOGIA.map((m) => celda(m[1], 3650, { tam: T_TXT })),
      }),
    ]),

    p(`Autor: ${AUTOR}   ·   Hoja resumen; las versiones completas están en los documentos `
      + `Matriz_operacionalizacion.docx y Matrices_antecedentes_marco_teorico.docx`,
      { alineacion: AlignmentType.CENTER, tam: 15, cursiva: true, antes: 180 }),
  ],
};

const doc = new Document({
  creator: AUTOR,
  title: "Hoja resumen: operacionalización, consistencia y metodología",
  description: TITULO,
  styles: { default: { document: { run: { font: "Arial", size: 20 } } } },
  sections: [hoja],
});

const salida = path.join(__dirname, "..", "..", "docs", "tesis",
                         "Hoja_resumen_matrices.docx");

Packer.toBuffer(doc).then((buffer) => {
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  fs.writeFileSync(salida, buffer);
  console.log(`hoja resumen -> ${salida} (${(buffer.length / 1024).toFixed(1)} KB)`);
});
