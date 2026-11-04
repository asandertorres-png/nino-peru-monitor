/* Monitor El Niño · Perú — logica del mapa.
   Colores de dato segun el metodo de visualizacion:
   - alerta: escala de estado fija (0 neutro, 1 warning, 2 serious, 3 critical), siempre con etiqueta;
   - anomalias: divergentes de dos tonos con punto medio neutro, pasos iguales por brazo, mas claros
     hacia afuera porque la superficie es oscura;
   - lluvia acumulada (zonas de normal muy baja): secuencial de un tono, oscuro -> claro.
   Las rampas se validaron por monotonia de luminosidad (OKLCH) antes de fijarlas. */

const NEUTRO = "#3f3f3b";
const SIN_DATOS = "#2b2e33";

const ESCALAS = {
  nivel_alerta: {
    titulo: "Nivel de alerta", nota: "Indicativo y provisional; no sustituye avisos oficiales.",
    tipo: "estado",
    clases: [
      { v: 0, color: NEUTRO,    op: 0.25, etq: "Sin señal" },
      { v: 1, color: "#fab219", op: 0.6, etq: "Leve" },
      { v: 2, color: "#ec835a", op: 0.62, etq: "Moderada" },
      { v: 3, color: "#d03b3b", op: 0.66, etq: "Alta" }
    ],
    formato: v => v == null ? "s/d" : ESCALAS.nivel_alerta.clases[v].etq
  },
  anomalia_precipitacion_pct: {
    titulo: "Anomalía de lluvia, 30 días", unidad: "%", tipo: "divergente",
    polos: ["déficit", "exceso"],
    cortes: [-60, -30, -10, 10, 30, 60],
    colores: ["#f8c3a8", "#f0906a", "#d95926", NEUTRO, "#3987e5", "#86b6ef", "#cde2fb"],
    formato: v => v == null ? "s/d" : `${v > 0 ? "+" : ""}${v} %`
  },
  precipitacion_mm: {
    titulo: "Lluvia acumulada, 30 días", unidad: "mm", tipo: "secuencial",
    cortes: [1, 5, 20, 50],
    colores: ["#184f95", "#256abf", "#3987e5", "#86b6ef", "#cde2fb"],
    formato: v => v == null ? "s/d" : `${v} mm`
  },
  anomalia_tmax_c: {
    titulo: "Anomalía de temperatura máxima, 30 días", unidad: "°C", tipo: "divergente",
    polos: ["más frío", "más cálido"],
    cortes: [-2, -1, -0.5, 0.5, 1, 2],
    colores: ["#cde2fb", "#86b6ef", "#3987e5", NEUTRO, "#e66767", "#f29a9a", "#f9cccc"],
    formato: v => v == null ? "s/d" : `${v > 0 ? "+" : ""}${v} °C`
  }
};

function claseEscalonada(v, escala) {
  let i = 0;
  while (i < escala.cortes.length && v >= escala.cortes[i]) i++;
  return i;
}

const normaliza = s => (s || "").toUpperCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
const fmtFecha = s => s ? new Date(conZona(s)).toLocaleString("es-PE", { dateStyle: "medium", timeStyle: "short" }) : "s/d";
const fmtDia = s => s ? new Date(s + "T12:00:00-05:00").toLocaleDateString("es-PE", { dateStyle: "medium" }) : "s/d";
// las horas del JSON vienen en hora de Lima sin zona; se la agregamos para no depender del navegador
const conZona = s => /[zZ]|[+-]\d\d:\d\d$/.test(s) ? s : (s.length === 10 ? s + "T23:59:00-05:00" : s + ":00-05:00").replace(/:00:00-05:00$/, ":00-05:00");

let capaActual = "nivel_alerta";
let nivelActual = "departamento";
let mesActual = new Date().getMonth() + 1;
let porUnidad = {};
let registros = [];
let umbralNormalBaja = null;
let capaGeo, capaSeleccion = null;
const geoCache = {};

