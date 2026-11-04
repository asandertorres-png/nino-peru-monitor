/**
 * Genera el documento Word con el titulo y la matriz de operacionalizacion.
 *
 * Salida: docs/tesis/Matriz_operacionalizacion.docx
 *
 * La fuente de verdad del contenido es docs/tesis/OPERACIONALIZACION.md y la
 * seccion 1 de docs/tesis/PROTOCOLO.md. Si cambia una ficha alli, hay que
 * cambiarla aqui y volver a generar.
 *
 * NOTA SOBRE LA CONVENCION DEL PROYECTO. CLAUDE.md pide Python estandar sin
 * dependencias externas. Esta es la unica pieza en Node, y la razon es que el
 * entregable es un .docx con tablas y el paquete docx de npm esta preinstalado
 * en el entorno. No es parte del monitor ni de su flujo diario: solo produce
 * un documento de la tesis.
 *
 * Uso:  node scripts/tesis/matriz_docx.js
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, HeadingLevel, PageOrientation,
  BorderStyle, VerticalAlign, PageBreak,
} = require("docx");

// ---------------------------------------------------------------- constantes

const TITULO =
  "Niño del Pacífico central y Niño costero: efecto diferenciado sobre la " +
  "inflación de alimentos en 26 ciudades del Perú, 2010–2026";

const AUTOR = "Alexander Torres Uchupe";
const CASA = "Universidad Nacional de San Antonio Abad del Cusco";

const {
  AZUL, GRIS, GRIS_OSCURO, LETTER, MARGEN, UTIL_V, UTIL_H,
  p, celda, encabezado, salto, tabla,
} = require("./docx_util.js");

// --------------------------------------------- datos de la matriz: variable X

// [dimension, codigo, indicador, definicion/formula, unidad y escala, fuente, hipotesis]
const FILAS_X = [
  ["D1 Magnitud", "X1", "Anomalía estandarizada de precipitación",
   "A_pp(c,t) = [PP(c,t) − μ_pp(c,m)] / σ_pp(c,m), base 1991–2020",
   "σ · Razón", "ERA5 / ERA5-Land (Open-Meteo)", "H1, H2, H6"],
  ["D1 Magnitud", "X2", "Anomalía estandarizada de temperatura máxima",
   "A_tx(c,t) = [TX(c,t) − μ_tx(c,m)] / σ_tx(c,m), base 1991–2020",
   "σ · Razón", "ERA5 / ERA5-Land", "H1, H2, H6"],

  ["D2 Signo", "X3", "Exceso de lluvia", "A⁺_pp(c,t) = máx[A_pp(c,t), 0]",
   "σ · Razón", "ERA5 / ERA5-Land", "H4"],
  ["D2 Signo", "X4", "Déficit de lluvia", "A⁻_pp(c,t) = máx[−A_pp(c,t), 0]",
   "σ · Razón", "ERA5 / ERA5-Land", "H4"],
  ["D2 Signo", "X5", "Exceso de calor", "A⁺_tx(c,t) = máx[A_tx(c,t), 0]",
   "σ · Razón", "ERA5 / ERA5-Land", "H4"],

  ["D3 Persistencia", "X6", "Racha de meses consecutivos sobre umbral",
   "Meses consecutivos terminados en t con |A(c,·)| ≥ 1, por signo. Umbral 1σ, convencional; contraste externo: criterio ENFEN de 3 meses",
   "Meses · Razón", "ERA5, NOAA/CPC", "H4b"],
  ["D3 Persistencia", "X7", "Shock acumulado a 3, 6 y 12 meses",
   "S_k(c,t) = Σ A(c,t−j), j = 0…k−1, con k = 3, 6, 12",
   "σ acumuladas · Razón", "ERA5, NOAA/CPC", "H4b"],

  ["D4 Anticipación", "X8", "ONI rezagado",
   "ONI(t−k), k = 0…12. Media móvil trimestral de la anomalía de TSM de la región Niño 3.4, base 1991–2020, criterio NOAA",
   "°C · Razón", "NOAA/CPC", "H1, H3"],
  ["D4 Anticipación", "X9", "ICEN-réplica rezagado",
   "ICEN*(t) = (1/3) Σ a₁₊₂(t−j), j = 0…2, donde a₁₊₂ es la anomalía mensual de TSM de la región Niño 1+2",
   "°C · Razón", "NOAA/CPC (Niño 1+2)", "H1, H3"],
  ["D4 Anticipación", "X10", "Aviso del ENFEN",
   "Indicadora = 1 en el mes de un pronunciamiento que declara o eleva el estado de alerta. Único indicador estrictamente informacional de la matriz",
   "Dicotómica · Nominal", "Comunicados del ENFEN", "H1"],
  ["D4 Anticipación", "X11", "Antelación del aviso",
   "Días entre el aviso (X10 = 1) y el primer mes con |A(c,·)| ≥ 1 en la unidad c. Puede ser negativa, y ese caso es informativo",
   "Días · Intervalo", "ENFEN, ERA5", "H1"],

  ["D5 Exposición económica", "X12", "Peso del sector primario en el VAB departamental",
   "E1(d) = [VAB agropecuario(d) + VAB pesca(d)] / VAB total(d)",
   "% · Razón", "INEI, cuentas departamentales", "H2"],
  ["D5 Exposición económica", "X13", "Peso del alimento en la canasta del IPC de la ciudad",
   "E2(c) = ponderación de la división 01 (alimentos y bebidas no alcohólicas) en la estructura del IPC de la ciudad c",
   "% · Razón", "INEI, ponderaciones del IPC", "H2"],
  ["D5 Exposición económica", "X14", "Sensibilidad climática estimada (exposición continua)",
   "β(c) de A_pp(c,τ) = α(c) + β(c)·ONI(τ) + ε, estimado SOLO en 1991–2020, fuera del periodo de estimación",
   "Coeficiente · Razón", "Derivado de ERA5 y NOAA", "H2"],
  ["D5 Exposición económica", "X15", "Aislamiento respecto de zonas productoras",
   "Distancia o índice de conectividad entre la ciudad y su principal zona abastecedora",
   "km o índice · Razón", "Por definir", "H2, H5"],

  ["D6 Calendario productivo", "X16", "Fase del calendario agrícola de la zona abastecedora",
   "Categórica: siembra, crecimiento, cosecha, poscosecha. Interactúa con X1–X5",
   "4 categorías · Nominal", "MIDAGRI", "H4b"],
];

// --------------------------------------------- datos de la matriz: variable Y

const FILAS_Y = [
  ["D1 Nivel y tendencia", "Y1", "Inflación mensual de alimentos",
   "π(c,t) = ln[IPC_alim(c,t)] − ln[IPC_alim(c,t−1)]",
   "% · Razón", "INEI, IPC de 26 ciudades", "H1–H4"],
  ["D1 Nivel y tendencia", "Y2", "Inflación a 12 meses",
   "π¹²(c,t) = ln[IPC_alim(c,t)] − ln[IPC_alim(c,t−12)]",
   "% · Razón", "INEI", "H1–H4"],
  ["D1 Nivel y tendencia", "Y3", "Nivel acumulado del logaritmo del índice",
   "p(c,t+h) − p(c,t−1), con p = ln(IPC_alim). Es la dependiente de las proyecciones locales: interesa cuánto más caro está el alimento h meses después, no la tasa de ese mes",
   "Logaritmo · Razón", "INEI", "H1, H2"],

  ["D2 Volatilidad", "Y4", "Desviación estándar móvil de 12 meses",
   "Desviación estándar de π(c,·) en la ventana de los 12 meses terminados en t",
   "% · Razón", "Derivado de Y1", "H4b"],
  ["D2 Volatilidad", "Y5", "Varianza condicional GARCH",
   "h(c,t) de un GARCH(1,1) sobre π(c,t). Con T ≈ 200 por ciudad es estimable pero justo; se reporta como contraste de Y4",
   "Varianza · Razón", "Derivado de Y1", "H4b"],

  ["D3 Picos", "Y6", "Indicador de pico",
   "1[π(c,t) > q₉₀(π(c,·))], con el percentil calculado sobre la distribución PROPIA de la ciudad, para no confundir ciudad volátil con mes extremo",
   "Dicotómica · Nominal", "Derivado de Y1", "H4b"],
  ["D3 Picos", "Y7", "Magnitud del exceso sobre el percentil 90",
   "máx[π(c,t) − q₉₀(π(c,·)), 0]",
   "% · Razón", "Derivado de Y1", "H4b"],

  ["D4 Traspaso", "Y8", "Elasticidad del IPC general respecto del de alimentos",
   "λ en: Δln IPC_gen(c,t) = κ(c) + λ·Δln IPC_alim(c,t) + controles. Referencia: traspaso incompleto de 1 a 6 trimestres (Jalil y Tamayo, 2011)",
   "Coeficiente · Razón", "INEI, BCRP", "Supuesto P8"],
  ["D4 Traspaso", "Y9", "Elasticidad del IPC subyacente respecto del de alimentos",
   "Igual que Y8, reemplazando el índice general por el subyacente",
   "Coeficiente · Razón", "INEI, BCRP", "Supuesto P8"],

  ["D5 Integración espacial", "Y10", "Correlación móvil entre pares de ciudades",
   "Correlación de π entre las ciudades c y c′ en la ventana de 12 meses terminada en t; se resume por ciudad como la media de sus correlaciones con las demás",
   "Coeficiente · Razón", "Derivado de Y1", "H5"],
  ["D5 Integración espacial", "Y11", "Ancho de la banda neutral",
   "Umbral estimado en un modelo de corrección de error con umbral (TVECM) por par de ciudades. Representa los costos de transacción",
   "% · Razón", "Derivado de Y1 y del nivel del índice", "H5"],
];


// ------------------------------------------- matriz simplificada (pregrado)

// La matriz del cuerpo de la tesis: 2 variables, 6 dimensiones, 10
// indicadores. La version de 27 indicadores pasa a anexo tecnico.
//
// Que se deja fuera y por que: las dimensiones de signo, persistencia y
// calendario productivo salen de la matriz y pasan a ser analisis de robustez
// en el capitulo de resultados. Eso significa que H4 (asimetria) y H4b
// (dependencia del estado) ya no tienen respaldo directo en la matriz, y hay
// que decirlo en la tesis en lugar de dejar la inconsistencia.

const DEF_X_CONCEPTUAL =
  "Perturbación exógena originada en la variabilidad del Pacífico tropical, " +
  "que desplaza la función de oferta agropecuaria y pesquera regional y eleva " +
  "los costos de transacción del comercio interregional.";
const DEF_X_OPERACIONAL =
  "Se mide mediante la anomalía climática local respecto de la normal " +
  "1991–2020, el estado del océano a través de dos índices (ONI e ICEN) y la " +
  "exposición económica de cada ciudad al fenómeno.";
const DEF_Y_CONCEPTUAL =
  "Nivel y dinámica del precio de la canasta de alimentos que enfrenta el " +
  "consumidor urbano de cada ciudad.";
const DEF_Y_OPERACIONAL =
  "Se mide con el índice de precios al consumidor del grupo de alimentos de " +
  "cada ciudad, en su nivel, su volatilidad y su grado de integración con las " +
  "demás ciudades.";

// [dimension, [indicadores], escala]
const SIMPLE_X = [
  ["D1. Magnitud del shock climático local",
   ["1. Anomalía estandarizada de precipitación mensual",
    "2. Anomalía estandarizada de temperatura máxima mensual"],
   "Razón (desviaciones estándar)"],
  ["D2. Estado del océano",
   ["3. Índice ONI, región Niño 3.4 (Pacífico central)",
    "4. Índice ICEN-réplica, región Niño 1+2 (Niño costero)"],
   "Razón (grados Celsius)"],
  ["D3. Exposición económica",
   ["5. Participación del sector agropecuario y pesquero en el VAB departamental",
    "6. Participación de los alimentos en la canasta del IPC de la ciudad"],
   "Razón (porcentaje)"],
];

const SIMPLE_Y = [
  ["D1. Nivel de precios",
   ["7. Variación mensual del IPC de alimentos",
    "8. Variación a doce meses del IPC de alimentos"],
   "Razón (porcentaje)"],
  ["D2. Volatilidad",
   ["9. Desviación estándar móvil de doce meses de la inflación de alimentos"],
   "Razón"],
  ["D3. Integración de mercados",
   ["10. Correlación de la inflación de alimentos de la ciudad con la de las demás ciudades"],
   "Razón (coeficiente)"],
];

// ------------------------------------------------------------ Ricitos de Oro

const RICITOS = [
  ["Demasiado amplio",
   "«Impacto económico del fenómeno El Niño en el Perú»",
   "No delimita variable dependiente, ni unidad de análisis, ni periodo. Abarca producción, empleo, precios, infraestructura y salud a la vez. No es abordable con el tiempo y los datos de una tesis, y no permite identificar aporte frente a lo ya publicado."],
  ["Demasiado estrecho",
   "«Efecto del Niño costero de marzo de 2017 sobre el precio de la papa en el mercado de Wanchaq, Cusco»",
   "Un solo evento, un producto y un mercado. Se responde con estadística descriptiva: no admite diseño de panel ni inferencia, y la literatura específica sobre ese caso puntual es insuficiente para sostener un marco teórico."],
  ["Calibrado · Ricitos de Oro",
   "«Niño del Pacífico central y Niño costero: efecto diferenciado sobre la inflación de alimentos en 26 ciudades del Perú, 2010–2026»",
   "Delimita las dos variables, la unidad de análisis (26 ciudades), el ámbito (Perú) y el periodo (2010–2026). Hay literatura suficiente y el aporte es identificable y enunciable en una frase: la separación ONI / ICEN a nivel subnacional."],
];

const CRITERIOS = [
  ["Literatura suficiente", "Cumple",
   "Antecedentes internacionales, nacionales y locales documentados, con la distinción CP/EP ya establecida entre países (Gallegati et al., 2026; Solomou et al., 2025)."],
  ["Aporte identificable", "Cumple",
   "La separación ONI / ICEN a nivel subnacional no se encuentra en la literatura revisada. El efecto agregado, en cambio, ya está cuantificado (Calero y Rodríguez, 2026; Crofils et al., 2024)."],
  ["Variables delimitadas", "Cumple",
   "Una variable independiente y una dependiente, con 6 dimensiones y 10 indicadores en la matriz; el anexo técnico detalla 27."],
  ["Unidad de análisis y periodo", "Cumple",
   "26 ciudades, frecuencia mensual, 2010–2026."],
  ["Factibilidad de los datos", "Cumple en parte",
   "Es el criterio no satisfecho del todo, y se declara: los indicadores 1 y 2 dependen de persistir el panel climático mensual 1991–2026, y la existencia del IPC por ciudad y división de gasto (indicadores 7 y 8) no está verificada. Ver el Anexo 2."],
];

const ESTADO = [
  ["X1, X2", "Bloqueado",
   "σ por unidad y mes del año no existe en el producto actual de normales; requiere persistir el panel climático mensual 1991–2026"],
  ["X3 – X7", "Bloqueado", "Derivan de X1 y X2"],
  ["X8", "Parcial", "La serie ONI guardada arranca en 2021; hay que extenderla a 1950"],
  ["X9", "Parcial",
   "Calculable desde la NOAA; falta validarla contra los informes del IGP. El nombre «ICEN-réplica» es obligatorio hasta esa validación"],
  ["X10, X11", "No verificado",
   "Disponibilidad histórica y codificación consistente de los comunicados del ENFEN"],
  ["X12", "No verificado", "Ruta de descarga del VAB departamental en formato utilizable"],
  ["X13", "En riesgo",
   "Si las ponderaciones del IPC solo existen para Lima Metropolitana, el indicador no varía entre ciudades. Plan alternativo: peso nacional, declarando la pérdida de variación"],
  ["X14", "Bloqueado", "Requiere el panel climático largo"],
  ["X15, X16", "En riesgo",
   "Falta el dato de qué zona abastece a cada ciudad (flujos comerciales). Sustituto admisible con supuesto declarado"],
  ["Y1 – Y3", "En riesgo · decide el diseño",
   "Que el INEI publique el IPC por ciudad y por división de gasto. Si solo existe el índice general por ciudad, se aplica el plan alternativo del protocolo"],
  ["Y4 – Y7, Y10, Y11", "Derivado", "Disponibles en cuanto exista Y1"],
  ["Y8", "No verificado", "IPC general por ciudad"],
  ["Y9", "En riesgo", "IPC subyacente por ciudad, dudoso. Si no existe, se elimina de la matriz"],
];

// ------------------------------------------------------------------ secciones

// Anchos de columna, pagina horizontal: suman UTIL_H = 13680
const A_MATRIZ = [1750, 620, 2300, 4650, 1500, 1660, 1200];
// Pagina vertical: suman UTIL_V = 10080
const A_RICITOS = [1700, 4180, 4200];
const A_CRITERIOS = [2100, 1500, 6480];
// Pagina horizontal
const A_ESTADO = [2100, 2300, 9280];

const filaMatriz = (f, i) =>
  new TableRow({
    children: [
      celda(f[0], A_MATRIZ[0], { fondo: i % 2 ? GRIS : undefined, tam: 15 }),
      celda(f[1], A_MATRIZ[1], { fondo: i % 2 ? GRIS : undefined, negrita: true, alineacion: AlignmentType.CENTER }),
      celda(f[2], A_MATRIZ[2], { fondo: i % 2 ? GRIS : undefined, tam: 15 }),
      celda(f[3], A_MATRIZ[3], { fondo: i % 2 ? GRIS : undefined, tam: 14 }),
      celda(f[4], A_MATRIZ[4], { fondo: i % 2 ? GRIS : undefined, tam: 14, alineacion: AlignmentType.CENTER }),
      celda(f[5], A_MATRIZ[5], { fondo: i % 2 ? GRIS : undefined, tam: 14 }),
      celda(f[6], A_MATRIZ[6], { fondo: i % 2 ? GRIS : undefined, tam: 14, alineacion: AlignmentType.CENTER }),
    ],
  });

const CAB_MATRIZ = ["Dimensión", "Cód.", "Indicador",
  "Definición operacional / fórmula", "Unidad y escala", "Fuente", "Hipótesis"];

const seccionVertical = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 60 },
      children: [new TextRun({ text: CASA, size: 20, color: "595959", font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
      children: [new TextRun({ text: "Escuela Profesional de Economía", size: 20, color: "595959", font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 360 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: AZUL, space: 8 } },
      children: [new TextRun({
        text: "MATRIZ DE OPERACIONALIZACIÓN DE VARIABLES",
        size: 30, bold: true, color: AZUL, font: "Arial",
      })],
    }),

    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      children: [new TextRun({ text: "1. Título de la investigación", size: 26, bold: true, color: AZUL, font: "Arial" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 160 },
      shading: { type: ShadingType.CLEAR, fill: GRIS, color: "auto" },
      border: {
        top: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
        bottom: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
        left: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
        right: { style: BorderStyle.SINGLE, size: 6, color: AZUL, space: 10 },
      },
      children: [new TextRun({ text: TITULO, size: 26, bold: true, font: "Arial" })],
    }),
    p(`Autor: ${AUTOR}`, { alineacion: AlignmentType.CENTER, tam: 20, despues: 300 }),

    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      children: [new TextRun({
        text: "2. Calibración del título: técnica de Ricitos de Oro",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("La técnica de Ricitos de Oro consiste en comprobar que el tema no sea demasiado " +
      "amplio ni demasiado estrecho, sino del alcance justo: lo bastante específico para " +
      "abordarlo con los datos y el tiempo disponibles, y lo bastante amplio para que exista " +
      "literatura suficiente y el trabajo constituya un aporte. El procedimiento es partir de " +
      "un enunciado general y acotarlo por etapas —por variable, unidad de análisis, ámbito y " +
      "periodo— hasta dar con la formulación intermedia. A continuación se muestran las tres " +
      "versiones evaluadas.", { despues: 160 }),

    tabla(A_RICITOS, [
      encabezado(["Versión", "Título candidato", "Veredicto"], A_RICITOS),
      ...RICITOS.map((f, i) => new TableRow({
        children: [
          celda(f[0], A_RICITOS[0], {
            negrita: true, tam: 16,
            fondo: i === 2 ? "E2EFDA" : GRIS,
            alineacion: AlignmentType.CENTER,
          }),
          celda(f[1], A_RICITOS[1], { tam: 15, cursiva: true, fondo: i === 2 ? "E2EFDA" : undefined }),
          celda(f[2], A_RICITOS[2], { tam: 15, fondo: i === 2 ? "E2EFDA" : undefined }),
        ],
      })),
    ]),

    p("Verificación de los criterios de la técnica", { negrita: true, antes: 300, despues: 120 }),

    tabla(A_CRITERIOS, [
      encabezado(["Criterio", "Resultado", "Sustento"], A_CRITERIOS),
      ...CRITERIOS.map((f, i) => new TableRow({
        children: [
          celda(f[0], A_CRITERIOS[0], { negrita: true, tam: 16, fondo: i % 2 ? GRIS : undefined }),
          celda(f[1], A_CRITERIOS[1], {
            tam: 16, negrita: true, alineacion: AlignmentType.CENTER,
            fondo: f[1] === "Cumple en parte" ? "FFF2CC" : (i % 2 ? GRIS : undefined),
          }),
          celda(f[2], A_CRITERIOS[2], { tam: 15, fondo: i % 2 ? GRIS : undefined }),
        ],
      })),
    ]),

  ],
};

// Anchos de la matriz simplificada, pagina horizontal: suman UTIL_H = 13680
const A_SIMPLE = [1350, 2550, 2550, 2050, 3980, 1200];

/** Filas de una variable, con celdas combinadas verticalmente. */
function filasSimple(variable, defConceptual, defOperacional, grupos) {
  const total = grupos.reduce((n, g) => n + g[1].length, 0);
  const filas = [];
  let primera = true;

  grupos.forEach(([dimension, indicadores, escala]) => {
    indicadores.forEach((indicador, j) => {
      const celdas = [];
      if (primera) {
        celdas.push(
          celda(variable, A_SIMPLE[0], {
            filas: total, tam: 17, negrita: true, fondo: GRIS_OSCURO,
            alineacion: AlignmentType.CENTER,
          }),
          celda(defConceptual, A_SIMPLE[1], { filas: total, tam: 15 }),
          celda(defOperacional, A_SIMPLE[2], { filas: total, tam: 15 }),
        );
        primera = false;
      }
      if (j === 0) {
        celdas.push(celda(dimension, A_SIMPLE[3], {
          filas: indicadores.length, tam: 16, negrita: true,
          alineacion: AlignmentType.CENTER,
        }));
      }
      celdas.push(celda(indicador, A_SIMPLE[4], { tam: 16 }));
      if (j === 0) {
        celdas.push(celda(escala, A_SIMPLE[5], {
          filas: indicadores.length, tam: 15, alineacion: AlignmentType.CENTER,
        }));
      }
      filas.push(new TableRow({ children: celdas }));
    });
  });
  return filas;
}

