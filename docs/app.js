const ESCALAS = {
  nivel_alerta: {
    titulo: "Nivel de alerta (indicativo)",
    colores: ["#2b5f3f", "#b78a2a", "#c25a1e", "#9b1d1d"],
    etiquetas: ["Sin señal", "Leve", "Moderada", "Alta"],
    color: v => ESCALAS.nivel_alerta.colores[Math.max(0, Math.min(3, v ?? 0))],
    formato: v => ESCALAS.nivel_alerta.etiquetas[v ?? 0]
  },
  anomalia_precipitacion_pct: {
    titulo: "Anomalía de lluvia (%)",
    cortes: [-60, -30, 0, 30, 60, 100],
    colores: ["#8c3b10", "#c07a35", "#d9c48a", "#8fc6c0", "#3f93b5", "#1f5d8c", "#123a63"],
    color: v => escalonado(v, ESCALAS.anomalia_precipitacion_pct),
    formato: v => v == null ? "s/d" : `${v > 0 ? "+" : ""}${v} %`
  },
  // Zonas con normal mensual muy baja: el porcentaje no informa, se muestra
  // el acumulado absoluto (escala propia, distinta de la de porcentaje).
  precipitacion_mm: {
    titulo: "Lluvia acumulada 30 días (mm), zonas de normal muy baja",
    cortes: [1, 5, 20, 50],
    colores: ["#efe6cf", "#d9c48a", "#8fc6c0", "#3f93b5", "#1f5d8c"],
    color: v => escalonado(v, ESCALAS.precipitacion_mm),
    formato: v => v == null ? "s/d" : `${v} mm`
  },
  anomalia_tmax_c: {
    titulo: "Anomalía de temperatura máxima (°C)",
    cortes: [-1, 0, 1, 2, 3],
    colores: ["#2f6f9e", "#7fb0c9", "#d9d2b4", "#e0a257", "#c9601f", "#8c2a10"],
    color: v => escalonado(v, ESCALAS.anomalia_tmax_c),
    formato: v => v == null ? "s/d" : `${v > 0 ? "+" : ""}${v} °C`
  }
};

function escalonado(v, escala) {
  if (v == null) return "#3a444d";
  let i = 0;
  while (i < escala.cortes.length && v >= escala.cortes[i]) i++;
  return escala.colores[i];
}

const normaliza = s => (s || "").toUpperCase()
  .normalize("NFD").replace(/[̀-ͯ]/g, "").trim();

const fmtFecha = s => s ? new Date(s).toLocaleString("es-PE",
  { dateStyle: "medium", timeStyle: "short" }) : "s/d";
const fmtDia = s => s ? new Date(s + "T12:00:00").toLocaleDateString("es-PE",
  { dateStyle: "medium" }) : "s/d";

let capaActual = "nivel_alerta";
let porDepartamento = {};
let umbralNormalBaja = null;
let capaGeo;

const mapa = L.map("mapa", { zoomControl: true, attributionControl: false })
  .setView([-9.8, -75.2], 5);

L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  maxZoom: 10, opacity: 0.55
}).addTo(mapa);

// Color de un departamento para la capa activa. En la capa de lluvia, las
// zonas con normal muy baja se pintan por acumulado en mm (ver limitacion 4).
function colorDe(d) {
  if (!d) return "#3a444d";
  if (capaActual === "anomalia_precipitacion_pct" && d.normal_baja) {
    return ESCALAS.precipitacion_mm.color(d.precipitacion_obs_mm);
  }
  return ESCALAS[capaActual].color(d[capaActual]);
}

function estilo(feature) {
  const d = porDepartamento[normaliza(feature.properties.NOMBDEP)];
  return {
    fillColor: colorDe(d),
    fillOpacity: 0.82, color: "#0f1419", weight: 1
  };
}

