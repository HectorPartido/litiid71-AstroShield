"""Pruebas de la geometría esférica.

Responsable: Anthony Oziel Ramos López
"""
import numpy as np
import pytest

from astroshield.geo import (distancia_angular, grados_a_km, km_a_grados, latitud_uniforme,
                             muestrear_disco, normalizar, punto_destino)


def test_distancia_de_un_punto_a_si_mismo_es_cero():
    assert distancia_angular(20.5, -89.0, 20.5, -89.0) == pytest.approx(0.0)


def test_distancia_polo_a_polo_es_180():
    assert distancia_angular(90, 0, -90, 0) == pytest.approx(180.0)


def test_un_grado_de_latitud_son_111_km():
    assert grados_a_km(distancia_angular(0, 0, 1, 0)) == pytest.approx(111.19, abs=0.01)


def test_300_km_son_2_7_grados():
    assert km_a_grados(300) == pytest.approx(2.698, abs=0.001)


def test_distancia_cruza_el_antimeridiano():
    """De 179°E a 179°W hay 2°, no 358°."""
    assert distancia_angular(0, 179, 0, -179) == pytest.approx(2.0)


def test_distancia_es_simetrica():
    assert distancia_angular(36, 138, -25, 133) == pytest.approx(distancia_angular(-25, 133, 36, 138))


@pytest.mark.parametrize("lat,lon,esp_lat,esp_lon", [
    (95, 10, 85, -170),       # pasa el polo norte
    (-95, 170, -85, -10),     # pasa el polo sur
    (10, 190, 10, -170),      # longitud mayor a 180
    (10, -540, 10, -180),     # varias vueltas
])
def test_normalizar(lat, lon, esp_lat, esp_lon):
    la, lo = normalizar(lat, lon)
    assert float(la) == pytest.approx(esp_lat)
    assert float(lo) == pytest.approx(esp_lon)


def test_punto_destino_queda_a_la_distancia_pedida():
    for az in (0, 45, 90, 200, 330):
        la, lo = punto_destino(20.5, -89.0, az, 10.0)
        assert distancia_angular(20.5, -89.0, la, lo) == pytest.approx(10.0, abs=1e-9)


def test_muestreo_de_region():
    la, lo = muestrear_disco(36.0, 138.0, 2.7)
    assert len(la) == 37
    d = distancia_angular(36.0, 138.0, la, lo)
    assert d.max() == pytest.approx(2.7, abs=1e-9)    # el anillo externo está en el borde
    assert d.min() == pytest.approx(0.0)              # incluye el centro


def test_latitudes_aleatorias_uniformes_en_area():
    """Con muestreo uniforme en área, la mitad de los puntos cae entre -30° y 30°
    (sen 30° = 0.5). Si fuera uniforme en grados sería solo un tercio."""
    lat = latitud_uniforme(np.random.default_rng(0), 100_000)
    assert np.mean(np.abs(lat) < 30) == pytest.approx(0.5, abs=0.01)