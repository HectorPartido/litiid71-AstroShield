# AstroShield — Evolucionar una constelación inteligente

Proyecto de **Fundamentos de Inteligencia Artificial** (grupo LITIID71). Un algoritmo evolutivo diseña una constelación de **8 satélites** para observar 6 regiones de la Tierra. La constelación respeta zonas de desechos espaciales y posiciones ocupadas. El resultado se explora en un **globo 3D**.

## Equipo

| Integrante | Rol |
|---|---|
| Hector Partido Flores | Coordinación, integración, geometría y escenarios |
| Hector Martínez Sánchez | Función de evaluación y restricciones |
| Gildardo Emmanuel González García | Algoritmo evolutivo y línea de comandos |
| Ismael Alexander Hidalgo Aguilando | Visualización 3D |
| Anthony Oziel Ramos López | Pruebas, experimentos y análisis |

## Estructura

```
config/escenarios/   Escenarios en JSON (base, reducido, inviable, ...)
src/astroshield/     Código fuente (geo, escenario, restricciones, fitness, ga, cli)
tests/               Pruebas automáticas (pytest)
experiments/         Scripts que generan las pruebas, gráficas y tablas
results/             Resultados reales de las ejecuciones (JSON + CSV)
viz/                 Visualización 3D (Three.js)
docs/                Entregables escritos
```

## Instalación

Requiere **Python 3.10 o superior** y **Git**.

```bash
git clone https://github.com/HectorPartido/astroshield.git
cd astroshield
```

**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

*(Se completa al integrar el algoritmo y la visualización.)*

## Documentación

- [Entregable 1 — Definición del problema](docs/01_definicion_problema.md)
- [Contrato entre módulos](docs/contrato.md)