function mostrarDetalle(d) {
  const caja = document.getElementById("detalle");
  if (!d) {
    caja.innerHTML = '<p class="vacio">Pasa el cursor sobre un departamento.</p>';
    return;
  }
  const f = (v, u, dec = 1) => v == null ? "s/d" : `${v.toFixed(dec)} ${u}`;
  const lluviaPct = d.normal_baja
    ? `<dt>Anomalía de lluvia</dt><dd>no informativa</dd>
       <dt>Anomalía (mm)</dt><dd>${d.anomalia_precipitacion_mm == null ? "s/d"
         : (d.anomalia_precipitacion_mm > 0 ? "+" : "") + d.anomalia_precipitacion_mm + " mm"}</dd>`
    : `<dt>Anomalía de lluvia</dt>
       <dd>${ESCALAS.anomalia_precipitacion_pct.formato(d.anomalia_precipitacion_pct)}</dd>`;
  const aviso = d.normal_baja
    ? `<p class="nota">Normal mensual menor a ${umbralNormalBaja ?? "—"} mm: el porcentaje
       exagera cualquier lluvia pequeña, por eso se muestra el acumulado en mm.</p>` : "";
  const altitud = d.elevacion_modelo_m == null ? "" :
    `<dt>Altitud del punto de malla</dt><dd>${d.elevacion_modelo_m} m</dd>
     <dt>Altitud de la capital (ref.)</dt><dd>${d.altitud_capital_m ?? "s/d"} m</dd>`;
  const hoy = d.lluvia_hoy_mm == null ? "" :
    `<dt>Lluvia hoy (hasta la hora)</dt><dd>${f(d.lluvia_hoy_mm, "mm")}</dd>
     <dt>Temperatura actual</dt><dd>${f(d.temperatura_actual_c, "°C")}</dd>`;
  caja.innerHTML = `
    <h2>${d.nombre}</h2>
    <p class="vacio">${d.capital} · ${d.zona.replace(/_/g, " ")}</p>
    <dl>
      ${hoy}
      <dt>Lluvia (30 días)</dt><dd>${f(d.precipitacion_obs_mm, "mm")}</dd>
      <dt>Normal del periodo</dt><dd>${f(d.precipitacion_normal_mm, "mm")}</dd>
      ${lluviaPct}
      <dt>T. máxima media</dt><dd>${f(d.tmax_obs_c, "°C", 1)}</dd>
      <dt>Anomalía térmica</dt>
      <dd>${ESCALAS.anomalia_tmax_c.formato(d.anomalia_tmax_c)}</dd>
      <dt>Pronóstico 7 días</dt><dd>${f(d.pronostico_7d_mm, "mm")}</dd>
      <dt>Nivel de alerta</dt><dd>${ESCALAS.nivel_alerta.formato(d.nivel_alerta)}</dd>
      ${altitud}
    </dl>${aviso}`;
}

function dibujarLeyenda() {
  const escala = ESCALAS[capaActual];
  const caja = document.getElementById("leyenda");
  let filas;
  if (capaActual === "nivel_alerta") {
    filas = escala.colores.map((c, i) =>
      `<div class="fila-leyenda"><span class="muestra" style="background:${c}"></span>${escala.etiquetas[i]}</div>`);
  } else {
    const t = capaActual === "anomalia_tmax_c" ? "°C" : "%";
    filas = escala.colores.map((c, i) => {
      const a = i === 0 ? "" : escala.cortes[i - 1];
      const b = i === escala.colores.length - 1 ? "" : escala.cortes[i];
      const txt = !a ? `< ${b} ${t}` : !b ? `≥ ${a} ${t}` : `${a} a ${b} ${t}`;
      return `<div class="fila-leyenda"><span class="muestra" style="background:${c}"></span>${txt}</div>`;
    });
  }
  let extra = "";
  if (capaActual === "anomalia_precipitacion_pct") {
    const mm = ESCALAS.precipitacion_mm;
    const filasMm = mm.colores.map((c, i) => {
      const a = i === 0 ? 0 : mm.cortes[i - 1];
      const b = i === mm.colores.length - 1 ? "" : mm.cortes[i];
      const txt = !b ? `≥ ${a} mm` : `${a} a ${b} mm`;
      return `<div class="fila-leyenda"><span class="muestra" style="background:${c}"></span>${txt}</div>`;
    });
    extra = `<strong class="sub-leyenda">${mm.titulo}</strong>` + filasMm.join("") +
      `<p class="nota">Estas zonas tienen normal muy baja; el porcentaje no es informativo.</p>`;
  }
  caja.innerHTML = `<strong>${escala.titulo}</strong>` + filas.join("") + extra;
}

