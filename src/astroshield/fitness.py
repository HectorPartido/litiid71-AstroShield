"""Función de evaluación (fitness) de una configuración de satélites.

Modelo de cobertura:
  - Cada satélite "ve" un círculo sobre la Tierra de radio
    `radio_vision_grados` alrededor de su punto subsatelital.
  - Cada región es un disco de 300 km representado por 37 puntos de muestra.
  - cobertura(región) = fracción de sus puntos vistos por al menos 1 satélite.
  - La región está CUBIERTA si cobertura >= umbral_cobertura (0.9).

Fitness (entre 0 y 1, solo tiene sentido para configuraciones válidas):
    fitness = 0.85 * cobertura_ponderada + 0.15 * redundancia_alta
  cobertura_ponderada = Σ peso_r · cobertura_r / Σ peso_r   (pesos 3/2/1)
  redundancia_alta    = promedio, en regiones de prioridad Alta, de la
                        fracción de puntos vistos por 2 o más satélites.

La redundancia le da un uso a los 2 satélites "sobrantes" (8 satélites,
6 regiones): respaldar las regiones más importantes.

Responsable: Hector Martínez Sánchez
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np

from .geo import distancia_angular, muestrear_disco
from .restricciones import calcular_violaciones
from astroshield import fitness as fit_mod


PESO_COBERTURA = 0.85
PESO_REDUNDANCIA = 0.15
wr = fit_mod.PESO_REDUNDANCIA


@dataclass
class Evaluacion:
    fitness: float
    valida: bool
    violacion: float
    cobertura_ponderada: float
    redundancia_alta: float
    regiones_cubiertas: int
    regiones: list = field(default_factory=list)
    violaciones: list = field(default_factory=list)
    suficientemente_buena: bool = False

    def a_dict(self) -> dict:
        return asdict(self)


class Evaluador:
    """Precalcula los puntos de muestra una sola vez y evalúa configuraciones."""

    def __init__(self, escenario):
        self.esc = escenario
        lats, lons, idx = [], [], []
        for k, r in enumerate(escenario.regiones):
            la, lo = muestrear_disco(r.lat, r.lon, escenario.radio_region_grados)
            lats.append(la)
            lons.append(lo)
            idx.append(np.full(len(la), k))
        self.pts_lat = np.concatenate(lats)
        self.pts_lon = np.concatenate(lons)
        self.pts_region = np.concatenate(idx)
        self.pesos = np.array([escenario.peso(r) for r in escenario.regiones])
        self.es_alta = np.array([r.prioridad == "alta" for r in escenario.regiones])
        self.evaluaciones = 0           # contador (sirve para comparar costo)

    def vistas_por_punto(self, satelites: np.ndarray) -> np.ndarray:
        """Matriz booleana (puntos x satélites): ¿el satélite j ve el punto i?"""
        d = distancia_angular(self.pts_lat[:, None], self.pts_lon[:, None],
                              satelites[None, :, 0], satelites[None, :, 1])
        return d <= self.esc.radio_vision_grados

    def evaluar(self, satelites: np.ndarray, detalle: bool = False) -> Evaluacion:
        self.evaluaciones += 1
        satelites = np.asarray(satelites, dtype=float)
        ve = self.vistas_por_punto(satelites)
        cuenta = ve.sum(axis=1)                     # satélites que ven cada punto

        n_reg = len(self.esc.regiones)
        cobertura = np.zeros(n_reg)
        redundancia = np.zeros(n_reg)
        for k in range(n_reg):
            m = self.pts_region == k
            cobertura[k] = np.mean(cuenta[m] >= 1)
            redundancia[k] = np.mean(cuenta[m] >= 2)

        cob_pond = float(np.sum(self.pesos * cobertura) / np.sum(self.pesos))
        red_alta = float(np.mean(redundancia[self.es_alta])) if self.es_alta.any() else 0.0
        fitness = PESO_COBERTURA * cob_pond + PESO_REDUNDANCIA * red_alta

        violacion, lista_viol = calcular_violaciones(satelites, self.esc)
        valida = violacion == 0.0
        cubiertas = cobertura >= self.esc.umbral_cobertura

        crit = self.esc.criterio_suficiente
        alta_ok = bool(np.all(cubiertas[self.es_alta])) if crit.get("todas_las_alta_cubiertas", True) else True
        suficiente = valida and alta_ok and cob_pond >= crit.get("cobertura_ponderada_minima", 0.95)

        regiones = []
        if detalle:
            for k, r in enumerate(self.esc.regiones):
                m = self.pts_region == k
                quienes = np.where(ve[m].any(axis=0))[0]
                regiones.append({
                    "id": r.id,
                    "nombre": r.nombre,
                    "prioridad": r.prioridad,
                    "peso": float(self.pesos[k]),
                    "cobertura": round(float(cobertura[k]), 4),
                    "redundancia": round(float(redundancia[k]), 4),
                    "cubierta": bool(cubiertas[k]),
                    "satelites_que_ven": [int(q) for q in quienes],
                })

        return Evaluacion(
            fitness=round(fitness, 6),
            valida=valida,
            violacion=round(float(violacion), 6),
            cobertura_ponderada=round(cob_pond, 6),
            redundancia_alta=round(red_alta, 6),
            regiones_cubiertas=int(cubiertas.sum()),
            regiones=regiones,
            violaciones=lista_viol if detalle else [],
            suficientemente_buena=bool(suficiente),
        )