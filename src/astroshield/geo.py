"""Geometría sobre una esfera: el modelo simplificado de la Tierra de AstroShield.

Todas las posiciones se expresan como (latitud, longitud) en grados.
Las distancias "angulares" son el ángulo central entre dos puntos, también
en grados (1° ≈ 111.2 km sobre la superficie).

Responsable: Hector Partido Flores
"""
import numpy as np

RADIO_TIERRA_KM = 6371.0


def km_a_grados(km):
    """Convierte una distancia sobre la superficie (km) a grados angulares."""
    return np.degrees(np.asarray(km, dtype=float) / RADIO_TIERRA_KM)


def grados_a_km(grados):
    """Convierte grados angulares a km sobre la superficie."""
    return np.radians(np.asarray(grados, dtype=float)) * RADIO_TIERRA_KM


def distancia_angular(lat1, lon1, lat2, lon2):
    """Distancia de gran círculo en grados (fórmula de haversine).

    Acepta escalares o arreglos de numpy (con broadcasting), así se puede
    calcular la distancia de muchos puntos contra muchos satélites a la vez.
    """
    p1 = np.radians(lat1)
    p2 = np.radians(lat2)
    dphi = p2 - p1
    dlam = np.radians(np.asarray(lon2, dtype=float) - np.asarray(lon1, dtype=float))
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlam / 2) ** 2
    return np.degrees(2 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0))))


def normalizar(lat, lon):
    """Lleva una posición a rangos válidos.

    - Latitud a [-90, 90]: si una mutación "se pasa" del polo, el punto
      reaparece del otro lado del polo (y su longitud gira 180°).
    - Longitud a [-180, 180).
    """
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    lat = ((lat + 90.0) % 360.0) - 90.0          # queda en [-90, 270)
    paso_polo = lat > 90.0
    lat = np.where(paso_polo, 180.0 - lat, lat)
    lon = np.where(paso_polo, lon + 180.0, lon)
    lon = ((lon + 180.0) % 360.0) - 180.0
    return lat, lon


def punto_destino(lat, lon, azimut_grados, distancia_grados):
    """Punto al que se llega avanzando `distancia_grados` desde (lat, lon)
    en la dirección `azimut_grados` (0 = norte, 90 = este)."""
    p1 = np.radians(lat)
    l1 = np.radians(lon)
    th = np.radians(azimut_grados)
    d = np.radians(distancia_grados)
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(th))
    l2 = l1 + np.arctan2(np.sin(th) * np.sin(d) * np.cos(p1),
                         np.cos(d) - np.sin(p1) * np.sin(p2))
    lat2, lon2 = normalizar(np.degrees(p2), np.degrees(l2))
    return lat2, lon2


def muestrear_disco(lat, lon, radio_grados, anillos=3):
    """Puntos de muestra que representan una región circular.

    Devuelve el centro + `anillos` círculos concéntricos con 6, 12, 18...
    puntos. Con anillos=3 son 1 + 6 + 12 + 18 = 37 puntos.
    Se usa para medir QUÉ FRACCIÓN de una región ve la constelación.
    """
    lats = [float(lat)]
    lons = [float(lon)]
    for i in range(1, anillos + 1):
        r = radio_grados * i / anillos
        n = 6 * i
        for k in range(n):
            la, lo = punto_destino(lat, lon, 360.0 * k / n, r)
            lats.append(float(la))
            lons.append(float(lo))
    return np.array(lats), np.array(lons)


def latitud_uniforme(rng, n):
    """Latitudes aleatorias uniformes EN ÁREA (no se amontonan en los polos)."""
    return np.degrees(np.arcsin(rng.uniform(-1.0, 1.0, size=n)))