"""Batería de pruebas y experimentos de AstroShield (Entregables 3 y 4).

Corre TODAS las pruebas pedidas en la actividad y genera la evidencia:

  results/<escenario>_s42.json/.csv    ejecuciones oficiales (las usa el visor 3D)
  results/reevaluaciones/*.json        cambio de condiciones (3.3)
  results/experimentos/*.csv           tablas con todas las corridas
  results/experimentos/resumen.md      tablas listas para pegar en los documentos
  docs/figuras/*.png                   gráficas

Pruebas:
  P1 Escenario inicial            base, semilla 42
  P2 Evolución                    historial de base, semilla 42
  P3 Zonas restringidas           margen mínimo a cada zona en TODAS las soluciones
  P4 Posiciones ocupadas          ídem para los objetos A y B
  P5 Espacio reducido             escenario `reducido`, 10 semillas
  P6 Condición inviable           escenario `inviable`, 10 semillas
  P7 Variación de la ejecución    escenario `base`, 10 semillas
  P8 Prueba propia A              ¿sirve la mutación de reubicación? (ablación)
  P9 Prueba propia B              ¿cuántos satélites hacen falta? (4 a 8)
  P10 Cambio de condiciones 3.3   reevaluar base_s42 bajo condiciones nuevas
  P11 Prueba propia C             calibración del peso de redundancia
  P12 Prueba propia D             criterio de paro: paciencia 80 vs 150

Uso (desde la raíz del repo; tarda de 4 a 15 minutos según los núcleos del CPU):
    python experiments/correr_pruebas.py

Responsable: Anthony Oziel Ramos López
"""
from __future__ import annotations

import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from astroshield import fitness as fit_mod
from astroshield.cli import guardar_resultado
from astroshield.escenario import cargar_escenario
from astroshield.fitness import Evaluador
from astroshield.ga import AlgoritmoEvolutivo
from astroshield.geo import distancia_angular

RAIZ = Path(__file__).resolve().parents[1]
ESC = RAIZ / "config" / "escenarios"
SALIDA = RAIZ / "results" / "experimentos"
FIGURAS = RAIZ / "docs" / "figuras"
SEMILLAS = list(range(1, 11))          # 10 semillas para comparar ejecuciones
SEMILLAS_BARRIDO = list(range(1, 6))   # 5 semillas por cada número de satélites
OFICIALES = ["base", "sin_restricciones", "reducido", "inviable", "prioridades_cambiadas"]

# P11: peso actual (el que está en fitness.py) contra un peso alternativo
PESO_ACTUAL = fit_mod.PESO_REDUNDANCIA
PESO_ALTERNATIVO = 0.10 if abs(PESO_ACTUAL - 0.10) > 1e-9 else 0.15


# ---------------------------------------------------------------- utilidades

def margenes(sats: np.ndarray, esc) -> dict:
    """Distancia (grados) del satélite más cercano al BORDE de cada zona.
    Positivo = afuera (válido). Negativo = invade."""
    res = {}
    for z in esc.zonas:
        d = distancia_angular(sats[:, 0], sats[:, 1], z.lat, z.lon)
        res[z.id] = round(float(np.min(d) - z.radio_grados), 3)
    return res


