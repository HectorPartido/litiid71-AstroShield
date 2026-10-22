"""Pruebas del algoritmo evolutivo y sus operadores.

Responsable: Gildardo Emmanuel González García
"""
from pathlib import Path

import numpy as np
import pytest

from astroshield.escenario import cargar_escenario
from astroshield.ga import (AlgoritmoEvolutivo, cruza_uniforme, mutar,
                            poblacion_inicial, seleccion_torneo)

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def esc():
    return cargar_escenario(RAIZ / "config/escenarios/base.json")


def test_poblacion_inicial_tiene_forma_correcta():
    rng = np.random.default_rng(0)
    pob = poblacion_inicial(10, 8, rng)
    assert len(pob) == 10
    for ind in pob:
        assert ind.shape == (8, 2)
        assert np.all(np.abs(ind[:, 0]) <= 90)
        assert np.all((ind[:, 1] >= -180) & (ind[:, 1] < 180))


def test_cruza_hereda_satelites_completos_de_los_padres():
    rng = np.random.default_rng(1)
    p1 = np.zeros((8, 2))
    p2 = np.ones((8, 2)) * 10
    hijo = cruza_uniforme(p1, p2, rng)
    for sat in hijo:          # cada satélite viene entero de un padre
        assert (sat == [0, 0]).all() or (sat == [10, 10]).all()


def test_mutacion_mantiene_coordenadas_validas():
    rng = np.random.default_rng(2)
    ind = np.array([[89.0, 179.0]] * 8)        # pegado al polo y al antimeridiano
    for _ in range(200):
        ind = mutar(ind, pm=1.0, sigma=10.0, rng=rng, p_reubicar=0.1)
        assert np.all(np.abs(ind[:, 0]) <= 90)
        assert np.all((ind[:, 1] >= -180) & (ind[:, 1] < 180))


def test_mutacion_con_probabilidad_cero_no_cambia_nada():
    rng = np.random.default_rng(3)
    ind = np.array([[10.0, 20.0]] * 8)
    assert np.allclose(mutar(ind, pm=0.0, sigma=5.0, rng=rng, p_reubicar=0.0), ind)


def test_torneo_escoge_al_mejor_de_los_candidatos():
    rng = np.random.default_rng(4)
    claves = [(1, 0.1), (1, 0.9), (0, -5.0)]
    # con k = tamaño de la población, siempre gana el mejor
    assert seleccion_torneo(claves, 3, rng) == 1


def test_el_algoritmo_mejora_respecto_a_la_poblacion_inicial(esc):
    res = AlgoritmoEvolutivo(esc, semilla=42, generaciones=60).ejecutar()
    h = res["historial"]
    assert res["final"]["evaluacion"]["fitness"] > res["inicial"]["evaluacion"]["fitness"]
    assert h[-1]["mejor_fitness"] >= h[0]["mejor_fitness"]


def test_elitismo_el_mejor_nunca_empeora(esc):
    res = AlgoritmoEvolutivo(esc, semilla=7, generaciones=80).ejecutar()
    mejores = [g["mejor_fitness"] for g in res["historial"] if g["mejor_valida"]]
    assert all(b >= a - 1e-12 for a, b in zip(mejores, mejores[1:]))


def test_misma_semilla_mismo_resultado(esc):
    a = AlgoritmoEvolutivo(esc, semilla=5, generaciones=30).ejecutar()
    b = AlgoritmoEvolutivo(esc, semilla=5, generaciones=30).ejecutar()
    assert a["final"]["satelites"] == b["final"]["satelites"]


def test_la_solucion_final_es_valida(esc):
    res = AlgoritmoEvolutivo(esc, semilla=42).ejecutar()
    assert res["final"]["evaluacion"]["valida"]
    assert res["final"]["evaluacion"]["violacion"] == 0.0


def test_formato_del_resultado(esc):
    res = AlgoritmoEvolutivo(esc, semilla=1, generaciones=5).ejecutar()
    for clave in ("escenario", "parametros", "semilla", "inicial", "final", "historial",
                  "generaciones_ejecutadas", "gen_suficiente"):
        assert clave in res
    assert len(res["final"]["satelites"]) == 8
    assert len(res["historial"]) == res["generaciones_ejecutadas"] + 1