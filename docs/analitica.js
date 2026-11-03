/* Capa descriptiva del monitor: perfil anual de la normal por unidad, resumen
   nacional por zona, ONI de cinco anios e historial diario. Todo sale de los
   JSON ya publicados; no pide nada nuevo a las APIs. Las funciones se cuelgan
   de window.analitica y app.js las llama en sus puntos de pintado. */
(() => {
  const SERIE = "#3987e5";       // una sola serie: tono 1 de la rampa
  const TINTA = "#f0efec", TENUE = "#898781", LINEA = "rgba(255,255,255,.14)";
  const MESES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];
  const ZONAS = { costa_norte: "Costa norte", costa_centro_sur: "Costa centro-sur", sierra_norte: "Sierra norte", sierra_sur: "Sierra sur", selva: "Selva" };
  const cache = {};
  const traer = (ruta, opcional) => cache[ruta] || (cache[ruta] = fetch(ruta).then(r => {
    if (!r.ok) { if (opcional) return null; throw new Error(`${ruta}: HTTP ${r.status}`); }
    return r.json();
  }).catch(e => { if (opcional) return null; throw e; }));
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const fmt = (v, dec = 1) => v == null ? "s/d" : (v > 0 ? "+" : "") + v.toFixed(dec);

  /* ---------- perfil anual de la normal (12 barras) con el mes actual y lo observado ---------- */
  function perfilNormal(normales, clave, d, mesActual) {
    const n = normales?.[clave];
    if (!n) return "";
    const vals = Array.from({ length: 12 }, (_, i) => n[String(i + 1).padStart(2, "0")]?.precipitacion_mensual_mm ?? 0);
    const obs = d.precipitacion_obs_mm;
    const max = Math.max(...vals, obs || 0, 1);
    const W = 300, H = 92, x0 = 26, y0 = 6, bw = (W - x0 - 4) / 12, hb = 60;
    const y = v => y0 + hb - (v / max) * hb;
    let s = `<svg viewBox="0 0 ${W} ${H}" class="perfil" role="img" aria-label="Normal mensual de lluvia 1991-2020 y valor observado del mes actual">`;
    s += `<line x1="${x0}" y1="${y0 + hb}" x2="${W - 4}" y2="${y0 + hb}" stroke="${LINEA}"/>`;
    s += `<text x="${x0 - 4}" y="${y0 + 6}" text-anchor="end" fill="${TENUE}" font-size="8">${Math.round(max)}</text>`;
    s += `<text x="${x0 - 4}" y="${y0 + hb}" text-anchor="end" fill="${TENUE}" font-size="8">0</text>`;
    vals.forEach((v, i) => {
      const actual = i + 1 === mesActual;
      const bx = x0 + i * bw + 2, bh = Math.max(0, (v / max) * hb);
      s += `<rect x="${bx}" y="${y(v)}" width="${bw - 4}" height="${bh}" rx="2" fill="${SERIE}" opacity="${actual ? 1 : 0.45}"><title>${MESES[i]}: normal ${v.toFixed(1)} mm</title></rect>`;
      s += `<text x="${bx + (bw - 4) / 2}" y="${H - 14}" text-anchor="middle" fill="${actual ? TINTA : TENUE}" font-size="8" font-weight="${actual ? 600 : 400}">${MESES[i]}</text>`;
      if (actual && obs != null) {
        s += `<line x1="${bx - 2}" y1="${y(obs)}" x2="${bx + bw - 2}" y2="${y(obs)}" stroke="${TINTA}" stroke-width="2"><title>observado 30 días: ${obs} mm</title></line>`;
      }
    });
    s += `</svg>`;
    const normMes = vals[mesActual - 1];
    const lectura = obs == null ? "" : obs > normMes * 1.3 ? "muy por encima de la normal del mes" : obs > normMes * 1.1 ? "por encima de la normal del mes"
      : obs < normMes * 0.7 ? "muy por debajo de la normal del mes" : obs < normMes * 0.9 ? "por debajo de la normal del mes" : "cerca de la normal del mes";
    return `<div class="analitica"><h4>Normal mensual de lluvia, 1991–2020</h4>${s}
      <p class="nota">Barras: normal de cada mes (mm). Línea blanca sobre el mes actual: lluvia observada en los últimos 30 días${obs == null ? "" : `, ${obs} mm, ${lectura}`}.</p></div>`;
  }

  /* ---------- linea de evolucion de una unidad (historial diario) ---------- */
  function sparkline(valores, etiqueta, unidad) {
    const puntos = valores.filter(p => p.v != null);
    if (puntos.length < 2) {
      return `<p class="nota">Evolución: ${puntos.length} día${puntos.length === 1 ? "" : "s"} de historial${puntos.length ? ` (desde ${puntos[0].f})` : ""}. Se completa con las próximas actualizaciones.</p>`;
    }
    const W = 300, H = 54, x0 = 4, x1 = W - 40, y0 = 6, y1 = H - 14;
    const vs = puntos.map(p => p.v), lo = Math.min(0, ...vs), hi = Math.max(0, ...vs), rango = hi - lo || 1;
    const x = i => x0 + (i / (puntos.length - 1)) * (x1 - x0), y = v => y1 - ((v - lo) / rango) * (y1 - y0);
    const path = puntos.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.v).toFixed(1)}`).join(" ");
    const ult = puntos[puntos.length - 1];
    return `<div class="analitica"><h4>${esc(etiqueta)}</h4>
      <svg viewBox="0 0 ${W} ${H}" class="spark" role="img" aria-label="${esc(etiqueta)}, ${puntos.length} días">
        <line x1="${x0}" y1="${y(0)}" x2="${x1}" y2="${y(0)}" stroke="${LINEA}"/>
        <path d="${path}" fill="none" stroke="${SERIE}" stroke-width="2" stroke-linejoin="round"/>
        <circle cx="${x(puntos.length - 1)}" cy="${y(ult.v)}" r="3" fill="${SERIE}" stroke="#15181d" stroke-width="2"/>
        <text x="${x1 + 6}" y="${y(ult.v) + 3}" fill="${TINTA}" font-size="9" font-family="IBM Plex Mono, monospace">${fmt(ult.v)}${unidad}</text>
        <text x="${x0}" y="${H - 2}" fill="${TENUE}" font-size="8">${puntos[0].f}</text>
        <text x="${x1}" y="${H - 2}" fill="${TENUE}" font-size="8" text-anchor="end">${ult.f}</text>
      </svg></div>`;
  }

  /* ---------- resumen nacional ---------- */
  function resumen(estado, lista, historial) {
    const regs = estado[lista];
    const niveles = [0, 0, 0, 0]; let sinInfo = 0, normalBaja = 0;
    const zonas = {};
    regs.forEach(d => {
      if (d.sin_datos || d.sin_normal || d.nivel_alerta == null) { sinInfo++; return; }
      niveles[d.nivel_alerta]++;
      if (d.normal_baja) normalBaja++;
      const z = zonas[d.zona] || (zonas[d.zona] = { n: 0, pp: [], tx: [], al: [] });
      z.n++; z.al.push(d.nivel_alerta);
      if (d.anomalia_precipitacion_pct != null) z.pp.push(d.anomalia_precipitacion_pct);
      if (d.anomalia_tmax_c != null) z.tx.push(d.anomalia_tmax_c);
    });
    const media = a => a.length ? a.reduce((s, v) => s + v, 0) / a.length : null;
    const etq = ["Sin señal", "Leve", "Moderada", "Alta"], col = ["#3f3f3b", "#fab219", "#ec835a", "#d03b3b"];
    const conteos = niveles.map((n, i) => `<div class="conteo"><i style="background:${col[i]}"></i><strong>${n}</strong><span>${etq[i]}</span></div>`).join("")
      + (sinInfo ? `<div class="conteo"><i class="sin-info"></i><strong>${sinInfo}</strong><span>Sin información</span></div>` : "");
    const filas = Object.entries(zonas).sort((a, b) => media(b[1].al) - media(a[1].al)).map(([z, v]) =>
      `<tr><td>${ZONAS[z] || z}</td><td class="num">${v.n}</td><td class="num">${v.pp.length ? fmt(media(v.pp), 0) + " %" : "—"}</td><td class="num">${v.tx.length ? fmt(media(v.tx), 1) + " °C" : "—"}</td></tr>`).join("");
    let evol = "";
    if (historial && lista === "departamentos") {
      const serie = historial.dias.map(dia => {
        const u = Object.values(dia.unidades); const con = u.filter(x => x.al != null);
        return { f: dia.fecha.slice(5), v: con.length ? Math.round(100 * con.filter(x => x.al >= 2).length / con.length) : null };
      });
      evol = sparkline(serie, "Departamentos en alerta moderada o alta (%)", " %");
    }
    return `<div class="conteos">${conteos}</div>
      <table class="zonas"><thead><tr><th>Zona</th><th>n</th><th>Anom. lluvia</th><th>Anom. T máx</th></tr></thead><tbody>${filas}</tbody></table>
      <p class="nota">Medias simples por zona de las unidades con dato; la anomalía de lluvia excluye las ${normalBaja} unidades con normal muy baja. Las zonas y los umbrales son provisionales.</p>${evol}`;
  }

  /* ---------- ONI, ultimos cinco anios ---------- */
  function graficoOni(oni) {
    const serie = oni?.serie || [];
    if (serie.length < 2) return "";
    const W = 300, H = 96, x0 = 26, x1 = W - 6, y0 = 8, y1 = H - 16;
    const vs = serie.map(p => p.oni), lo = Math.min(-1, ...vs) - 0.2, hi = Math.max(1, ...vs) + 0.2;
    const x = i => x0 + (i / (serie.length - 1)) * (x1 - x0), y = v => y1 - ((v - lo) / (hi - lo)) * (y1 - y0);
    const path = serie.map((p, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(p.oni).toFixed(1)}`).join(" ");
    let s = `<svg viewBox="0 0 ${W} ${H}" class="oni" role="img" aria-label="ONI de los últimos cinco años">`;
    [[0.5, "+0,5"], [-0.5, "−0,5"]].forEach(([u, t]) => s += `<line x1="${x0}" y1="${y(u)}" x2="${x1}" y2="${y(u)}" stroke="${LINEA}"/><text x="${x0 - 3}" y="${y(u) + 3}" text-anchor="end" fill="${TENUE}" font-size="8">${t}</text>`);
    s += `<line x1="${x0}" y1="${y(0)}" x2="${x1}" y2="${y(0)}" stroke="rgba(255,255,255,.28)"/>`;
    s += `<path d="${path}" fill="none" stroke="${SERIE}" stroke-width="2" stroke-linejoin="round"/>`;
    serie.forEach((p, i) => { if (p.trimestre === "DJF") s += `<text x="${x(i)}" y="${H - 4}" text-anchor="middle" fill="${TENUE}" font-size="8">${p.anio}</text>`; });
    // objetivos de hover mas anchos que el punto (tooltip nativo)
    serie.forEach((p, i) => s += `<rect x="${x(i) - (x1 - x0) / serie.length / 2}" y="${y0}" width="${(x1 - x0) / serie.length}" height="${y1 - y0}" fill="transparent"><title>${p.trimestre} ${p.anio}: ${fmt(p.oni, 2)}</title></rect>`);
    const ult = serie[serie.length - 1];
    s += `<circle cx="${x(serie.length - 1)}" cy="${y(ult.oni)}" r="3" fill="${SERIE}" stroke="#15181d" stroke-width="2"/>`;
    s += `</svg>`;
    return `<div class="analitica"><h4>ONI, últimos cinco años</h4>${s}<p class="nota">Media móvil trimestral de la anomalía en Niño 3.4. Líneas finas: umbrales ±0,5 °C de la NOAA; El Niño requiere cinco trimestres seguidos por encima. Pasa el cursor para ver cada trimestre.</p></div>`;
  }

  window.analitica = {
    // bloque ENSO: ONI de cinco anios
    cabecera() {
      traer("data/oni.json", true).then(o => { const el = document.getElementById("oni-grafico"); if (el) el.innerHTML = graficoOni(o); });
    },
    // bloque resumen: por nivel cargado
    resumen(estado, nivel, lista) {
      const el = document.getElementById("resumen-cuerpo"); if (!el) return;
      document.getElementById("resumen-nivel").textContent = nivel === "provincia" ? "provincias" : "departamentos";
      traer("data/historial.json", true).then(h => { el.innerHTML = resumen(estado, lista, h); });
    },
    // detalle de una unidad: perfil anual + evolucion
    detalle(d, nivel, clave, mesActual) {
      const cont = document.getElementById("detalle-analitica"); if (!cont || !d || d.sin_datos || d.sin_normal) return;
      const ruta = nivel === "provincia" ? "data/normales_provincias.json" : "data/normales.json";
      Promise.all([traer(ruta, true), nivel === "departamento" ? traer("data/historial.json", true) : null]).then(([n, h]) => {
        let html = perfilNormal(n?.normales, clave, d, mesActual);
        if (h) {
          const serie = h.dias.map(dia => ({ f: dia.fecha.slice(5), v: dia.unidades[clave]?.pp ?? null }));
          html += sparkline(serie, "Anomalía de lluvia, evolución diaria (%)", " %");
        }
        cont.innerHTML = html;
      });
    }
  };
})();