def trabajo(tarea: dict) -> dict:
    """Corre UNA ejecución del algoritmo. Se ejecuta en paralelo."""
    from astroshield import fitness as fm   # copia del módulo en ESTE proceso

    esc = cargar_escenario(ESC / f"{tarea['escenario']}.json")
    if tarea.get("satelites"):
        esc.num_satelites = tarea["satelites"]

    # Ajustes a constantes del módulo fitness (p. ej. PESO_REDUNDANCIA).
    # Se guardan y restauran para que no "se peguen" a la siguiente tarea del worker.
    ajustes = tarea.get("ajustes", {})
    originales = {k: getattr(fm, k) for k in ajustes}
    try:
        for nombre, valor in ajustes.items():
            setattr(fm, nombre, valor)
        res = AlgoritmoEvolutivo(esc, semilla=tarea["semilla"], **tarea.get("cambios", {})).ejecutar()
    finally:
        for nombre, valor in originales.items():
            setattr(fm, nombre, valor)

    fin = res["final"]["evaluacion"]
    sats = np.array([[s["lat"], s["lon"]] for s in res["final"]["satelites"]])
    fila = {
        "experimento": tarea["experimento"],
        "escenario": tarea["escenario"],
        "variante": tarea.get("variante", ""),
        "satelites": esc.num_satelites,
        "semilla": tarea["semilla"],
        "fitness_inicial": res["inicial"]["evaluacion"]["fitness"],
        "fitness_final": fin["fitness"],
        "valida": fin["valida"],
        "violacion": fin["violacion"],
        "cobertura_ponderada": fin["cobertura_ponderada"],
        "redundancia_alta": fin["redundancia_alta"],
        "regiones_cubiertas": fin["regiones_cubiertas"],
        "gen_suficiente": res["gen_suficiente"],
        "generaciones": res["generaciones_ejecutadas"],
        "tiempo_s": res["tiempo_s"],
    }
    for r in fin["regiones"]:
        fila[f"cob_{r['id']}"] = r["cobertura"]
    for zid, m in margenes(sats, esc).items():
        fila[f"margen_{zid}"] = m
    return {"fila": fila, "curva": [g["mejor_fitness"] for g in res["historial"]],
            "sats": sats.tolist(), "res": res if tarea.get("guardar") else None}


def correr_en_paralelo(tareas: list) -> list:
    hilos = max(1, (os.cpu_count() or 2) - 1)
    with ProcessPoolExecutor(max_workers=hilos) as ex:
        return list(ex.map(trabajo, tareas))


def guardar_csv(filas: list, nombre: str) -> None:
    claves = []
    for f in filas:
        claves += [k for k in f if k not in claves]
    with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=claves)
        w.writeheader()
        w.writerows(filas)


def estad(valores) -> str:
    v = np.array([x for x in valores if x is not None], dtype=float)
    if len(v) == 0:
        return "—"
    return f"{v.mean():.4f} ± {v.std():.4f} (mín {v.min():.4f}, máx {v.max():.4f})"


def tabla_md(encabezados: list, filas: list) -> str:
    out = "| " + " | ".join(encabezados) + " |\n|" + "---|" * len(encabezados) + "\n"
    for f in filas:
        out += "| " + " | ".join(str(x) for x in f) + " |\n"
    return out


# ---------------------------------------------------------------- principal

