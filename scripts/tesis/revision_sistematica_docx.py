#!/usr/bin/env python3
"""Genera la propuesta de revision sistematica en Word con formato APA 7.

Salida: docs/tesis/Propuesta_revision_sistematica_APA.docx

La fuente de verdad del contenido es docs/tesis/REVISION_SISTEMATICA.md.

DEPENDENCIA EXTERNA, y conviene saberlo antes de correrlo. Este script usa
apa_docx.py, que viene con la skill "redaccion-apa-7" y NO esta versionado en
este repositorio. Si no lo encuentra, avisa donde buscarlo en lugar de fallar
con un error oscuro. Tambien necesita python-docx.

Uso:
    python scripts/tesis/revision_sistematica_docx.py
    python scripts/tesis/revision_sistematica_docx.py --apa-dir /ruta/a/scripts
"""

import argparse
import glob
import os
import sys

RUTA_SKILL = "/root/.claude/skills/synced/*/redaccion-apa-7/scripts"


def cargar_apa(ruta_manual=None):
    candidatas = [ruta_manual] if ruta_manual else []
    candidatas += sorted(glob.glob(RUTA_SKILL))
    candidatas += [os.path.dirname(os.path.abspath(__file__))]
    for c in candidatas:
        if c and os.path.exists(os.path.join(c, "apa_docx.py")):
            sys.path.insert(0, c)
            from apa_docx import APADocument  # noqa: E402
            return APADocument
    raise SystemExit(
        "No se encontro apa_docx.py.\n"
        "Viene con la skill 'redaccion-apa-7'. Opciones:\n"
        "  1. Pasar la ruta:  --apa-dir /ruta/que/contiene/apa_docx.py\n"
        "  2. Copiar apa_docx.py junto a este script.\n"
        f"Se buscó en: {RUTA_SKILL} y en el directorio de este script.")


# ------------------------------------------------------------ tablas APA

def tabla_apa(apa, numero, titulo, encabezados, filas, anchos_cm=None, nota=None):
    """Tabla con formato APA: numero en negrita, titulo en cursiva, y solo
    bordes horizontales (arriba, bajo encabezados y abajo). Sin verticales."""
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    # Numero y titulo
    p1 = apa.doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1.paragraph_format.space_before = Pt(12)
    r = p1.add_run(f"Tabla {numero}")
    r.bold = True
    apa._set_run_font(r)

    p2 = apa.doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p2.add_run(titulo)
    r.italic = True
    apa._set_run_font(r)

    t = apa.doc.add_table(rows=1, cols=len(encabezados))
    t.autofit = anchos_cm is None

    # Bordes: solo horizontales
    tbl_pr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for borde, valor in (("top", "single"), ("bottom", "single"),
                         ("left", "none"), ("right", "none"),
                         ("insideH", "none"), ("insideV", "none")):
        e = OxmlElement(f"w:{borde}")
        e.set(qn("w:val"), valor)
        e.set(qn("w:sz"), "6")
        e.set(qn("w:color"), "000000")
        borders.append(e)
    tbl_pr.append(borders)

    def linea_inferior(fila):
        for celda in fila.cells:
            tc_pr = celda._tc.get_or_add_tcPr()
            bs = OxmlElement("w:tcBorders")
            b = OxmlElement("w:bottom")
            b.set(qn("w:val"), "single")
            b.set(qn("w:sz"), "6")
            b.set(qn("w:color"), "000000")
            bs.append(b)
            tc_pr.append(bs)

    def escribir(fila, textos, negrita=False, centrado=False):
        for i, txt in enumerate(textos):
            celda = fila.cells[i]
            if anchos_cm:
                celda.width = Cm(anchos_cm[i])
            par = celda.paragraphs[0]
            par.alignment = (WD_ALIGN_PARAGRAPH.CENTER if centrado
                             else WD_ALIGN_PARAGRAPH.LEFT)
            par.paragraph_format.space_after = Pt(2)
            par.paragraph_format.space_before = Pt(2)
            par.paragraph_format.line_spacing = 1.0
            run = par.add_run(str(txt))
            run.bold = negrita
            apa._set_run_font(run)
            run.font.size = Pt(10)

    escribir(t.rows[0], encabezados, negrita=True, centrado=True)
    linea_inferior(t.rows[0])
    for f in filas:
        escribir(t.add_row(), f)

    if nota:
        pn = apa.doc.add_paragraph()
        pn.paragraph_format.space_before = Pt(4)
        r = pn.add_run("Nota. ")
        r.italic = True
        apa._set_run_font(r)
        r2 = pn.add_run(nota)
        apa._set_run_font(r2)
        for run in (r, r2):
            run.font.size = Pt(10)


