"""Pruebas de punta a punta: el algoritmo completo en cada escenario.

Verifican lo que pide la actividad: que las soluciones finales respeten las
restricciones y que el sistema reporte correctamente cuando algo es imposible.

Responsable: Anthony Oziel Ramos López
"""
from pathlib import Path

import numpy as np
import pytest

from astroshield.escenario import cargar_escenario
from astroshield.ga import AlgoritmoEvolutivo
from astroshield.geo import distancia_angular

ESC = Path(__file__).resolve().parents[1] / "config" / "escenarios"


def _correr(nombre, semilla=42, **cambios):
    esc = cargar_escenario(ESC / f"{nombre}.json")
    return esc, AlgoritmoEvolutivo(esc, semilla=semilla, **cambios).ejecutar()


@pytest.mark.parametrize("nombre", ["base", "reducido", "inviable", "prioridades_cambiadas"])
def test_ningun_satelite_final_invade_zonas(nombre):
    esc, res = _correr(nombre, generaciones=150)
    sats = np.array([[s["lat"], s["lon"]] for s in res["final"]["satelites"]])
    for z in esc.zonas:
        d = distancia_angular(sats[:, 0], sats[:, 1], z.lat, z.lon)
        assert d.min() >= z.radio_grados, f"un satélite invade {z.id}"
    assert res["final"]["evaluacion"]["valida"]


def test_poblacion_inicial_si_tiene_invalidas_y_el_algoritmo_las_elimina():
    _, res = _correr("base", generaciones=60)
    h = res["historial"]
    assert h[0]["pct_validos"] < 1.0          # al inicio hay configuraciones inválidas
    assert res["final"]["evaluacion"]["valida"]


def test_escenario_inviable_reporta_yucatan_sin_cubrir():
    _, res = _correr("inviable")
    fin = res["final"]["evaluacion"]
    yuc = next(r for r in fin["regiones"] if r["id"] == "yucatan")
    assert yuc["cobertura"] == 0.0 and not yuc["cubierta"]
    assert fin["valida"]                      # aun así entrega la mejor solución VÁLIDA
    assert res["gen_suficiente"] is None      # y avisa que no es suficientemente buena
    assert fin["regiones_cubiertas"] == 5     # cubre todo lo demás


def test_con_4_satelites_no_se_pueden_cubrir_6_regiones():
    esc = cargar_escenario(ESC / "base.json")
    esc.num_satelites = 4
    res = AlgoritmoEvolutivo(esc, semilla=1, generaciones=100).ejecutar()
    assert res["final"]["evaluacion"]["regiones_cubiertas"] <= 4