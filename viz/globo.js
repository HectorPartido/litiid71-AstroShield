// AstroShield — escena 3D del globo terrestre (Three.js).
// Solo dibuja; los datos los recibe de app.js, que los lee de results/*.json.
//
// Responsable: Ismael Alexander Hidalgo Aguilando

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";
import * as topojson from "topojson-client";

const RADIO_TIERRA_KM = 6371;
const URL_CONTINENTES = "https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json";

export const COLORES = {
    oceano: 0x0b1e3a,
    tierra: 0x5b7aa6,
    reticula: 0x1c3358,
    cubierta: 0x34d399,
    parcial: 0xfbbf24,
    descubierta: 0xf43f5e,
    satelite: 0x38bdf8,
    inicial: 0xa3a3a3,
    desechos: 0xef4444,
    ocupado: 0xf97316,
};

// Pequeñas alturas sobre la superficie para que las capas no se encimen
const ALTURA = { tierra: 1.001, zona: 1.002, huella: 1.003, region: 1.005 };

// ---------- Geometría esférica (misma matemática que src/astroshield/geo.py) ----------

const rad = (g) => (g * Math.PI) / 180;
const grad = (r) => (r * 180) / Math.PI;

/** lat/lon (grados) → vector 3D sobre una esfera de radio r (eje Y = norte). */
export function aVector(lat, lon, r = 1) {
    const f = rad(lat), l = rad(lon);
    return new THREE.Vector3(r * Math.cos(f) * Math.cos(l), r * Math.sin(f), -r * Math.cos(f) * Math.sin(l));
}

/** Punto al que se llega avanzando `dist` grados desde (lat, lon) con rumbo `az`. */
function puntoDestino(lat, lon, az, dist) {
    const p1 = rad(lat), l1 = rad(lon), th = rad(az), d = rad(dist);
    const p2 = Math.asin(Math.sin(p1) * Math.cos(d) + Math.cos(p1) * Math.sin(d) * Math.cos(th));
    const l2 = l1 + Math.atan2(Math.sin(th) * Math.sin(d) * Math.cos(p1), Math.cos(d) - Math.sin(p1) * Math.sin(p2));
    return [grad(p2), grad(l2)];
}

/** Casquete esférico (círculo sobre la esfera) de radio angular `radioGrados`.
 *  Se subdivide en anillos para que siga la curvatura y no quede bajo la superficie. */
function geometriaCasquete(lat, lon, radioGrados, r, anillos = 8, segmentos = 64) {
    const pos = [aVector(lat, lon, r)];
    for (let i = 1; i <= anillos; i++) {
        for (let j = 0; j < segmentos; j++) {
            const [la, lo] = puntoDestino(lat, lon, (360 * j) / segmentos, (radioGrados * i) / anillos);
            pos.push(aVector(la, lo, r));
        }
    }
    const indices = [];
    for (let j = 0; j < segmentos; j++) indices.push(0, 1 + j, 1 + ((j + 1) % segmentos));
    for (let i = 1; i < anillos; i++) {
        const a = 1 + (i - 1) * segmentos, b = 1 + i * segmentos;
        for (let j = 0; j < segmentos; j++) {
            const j2 = (j + 1) % segmentos;
            indices.push(a + j, b + j, b + j2, a + j, b + j2, a + j2);
        }
    }
    const g = new THREE.BufferGeometry().setFromPoints(pos);
    g.setIndex(indices);
    return g;
}

function contornoCirculo(lat, lon, radioGrados, r, segmentos = 96) {
    const pts = [];
    for (let j = 0; j <= segmentos; j++) {
        const [la, lo] = puntoDestino(lat, lon, (360 * j) / segmentos, radioGrados);
        pts.push(aVector(la, lo, r));
    }
    return new THREE.BufferGeometry().setFromPoints(pts);
}

function circuloSobreEsfera(lat, lon, radioGrados, r, color, opacidad, conBorde = true) {
    const grupo = new THREE.Group();
    const relleno = new THREE.Mesh(
        geometriaCasquete(lat, lon, radioGrados, r),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: opacidad, depthWrite: false, side: THREE.DoubleSide })
    );
    grupo.add(relleno);
    if (conBorde) {
        grupo.add(new THREE.Line(contornoCirculo(lat, lon, radioGrados, r * 1.0005),
            new THREE.LineBasicMaterial({ color, transparent: true, opacity: Math.min(1, opacidad * 3) })));
    }
    return grupo;
}

function etiqueta(texto, clase, posicion, aLaDerecha = false) {
    const div = document.createElement("div");
    div.className = `etq ${clase}`;
    div.textContent = texto;
    const obj = new CSS2DObject(div);
    obj.position.copy(posicion);
    if (aLaDerecha) obj.center.set(-0.7, 0.5);   // la etiqueta no tapa al satélite
    return obj;
}

