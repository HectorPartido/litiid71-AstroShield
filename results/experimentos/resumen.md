# Resumen de pruebas y experimentos (generado automáticamente)

Generado por `python experiments/correr_pruebas.py`. No editar a mano.

## P1. Escenario inicial (base, semilla 42)

- Fitness inicial → final: **0.1962 → 1.0000**
- Regiones cubiertas: **6/6**, válida: **True**, generación en que fue suficientemente buena: **32**, generaciones ejecutadas: 120

| Región | Prioridad | Cobertura | Redundancia | Cubierta | Satélites |
|---|---|---|---|---|---|
| Península de Yucatán, México | alta | 100% | 100% | sí | S2, S4 |
| Amazonía brasileña | alta | 100% | 100% | sí | S5, S7 |
| California, Estados Unidos | media | 100% | 0% | sí | S6 |
| Región del Sahel, África | media | 100% | 0% | sí | S1 |
| Japón | media | 100% | 0% | sí | S0 |
| Interior de Australia | normal | 100% | 0% | sí | S3 |


| Satélite | Latitud | Longitud |
|---|---|---|
| S0 | 40.1822 | 130.4589 |
| S1 | 19.4585 | -4.3967 |
| S2 | 25.093 | -94.6334 |
| S3 | -28.2875 | 129.9452 |
| S4 | 25.0591 | -90.9965 |
| S5 | -9.3927 | -66.1629 |
| S6 | 42.2202 | -124.1221 |
| S7 | -0.7149 | -64.3906 |


## P2. Evolución (base, semilla 42)

| Gen | Mejor | Promedio | Peor | % válidos | Regiones (mejor) | Diversidad (°) |
|---|---|---|---|---|---|---|
| 0 | 0.1962 | 0.0593 | 0.0000 | 70% | 1 | 71.3 |
| 1 | 0.2280 | 0.0890 | 0.0000 | 97% | 1 | 68.6 |
| 2 | 0.3274 | 0.1424 | 0.0000 | 100% | 1 | 67.9 |
| 3 | 0.5231 | 0.1969 | 0.0000 | 98% | 3 | 64.9 |
| 5 | 0.5652 | 0.3689 | 0.0424 | 98% | 3 | 56.6 |
| 6 | 0.6397 | 0.4465 | 0.1997 | 97% | 3 | 50.7 |
| 7 | 0.7253 | 0.4909 | 0.3163 | 97% | 3 | 46.2 |
| 8 | 0.7293 | 0.5362 | 0.2792 | 97% | 3 | 44.0 |
| 9 | 0.7501 | 0.5805 | 0.3269 | 95% | 3 | 42.0 |
| 10 | 0.7766 | 0.6191 | 0.3057 | 100% | 4 | 37.4 |
| 12 | 0.7836 | 0.6541 | 0.4094 | 95% | 5 | 31.1 |
| 13 | 0.8038 | 0.6890 | 0.4373 | 97% | 4 | 31.3 |
| 14 | 0.8445 | 0.7005 | 0.4582 | 88% | 4 | 34.9 |
| 15 | 0.8551 | 0.7145 | 0.4135 | 93% | 4 | 32.5 |
| 16 | 0.8692 | 0.7322 | 0.4814 | 98% | 5 | 32.2 |
| 32 | 0.8861 | 0.8191 | 0.6342 | 100% | 5 | 19.4 |
| 33 | 0.9073 | 0.8244 | 0.6016 | 98% | 5 | 18.1 |
| 34 | 0.9250 | 0.8239 | 0.5203 | 98% | 6 | 21.1 |
| 39 | 0.9432 | 0.8658 | 0.6440 | 93% | 6 | 20.8 |
| 40 | 1.0000 | 0.8613 | 0.6362 | 100% | 6 | 17.5 |
| 120 | 1.0000 | 0.9256 | 0.6546 | 97% | 6 | 14.4 |


## P3 y P4. Zonas restringidas y posiciones ocupadas

Se revisaron **90 soluciones finales** de todos los experimentos que tienen restricciones. *Margen* = distancia del satélite más cercano al borde de la zona (positivo = afuera).


| Zona | Tipo | Radio | Margen mínimo observado | Soluciones que la invaden |
|---|---|---|---|---|
| Atlántico Norte | desechos | 12° | 1.98° | 0 |
| Pacífico Sur | desechos | 10° | 2.79° | 0 |
| Región polar norte | desechos | 8° | 28.76° | 0 |
| Objeto A | ocupado | 5° | 10.85° | 0 |
| Objeto B | ocupado | 5° | 9.81° | 0 |


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
| base | 0.9654 ± 0.0348 (mín 0.9250, máx 1.0000) | 5.7 | 7 | 10 | 7/10 (gen. media 21) | 116 |
| sin_restricciones | 0.9850 ± 0.0300 (mín 0.9250, máx 1.0000) | 6.0 | 10 | 10 | 10/10 (gen. media 35) | 132 |
| reducido | 0.9860 ± 0.0282 (mín 0.9250, máx 1.0000) | 5.9 | 9 | 10 | 9/10 (gen. media 38) | 143 |
| inviable | 0.7288 ± 0.0000 (mín 0.7288, máx 0.7288) | 5.0 | 0 | 10 | 0/10 | 96 |


### Detalle por semilla — escenario base (P7)

