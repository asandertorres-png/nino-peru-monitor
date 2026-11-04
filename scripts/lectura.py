"""Lectura automatica del estado del ENSO y del monitor.

Genera, con reglas fijas y umbrales declarados, un texto en espanol que
interpreta los indices publicados: ONI (Nino 3.4, NOAA), anomalia semanal de
TSM por region Nino, ICEN (Nino 1+2, ENFEN/IGP), el mapa del monitor y, si
existe, la sensibilidad al ENSO estimada para el mes en curso.

La misma entrada produce siempre el mismo texto. Describe lo observado y la
climatologia conocida del ENSO; no es un pronostico ni reemplaza los
comunicados del ENFEN. Los umbrales son provisionales y estan abajo, juntos,
para que puedan discutirse y cambiarse en un solo lugar.

Uso directo (imprime la lectura con los datos ya publicados):
    PYTHONPATH=scripts python3 scripts/lectura.py [--nivel departamento|provincia]
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import median

RAIZ = Path(__file__).resolve().parent.parent

# ---- umbrales de las reglas (provisionales) ----------------------------------
TENDENCIA = 0.3          # cambio del indice en tres pasos (meses) para hablar de ascenso o descenso
SEMANAL_VS_MEDIA = 0.5   # anomalia semanal menos media movil: "sigue creciendo" / "empieza a ceder"
MUY_POR_ENCIMA = 1.0     # idem, para "muy por encima" / "muy por debajo"
GRADIENTE = 1.0          # maximo - minimo entre regiones para hablar de patron oriental o central
ONI_CALIDO, ONI_FRIO = 0.5, -0.5       # NOAA
ICEN_CALIDO, ICEN_FRIO = 0.4, -1.0     # ENFEN: calida debil / fria debil
RACHA_EPISODIO = 5       # trimestres moviles seguidos que exige la NOAA para hablar de episodio
EXCESO_PCT, DEFICIT_PCT = 50, -30      # mismos cortes que el mapa
ALERTA_MINIMA = 2        # alerta moderada o alta
ALFA = 0.05              # sensibilidad: p orientativo
VERSION = "reglas fijas v1 (scripts/lectura.py)"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
TRIMESTRES = {"DJF": "diciembre–febrero", "JFM": "enero–marzo", "FMA": "febrero–abril",
              "MAM": "marzo–mayo", "AMJ": "abril–junio", "MJJ": "mayo–julio", "JJA": "junio–agosto",
              "JAS": "julio–septiembre", "ASO": "agosto–octubre", "SON": "septiembre–noviembre",
              "OND": "octubre–diciembre", "NDJ": "noviembre–enero"}
REGIONES = {"nino4": "Niño 4", "nino34": "Niño 3.4", "nino3": "Niño 3", "nino12": "Niño 1+2"}
TITULO_COSTA = {"cálida extraordinaria": "Niño costero extraordinario", "cálida fuerte": "Niño costero fuerte",
                "cálida moderada": "Niño costero moderado", "cálida débil": "Niño costero débil",
                "neutro": "costa en condición neutra", "fría débil": "Niña costera débil",
                "fría moderada": "Niña costera moderada", "fría fuerte": "Niña costera fuerte"}
ZONAS = {"costa_norte": "costa norte", "costa_centro_sur": "costa centro-sur", "sierra_norte": "sierra norte",
         "sierra_sur": "sierra sur", "selva": "selva"}


# ---- utilidades --------------------------------------------------------------
def num(v, dec=1, signo=True, unidad=""):
    s = f"{v:+.{dec}f}" if signo else f"{v:.{dec}f}"
    s = s.replace("-", "−").replace(".", ",")
    return s + unidad


def fecha_larga(iso):
    try:
        d = datetime.strptime(iso[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return iso or "fecha desconocida"
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def con_enie(s):
    return (s or "").replace("Nino", "Niño").replace("Nina", "Niña").replace("calida", "cálida") \
        .replace("fria", "fría").replace("debil", "débil")


def lista(nombres):
    nombres = list(nombres)
    if not nombres:
        return ""
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


def tendencia(valores, pasos=3, umbral=TENDENCIA):
    """Compara el ultimo valor con el de `pasos` atras. Devuelve (etiqueta, diferencia)."""
    valores = [v for v in valores if v is not None]
    if len(valores) <= pasos:
        return None, None
    d = valores[-1] - valores[-1 - pasos]
    if d >= umbral:
        return "en ascenso", d
    if d <= -umbral:
        return "en descenso", d
    return "estable", d


def fase(v, calido, frio):
    if v is None:
        return None
    return "calido" if v >= calido else "frio" if v <= frio else "neutro"


def racha(valores, umbral=ONI_CALIDO):
    """Trimestres seguidos, contando desde el ultimo, del mismo lado del umbral que el ultimo."""
    if not valores or valores[-1] is None:
        return 0
    signo = 1 if valores[-1] >= umbral else -1 if valores[-1] <= -umbral else 0
    if signo == 0:
        return 0
    n = 0
    for v in reversed(valores):
        if v is None or signo * v < umbral:
            break
        n += 1
    return n


def meses_entre(anio, mes, hoy):
    return (hoy.year - anio) * 12 + (hoy.month - mes)


def comparar(semanal, media):
    """Lectura de la anomalia semanal frente a la media movil (misma region)."""
    d = semanal - media
    if d >= MUY_POR_ENCIMA:
        return "muy por encima", d
    if d >= SEMANAL_VS_MEDIA:
        return "por encima", d
    if d <= -MUY_POR_ENCIMA:
        return "muy por debajo", d
    if d <= -SEMANAL_VS_MEDIA:
        return "por debajo", d
    return "en línea", d


def respecto(etiqueta):
    return "en línea con el" if etiqueta == "en línea" else f"{etiqueta} del"


def unidades_txt(n, nivel):
    base = "departamento" if nivel == "departamento" else "provincia"
    return f"{n} {base}{'' if n == 1 else 's'}"


# ---- parrafos ----------------------------------------------------------------
def parrafo_central(oni_doc):
    u = oni_doc["ultimo"]
    serie = [x.get("oni") for x in oni_doc.get("serie", [])]
    v = u["oni"]
    estado = con_enie(u.get("estado"))
    tend, d = tendencia(serie)
    n_racha = racha(serie)
    f = fase(v, ONI_CALIDO, ONI_FRIO)

    tri = TRIMESTRES.get(u["trimestre"], u["trimestre"])
    s = f"Pacífico central: el ONI de {tri} de {u['anio']} es {num(v, 2)}, "
    s += ("dentro del rango neutro (entre −0,5 y +0,5)" if f == "neutro"
          else f"nivel de {estado} en la escala del monitor (umbrales de la NOAA/CPC)")
    if tend:
        s += f", {tend} ({num(d, 2)} en tres meses)"
    if f != "neutro" and n_racha:
        lado = "por encima de +0,5" if f == "calido" else "por debajo de −0,5"
        if n_racha >= RACHA_EPISODIO:
            s += f"; lleva {n_racha} trimestres seguidos {lado} y cumple así el criterio de episodio de la NOAA"
        else:
            pl = "s" if n_racha > 1 else ""
            s += f"; lleva {n_racha} trimestre{pl} seguido{pl} {lado} y el criterio de episodio de la NOAA exige cinco"
    s += "."

    sem = oni_doc.get("semanal") or {}
    a34 = (sem.get("regiones") or {}).get("nino34", {}).get("anomalia", sem.get("anomalia"))
    comp = None
    if a34 is not None:
        etiqueta, _ = comparar(a34, v)
        comp = etiqueta
        s += (f" La anomalía semanal en Niño 3.4 ({num(a34, 1, unidad=' °C')}, semana centrada el "
              f"{fecha_larga(sem.get('semana_centrada'))}) está {respecto(etiqueta)} promedio trimestral")
        if etiqueta in ("por encima", "muy por encima"):
            s += ": el calentamiento no muestra señales de ceder." if v > 0 else ": el enfriamiento está cediendo."
        elif etiqueta in ("por debajo", "muy por debajo"):
            s += ": el evento cálido empieza a ceder." if v > 0 else ": el enfriamiento sigue profundizándose."
        else:
            s += "."
    return s, {"oni": v, "oni_estado": estado, "oni_fase": f, "oni_tendencia": tend, "oni_racha": n_racha,
               "semanal_34": a34, "semanal_34_vs_oni": comp}


def parrafo_costa(oni_doc, hoy):
    ic = oni_doc.get("icen")
    sem = oni_doc.get("semanal") or {}
    a12 = (sem.get("regiones") or {}).get("nino12", {}).get("anomalia")
    claves = {"icen": None, "icen_categoria": None, "costa_fase": None, "icen_tendencia": None,
              "semanal_12": a12, "costa_fuente": None}

    if ic and ic.get("icen") is not None:
        v = ic["icen"]
        cat = con_enie(ic.get("categoria"))
        cat_txt = "neutra" if cat == "neutro" else cat
        serie = [x.get("icen") for x in ic.get("serie", [])]
        tend, d = tendencia(serie)
        f = fase(v, ICEN_CALIDO, ICEN_FRIO)
        rezago = meses_entre(ic["anio"], ic["mes"], hoy)
        s = (f"Costa peruana: el ICEN con mes central {MESES[ic['mes'] - 1]} de {ic['anio']} es "
             f"{num(v, 2, unidad=' °C')}, condición {cat_txt} según las categorías del ENFEN")
        if tend:
            s += f", {tend} ({num(d, 2)} en tres meses)"
        s += "."
        if a12 is not None:
            etiqueta, _ = comparar(a12, v)
            if rezago >= 2:
                s += (f" El ICEN llega con {rezago} meses de rezago; la señal más reciente de la costa es la "
                      f"anomalía semanal en Niño 1+2, {num(a12, 1, unidad=' °C')}, {respecto(etiqueta)} ICEN")
            else:
                s += f" La anomalía semanal en Niño 1+2 ({num(a12, 1, unidad=' °C')}) está {respecto(etiqueta)} ICEN"
            if etiqueta in ("por encima", "muy por encima"):
                s += ": el calentamiento costero seguía creciendo." if a12 > 0 else ": el enfriamiento costero cede."
            elif etiqueta in ("por debajo", "muy por debajo"):
                s += ": el calentamiento costero estaría cediendo." if v > 0 else ": el enfriamiento costero se profundiza."
            else:
                s += "."
        claves.update({"icen": v, "icen_categoria": cat, "costa_fase": f, "icen_tendencia": tend,
                       "costa_fuente": "icen"})
        return s, claves

    if a12 is not None:
        f = fase(a12, ICEN_CALIDO, ICEN_FRIO)
        s = (f"Costa peruana: el ICEN del ENFEN no estuvo accesible en esta corrida. La anomalía semanal en "
             f"Niño 1+2 es {num(a12, 1, unidad=' °C')} (semana centrada el {fecha_larga(sem.get('semana_centrada'))}); "
             f"aplicada de forma orientativa a los umbrales del ENFEN, apunta a condición "
             f"{con_enie(_categoria_icen(a12))}, pero el ICEN oficial es una media de tres meses y puede diferir.")
        claves.update({"costa_fase": f, "costa_fuente": "semanal"})
        return s, claves

    return ("Costa peruana: ni el ICEN ni la anomalía semanal en Niño 1+2 estuvieron disponibles en esta corrida; "
            "la lectura de la costa queda pendiente."), claves


def _categoria_icen(v):
    from config import clasificar_icen
    return clasificar_icen(v)


def parrafo_configuracion(claves, oni_doc):
    c, k = claves.get("oni_fase"), claves.get("costa_fase")
    if c is None or k is None:
        return None, None
    combo = {
        ("calido", "calido"): ("Las dos cuencas están en fase cálida a la vez: El Niño del Pacífico central con expresión "
                               "costera, como en 1982-83 y 1997-98.", "nino_global_y_costero"),
        ("neutro", "calido"): ("Fase cálida solo frente a la costa: un Niño costero sin El Niño del Pacífico central, "
                               "como el de 2017.", "nino_costero"),
        ("frio", "calido"): ("Fase cálida frente a la costa con La Niña en el Pacífico central: una configuración poco "
                             "frecuente que el ENFEN sigue como Niño costero.", "nino_costero_con_nina"),
        ("calido", "neutro"): ("Fase cálida solo en el Pacífico central, sin expresión costera por ahora: el impacto "
                               "esperable en el Perú pasa más por la sierra que por la costa norte.", "nino_central"),
        ("calido", "frio"): ("El Niño en el Pacífico central con costa fría: configuración contrapuesta, sin "
                             "expresión costera.", "nino_central_costa_fria"),
        ("frio", "frio"): ("Las dos cuencas están en fase fría: La Niña del Pacífico central con costa fría.",
                           "nina_global_y_costera"),
        ("frio", "neutro"): ("La Niña en el Pacífico central con la costa cerca de lo normal.", "nina_central"),
        ("neutro", "frio"): ("Costa fría con el Pacífico central neutro: una Niña costera.", "nina_costera"),
        ("neutro", "neutro"): ("Condiciones neutras en las dos cuencas.", "neutro"),
    }
    texto, config = combo[(c, k)]

    reg = ((oni_doc.get("semanal") or {}).get("regiones") or {})
    vals = {r: reg[r]["anomalia"] for r in REGIONES if reg.get(r, {}).get("anomalia") is not None}
    patron = None
    if len(vals) == 4:
        r_max = max(vals, key=lambda r: abs(vals[r]))
        amplitud = max(vals.values()) - min(vals.values())
        calor = vals[r_max] > 0
        palabra = "calentamiento" if calor else "enfriamiento"
        if max(abs(x) for x in vals.values()) < ONI_CALIDO:
            texto += " Las cuatro regiones Niño están cerca de lo normal esta semana."
            patron = "normal"
        elif amplitud < GRADIENTE:
            texto += f" Entre las cuatro regiones el {palabra} es parejo a lo largo del Pacífico ecuatorial."
            patron = "parejo"
        elif r_max in ("nino12", "nino3"):
            texto += (f" Entre las cuatro regiones la anomalía es mayor junto a la costa sudamericana "
                      f"({REGIONES[r_max]}, {num(vals[r_max], 1, unidad=' °C')}) y disminuye hacia el oeste "
                      f"(Niño 4, {num(vals['nino4'], 1, unidad=' °C')}): el patrón de un evento de tipo oriental, "
                      f"el que históricamente ha tenido mayor impacto en la costa norte del Perú.")
            patron = "oriental"
        else:
            texto += (f" Entre las cuatro regiones la anomalía es mayor en el Pacífico central "
                      f"({REGIONES[r_max]}, {num(vals[r_max], 1, unidad=' °C')}) que frente a la costa "
                      f"(Niño 1+2, {num(vals['nino12'], 1, unidad=' °C')}): el patrón de un evento de tipo central, "
                      f"con menor expresión costera.")
            patron = "central"
    return texto, {"configuracion": config, "patron": patron}


def parrafo_estacion(hoy, claves):
    m = hoy.month
    hay_evento = "neutro" not in (claves.get("oni_fase"), claves.get("costa_fase")) and \
        (claves.get("oni_fase") or claves.get("costa_fase"))
    calido = "calido" in (claves.get("oni_fase"), claves.get("costa_fase"))
    if m in (9, 10, 11, 12):
        s = (f"En {MESES[m - 1]} los episodios del Pacífico central suelen acercarse a su máximo, que ocurre entre "
             f"noviembre y enero, y el efecto sobre la lluvia de la costa norte se concentra entre enero y abril")
        s += ": el periodo de mayor riesgo está por delante." if calido else "."
        return s, "desarrollo"
    if m in (1, 2, 3, 4):
        s = (f"{MESES[m - 1].capitalize()} está dentro del periodo (enero–abril) en que un Niño costero descarga "
             f"sus lluvias sobre la costa norte")
        s += ", de modo que lo que muestra el mapa es el impacto en curso." if calido else \
            "; con la costa fuera de fase cálida, ese riesgo es bajo esta temporada."
        return s, "impacto"
    s = (f"Después de abril la costa norte entra a su estación seca; un cambio en los índices en {MESES[m - 1]} "
         f"anticipa, más que impacta, y es lo que el ENFEN vigila para el verano siguiente.")
    return s, "transicion"


def parrafo_mapa(registros, nivel):
    regs = [r for r in registros if not r.get("sin_datos")]
    if not regs:
        return None, {}
    total = len(registros)
    plural = "departamentos" if nivel == "departamento" else "provincias"
    con_alerta = [r for r in regs if r.get("nivel_alerta") is not None]
    n_alerta = sum(1 for r in con_alerta if r["nivel_alerta"] >= ALERTA_MINIMA)
    s = f"En el mapa, {n_alerta} de {unidades_txt(total, nivel)} {'están' if total > 1 else 'está'} en alerta moderada o alta"
    if len(con_alerta) < total:
        s += f" ({total - len(con_alerta)} sin alerta calculada)"
    s += "."

    con_pct = [r for r in regs if r.get("anomalia_precipitacion_pct") is not None and not r.get("normal_baja")]
    exceso = sorted((r for r in con_pct if r["anomalia_precipitacion_pct"] >= EXCESO_PCT),
                    key=lambda r: -r["anomalia_precipitacion_pct"])
    deficit = sorted((r for r in con_pct if r["anomalia_precipitacion_pct"] <= DEFICIT_PCT),
                     key=lambda r: r["anomalia_precipitacion_pct"])
    otros = "entre otros" if nivel == "departamento" else "entre otras"
    nombrar = lambda rs: ", ".join(f"{r['nombre']} {num(r['anomalia_precipitacion_pct'], 0, unidad=' %')}" for r in rs[:3]) \
        + (f", {otros}" if len(rs) > 3 else "")
    partes = []
    if exceso:
        partes.append(f"supera en más de {EXCESO_PCT} % su normal en {len(exceso)} ({nombrar(exceso)})")
    if deficit:
        partes.append(f"queda más de {abs(DEFICIT_PCT)} % por debajo en {len(deficit)} ({nombrar(deficit)})")
    if partes:
        s += " La lluvia de los últimos 30 días " + " y ".join(partes) + "."
    elif con_pct:
        s += f" Ninguna unidad supera los cortes de exceso ({EXCESO_PCT:+d} %) ni de déficit ({DEFICIT_PCT:+d} %) de lluvia."

    tx = [r["anomalia_tmax_c"] for r in regs if r.get("anomalia_tmax_c") is not None]
    if tx:
        n_calidas = sum(1 for v in tx if v > 0)
        med = median(tx)
        if len(tx) == 1:
            donde = "en la única unidad con dato" if n_calidas else "en ninguna unidad con dato"
        elif n_calidas == len(tx):
            donde = f"en {'los' if nivel == 'departamento' else 'las'} {len(tx)} {plural}"
        else:
            donde = f"en {n_calidas} de {len(tx)} {plural}"
        s += f" La temperatura máxima de 30 días está por encima de su normal {donde} (mediana {num(med, 1, unidad=' °C')})."
    return s, {"alerta_moderada_o_alta": n_alerta, "exceso": [r["nombre"] for r in exceso],
               "deficit": [r["nombre"] for r in deficit], "mediana_anomalia_tmax_c": round(median(tx), 2) if tx else None}


def parrafo_sensibilidad(sens, hoy, nivel, registros):
    if not sens or not sens.get("unidades"):
        return None
    mm = f"{hoy.month:02d}"
    nombre_de = {}
    for r in registros:
        nombre_de[r.get("ubigeo") or r.get("nombre")] = r.get("nombre")
        nombre_de[r.get("nombre")] = r.get("nombre")
    neg, pos = [], []
    for k, meses in sens["unidades"].items():
        m = meses.get(mm) or {}
        if m.get("p") is None or m["p"] >= ALFA:
            continue
        (neg if m["r"] < 0 else pos).append((abs(m["r"]), nombre_de.get(k, k)))
    if not neg and not pos:
        return (f"La sensibilidad estimada en este monitor (1991–2020) no encuentra, para {MESES[hoy.month - 1]}, "
                f"una asociación significativa entre el ONI y la lluvia en ninguna unidad.")
    s = (f"Según la sensibilidad estimada en este monitor (1991–2020), en {MESES[hoy.month - 1]} la lluvia de "
         f"{unidades_txt(len(neg) + len(pos), nivel)} se asocia de forma significativa con el ONI (p < {str(ALFA).replace('.', ',')}):")
    partes = []
    if neg:
        top = [n for _, n in sorted(neg, reverse=True)[:4]]
        partes.append(f" menos lluvia con El Niño en {lista(top)}{', entre otras' if len(neg) > 4 else ''}")
    if pos:
        top = [n for _, n in sorted(pos, reverse=True)[:4]]
        partes.append(f" más lluvia en {lista(top)}{', entre otras' if len(pos) > 4 else ''}")
    return s + ";".join(partes) + ". Es asociación histórica, no causalidad, y con pocos eventos detrás."


def millones(v):
    if v is None:
        return "s/d"
    if abs(v) >= 1e9:
        return f"{v / 1e9:.2f}".replace(".", ",") + " mil millones"
    return f"{v / 1e6:,.0f}".replace(",", " ") + " millones"


def parrafo_gasto(gasto, registros, nivel, hoy):
    """Gasto publico en el PP 0068 (MEF) leido junto con la exposicion al evento."""
    if not gasto or not gasto.get("departamentos"):
        return None, None
    t = gasto.get("total") or {}
    if t.get("pim") is None or t.get("devengado") is None:
        return None, None
    deps = gasto["departamentos"]
    corte = gasto.get("mes_corte")
    s = (f"Gasto público: el Programa Presupuestal 0068 (reducción de vulnerabilidad y atención de emergencias por "
         f"desastres, todos los peligros) tiene en {gasto.get('anio')} un PIM de S/ {millones(t['pim'])}, con "
         f"S/ {millones(t['devengado'])} devengados ({num(t['avance_pct'], 1, signo=False)} %)")
    if corte:
        s += f" al cierre de {MESES[int(corte) - 1]}"
    por_mes = gasto.get("por_mes") or {}
    if corte and f"{int(corte):02d}" in por_mes:
        s += f"; en {MESES[int(corte) - 1]} se devengaron S/ {millones(por_mes[f'{int(corte):02d}'].get('devengado'))}"
    s += "."
    claves = {"avance_nacional_pct": t.get("avance_pct"), "devengado_per_capita_nacional": t.get("devengado_per_capita")}

    # costa norte: la zona mas expuesta a lluvias en fase calida
    zona_de = {r["nombre"]: r.get("zona") for r in registros} if nivel == "departamento" else {}
    costa = [(n, deps[n]) for n, z in zona_de.items() if z == "costa_norte" and deps.get(n) and not deps[n].get("sin_datos")]
    if costa:
        costa.sort(key=lambda x: (x[1].get("avance_pct") if x[1].get("avance_pct") is not None else -1))
        detalle = ", ".join(f"{n} {num(d['avance_pct'], 0, signo=False)} %" for n, d in costa if d.get("avance_pct") is not None)
        pc = [d.get("devengado_per_capita") for _, d in costa if d.get("devengado_per_capita") is not None]
        s += (f" En la costa norte, la zona más expuesta a lluvias con Niño costero, el avance es {detalle}, frente a "
              f"{num(t['avance_pct'], 0, signo=False)} % nacional")
        if pc and t.get("devengado_per_capita") is not None:
            s += (f"; el devengado por habitante va de S/ {num(min(pc), 0, signo=False)} a S/ {num(max(pc), 0, signo=False)}, "
                  f"frente a S/ {num(t['devengado_per_capita'], 0, signo=False)} nacional")
        s += "."
        claves["costa_norte"] = {n: d.get("avance_pct") for n, d in costa}

    # unidades en alerta que ejecutan por debajo del promedio nacional
    if nivel == "departamento" and t.get("avance_pct") is not None:
        en_alerta = [r["nombre"] for r in registros if (r.get("nivel_alerta") or 0) >= ALERTA_MINIMA]
        rezagados = sorted((deps[n]["avance_pct"], n) for n in en_alerta
                           if deps.get(n) and deps[n].get("avance_pct") is not None and deps[n]["avance_pct"] < t["avance_pct"])
        if en_alerta:
            if rezagados:
                top = [f"{n} ({num(a, 0, signo=False)} %)" for a, n in rezagados[:3]]
                s += (f" De los {len(en_alerta)} departamentos en alerta moderada o alta, {len(rezagados)} ejecutan por debajo "
                      f"del promedio nacional: {lista(top)}{', entre otros' if len(rezagados) > 3 else ''}.")
            else:
                s += f" Los {len(en_alerta)} departamentos en alerta moderada o alta ejecutan al nivel del promedio nacional o por encima."
            claves["en_alerta_rezagados"] = [n for _, n in rezagados]
    s += " Es una capa de insumo (presupuesto y devengado), no de resultado, y el programa no distingue el gasto por El Niño."
    return s, claves


def titulo(claves):
    partes = []
    if claves.get("oni_fase") == "neutro":
        partes.append("Pacífico central neutro")
    elif claves.get("oni_estado"):
        partes.append(f"{claves['oni_estado']} en el Pacífico central")
    cat = claves.get("icen_categoria")
    if cat:
        partes.append(TITULO_COSTA.get(cat, f"costa en condición {cat}"))
    elif claves.get("costa_fase"):
        partes.append({"calido": "costa en fase cálida", "frio": "costa en fase fría",
                       "neutro": "costa en condición neutra"}[claves["costa_fase"]] + " (señal semanal)")
    t = " y ".join(partes) if partes else "Estado del ENSO"
    to, ti = claves.get("oni_tendencia"), claves.get("icen_tendencia")
    if to and ti and to == ti and to != "estable":
        t += f", los dos índices {to}"
    elif to and to != "estable":
        t += f", ONI {to}"
    return t[0].upper() + t[1:]


# ---- entrada principal -------------------------------------------------------
def lectura_automatica(oni_doc, registros=(), nivel="departamento", hoy=None, sensibilidad=None, gasto=None):
    """Devuelve {"titulo", "parrafos", "nota", "claves", "generada", "metodo"} o lanza si falta el ONI."""
    hoy = hoy or datetime.now()
    claves = {}
    parrafos = []

    s, k = parrafo_central(oni_doc)
    parrafos.append(s); claves.update(k)
    s, k = parrafo_costa(oni_doc, hoy)
    parrafos.append(s); claves.update(k)
    s, k = parrafo_configuracion(claves, oni_doc)
    if s:
        parrafos.append(s); claves.update(k)
    s, k = parrafo_estacion(hoy, claves)
    parrafos.append(s); claves["fase_estacional"] = k
    s, k = parrafo_mapa(registros, nivel)
    if s:
        parrafos.append(s); claves["mapa"] = k
    s = parrafo_sensibilidad(sensibilidad, hoy, nivel, registros)
    if s:
        parrafos.append(s)
    s, k = parrafo_gasto(gasto, registros, nivel, hoy)
    if s:
        parrafos.append(s); claves["gasto"] = k

    return {
        "titulo": titulo(claves),
        "parrafos": parrafos,
        "nota": ("Lectura generada automáticamente con reglas fijas a partir de los índices publicados; describe lo "
                 "observado y la climatología conocida del ENSO. No es un pronóstico ni reemplaza los comunicados "
                 "oficiales del ENFEN."),
        "claves": claves,
        "generada": hoy.isoformat(timespec="minutes"),
        "metodo": VERSION,
    }


def cargar_gasto():
    ruta = RAIZ / "data" / "gasto_pp0068.json"
    if ruta.exists():
        try:
            return json.loads(ruta.read_text())
        except ValueError:
            return None
    return None


def cargar_sensibilidad(nivel):
    from niveles import rutas
    ruta = rutas(nivel)["sensibilidad"]
    if ruta.exists():
        try:
            return json.loads(ruta.read_text())
        except ValueError:
            return None
    return None


def main():
    from niveles import nivel_desde_argv, rutas
    nivel = nivel_desde_argv()
    oni_doc = json.loads((RAIZ / "data" / "oni.json").read_text())
    ruta_estado = rutas(nivel)["estado"]
    estado = json.loads(ruta_estado.read_text()) if ruta_estado.exists() else {}
    registros = estado.get("departamentos") or estado.get("provincias") or []
    hoy = datetime.fromisoformat(estado["actualizado"]) if estado.get("actualizado") else datetime.now()
    lec = lectura_automatica(oni_doc, registros, nivel, hoy, cargar_sensibilidad(nivel), cargar_gasto())
    print(lec["titulo"].upper())
    for p in lec["parrafos"]:
        print("\n" + p)
    print("\n[" + lec["nota"] + "]")
    print(json.dumps(lec["claves"], ensure_ascii=False))


if __name__ == "__main__":
    main()
