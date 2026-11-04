/**
 * Ayudantes de formato compartidos por los generadores .docx de la tesis.
 *
 * Los usan scripts/tesis/matriz_docx.js y scripts/tesis/matrices_teoricas_docx.js.
 * Estan aqui y no duplicados en cada uno para que los dos documentos no se
 * desalineen visualmente cuando se toque uno solo.
 *
 * Nota sobre la convencion del proyecto: CLAUDE.md pide Python estandar. Estas
 * piezas en Node existen solo porque los entregables son .docx con tablas y el
 * paquete docx de npm esta preinstalado. No forman parte del monitor.
 */

const {
  Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType,
  BorderStyle, VerticalAlign, PageBreak,
} = require("docx");

const AZUL = "1F3864";
const GRIS = "F2F2F2";
const GRIS_OSCURO = "D9D9D9";

// Letter en DXA. Para horizontal se pasan las medidas verticales y docx-js
// intercambia ancho y alto al aplicar la orientacion.
const LETTER = { width: 12240, height: 15840 };
const MARGEN = 1080;
const UTIL_V = LETTER.width - 2 * MARGEN;   // 10080, pagina vertical
const UTIL_H = LETTER.height - 2 * MARGEN;  // 13680, pagina horizontal

// ------------------------------------------------------------------ utiles

const p = (texto, opciones = {}) =>
  new Paragraph({
    alignment: opciones.alineacion || AlignmentType.JUSTIFIED,
    spacing: { before: opciones.antes ?? 0, after: opciones.despues ?? 120 },
    children: [new TextRun({
      text: texto,
      size: opciones.tam || 22,
      bold: !!opciones.negrita,
      italics: !!opciones.cursiva,
      color: opciones.color,
      font: "Arial",
    })],
  });

/** Celda de tabla. */
const celda = (texto, ancho, opciones = {}) =>
  new TableCell({
    width: { size: ancho, type: WidthType.DXA },
    shading: opciones.fondo
      ? { type: ShadingType.CLEAR, fill: opciones.fondo, color: "auto" }
      : undefined,
    verticalAlign: VerticalAlign.CENTER,
    rowSpan: opciones.filas,
    margins: { top: 60, bottom: 60, left: 80, right: 80 },
    children: (Array.isArray(texto) ? texto : [texto]).map((linea) =>
      new Paragraph({
        alignment: opciones.alineacion || AlignmentType.LEFT,
        spacing: { before: 0, after: 0 },
        children: [new TextRun({
          text: linea,
          size: opciones.tam || 16,
          bold: !!opciones.negrita,
          italics: !!opciones.cursiva,
          color: opciones.color,
          font: opciones.mono ? "Consolas" : "Arial",
        })],
      })),
  });

/** Fila de encabezado con fondo azul y texto blanco. */
const encabezado = (textos, anchos) =>
  new TableRow({
    tableHeader: true,
    children: textos.map((t, i) =>
      celda(t, anchos[i], {
        fondo: AZUL, negrita: true, color: "FFFFFF", tam: 16,
        alineacion: AlignmentType.CENTER,
      })),
  });

const salto = () => new Paragraph({ children: [new PageBreak()] });

const tabla = (anchos, filas) =>
  new Table({
    columnWidths: anchos,
    width: { size: anchos.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "808080" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "808080" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "808080" },
      right: { style: BorderStyle.SINGLE, size: 4, color: "808080" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" },
    },
    rows: filas,
  });

module.exports = {
  AZUL, GRIS, GRIS_OSCURO, LETTER, MARGEN, UTIL_V, UTIL_H,
  p, celda, encabezado, salto, tabla,
};
