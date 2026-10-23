# Entregable 1 — Definición del problema

**Proyecto:** AstroShield — Evolucionar una constelación inteligente
**Materia:** Fundamentos de Inteligencia Artificial · Grupo LITIID71
**Equipo:** Hector Partido Flores · Ismael Alexander Hidalgo Aguilando · Hector Martínez Sánchez · Gildardo Emmanuel González García · Anthony Oziel Ramos López

Este documento fija las decisiones que convierten el escenario en un problema computacional. Todos los valores numéricos viven en `config/escenarios/base.json`, así que se pueden cambiar sin tocar el código.

---

## 0. Supuestos del modelo (simplificaciones)

1. La Tierra es una **esfera perfecta** de radio 6,371 km. Las distancias se miden como **ángulo central** (grados) con la fórmula de haversine. 1° ≈ 111.2 km.
2. **No simulamos órbitas.** Cada satélite se modela como un punto fijo en el cielo sobre una posición (lat, lon) de la Tierra, su *punto subsatelital*. La actividad aclara que no se exige mecánica orbital real.
3. Todos los satélites están a la **misma altitud** (800 km). La altitud solo se usa para dibujarlos en 3D; no cambia el cálculo.
4. Las zonas restringidas y de exclusión se interpretan como **conos** desde el centro de la Tierra. Un satélite está dentro de la zona si su punto subsatelital está a menos de `radio` grados del centro de la zona, sin importar la altitud.

## 1. Representación de una configuración

Una configuración (individuo) es una matriz de **8 × 2 números reales**:

```
[[lat_0, lon_0],
 [lat_1, lon_1],
 ...
 [lat_7, lon_7]]      lat ∈ [-90, 90], lon ∈ [-180, 180)
```

- Cada fila es un satélite.
- Se eligió **codificación real** y no binaria porque las posiciones son continuas y la mutación gaussiana tiene sentido físico: "mover el satélite unos grados".
- El número de satélites es un parámetro (`num_satelites`), lo que permite la prueba propia de variar la cantidad.

## 2. ¿Qué significa que una región esté cubierta?

- Cada satélite **observa** un círculo sobre la Tierra de radio angular `radio_vision_grados = 10°` (≈ 1,112 km) alrededor de su punto subsatelital.
  - Justificación: es un orden de magnitud realista para un satélite de observación a ~800 km con un sensor de campo amplio. Además hace que **cada satélite alcance como máximo una región**, porque las 6 regiones están separadas por más de 20°. Así el problema no es trivial: se necesita al menos 1 satélite por región.
- Cada región es un **disco de 300 km** (≈ 2.70°) alrededor de su centro. Se representa con **37 puntos de muestra**: el centro más 3 anillos de 6, 12 y 18 puntos.
- **Cobertura de una región** = fracción de sus 37 puntos que ve al menos un satélite (de 0 a 1).
- Una región está **CUBIERTA** si su cobertura es **≥ 0.9** (`umbral_cobertura`). Se usa 0.9 y no 1.0 para aceptar una cobertura prácticamente total sin exigir precisión perfecta en el borde.
- **Redundancia de una región** = fracción de sus puntos vista por **2 o más** satélites.

## 3. Calidad de una configuración (fitness)

Las prioridades se traducen en **pesos**: Alta = 3, Media = 2, Normal = 1. Así una región Alta vale el triple que una Normal.

```
cobertura_ponderada = Σ (peso_r × cobertura_r) / Σ peso_r          ∈ [0, 1]
redundancia_alta    = promedio de redundancia_r en regiones Alta    ∈ [0, 1]

fitness = 0.90 × cobertura_ponderada + 0.10 × redundancia_alta      ∈ [0, 1]
```

- **Por qué la redundancia:** hay 8 satélites y 6 regiones. Sin este término, los 2 satélites sobrantes no aportarían nada y el algoritmo los dejaría en cualquier lugar. Con él, se usan para respaldar las regiones más importantes (si un satélite falla, la región Alta sigue vigilada).
- **Por qué 0.90 / 0.10:** el peso del respaldo es el parámetro `peso_redundancia` del escenario. Cubrir la región de menor peso (Australia, Normal) aporta 0.90 × 1/13 ≈ 0.069. Respaldar por completo una región Alta aporta 0.10 × ½ = 0.05. Así **cubrir una región nueva siempre vale más que reforzar una ya cubierta**.
- **Corrección tras las pruebas:** la primera versión usaba 0.85 / 0.15. Con esos pesos, el respaldo de una región Alta (0.075) valía más que cubrir Australia (0.065). En la primera detección (todavía con el criterio de paro original de 80 generaciones), 3 de 10 ejecuciones dejaron Australia sin cubrir para poner un segundo satélite sobre Amazonía; con la configuración final del algoritmo la batería mide 1 de 10. La prueba P11 del Entregable 3 documenta el antes y el después.

## 4. Configuraciones inválidas

Una configuración es **inválida** si se cumple cualquiera de estas condiciones:

| Restricción | Condición de violación | Origen |
|---|---|---|
| Zonas de desechos (Atlántico Norte 12°, Pacífico Sur 10°, Polar Norte 8°) | distancia(satélite, centro) < radio | Actividad 3.1 |
| Objetos ocupados (Objeto A 5°, Objeto B 5°) | distancia(satélite, objeto) < radio | Actividad 3.2 |
| Separación mínima entre satélites propios | distancia(sat_i, sat_j) < 2° | Decisión del equipo (evita satélites encimados o colisiones) |

