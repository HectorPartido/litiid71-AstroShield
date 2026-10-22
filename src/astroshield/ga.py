"""Algoritmo evolutivo (algoritmo genético con codificación real).

Individuo  = arreglo (n_satélites, 2) con [lat, lon] de cada satélite.
Ciclo por generación:
  1. Elitismo: los `elitismo` mejores pasan sin cambios.
  2. Selección por torneo de tamaño k (usando la regla de factibilidad).
  3. Cruza uniforme por satélite: cada satélite del hijo viene del padre 1
     o del padre 2 con probabilidad 1/2.
  4. Mutación: gaussiana (cada satélite, con prob. pm, se desplaza N(0, σ)
     grados) + reubicación (con prob. p_reubicar un satélite salta a un
     punto aleatorio del globo).
  5. Se evalúa la nueva población y se guarda el historial.
Paro: número máximo de generaciones o `paciencia` generaciones sin mejora.

Responsable: Gildardo Emmanuel González García
"""
from __future__ import annotations

import time

import numpy as np

from .fitness import Evaluador
from .geo import latitud_uniforme, normalizar
from .restricciones import clave_factibilidad


def poblacion_inicial(tam: int, n_sat: int, rng) -> list:
    """Configuraciones al azar repartidas uniformemente sobre la esfera.
    No se filtran las inválidas a propósito: así se demuestra que el algoritmo
    las corrige gracias al manejo de restricciones."""
    pob = []
    for _ in range(tam):
        lat = latitud_uniforme(rng, n_sat)
        lon = rng.uniform(-180.0, 180.0, n_sat)
        pob.append(np.column_stack([lat, lon]))
    return pob


def seleccion_torneo(claves: list, k: int, rng) -> int:
    """Escoge k individuos al azar y regresa el índice del mejor."""
    candidatos = rng.choice(len(claves), size=k, replace=False)
    return int(max(candidatos, key=lambda i: claves[i]))


def cruza_uniforme(p1: np.ndarray, p2: np.ndarray, rng) -> np.ndarray:
    mascara = rng.random(len(p1)) < 0.5
    hijo = np.where(mascara[:, None], p1, p2)
    return hijo.copy()


def mutar(ind: np.ndarray, pm: float, sigma: float, rng, p_reubicar: float = 0.0) -> np.ndarray:
    """Dos tipos de mutación:
    - Gaussiana (prob. pm por satélite): ajuste fino, mueve el satélite
      unos cuantos grados. Explota la zona donde ya está.
    - Reubicación (prob. p_reubicar por satélite): lo manda a un punto
      aleatorio del globo. Explora; evita que el algoritmo se estanque con
      regiones lejanas que ningún satélite alcanza.
    """
    hijo = ind.copy()
    cuales = rng.random(len(hijo)) < pm
    if cuales.any():
        hijo[cuales] += rng.normal(0.0, sigma, size=(int(cuales.sum()), 2))
    reubicar = rng.random(len(hijo)) < p_reubicar
    if reubicar.any():
        n = int(reubicar.sum())
        hijo[reubicar] = np.column_stack([latitud_uniforme(rng, n), rng.uniform(-180, 180, n)])
    lat, lon = normalizar(hijo[:, 0], hijo[:, 1])
    return np.column_stack([lat, lon])


def diversidad(pob: list) -> float:
    """Desviación estándar promedio (en grados) de las coordenadas de los
    satélites dentro de la población. Si baja mucho, la población ya
    convergió (todos los individuos se parecen) y explora poco."""
    arr = np.stack(pob)                       # (tam, n_sat, 2)
    return float(np.mean(np.std(arr, axis=0)))


def satelites_a_lista(ind: np.ndarray) -> list:
    return [{"id": i, "lat": round(float(a), 4), "lon": round(float(b), 4)}
            for i, (a, b) in enumerate(ind)]


