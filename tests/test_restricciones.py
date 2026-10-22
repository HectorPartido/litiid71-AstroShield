"""Pruebas de las restricciones espaciales.

Responsable: Hector Martínez Sánchez
"""
from pathlib import Path

import numpy as np
import pytest

from astroshield.escenario import cargar_escenario
from astroshield.fitness import Evaluador
from astroshield.geo import punto_destino
from astroshield.restricciones import calcular_violaciones, clave_factibilidad, es_valida

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def esc():
    return cargar_escenario(RAIZ / "config/escenarios/base.json")


# Configuración "ideal" hecha a mano: un satélite sobre cada región y
# dos de respaldo a 3° de las regiones Alta. Es válida.
IDEAL = np.array([
    [20.5, -89.0],    # 0 Yucatán
    [-3.5, -62.0],    # 1 Amazonía
    [36.8, -119.4],   # 2 California
    [15.0, 0.0],      # 3 Sahel
    [36.0, 138.0],    # 4 Japón
    [-25.0, 133.0],   # 5 Australia
    [23.5, -89.0],    # 6 respaldo Yucatán (3° al norte)
    [-6.5, -62.0],    # 7 respaldo Amazonía (3° al sur)
])


def test_configuracion_ideal_es_valida(esc):
    total, lista = calcular_violaciones(IDEAL, esc)
    assert total == 0.0
    assert lista == []


@pytest.mark.parametrize("zona_id", ["atlantico_norte", "pacifico_sur", "polar_norte"])
def test_satelite_en_centro_de_zona_de_desechos_es_invalido(esc, zona_id):
    zona = next(z for z in esc.zonas if z.id == zona_id)
    sats = IDEAL.copy()
    sats[3] = [zona.lat, zona.lon]
    total, lista = calcular_violaciones(sats, esc)
    assert total == pytest.approx(zona.radio_grados, abs=1e-6)
    assert any(v["zona"] == zona_id and v["tipo"] == "desechos" for v in lista)


@pytest.mark.parametrize("obj_id", ["objeto_a", "objeto_b"])
def test_satelite_en_objeto_ocupado_es_invalido(esc, obj_id):
    obj = next(z for z in esc.zonas if z.id == obj_id)
    sats = IDEAL.copy()
    # 2° adentro de la zona de exclusión (radio 5°)
    lat, lon = punto_destino(obj.lat, obj.lon, 90, 3.0)
    sats[3] = [lat, lon]
    total, lista = calcular_violaciones(sats, esc)
    assert not es_valida(sats, esc)
    v = next(v for v in lista if v["zona"] == obj_id)
    assert v["tipo"] == "ocupado"
    assert v["invasion_grados"] == pytest.approx(2.0, abs=1e-3)


def test_borde_de_zona_justo_afuera_es_valido(esc):
    """Un satélite a 12.01° del centro del Atlántico Norte (radio 12°) es válido."""
    zona = next(z for z in esc.zonas if z.id == "atlantico_norte")
    lat, lon = punto_destino(zona.lat, zona.lon, 180, 12.01)
    sats = IDEAL.copy()
    sats[3] = [lat, lon]
    assert es_valida(sats, esc)


def test_satelites_demasiado_juntos_es_invalido(esc):
    sats = IDEAL.copy()
    sats[6] = [21.5, -89.0]          # a 1° del satélite 0 (mínimo 2°)
    total, lista = calcular_violaciones(sats, esc)
    sep = [v for v in lista if v["tipo"] == "separacion"]
    assert len(sep) == 1
    assert sep[0]["invasion_grados"] == pytest.approx(1.0, abs=1e-3)


def test_valida_siempre_gana_a_invalida(esc):
    """Regla de factibilidad: una válida mala le gana a una inválida perfecta."""
    ev = Evaluador(esc)
    invalida = IDEAL.copy()
    invalida[6] = [21.0, -89.0]      # pegado a otro satélite → inválida
    mala_valida = np.array([[0.0, lon] for lon in range(-170, 170, 40)])[:8]
    e_inv = ev.evaluar(invalida)
    e_val = ev.evaluar(mala_valida)
    assert not e_inv.valida and e_val.valida
    assert e_inv.fitness > e_val.fitness             # la inválida "puntúa" más...
    assert clave_factibilidad(e_val) > clave_factibilidad(e_inv)   # ...pero pierde


def test_entre_invalidas_gana_la_que_viola_menos(esc):
    ev = Evaluador(esc)
    poco = IDEAL.copy()
    poco[3] = [45.0, -24.0]          # ~4.2° adentro del Atlántico Norte (borde)
    mucho = IDEAL.copy()
    mucho[3] = [45.0, -35.0]         # en el centro (12° adentro)
    assert clave_factibilidad(ev.evaluar(poco)) > clave_factibilidad(ev.evaluar(mucho))