// Estado de la vista en la URL (#nivel=…&capa=…&u=…): una vista concreta se puede
// citar o compartir. replaceState evita que el navegador salte al cambiar el hash.
function leerHash() {
  const p = new URLSearchParams(location.hash.slice(1));
  return { nivel: p.get("nivel"), capa: p.get("capa"), u: p.get("u") };
}
function escribirHash(u) {
  const p = new URLSearchParams();
  p.set("nivel", nivelActual); p.set("capa", capaActual);
  if (u) p.set("u", u);
  history.replaceState(null, "", "#" + p.toString());
}
let seleccionPendiente = leerHash().u;
let claveSeleccion = null;
let actualizadoISO = "";

function seleccionar(layer, clave) {
  if (capaSeleccion && capaSeleccion !== layer) capaGeo.resetStyle(capaSeleccion);
  capaSeleccion = layer; claveSeleccion = clave;
  layer.setStyle({ weight: 2.5, color: "#f0efec" }); layer.bringToFront();
  mostrarDetalle(porUnidad[clave]);
  escribirHash(clave);
}

// Los tooltips son un recurso de hover: en pantallas tactiles quedan pegados tras tocar y
// repiten lo que el panel de detalle ya muestra, asi que solo se activan con puntero fino.
const CON_TOOLTIPS = matchMedia("(hover: hover) and (pointer: fine)").matches;

const NIVELES = {
  departamento: {
    estado: "data/estado.json", geo: "peru_departamentos.geojson", lista: "departamentos",
    claveGeo: f => normaliza(f.properties.NOMBDEP), claveDato: d => normaliza(d.nombre),
    etiqueta: f => f.properties.NOMBDEP
  },
  provincia: {
    estado: "data/estado_provincias.json", geo: "peru_provincias.geojson", lista: "provincias",
    claveGeo: f => f.properties.FIRST_IDPR, claveDato: d => d.ubigeo,
    etiqueta: f => `${f.properties.NOMBPROV} · ${f.properties.FIRST_NOMB}`
  }
};

/* ---------- mapa ---------- */
const mapa = L.map("mapa", { zoomControl: true, attributionControl: true, zoomSnap: 0.5 })
  .setView([-9.8, -75.2], 5);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 11, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(mapa);

// etiquetas de capitales (se ocultan si el zoom aleja demasiado)
const capasEtiquetas = L.layerGroup().addTo(mapa);
fetch("capitales.json").then(r => r.json()).then(caps => {
  caps.forEach(c => L.marker([c.lat, c.lon], {
    interactive: false, keyboard: false,
    icon: L.divIcon({ className: "", iconSize: [0, 0], html: `<span class="etq-capital p${c.prioridad || 1}${c.lon > -70.5 ? " izq" : ""}">${c.nombre}</span>` })
  }).addTo(capasEtiquetas));
}).catch(() => {});
// prioridad cartografica: con el zoom lejos solo quedan las capitales principales
const ajustarEtiquetas = () => {
  const z = mapa.getZoom(), cl = mapa.getContainer().classList;
  cl.toggle("ocultar-etq", z < 4.5); cl.toggle("zoom-lejos", z < 6);
};
mapa.on("zoomend", ajustarEtiquetas); ajustarEtiquetas();

// leyenda dentro del mapa
const leyenda = L.control({ position: "bottomleft" });
leyenda.onAdd = () => { const d = L.DomUtil.create("div", "leyenda"); L.DomEvent.disableClickPropagation(d); return d; };
leyenda.addTo(mapa);

/* ---------- color ---------- */
const sinInfo = d => !d || d.sin_datos || d.sin_normal;
function claseDe(d) {
  if (sinInfo(d)) return { color: SIN_DATOS, op: 0.55 };
  if (capaActual === "nivel_alerta") {
    const c = ESCALAS.nivel_alerta.clases[Math.max(0, Math.min(3, d.nivel_alerta ?? 0))];
    return { color: c.color, op: c.op };
  }
  if (capaActual === "anomalia_precipitacion_pct" && d.normal_baja) {
    const e = ESCALAS.precipitacion_mm, v = d.precipitacion_obs_mm;
    return v == null ? { color: SIN_DATOS, op: 0.5 } : { color: e.colores[claseEscalonada(v, e)], op: 0.62 };
  }
  const e = ESCALAS[capaActual], v = d[capaActual];
  if (v == null) return { color: SIN_DATOS, op: 0.55 };
  const i = claseEscalonada(v, e);
  return { color: e.colores[i], op: e.colores[i] === NEUTRO ? 0.25 : 0.62 };
}

