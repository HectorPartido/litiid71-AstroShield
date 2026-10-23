# Resumen de pruebas y experimentos (generado automáticamente)

Generado por `python experiments/correr_pruebas.py`. No editar a mano.

## P1. Escenario inicial (base, semilla 42)

- Fitness inicial → final: **0.2077 → 1.0000**
- Regiones cubiertas: **6/6**, válida: **True**, generación en que fue suficientemente buena: **119**, generaciones ejecutadas: 300

| Región | Prioridad | Cobertura | Redundancia | Cubierta | Satélites |
|---|---|---|---|---|---|
| Península de Yucatán, México | alta | 100% | 100% | sí | S0, S1 |
| Amazonía brasileña | alta | 100% | 100% | sí | S2, S3 |
| California, Estados Unidos | media | 100% | 0% | sí | S6 |
| Región del Sahel, África | media | 100% | 0% | sí | S5 |
| Japón | media | 100% | 0% | sí | S7 |
| Interior de Australia | normal | 100% | 0% | sí | S4 |


| Satélite | Latitud | Longitud |
|---|---|---|
| S0 | 24.6592 | -90.7567 |
| S1 | 25.3297 | -85.8736 |
| S2 | -1.1545 | -66.2705 |
| S3 | -1.4471 | -58.2631 |
| S4 | -27.9946 | 126.6602 |
| S5 | 13.4973 | 0.5629 |
| S6 | 38.6294 | -111.4923 |
| S7 | 39.1132 | 131.4582 |


## P2. Evolución (base, semilla 42)

| Gen | Mejor | Promedio | Peor | % válidos | Regiones (mejor) | Diversidad (°) |
|---|---|---|---|---|---|---|
| 0 | 0.2077 | 0.0628 | 0.0000 | 70% | 1 | 71.3 |
| 1 | 0.2414 | 0.0942 | 0.0000 | 97% | 1 | 68.6 |
| 2 | 0.3462 | 0.1475 | 0.0000 | 100% | 2 | 67.5 |
| 3 | 0.5538 | 0.2135 | 0.0000 | 98% | 3 | 64.4 |
| 4 | 0.6447 | 0.3127 | 0.0000 | 98% | 3 | 61.0 |
| 5 | 0.6773 | 0.4101 | 0.1403 | 95% | 3 | 54.6 |
| 6 | 0.7261 | 0.5070 | 0.1385 | 97% | 4 | 49.2 |
| 7 | 0.8204 | 0.5369 | 0.3087 | 98% | 4 | 49.0 |
| 9 | 0.8578 | 0.6326 | 0.3462 | 100% | 5 | 39.4 |
| 10 | 0.8591 | 0.6644 | 0.4210 | 98% | 5 | 37.6 |
| 11 | 0.8740 | 0.6868 | 0.3967 | 100% | 5 | 36.2 |
| 12 | 0.8808 | 0.7166 | 0.4565 | 100% | 5 | 31.6 |
| 25 | 0.9240 | 0.8315 | 0.6357 | 98% | 5 | 18.6 |
| 27 | 0.9308 | 0.8393 | 0.5571 | 100% | 5 | 21.9 |
| 119 | 0.9388 | 0.8774 | 0.6596 | 95% | 6 | 19.2 |
| 122 | 0.9432 | 0.8731 | 0.6731 | 98% | 6 | 20.3 |
| 123 | 0.9500 | 0.8905 | 0.7615 | 100% | 6 | 22.6 |
| 188 | 0.9662 | 0.8885 | 0.6038 | 97% | 6 | 25.2 |
| 191 | 0.9797 | 0.8837 | 0.5346 | 95% | 6 | 19.8 |
| 194 | 0.9824 | 0.8949 | 0.5816 | 97% | 6 | 20.0 |
| 195 | 0.9865 | 0.9012 | 0.6862 | 97% | 6 | 19.3 |
| 196 | 0.9932 | 0.9010 | 0.7004 | 100% | 6 | 16.0 |
| 197 | 1.0000 | 0.9120 | 0.7163 | 100% | 6 | 12.2 |
| 300 | 1.0000 | 0.9442 | 0.7923 | 98% | 6 | 15.3 |