Para cada configuración se calcula la **violación total** = suma de los grados de invasión. Si es 0, la configuración es válida.

### Tratamiento de restricciones: regla de factibilidad (Deb, 2000)

No se descartan las configuraciones inválidas, porque se perdería información. Se comparan así:

1. Una configuración **válida siempre le gana** a una inválida, aunque la inválida tenga mejor cobertura.
2. Entre dos válidas, gana la de **mayor fitness**.
3. Entre dos inválidas, gana la que **viola menos**.

Esto garantiza que la solución final reportada **nunca sea inválida** si existe al menos una válida. También guía a las inválidas hacia el espacio permitido.

Se descartó usar una **penalización fija** (fitness − k·violación) porque obliga a calibrar k: si es muy chica se aceptan soluciones inválidas, y si es muy grande se pierde la búsqueda. También se descartó **eliminar** las inválidas, porque la población inicial aleatoria tiene ~30 % de inválidas y se perdería diversidad.

## 5. Estrategia del algoritmo evolutivo

Algoritmo genético generacional con elitismo:

1. **Población inicial:** 60 configuraciones aleatorias, uniformes **en área** sobre la esfera (para no amontonar puntos en los polos). No se filtran inválidas, para demostrar que el algoritmo las corrige.
2. **Evaluación:** fitness + violación de cada configuración.
3. **Elitismo:** las 2 mejores pasan intactas a la siguiente generación, así la mejor solución nunca empeora.
4. **Selección por torneo (k = 3):** se eligen 3 al azar y gana la mejor según la regla de factibilidad. Mantiene presión selectiva sin perder diversidad tan rápido como la ruleta.
5. **Cruza uniforme por satélite (pc = 0.9):** cada satélite del hijo se hereda completo del padre 1 o del padre 2. No se cruzan lat y lon por separado porque un satélite "bueno" es el par completo.
6. **Mutación:**
   - *Gaussiana* (pm = 0.15 por satélite, σ = 5°): ajuste fino de la posición (explotación).
   - *Reubicación* (0.03 por satélite): el satélite salta a un punto aleatorio del globo (exploración). Se agregó porque en pruebas preliminares el algoritmo se estancaba con regiones lejanas (Sahel, Australia) que ningún satélite alcanzaba. Ningún paso gaussiano de 5° las acercaba, porque la cobertura no cambia hasta que el satélite queda a ≤ 10°.
   - Si una mutación pasa del polo, el punto reaparece del otro lado (normalización de coordenadas).
7. Se repite hasta el criterio de paro.

## 6. Parámetros y valores iniciales

| Parámetro | Valor | Cómo se eligió |
|---|---|---|
| `num_satelites` | 8 | Dato de la actividad |
| `radio_vision_grados` | 10° | Ver sección 2 |
| `radio_region_km` | 300 | Dato de la actividad |
| `umbral_cobertura` | 0.9 | Ver sección 2 |
| `separacion_minima_grados` | 2° | Decisión del equipo |
| `peso_redundancia` | 0.10 | Ver sección 3 (calibrado con la prueba P11) |
| `poblacion` | 60 | Alrededor de 7 veces el número de satélites. Evaluar 60 individuos tarda milisegundos. |
| `generaciones` | 300 | Límite superior. Se subió de 200 a 300 junto con la paciencia (ver prueba P12). |
| `prob_cruza` | 0.9 | Valor típico de la literatura de AG |
| `prob_mutacion` | 0.15 | ≈ 1/8 satélites → en promedio 1 satélite mutado por hijo |
| `sigma_mutacion` | 5° | Menor que el radio de visión (10°): ajusta sin "perder" la región |
| `prob_reubicar` | 0.03 | Pequeña: exploración ocasional sin destruir buenas soluciones |
| `torneo_k` | 3 | Presión selectiva moderada |
| `elitismo` | 2 | Conserva las 2 mejores |
| `paciencia` | 150 | Generaciones sin mejora antes de detenerse. Con 80, la semilla 42 se detenía en un óptimo local con 5/6 regiones; con 150 alcanza 6/6 (prueba P12). |
| `semilla` | 42 | Reproducibilidad. Se varía en las pruebas de variación. |

Los valores iniciales se toman de recomendaciones comunes para AG de codificación real y se ajustan con las pruebas del Entregable 3.

## 7. ¿Cuándo una solución es "suficientemente buena"?

Una configuración se considera suficientemente buena si cumple **las tres** condiciones:

1. Es **válida** (violación = 0).
2. **Todas las regiones de prioridad Alta** están cubiertas.
3. **Cobertura ponderada ≥ 0.95.** Con los pesos actuales, dejar sin cubrir solo Australia (peso 1/13) ya baja la cobertura a 0.92. En la práctica, esto exige cubrir las 6 regiones casi por completo.

El programa registra **en qué generación** se alcanzó este criterio (`gen_suficiente`). Que el algoritmo deje de mejorar **no** prueba que encontró el óptimo. Por eso comparamos varias semillas y conocemos el valor máximo teórico (fitness = 1.0).

## 8. Cambios de condiciones (actividad 3.3)

Cada escenario es un archivo JSON. Un escenario derivado puede **heredar** del base y declarar solo lo que cambia: agregar o quitar zonas, cambiar prioridades. El comando `reevaluar` toma una configuración ya obtenida y la evalúa bajo condiciones nuevas. Reporta si **sigue siendo válida** y cómo cambian su fitness y su cobertura.