function estilo(feature) {
  const d = porUnidad[NIVELES[nivelActual].claveGeo(feature)];
  const c = claseDe(d);
  if (sinInfo(d)) return { fillColor: "#5a5f66", fillOpacity: 0.5, color: "#898781", weight: 1, dashArray: "4 3" };
  // el trazo lleva el color del plano: separa los rellenos vecinos ahora que son translucidos
  return { fillColor: c.color, fillOpacity: c.op, color: "#0d0f12", weight: nivelActual === "provincia" ? 1 : 1.5 };
}

function valorCapa(d) {
  if (!d || d.sin_datos || d.sin_normal) return "sin información";
  if (capaActual === "anomalia_precipitacion_pct" && d.normal_baja) return `${d.precipitacion_obs_mm} mm (normal muy baja)`;
  return ESCALAS[capaActual].formato(d[capaActual]);
}

/* ---------- leyenda ---------- */
function dibujarLeyenda() {
  const e = ESCALAS[capaActual];
  const caja = leyenda.getContainer();
  let cuerpo = "";
  if (e.tipo === "estado") {
    cuerpo = `<div class="chips">` + e.clases.map(c =>
      `<div class="chip${c.color === NEUTRO ? " neutro" : ""}"><i style="background:${c.color}">${c.v}</i>${c.etq}</div>`).join("") + `</div>`;
  } else {
    cuerpo = franja(e);
  }
  if (capaActual === "anomalia_precipitacion_pct") {
    const m = ESCALAS.precipitacion_mm;
    cuerpo += `<div class="sub-ley"><h4>${m.titulo} (mm)</h4>${franja(m)}
      <p class="nota">Zonas con normal mensual menor a ${umbralNormalBaja ?? "—"} mm: ahí el porcentaje no informa y se pinta el acumulado.</p></div>`;
  }
  if (registros.some(sinInfo)) cuerpo += `<div class="chip" style="margin-top:.45rem"><i class="sin-info"></i>Sin información</div>`;
  const html = `<div class="ley-cuerpo"><h4>${e.titulo}${e.unidad ? ` (${e.unidad})` : ""}</h4>${cuerpo}${e.nota ? `<p class="nota">${e.nota}</p>` : ""}</div>`;
  caja.innerHTML = html;
  document.getElementById("leyenda-movil").innerHTML = html;
}

function franja(e) {
  const sw = e.colores.map(c => `<i style="background:${c}"></i>`).join("");
  // cada corte va sobre la frontera entre dos muestras
  const n = e.colores.length;
  const cortes = e.cortes.map((c, i) => `<span style="left:${((i + 1) / n * 100).toFixed(2)}%">${c}</span>`).join("");
  const polos = e.polos ? `<div class="polos"><span>← ${e.polos[0]}</span><span>${e.polos[1]} →</span></div>` : "";
  return `<div class="franja">${sw}</div><div class="cortes">${cortes}</div>${polos}`;
}

