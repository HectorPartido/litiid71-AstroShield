"""Carga y validación de escenarios (archivos JSON en config/escenarios/).

Un escenario contiene TODO lo que define el problema: regiones, prioridades,
zonas prohibidas, objetos ocupados y parámetros del algoritmo. Cambiar las
condiciones (punto 3.3 de la actividad) = usar otro JSON, sin tocar código.

Responsable: Hector Partido Flores
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .geo import km_a_grados

PARAMETROS_GA_DEFECTO = {
    "poblacion": 60,
    "generaciones": 200,
    "prob_cruza": 0.9,
    "prob_mutacion": 0.15,
    "sigma_mutacion": 5.0,
    "prob_reubicar": 0.03,
    "torneo_k": 3,
    "elitismo": 2,
    "paciencia": 80,
    "semilla": 42,
}


@dataclass
class Region:
    id: str
    nombre: str
    lat: float
    lon: float
    prioridad: str          # "alta" | "media" | "normal"


@dataclass
class Zona:
    id: str
    nombre: str
    lat: float
    lon: float
    radio_grados: float
    tipo: str               # "desechos" | "ocupado"


@dataclass
class Escenario:
    nombre: str
    descripcion: str
    num_satelites: int
    altitud_km: float
    radio_vision_grados: float
    separacion_minima_grados: float
    radio_region_km: float
    umbral_cobertura: float
    pesos_prioridad: dict
    regiones: list
    zonas: list                                  # desechos + ocupados
    ga: dict = field(default_factory=dict)
    criterio_suficiente: dict = field(default_factory=dict)

    @property
    def radio_region_grados(self) -> float:
        return float(km_a_grados(self.radio_region_km))

    def peso(self, region: Region) -> float:
        return float(self.pesos_prioridad[region.prioridad])

    def a_dict(self) -> dict:
        """Versión serializable (se guarda dentro de cada resultado)."""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "num_satelites": self.num_satelites,
            "altitud_km": self.altitud_km,
            "radio_vision_grados": self.radio_vision_grados,
            "separacion_minima_grados": self.separacion_minima_grados,
            "radio_region_km": self.radio_region_km,
            "umbral_cobertura": self.umbral_cobertura,
            "pesos_prioridad": dict(self.pesos_prioridad),
            "regiones": [asdict(r) for r in self.regiones],
            "zonas_restringidas": [asdict(z) for z in self.zonas if z.tipo == "desechos"],
            "objetos_ocupados": [asdict(z) for z in self.zonas if z.tipo == "ocupado"],
            "ga": dict(self.ga),
            "criterio_suficiente": dict(self.criterio_suficiente),
        }


def escenario_desde_dict(datos: dict) -> Escenario:
    """Construye y valida un Escenario a partir de un diccionario."""
    pesos = datos["pesos_prioridad"]
    regiones = [Region(**r) for r in datos["regiones"]]
    for r in regiones:
        if r.prioridad not in pesos:
            raise ValueError(f"Región {r.id}: prioridad '{r.prioridad}' no está en pesos_prioridad")
        if not (-90 <= r.lat <= 90 and -180 <= r.lon <= 180):
            raise ValueError(f"Región {r.id}: coordenadas fuera de rango")

    zonas = [Zona(tipo="desechos", **z) for z in datos.get("zonas_restringidas", [])]
    zonas += [Zona(tipo="ocupado", **z) for z in datos.get("objetos_ocupados", [])]
    for z in zonas:
        if z.radio_grados <= 0:
            raise ValueError(f"Zona {z.id}: el radio debe ser positivo")

    ga = dict(PARAMETROS_GA_DEFECTO)
    ga.update(datos.get("ga", {}))

    criterio = {"cobertura_ponderada_minima": 0.95, "todas_las_alta_cubiertas": True}
    criterio.update(datos.get("criterio_suficiente", {}))

    if int(datos["num_satelites"]) < 1:
        raise ValueError("num_satelites debe ser al menos 1")

    return Escenario(
        nombre=datos["nombre"],
        descripcion=datos.get("descripcion", ""),
        num_satelites=int(datos["num_satelites"]),
        altitud_km=float(datos.get("altitud_km", 800)),
        radio_vision_grados=float(datos["radio_vision_grados"]),
        separacion_minima_grados=float(datos.get("separacion_minima_grados", 0.0)),
        radio_region_km=float(datos.get("radio_region_km", 300)),
        umbral_cobertura=float(datos.get("umbral_cobertura", 0.9)),
        pesos_prioridad={k: float(v) for k, v in pesos.items()},
        regiones=regiones,
        zonas=zonas,
        ga=ga,
        criterio_suficiente=criterio,
    )


def cargar_escenario(ruta) -> Escenario:
    """Lee un archivo JSON de escenario.

    Si el JSON trae la clave "hereda_de", primero carga ese escenario base y
    luego aplica encima los cambios (así los escenarios derivados solo
    escriben lo que cambia).
    """
    ruta = Path(ruta)
    datos = _leer_con_herencia(ruta)
    return escenario_desde_dict(datos)


def _leer_con_herencia(ruta: Path) -> dict:
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    padre = datos.pop("hereda_de", None)
    if padre is None:
        return datos
    base = _leer_con_herencia(ruta.parent / padre)
    return _aplicar_cambios(base, datos)


def _aplicar_cambios(base: dict, cambios: dict) -> dict:
    """Combina un escenario base con los cambios de un escenario derivado.

    Claves especiales:
      - "zonas_restringidas_extra" / "objetos_ocupados_extra": se AGREGAN.
      - "quitar_zonas": lista de ids de zonas/objetos a eliminar.
      - "cambiar_prioridades": {id_region: nueva_prioridad}.
      - "ga": se mezcla clave por clave.
    Cualquier otra clave reemplaza a la del base.
    """
    res = copy.deepcopy(base)
    for clave, valor in cambios.items():
        if clave == "zonas_restringidas_extra":
            res.setdefault("zonas_restringidas", []).extend(valor)
        elif clave == "objetos_ocupados_extra":
            res.setdefault("objetos_ocupados", []).extend(valor)
        elif clave == "quitar_zonas":
            for k in ("zonas_restringidas", "objetos_ocupados"):
                res[k] = [z for z in res.get(k, []) if z["id"] not in valor]
        elif clave == "cambiar_prioridades":
            for r in res["regiones"]:
                if r["id"] in valor:
                    r["prioridad"] = valor[r["id"]]
        elif clave == "ga":
            res.setdefault("ga", {}).update(valor)
        else:
            res[clave] = copy.deepcopy(valor)
    return res