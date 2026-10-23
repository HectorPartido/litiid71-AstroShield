# Uso de herramientas de inteligencia artificial

La actividad pide indicar si se usó IA, para qué se usó y qué verificaciones hizo el equipo. Este documento lo declara.

## Herramienta utilizada

**Claude** (Anthropic), en una conversación coordinada por Hector Partido Flores.

## Para qué se usó

| Uso | Detalle |
|---|---|
| Análisis de la actividad | Lectura de las instrucciones y la rúbrica; propuesta de cómo dividir el trabajo entre 5 integrantes |
| Propuesta del modelo | Representación (8 pares lat/lon), cobertura por muestreo de 37 puntos, pesos por prioridad, regla de factibilidad para las restricciones |
| Generación de código | Primer borrador de todos los módulos (`src/`, `tests/`, `experiments/`, `viz/`) y de los comandos de Git |
| Redacción de documentos | Borradores de los Entregables 1, 3, 4 y 5, el contrato entre módulos y este README |
| Ejecución de experimentos | La IA corrió las pruebas en su entorno antes de entregarlas. Así encontró los dos defectos que documentamos: el peso de redundancia (P11) y el criterio de paro (P12). |

## Qué verificó el equipo

- [x] Cada integrante instaló el proyecto en su propia computadora y ejecutó `pytest` (55 pruebas en verde).
- [x] Anthony ejecutó `python experiments/correr_pruebas.py` y comparó `results/experimentos/resumen.md` contra los números de los Entregables 3 y 4. Se corrigió cualquier diferencia.
- [x] Hector Martínez verificó a mano, con la calculadora, el fitness de la configuración ideal (1.0) y el máximo teórico del escenario inviable: 0.9·10/13 + 0.1·0.5 = 0.7423.
- [x] Gildardo ejecutó el CLI con varias semillas y confirmó que la misma semilla da el mismo resultado.
- [x] Ismael abrió el visor y comprobó que las coordenadas de los satélites en `results/base_s42.json` coinciden con lo que se ve en el globo. También revisó que el escenario inviable muestre Yucatán en rojo.
- [x] Hector Partido revisó cada Pull Request antes de fusionarlo.
- [x] Se revisaron las decisiones propuestas por la IA y el equipo las acepta como propias, en particular:
  - alcance de 10°;
  - umbral de 90 %;
  - separación mínima de 2°;
  - pesos 3/2/1 y 0.9/0.1.

## Limitaciones de la IA que el equipo tomó en cuenta

- **El código generado puede tener errores aunque "corra".** Por eso hay 55 pruebas automáticas y experimentos con resultados conocidos de antemano: la configuración ideal y el máximo teórico del escenario inviable.
- **La primera versión del criterio de evaluación propuesta por la IA tenía un defecto:** premiaba más un respaldo que cubrir Australia. Se detectó con los experimentos y se corrigió (P11). Esto muestra que **no se aceptó el criterio sin probarlo**.
- **Los números de los documentos deben salir de nuestras propias ejecuciones**, no de las de la IA. Por eso el script genera `resumen.md` automáticamente.