const CAB_SIMPLE = ["Variable", "Definición conceptual", "Definición operacional",
  "Dimensiones", "Indicadores", "Escala de medición"];

const seccionMatrizSimple = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { after: 60 },
      children: [new TextRun({
        text: "3. Matriz de operacionalización de variables",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("2 variables · 6 dimensiones · 10 indicadores", { cursiva: true, tam: 18, despues: 140 }),
    tabla(A_SIMPLE, [
      encabezado(CAB_SIMPLE, A_SIMPLE),
      ...filasSimple(["Variable independiente (X)", "Shock de oferta de origen ENSO"],
                     DEF_X_CONCEPTUAL, DEF_X_OPERACIONAL, SIMPLE_X),
      ...filasSimple(["Variable dependiente (Y)", "Precios de alimentos al consumidor urbano"],
                     DEF_Y_CONCEPTUAL, DEF_Y_OPERACIONAL, SIMPLE_Y),
    ]),
    p("Nota. El detalle de cada indicador —fórmula de cálculo, fuente, periodicidad y estado de " +
      "verificación de los datos— se presenta en el Anexo 1. Las pruebas de asimetría del shock y " +
      "de dependencia del nivel de existencias no constituyen dimensiones de la matriz: se tratan " +
      "como análisis de robustez en el capítulo de resultados.",
      { antes: 200, tam: 17 }),
  ],
};

// -------------------------------------- matriz de consistencia metodologica

// [etiqueta, problema, objetivo, hipotesis, indicadores]
const CONSISTENCIA = [
  ["General",
   "¿Cuál es el efecto diferenciado del Niño del Pacífico central (ONI) y del Niño costero (ICEN) sobre la inflación de alimentos de las ciudades del Perú, según la exposición económica de cada ciudad, en el periodo 2010–2026?",
   "Determinar el efecto diferenciado del Niño del Pacífico central y del Niño costero sobre la inflación de alimentos de las ciudades del Perú, según la exposición económica de cada ciudad, 2010–2026.",
   "En las ciudades del Perú, entre 2010 y 2026, el Niño costero y el Niño del Pacífico central producen efectos de magnitud distinta sobre la inflación de alimentos: el del Niño costero es mayor en las ciudades de la costa norte, y la magnitud de ambos aumenta con la exposición económica de la ciudad.",
   "1 – 10"],
  ["Esp. 1",
   "¿Cuál es el efecto de las anomalías climáticas locales sobre la inflación de alimentos de las ciudades del Perú?",
   "Estimar el efecto de las anomalías locales de precipitación y temperatura sobre la inflación de alimentos por ciudad.",
   "Las anomalías locales de precipitación y temperatura afectan la inflación de alimentos de las ciudades del Perú, alcanzando su efecto máximo dentro de los dieciocho meses posteriores al shock.",
   "1, 2, 7, 8"],
  ["Esp. 2",
   "¿Cuál de los dos índices oceánicos —ONI o ICEN— explica mejor la inflación de alimentos de las ciudades del Perú?",
   "Comparar el poder explicativo del ONI y del ICEN-réplica sobre la inflación de alimentos por ciudad.",
   "En las ciudades de la costa norte del Perú, el ICEN explica la inflación de alimentos mejor que el ONI.",
   "3, 4, 7, 8"],
  ["Esp. 3",
   "¿En qué medida difiere el efecto entre regiones según la exposición económica de cada ciudad?",
   "Contrastar la heterogeneidad regional del efecto según la exposición económica de cada ciudad.",
   "El efecto de las anomalías climáticas sobre la inflación de alimentos aumenta con la participación del sector agropecuario y pesquero en el VAB departamental y con el peso del alimento en la canasta de la ciudad, y difiere en signo entre la costa norte y la sierra sur.",
   "5, 6, 1, 2"],
  ["Esp. 4",
   "¿En qué medida se reduce la integración de los mercados de alimentos entre las ciudades del Perú durante los episodios cálidos del ENSO?",
   "Determinar en qué medida se reduce la integración de los mercados de alimentos entre las ciudades del Perú durante los episodios cálidos del ENSO.",
   "La integración de los mercados de alimentos entre las ciudades del Perú disminuye durante los episodios cálidos del ENSO.",
   "10, 3, 4"],
];

const METODOLOGIA = [
  "Enfoque: cuantitativo",
  "Tipo: aplicada",
  "Nivel: explicativo",
  "Diseño: no experimental, longitudinal de panel (ex post facto)",
  "Método: hipotético-deductivo",
  "",
  "Población: las 26 ciudades del ámbito urbano que componen el IPC del INEI, enero 2010 – septiembre 2026",
  "Muestra: censal, las 26 ciudades; aproximadamente 5 200 observaciones ciudad-mes",
  "Unidad de análisis: la ciudad-mes",
  "",
  "Técnica de recolección: análisis documental de fuentes secundarias de acceso abierto",
  "Instrumento: ficha de registro de datos secundarios",
  "",
  "Procesamiento y análisis: ver la sección 5",
];

// El tratamiento estadistico -- estimador, correccion de sesgo, inferencia y
// robustez -- NO va en la matriz de consistencia: su lugar es el acapite de
// procesamiento y analisis de datos. Va en PROCESAMIENTO, abajo.
const PROCESAMIENTO = [
  ["Preparación de los datos",
   "Construcción del panel ciudad-mes 2010–2026 a partir de las series diarias de ERA5 y del IPC del INEI; cálculo de la media y la desviación estándar por unidad y mes del año sobre 1991–2020; empalme de las bases 2009 y diciembre 2021 del IPC; cálculo de la réplica del ICEN y su validación contra los informes del IGP"],
  ["Técnica principal de estimación",
   "Proyecciones locales en panel con AUMENTO DE REZAGOS, con efectos fijos de ciudad y de tiempo, para horizontes h = 0 a 24 meses (Jordà, 2005; Montiel Olea y Plagborg-Møller, 2021)"],
  ["Corrección de sesgo",
   "Jackknife de medio panel, por el sesgo de Nickell implícito en el panel con efectos fijos, que subestima los efectos (Mei, Sheng y Shi, 2023)"],
  ["Procedimiento de inferencia",
   "Rezagos como controles y agrupamiento en la dimensión transversal, por tratarse de un shock macroeconómico en un panel (Almuzara y Sarto, 2024). Driscoll–Kraay y bootstrap wild cluster como contraste, por los 26 grupos"],
  ["Tratamiento por objetivo",
   "Obj. 2: dos estimaciones paralelas, ONI e ICEN, y comparación de ajuste por zona. Obj. 3: interacción exposición × shock con heterogeneidad de parámetros por subregión (Ponce, 2020). Obj. 4: correlaciones móviles entre pares de ciudades y modelo de corrección de error con umbral (Goodwin y Piggott, 2001)"],
  ["Pruebas de robustez",
   "Dependencia espacial sobre los residuos y panel espacial si resulta significativa (Baltagi y Pirotte, 2010); quiebre estructural y estimación por submuestras (Duran y Dindaroğlu, 2021); proyecciones locales suavizadas (Barnichon y Brownlees, 2019); placebo con rezagos adelantados; exclusión de 2017 y 2023; comparación entre niveles de agregación del clima"],
  ["Software y reproducibilidad",
   "Python. Código y datos derivados versionados en repositorio público, de modo que toda la cadena sea reproducible"],
];

// Suman UTIL_H = 13680
const A_PROC = [3200, 10480];

const seccionProcesamiento = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { after: 60 },
      children: [new TextRun({
        text: "5. Procesamiento y análisis de datos",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("El tratamiento estadístico no forma parte de la matriz de consistencia: la matriz declara " +
      "el diseño, la población, la muestra, la técnica y el instrumento, mientras que el estimador, " +
      "la corrección de sesgo, el procedimiento de inferencia y las pruebas de robustez corresponden " +
      "a este acápite.",
      { tam: 18, despues: 160 }),
    tabla(A_PROC, [
      encabezado(["Aspecto", "Descripción"], A_PROC),
      ...PROCESAMIENTO.map((f, i) => new TableRow({
        children: [
          celda(f[0], A_PROC[0], { negrita: true, tam: 16, fondo: i % 2 ? GRIS : undefined }),
          celda(f[1], A_PROC[1], { tam: 15, fondo: i % 2 ? GRIS : undefined }),
        ],
      })),
    ]),
  ],
};

// Suman UTIL_H = 13680
const A_CONS = [760, 2900, 2900, 3200, 920, 3000];

const seccionConsistencia = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { after: 60 },
      children: [new TextRun({
        text: "4. Matriz de consistencia metodológica",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("1 problema general y 4 específicos · cada fila cierra con su objetivo, su hipótesis y sus indicadores",
      { cursiva: true, tam: 18, despues: 140 }),
    tabla(A_CONS, [
      encabezado(["", "Problema", "Objetivo", "Hipótesis", "Ind.", "Metodología"], A_CONS),
      ...CONSISTENCIA.map((f, i) => {
        const celdas = [
          celda(f[0], A_CONS[0], {
            tam: 15, negrita: true, alineacion: AlignmentType.CENTER,
            fondo: i === 0 ? GRIS_OSCURO : GRIS,
          }),
          celda(f[1], A_CONS[1], { tam: 15, fondo: i === 0 ? "EDEDED" : undefined }),
          celda(f[2], A_CONS[2], { tam: 15, fondo: i === 0 ? "EDEDED" : undefined }),
          celda(f[3], A_CONS[3], { tam: 15, fondo: i === 0 ? "EDEDED" : undefined }),
          celda(f[4], A_CONS[4], {
            tam: 15, alineacion: AlignmentType.CENTER,
            fondo: i === 0 ? "EDEDED" : undefined,
          }),
        ];
        if (i === 0) {
          celdas.push(celda(METODOLOGIA, A_CONS[5], { filas: CONSISTENCIA.length, tam: 14 }));
        }
        return new TableRow({ children: celdas });
      }),
    ]),
    p("Nota. La construcción del panel y la validación de la réplica del ICEN no figuran como " +
      "objetivos: son tareas previas a la estimación, consignadas en la columna de metodología. " +
      "La asimetría del shock y la dependencia del nivel de existencias se tratan como análisis " +
      "de robustez. En la hipótesis específica 4 se contrasta la predicción —que la integración " +
      "cae— y no el mecanismo que la explica, porque no se dispone de datos de transporte.",
      { antes: 160, tam: 16 }),
  ],
};

// ------------------------------------------------------- matriz de datos

// El esquema lo define scripts/tesis/esquema_panel.py y se lee desde el JSON
// que ese script genera, para que la tabla del documento y el archivo real no
// puedan decir cosas distintas. Si falta el JSON, se avisa y se omite la
// seccion en lugar de inventar su contenido.
const RUTA_ESQUEMA = path.join(__dirname, "..", "..", "docs", "tesis",
                               "esquema_panel.json");
let ESQUEMA = null;
try {
  ESQUEMA = JSON.parse(fs.readFileSync(RUTA_ESQUEMA, "utf-8"));
} catch (e) {
  console.warn(`AVISO: no se pudo leer ${RUTA_ESQUEMA}. `
             + "Se omite la seccion de matriz de datos. "
             + "Correr antes: python scripts/tesis/esquema_panel.py --plantilla");
}

// Suman UTIL_H = 13680
const A_DAT = [500, 1700, 3100, 1000, 1200, 2800, 2380, 1000];

function seccionDatos() {
  if (!ESQUEMA) return null;
  return {
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
          text: "6. Matriz de datos", size: 26, bold: true, color: AZUL, font: "Arial",
        })],
      }),
      p(`Unidad de observación: la ciudad-mes · formato largo · `
        + `${ESQUEMA.ciudades} ciudades × ${ESQUEMA.periodos} periodos = `
        + `${ESQUEMA.filas_esperadas} filas · ${ESQUEMA.campos.length} campos · `
        + `${ESQUEMA.periodo_inicio} a ${ESQUEMA.periodo_fin}`,
        { cursiva: true, tam: 18, despues: 140 }),
      tabla(A_DAT, [
        encabezado(["N°", "Campo", "Etiqueta", "Tipo", "Escala", "Rango válido",
                    "Fuente", "Ind."], A_DAT),
        ...ESQUEMA.campos.map((c, i) => new TableRow({
          children: [
            celda(String(c.orden), A_DAT[0], { tam: 14, alineacion: AlignmentType.CENTER,
                                               fondo: i % 2 ? GRIS : undefined }),
            celda(c.nombre, A_DAT[1], { tam: 14, negrita: true, mono: true,
                                        fondo: i % 2 ? GRIS : undefined }),
            celda(c.etiqueta, A_DAT[2], { tam: 14, fondo: i % 2 ? GRIS : undefined }),
            celda(c.tipo, A_DAT[3], { tam: 14, alineacion: AlignmentType.CENTER,
                                      fondo: i % 2 ? GRIS : undefined }),
            celda(c.escala, A_DAT[4], { tam: 14, alineacion: AlignmentType.CENTER,
                                        fondo: i % 2 ? GRIS : undefined }),
            celda(c.rango, A_DAT[5], { tam: 13, fondo: i % 2 ? GRIS : undefined }),
            celda(c.fuente, A_DAT[6], { tam: 13, fondo: i % 2 ? GRIS : undefined }),
            celda(c.indicador, A_DAT[7], { tam: 14, negrita: true,
                                           alineacion: AlignmentType.CENTER,
                                           fondo: i % 2 ? GRIS : undefined }),
          ],
        })),
      ]),
      salto(),
      p("Tabla auxiliar: normales climáticas", { negrita: true, antes: 0, despues: 100 }),
      p(`Se une al panel por (ciudad, mes). ${ESQUEMA.tabla_auxiliar.filas_esperadas} filas. `
        + "Estos campos NO van en el panel: son constantes para cada par ciudad-mes del año, "
        + "de modo que repetirlos en las 5 226 filas sería redundante.",
        { tam: 17, despues: 120 }),
      tabla([800, 1900, 3600, 1100, 1300, 2600, 2380], [
        encabezado(["N°", "Campo", "Etiqueta", "Tipo", "Escala", "Rango válido", "Fuente"],
                   [800, 1900, 3600, 1100, 1300, 2600, 2380]),
        ...ESQUEMA.tabla_auxiliar.campos.map((c, i) => new TableRow({
          children: [
            celda(String(c.orden), 800, { tam: 14, alineacion: AlignmentType.CENTER, fondo: i % 2 ? GRIS : undefined }),
            celda(c.nombre, 1900, { tam: 14, negrita: true, mono: true, fondo: i % 2 ? GRIS : undefined }),
            celda(c.etiqueta, 3600, { tam: 14, fondo: i % 2 ? GRIS : undefined }),
            celda(c.tipo, 1100, { tam: 14, alineacion: AlignmentType.CENTER, fondo: i % 2 ? GRIS : undefined }),
            celda(c.escala, 1300, { tam: 14, alineacion: AlignmentType.CENTER, fondo: i % 2 ? GRIS : undefined }),
            celda(c.rango, 2600, { tam: 13, fondo: i % 2 ? GRIS : undefined }),
            celda(c.fuente, 2380, { tam: 13, fondo: i % 2 ? GRIS : undefined }),
          ],
        })),
      ]),
      p("Nota. Los vacíos se dejan en blanco, nunca como 0 ni como −99: un cero es un dato y un "
        + "vacío es su ausencia. Los campos sigma_pp_mm, anios_normal, base_ipc y fuente_ipc no "
        + "entran en las regresiones; son controles de calidad y de trazabilidad, y son los que "
        + "permiten auditar el panel. El esquema se define en scripts/tesis/esquema_panel.py, que "
        + "genera la plantilla y un validador.",
        { antes: 160, tam: 16 }),
    ],
  };
}

