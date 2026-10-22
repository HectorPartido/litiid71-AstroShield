// AstroShield — lógica del visor: carga resultados reales y llena el panel.
//
// Lee results/index.json (lista de ejecuciones) y results/<archivo>.json
// (generados por `python -m astroshield.cli run`). No hay datos fijos aquí:
// si el archivo cambia, el globo cambia.
//
// Responsable: Ismael Alexander Hidalgo Aguilando

import { Globo } from "./globo.js";

const RUTA_RESULTADOS = "../results/";

const estado = { resultado: null, modo: "final" };
const globo = new Globo(document.getElementById("escena"));

globo.cargarContinentes().catch(() =>
    avisar("No se pudieron cargar los contornos de los continentes (¿sin internet?). El resto del visor funciona."));

// ---------- Utilidades ----------

const $ = (sel) => document.querySelector(sel);
const pct = (x) => `${(x * 100).toFixed(1)}%`;
const fx = (x) => Number(x).toFixed(4);

function avisar(texto) {
    const a = $("#aviso");
    a.textContent = texto;
    a.hidden = false;
}

const COLOR_CSS = (r) => r.cubierta ? "var(--cubierta)" : r.cobertura > 0 ? "var(--parcial)" : "var(--descubierta)";

// ---------- Carga de datos ----------

async function cargarIndice() {
    const resp = await fetch(RUTA_RESULTADOS + "index.json", { cache: "no-store" });
    if (!resp.ok) throw new Error("Sin index.json");
    return resp.json();
}

async function cargarResultado(archivo) {
    const resp = await fetch(RUTA_RESULTADOS + archivo, { cache: "no-store" });
    if (!resp.ok) throw new Error(`No se encontró ${archivo}`);
    return resp.json();
}

// ---------- Panel ----------

function pintarResumen(res) {
    const ini = res.inicial.evaluacion;
    const fin = res.final.evaluacion;
    const fila = (nombre, a, b, formato = fx) => {
        const mejora = typeof a === "number" && b > a ? "mejora" : "";
        return `<span>${nombre}</span><span class="num">${formato(a)}</span><span class="num ${mejora}">${formato(b)}</span>`;
    };
    const suf = res.gen_suficiente === null
        ? "No alcanzó el criterio de “suficientemente buena”."
        : `“Suficientemente buena” desde la generación ${res.gen_suficiente}.`;

    $("#resumen").innerHTML = `
    <h2>Resultado</h2>
    <span class="etiqueta-estado ${fin.valida ? "ok" : "mal"}">${fin.valida ? "Configuración válida" : "Configuración INVÁLIDA"}</span>
    <p class="meta">Escenario <b>${res.escenario.nombre}</b> · semilla ${res.semilla} ·
      ${res.generaciones_ejecutadas} generaciones · ${res.parametros.num_satelites} satélites<br>${suf}</p>
    <div class="metricas">
      <span></span><span class="enc">Inicial</span><span class="enc">Final</span>
      ${fila("Fitness", ini.fitness, fin.fitness)}
      ${fila("Cobertura ponderada", ini.cobertura_ponderada, fin.cobertura_ponderada, pct)}
      ${fila("Redundancia Alta", ini.redundancia_alta, fin.redundancia_alta, pct)}
      ${fila("Regiones cubiertas", ini.regiones_cubiertas, fin.regiones_cubiertas, (x) => `${x}/${res.escenario.regiones.length}`)}
      ${fila("Violación (°)", ini.violacion, fin.violacion, (x) => Number(x).toFixed(2))}
    </div>`;
}

function pintarRegiones(res) {
    const ev = (estado.modo === "inicial" ? res.inicial : res.final).evaluacion;
    const filas = ev.regiones.map((r) => `
    <tr>
      <td><span class="punto" style="background:${COLOR_CSS(r)}"></span>${r.nombre.split(",")[0]}</td>
      <td>${r.prioridad}</td>
      <td class="num">${pct(r.cobertura)}</td>
      <td class="num">${r.satelites_que_ven.length ? "S" + r.satelites_que_ven.join(", S") : "—"}</td>
    </tr>`).join("");
    $("#tabla-regiones").innerHTML =
        `<tr><th>Región</th><th>Prioridad</th><th style="text-align:right">Cobertura</th><th style="text-align:right">Satélites</th></tr>${filas}`;
}

function pintarViolaciones(res) {
    const conf = estado.modo === "inicial" ? res.inicial : res.final;
    const v = conf.evaluacion.violaciones;
    $("#violaciones").innerHTML = v.length === 0
        ? `<h2>Restricciones</h2><p class="meta">Ningún satélite invade zonas de desechos, objetos ocupados ni la separación mínima.</p>`
        : `<h2>Restricciones violadas</h2><ul>${v.map((x) =>
            `<li>S${x.satelite} → ${x.zona} (${x.tipo}): ${x.invasion_grados}°</li>`).join("")}</ul>`;
}

