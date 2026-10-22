"""Restricciones espaciales y regla de factibilidad.

Una configuración es INVÁLIDA si:
  1. Algún satélite está dentro de una zona de desechos o de exclusión de un
     objeto ocupado (distancia angular al centro < radio de la zona).
  2. Dos satélites de la constelación están a menos de
     `separacion_minima_grados` entre sí (regla propia del equipo para evitar
     satélites encimados / colisiones).

No se tira a la basura una configuración inválida: se mide CUÁNTO viola
(grados de invasión) para que el algoritmo pueda guiarla hacia zonas válidas.

Responsable: Hector Martínez Sánchez
"""
from __future__ import annotations

import numpy as np

from .geo import distancia_angular


def calcular_violaciones(satelites: np.ndarray, escenario) -> tuple[float, list]:
    """Revisa todas las restricciones.

    satelites: arreglo (n, 2) con [lat, lon] de cada satélite.
    Devuelve (violacion_total_en_grados, lista_de_violaciones).
    violacion_total == 0  ⇔  la configuración es válida.
    """
    lats = satelites[:, 0]
    lons = satelites[:, 1]
    total = 0.0
    detalle = []

    # 1) Zonas de desechos y objetos ocupados
    for zona in escenario.zonas:
        d = distancia_angular(lats, lons, zona.lat, zona.lon)
        invasion = zona.radio_grados - d
        for i in np.where(invasion > 0)[0]:
            total += float(invasion[i])
            detalle.append({
                "satelite": int(i),
                "tipo": zona.tipo,
                "zona": zona.id,
                "invasion_grados": round(float(invasion[i]), 3),
            })

    # 2) Separación mínima entre satélites propios
    sep = escenario.separacion_minima_grados
    if sep > 0 and len(satelites) > 1:
        d = distancia_angular(lats[:, None], lons[:, None], lats[None, :], lons[None, :])
        n = len(satelites)
        for i in range(n):
            for j in range(i + 1, n):
                if d[i, j] < sep:
                    falta = sep - float(d[i, j])
                    total += falta
                    detalle.append({
                        "satelite": i,
                        "tipo": "separacion",
                        "zona": f"satelite_{j}",
                        "invasion_grados": round(falta, 3),
                    })
    return total, detalle


def es_valida(satelites: np.ndarray, escenario) -> bool:
    total, _ = calcular_violaciones(satelites, escenario)
    return total == 0.0


def clave_factibilidad(evaluacion) -> tuple:
    """Clave para ordenar soluciones (mayor = mejor). Regla de Deb:

      1. Una solución VÁLIDA siempre le gana a una INVÁLIDA.
      2. Entre dos válidas, gana la de mayor fitness.
      3. Entre dos inválidas, gana la que viola MENOS.

    Así una configuración con buen puntaje pero que invade una zona prohibida
    nunca puede quedar como "la mejor".
    """
    if evaluacion.valida:
        return (1, evaluacion.fitness)
    return (0, -evaluacion.violacion)