## P3 y P4. Zonas restringidas y posiciones ocupadas

Se revisaron **90 soluciones finales** de todos los experimentos que tienen restricciones. *Margen* = distancia del satélite más cercano al borde de la zona (positivo = afuera).


| Zona | Tipo | Radio | Margen mínimo observado | Soluciones que la invaden |
|---|---|---|---|---|
| Atlántico Norte | desechos | 12° | 5.31° | 0 |
| Pacífico Sur | desechos | 10° | 18.98° | 0 |
| Región polar norte | desechos | 8° | 3.42° | 0 |
| Objeto A | ocupado | 5° | 4.54° | 0 |
| Objeto B | ocupado | 5° | 1.34° | 0 |


Soluciones finales inválidas: **0 de 90**.


**Contraprueba:** de las 10 soluciones obtenidas *sin* restricciones, **0** serían inválidas si se aplicaran las restricciones del escenario base:


| Semilla | Válida con restricciones | Zonas invadidas |
|---|---|---|
| 1 | sí | — |
| 2 | sí | — |
| 3 | sí | — |
| 4 | sí | — |
| 5 | sí | — |
| 6 | sí | — |
| 7 | sí | — |
| 8 | sí | — |
| 9 | sí | — |
| 10 | sí | — |


## P5, P6 y P7. Diez semillas por escenario

| Escenario | Fitness final (media ± desv.) | Regiones prom. | Corridas con 6/6 | Válidas | Suficientemente buena | Generaciones prom. |
|---|---|---|---|---|---|---|
| base | 0.9950 ± 0.0150 (mín 0.9500, máx 1.0000) | 6.0 | 10 | 10 | 10/10 (gen. media 22) | 224 |
| sin_restricciones | 1.0000 ± 0.0000 (mín 1.0000, máx 1.0000) | 6.0 | 10 | 10 | 10/10 (gen. media 28) | 230 |
| reducido | 1.0000 ± 0.0000 (mín 1.0000, máx 1.0000) | 6.0 | 10 | 10 | 10/10 (gen. media 50) | 261 |
| inviable | 0.7423 ± 0.0000 (mín 0.7423, máx 0.7423) | 5.0 | 0 | 10 | 0/10 | 166 |


### Detalle por semilla — escenario base (P7)

| Semilla | Fitness | Regiones | Gen. suficiente | Generaciones | Región sin cubrir |
|---|---|---|---|---|---|
| 1 | 1.0000 | 6 | 86 | 242 | — |
| 2 | 1.0000 | 6 | 19 | 186 | — |
| 3 | 1.0000 | 6 | 13 | 218 | — |
| 4 | 1.0000 | 6 | 10 | 259 | — |
| 5 | 1.0000 | 6 | 16 | 193 | — |
| 6 | 1.0000 | 6 | 17 | 222 | — |
| 7 | 1.0000 | 6 | 15 | 292 | — |
| 8 | 1.0000 | 6 | 15 | 175 | — |
| 9 | 1.0000 | 6 | 19 | 283 | — |
| 10 | 0.9500 | 6 | 13 | 169 | — |


### Cobertura promedio por región (10 semillas)

| Escenario | yucatan | amazonia | california | sahel | japon | australia |
|---|---|---|---|---|---|---|
| base | 100% | 100% | 100% | 100% | 100% | 100% |
| sin_restricciones | 100% | 100% | 100% | 100% | 100% | 100% |
| reducido | 100% | 100% | 100% | 100% | 100% | 100% |
| inviable | 0% | 100% | 100% | 100% | 100% | 100% |