/** Gráfica de mejor/promedio fitness y % de válidos por generación (canvas 2D). */
function pintarGrafica(res) {
    const canvas = $("#grafica");
    const ctx = canvas.getContext("2d");
    const escala = window.devicePixelRatio || 1;
    const W = canvas.clientWidth, H = canvas.clientHeight;
    canvas.width = W * escala;
    canvas.height = H * escala;
    ctx.setTransform(escala, 0, 0, escala, 0, 0);
    ctx.clearRect(0, 0, W, H);

    const h = res.historial;
    const m = { izq: 28, der: 6, arr: 8, aba: 18 };
    const x = (g) => m.izq + (g / Math.max(1, h.length - 1)) * (W - m.izq - m.der);
    const y = (v) => H - m.aba - v * (H - m.arr - m.aba);

    ctx.strokeStyle = "#1f2a3d";
    ctx.fillStyle = "#8796ad";
    ctx.font = "10px system-ui";
    for (const v of [0, 0.5, 1]) {
        ctx.beginPath(); ctx.moveTo(m.izq, y(v)); ctx.lineTo(W - m.der, y(v)); ctx.stroke();
        ctx.fillText(v.toFixed(1), 4, y(v) + 3);
    }
    ctx.fillText("gen 0", m.izq, H - 4);
    ctx.textAlign = "right";
    ctx.fillText(`gen ${h.length - 1}`, W - m.der, H - 4);
    ctx.textAlign = "left";

    const serie = (campo, color, ancho) => {
        ctx.strokeStyle = color; ctx.lineWidth = ancho; ctx.beginPath();
        h.forEach((g, i) => (i ? ctx.lineTo(x(i), y(g[campo])) : ctx.moveTo(x(i), y(g[campo]))));
        ctx.stroke(); ctx.lineWidth = 1;
    };
    serie("pct_validos", "#64748b", 1);
    serie("promedio_fitness", "#c084fc", 1.5);
    serie("mejor_fitness", "#4fc3f7", 2);

    if (res.gen_suficiente !== null) {
        ctx.strokeStyle = "#34d399"; ctx.setLineDash([3, 3]);
        ctx.beginPath(); ctx.moveTo(x(res.gen_suficiente), y(0)); ctx.lineTo(x(res.gen_suficiente), y(1)); ctx.stroke();
        ctx.setLineDash([]);
    }
}

function pintarTodo() {
    const res = estado.resultado;
    if (!res) return;
    globo.mostrar(res, estado.modo);
    pintarResumen(res);
    pintarRegiones(res);
    pintarViolaciones(res);
    pintarGrafica(res);
}

// ---------- Eventos ----------

async function seleccionar(archivo) {
    try {
        estado.resultado = await cargarResultado(archivo);
        $("#aviso").hidden = true;
        const url = new URL(location.href);
        url.searchParams.set("archivo", archivo);
        history.replaceState(null, "", url);
        pintarTodo();
    } catch (e) {
        avisar(e.message);
    }
}

$("#selector").addEventListener("change", (e) => seleccionar(e.target.value));

document.querySelectorAll(".modos button").forEach((b) =>
    b.addEventListener("click", () => {
        document.querySelectorAll(".modos button").forEach((x) => x.classList.toggle("activo", x === b));
        estado.modo = b.dataset.modo;
        pintarTodo();
    }));

document.querySelectorAll("[data-capa]").forEach((c) =>
    c.addEventListener("change", () => globo.verCapa(c.dataset.capa, c.checked)));

$("#girar").addEventListener("change", (e) => globo.girar(e.target.checked));

// ---------- Inicio ----------

(async function iniciar() {
    let indice;
    try {
        indice = await cargarIndice();
    } catch {
        avisar("No se encontró results/index.json. Ejecuta primero: python -m astroshield.cli run, " +
            "y abre el visor con un servidor desde la raíz del repo (python -m http.server 8000).");
        return;
    }
    if (indice.length === 0) {
        avisar("results/index.json está vacío: todavía no hay ejecuciones.");
        return;
    }
    const sel = $("#selector");
    sel.innerHTML = indice.map((e) =>
        `<option value="${e.archivo}">${e.escenario} · semilla ${e.semilla} · fitness ${fx(e.fitness)}` +
        `${e.valida ? "" : " · INVÁLIDA"}</option>`).join("");

    const pedido = new URLSearchParams(location.search).get("archivo");
    const inicial = indice.find((e) => e.archivo === pedido) || indice.find((e) => e.archivo === "base_s42.json") || indice[0];
    sel.value = inicial.archivo;
    await seleccionar(inicial.archivo);
})();