const seccionHorizontal = {
  properties: {
    page: {
      size: { width: LETTER.width, height: LETTER.height, orientation: PageOrientation.LANDSCAPE },
      margin: { top: MARGEN, right: MARGEN, bottom: MARGEN, left: MARGEN },
    },
  },
  children: [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { after: 60 },
      children: [new TextRun({
        text: "Anexo 1. Matriz detallada de indicadores · Variable independiente (X)",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("Shock exógeno de oferta de origen ENSO · 6 dimensiones · 16 indicadores", { cursiva: true, tam: 18, despues: 120 }),
    tabla(A_MATRIZ, [encabezado(CAB_MATRIZ, A_MATRIZ), ...FILAS_X.map(filaMatriz)]),

    salto(),
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 0, after: 60 },
      children: [new TextRun({
        text: "Anexo 1. Matriz detallada de indicadores · Variable dependiente (Y)",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("Precios de alimentos al consumidor urbano · 5 dimensiones · 11 indicadores", { cursiva: true, tam: 18, despues: 120 }),
    tabla(A_MATRIZ, [encabezado(CAB_MATRIZ, A_MATRIZ), ...FILAS_Y.map(filaMatriz)]),

    salto(),
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 0, after: 60 },
      children: [new TextRun({
        text: "Anexo 2. Estado de verificación de las fuentes",
        size: 26, bold: true, color: AZUL, font: "Arial",
      })],
    }),
    p("Regla de trabajo: una dimensión cuya fuente no se confirme se elimina de la matriz antes " +
      "de estimar; no se estima con un sustituto silencioso.", { cursiva: true, tam: 18, despues: 120 }),
    tabla(A_ESTADO, [
      encabezado(["Indicadores", "Estado", "Qué falta"], A_ESTADO),
      ...ESTADO.map((f, i) => new TableRow({
        children: [
          celda(f[0], A_ESTADO[0], { negrita: true, tam: 15, fondo: i % 2 ? GRIS : undefined }),
          celda(f[1], A_ESTADO[1], {
            tam: 15, negrita: true, alineacion: AlignmentType.CENTER,
            fondo: f[1] === "Bloqueado" ? "FBE5E5"
              : (f[1].startsWith("En riesgo") ? "FFF2CC"
              : (f[1] === "Derivado" ? "E2EFDA" : (i % 2 ? GRIS : undefined))),
          }),
          celda(f[2], A_ESTADO[2], { tam: 15, fondo: i % 2 ? GRIS : undefined }),
        ],
      })),
    ]),
    p("Lectura del cuadro: de los 27 indicadores, ninguno es calculable al día de hoy. Los de la " +
      "variable X porque falta persistir el panel climático mensual; los de la variable Y porque " +
      "falta confirmar que el IPC exista desagregado por ciudad y división de gasto. Ambas son " +
      "tareas previas a la estimación, no capítulos de la tesis.",
      { antes: 180, tam: 18 }),
  ],
};

// ------------------------------------------------------------------- documento

const doc = new Document({
  creator: AUTOR,
  title: "Matriz de operacionalización de variables",
  description: TITULO,
  styles: {
    default: {
      document: { run: { font: "Arial", size: 22 } },
      heading1: {
        run: { font: "Arial", size: 26, bold: true, color: AZUL },
        paragraph: { spacing: { before: 280, after: 120 }, keepNext: true },
      },
      heading2: {
        run: { font: "Arial", size: 24, bold: true, color: AZUL },
        paragraph: { spacing: { before: 200, after: 100 }, keepNext: true },
      },
    },
  },
  sections: [seccionVertical, seccionMatrizSimple, seccionConsistencia,
             seccionProcesamiento, seccionDatos(), seccionHorizontal].filter(Boolean),
});

const salida = path.join(__dirname, "..", "..", "docs", "tesis",
                         "Matriz_operacionalizacion.docx");

Packer.toBuffer(doc).then((buffer) => {
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  fs.writeFileSync(salida, buffer);
  const kb = (buffer.length / 1024).toFixed(1);
  console.log(`${FILAS_X.length + FILAS_Y.length} indicadores -> ${salida} (${kb} KB)`);
});