# ------------------------------------------------------------- contenido

TITULO = ("Propuesta de Revisión Sistemática Sobre el Efecto de los Shocks de "
          "El Niño–Oscilación del Sur en los Precios de Alimentos")


def construir(APADocument, salida):
    apa = APADocument(font="Times New Roman", size=12)
    apa.student_title_page(
        title=TITULO,
        authors=["Alexander Torres Uchupe"],
        affiliation="Universidad Nacional de San Antonio Abad del Cusco, "
                    "Escuela Profesional de Economía",
        course="Proyecto de Tesis",
        instructor="",
        date="4 de noviembre de 2026",
    )
    apa.paper_title(TITULO)

    apa.heading("Marco Normativo de la Revisión", level=1)
    apa.body(
        "Esta propuesta se rige por dos estándares y no por uno. Para el reporte se sigue la "
        "declaración PRISMA 2020 (Page et al., 2021; versión en español de Yepes-Núñez et al., "
        "2021), y para lo específico de la síntesis de evidencia económica se siguen las guías de "
        "la Meta-Analysis of Economics Research Network (Havránek et al., 2020), actualizadas "
        "recientemente para contemplar el uso de inteligencia artificial (Cook et al., 2026). "
        "PRISMA por sí sola resulta insuficiente: fue concebida para ensayos clínicos y no cubre "
        "los problemas propios de la evidencia económica, en particular el tratamiento de "
        "estimaciones múltiples por estudio y la evaluación del sesgo de selección de "
        "publicaciones.")

    apa.heading("Justificación del Diseño: el Sesgo de Publicación en Economía", level=1)
    apa.body(
        "Bartoš et al. (2022) examinaron más de 68 000 metaanálisis que contienen más de 700 000 "
        "estimaciones en medicina, ciencias ambientales, psicología y economía. Encontraron que "
        "los metaanálisis en economía son los más contaminados por sesgo de selección de "
        "publicaciones entre los cuatro campos examinados: tras ajustar por dicho sesgo, la "
        "probabilidad mediana de que exista un efecto descendió de 99,9 % a 29,7 % en economía, y "
        "el tamaño del efecto mediano se redujo de 0,20 a 0,07 desviaciones estándar.")
    apa.body(
        "Ese hallazgo condiciona dos decisiones del protocolo. En primer lugar, la literatura gris "
        "—documentos de trabajo, informes institucionales y tesis— se incluye deliberadamente, "
        "porque es precisamente allí donde se encuentran los resultados no significativos que las "
        "revistas tienden a rechazar; excluirla garantizaría reproducir el sesgo. En segundo "
        "lugar, la evaluación del riesgo de sesgo de publicación constituye una parte central del "
        "trabajo y no un apartado accesorio.")

    apa.heading("Alcance de la Revisión", level=1)
    apa.body(
        "Se plantean dos alcances posibles. La recomendación es ejecutar el primero y diseñar la "
        "extracción de datos de modo que el segundo sea después un paso incremental y no un "
        "proyecto nuevo.")

    tabla_apa(apa, 1, "Comparación de los Dos Alcances Posibles",
              ["Criterio", "A. Revisión cualitativa", "B. Con metaanálisis"],
              [["Producto", "Síntesis narrativa estructurada",
                "Efecto medio y moderadores"],
               ["Estándar", "PRISMA 2020", "PRISMA 2020 y MAER-Net"],
               ["Esfuerzo estimado", "10 a 12 semanas", "20 a 30 semanas"],
               ["Requisito crítico", "Ninguno adicional",
                "Efectos comparables con su error estándar"],
               ["Riesgo principal", "Bajo",
                "Descubrir tardíamente que no hay estimaciones homogeneizables"],
               ["Recomendación", "Para la tesis de pregrado", "Producto posterior"]],
              anchos_cm=[3.4, 6.0, 6.6],
              nota="El requisito crítico del alcance B es dudoso en esta literatura, donde "
                   "conviven elasticidades, respuestas a una desviación estándar, variables "
                   "dicotómicas de evento y funciones impulso-respuesta.")

    apa.heading("Pregunta de la Revisión", level=1)
    apa.body(
        "La pregunta se formula mediante el esquema PECO adaptado a economía. La población está "
        "constituida por mercados de alimentos a cualquier escala: país, región, ciudad o mercado "
        "local. La exposición son los shocks de El Niño–Oscilación del Sur, medidos mediante "
        "índices oceánicos o mediante anomalías climáticas locales atribuibles al fenómeno. La "
        "comparación corresponde a periodos o unidades sin shock. El resultado son los precios de "
        "alimentos en su nivel, inflación, volatilidad o transmisión.")
    apa.body(
        "La pregunta principal es la siguiente: ¿cuál es el efecto de los shocks de El "
        "Niño–Oscilación del Sur sobre los precios de alimentos, y cómo varía ese efecto según la "
        "escala espacial a la que se mide? Como preguntas secundarias se plantean cuatro: si la "
        "evidencia distingue entre el Pacífico central y el Pacífico oriental; qué proporción de "
        "los estudios estima a escala subnacional; qué métodos predominan y cómo han cambiado en "
        "el tiempo; y si existen señales de sesgo de publicación.")
    apa.body(
        "La segunda pregunta secundaria merece una observación. Esa pregunta corresponde "
        "exactamente a la brecha que motiva la investigación principal. Si la revisión documenta "
        "que la proporción de estudios con estimación subnacional es reducida, la justificación de "
        "la tesis deja de ser una afirmación del autor y pasa a ser un hallazgo cuantificado. Esa "
        "es la razón de realizar una revisión sistemática en lugar de una reseña narrativa.")

    apa.heading("Registro del Protocolo", level=1)
    apa.body(
        "La base PROSPERO admite únicamente revisiones con desenlaces en salud, por lo que no "
        "resulta aplicable. El registro se efectuará en OSF Registries, que acepta protocolos de "
        "ciencias sociales y emite un identificador con fecha. El registro previo no es un "
        "trámite: impide ajustar los criterios de inclusión después de conocer los resultados. "
        "Afonso et al. (2023) sostienen que, dada la dificultad de detectar el sesgo de "
        "publicación a posteriori, las estrategias preventivas constituyen la solución más "
        "eficiente.")

    apa.heading("Criterios de Elegibilidad", level=1)
    apa.body(
        "Se incluirá el estudio que cumpla simultáneamente seis condiciones: ser empírico y "
        "cuantitativo, es decir, estimar una relación con datos en lugar de simularla o "
        "postularla; emplear como exposición un índice de El Niño–Oscilación del Sur o una "
        "anomalía climática atribuida al fenómeno; tener como resultado un precio de alimentos o "
        "un índice que lo contenga; reportar un efecto identificable, sea coeficiente, "
        "elasticidad, variación porcentual o función impulso-respuesta; estar redactado en "
        "español, inglés o portugués; y haber sido publicado entre 1990 y 2026.")
    apa.body(
        "Se excluirán los estudios agronómicos o climatológicos que no incorporen un resultado de "
        "precios, las simulaciones y proyecciones sin estimación empírica, los documentos de "
        "opinión y divulgación, y aquellos cuyo texto completo no resulte accesible tras "
        "solicitarlo a los autores. Los estudios agronómicos excluidos se registrarán por "
        "separado, pues resultan pertinentes para el marco teórico de la investigación principal "
        "aunque no para esta revisión.")

    apa.heading("Fuentes de Información y Estrategia de Búsqueda", level=1)
    tabla_apa(apa, 2, "Fuentes de Información Consultadas",
              ["Tipo de fuente", "Fuentes específicas"],
              [["Bases bibliográficas", "Scopus, Web of Science, EconLit, ScienceDirect, JSTOR"],
               ["Específicas de economía", "RePEc/IDEAS, NBER, SSRN"],
               ["Iberoamericanas", "SciELO, Redalyc, Latindex"],
               ["Tesis peruanas", "ALICIA (CONCYTEC), RENATI (SUNEDU)"],
               ["Institucionales", "BCRP, BID, CEPAL, FAO, FMI, Banco Mundial, IFPRI"],
               ["Complementarias",
                "Google Scholar (200 primeras entradas) y revisión de las referencias de los estudios incluidos"]],
              anchos_cm=[4.2, 11.8],
              nota="Las fuentes iberoamericanas y los repositorios de tesis peruanas suelen "
                   "omitirse en las búsquedas convencionales. Una estrategia restringida al "
                   "inglés y a las bases internacionales excluiría buena parte de la evidencia "
                   "regional pertinente para esta investigación.")

    apa.body(
        "La cadena de búsqueda para las bases en inglés combina tres bloques mediante el operador "
        "Y, con los sinónimos de cada bloque unidos mediante el operador O. El primer bloque "
        "recoge el fenómeno; el segundo, el resultado de precios; el tercero, el carácter "
        "empírico del estudio.")
    apa.block_quote(
        '("El Nino" OR "El Niño" OR "La Nina" OR ENSO OR "Southern Oscillation" OR "Oceanic Nino '
        'Index" OR "coastal El Nino" OR "sea surface temperature anomal*") AND ("food price*" OR '
        '"food inflation" OR "consumer price*" OR "price index" OR "agricultural price*" OR '
        '"price transmission") AND (empiric* OR estimat* OR panel OR regression OR "impulse '
        'response" OR econometric*)')
    apa.body(
        "Para las bases en español y portugués se emplea la cadena equivalente con los términos "
        "«El Niño», «La Niña», «Niño costero», «Oscilación del Sur», «anomalía climática» y "
        "«choque climático» en el primer bloque, y «precios de alimentos», «inflación de "
        "alimentos», «índice de precios», «precios agrícolas», «transmisión de precios» y «preços "
        "dos alimentos» en el segundo. Para los repositorios de tesis peruanas, cuyos buscadores "
        "admiten consultas menos complejas, se emplean términos sueltos.")
    apa.body(
        "Cada búsqueda se registrará indicando fecha, base consultada, cadena exacta empleada y "
        "número de resultados obtenidos. Dicha bitácora se incluirá como anexo: sin ella la "
        "revisión no es replicable, requisito que PRISMA 2020 establece de manera explícita.")

    apa.heading("Selección y Extracción de Datos", level=1)
    apa.body(
        "El proceso de selección comprende las cuatro fases del diagrama de flujo PRISMA: "
        "identificación, cribado por título y resumen, evaluación de elegibilidad mediante texto "
        "completo e inclusión. Se reportará el número de registros en cada fase y el motivo de "
        "cada exclusión producida en la fase de texto completo.")
    apa.body(
        "Corresponde declarar una limitación del diseño. PRISMA recomienda que el cribado sea "
        "realizado por dos revisores independientes, mientras que una tesis de pregrado cuenta "
        "normalmente con uno. Como mitigación, el asesor cribará de manera independiente una "
        "muestra aleatoria del 20 % de los registros y se reportará el índice kappa de Cohen como "
        "medida de concordancia. La mitigación es inferior al estándar, pero resulta verificable "
        "y es preferible a omitir la cuestión.")

    tabla_apa(apa, 3, "Campos de la Ficha de Extracción de Datos",
              ["Grupo", "Campos"],
              [["Identificación", "Autores, año, título, tipo de publicación, revista o institución, DOI"],
               ["Ámbito", "País, escala espacial, periodo de análisis"],
               ["Exposición", "Índice empleado, región oceánica, frecuencia"],
               ["Resultado", "Variable de precio, nivel de desagregación, fuente del dato"],
               ["Método", "Estimador, especificación, tratamiento de la endogeneidad, errores estándar"],
               ["Efecto", "Signo, magnitud, unidad, error estándar o estadístico t, número de observaciones"],
               ["Heterogeneidad", "Efectos reportados por región, cultivo o estación"],
               ["Dinámica", "Horizonte del efecto máximo y persistencia"],
               ["Calidad", "Exogeneidad declarada, efectos fijos, pruebas de robustez, replicabilidad"],
               ["Declaraciones", "Financiamiento, conflicto de interés, disponibilidad de datos y código"]],
              anchos_cm=[3.6, 12.4],
              nota="El grupo «Efecto» habilita el alcance B. Si el error estándar no se extrae "
                   "desde el inicio, un metaanálisis posterior obligaría a releer la totalidad de "
                   "los estudios.")

    apa.heading("Evaluación del Riesgo de Sesgo", level=1)
    apa.body(
        "No existe para la economía observacional un instrumento equivalente al que la "
        "colaboración Cochrane emplea con ensayos clínicos. La convención en economía no consiste "
        "en puntuar la calidad de los estudios, sino en codificar sus características y tratarlas "
        "como moderadores en la síntesis (Havránek et al., 2020). Se adopta dicha convención, "
        "codificando la estrategia de identificación, la inclusión de efectos fijos, el "
        "tratamiento de la dependencia temporal y transversal, la frecuencia de los datos, la "
        "escala espacial y el tipo de publicación.")
    apa.body(
        "La evaluación del riesgo de sesgo de publicación se rige por cinco reglas. Primera: "
        "emplear varias pruebas y nunca una sola, pues Lin et al. (2018), sobre 28 655 "
        "metaanálisis de la biblioteca Cochrane, encuentran una concordancia débil o moderada "
        "entre las pruebas disponibles. Segunda: no equiparar la asimetría del gráfico de embudo "
        "con el sesgo de publicación, dado que dicha asimetría admite otras causas, entre ellas la "
        "heterogeneidad entre estudios (Sterne et al., 2011). Tercera: tratar con cautela el "
        "procedimiento FAT-PET-PEESE, que según Alinaghi y Reed (2018) funciona adecuadamente bajo "
        "efectos fijos pero resulta poco fiable cuando existe heterogeneidad de efectos entre y "
        "dentro de los estudios, que es la situación de esta literatura. Cuarta: modelar la no "
        "independencia entre estimaciones mediante modelos multinivel, pues un estudio de economía "
        "reporta habitualmente varias estimaciones y Nakagawa et al. (2023) muestran que ignorar "
        "esa dependencia constituye un error extendido. Quinta: emplear la expresión «riesgo de "
        "sesgo de publicación» en lugar de afirmar que el sesgo existe (Afonso et al., 2023).")

    apa.heading("Síntesis de Resultados", level=1)
    apa.body(
        "En el alcance A la síntesis será narrativa y estructurada según escala espacial, índice "
        "empleado, signo y magnitud del efecto, horizonte temporal y región. Se acompañará de "
        "tablas de evidencia y de un gráfico de burbujas que cruce la escala espacial con el año "
        "de publicación, figura que respondería visualmente la segunda pregunta secundaria y "
        "documentaría la brecha identificada. En el alcance B, de resultar viable, se estimará un "
        "metaanálisis multinivel con metarregresión sobre los moderadores codificados y el "
        "conjunto de pruebas de sesgo de publicación descritas.")

    apa.heading("Uso de Inteligencia Artificial", level=1)
    apa.body(
        "La Meta-Analysis of Economics Research Network adoptó principios específicos para el uso "
        "de inteligencia artificial en metaanálisis de economía y actualizó en consecuencia sus "
        "guías de reporte (Cook et al., 2026). En caso de emplearse asistencia de inteligencia "
        "artificial en la búsqueda, el cribado o la extracción, corresponde declararlo indicando "
        "las fases, la herramienta y la verificación humana aplicada. Se propone la siguiente "
        "redacción, que deberá ajustarse a lo efectivamente realizado:")
    apa.block_quote(
        "Se empleó asistencia de inteligencia artificial en la fase de búsqueda exploratoria y en "
        "la identificación preliminar de literatura relevante. Toda referencia identificada por "
        "esa vía fue verificada manualmente contra la fuente primaria antes de su inclusión. El "
        "cribado por criterios de elegibilidad, la extracción de datos y la síntesis fueron "
        "realizados por el autor. Se siguen las guías de reporte de MAER-Net actualizadas para el "
        "uso de inteligencia artificial.")
    apa.body(
        "Esta exigencia tiene una implicación concreta para el presente proyecto. Parte de la "
        "literatura reunida hasta la fecha procede de búsquedas asistidas por inteligencia "
        "artificial, y varias referencias no han podido verificarse contra la fuente primaria. "
        "Dicha verificación constituye un requisito y no una formalidad: una revisión sistemática "
        "que cite lo que no ha leído carece de validez.")

    apa.heading("Cronograma", level=1)
    tabla_apa(apa, 4, "Cronograma del Alcance A, en Semanas",
              ["Semanas", "Actividad", "Producto"],
              [["1", "Afinar pregunta y criterios; registrar el protocolo", "Protocolo registrado"],
               ["2 a 3", "Ejecutar búsquedas y llevar bitácora", "Registros identificados"],
               ["4", "Eliminar duplicados y cribar por título y resumen", "Diagrama PRISMA, fases 1 y 2"],
               ["5", "Cribado independiente del asesor sobre el 20 %", "Índice kappa de Cohen"],
               ["6 a 7", "Lectura a texto completo y elegibilidad", "Diagrama PRISMA completo"],
               ["8 a 9", "Extracción de datos", "Matriz de evidencia"],
               ["10", "Codificación de características y riesgo de sesgo", "Tabla de moderadores"],
               ["11", "Síntesis narrativa y figuras", "Capítulo de resultados"],
               ["12", "Redacción, lista de verificación PRISMA y anexos", "Documento final"]],
              anchos_cm=[2.4, 8.0, 5.6])

    apa.heading("Limitaciones Previsibles", level=1)
    apa.body(
        "Se anticipan cinco limitaciones. La revisión contará con un solo revisor, mitigado "
        "parcialmente según lo descrito. Persistirá un sesgo idiomático residual, pues aunque "
        "tres idiomas superan la práctica habitual, la literatura en otros queda excluida. La "
        "heterogeneidad de las medidas del efecto podría impedir el alcance B. Parte de la "
        "literatura gris institucional no se encuentra indexada y requiere navegación directa en "
        "los repositorios. Finalmente, y es la limitación de mayor alcance, esta revisión "
        "documenta la brecha de conocimiento pero no resuelve el problema de disponibilidad de "
        "datos de la investigación principal: son tareas distintas y la segunda permanece "
        "pendiente.")

    apa.references_heading()
    apa.references([
        "Afonso, J., Ramirez-Campillo, R., Clemente, F. M., Büttner, F. C. y Andrade, R. (2023). "
        "The perils of misinterpreting and misusing “publication bias” in meta-analyses: "
        "An education review on funnel plot-based methods. Sports Medicine.",

        "Alinaghi, N. y Reed, W. R. (2018). Meta-analysis and publication bias: How well does the "
        "FAT-PET-PEESE procedure work? Research Synthesis Methods.",

        "Bartoš, F., Maier, M., Wagenmakers, E.-J., Doucouliagos, H., Stanley, T. D. y Ioannidis, "
        "J. P. A. (2022). Footprint of publication selection bias on meta-analyses in medicine, "
        "environmental sciences, psychology, and economics. Research Synthesis Methods.",

        "Cook, N., Havránek, T., Irsova, Z., Stanley, T. D. y Doucouliagos, H. (2026). Reporting "
        "guidelines for meta-analysis in economics—Updated for AI. Journal of Economic Surveys.",

        "Havránek, T., Stanley, T. D., Doucouliagos, H., Bom, P., Geyer-Klingeberg, J., Iwasaki, "
        "I., Reed, W. R., Rost, K. y van Aert, R. C. M. (2020). Reporting guidelines for "
        "meta-analysis in economics. Journal of Economic Surveys.",

        "Lin, L., Chu, H., Murad, M. H., Hong, C., Qu, Z., Cole, S. R. y Chen, Y. (2018). "
        "Empirical comparison of publication bias tests in meta-analysis. Journal of General "
        "Internal Medicine.",

        "Nakagawa, S., Yang, Y., Macartney, E. L., Spake, R. y Lagisz, M. (2023). Quantitative "
        "evidence synthesis: A practical guide on meta-analysis, meta-regression, and publication "
        "bias tests for environmental sciences. Environmental Evidence.",

        "Page, M. J., McKenzie, J. E., Bossuyt, P. M., Boutron, I., Hoffmann, T. C., Mulrow, C. D., "
        "Shamseer, L., Tetzlaff, J. M., Akl, E. A., Brennan, S. E., Chou, R., Glanville, J., "
        "Grimshaw, J. M., Hróbjartsson, A., Lalu, M. M., Li, T., Loder, E. W., Mayo-Wilson, E., "
        "McDonald, S., … Moher, D. (2021). The PRISMA 2020 statement: An updated guideline for "
        "reporting systematic reviews. BMJ, 372, n71. https://doi.org/10.1136/bmj.n71",

        "Stanley, T. D., Doucouliagos, H., Giles, M., Heckemeyer, J. H., Johnston, R. J., Laroche, "
        "P., Nelson, J. P., Paldam, M., Poot, J., Pugh, G., Rosenberger, R. S. y Rost, K. (2013). "
        "Meta-analysis of economics research reporting guidelines. Journal of Economic Surveys.",

        "Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., Terrin, N., Jones, D. R., Lau, J., "
        "Carpenter, J., Rücker, G., Harbord, R. M., Schmid, C. H., Tetzlaff, J., Deeks, J. J., "
        "Peters, J., Macaskill, P., Schwarzer, G., Duval, S., Altman, D. G., Moher, D. y Higgins, "
        "J. P. T. (2011). Recommendations for examining and interpreting funnel plot asymmetry in "
        "meta-analyses of randomised controlled trials. BMJ, 343, d4002. "
        "https://doi.org/10.1136/bmj.d4002",

        "Yepes-Núñez, J. J., Urrútia, G., Romero-García, M. y Alonso-Fernández, S. (2021). "
        "Declaración PRISMA 2020: una guía actualizada para la publicación de revisiones "
        "sistemáticas. Revista Española de Cardiología, 74(9), 790–799. "
        "https://doi.org/10.1016/j.recesp.2021.06.016",
    ])

    os.makedirs(os.path.dirname(salida), exist_ok=True)
    apa.save(salida)
    return salida


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apa-dir", help="directorio que contiene apa_docx.py")
    args = ap.parse_args()

    APADocument = cargar_apa(args.apa_dir)
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    salida = os.path.join(raiz, "docs", "tesis",
                          "Propuesta_revision_sistematica_APA.docx")
    construir(APADocument, salida)
    print(f"documento APA generado -> {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
