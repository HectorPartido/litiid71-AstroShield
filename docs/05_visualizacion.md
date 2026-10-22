# Entregable 5 — Visualización 3D de la constelación

**Responsable:** Ismael Alexander Hidalgo Aguilando

## Cómo abrirla

Desde la **raíz del repositorio**, con el entorno activado:

```bash
python -m http.server 8000
```

Luego abre en el navegador: <http://localhost:8000/viz/>

- Se necesita un servidor porque el navegador no deja que una página abierta con doble clic (`file://`) lea los archivos de `results/`.
- Se necesita internet la primera vez para descargar Three.js y los contornos de los continentes desde el CDN jsDelivr.
- Para abrir directamente una ejecución: `http://localhost:8000/viz/?archivo=inviable_s42.json`

## De dónde salen los datos

El visor **no tiene ninguna constelación escrita en el código**. Todo se lee de los archivos que genera `python -m astroshield.cli run`:

| Lo que se ve | Campo del JSON de resultados |
|---|---|
| Lista de ejecuciones | `results/index.json` |
| Regiones (posición y tamaño) | `escenario.regiones`, `escenario.radio_region_km` |
| Color de cada región | `final.evaluacion.regiones[i].cubierta` y `.cobertura` |
| Satélites | `final.satelites` (o `inicial.satelites`) |
| Altura de los satélites | `escenario.altitud_km` |
| Círculo de alcance de cada satélite | `escenario.radio_vision_grados` |
| Zonas de desechos | `escenario.zonas_restringidas` |
| Objetos ocupados y su exclusión | `escenario.objetos_ocupados` |
| Satélites en rojo con ⚠ | `evaluacion.violaciones` |
| Gráfica de evolución | `historial` (mejor, promedio, % válidos por generación) |
| Tabla de métricas | `inicial.evaluacion` y `final.evaluacion` |

Si se vuelve a correr el algoritmo con otra semilla o con otro escenario, el visor muestra la nueva configuración sin cambiar una sola línea.

## Qué distingue

| Elemento | Representación |
|---|---|
| Tierra | Esfera azul oscuro con contornos de continentes (Natural Earth 1:110m) y retícula cada 30° |
| Región cubierta / parcial / sin cubrir | Disco verde / ámbar / rojo de 300 km, con su % de cobertura |
| Satélites | Esferas azules a 800 km de altura, con una línea a su punto subsatelital |
| Alcance de cada satélite | Círculo azul translúcido de 10° |
| Configuración inicial (modo Comparar) | Satélites grises translúcidos, etiquetados como `ini N` |
| Zonas de desechos | Círculos rojos translúcidos con su nombre |
| Objetos ocupados | Cubo naranja en órbita + círculo naranja de exclusión |

## Controles

- **Arrastrar:** girar el globo. **Rueda:** acercar y alejar.
- **Final / Inicial / Comparar:** la mejor configuración encontrada, la mejor de la generación 0, o ambas encimadas.
- **Capas:** encender o apagar alcances, zonas, objetos y etiquetas.
- **Girar automáticamente:** rotación continua, útil para la presentación.

## Consistencia con el modelo

La conversión lat/lon → 3D y el trazo de círculos sobre la esfera usan la **misma fórmula del punto destino** que `src/astroshield/geo.py`. Por eso, si el modelo dice que un satélite ve una región, en el globo la región queda dentro de su círculo de alcance.

Las alturas de las capas (1.001–1.005 × radio terrestre) son solo para que no se encimen visualmente. No afectan ningún cálculo.