| Semilla | Fitness | Regiones | Gen. suficiente | Generaciones | Región sin cubrir |
|---|---|---|---|---|---|
| 1 | 0.9346 | 5 | — | 91 | australia |
| 2 | 1.0000 | 6 | 19 | 157 | — |
| 3 | 0.9250 | 6 | 13 | 95 | — |
| 4 | 1.0000 | 6 | 14 | 138 | — |
| 5 | 1.0000 | 6 | 17 | 124 | — |
| 6 | 1.0000 | 6 | 18 | 108 | — |
| 7 | 0.9250 | 6 | 15 | 97 | — |
| 8 | 0.9346 | 5 | — | 105 | australia |
| 9 | 0.9346 | 5 | — | 106 | australia |
| 10 | 1.0000 | 6 | 52 | 134 | — |


### Cobertura promedio por región (10 semillas)

| Escenario | yucatan | amazonia | california | sahel | japon | australia |
|---|---|---|---|---|---|---|
| base | 100% | 100% | 100% | 100% | 100% | 70% |
| sin_restricciones | 100% | 100% | 100% | 100% | 100% | 100% |
| reducido | 100% | 100% | 100% | 100% | 100% | 90% |
| inviable | 0% | 100% | 100% | 100% | 100% | 100% |


**P6. Máximo teórico del escenario inviable:** si Yucatán (peso 3 de 13) no se puede ver, el mejor fitness posible es 0.85·10/13 + 0.15·0.5 = **0.7288** (Amazonía sí puede tener respaldo, Yucatán no). 10 de 10 corridas lo alcanzaron (máximo observado 0.7288).


## P8. Prueba propia A — ¿sirve la mutación de reubicación?

| Variante | Fitness final | Regiones prom. | Corridas con 6/6 | Suficientemente buena |
|---|---|---|---|---|
| Con reubicación (0.03) | 0.9654 ± 0.0348 (mín 0.9250, máx 1.0000) | 5.7 | 7 | 7 |
| Sin reubicación (0.0) | 0.8840 ± 0.0766 (mín 0.6731, máx 0.9346) | 5.1 | 3 | 3 |


## P9. Prueba propia B — ¿cuántos satélites hacen falta?

| Satélites | Fitness final | Regiones prom. | Redundancia Alta prom. | Suficientemente buena (de 5) |
|---|---|---|---|---|
| 4 | 0.6538 ± 0.0000 (mín 0.6538, máx 0.6538) | 4.0 | 0.00 | 0 |
| 5 | 0.7585 ± 0.0320 (mín 0.7192, máx 0.7846) | 5.0 | 0.00 | 0 |
| 6 | 0.8596 ± 0.0000 (mín 0.8596, máx 0.8596) | 5.0 | 0.50 | 1 |
| 7 | 0.9346 ± 0.0000 (mín 0.9346, máx 0.9346) | 5.0 | 1.00 | 1 |
| 8 | 0.9719 ± 0.0345 (mín 0.9250, máx 1.0000) | 5.8 | 0.90 | 4 |


## P10. Cambio de condiciones (3.3): ¿sigue siendo válida la solución de base_s42?

| Escenario nuevo | Fitness de la sol. vieja | Regiones | ¿Válida? | Violaciones | Fitness al re-ejecutar (s42) |
|---|---|---|---|---|---|
| prioridades_cambiadas | 0.9250 | 6 | sí | — | 1.0000 (6/6) |
| reducido | 1.0000 | 6 | NO | S0→mar_de_japon | 0.9346 (5/6) |
| inviable | 1.0000 | 6 | NO | S2→golfo_mexico, S4→golfo_mexico | 0.7288 (5/6) |


## P11. Prueba propia C — calibración del peso de redundancia

Mismo escenario base y mismas 10 semillas; solo cambia `PESO_REDUNDANCIA`. Se comparan métricas de cobertura (el fitness no es comparable entre pesos distintos).

| PESO_REDUNDANCIA | Corridas con 6/6 | Corridas que abandonan Australia | Cobertura prom. Australia | Redundancia Alta prom. | Suficientemente buena |
|---|---|---|---|---|---|
| 0.15 (actual en fitness.py) | 7 | 3 | 70% | 0.90 | 7 |
| 0.1 (variante) | 10 | 0 | 100% | 0.85 | 10 |


## P12. Prueba propia D — criterio de paro (paciencia)

Mismas semillas; solo cambia cuántas generaciones sin mejora se toleran antes de detenerse.

| Semilla | Paciencia 80: fitness (gen. al parar) | Paciencia 150: fitness (gen. al parar) | ¿Mejoró al esperar más? |
|---|---|---|---|
| 1 | 0.9346 (91) | 0.9346 (91) | no |
| 2 | 1.0000 (157) | 1.0000 (157) | no |
| 3 | 0.9250 (95) | 0.9250 (95) | no |
| 4 | 1.0000 (138) | 1.0000 (138) | no |
| 5 | 1.0000 (124) | 1.0000 (124) | no |
| 6 | 1.0000 (108) | 1.0000 (108) | no |
| 7 | 0.9250 (97) | 0.9250 (97) | no |
| 8 | 0.9346 (105) | 0.9346 (105) | no |
| 9 | 0.9346 (106) | 0.9346 (106) | no |
| 10 | 1.0000 (134) | 1.0000 (134) | no |
| 42 | 1.0000 (120) | 1.0000 (120) | no |
