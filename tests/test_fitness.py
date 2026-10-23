"""Pruebas de la función de evaluación.

Responsable: Hector Martínez Sánchez
"""
from pathlib import Path

import numpy as np
import pytest

from astroshield.escenario import cargar_escenario
from astroshield.fitness import Evaluador
from astroshield.geo import punto_destino

RAIZ = Path(__file__).resolve().parents[1]

IDEAL = np.array([
    [20.5, -89.0], [-3.5, -62.0], [36.8, -119.4], [15.0, 0.0],
    [36.0, 138.0], [-25.0, 133.0], [23.5, -89.0], [-6.5, -62.0],
])


@pytest.fixture(scope="module")
def evaluador():
    return Evaluador(cargar_escenario(RAIZ / "config/escenarios/base.json"))


def test_cada_region_tiene_37_puntos(evaluador):
    for k in range(6):
        assert np.sum(evaluador.pts_region == k) == 37


def test_configuracion_ideal_tiene_fitness_1(evaluador):
    e = evaluador.evaluar(IDEAL, detalle=True)
    assert e.valida
    assert e.fitness == pytest.approx(1.0)
    assert e.regiones_cubiertas == 6
    assert e.suficientemente_buena
    yuc = next(r for r in e.regiones if r["id"] == "yucatan")
    assert sorted(yuc["satelites_que_ven"]) == [0, 6]


def test_region_sin_satelite_no_esta_cubierta(evaluador):
    sats = IDEAL.copy()
    sats[5] = [-60.0, 60.0]            # Australia se queda sola
    e = evaluador.evaluar(sats, detalle=True)
    aus = next(r for r in e.regiones if r["id"] == "australia")
    assert aus["cobertura"] == 0.0 and not aus["cubierta"]
    assert e.regiones_cubiertas == 5
    assert e.fitness == pytest.approx(1.0 - evaluador.w_cob * 1 / 13, abs=1e-6)


def test_prioridad_alta_pesa_mas_que_normal(evaluador):
    sin_yucatan = IDEAL.copy()
    sin_yucatan[[0, 6]] = [[-60.0, 0.0], [-60.0, 30.0]]
    sin_australia = IDEAL.copy()
    sin_australia[5] = [-60.0, 60.0]
    assert evaluador.evaluar(sin_yucatan).fitness < evaluador.evaluar(sin_australia).fitness


def test_cobertura_parcial(evaluador):
    """Un satélite a 11° de Sahel ve solo el borde de la región (radio 10°)."""
    sats = IDEAL.copy()
    lat, lon = punto_destino(15.0, 0.0, 90, 11.0)
    sats[3] = [lat, lon]
    e = evaluador.evaluar(sats, detalle=True)
    sahel = next(r for r in e.regiones if r["id"] == "sahel")
    assert 0.0 < sahel["cobertura"] < 0.9
    assert not sahel["cubierta"]


def test_redundancia_solo_cuenta_regiones_alta(evaluador):
    sin_respaldo = IDEAL.copy()
    sin_respaldo[[6, 7]] = [[-60.0, 0.0], [-60.0, 30.0]]
    e = evaluador.evaluar(sin_respaldo)
    assert e.cobertura_ponderada == pytest.approx(1.0)
    assert e.redundancia_alta == 0.0
    assert e.fitness == pytest.approx(evaluador.w_cob)


def test_satelites_en_cualquier_orden_dan_el_mismo_fitness(evaluador):
    rng = np.random.default_rng(0)
    revuelta = IDEAL[rng.permutation(8)]
    assert evaluador.evaluar(revuelta).fitness == evaluador.evaluar(IDEAL).fitness

def test_cubrir_una_region_nueva_vale_mas_que_un_respaldo(evaluador):
    """6 regiones + respaldo solo en Yucatán  >  5 regiones (sin Australia) + doble respaldo.
    Con peso_redundancia = 0.15 esta prueba FALLABA (0.925 < 0.9346): el
    algoritmo prefería reforzar Amazonía antes que cubrir Australia."""
    seis_regiones = IDEAL.copy()
    seis_regiones[7] = [-60.0, 30.0]                  # se pierde el respaldo de Amazonía
    cinco_regiones = IDEAL.copy()
    cinco_regiones[5] = [-0.5, -62.0]                 # Australia se abandona para respaldar
    a = evaluador.evaluar(seis_regiones, detalle=True)
    b = evaluador.evaluar(cinco_regiones, detalle=True)
    assert a.valida and b.valida
    assert a.regiones_cubiertas == 6 and b.regiones_cubiertas == 5
    assert a.fitness > b.fitness