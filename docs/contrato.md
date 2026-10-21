# Contrato entre módulos

Este archivo define **qué expone cada módulo y con qué formato**. Así cada integrante puede trabajar en su parte sin esperar a los demás. Si alguien necesita cambiar algo de aquí, lo avisa al equipo antes de hacer el commit.

## Mapa de módulos

```
config/escenarios/*.json ──► escenario.py ──► fitness.py ◄── restricciones.py
                                   │              │
                                   ▼              ▼
                              geo.py         ga.py ──► cli.py ──► results/*.json ──► viz/ (3D)
                                                                      │
                                                                      └──► experiments/ (gráficas, análisis)
```

| Módulo | Responsable | Expone |
|---|---|---|
| `geo.py` | Hector Partido | `distancia_angular`, `normalizar`, `muestrear_disco`, `latitud_uniforme`, `km_a_grados`, `grados_a_km` |
| `escenario.py` | Hector Partido | `cargar_escenario(ruta) -> Escenario`, clases `Escenario`, `Region`, `Zona` |
| `restricciones.py` | Hector Martínez | `calcular_violaciones(sats, esc) -> (total, lista)`, `es_valida`, `clave_factibilidad(evaluacion)` |
| `fitness.py` | Hector Martínez | `Evaluador(esc).evaluar(sats, detalle=False) -> Evaluacion` |
| `ga.py` | Gildardo | `AlgoritmoEvolutivo(esc, **parametros).ejecutar() -> dict` (formato abajo) |
| `cli.py` | Gildardo | comandos `run` y `reevaluar` |
| `viz/` | Ismael | lee `results/index.json` y `results/<nombre>.json` |
| `tests/`, `experiments/` | Anthony | pruebas y análisis |

## Convenciones

- Una **configuración** siempre es un `numpy.ndarray` de forma `(n_satelites, 2)` con columnas `[lat, lon]` en grados.
- Todas las distancias y radios internos están en **grados angulares**. Solo `radio_region_km` y `altitud_km` están en km.
- Los nombres de variables, funciones y comentarios van en español.

## Clase `Evaluacion` (fitness.py)

| Campo | Tipo | Significado |
|---|---|---|
| `fitness` | float [0,1] | 0.85·cobertura_ponderada + 0.15·redundancia_alta |
| `valida` | bool | `violacion == 0` |
| `violacion` | float | Suma de grados de invasión |
| `cobertura_ponderada` | float [0,1] | |
| `redundancia_alta` | float [0,1] | |
| `regiones_cubiertas` | int | Regiones con cobertura ≥ umbral |
| `regiones` | list[dict] | Solo con `detalle=True`. Ver abajo. |
| `violaciones` | list[dict] | Solo con `detalle=True`: `{satelite, tipo, zona, invasion_grados}` |
| `suficientemente_buena` | bool | Criterio de la sección 7 del Entregable 1 |

Cada elemento de `regiones`:
`{id, nombre, prioridad, peso, cobertura, redundancia, cubierta, satelites_que_ven: [índices]}`

## Formato de `results/<escenario>_s<semilla>.json`

```json
{
  "escenario": { "...todo el escenario usado, incluye regiones, zonas_restringidas, objetos_ocupados..." },
  "parametros": { "poblacion": 60, "generaciones": 200, "...": "..." },
  "semilla": 42,
  "generaciones_ejecutadas": 120,
  "gen_suficiente": 32,
  "evaluaciones": 7322,
  "tiempo_s": 4.1,
  "inicial": {
    "satelites": [ { "id": 0, "lat": 12.3, "lon": -45.6 }, "..." ],
    "evaluacion": { "...Evaluacion con detalle..." }
  },
  "final": {
    "satelites": [ "..." ],
    "evaluacion": { "..." }
  },
  "historial": [
    { "generacion": 0, "mejor_fitness": 0.19, "mejor_valida": true,
      "promedio_fitness": 0.06, "peor_fitness": 0.0, "promedio_validos": 0.07,
      "pct_validos": 0.7, "cobertura_ponderada_mejor": 0.23,
      "regiones_cubiertas_mejor": 1, "violacion_mejor": 0.0, "diversidad": 52.1 }
  ]
}
```

- `inicial` = la mejor configuración de la **generación 0** (población aleatoria).
- `final` = la mejor configuración encontrada en toda la ejecución.
- La visualización 3D **solo** dibuja lo que está en estos archivos.

## Formato de `results/index.json`

```json
[ { "archivo": "base_s42.json", "escenario": "base", "semilla": 42,
    "fitness": 1.0, "valida": true, "regiones_cubiertas": 6 } ]
```

## Escenarios disponibles

| Archivo | Para qué prueba |
|---|---|
| `base.json` | Escenario oficial |
| `sin_restricciones.json` | Primera etapa / efecto de las restricciones |
| `reducido.json` | Espacio reducido (3 zonas nuevas) |
| `inviable.json` | Condición inviable (Yucatán imposible de cubrir) |
| `prioridades_cambiadas.json` | Cambio de condiciones 3.3 |