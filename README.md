# Kaido Motors España: demanda, stock y beneficio

Trabajo de **Simulación de Sistemas Logísticos**, Universidad Alfonso X el Sabio.
Caso elaborado por Jacinto Velasco y Javier Goikoetxea. Profesor: Javier Goikoetxea.

El objetivo es prever la demanda mensual de los siete segmentos de Kaido para A013
y simular cómo afecta a la producción, el stock y el beneficio en tres escenarios.

> Material de uso exclusivamente docente. Los datos y los nombres están camuflados.
> No se permite su publicación ni redistribución sin autorización de los autores.

## Estado y punto de entrada

La solución revisada se encuentra en **`datos.ipynb`, `demanda.ipynb`,
`simulacion.ipynb` y `escenarios.ipynb`**. El
[plan de revisión](docs/plan-revision-modelo.md) recoge las 23 decisiones aprobadas
y su estado. La [auditoría](docs/auditoria-modelo.md) describe la versión inicial.

Los notebooks revisados contienen la lógica actual y comparten únicamente sus
celdas de definiciones etiquetadas `api`, cargadas en espacios independientes.
`src/datos.py` conserva la lectura y las comprobaciones originales. Los otros
módulos de `src/` y `analisis.ipynb` corresponden a la versión inicial y se
conservan como referencia; no producen la recomendación revisada.

Antes de trabajar, leer:

1. [Guía del proyecto](docs/guia-proyecto.md): decisiones compartidas de código,
   gráficos, redacción, nivel de detalle y orden de implementación. También es la
   referencia para los asistentes que trabajen en este repositorio.
2. [Enunciado en Markdown](docs/kaido-motors-case-study.md): preguntas, restricciones
   y anexos. El [PDF original](docs/kaido-motors-case-study.pdf) es la fuente del caso.
3. [Datos](data/README.md): contenido, nombres originales y reglas de lectura.

## Estructura actual

```text
Kaido-Motors/
├── README.md
├── requirements.txt
├── config/
│   └── graficos.mplstyle             # Estilo común de Matplotlib
├── data/                             # CSV de entrada y su inventario
├── docs/
│   ├── guia-proyecto.md              # Convenciones y siguientes fases
│   ├── kaido-motors-case-study.pdf   # Original del profesor
│   ├── kaido-motors-case-study.md    # Versión de lectura
│   ├── resumen-ejecutivo.docx/.pdf   # Resumen de dos páginas para el comité
│   ├── presentacion.pptx/.pdf        # Presentación de diez minutos
│   └── img/                         # Figuras del enunciado
├── examples/                         # Ejemplo del Anexo 4, con rutas actualizadas
├── src/
│   ├── datos.py                      # Lectura, comprobaciones y series mensuales
│   ├── demanda.py                    # Previsión histórica, conservada como referencia
│   ├── escenarios.py                 # Escenarios históricos
│   └── simulacion.py                 # Simulación histórica
├── resultados/                       # Salidas separadas por notebook y tipo
├── datos.ipynb                       # Datos y demanda observada
├── demanda.ipynb                     # Validación y previsión de demanda
├── simulacion.ipynb                  # Simulación determinista
├── escenarios.ipynb                  # Incertidumbre y recomendación
└── analisis.ipynb                    # Versión inicial, conservada como referencia
```

Cada notebook revisado guarda sus salidas en
`resultados/<notebook>/tablas/` y `resultados/<notebook>/figuras/`.
La preparación de datos, la previsión y el simulador tienen una única definición
activa en sus respectivos notebooks; las fases posteriores no ejecutan sus
gráficos ni leen resultados antiguos para reconstruir el modelo.

## Puesta en marcha