// ---------- Clase principal ----------

export class Globo {
    constructor(contenedor) {
        this.contenedor = contenedor;
        this.escena = new THREE.Scene();

        this.camara = new THREE.PerspectiveCamera(45, 1, 0.01, 100);
        this.camara.position.copy(aVector(15, -60, 3.6));

        this.render3d = new THREE.WebGLRenderer({ antialias: true });
        this.render3d.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        contenedor.appendChild(this.render3d.domElement);

        this.renderEtq = new CSS2DRenderer();
        this.renderEtq.domElement.style.position = "absolute";
        this.renderEtq.domElement.style.top = "0";
        this.renderEtq.domElement.style.pointerEvents = "none";
        contenedor.appendChild(this.renderEtq.domElement);

        this.controles = new OrbitControls(this.camara, this.render3d.domElement);
        this.controles.enableDamping = true;
        this.controles.minDistance = 1.4;
        this.controles.maxDistance = 8;
        this.controles.autoRotateSpeed = 0.6;

        this.escena.add(new THREE.AmbientLight(0xffffff, 0.55));
        const sol = new THREE.DirectionalLight(0xffffff, 1.1);
        sol.position.set(5, 3, 5);
        this.escena.add(sol);

        // Capas que se pueden encender/apagar desde el panel
        this.capas = {
            base: new THREE.Group(),
            regiones: new THREE.Group(),
            huellas: new THREE.Group(),
            satelites: new THREE.Group(),
            zonas: new THREE.Group(),
            ocupados: new THREE.Group(),
            etiquetas: new THREE.Group(),
        };
        Object.values(this.capas).forEach((g) => this.escena.add(g));

        this._crearTierra();
        this._ajustarTamano();
        window.addEventListener("resize", () => this._ajustarTamano());
        this._animar();
    }

    _crearTierra() {
        const tierra = new THREE.Mesh(
            new THREE.SphereGeometry(1, 96, 64),
            new THREE.MeshPhongMaterial({ color: COLORES.oceano, shininess: 12 })
        );
        this.capas.base.add(tierra);

        // Retícula cada 30°
        const mat = new THREE.LineBasicMaterial({ color: COLORES.reticula, transparent: true, opacity: 0.7 });
        for (let lat = -60; lat <= 60; lat += 30) {
            const pts = [];
            for (let lon = -180; lon <= 180; lon += 3) pts.push(aVector(lat, lon, ALTURA.tierra));
            this.capas.base.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
        }
        for (let lon = -180; lon < 180; lon += 30) {
            const pts = [];
            for (let lat = -90; lat <= 90; lat += 3) pts.push(aVector(lat, lon, ALTURA.tierra));
            this.capas.base.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
        }
    }

    /** Descarga los contornos de los continentes (Natural Earth vía world-atlas). */
    async cargarContinentes() {
        const resp = await fetch(URL_CONTINENTES);
        if (!resp.ok) throw new Error("No se pudieron descargar los continentes");
        const topo = await resp.json();
        const lineas = topojson.mesh(topo, topo.objects.land);
        const mat = new THREE.LineBasicMaterial({ color: COLORES.tierra });
        for (const anillo of lineas.coordinates) {
            const pts = anillo.map(([lon, lat]) => aVector(lat, lon, ALTURA.tierra));
            this.capas.base.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
        }
    }

    _limpiar(grupo) {
        grupo.traverse((o) => {
            if (o.geometry) o.geometry.dispose();
            if (o.material) o.material.dispose();
            if (o.element) o.element.remove();
        });
        grupo.clear();
    }

