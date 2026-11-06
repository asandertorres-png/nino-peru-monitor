#!/usr/bin/env python3
"""Reune todo el avance metodologico de la tesis en un libro de Excel.

Salida: docs/tesis/Tesis_matrices.xlsx

DE DONDE SALE CADA HOJA
-----------------------
Los 27 indicadores y el esquema del panel se IMPORTAN de los scripts que ya
los definen, de modo que no puedan desalinearse:

    scripts/tesis/matriz.py          -> hoja Indicadores_detalle
    scripts/tesis/esquema_panel.py   -> hoja Matriz_de_datos

Los antecedentes y el marco teorico se definen aqui abajo Y TAMBIEN en
scripts/tesis/matrices_teoricas_docx.js. Es la unica duplicacion del
conjunto: si se agrega un antecedente hay que agregarlo en los dos sitios.
Se deja asi porque el generador de Word esta en Node y este en Python, y
montar un formato comun para dos listas no compensa.

Uso:
    python scripts/tesis/libro_excel.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension

from matriz import FILAS as IND_DETALLE, CAMPOS as IND_CABECERA
from esquema_panel import (CAMPOS as PANEL_CAMPOS,
                           CAMPOS_NORMALES as PANEL_NORMALES,
                           CIUDADES, PERIODO_INICIO, PERIODO_FIN)

# ------------------------------------------------------------------ estilo

FUENTE = "Arial"
AZUL = "1F3864"
GRIS = "F2F2F2"
GRIS_OSCURO = "D9D9D9"
AMBAR = "FFF2CC"
ROJO = "FBE5E5"
VERDE = "E2EFDA"

BORDE = Border(*[Side(style="thin", color="BFBFBF")] * 4)


def titulo_hoja(ws, texto, subtitulo=None, ancho=8):
    ws.cell(row=1, column=1, value=texto).font = Font(
        name=FUENTE, size=14, bold=True, color=AZUL)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ancho)
    fila = 2
    if subtitulo:
        c = ws.cell(row=2, column=1, value=subtitulo)
        c.font = Font(name=FUENTE, size=10, italic=True, color="595959")
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ancho)
        fila = 3
    ws.row_dimensions[1].height = 22
    return fila + 1  # una fila en blanco


def escribir_tabla(ws, fila_inicio, encabezados, filas, anchos,
                   alturas_auto=True, colorear=None):
    """Escribe una tabla con cabecera azul y bandas. Devuelve la fila siguiente."""
    for j, h in enumerate(encabezados, start=1):
        c = ws.cell(row=fila_inicio, column=j, value=h)
        c.font = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(horizontal="center", vertical="center",
                                wrap_text=True)
        c.border = BORDE
    ws.row_dimensions[fila_inicio].height = 30

    for i, fila in enumerate(filas):
        r = fila_inicio + 1 + i
        fondo = GRIS if i % 2 else None
        for j, v in enumerate(fila, start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = Font(name=FUENTE, size=10)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = BORDE
            especial = colorear(i, j, v) if colorear else None
            if especial:
                c.fill = PatternFill("solid", fgColor=especial)
            elif fondo:
                c.fill = PatternFill("solid", fgColor=fondo)

    for j, a in enumerate(anchos, start=1):
        ws.column_dimensions[get_column_letter(j)].width = a

    ws.freeze_panes = ws.cell(row=fila_inicio + 1, column=1)
    ws.auto_filter.ref = (f"A{fila_inicio}:"
                          f"{get_column_letter(len(encabezados))}"
                          f"{fila_inicio + len(filas)}")
    return fila_inicio + len(filas) + 2


def nota(ws, fila, texto, ancho=8):
    c = ws.cell(row=fila, column=1, value=texto)
    c.font = Font(name=FUENTE, size=9, italic=True, color="595959")
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=ancho)
    ws.row_dimensions[fila].height = 30
    return fila + 2


# ------------------------------------------------------------------ datos

TITULO_TESIS = ("Niño del Pacífico central y Niño costero: efecto diferenciado "
                "sobre la inflación de alimentos en 26 ciudades del Perú, 2010–2026")
AUTOR = "Alexander Torres Uchupe"

CONSISTENCIA = [
    ["General",
     "¿Cuál es el efecto diferenciado del Niño del Pacífico central (ONI) y del Niño costero (ICEN) sobre la inflación de alimentos de las ciudades del Perú, según la exposición económica de cada ciudad, 2010–2026?",
     "Determinar el efecto diferenciado del Niño del Pacífico central y del Niño costero sobre la inflación de alimentos de las ciudades del Perú, según la exposición económica de cada ciudad, 2010–2026.",
     "El efecto del Niño costero es mayor que el del Pacífico central en las ciudades de la costa norte, y la magnitud del efecto de ambos aumenta con la exposición económica de la ciudad.",
     "1 a 10"],
    ["Específico 1",
     "¿Cuál es el efecto de las anomalías climáticas locales sobre la inflación de alimentos de las ciudades del Perú?",
     "Estimar el efecto de las anomalías locales de precipitación y temperatura sobre la inflación de alimentos por ciudad.",
     "Las anomalías locales afectan la inflación de alimentos, alcanzando su efecto máximo dentro de los dieciocho meses posteriores al shock.",
     "1, 2, 7, 8"],
    ["Específico 2",
     "¿Cuál de los dos índices oceánicos —ONI o ICEN— explica mejor la inflación de alimentos de las ciudades del Perú?",
     "Comparar el poder explicativo del ONI y del ICEN-réplica sobre la inflación de alimentos por ciudad.",
     "En las ciudades de la costa norte del Perú, el ICEN explica la inflación de alimentos mejor que el ONI.",
     "3, 4, 7, 8"],
    ["Específico 3",
     "¿En qué medida difiere el efecto entre regiones según la exposición económica de cada ciudad?",
     "Contrastar la heterogeneidad regional del efecto según la exposición económica de cada ciudad.",
     "El efecto aumenta con la participación del sector agropecuario y pesquero en el VAB y con el peso del alimento en la canasta, y difiere en signo entre la costa norte y la sierra sur.",
     "5, 6, 1, 2"],
    ["Específico 4",
     "¿En qué medida se reduce la integración de los mercados de alimentos entre las ciudades del Perú durante los episodios cálidos del ENSO?",
     "Determinar en qué medida se reduce la integración de los mercados de alimentos entre las ciudades del Perú durante los episodios cálidos del ENSO.",
     "La integración de los mercados de alimentos entre las ciudades del Perú disminuye durante los episodios cálidos del ENSO.",
     "10, 3, 4"],
]

OPERACION = [
    ["X. Shock de oferta de origen ENSO", "D1. Magnitud del shock climático local",
     "1", "Anomalía estandarizada de precipitación mensual", "Razón (σ)", "Bloqueado"],
    ["X. Shock de oferta de origen ENSO", "D1. Magnitud del shock climático local",
     "2", "Anomalía estandarizada de temperatura máxima mensual", "Razón (σ)", "Bloqueado"],
    ["X. Shock de oferta de origen ENSO", "D2. Estado del océano",
     "3", "Índice ONI, región Niño 3.4 (Pacífico central)", "Razón (°C)", "Parcial"],
    ["X. Shock de oferta de origen ENSO", "D2. Estado del océano",
     "4", "Índice ICEN-réplica, región Niño 1+2 (Niño costero)", "Razón (°C)", "Parcial"],
    ["X. Shock de oferta de origen ENSO", "D3. Exposición económica",
     "5", "Participación del sector agropecuario y pesquero en el VAB departamental",
     "Razón (%)", "No verificado"],
    ["X. Shock de oferta de origen ENSO", "D3. Exposición económica",
     "6", "Participación de los alimentos en la canasta del IPC de la ciudad",
     "Razón (%)", "En riesgo"],
    ["Y. Precios de alimentos al consumidor urbano", "D1. Nivel de precios",
     "7", "Variación mensual del IPC de alimentos", "Razón (%)", "En riesgo"],
    ["Y. Precios de alimentos al consumidor urbano", "D1. Nivel de precios",
     "8", "Variación a doce meses del IPC de alimentos", "Razón (%)", "En riesgo"],
    ["Y. Precios de alimentos al consumidor urbano", "D2. Volatilidad",
     "9", "Desviación estándar móvil de doce meses de la inflación de alimentos",
     "Razón", "Derivado"],
    ["Y. Precios de alimentos al consumidor urbano", "D3. Integración de mercados",
     "10", "Correlación de la inflación de alimentos con la de las demás ciudades",
     "Razón", "Derivado"],
]

# [nivel, autor y anio, titulo, metodologia, resultados, aporte o vacio]
# OJO: duplicado con scripts/tesis/matrices_teoricas_docx.js
ANTECEDENTES = [
    ["Internacional", "Cashin, Mohaddes y Raissi (2015)",
     "Fair Weather or Foul? The Macroeconomic Effects of El Niño",
     "GVAR con 21 modelos país o región, 1979Q2–2013Q1",
     "Estima la transmisión internacional de El Niño con exposiciones directas e indirectas",
     "Antecedente macro de referencia. Deja abierto todo lo subnacional"],
    ["Internacional", "McNew (1996)",
     "Spatial Market Integration: Definition, Theory and Evidence",
     "Modelo punto-espacio; maíz del Misisipi durante la inundación de 1993",
     "Los mayores costos de transporte redujeron la integración y la transferencia de shocks entre regiones",
     "Funda el mecanismo de costos de transacción: hipótesis 4 y la mitad del mecanismo de la 3"],
    ["Internacional", "Ubilava (2017)",
     "ENSO y la dinámica de precios de commodities",
     "43 precios mensuales y anomalías de TSM de la región Niño 3.4",
     "ENSO afecta la dinámica de precios, con asimetrías entre fases",
     "Funda la asimetría. No trata el IPC ni el nivel subnacional"],
    ["Internacional", "Abril et al. (2019)",
     "Relación no lineal entre El Niño y los precios de alimentos en Colombia",
     "Series de precios; énfasis en el evento 2015-16",
     "La relación entre ENSO y precios de alimentos es no lineal",
     "Funda la no linealidad de la respuesta"],
    ["Internacional", "Letta et al. (2021)",
     "Weather shocks, traders' expectations and food prices",
     "Panel distrital mensual de precios mayoristas, India 2004–2017",
     "La sequía eleva los precios antes de la cosecha; las expectativas anticipan más del 80 % del impacto",
     "Funda el canal de expectativas y obligó a reformular la hipótesis 1"],
    ["Internacional", "Emediegwu (2024)",
     "Efecto asimétrico de las anomalías climáticas sobre precios locales",
     "Modelos STAR variables en el tiempo; 1 100 mercados en 36 países de África subsahariana",
     "ENSO afecta cerca de la mitad de los precios, con asimetría y persistencia; la respuesta debe ser subregional",
     "Funda la asimetría y el argumento de desagregación espacial"],
    ["Internacional", "Gallegati et al. (2026); Solomou et al. (2025)",
     "Diversidad de ENSO: Pacífico central frente a oriental",
     "GVAR y wavelets sobre inflación nacional de varios países",
     "Los tipos CP y EP difieren en estructura, intensidad y perfil temporal, y sus efectos sobre la inflación no son los mismos",
     "Antecedente directo del objetivo 2. Lo estima ENTRE países; la tesis lo estima DENTRO de uno"],
    ["Internacional", "Yilmazkuday (2025)",
     "El Niño, La Niña and Inflation",
     "Proyecciones locales, 188 países, 1970–2023",
     "La Niña eleva todas las medidas de inflación; los países en desarrollo más en alimentos; efectos crecientes en el tiempo",
     "Respalda la técnica y advierte contra suponer el signo"],
    ["Internacional", "Arango-Castillo et al. (2025)",
     "Anomalías de temperatura y precipitación e inflación en México",
     "Panel regional; ARDL y proyecciones locales; anomalías ponderadas por población",
     "Sin efecto de corto plazo; en el largo plazo solo la precipitación importa",
     "Antecedente metodológico más cercano. Advierte que un no-resultado es posible"],
    ["Nacional", "Saldarriaga (2016), BID",
     "Variabilidad de la temperatura, productividad y precios agrícolas en el Perú",
     "ENAHO 2004–2010 con grilla climática de 0,5°; variación interanual dentro de municipalidad",
     "1 σ de temperatura reduce la producción entre US$ 170 y 190 por hectárea; las cálidas dañan más que las frías",
     "Antecedente nacional más cercano en precios. Solo temperatura, precios en finca, hasta 2010"],
    ["Nacional", "Crofils, Gallic y Vermandel (2024), JEEM",
     "The dynamic effects of weather shocks on agricultural production",
     "Proyecciones locales sobre producción agrícola mensual del Perú",
     "Caída de ~5 % mensual hasta cuatro meses; mayor en selva y temporada de crecimiento; a nivel macro eleva la inflación",
     "El antecedente más cercano que existe. Deja abierto el IPC por ciudad y la separación ONI/ICEN"],
    ["Nacional", "Calero y Rodríguez (2026), PUCP",
     "Efectos variables en el tiempo de shocks climáticos en el Perú",
     "TVP-VAR con volatilidad estocástica",
     "Shocks de oferta: PBI −0,8 pp, inflación +0,25 pp, pesca −5,0 pp; efectos mayores en 1998Q2 y 2017Q2",
     "Confirma el canal inflacionario. Obliga a replantear el aporte: medir la distribución, no descubrir el efecto"],
    ["Nacional", "BCRP DT 008-2025; BIS WP 1276",
     "ENSO and its Economic Impact in the Peruvian Economy",
     "Modelo semi-estructural; BCRPData 1994M1–2019M12",
     "Huella de shock de oferta; el sector primario responde antes, más y de forma persistente",
     "Agregado nacional, sin precios regionales"],
    ["Nacional", "Tambet y Stopnitzky (2021), AJAE",
     "Climate Adaptation and Conservation Agriculture among Peruvian Farmers",
     "Tres rondas de la Encuesta Nacional Agropecuaria con shocks georreferenciados de lluvia",
     "Los productores ajustan prácticas según el shock",
     "Evidencia de respuesta endógena. Señala la ENA como fuente no considerada"],
    ["Nacional", "Andrián et al. (2024); Martin (2016), BID",
     "El Niño en la Región Andina",
     "VAR con El Niño como variable exógena",
     "Crecimiento −0,1 a −3,4 pp, Perú entre los más afectados; inflación +0,7 a +3,5 pp",
     "La conclusión sobre estructura económica es la justificación de medir dentro del país"],
    ["Nacional", "Briceño-Ávalos et al. (2025)",
     "Efectos del cambio climático sobre el bienestar",
     "Serie nacional 1950–2023 y panel regional 2014–2023",
     "La duración de El Niño y La Niña no resulta significativa",
     "Debilita el panel departamental anual; refuerza la frecuencia mensual"],
    ["Local", "Canedo-Rosso et al. (2020)",
     "Drought and Agricultural Production in the Central Andes",
     "Precipitación de verano y fases de ENSO; rendimientos de quinua y papa",
     "Menor rendimiento de quinua y papa en años de El Niño fuerte y muy fuerte",
     "Sostiene el mecanismo de déficit hídrico en la sierra sur"],
    ["Local", "Arana-Ruedas et al. (2023)",
     "ENSO y sequía agrícola en el valle del Mantaro",
     "SPEI en cuatro provincias y seis estaciones, 1990–2021",
     "El 70 % de los eventos de sequía agrícola ocurrió con ENSO presente",
     "Cuantifica el vínculo ENSO–sequía–agricultura en la sierra"],
    ["Local", "Ponce (2020, World Development; 2023, JDS)",
     "Variabilidad climática intraestacional en los Andes peruanos",
     "Censos agrarios con clima distrital; efectos fijos con heterogeneidad por subregión",
     "Efectos heterogéneos; ningún efecto directo entre los hogares del sur",
     "Antecedente económico más próximo a la sierra sur. Advierte de un posible no-resultado"],
    ["Local", "Imfeld et al. (2020)",
     "Climatología y tendencias en los Andes del sur del Perú",
     "Datos de estación homogeneizados más grilla, 1965/66–2017/18",
     "ENSO modifica precipitación y temperatura, con tendencias mayores en las máximas",
     "Candidato para validar las normales ERA5 en el sur"],
    ["Local", "Estudio ricardiano del Altiplano (2021)",
     "Impacto del cambio climático en la quinua orgánica, Puno",
     "Enfoque ricardiano; 237 agricultores en Cabana, Capachica e Ilave",
     "El impacto de las variables agroclimáticas sobre el ingreso resultó marginal",
     "Antecedente local, económico y en español. Advierte de un posible no-resultado"],
]

MARCO = [
    ["I", "El clima como variación identificadora",
     "Hsiang (2016); Dell, Jones y Olken (2014); Blanc y Schlenker (2017); Mérel y Gammans (2018)",
     "La variación meteorológica dentro de una unidad es exógena una vez absorbido lo invariante, y permite identificar efectos. Pero los efectos fijos absorben señal y el ruido de medición sesga los coeficientes hacia abajo",
     "P10. La agregación puntual atenúa el coeficiente hacia cero",
     "Identificación y H6"],
    ["II", "Almacenamiento competitivo con expectativas racionales",
     "Wright y Williams (1982); Deaton y Laroque (1992, 1996); Cafiero et al. (2011, 2014); Gouel y Legrand (2025, 2026)",
     "El inventario amortigua el excedente pero la no negatividad no amortigua el déficit. Sin existencias el precio sube abruptamente, y el mismo shock da respuestas distintas según el stock",
     "P1 convexidad; P2 asimetría; P3 dependencia del estado",
     "H4 y H4b (robustez)"],
    ["III", "Expectativas de los comerciantes",
     "Letta et al. (2021)",
     "Los precios incorporan la información del shock antes de que el daño se materialice. El rezago entre señal y realización separa ambos canales",
     "P4. Parte del efecto anticipa la realización",
     "H1 (reformulada por este pilar)"],
    ["IV", "Equilibrio espacial de precios con costos de transacción",
     "Enke (1951); Samuelson (1952); Takayama y Judge (1964); Goodwin y Piggott (2001); McNew (1996); Roehner (1996); Zhu (2018)",
     "Los precios de regiones que comercian se mueven juntos solo mientras el diferencial supere los costos de transacción. Al subir estos, la banda neutral se ensancha y el mercado se segmenta",
     "P5 exposición y aislamiento; P6 la integración cae; P7 transmisión no lineal",
     "H2 (mecanismo) y H5"],
    ["V", "Traspaso a la inflación y segunda vuelta",
     "Jalil y Tamayo (2011); Furceri et al. (2016); Anand, Ding y Tulin (2014)",
     "El traspaso del precio de alimentos a la inflación general es incompleto y rezagado, y mayor donde el alimento pesa más en la canasta",
     "P8. Traspaso incompleto, de uno a seis trimestres",
     "Justifica el IPC como dependiente y fija el horizonte de H1"],
    ["VI", "Diversidad de ENSO: Pacífico central y oriental",
     "Gallegati et al. (2026); Solomou et al. (2025); criterio del ENFEN",
     "Los tipos de El Niño del Pacífico central y oriental difieren en estructura, intensidad y perfil temporal, y sus efectos económicos no tienen por qué coincidir",
     "P9. ONI e ICEN tienen efectos distintos, y la diferencia varía por región",
     "H3, la hipótesis que da el título"],
]

METODOLOGIA = [
    ["Diseño", "Enfoque", "Cuantitativo"],
    ["Diseño", "Tipo de investigación", "Aplicada (verificar el reglamento de la escuela: hay escuelas que la llamarían básica o sustantiva)"],
    ["Diseño", "Nivel", "Explicativo"],
    ["Diseño", "Diseño", "No experimental, longitudinal de panel (ex post facto)"],
    ["Diseño", "Método", "Hipotético-deductivo"],
    ["Población y muestra", "Población", "Las 26 ciudades del ámbito urbano que componen el IPC del INEI, enero 2010 – septiembre 2026"],
    ["Población y muestra", "Muestra", "Censal: las 26 ciudades. Aproximadamente 5 226 observaciones ciudad-mes"],
    ["Población y muestra", "Unidad de análisis", "La ciudad-mes"],
    ["Recolección", "Técnica", "Análisis documental de fuentes secundarias de acceso abierto"],
    ["Recolección", "Instrumento", "Ficha de registro de datos secundarios"],
    ["Procesamiento", "Preparación de datos",
     "Panel ciudad-mes 2010–2026 desde series diarias de ERA5 y el IPC del INEI; media y desviación estándar por unidad y mes sobre 1991–2020; empalme de bases 2009 y dic-2021; réplica del ICEN y su validación contra el IGP"],
    ["Procesamiento", "Técnica principal",
     "Proyecciones locales en panel CON AUMENTO DE REZAGOS, efectos fijos de ciudad y tiempo, horizontes h = 0 a 24 (Jordà, 2005; Montiel Olea y Plagborg-Møller, 2021)"],
    ["Procesamiento", "Corrección de sesgo",
     "Jackknife de medio panel, por el sesgo de Nickell implícito que subestima los efectos (Mei, Sheng y Shi, 2023)"],
    ["Procesamiento", "Inferencia",
     "Rezagos como controles y agrupamiento transversal (Almuzara y Sarto, 2024). Driscoll–Kraay y bootstrap wild cluster como contraste"],
    ["Procesamiento", "Por objetivo",
     "Obj. 2: dos estimaciones paralelas y comparación de ajuste por zona. Obj. 3: interacción exposición × shock con heterogeneidad por subregión (Ponce, 2020). Obj. 4: correlaciones móviles y modelo con umbral (Goodwin y Piggott, 2001)"],
    ["Procesamiento", "Robustez",
     "Dependencia espacial sobre residuos y panel espacial si resulta significativa (Baltagi y Pirotte, 2010); quiebre estructural y submuestras (Duran y Dindaroğlu, 2021); proyecciones locales suavizadas (Barnichon y Brownlees, 2019); placebo con rezagos adelantados; exclusión de 2017 y 2023"],
    ["Procesamiento", "Software", "Python, con código y datos derivados versionados en repositorio público"],
]

CRONOGRAMA = [
    ["0", "Persistir el panel climático mensual y re-indexar tmax y tmin", "Panel climático mensual", "PREVIA — desbloquea los indicadores 1 y 2"],
    ["1", "Verificar la disponibilidad del IPC por ciudad y división de gasto", "Nota de decisión de datos", "PREVIA — decide la viabilidad"],
    ["2", "Mapear las 26 ciudades; descargar normales ERA5; arreglar el parser de TSM semanal y extender el ONI a 1950", "Normales por ciudad", ""],
    ["3", "Descargar el IPC y construir el panel", "data/tesis/panel.csv", ""],
    ["4", "Calcular la réplica del ICEN y validarla contra los informes del IGP", "ICEN-réplica validado", "Sostiene el título"],
    ["5", "Descriptiva, gráficos y control de calidad del panel", "Capítulo de datos", ""],
    ["6–7", "Especificaciones A y B", "Resultados preliminares", ""],
    ["8", "Proyecciones locales", "Función impulso-respuesta", ""],
    ["9", "Heterogeneidad, ONI frente a ICEN, integración", "Capítulo de resultados", ""],
    ["10", "Robustez completa, con el placebo primero", "Capítulo de robustez", ""],
    ["11", "Redacción de los capítulos 1 a 4", "Borrador completo", ""],
    ["12", "Revisión, anexos y reproducibilidad de punta a punta", "Documento final", ""],
]

REV_SISTEMATICA = [
    ["Estándar", "PRISMA 2020 (Page et al., 2021) para el reporte y guías de MAER-Net (Havránek et al., 2020; Cook et al., 2026) para lo específico de economía"],
    ["Dato que condiciona el diseño", "Bartoš et al. (2022): los metaanálisis en economía son los MÁS contaminados por sesgo de publicación de cuatro campos; tras ajustar, la probabilidad mediana de que exista un efecto cae de 99,9 % a 29,7 %"],
    ["Alcance recomendado", "A. Revisión cualitativa, 10 a 12 semanas. B. Con metaanálisis, 20 a 30 semanas, condicionada a que haya efectos comparables con su error estándar"],
    ["Pregunta principal", "¿Cuál es el efecto de los shocks de ENSO sobre los precios de alimentos, y cómo varía según la escala espacial a la que se mide?"],
    ["Pregunta clave", "¿Qué proporción de los estudios estima a escala subnacional? Es la brecha de la tesis: si se cuantifica, la justificación deja de ser una afirmación del autor"],
    ["Registro", "OSF Registries. PROSPERO solo acepta revisiones con desenlaces en salud"],
    ["Fuentes que suelen omitirse", "SciELO, Redalyc, Latindex; y ALICIA (CONCYTEC) y RENATI (SUNEDU) para tesis peruanas"],
    ["Literatura gris", "Se incluye deliberadamente: es donde están los resultados no significativos que las revistas rechazan"],
    ["Riesgo de sesgo", "Codificar características como moderadores, no puntuar calidad (Havránek et al., 2020). Varias pruebas de sesgo de publicación, nunca una (Lin et al., 2018). FAT-PET-PEESE con cautela bajo heterogeneidad (Alinaghi y Reed, 2018). Modelos multinivel (Nakagawa et al., 2023)"],
    ["Un solo revisor", "PRISMA pide dos. Mitigación: el asesor criba el 20 % y se reporta el kappa de Cohen"],
    ["Uso de IA", "MAER-Net exige declararlo desde 2026 (Cook et al.). Toda referencia hallada con asistencia debe verificarse contra la fuente primaria"],
]

ESTADO_FUENTES = [
    ["1, 2", "Anomalías estandarizadas de lluvia y temperatura", "ERA5 vía Open-Meteo", "Bloqueado",
     "σ por unidad y mes no existe en el producto actual; requiere persistir el panel climático"],
    ["3", "Índice ONI", "NOAA/CPC", "Parcial", "La serie guardada arranca en 2021; extenderla a 1950"],
    ["4", "ICEN-réplica", "NOAA/CPC", "Parcial",
     "Calculable; falta validarla contra los informes del IGP. El nombre réplica es obligatorio hasta entonces"],
    ["5", "VAB departamental", "INEI", "No verificado", "Ruta de descarga en formato utilizable"],
    ["6", "Ponderaciones del IPC por ciudad", "INEI", "En riesgo",
     "Si solo existen para Lima, el indicador no varía entre ciudades. Plan alternativo: peso nacional"],
    ["7, 8", "IPC de alimentos por ciudad", "INEI", "En riesgo · decide el diseño",
     "El BCRP publica el IPC nacional pero no por ciudad. El INEI sí publica por ciudad y gran grupo, pero en boletines PDF"],
    ["9, 10", "Volatilidad e integración", "Derivados de 7 y 8", "Derivado", "Disponibles en cuanto existan 7 y 8"],
]

REFERENCIAS = [
    "Afonso, J. et al. (2023). The perils of misinterpreting and misusing publication bias in meta-analyses. Sports Medicine.",
    "Alinaghi, N. y Reed, W. R. (2018). Meta-analysis and publication bias: How well does the FAT-PET-PEESE procedure work? Research Synthesis Methods.",
    "Almuzara, M. y Sarto, A. (2024). Micro Responses to Macro Shocks. Staff Reports, Federal Reserve Bank of New York.",
    "Andrián, L. et al. (2024). Efectos del fenómeno El Niño en la Región Andina. BID. https://doi.org/10.18235/0005494",
    "Arana-Ruedas, D. P. R. et al. (2023). ENSO influence on agricultural drought, Mantaro Valley. Manglar.",
    "Baltagi, B. y Pirotte, A. (2010). Panel Data Inference Under Spatial Dependence. https://doi.org/10.2139/SSRN.1805892",
    "Barnichon, R. y Brownlees, C. (2019). Impulse Response Estimation by Smooth Local Projections. REStat.",
    "Bartoš, F. et al. (2022). Footprint of publication selection bias on meta-analyses. Research Synthesis Methods.",
    "Blanc, É. y Schlenker, W. (2017). The Use of Panel Models in Assessments of Climate Impacts on Agriculture. REEP.",
    "Calero, R. y Rodríguez, G. (2026). Time-varying effects of climate change shocks in Peru. PUCP. https://doi.org/10.18800/2079-8474.0558",
    "Canedo-Rosso, C. et al. (2020). Drought and Agricultural Production in the Central Andes.",
    "Cashin, P., Mohaddes, K. y Raissi, M. (2015). Fair Weather or Foul? The Macroeconomic Effects of El Niño.",
    "Cook, N. et al. (2026). Reporting guidelines for meta-analysis in economics—Updated for AI. Journal of Economic Surveys.",
    "Crofils, C., Gallic, E. y Vermandel, G. (2024). The dynamic effects of weather shocks on agricultural production. JEEM. https://doi.org/10.1016/j.jeem.2024.103078",
    "Dell, M., Jones, B. y Olken, B. (2014). What Do We Learn from the Weather? JEL 52(3).",
    "Duran, H. E. y Dindaroğlu, B. (2021). Regional inflation persistence in Turkey. Growth and Change. https://doi.org/10.1111/GROW.12456",
    "Emediegwu, L. (2024). Assessing the Asymmetric Effect of Global Climate Anomalies on Food Prices. Environmental and Resource Economics.",
    "Furceri, D. et al. (2016). Global food prices and domestic inflation. Oxford Economic Papers 68(3).",
    "Goodwin, B. y Piggott, N. (2001). Spatial Market Integration in the Presence of Threshold Effects. AJAE.",
    "Havránek, T. et al. (2020). Reporting guidelines for meta-analysis in economics. Journal of Economic Surveys.",
    "Herbst, E. y Johannsen, B. (2024). Bias in local projections. Journal of Econometrics.",
    "Hsiang, S. (2016). Climate Econometrics. NBER Working Paper.",
    "Imfeld, N. et al. (2020). Precipitation and temperature climatology in the southern Andes of Peru. Int. J. Climatology.",
    "Jalil, M. y Tamayo Zea, E. (2011). Pass-through of International Food Prices to Domestic Inflation. https://doi.org/10.13043/DYS.67.4",
    "Jordà, Ò. (2005). Estimation and Inference of Impulse Responses by Local Projections. AER 95(1).",
    "Kirillov, A. (2017). Inflación de precios de alimentos en las regiones de Rusia. Spatial Economics. https://doi.org/10.14530/SE.2017.4.041-058",
    "Letta, M. et al. (2021). Weather shocks, traders' expectations, and food prices. AJAE.",
    "Lin, L. et al. (2018). Empirical comparison of publication bias tests in meta-analysis. JGIM.",
    "Martin, L. (2016). ¡Es Niño! Impacto económico en la Región Andina. BID. https://doi.org/10.18235/0000234",
    "McNew, K. (1996). Spatial Market Integration: Definition, Theory, and Evidence. ARER. https://doi.org/10.1017/S1068280500000010",
    "Mei, Z.-W., Sheng, X.-S. y Shi, Z. (2023). Nickell bias in panel local projection. Journal of International Economics.",
    "Montiel Olea, J. L. y Plagborg-Møller, M. (2021). Local Projection Inference Is Simpler and More Robust Than You Think. Econometrica.",
    "Nakagawa, S. et al. (2023). Quantitative evidence synthesis. Environmental Evidence.",
    "Page, M. J. et al. (2021). The PRISMA 2020 statement. BMJ 372, n71. https://doi.org/10.1136/bmj.n71",
    "Ponce, C. (2020). Intra-seasonal climate variability and crop diversification in the Peruvian Andes. World Development.",
    "Ponce, C. (2023). Revisiting the Determinants of Non-farm Labour Income in the Peruvian Andes. JDS.",
    "Saldarriaga, V. (2016). Efectos de la variabilidad de la temperatura en la productividad y los precios agrícolas. BID. https://doi.org/10.18235/0000522",
    "Solomou, S. et al. (2025). The macroeconomic effects of El Niño diversity: a GVAR approach. Climate Research.",
    "Stanley, T. D. et al. (2013). Meta-analysis of economics research reporting guidelines. Journal of Economic Surveys.",
    "Sterne, J. A. C. et al. (2011). Recommendations for examining funnel plot asymmetry. BMJ 343, d4002.",
    "Tambet, H. y Stopnitzky, Y. (2021). Climate Adaptation and Conservation Agriculture among Peruvian Farmers. AJAE.",
    "Thombs, R. P. (2022). A Guide to Analyzing Large N, Large T Panel Data. Socius.",
    "Tito, R. et al. (2018). Global climate change increases risk of crop yield losses in the tropical Andes. Global Change Biology.",
    "Ubilava, D. (2017). The Role of ENSO in Commodity Price Movement and Predictability. AJAE.",
    "von Braun, J. y Tadesse, G. (2012). Global Food Price Volatility and Spikes. https://doi.org/10.22004/AG.ECON.120021",
    "Wright, B. y Williams, J. (1982). The Economic Role of Commodity Storage. The Economic Journal.",
    "Yglesias-González, M. et al. (2023). Reflections on the Peruvian 2017 Coastal El Niño event. PLOS ONE 18(9). https://doi.org/10.1371/journal.pone.0290767",
    "Yilmazkuday, H. (2025). El Niño, La Niña and Inflation. https://doi.org/10.2139/ssrn.5014991",
]

ESTADOS_COLOR = {
    "Bloqueado": ROJO,
    "En riesgo": AMBAR,
    "En riesgo · decide el diseño": AMBAR,
    "Parcial": AMBAR,
    "No verificado": GRIS_OSCURO,
    "Derivado": VERDE,
}


# ------------------------------------------------------------------ hojas

def main():
    wb = Workbook()

    # ---------------------------------------------------------- Índice
    ws = wb.active
    ws.title = "Índice"
    f = titulo_hoja(ws, "Tesis · avance metodológico", TITULO_TESIS, ancho=4)
    ws.cell(row=f, column=1, value=f"Autor: {AUTOR}").font = Font(
        name=FUENTE, size=10, bold=True)
    f += 2

    # Los rangos NO se escriben a mano: se calculan desde la longitud real de
    # cada lista. Escribirlos a mano produjo un error de un lugar en las once
    # formulas, que el recalculo no detecta porque evaluan sin error.
    FILA_DATOS = 5  # titulo en 1, subtitulo en 2, cabecera en 4, datos desde 5

    def cuenta(hoja, col, n):
        return f"=COUNTA('{hoja}'!{col}{FILA_DATOS}:{col}{FILA_DATOS + n - 1})"

    indice = [
        ["Consistencia", "Matriz de consistencia: problema, objetivo e hipótesis",
         cuenta("Consistencia", "A", len(CONSISTENCIA)), "filas"],
        ["Operacionalización", "Variables, dimensiones e indicadores",
         cuenta("Operacionalización", "C", len(OPERACION)), "indicadores"],
        ["Indicadores_detalle", "Anexo técnico: fórmula de cada indicador",
         cuenta("Indicadores_detalle", "C", len(IND_DETALLE)), "indicadores"],
        ["Matriz_de_datos", "Esquema del panel y tabla auxiliar de normales",
         cuenta("Matriz_de_datos", "B", len(PANEL_CAMPOS)), "campos"],
        ["Antecedentes", "Internacionales, nacionales y locales",
         cuenta("Antecedentes", "B", len(ANTECEDENTES)), "trabajos"],
        ["Marco_teórico", "Pilares, postulados, predicciones e hipótesis",
         cuenta("Marco_teórico", "A", len(MARCO)), "pilares"],
        ["Metodología", "Diseño, población, muestra y procesamiento",
         cuenta("Metodología", "B", len(METODOLOGIA)), "entradas"],
        ["Estado_fuentes", "Qué indicador se puede calcular hoy y cuál no",
         cuenta("Estado_fuentes", "A", len(ESTADO_FUENTES)), "grupos"],
        ["Cronograma", "Doce semanas, más dos tareas previas",
         cuenta("Cronograma", "A", len(CRONOGRAMA)), "etapas"],
        ["Rev_sistemática", "Propuesta de revisión sistemática",
         cuenta("Rev_sistemática", "A", len(REV_SISTEMATICA)), "puntos"],
        ["Referencias", "Bibliografía reunida",
         cuenta("Referencias", "A", len(REFERENCIAS)), "referencias"],
    ]
    f2 = escribir_tabla(ws, f, ["Hoja", "Contenido", "Cantidad", "Unidad"],
                        indice, [22, 56, 12, 14])
    f2 = nota(ws, f2,
              "Las cantidades se calculan con fórmulas sobre cada hoja: si se agrega o "
              "quita una fila, el índice se actualiza solo.", ancho=4)
    nota(ws, f2,
         "ADVERTENCIA. Ninguno de los 10 indicadores está confirmado todavía. Ver la hoja "
         "Estado_fuentes: faltan persistir el panel climático y confirmar que el INEI "
         "publique el IPC por ciudad y división de gasto. Este libro documenta el diseño, "
         "no garantiza que los datos existan.", ancho=4)

    # ---------------------------------------------------------- Consistencia
    ws = wb.create_sheet("Consistencia")
    f = titulo_hoja(ws, "Matriz de consistencia",
                    "1 problema general y 4 específicos; cada fila cierra con su objetivo, "
                    "hipótesis e indicadores", ancho=5)
    f = escribir_tabla(ws, f, ["Nivel", "Problema", "Objetivo", "Hipótesis", "Indicadores"],
                       CONSISTENCIA, [14, 52, 52, 52, 14])
    nota(ws, f,
         "La construcción del panel y la validación del ICEN no figuran como objetivos: son "
         "tareas previas y van en metodología. La asimetría y la dependencia del nivel de "
         "existencias se tratan como análisis de robustez. En la hipótesis específica 4 se "
         "contrasta la predicción, no el mecanismo, porque no hay datos de transporte.", ancho=5)

    # ---------------------------------------------------------- Operacionalización
    ws = wb.create_sheet("Operacionalización")
    f = titulo_hoja(ws, "Matriz de operacionalización de variables",
                    "2 variables · 6 dimensiones · 10 indicadores", ancho=6)

    def color_ope(i, j, v):
        return ESTADOS_COLOR.get(v) if j == 6 else None

    f = escribir_tabla(ws, f,
                       ["Variable", "Dimensión", "N°", "Indicador", "Escala", "Estado del dato"],
                       OPERACION, [32, 32, 6, 56, 16, 20], colorear=color_ope)
    nota(ws, f,
         "El detalle de cada indicador, con su fórmula, está en la hoja Indicadores_detalle.",
         ancho=6)

    # ---------------------------------------------------------- Indicadores detalle
    ws = wb.create_sheet("Indicadores_detalle")
    f = titulo_hoja(ws, "Anexo técnico: los 27 indicadores con su fórmula",
                    "Versión completa de la que la matriz del cuerpo toma 10", ancho=11)
    f = escribir_tabla(ws, f, list(IND_CABECERA), [list(x) for x in IND_DETALLE],
                       [30, 20, 8, 34, 58, 18, 12, 26, 16, 40, 14])

    # ---------------------------------------------------------- Matriz de datos
    ws = wb.create_sheet("Matriz_de_datos")
    periodos = 201
    f = titulo_hoja(ws, "Matriz de datos · panel principal",
                    f"Unidad de observación: la ciudad-mes · formato largo · {CIUDADES} "
                    f"ciudades × {periodos} periodos · {PERIODO_INICIO} a {PERIODO_FIN}",
                    ancho=8)
    filas_panel = [[c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]] for c in PANEL_CAMPOS]
    f = escribir_tabla(ws, f,
                       ["N°", "Campo", "Etiqueta", "Tipo", "Escala", "Rango válido",
                        "Fuente", "Indicador"],
                       filas_panel, [6, 18, 40, 10, 12, 34, 28, 14])
    ws.cell(row=f, column=1, value="Tabla auxiliar: normales climáticas").font = Font(
        name=FUENTE, size=12, bold=True, color=AZUL)
    f += 1
    ws.cell(row=f, column=1,
            value=f"Se une al panel por (ciudad, mes). {CIUDADES * 12} filas. Estos campos "
                  f"NO van en el panel: son constantes para cada par ciudad-mes del año.").font = Font(
        name=FUENTE, size=9, italic=True, color="595959")
    f += 2
    filas_norm = [[c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]] for c in PANEL_NORMALES]
    for j, h in enumerate(["N°", "Campo", "Etiqueta", "Tipo", "Escala", "Rango válido",
                           "Fuente", "Papel"], start=1):
        c = ws.cell(row=f, column=j, value=h)
        c.font = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        c.border = BORDE
    for i, fila in enumerate(filas_norm):
        for j, v in enumerate(fila, start=1):
            c = ws.cell(row=f + 1 + i, column=j, value=v)
            c.font = Font(name=FUENTE, size=10)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = BORDE
            if i % 2:
                c.fill = PatternFill("solid", fgColor=GRIS)
    nota(ws, f + len(filas_norm) + 2,
         "Los vacíos se dejan en blanco, nunca como 0 ni como −99: un cero es un dato y un "
         "vacío es su ausencia. Las plantillas para llenar están en docs/tesis/"
         "plantilla_panel.csv y plantilla_normales.csv, y se validan con "
         "scripts/tesis/esquema_panel.py --validar.", ancho=8)

    # ---------------------------------------------------------- Antecedentes
    ws = wb.create_sheet("Antecedentes")
    f = titulo_hoja(ws, "Matriz de antecedentes",
                    "21 trabajos · 9 internacionales · 7 nacionales · 5 locales", ancho=6)
    f = escribir_tabla(ws, f,
                       ["Nivel", "Autor y año", "Título", "Metodología",
                        "Resultados principales", "Aporte o vacío que deja"],
                       ANTECEDENTES, [14, 28, 38, 44, 50, 50])
    nota(ws, f,
         "La capa local es en su mayoría agronómica y climatológica, no económica: fija el "
         "mecanismo físico que la tesis supone y debe presentarse como tal.", ancho=6)

    # ---------------------------------------------------------- Marco teórico
    ws = wb.create_sheet("Marco_teórico")
    f = titulo_hoja(ws, "Matriz del marco teórico",
                    "6 pilares · la cadena océano → clima local → oferta → precio regional → "
                    "IPC urbano", ancho=6)
    f = escribir_tabla(ws, f,
                       ["Pilar", "Teoría o enfoque", "Autores principales",
                        "Postulado central", "Predicción contrastable",
                        "Hipótesis que sustenta"],
                       MARCO, [8, 30, 42, 62, 36, 26])
    nota(ws, f,
         "Un pilar que no genere una predicción contrastable con los datos disponibles no "
         "entra en la matriz: sería ornamento y no fundamento. La formalización del modelo "
         "está en docs/tesis/MODELO_ECONOMICO.md.", ancho=6)

    # ---------------------------------------------------------- Metodología
    ws = wb.create_sheet("Metodología")
    f = titulo_hoja(ws, "Metodología y procesamiento de datos",
                    "El tratamiento estadístico no forma parte de la matriz de consistencia: "
                    "su lugar es este acápite", ancho=3)
    f = escribir_tabla(ws, f, ["Bloque", "Aspecto", "Definición"],
                       METODOLOGIA, [24, 26, 100])

    # ---------------------------------------------------------- Estado fuentes
    ws = wb.create_sheet("Estado_fuentes")
    f = titulo_hoja(ws, "Estado de verificación de las fuentes",
                    "Regla: un indicador cuya fuente no se confirme se elimina de la matriz "
                    "antes de estimar; no se sustituye en silencio", ancho=5)

    def color_est(i, j, v):
        return ESTADOS_COLOR.get(v) if j == 4 else None

    f = escribir_tabla(ws, f,
                       ["Indicadores", "Qué mide", "Fuente", "Estado", "Qué falta"],
                       ESTADO_FUENTES, [14, 38, 26, 24, 70], colorear=color_est)
    nota(ws, f,
         "Verificación ejecutable: en el repositorio, pestaña Actions, workflow «Verificar "
         "fuentes de la tesis». El runner de GitHub sí alcanza Open-Meteo, la NOAA, el BCRP y "
         "el INEI. También: python scripts/tesis/verificar_fuentes.py", ancho=5)

    # ---------------------------------------------------------- Cronograma
    ws = wb.create_sheet("Cronograma")
    f = titulo_hoja(ws, "Cronograma", "Doce semanas, más dos tareas previas que condicionan "
                                      "todo lo demás", ancho=4)
    f = escribir_tabla(ws, f, ["Semana", "Actividad", "Entregable", "Observación"],
                       CRONOGRAMA, [10, 62, 34, 40])

    # ---------------------------------------------------------- Revisión sistemática
    ws = wb.create_sheet("Rev_sistemática")
    f = titulo_hoja(ws, "Propuesta de revisión sistemática",
                    "PRISMA 2020 y guías de MAER-Net; el protocolo completo está en "
                    "docs/tesis/REVISION_SISTEMATICA.md", ancho=2)
    f = escribir_tabla(ws, f, ["Aspecto", "Definición"],
                       REV_SISTEMATICA, [34, 110])

    # ---------------------------------------------------------- Referencias
    ws = wb.create_sheet("Referencias")
    f = titulo_hoja(ws, "Referencias", f"{len(REFERENCIAS)} entradas reunidas en el avance",
                    ancho=2)
    filas_ref = [[i, r] for i, r in enumerate(sorted(REFERENCIAS), start=1)]
    escribir_tabla(ws, f, ["N°", "Referencia"], filas_ref, [6, 130])

    salida = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs", "tesis", "Tesis_matrices.xlsx")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    wb.save(salida)
    print(f"{len(wb.sheetnames)} hojas -> {salida}")
    for s in wb.sheetnames:
        print(f"  · {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