/* ---------- detalle ---------- */
function mostrarDetalle(d) {
  const caja = document.getElementById("detalle");
  if (!d) { caja.innerHTML = '<p class="vacio">Pasa el cursor o toca una unidad del mapa para ver su detalle.</p>'; return; }
  const f = (v, u, dec = 1) => v == null ? "s/d" : `${v.toFixed(dec)} ${u}`;
  const signo = (v, u, dec = 1) => v == null ? "s/d" : `${v > 0 ? "+" : ""}${v.toFixed(dec)} ${u}`;
  const sub = d.departamento ? `${d.departamento} · ${d.zona.replace(/_/g, " ")}` : `${d.capital} · ${d.zona.replace(/_/g, " ")}`;
  if (d.sin_datos || d.sin_normal) {
    caja.innerHTML = `<h2>${d.nombre}</h2><p class="sub">${sub}</p>
      <p class="nota"><strong>Sin información para esta unidad.</strong> ${d.motivo_sin_normal || d.motivo_sin_datos || ""}</p>
      ${d.temperatura_actual_c != null ? `<dl><dt>Temperatura actual</dt><dd>${f(d.temperatura_actual_c, "°C")}</dd></dl>` : ""}`;
    return;
  }
  const al = ESCALAS.nivel_alerta.clases[d.nivel_alerta ?? 0];
  const lluvia = d.normal_baja
    ? `<dt>Anomalía de lluvia</dt><dd>${signo(d.anomalia_precipitacion_mm, "mm")}</dd>`
    : `<dt>Anomalía de lluvia</dt><dd class="destacado">${ESCALAS.anomalia_precipitacion_pct.formato(d.anomalia_precipitacion_pct)}</dd>`;
  caja.innerHTML = `
    <h2>${d.nombre}</h2><p class="sub">${sub}</p>
    <dl>
      <dt>Nivel de alerta</dt><dd><span class="alerta"><i style="background:${al.color}"></i>${al.etq}</span></dd>
      <div class="sep"></div>
      ${d.lluvia_hoy_mm == null ? "" : `<dt>Lluvia de hoy, hasta la hora</dt><dd>${f(d.lluvia_hoy_mm, "mm")}</dd>
      <dt>Temperatura actual</dt><dd>${f(d.temperatura_actual_c, "°C")}</dd><div class="sep"></div>`}
      <dt>Lluvia, 30 días</dt><dd>${f(d.precipitacion_obs_mm, "mm")}</dd>
      <dt>Normal del mes</dt><dd>${f(d.precipitacion_normal_mm, "mm")}</dd>
      ${lluvia}
      <dt>T. máxima media, 30 días</dt><dd>${f(d.tmax_obs_c, "°C")}</dd>
      <dt>Anomalía térmica</dt><dd class="destacado">${ESCALAS.anomalia_tmax_c.formato(d.anomalia_tmax_c)}</dd>
      <dt>Pronóstico de lluvia, 7 días</dt><dd>${f(d.pronostico_7d_mm, "mm")}</dd>
      ${d.elevacion_modelo_m == null ? "" : `<div class="sep"></div><dt>Altitud del punto de malla</dt><dd>${Math.round(d.elevacion_modelo_m)} m</dd>`}
      ${d.altitud_capital_m == null ? "" : `<dt>Altitud de la capital (ref.)</dt><dd>${d.altitud_capital_m} m</dd>`}
    </dl>
    ${d.normal_baja ? `<p class="nota" style="margin:.5rem 0 0">Normal mensual menor a ${umbralNormalBaja ?? "—"} mm: el porcentaje exageraría cualquier lluvia; se muestra la diferencia en mm.</p>` : ""}
    <div id="detalle-analitica"></div>`;
  window.analitica?.detalle(d, nivelActual, nivelActual === "departamento" ? d.nombre : d.ubigeo, mesActual);
}

/* ---------- mapa de regiones Nino ---------- */
// Recuadros oficiales (NOAA). Longitudes en 0-360 para que el Pacifico no se parta
// en el antimeridiano: 160E = 160, 150W = 210, 90W = 270, 80W = 280.
const REGIONES_NINO = {
  nino4:  { nombre: "Niño 4",   bounds: [[-5, 160], [5, 210]] },
  nino34: { nombre: "Niño 3.4", bounds: [[-5, 190], [5, 240]] },
  nino3:  { nombre: "Niño 3",   bounds: [[-5, 210], [5, 270]] },
  nino12: { nombre: "Niño 1+2", bounds: [[-10, 270], [0, 280]] }
};
let mapaEnso = null;
const rectEnso = {};

