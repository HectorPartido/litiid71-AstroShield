"""Interfaz de línea de comandos de AstroShield.

Ejemplos:
  python -m astroshield.cli run --escenario config/escenarios/base.json
  python -m astroshield.cli run --escenario config/escenarios/base.json --semilla 7 --generaciones 300
  python -m astroshield.cli reevaluar --resultado results/base_s42.json --escenario config/escenarios/prioridades_cambiadas.json

Cada `run` guarda en results/:
  <escenario>_s<semilla>.json  -> resultado completo (lo lee la visualización 3D)
  <escenario>_s<semilla>.csv   -> historial por generación (para gráficas)
  index.json                   -> lista de ejecuciones disponibles para el visor

Responsable: Gildardo Emmanuel González García
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from .escenario import cargar_escenario
from .fitness import Evaluador
from .ga import AlgoritmoEvolutivo

RAIZ = Path(__file__).resolve().parents[2]
CARPETA_RESULTADOS = RAIZ / "results"


def guardar_resultado(res: dict, nombre: str, carpeta: Path = CARPETA_RESULTADOS) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_json = carpeta / f"{nombre}.json"
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)

    with open(carpeta / f"{nombre}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res["historial"][0].keys()))
        w.writeheader()
        w.writerows(res["historial"])

    actualizar_indice(carpeta)
    return ruta_json


def actualizar_indice(carpeta: Path = CARPETA_RESULTADOS) -> None:
    """Reconstruye results/index.json con todas las ejecuciones guardadas."""
    entradas = []
    for ruta in sorted(carpeta.glob("*.json")):
        if ruta.name == "index.json":
            continue
        try:
            with open(ruta, encoding="utf-8") as f:
                r = json.load(f)
            fin = r["final"]["evaluacion"]
            entradas.append({
                "archivo": ruta.name,
                "escenario": r["escenario"]["nombre"],
                "semilla": r["semilla"],
                "fitness": fin["fitness"],
                "valida": fin["valida"],
                "regiones_cubiertas": fin["regiones_cubiertas"],
            })
        except (KeyError, json.JSONDecodeError):
            continue
    with open(carpeta / "index.json", "w", encoding="utf-8") as f:
        json.dump(entradas, f, ensure_ascii=False, indent=1)


def imprimir_resumen(res: dict) -> None:
    ini = res["inicial"]["evaluacion"]
    fin = res["final"]["evaluacion"]
    print()
    print(f"Escenario: {res['escenario']['nombre']}   semilla: {res['semilla']}   "
          f"generaciones: {res['generaciones_ejecutadas']}   tiempo: {res['tiempo_s']} s")
    print(f"{'':22s}{'INICIAL':>12s}{'FINAL':>12s}")
    print(f"{'Fitness':22s}{ini['fitness']:12.4f}{fin['fitness']:12.4f}")
    print(f"{'Cobertura ponderada':22s}{ini['cobertura_ponderada']:12.4f}{fin['cobertura_ponderada']:12.4f}")
    print(f"{'Redundancia Alta':22s}{ini['redundancia_alta']:12.4f}{fin['redundancia_alta']:12.4f}")
    print(f"{'Regiones cubiertas':22s}{ini['regiones_cubiertas']:12d}{fin['regiones_cubiertas']:12d}")
    print(f"{'Válida':22s}{str(ini['valida']):>12s}{str(fin['valida']):>12s}")
    print(f"{'Violación (grados)':22s}{ini['violacion']:12.3f}{fin['violacion']:12.3f}")
    print()
    print(f"{'Región':32s}{'Prioridad':>10s}{'Cobertura':>11s}{'Cubierta':>10s}  Satélites")
    for r in fin["regiones"]:
        print(f"{r['nombre']:32s}{r['prioridad']:>10s}{r['cobertura']:11.0%}"
              f"{'sí' if r['cubierta'] else 'NO':>10s}  {r['satelites_que_ven']}")
    if res["gen_suficiente"] is not None:
        print(f"\nSolución 'suficientemente buena' alcanzada en la generación {res['gen_suficiente']}.")
    else:
        print("\nNo se alcanzó el criterio de 'suficientemente buena'.")
    if not fin["valida"]:
        print("ATENCIÓN: la mejor configuración encontrada NO es válida:")
        for v in fin["violaciones"]:
            print("   ", v)


def comando_run(args) -> dict:
    esc = cargar_escenario(args.escenario)
    if args.satelites:
        esc.num_satelites = args.satelites
    ae = AlgoritmoEvolutivo(
        esc,
        semilla=args.semilla,
        generaciones=args.generaciones,
        poblacion=args.poblacion,
        prob_mutacion=args.prob_mutacion,
        sigma_mutacion=args.sigma,
    )
    res = ae.ejecutar(verbose=not args.silencioso)
    nombre = args.nombre or f"{esc.nombre}_s{res['semilla']}"
    ruta = guardar_resultado(res, nombre)
    if not args.silencioso:
        imprimir_resumen(res)
        print(f"\nGuardado en {ruta.relative_to(RAIZ)} (+ .csv con el historial)")
    return res


def comando_reevaluar(args) -> dict:
    """Punto 3.3: ¿una configuración vieja sigue siendo válida con condiciones nuevas?"""
    with open(args.resultado, encoding="utf-8") as f:
        viejo = json.load(f)
    sats = np.array([[s["lat"], s["lon"]] for s in viejo["final"]["satelites"]])
    esc_nuevo = cargar_escenario(args.escenario)
    ev = Evaluador(esc_nuevo).evaluar(sats, detalle=True)
    antes = viejo["final"]["evaluacion"]

    print(f"\nConfiguración de: {args.resultado} (escenario '{viejo['escenario']['nombre']}')")
    print(f"Evaluada bajo:    {args.escenario} (escenario '{esc_nuevo.nombre}')\n")
    print(f"{'':22s}{'ANTES':>12s}{'AHORA':>12s}")
    print(f"{'Fitness':22s}{antes['fitness']:12.4f}{ev.fitness:12.4f}")
    print(f"{'Cobertura ponderada':22s}{antes['cobertura_ponderada']:12.4f}{ev.cobertura_ponderada:12.4f}")
    print(f"{'Regiones cubiertas':22s}{antes['regiones_cubiertas']:12d}{ev.regiones_cubiertas:12d}")
    print(f"{'Válida':22s}{str(antes['valida']):>12s}{str(ev.valida):>12s}")
    if not ev.valida:
        print("\nLa configuración anterior YA NO ES VÁLIDA con las nuevas condiciones:")
        for v in ev.violaciones:
            print("   ", v)
        print("Se debe volver a ejecutar el algoritmo con el escenario nuevo.")
    else:
        print("\nLa configuración anterior sigue siendo válida con las nuevas condiciones.")
    salida = {"origen": args.resultado, "escenario_nuevo": esc_nuevo.nombre,
              "antes": antes, "ahora": ev.a_dict()}
    if args.guardar:
        CARPETA_RESULTADOS.mkdir(exist_ok=True)
        destino = CARPETA_RESULTADOS / "reevaluaciones"
        destino.mkdir(exist_ok=True)
        ruta = destino / f"{Path(args.resultado).stem}_bajo_{esc_nuevo.nombre}.json"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(salida, f, ensure_ascii=False, indent=1)
        print(f"Guardado en {ruta.relative_to(RAIZ)}")
    return salida


def construir_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="astroshield", description="AstroShield: constelación evolutiva")
    sub = ap.add_subparsers(dest="comando", required=True)

    r = sub.add_parser("run", help="Ejecuta el algoritmo evolutivo")
    r.add_argument("--escenario", default=str(RAIZ / "config/escenarios/base.json"))
    r.add_argument("--semilla", type=int)
    r.add_argument("--generaciones", type=int)
    r.add_argument("--poblacion", type=int)
    r.add_argument("--prob-mutacion", type=float, dest="prob_mutacion")
    r.add_argument("--sigma", type=float, help="Desviación de la mutación en grados")
    r.add_argument("--satelites", type=int, help="Cambia el número de satélites")
    r.add_argument("--nombre", help="Nombre del archivo de salida (sin extensión)")
    r.add_argument("--silencioso", action="store_true")
    r.set_defaults(func=comando_run)

    e = sub.add_parser("reevaluar", help="Evalúa una configuración guardada bajo otro escenario")
    e.add_argument("--resultado", required=True)
    e.add_argument("--escenario", required=True)
    e.add_argument("--guardar", action="store_true")
    e.set_defaults(func=comando_reevaluar)
    return ap


def main(argv=None):
    args = construir_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()