"""Demostración de la función de evaluación y de las restricciones.

Evalúa a mano varias configuraciones conocidas para mostrar, con números,
cómo responde el criterio de evaluación. Útil para explicar el modelo en
la revisión sin tener que correr el algoritmo completo.

Uso:  python experiments/demo_evaluacion.py

Responsable: Hector Martínez Sánchez
"""
from pathlib import Path

import numpy as np

from astroshield.escenario import cargar_escenario
from astroshield.fitness import Evaluador

RAIZ = Path(__file__).resolve().parents[1]

IDEAL = np.array([
    [20.5, -89.0], [-3.5, -62.0], [36.8, -119.4], [15.0, 0.0],
    [36.0, 138.0], [-25.0, 133.0], [23.5, -89.0], [-6.5, -62.0],
])


def variante(cambios):
    sats = IDEAL.copy()
    for i, pos in cambios.items():
        sats[i] = pos
    return sats


CASOS = [
    ("1. Ideal: 1 satélite por región + 2 de respaldo en las Alta", IDEAL),
    ("2. Sin respaldo (los 2 extra mandados al océano Antártico)",
     variante({6: [-60, 0], 7: [-60, 30]})),
    ("3. Sin Australia (prioridad Normal)", variante({5: [-60, 60]})),
    ("4. Sin Yucatán (prioridad Alta, ni respaldo)", variante({0: [-60, 0], 6: [-60, 30]})),
    ("5. Satélite de Sahel dentro del Objeto A", variante({3: [10.0, 45.0]})),
    ("6. Satélite de Sahel movido al Atlántico Norte",
     variante({3: [45.0, -35.0]})),
    ("7. Respaldo pegado a Yucatán (0.5°, viola separación)", variante({6: [21.0, -89.0]})),
]


def main():
    esc = cargar_escenario(RAIZ / "config/escenarios/base.json")
    ev = Evaluador(esc)
    print(f"{'Caso':62s}{'fitness':>9s}{'cob.pond':>10s}{'redund':>8s}{'cubiertas':>10s}  válida")
    print("-" * 108)
    for nombre, sats in CASOS:
        e = ev.evaluar(sats, detalle=True)
        print(f"{nombre:62s}{e.fitness:9.4f}{e.cobertura_ponderada:10.4f}"
              f"{e.redundancia_alta:8.2f}{e.regiones_cubiertas:>7d}/6   {'sí' if e.valida else 'NO'}")
        for v in e.violaciones:
            if v["tipo"] == "separacion":
                print(f"{'':6s}↳ satélite {v['satelite']} está pegado al {v['zona']} "
                      f"(faltan {v['invasion_grados']}° de separación)")
            else:
                print(f"{'':6s}↳ satélite {v['satelite']} invade '{v['zona']}' ({v['tipo']}) "
                      f"por {v['invasion_grados']}°")
    print("\nLectura: los casos 5-7 tienen buen fitness pero son INVÁLIDOS; con la regla de")
    print("factibilidad cualquier configuración válida (incluso el caso 4) les gana.")


if __name__ == "__main__":
    main()