function pintarEnso(estado) {
  const s = estado.tsm_semanal, reg = s && s.regiones;
  const nota = document.getElementById("enso-mapa-nota");
  if (!mapaEnso) {
    mapaEnso = L.map("mapa-enso", {
      zoomControl: false, dragging: false, scrollWheelZoom: false, doubleClickZoom: false,
      touchZoom: false, boxZoom: false, keyboard: false, attributionControl: false, zoomSnap: 0.25
    });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 4 }).addTo(mapaEnso);
    mapaEnso.fitBounds([[-24, 150], [20, 295]]);
    // contorno del Peru, desplazado 360 grados a esta copia del mundo
    (geoCache.departamento || (geoCache.departamento = fetch(NIVELES.departamento.geo).then(r => r.json())))
      .then(geo => L.geoJSON(geo, {
        coordsToLatLng: p => L.latLng(p[1], p[0] + 360),
        style: { color: "#f0efec", weight: 1, fillColor: "#f0efec", fillOpacity: 0.12 }, interactive: false
      }).addTo(mapaEnso)).catch(() => {});
    for (const [k, r] of Object.entries(REGIONES_NINO)) {
      rectEnso[k] = L.rectangle(r.bounds, { color: "#f0efec", weight: 1, fillColor: NEUTRO, fillOpacity: 0.3, interactive: false }).addTo(mapaEnso);
    }
  }
  const e = ESCALAS.anomalia_tmax_c;
  const fichas = [];
  for (const [k, r] of Object.entries(REGIONES_NINO)) {
    const v = reg?.[k]?.anomalia;
    const color = v == null ? NEUTRO : e.colores[claseEscalonada(v, e)];
    rectEnso[k].setStyle(v == null ? { fillColor: NEUTRO, fillOpacity: 0.3 } : { fillColor: color, fillOpacity: 0.85 });
    fichas.push(`<div class="ficha${k === "nino12" ? " costera" : ""}"><i style="background:${color}"></i>
      <span class="reg">${r.nombre}</span><span class="val">${v == null ? "s/d" : (v > 0 ? "+" : "") + v.toFixed(1) + " °C"}</span></div>`);
  }
  document.getElementById("enso-chips").innerHTML = fichas.join("");
  nota.textContent = reg
    ? `Anomalía semanal de la temperatura del mar por región Niño (°C), semana centrada en ${fmtDia(s.semana_centrada)}. Niño 1+2, frente a la costa, es la región del Niño costero; Niño 3.4 es la del ONI.`
    : "El detalle por región Niño aparece con la próxima actualización del monitor.";
}

/* ---------- cabecera ENSO y frescura ---------- */
const CENTRO_TRIMESTRE = { DJF: 1, JFM: 2, FMA: 3, MAM: 4, AMJ: 5, MJJ: 6, JJA: 7, JAS: 8, ASO: 9, SON: 10, OND: 11, NDJ: 12 };

function pintarCabecera(estado) {
  const o = estado.oni;
  document.getElementById("oni-valor").textContent = (o.oni > 0 ? "+" : "") + o.oni.toFixed(2);
  document.getElementById("oni-estado").textContent = (o.estado || "").replace("Nino", "Niño").replace("Nina", "Niña");
  document.getElementById("oni-trimestre").textContent = `${o.trimestre} ${o.anio} · media móvil de 3 meses`;
  const s = estado.tsm_semanal;
  document.getElementById("semanal-valor").textContent = s ? (s.anomalia > 0 ? "+" : "") + s.anomalia.toFixed(2) + " °C" : "s/d";
  document.getElementById("semanal-nota").textContent = s ? `semana centrada en ${fmtDia(s.semana_centrada)}` : "no publicada en la última corrida";
  document.getElementById("actualizado").textContent = fmtFecha(estado.actualizado);
  actualizadoISO = estado.actualizado || "";
  const hace = (Date.now() - Date.parse(conZona(estado.actualizado))) / 36e5;
  document.getElementById("hace").textContent = isNaN(hace) ? "" :
    ` · actualizado hace ${hace < 1 ? Math.max(1, Math.round(hace * 60)) + " min" : hace < 48 ? Math.round(hace) + " h" : Math.round(hace / 24) + " d"}`;
  pintarFrescura(estado);
  pintarEnso(estado);
  window.analitica?.cabecera();
}