def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    FIGURAS.mkdir(parents=True, exist_ok=True)
    md = ["# Resumen de pruebas y experimentos (generado automáticamente)\n",
          "Generado por `python experiments/correr_pruebas.py`. No editar a mano.\n"]

    # ---------- ejecuciones oficiales (semilla 42) ----------
    print("1/5 Ejecuciones oficiales (semilla 42)...")
    oficiales = correr_en_paralelo([
        {"experimento": "oficial", "escenario": e, "semilla": 42, "guardar": True} for e in OFICIALES])
    for o in oficiales:
        guardar_resultado(o["res"], f"{o['fila']['escenario']}_s42")

    # ---------- multi-semilla por escenario ----------
    print("2/5 Diez semillas por escenario...")
    multi = correr_en_paralelo([
        {"experimento": "semillas", "escenario": e, "semilla": s}
        for e in ["base", "sin_restricciones", "reducido", "inviable"] for s in SEMILLAS])
    guardar_csv([m["fila"] for m in multi], "semillas.csv")

    # ---------- P8: ablación de la mutación de reubicación ----------
    print("3/5 Ablación: sin mutación de reubicación...")
    ablacion = correr_en_paralelo([
        {"experimento": "ablacion", "escenario": "base", "variante": "sin_reubicacion",
         "semilla": s, "cambios": {"prob_reubicar": 0.0}} for s in SEMILLAS])
    guardar_csv([a["fila"] for a in ablacion], "ablacion_reubicacion.csv")

    # ---------- P9: número de satélites ----------
    print("4/5 Barrido del número de satélites...")
    barrido = correr_en_paralelo([
        {"experimento": "barrido", "escenario": "base", "satelites": n, "semilla": s}
        for n in [4, 5, 6, 7, 8] for s in SEMILLAS_BARRIDO])
    guardar_csv([b["fila"] for b in barrido], "barrido_satelites.csv")

    # ---------- P11: calibración del peso de redundancia ----------
    print(f"     Calibración: peso de redundancia {PESO_ALTERNATIVO} (actual: {PESO_ACTUAL})...")
    calibracion = correr_en_paralelo([
        {"experimento": "calibracion", "escenario": "base",
         "variante": f"peso_redundancia_{PESO_ALTERNATIVO}",
         "semilla": s, "ajustes": {"PESO_REDUNDANCIA": PESO_ALTERNATIVO}} for s in SEMILLAS])
    guardar_csv([c["fila"] for c in calibracion], "calibracion_peso_redundancia.csv")

    # ---------- P12: criterio de paro ----------
    print("     Criterio de paro: paciencia 80 / 200 generaciones...")
    paro = correr_en_paralelo([
        {"experimento": "paro", "escenario": "base", "variante": "paciencia_80",
         "semilla": s, "cambios": {"paciencia": 80, "generaciones": 200}} for s in SEMILLAS + [42]])
    guardar_csv([c["fila"] for c in paro], "criterio_paro.csv")

    print("5/5 Validaciones, reevaluaciones y gráficas...")
    por_esc = {e: [m for m in multi if m["fila"]["escenario"] == e]
               for e in ["base", "sin_restricciones", "reducido", "inviable"]}
    base_of = next(o for o in oficiales if o["fila"]["escenario"] == "base")["res"]

    # ---------- P1 ----------
    fin = base_of["final"]["evaluacion"]
    md.append("## P1. Escenario inicial (base, semilla 42)\n")
    md.append(f"- Fitness inicial → final: **{base_of['inicial']['evaluacion']['fitness']:.4f} → {fin['fitness']:.4f}**\n"
              f"- Regiones cubiertas: **{fin['regiones_cubiertas']}/6**, válida: **{fin['valida']}**, "
              f"generación en que fue suficientemente buena: **{base_of['gen_suficiente']}**, "
              f"generaciones ejecutadas: {base_of['generaciones_ejecutadas']}\n")
    md.append(tabla_md(["Región", "Prioridad", "Cobertura", "Redundancia", "Cubierta", "Satélites"],
                       [[r["nombre"], r["prioridad"], f"{r['cobertura']:.0%}", f"{r['redundancia']:.0%}",
                         "sí" if r["cubierta"] else "NO", ", ".join(f"S{i}" for i in r["satelites_que_ven"])]
                        for r in fin["regiones"]]))
    md.append("\n" + tabla_md(["Satélite", "Latitud", "Longitud"],
                              [[f"S{s['id']}", s["lat"], s["lon"]] for s in base_of["final"]["satelites"]]))

    # ---------- P2 ----------
    h = base_of["historial"]
    # hitos: generación 0, cada vez que mejoró el mejor, y la última
    hitos = [h[0]] + [g for a, g in zip(h, h[1:]) if g["mejor_fitness"] > a["mejor_fitness"]]
    if h[-1] is not hitos[-1]:
        hitos.append(h[-1])
    md.append("\n## P2. Evolución (base, semilla 42)\n")
    md.append(tabla_md(["Gen", "Mejor", "Promedio", "Peor", "% válidos", "Regiones (mejor)", "Diversidad (°)"],
                       [[g["generacion"], f"{g['mejor_fitness']:.4f}", f"{g['promedio_fitness']:.4f}",
                         f"{g['peor_fitness']:.4f}", f"{g['pct_validos']:.0%}", g["regiones_cubiertas_mejor"],
                         f"{g['diversidad']:.1f}"] for g in hitos]))

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6.5), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    gens = [g["generacion"] for g in h]
    a1.plot(gens, [g["mejor_fitness"] for g in h], label="Mejor", lw=2.2, color="#1f77b4")
    a1.plot(gens, [g["promedio_fitness"] for g in h], label="Promedio", lw=1.5, color="#9467bd")
    a1.plot(gens, [g["peor_fitness"] for g in h], label="Peor", lw=1, color="#bbbbbb")
    if base_of["gen_suficiente"] is not None:
        a1.axvline(base_of["gen_suficiente"], ls="--", color="#2ca02c", label="Suficientemente buena")
    a1.set_ylabel("Fitness"); a1.set_ylim(-0.02, 1.05); a1.legend(loc="lower right"); a1.grid(alpha=0.3)
    a1.set_title("P2. Evolución del fitness — escenario base, semilla 42")
    a2.plot(gens, [g["pct_validos"] * 100 for g in h], color="#d62728", label="% configuraciones válidas")
    a2b = a2.twinx()
    a2b.plot(gens, [g["diversidad"] for g in h], color="#7f7f7f", label="Diversidad (°)")
    a2.set_ylabel("% válidas"); a2b.set_ylabel("Diversidad (°)"); a2.set_xlabel("Generación")
    a2.legend(loc="center right"); a2b.legend(loc="upper right"); a2.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(FIGURAS / "p2_evolucion_base.png", dpi=130); plt.close(fig)

    # ---------- P3 y P4: restricciones en TODAS las soluciones ----------
    todas = oficiales + multi + ablacion + barrido + calibracion + paro
    con_restricciones = [t for t in todas if t["fila"]["escenario"] != "sin_restricciones"]
    esc_base = cargar_escenario(ESC / "base.json")
    md.append("\n## P3 y P4. Zonas restringidas y posiciones ocupadas\n")
    md.append(f"Se revisaron **{len(con_restricciones)} soluciones finales** de todos los experimentos que tienen "
              "restricciones. *Margen* = distancia del satélite más cercano al borde de la zona "
              "(positivo = afuera).\n\n")
    filas_zona = []
    for z in esc_base.zonas:
        ms = [t["fila"][f"margen_{z.id}"] for t in con_restricciones]
        filas_zona.append([z.nombre, z.tipo, f"{z.radio_grados}°", f"{min(ms):.2f}°",
                           sum(1 for m in ms if m < 0)])
    md.append(tabla_md(["Zona", "Tipo", "Radio", "Margen mínimo observado", "Soluciones que la invaden"], filas_zona))
    invalidas = [t for t in con_restricciones if not t["fila"]["valida"]]
    md.append(f"\nSoluciones finales inválidas: **{len(invalidas)} de {len(con_restricciones)}**.\n")

    # efecto de las restricciones: soluciones SIN restricciones evaluadas CON restricciones
    ev_base = Evaluador(esc_base)
    rev = [ev_base.evaluar(np.array(t["sats"]), detalle=True) for t in por_esc["sin_restricciones"]]
    n_inv = sum(not e.valida for e in rev)
    md.append(f"\n**Contraprueba:** de las 10 soluciones obtenidas *sin* restricciones, **{n_inv}** "
              "serían inválidas si se aplicaran las restricciones del escenario base:\n\n")
    md.append(tabla_md(["Semilla", "Válida con restricciones", "Zonas invadidas"],
                       [[t["fila"]["semilla"], "sí" if e.valida else "NO",
                         ", ".join(sorted({v["zona"] for v in e.violaciones})) or "—"]
                        for t, e in zip(por_esc["sin_restricciones"], rev)]))

    # ---------- P5, P6, P7: comparación de escenarios con 10 semillas ----------
    md.append("\n## P5, P6 y P7. Diez semillas por escenario\n")
    filas = []
    for e, corr in por_esc.items():
        f = [c["fila"] for c in corr]
        suf = [x["gen_suficiente"] for x in f if x["gen_suficiente"] is not None]
        filas.append([e, estad([x["fitness_final"] for x in f]),
                      f"{np.mean([x['regiones_cubiertas'] for x in f]):.1f}",
                      sum(x["regiones_cubiertas"] == 6 for x in f),
                      sum(x["valida"] for x in f),
                      f"{len(suf)}/10" + (f" (gen. media {np.mean(suf):.0f})" if suf else ""),
                      f"{np.mean([x['generaciones'] for x in f]):.0f}"])
    md.append(tabla_md(["Escenario", "Fitness final (media ± desv.)", "Regiones prom.", "Corridas con 6/6",
                        "Válidas", "Suficientemente buena", "Generaciones prom."], filas))

    md.append("\n### Detalle por semilla — escenario base (P7)\n")
    md.append(tabla_md(["Semilla", "Fitness", "Regiones", "Gen. suficiente", "Generaciones", "Región sin cubrir"],
                       [[c["fila"]["semilla"], f"{c['fila']['fitness_final']:.4f}", c["fila"]["regiones_cubiertas"],
                         c["fila"]["gen_suficiente"] if c["fila"]["gen_suficiente"] is not None else "—",
                         c["fila"]["generaciones"],
                         ", ".join(k[4:] for k, v in c["fila"].items() if k.startswith("cob_") and v < 0.9) or "—"]
                        for c in por_esc["base"]]))

    md.append("\n### Cobertura promedio por región (10 semillas)\n")
    regiones = [r.id for r in esc_base.regiones]
    md.append(tabla_md(["Escenario"] + regiones,
                       [[e] + [f"{np.mean([c['fila'][f'cob_{r}'] for c in corr]):.0%}" for r in regiones]
                        for e, corr in por_esc.items()]))

    # Máximo teórico en el escenario inviable: Yucatán imposible
    total = sum(esc_base.peso(r) for r in esc_base.regiones)
    wr = fit_mod.PESO_REDUNDANCIA            # peso real usado en las corridas
    max_inviable = (1 - wr) * (total - 3) / total + wr * 0.5
    fit_inv = [c["fila"]["fitness_final"] for c in por_esc["inviable"]]
    md.append(f"\n**P6. Máximo teórico del escenario inviable:** si Yucatán (peso 3 de {total:.0f}) no se puede ver, "
              f"el mejor fitness posible es {1 - wr:.2f}·{total - 3:.0f}/{total:.0f} + {wr:.2f}·0.5 = **{max_inviable:.4f}** "
              "(Amazonía sí puede tener respaldo, Yucatán no). "
              f"{sum(abs(x - max_inviable) < 1e-4 for x in fit_inv)} de 10 corridas lo alcanzaron "
              f"(máximo observado {max(fit_inv):.4f}).\n")

    # Figuras de comparación
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for c in por_esc["base"]:
        ax.plot(c["curva"], lw=1.3, label=f"semilla {c['fila']['semilla']}")
    ax.set_xlabel("Generación"); ax.set_ylabel("Mejor fitness"); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
    ax.set_title("P7. Mejor fitness por generación — 10 semillas, escenario base")
    ax.legend(ncol=5, fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(FIGURAS / "p7_variacion_semillas.png", dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    nombres = list(por_esc)
    datos = [[c["fila"]["fitness_final"] for c in por_esc[e]] for e in nombres]
    ax.boxplot(datos, showmeans=True)
    ax.set_xticks(range(1, len(nombres) + 1), nombres)
    for i, d in enumerate(datos, 1):
        ax.scatter(np.random.default_rng(i).normal(i, 0.04, len(d)), d, s=14, alpha=0.6, color="#1f77b4")
    ax.axhline(max_inviable, ls=":", color="#d62728", label=f"máximo teórico inviable ({max_inviable:.3f})")
    ax.set_ylabel("Fitness final"); ax.grid(alpha=0.3, axis="y"); ax.legend(loc="lower left")
    ax.set_title("P5-P7. Fitness final por escenario (10 semillas cada uno)")
    fig.tight_layout(); fig.savefig(FIGURAS / "p5_p7_escenarios.png", dpi=130); plt.close(fig)

    # ---------- P8: ablación ----------
    con = [c["fila"] for c in por_esc["base"]]
    sin = [a["fila"] for a in ablacion]
    md.append("\n## P8. Prueba propia A — ¿sirve la mutación de reubicación?\n")
    md.append(tabla_md(["Variante", "Fitness final", "Regiones prom.", "Corridas con 6/6", "Suficientemente buena"],
                       [["Con reubicación (0.03)", estad([x["fitness_final"] for x in con]),
                         f"{np.mean([x['regiones_cubiertas'] for x in con]):.1f}",
                         sum(x["regiones_cubiertas"] == 6 for x in con),
                         sum(x["gen_suficiente"] is not None for x in con)],
                        ["Sin reubicación (0.0)", estad([x["fitness_final"] for x in sin]),
                         f"{np.mean([x['regiones_cubiertas'] for x in sin]):.1f}",
                         sum(x["regiones_cubiertas"] == 6 for x in sin),
                         sum(x["gen_suficiente"] is not None for x in sin)]]))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot([[x["fitness_final"] for x in con], [x["fitness_final"] for x in sin]], showmeans=True)
    ax.set_xticks([1, 2], ["con reubicación", "sin reubicación"])
    ax.set_ylabel("Fitness final"); ax.grid(alpha=0.3, axis="y")
    ax.set_title("P8. Ablación de la mutación de reubicación (10 semillas)")
    fig.tight_layout(); fig.savefig(FIGURAS / "p8_ablacion_reubicacion.png", dpi=130); plt.close(fig)

    # ---------- P9: número de satélites ----------
    md.append("\n## P9. Prueba propia B — ¿cuántos satélites hacen falta?\n")
    filas, xs, med, regs = [], [], [], []
    for n in [4, 5, 6, 7, 8]:
        f = [b["fila"] for b in barrido if b["fila"]["satelites"] == n]
        xs.append(n); med.append(np.mean([x["fitness_final"] for x in f]))
        regs.append(np.mean([x["regiones_cubiertas"] for x in f]))
        filas.append([n, estad([x["fitness_final"] for x in f]), f"{regs[-1]:.1f}",
                      f"{np.mean([x['redundancia_alta'] for x in f]):.2f}",
                      sum(x["gen_suficiente"] is not None for x in f)])
    md.append(tabla_md(["Satélites", "Fitness final", "Regiones prom.", "Redundancia Alta prom.",
                        "Suficientemente buena (de 5)"], filas))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, med, "o-", lw=2, label="Fitness final promedio")
    ax.set_xlabel("Número de satélites"); ax.set_ylabel("Fitness"); ax.set_ylim(0, 1.05); ax.grid(alpha=0.3)
    ax2 = ax.twinx(); ax2.plot(xs, regs, "s--", color="#ff7f0e", label="Regiones cubiertas")
    ax2.set_ylabel("Regiones cubiertas (de 6)"); ax2.set_ylim(0, 6.3)
    ax.legend(loc="upper left"); ax2.legend(loc="lower right")
    ax.set_title("P9. Efecto del número de satélites (5 semillas c/u)")
    fig.tight_layout(); fig.savefig(FIGURAS / "p9_num_satelites.png", dpi=130); plt.close(fig)

    # ---------- P10: cambio de condiciones (3.3) ----------
    md.append("\n## P10. Cambio de condiciones (3.3): ¿sigue siendo válida la solución de base_s42?\n")
    sats42 = np.array([[s["lat"], s["lon"]] for s in base_of["final"]["satelites"]])
    destino = RAIZ / "results" / "reevaluaciones"
    destino.mkdir(exist_ok=True)
    filas = []
    for e in ["prioridades_cambiadas", "reducido", "inviable"]:
        esc_n = cargar_escenario(ESC / f"{e}.json")
        ev = Evaluador(esc_n).evaluar(sats42, detalle=True)
        nuevo = next(o for o in oficiales if o["fila"]["escenario"] == e)["fila"]
        with open(destino / f"base_s42_bajo_{e}.json", "w", encoding="utf-8") as fh:
            json.dump({"origen": "results/base_s42.json", "escenario_nuevo": e,
                       "antes": fin, "ahora": ev.a_dict()}, fh, ensure_ascii=False, indent=1)
        filas.append([e, f"{ev.fitness:.4f}", ev.regiones_cubiertas, "sí" if ev.valida else "NO",
                      ", ".join(f"S{v['satelite']}→{v['zona']}" for v in ev.violaciones) or "—",
                      f"{nuevo['fitness_final']:.4f} ({nuevo['regiones_cubiertas']}/6)"])
    md.append(tabla_md(["Escenario nuevo", "Fitness de la sol. vieja", "Regiones", "¿Válida?",
                        "Violaciones", "Fitness al re-ejecutar (s42)"], filas))

    # ---------- P11 ----------
    c_alt = [c["fila"] for c in calibracion]
    c_act = [c["fila"] for c in por_esc["base"]]
    md.append("\n## P11. Prueba propia C — calibración del peso de redundancia\n")
    md.append("Mismo escenario base y mismas 10 semillas; solo cambia `PESO_REDUNDANCIA`. "
              "Se comparan métricas de cobertura (el fitness no es comparable entre pesos distintos).\n")
    md.append(tabla_md(["PESO_REDUNDANCIA", "Corridas con 6/6", "Corridas que abandonan Australia",
                        "Cobertura prom. Australia", "Redundancia Alta prom.", "Suficientemente buena"],
                       [[w_, sum(x["regiones_cubiertas"] == 6 for x in f_),
                         sum(x["cob_australia"] < 0.9 for x in f_),
                         f"{np.mean([x['cob_australia'] for x in f_]):.0%}",
                         f"{np.mean([x['redundancia_alta'] for x in f_]):.2f}",
                         sum(x["gen_suficiente"] is not None for x in f_)]
                        for w_, f_ in [(f"{PESO_ACTUAL} (actual en fitness.py)", c_act),
                                       (f"{PESO_ALTERNATIVO} (variante)", c_alt)]]))

    # ---------- P12 ----------
    p80 = {c["fila"]["semilla"]: c["fila"] for c in paro}
    p150 = {c["fila"]["semilla"]: c["fila"] for c in por_esc["base"]}
    p150[42] = next(o for o in oficiales if o["fila"]["escenario"] == "base")["fila"]
    md.append("\n## P12. Prueba propia D — criterio de paro (paciencia)\n")
    md.append("Mismas semillas; solo cambia cuántas generaciones sin mejora se toleran antes de detenerse.\n")
    md.append(tabla_md(["Semilla", "Paciencia 80: fitness (gen. al parar)", "Paciencia 150: fitness (gen. al parar)",
                        "¿Mejoró al esperar más?"],
                       [[s_, f"{p80[s_]['fitness_final']:.4f} ({p80[s_]['generaciones']})",
                         f"{p150[s_]['fitness_final']:.4f} ({p150[s_]['generaciones']})",
                         "sí" if p150[s_]["fitness_final"] > p80[s_]["fitness_final"] + 1e-9 else "no"]
                        for s_ in SEMILLAS + [42]]))

    (SALIDA / "resumen.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nListo. Resumen en {(SALIDA / 'resumen.md').relative_to(RAIZ)}; "
          f"figuras en {FIGURAS.relative_to(RAIZ)}/")


if __name__ == "__main__":
    main()