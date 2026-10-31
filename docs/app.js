const ESCALAS = {
  nivel_alerta: {
    titulo: "Nivel de alerta",
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

let capaActual = "nivel_alerta";
let porDepartamento = {};
let capaGeo;

const mapa = L.map("mapa", { zoomControl: true, attributionControl: false })
  .setView([-9.8, -75.2], 5);

L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  maxZoom: 10, opacity: 0.55
}).addTo(mapa);

function estilo(feature) {
  const d = porDepartamento[normaliza(feature.properties.NOMBDEP)];
  const escala = ESCALAS[capaActual];
  return {
    fillColor: d ? escala.color(d[capaActual]) : "#3a444d",
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
  caja.innerHTML = `
    <h2>${d.nombre}</h2>
    <p class="vacio">${d.capital} · ${d.zona.replace(/_/g, " ")}</p>
    <dl>
      <dt>Lluvia (30 días)</dt><dd>${f(d.precipitacion_obs_mm, "mm")}</dd>
      <dt>Normal del periodo</dt><dd>${f(d.precipitacion_normal_mm, "mm")}</dd>
      <dt>Anomalía de lluvia</dt>
      <dd>${ESCALAS.anomalia_precipitacion_pct.formato(d.anomalia_precipitacion_pct)}</dd>
      <dt>T. máxima media</dt><dd>${f(d.tmax_obs_c, "°C", 1)}</dd>
      <dt>Anomalía térmica</dt>
      <dd>${ESCALAS.anomalia_tmax_c.formato(d.anomalia_tmax_c)}</dd>
      <dt>Pronóstico 7 días</dt><dd>${f(d.pronostico_7d_mm, "mm")}</dd>
      <dt>Nivel de alerta</dt><dd>${ESCALAS.nivel_alerta.formato(d.nivel_alerta)}</dd>
    </dl>`;
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
  caja.innerHTML = `<strong>${escala.titulo}</strong>` + filas.join("");
}

Promise.all([
  fetch("data/estado.json").then(r => r.json()),
  fetch("peru_departamentos.geojson").then(r => r.json())
]).then(([estado, geo]) => {
  estado.departamentos.forEach(d => { porDepartamento[normaliza(d.nombre)] = d; });

  document.getElementById("oni-valor").textContent =
    (estado.oni.oni > 0 ? "+" : "") + estado.oni.oni.toFixed(2);
  document.getElementById("oni-estado").textContent = estado.oni.estado;
  document.getElementById("oni-trimestre").textContent =
    `${estado.oni.trimestre} ${estado.oni.anio} · TSM ${estado.oni.tsm} °C`;
  document.getElementById("actualizado").textContent =
    new Date(estado.actualizado).toLocaleString("es-PE",
      { dateStyle: "medium", timeStyle: "short" });

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