    /**
     * Dibuja un resultado.
     * @param {object} res   contenido de results/<archivo>.json
     * @param {"final"|"inicial"|"ambas"} modo
     */
    mostrar(res, modo) {
        ["regiones", "huellas", "satelites", "zonas", "ocupados", "etiquetas"].forEach((c) => this._limpiar(this.capas[c]));

        const esc = res.escenario;
        const altura = 1 + esc.altitud_km / RADIO_TIERRA_KM;
        const radioRegion = grad(esc.radio_region_km / RADIO_TIERRA_KM);
        const evalMostrada = (modo === "inicial" ? res.inicial : res.final).evaluacion;

        // Regiones de interés, coloreadas según la evaluación mostrada
        for (const r of esc.regiones) {
            const ev = evalMostrada.regiones.find((x) => x.id === r.id);
            const color = ev.cubierta ? COLORES.cubierta : ev.cobertura > 0 ? COLORES.parcial : COLORES.descubierta;
            this.capas.regiones.add(circuloSobreEsfera(r.lat, r.lon, radioRegion, ALTURA.region, color, 0.75));
            this.capas.etiquetas.add(etiqueta(`${r.nombre.split(",")[0]} · ${Math.round(ev.cobertura * 100)}%`,
                "", aVector(r.lat, r.lon, 1.02)));
        }

        // Zonas restringidas por desechos
        for (const z of esc.zonas_restringidas) {
            this.capas.zonas.add(circuloSobreEsfera(z.lat, z.lon, z.radio_grados, ALTURA.zona, COLORES.desechos, 0.22));
            // etiqueta en el borde norte de la zona, para no tapar regiones
            this.capas.zonas.add(etiqueta(z.nombre, "zona", aVector(Math.min(z.lat + z.radio_grados * 0.8, 89), z.lon, 1.02)));
        }

        // Objetos ocupados: zona de exclusión + el objeto en órbita
        for (const o of esc.objetos_ocupados) {
            this.capas.ocupados.add(circuloSobreEsfera(o.lat, o.lon, o.radio_grados, ALTURA.zona, COLORES.ocupado, 0.28));
            const cubo = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.035, 0.035),
                new THREE.MeshPhongMaterial({ color: COLORES.ocupado }));
            cubo.position.copy(aVector(o.lat, o.lon, altura));
            this.capas.ocupados.add(cubo);
            this.capas.ocupados.add(this._linea(aVector(o.lat, o.lon, 1), cubo.position, COLORES.ocupado, 0.6));
            this.capas.ocupados.add(etiqueta(o.nombre, "obj", cubo.position, true));
        }

        // Satélites
        const conjuntos = modo === "ambas"
            ? [[res.inicial, COLORES.inicial, "ini", 0.35], [res.final, COLORES.satelite, "sat", 1]]
            : [[modo === "inicial" ? res.inicial : res.final, COLORES.satelite, "sat", 1]];

        for (const [conf, color, clase, opac] of conjuntos) {
            const invasores = new Set(conf.evaluacion.violaciones.map((v) => v.satelite));
            for (const s of conf.satelites) {
                const posicion = aVector(s.lat, s.lon, altura);
                const malo = invasores.has(s.id);
                const c = malo ? COLORES.descubierta : color;
                const esfera = new THREE.Mesh(new THREE.SphereGeometry(0.022, 16, 12),
                    new THREE.MeshBasicMaterial({ color: c, transparent: opac < 1, opacity: opac }));
                esfera.position.copy(posicion);
                this.capas.satelites.add(esfera);
                this.capas.satelites.add(this._linea(aVector(s.lat, s.lon, 1), posicion, c, 0.5 * opac));
                this.capas.huellas.add(circuloSobreEsfera(s.lat, s.lon, esc.radio_vision_grados, ALTURA.huella, c, 0.12 * opac));
                const prefijo = clase === "ini" ? "ini " : "S";
                this.capas.etiquetas.add(etiqueta(`${prefijo}${s.id}${malo ? " ⚠" : ""}`, clase, posicion, true));
            }
        }
    }

    _linea(a, b, color, opacidad) {
        return new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]),
            new THREE.LineBasicMaterial({ color, transparent: true, opacity: opacidad }));
    }

    verCapa(nombre, visible) {
        this.capas[nombre].visible = visible;
        if (nombre === "etiquetas") this.renderEtq.domElement.style.display = visible ? "" : "none";
    }

    girar(activo) { this.controles.autoRotate = activo; }

    /** Centra la cámara sobre una latitud/longitud. */
    mirarA(lat, lon) {
        const d = this.camara.position.length();
        this.camara.position.copy(aVector(lat, lon, d));
    }

    _ajustarTamano() {
        const w = this.contenedor.clientWidth, h = this.contenedor.clientHeight;
        this.camara.aspect = w / h;
        this.camara.updateProjectionMatrix();
        this.render3d.setSize(w, h);
        this.renderEtq.setSize(w, h);
    }

    /** Oculta las etiquetas que quedan detrás del globo o en capas apagadas. */
    _actualizarEtiquetas() {
        const haciaCamara = this.camara.position.clone().normalize();
        this.escena.traverse((o) => {
            if (!o.isCSS2DObject) return;
            let visible = o.position.clone().normalize().dot(haciaCamara) > 0.15;
            for (let p = o.parent; p; p = p.parent) if (!p.visible) visible = false;
            o.visible = visible;
        });
    }

    _animar() {
        requestAnimationFrame(() => this._animar());
        this.controles.update();
        this._actualizarEtiquetas();
        this.render3d.render(this.escena, this.camara);
        this.renderEtq.render(this.escena, this.camara);
    }
}