function pintarFuentes(estado) {
  const f = estado.fuentes;
  const lista = document.getElementById("fuentes");
  if (!f) {
    lista.innerHTML = "<li>Este archivo no trae el detalle por fuente; se actualiza en la próxima corrida.</li>";
    return;
  }
  const filas = [
    ["Condiciones actuales (Open-Meteo)", fmtFecha(f.condiciones_actuales?.hora), "cada hora"],
    ["Lluvia de los últimos 30 días hasta", fmtDia(f.lluvia_30_dias?.hasta), "rezago de 1 día"],
    ["Pronóstico 7 días hasta", fmtDia(f.pronostico_7_dias?.hasta), "pronóstico"],
    ["TSM semanal Niño 3.4, semana centrada en", f.tsm_semanal ? fmtDia(f.tsm_semanal.semana_centrada) : "no publicada", "semanal, lunes"],
    ["ONI (trimestre móvil)", f.oni?.trimestre ?? "s/d", "mensual"],
    ["Normal 1991–2020 (ERA5)", "fija", "no cambia"]
  ];
  lista.innerHTML = filas.map(([a, b, c]) =>
    `<li><span>${a}</span><strong>${b}</strong><em>${c}</em></li>`).join("");
}

Promise.all([
  fetch("data/estado.json").then(r => r.json()),
  fetch("peru_departamentos.geojson").then(r => r.json())
]).then(([estado, geo]) => {
  umbralNormalBaja = estado.umbral_normal_baja_mm ?? null;
  estado.departamentos.forEach(d => { porDepartamento[normaliza(d.nombre)] = d; });

  document.getElementById("oni-valor").textContent =
    (estado.oni.oni > 0 ? "+" : "") + estado.oni.oni.toFixed(2);
  document.getElementById("oni-estado").textContent = estado.oni.estado;
  document.getElementById("oni-trimestre").textContent =
    `${estado.oni.trimestre} ${estado.oni.anio} · TSM ${estado.oni.tsm} °C · trimestral`;

  const s = estado.tsm_semanal;
  document.getElementById("semanal-valor").textContent = s
    ? (s.anomalia > 0 ? "+" : "") + s.anomalia.toFixed(2) + " °C" : "s/d";
  document.getElementById("semanal-nota").textContent = s
    ? `semana centrada en ${fmtDia(s.semana_centrada)} · semanal`
    : "no publicada en la última corrida · semanal";

  document.getElementById("actualizado").textContent = fmtFecha(estado.actualizado);
  pintarFuentes(estado);

  capaGeo = L.geoJSON(geo, {
    style: estilo,
    onEachFeature: (feature, layer) => {
      const d = porDepartamento[normaliza(feature.properties.NOMBDEP)];
      layer.bindTooltip(feature.properties.NOMBDEP, { sticky: true });
      layer.on({
        mouseover: e => { e.target.setStyle({ weight: 2.5, color: "#e6edf3" }); mostrarDetalle(d); },
        mouseout: e => capaGeo.resetStyle(e.target),
        click: () => mapa.fitBounds(layer.getBounds())
      });
    }
  }).addTo(mapa);

  mapa.fitBounds(capaGeo.getBounds(), { padding: [12, 12] });
  dibujarLeyenda();
}).catch(err => {
  document.getElementById("detalle").innerHTML =
    `<p class="vacio">No se pudieron cargar los datos (${err.message}).
     Ejecuta <code>python scripts/actualizar.py</code> para generarlos.</p>`;
});

document.querySelectorAll('input[name="capa"]').forEach(input => {
  input.addEventListener("change", e => {
    capaActual = e.target.value;
    if (capaGeo) capaGeo.setStyle(estilo);
    dibujarLeyenda();
  });
});