function pintarFrescura(estado) {
  const f = estado.fuentes || {};
  const ahora = Date.parse(conZona(estado.actualizado));
  const horas = iso => {
    if (!iso || isNaN(ahora)) return null;
    const h = (ahora - Date.parse(conZona(iso))) / 36e5;
    return isNaN(h) ? null : Math.max(0, h);
  };
  let hOni = null;
  if (f.oni?.trimestre) {
    const [tri, anio] = f.oni.trimestre.split(" ");
    const m = CENTRO_TRIMESTRE[tri];
    if (m) hOni = horas(`${anio}-${String(m).padStart(2, "0")}-15`);
  }
  const fuentes = [
    { n: "Condiciones de hoy", h: horas(f.condiciones_actuales?.hora), det: "cada hora" },
    { n: "Lluvia 30 días", h: horas(f.lluvia_30_dias?.hasta), det: "hasta ayer" },
    { n: "TSM semanal", h: f.tsm_semanal ? horas(f.tsm_semanal.semana_centrada) : null, det: "los lunes" },
    { n: "ONI", h: hOni, det: "centro del trimestre" },
  ];
  // eje logaritmico de edad (ahora ... 3 meses) y la climatologia fija al extremo derecho
  const X0 = 36, X1 = 280, HMAX = 2200;
  const x = h => X0 + (Math.log10(1 + h) / Math.log10(1 + HMAX)) * (X1 - X0);
  const ticks = [[6, "6 h"], [24, "1 d"], [168, "1 sem"], [720, "1 mes"]];
  const clamp = v => Math.min(Math.max(v, 30), 300);
  let svg = `<line class="eje" x1="${X0}" y1="40" x2="${X1 + 30}" y2="40"/>`;
  svg += `<line class="tick" x1="${X0}" y1="36" x2="${X0}" y2="44"/><text class="ahora" x="${X0}" y="58" text-anchor="middle">ahora</text>`;
  ticks.forEach(([h, t]) => svg += `<line class="tick" x1="${x(h)}" y1="37" x2="${x(h)}" y2="43"/><text class="tick-txt" x="${x(h)}" y="58" text-anchor="middle">${t}</text>`);
  svg += `<circle class="punto fijo" cx="${X1 + 30}" cy="40" r="3.5"/><text class="tick-txt" x="${X1 + 30}" y="58" text-anchor="middle">normal</text>`;
  fuentes.forEach((s, i) => {
    if (s.h == null) return;
    const cx = x(Math.min(s.h, HMAX));
    const arriba = i % 2 === 0;
    svg += `<line class="tick" x1="${cx}" y1="${arriba ? 24 : 40}" x2="${cx}" y2="${arriba ? 40 : 56}" opacity=".6"/>`;
    svg += `<circle class="punto" cx="${cx}" cy="40" r="4"/>`;
    svg += `<text class="punto-txt" x="${clamp(cx)}" y="${arriba ? 19 : 72}" text-anchor="middle">${s.n}</text>`;
  });
  document.getElementById("frescura").innerHTML = svg;

  const edad = h => h == null ? "s/d" : h < 1.5 ? "menos de 1 h" : h < 48 ? `${Math.round(h)} h` : h < 24 * 21 ? `${Math.round(h / 24)} d` : `${Math.round(h / 24 / 7)} sem`;
  const filas = fuentes.map(s => `<li><span>${s.n} · ${s.det}</span><strong>${edad(s.h)}</strong></li>`);
  filas.push(`<li><span>Pronóstico de lluvia hasta</span><strong>${fmtDia(f.pronostico_7_dias?.hasta)}</strong></li>`);
  filas.push(`<li><span>Normal 1991–2020</span><strong>fija</strong></li>`);
  document.getElementById("fuentes").innerHTML = filas.join("");
}