Python 3.10 o superior. Desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name kaido-motors --display-name "Python (kaido-motors)"
```

En Windows, activar con `.venv\Scripts\activate`.
Si ya se utiliza un entorno de Conda para este proyecto, instalar las dependencias
en ese entorno en lugar de crear otro.

Abrir Jupyter desde la raíz y ejecutar «reiniciar y ejecutar todo», en este orden:
`datos.ipynb` → `demanda.ipynb` → `simulacion.ipynb` → `escenarios.ipynb`.
Elegir el kernel del entorno donde se han instalado las dependencias. Los cálculos
son autónomos respecto a las salidas guardadas, pero requieren los notebooks de
definiciones presentes en el repositorio.

La última sección de `escenarios.ipynb` regenera Word, PowerPoint y sus PDF con
los resultados de la misma ejecución. Para convertir a PDF se necesita
**LibreOffice**: `soffice` en el PATH o la instalación habitual en macOS.
La semilla, versiones, tamaño del piloto y réplicas finales se guardan en
[`configuracion_ejecucion.json`](resultados/escenarios/tablas/configuracion_ejecucion.json).

## Leer los datos

Los CSV usan comas como separador y punto decimal. **Solo las celdas vacías son
datos ausentes**: `NA` es un código de modelo válido.

```python
from pathlib import Path

import pandas as pd

datos = Path("data")
mercado = pd.read_csv(
    datos / "mercado_mensual.csv", keep_default_na=False, na_values=[""]
)
```

El código del proyecto se ejecutará desde la raíz. Los CSV de `data/` son las
entradas originales: cualquier transformación se hará en memoria o se guardará
en `resultados/`. No abrir ni guardar estos CSV con Excel, que puede cambiar
separadores, decimales o el código `NA`.

## Ejemplo del profesor

- [`examples/annex4_demand_baseline.ipynb`](examples/annex4_demand_baseline.ipynb):
  explicación y visualizaciones.
- [`examples/annex4_demand_baseline.py`](examples/annex4_demand_baseline.py):
  versión en script; calcula la descomposición y la previsión.

```bash
python examples/annex4_demand_baseline.py
jupyter lab
```

El ejemplo usa STL y SARIMAX para el mercado del SUV medio, entrena hasta A011 y
prevé A012. Emplea los valores económicos reales de A012: es una evaluación
condicionada a conocer esas variables, no una previsión operativa completa.
Es material de referencia, no la solución del trabajo.

## Años y calendario

Los años van de A001 a A012; A013 es el futuro y solo tiene calendario conocido.
Para las librerías, A001 se representa como 2001, A002 como 2002, etc. En textos y
gráficos se mostrarán los códigos del caso, no esos años ficticios.

Los días laborables y la Semana Santa se toman de
`data/economia_eventos_mensuales.csv` y `data/calendario_mensual_a013.csv`.

## Entrega

- Resumen ejecutivo de **dos páginas**.
- Plan mensual por segmento y resultados de los tres escenarios según la tabla 5.
- Código y datos reproducibles del modelo y de la simulación.
- Presentación de **diez minutos**.

Resumen y presentación están en `docs/`: [resumen ejecutivo](docs/resumen-ejecutivo.pdf)
(Word y PDF) y [presentación](docs/presentacion.pdf) (PowerPoint y PDF). Sus cifras
proceden de `resultados/escenarios/`, no de las salidas de `analisis.ipynb`.

Puntos de consulta de la versión revisada:

- [Tabla 5: siete segmentos y total](resultados/escenarios/tablas/tabla5_plan_recomendado_a013.csv).
- [Pedidos del plan inicial, con fechas de decisión y llegada](resultados/escenarios/tablas/plan_pedidos_inicial_a013_a014.csv).
- [Política y servicio por segmento](resultados/escenarios/tablas/politica_recomendada_a013.csv).
- [Supuestos de escenarios](resultados/escenarios/tablas/parametros_escenarios_a013.csv).
- [Sensibilidades y límites del resultado](resultados/escenarios/tablas/sensibilidades_plan_recomendado.csv).

El objetivo del 95 % se refiere al **servicio anual medio del escenario central**
en segmentos viables; no garantiza ese nivel en cada réplica ni en los extremos.
A012 es evaluación retrospectiva, CSUV requiere una incertidumbre específica y
los efectos no identificados se presentan como sensibilidades explícitas.
