"""Pruebas de la carga de escenarios.

Responsable: Anthony Oziel Ramos López
"""
from pathlib import Path

import pytest

from astroshield.escenario import cargar_escenario, escenario_desde_dict

ESC = Path(__file__).resolve().parents[1] / "config" / "escenarios"


def test_escenario_base_tiene_los_datos_de_la_actividad():
    e = cargar_escenario(ESC / "base.json")
    assert e.num_satelites == 8
    assert len(e.regiones) == 6
    assert e.radio_region_km == 300
    desechos = {z.id: z.radio_grados for z in e.zonas if z.tipo == "desechos"}
    ocupados = {z.id: z.radio_grados for z in e.zonas if z.tipo == "ocupado"}
    assert desechos == {"atlantico_norte": 12, "pacifico_sur": 10, "polar_norte": 8}
    assert ocupados == {"objeto_a": 5, "objeto_b": 5}
    prioridades = {r.id: r.prioridad for r in e.regiones}
    assert prioridades["yucatan"] == "alta" and prioridades["australia"] == "normal"


def test_herencia_agrega_zonas():
    e = cargar_escenario(ESC / "reducido.json")
    assert len(e.zonas) == 5 + 3
    assert e.num_satelites == 8          # lo demás se hereda del base


def test_herencia_quita_zonas():
    assert cargar_escenario(ESC / "sin_restricciones.json").zonas == []


def test_herencia_cambia_prioridades():
    e = cargar_escenario(ESC / "prioridades_cambiadas.json")
    p = {r.id: r.prioridad for r in e.regiones}
    assert p["australia"] == "alta" and p["yucatan"] == "normal"


def test_todos_los_escenarios_cargan():
    for ruta in ESC.glob("*.json"):
        cargar_escenario(ruta)


def _minimo():
    return {"nombre": "x", "num_satelites": 2, "radio_vision_grados": 10,
            "pesos_prioridad": {"alta": 3},
            "regiones": [{"id": "r", "nombre": "R", "lat": 0, "lon": 0, "prioridad": "alta"}]}


def test_prioridad_desconocida_es_error():
    d = _minimo()
    d["regiones"][0]["prioridad"] = "urgente"
    with pytest.raises(ValueError):
        escenario_desde_dict(d)


def test_radio_de_zona_negativo_es_error():
    d = _minimo()
    d["zonas_restringidas"] = [{"id": "z", "nombre": "Z", "lat": 0, "lon": 0, "radio_grados": -1}]
    with pytest.raises(ValueError):
        escenario_desde_dict(d)