class AlgoritmoEvolutivo:
    def __init__(self, escenario, **cambios_parametros):
        self.esc = escenario
        self.p = dict(escenario.ga)
        self.p.update({k: v for k, v in cambios_parametros.items() if v is not None})
        self.n_sat = escenario.num_satelites
        self.rng = np.random.default_rng(int(self.p["semilla"]))
        self.evaluador = Evaluador(escenario)

    def _evaluar_todos(self, pob):
        evals = [self.evaluador.evaluar(ind) for ind in pob]
        claves = [clave_factibilidad(e) for e in evals]
        return evals, claves

    def ejecutar(self, verbose: bool = False) -> dict:
        p = self.p
        rng = self.rng
        inicio = time.time()

        pob = poblacion_inicial(int(p["poblacion"]), self.n_sat, rng)
        evals, claves = self._evaluar_todos(pob)
        i_mejor = max(range(len(pob)), key=lambda i: claves[i])
        inicial = pob[i_mejor].copy()

        mejor_global = pob[i_mejor].copy()
        clave_global = claves[i_mejor]
        historial = []
        sin_mejora = 0
        gen_suficiente = None
        gen = 0

        for gen in range(int(p["generaciones"]) + 1):
            # ---- registro de la generación actual ----
            fits = np.array([e.fitness for e in evals])
            validos = np.array([e.valida for e in evals])
            i_mejor = max(range(len(pob)), key=lambda i: claves[i])
            e_mejor = evals[i_mejor]
            historial.append({
                "generacion": gen,
                "mejor_fitness": e_mejor.fitness,
                "mejor_valida": e_mejor.valida,
                "promedio_fitness": round(float(fits.mean()), 6),
                "peor_fitness": round(float(fits.min()), 6),
                "promedio_validos": round(float(fits[validos].mean()), 6) if validos.any() else None,
                "pct_validos": round(float(validos.mean()), 4),
                "cobertura_ponderada_mejor": e_mejor.cobertura_ponderada,
                "regiones_cubiertas_mejor": e_mejor.regiones_cubiertas,
                "violacion_mejor": e_mejor.violacion,
                "diversidad": round(diversidad(pob), 4),
            })
            if e_mejor.suficientemente_buena and gen_suficiente is None:
                gen_suficiente = gen

            if claves[i_mejor] > clave_global:
                clave_global = claves[i_mejor]
                mejor_global = pob[i_mejor].copy()
                sin_mejora = 0
            else:
                sin_mejora += 1

            if verbose and gen % 20 == 0:
                print(f"gen {gen:4d} | mejor {e_mejor.fitness:.4f} "
                      f"({'válida' if e_mejor.valida else 'INVÁLIDA'}) | "
                      f"prom {fits.mean():.4f} | válidos {validos.mean():.0%}")

            if gen == int(p["generaciones"]) or sin_mejora >= int(p["paciencia"]):
                break

            # ---- nueva generación ----
            orden = sorted(range(len(pob)), key=lambda i: claves[i], reverse=True)
            nueva = [pob[i].copy() for i in orden[: int(p["elitismo"])]]
            while len(nueva) < len(pob):
                a = pob[seleccion_torneo(claves, int(p["torneo_k"]), rng)]
                b = pob[seleccion_torneo(claves, int(p["torneo_k"]), rng)]
                hijo = cruza_uniforme(a, b, rng) if rng.random() < p["prob_cruza"] else a.copy()
                hijo = mutar(hijo, p["prob_mutacion"], p["sigma_mutacion"], rng, p["prob_reubicar"])
                nueva.append(hijo)
            pob = nueva
            evals, claves = self._evaluar_todos(pob)

        ev_ini = self.evaluador.evaluar(inicial, detalle=True)
        ev_fin = self.evaluador.evaluar(mejor_global, detalle=True)
        return {
            "escenario": self.esc.a_dict(),
            "parametros": {**p, "num_satelites": self.n_sat},
            "semilla": int(p["semilla"]),
            "generaciones_ejecutadas": gen,
            "gen_suficiente": gen_suficiente,
            "evaluaciones": self.evaluador.evaluaciones,
            "tiempo_s": round(time.time() - inicio, 3),
            "inicial": {"satelites": satelites_a_lista(inicial), "evaluacion": ev_ini.a_dict()},
            "final": {"satelites": satelites_a_lista(mejor_global), "evaluacion": ev_fin.a_dict()},
            "historial": historial,
        }