**P6. Máximo teórico del escenario inviable:** si Yucatán (peso 3 de 13) no se puede ver, el mejor fitness posible es 0.90·10/13 + 0.10·0.5 = **0.7423** (Amazonía sí puede tener respaldo, Yucatán no). 10 de 10 corridas lo alcanzaron (máximo observado 0.7423).


## P8. Prueba propia A — ¿sirve la mutación de reubicación?

| Variante | Fitness final | Regiones prom. | Corridas con 6/6 | Suficientemente buena |
|---|---|---|---|---|
| Con reubicación (0.03) | 0.9950 ± 0.0150 (mín 0.9500, máx 1.0000) | 6.0 | 10 | 10 |
| Sin reubicación (0.0) | 0.8800 ± 0.0911 (mín 0.6538, máx 1.0000) | 5.1 | 3 | 3 |


## P9. Prueba propia B — ¿cuántos satélites hacen falta?

| Satélites | Fitness final | Regiones prom. | Redundancia Alta prom. | Suficientemente buena (de 5) |
|---|---|---|---|---|
| 4 | 0.6923 ± 0.0000 (mín 0.6923, máx 0.6923) | 4.0 | 0.00 | 0 |
| 5 | 0.8308 ± 0.0000 (mín 0.8308, máx 0.8308) | 5.0 | 0.00 | 0 |
| 6 | 0.9000 ± 0.0000 (mín 0.9000, máx 0.9000) | 6.0 | 0.00 | 5 |
| 7 | 0.9500 ± 0.0000 (mín 0.9500, máx 0.9500) | 6.0 | 0.50 | 5 |
| 8 | 1.0000 ± 0.0000 (mín 1.0000, máx 1.0000) | 6.0 | 1.00 | 5 |


## P10. Cambio de condiciones (3.3): ¿sigue siendo válida la solución de base_s42?

| Escenario nuevo | Fitness de la sol. vieja | Regiones | ¿Válida? | Violaciones | Fitness al re-ejecutar (s42) |
|---|---|---|---|---|---|
| prioridades_cambiadas | 0.9500 | 6 | sí | — | 1.0000 (6/6) |
| reducido | 1.0000 | 6 | NO | S7→mar_de_japon | 1.0000 (6/6) |
| inviable | 1.0000 | 6 | NO | S0→golfo_mexico, S1→golfo_mexico | 0.7423 (5/6) |


## P11. Prueba propia C — calibración del peso de redundancia

Mismo escenario base y mismas 10 semillas; solo cambia `peso_redundancia`.

| peso_redundancia | Corridas con 6/6 | Corridas que abandonan Australia | Cobertura prom. Australia | Suficientemente buena |
|---|---|---|---|---|
| 0.15 (original) | 9 | 1 | 90% | 9 |
| 0.10 (actual) | 10 | 0 | 100% | 10 |


## P12. Prueba propia D — criterio de paro (paciencia)

Mismas semillas; solo cambia cuántas generaciones sin mejora se toleran antes de detenerse.

| Semilla | Paciencia 80: fitness (gen. al parar) | Paciencia 150: fitness (gen. al parar) | ¿Mejoró al esperar más? |
|---|---|---|---|
| 1 | 1.0000 (172) | 1.0000 (242) | no |
| 2 | 1.0000 (116) | 1.0000 (186) | no |
| 3 | 1.0000 (148) | 1.0000 (218) | no |
| 4 | 1.0000 (189) | 1.0000 (259) | no |
| 5 | 1.0000 (123) | 1.0000 (193) | no |
| 6 | 1.0000 (152) | 1.0000 (222) | no |
| 7 | 0.9500 (98) | 1.0000 (292) | sí |
| 8 | 1.0000 (105) | 1.0000 (175) | no |
| 9 | 1.0000 (200) | 1.0000 (283) | no |
| 10 | 0.9500 (99) | 0.9500 (169) | no |
| 42 | 0.9308 (107) | 1.0000 (300) | sí |