/* ---------- tabla ---------- */
function pintarTabla() {
  const prov = nivelActual === "provincia";
  const orden = [...registros].sort((a, b) => (b.nivel_alerta ?? -1) - (a.nivel_alerta ?? -1)
    || (b.anomalia_precipitacion_pct ?? -999) - (a.anomalia_precipitacion_pct ?? -999));
  const n = v => v == null ? "s/d" : v;
  const filas = orden.map(d => `<tr><td>${d.nombre}</td>${prov ? `<td>${d.departamento}</td>` : ""}
    <td class="num">${n(d.precipitacion_obs_mm)}</td><td class="num">${n(d.precipitacion_normal_mm)}</td>
    <td class="num">${d.normal_baja ? `${n(d.anomalia_precipitacion_mm)} mm` : ESCALAS.anomalia_precipitacion_pct.formato(d.anomalia_precipitacion_pct)}</td>
    <td class="num">${ESCALAS.anomalia_tmax_c.formato(d.anomalia_tmax_c)}</td>
    <td>${d.sin_datos || d.sin_normal ? "sin información" : ESCALAS.nivel_alerta.formato(d.nivel_alerta)}</td></tr>`);
  document.getElementById("tabla").innerHTML = `<thead><tr><th>Unidad</th>${prov ? "<th>Departamento</th>" : ""}
    <th>Lluvia 30 d (mm)</th><th>Normal (mm)</th><th>Anom. lluvia</th><th>Anom. T máx</th><th>Alerta</th></tr></thead>
    <tbody>${filas.join("")}</tbody>`;
}

/* ---------- carga por nivel ---------- */
function cargarNivel(nivel) {
  const cfg = NIVELES[nivel];
  const geoP = geoCache[nivel] || (geoCache[nivel] = fetch(cfg.geo).then(r => r.json()));
  // mientras llega el nivel nuevo, el anterior se mantiene atenuado: sin salto de layout
  const cont = document.getElementById("mapa");
  cont.classList.add("cargando");
  const fin = () => cont.classList.remove("cargando");
  return Promise.all([
    fetch(cfg.estado).then(r => { if (!r.ok) throw new Error(`${cfg.estado}: HTTP ${r.status}`); return r.json(); }),
    geoP
  ]).then(([estado, geo]) => {
    nivelActual = nivel;
    umbralNormalBaja = estado.umbral_normal_baja_mm ?? null;
    mesActual = estado.actualizado ? parseInt(estado.actualizado.slice(5, 7), 10) : mesActual;
    registros = estado[cfg.lista];
    porUnidad = {};
    registros.forEach(d => { porUnidad[cfg.claveDato(d)] = d; });
    pintarCabecera(estado);
    document.getElementById("aviso-nivel").textContent = nivel === "provincia"
      ? `${registros.length} provincias; ${estado.unidades_sin_datos ?? 0} sin información (en gris). Modelo de ~9 km; Putumayo figura dentro de Maynas.`
      : "";

    if (capaGeo) mapa.removeLayer(capaGeo);
    capaSeleccion = null; claveSeleccion = null;
    capaGeo = L.geoJSON(geo, {
      style: estilo,
      onEachFeature: (feature, layer) => {
        const clave = cfg.claveGeo(feature);
        if (CON_TOOLTIPS) layer.bindTooltip(() => `${cfg.etiqueta(feature)} · <b>${valorCapa(porUnidad[clave])}</b>`, { sticky: true, direction: "top", opacity: 1 });
        layer.on({
          mouseover: e => { if (capaSeleccion !== layer) e.target.setStyle({ weight: 2.5, color: "#f0efec" }); mostrarDetalle(porUnidad[clave]); },
          mouseout: e => { if (capaSeleccion !== layer) capaGeo.resetStyle(e.target); },
          click: e => { seleccionar(layer, clave); L.DomEvent.stopPropagation(e); }
        });
      }
    }).addTo(mapa);
    capasEtiquetas.eachLayer(l => l.setZIndexOffset(1000));
    dibujarLeyenda();
    pintarTabla();
    mostrarDetalle(null);
    window.analitica?.resumen(estado, nivel, cfg.lista);
    if (seleccionPendiente) {
      const buscada = seleccionPendiente; seleccionPendiente = null;
      capaGeo.eachLayer(l => { if (String(cfg.claveGeo(l.feature)) === buscada) seleccionar(l, buscada); });
    }
    escribirHash(claveSeleccion);
  }).finally(fin);
}

const inicial = leerHash();
if (inicial.capa && ESCALAS[inicial.capa] && inicial.capa !== "precipitacion_mm") {
  capaActual = inicial.capa;
  const r = document.querySelector(`input[name="capa"][value="${inicial.capa}"]`); if (r) r.checked = true;
}
const nivelInicial = inicial.nivel === "provincia" ? "provincia" : "departamento";
cargarNivel(nivelInicial).catch(() => cargarNivel("departamento")).then(() => {
  const r = document.querySelector(`input[name="nivel"][value="${nivelActual}"]`); if (r) r.checked = true;
  if (!capaSeleccion) mapa.fitBounds(capaGeo.getBounds(), { padding: [10, 10] });
  else mapa.fitBounds(capaSeleccion.getBounds().pad(1.2));
}).catch(err => {
  document.getElementById("detalle").innerHTML =
    `<p class="vacio">No se pudieron cargar los datos (${err.message}). Ejecuta <code>python scripts/actualizar.py</code> para generarlos.</p>`;
});

// La opcion "Provincias" solo se habilita si su estado ya fue publicado: las normales
// provinciales se calculan en una corrida larga y hasta entonces el archivo no existe.
fetch(NIVELES.provincia.estado, { method: "HEAD" }).then(r => {
  const lab = document.getElementById("opcion-provincia");
  if (!r.ok) {
    lab.classList.add("deshabilitada");
    lab.querySelector("input").disabled = true;
    lab.title = "En preparación: el cálculo de normales provinciales está en curso";
    lab.appendChild(Object.assign(document.createElement("span"), { textContent: " · en preparación", className: "nota" }));
  }
}).catch(() => {});

document.querySelectorAll('input[name="nivel"]').forEach(input => {
  input.addEventListener("change", e => {
    cargarNivel(e.target.value).catch(err => {
      document.getElementById("aviso-nivel").textContent = `Nivel provincial todavía sin datos publicados (${err.message}).`;
      document.querySelector('input[name="nivel"][value="departamento"]').checked = true;
    });
  });
});

document.querySelectorAll('input[name="capa"]').forEach(input => {
  input.addEventListener("change", e => {
    capaActual = e.target.value;
    if (capaGeo) { capaGeo.setStyle(estilo); if (capaSeleccion) capaSeleccion.setStyle({ weight: 2.5, color: "#f0efec" }); }
    dibujarLeyenda();
    escribirHash(claveSeleccion);
  });
});


/* ---------- descarga CSV (mismos valores que el mapa) ---------- */
document.getElementById("descargar-csv").addEventListener("click", () => {
  const prov = nivelActual === "provincia";
  const cols = [["unidad", d => d.nombre], ...(prov ? [["ubigeo", d => d.ubigeo], ["departamento", d => d.departamento]] : [["capital", d => d.capital]]),
    ["zona", d => d.zona], ["lluvia_30d_mm", d => d.precipitacion_obs_mm], ["normal_mm", d => d.precipitacion_normal_mm],
    ["normal_baja", d => d.normal_baja ? 1 : 0], ["anomalia_lluvia_pct", d => d.anomalia_precipitacion_pct],
    ["anomalia_lluvia_mm", d => d.anomalia_precipitacion_mm], ["tmax_30d_c", d => d.tmax_obs_c], ["anomalia_tmax_c", d => d.anomalia_tmax_c],
    ["lluvia_hoy_mm", d => d.lluvia_hoy_mm], ["temperatura_actual_c", d => d.temperatura_actual_c], ["pronostico_7d_mm", d => d.pronostico_7d_mm],
    ["nivel_alerta", d => d.nivel_alerta], ["sin_informacion", d => sinInfo(d) ? 1 : 0], ["lat", d => d.lat], ["lon", d => d.lon]];
  const celda = v => v == null ? "" : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v);
  const lineas = [cols.map(c => c[0]).join(","), ...registros.map(d => cols.map(c => celda(c[1](d))).join(","))];
  const blob = new Blob(["\ufeff" + lineas.join("\n")], { type: "text/csv;charset=utf-8" });
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob),
    download: `monitor-nino-${nivelActual}-${(actualizadoISO.slice(0, 16) || "datos").replace(/[:T]/g, "-")}.csv` });
  document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(a.href);
});
