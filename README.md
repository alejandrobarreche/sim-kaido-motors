# Kaido Motors España: demanda, stock y beneficio

Trabajo de **Simulación de Sistemas Logísticos**, Universidad Alfonso X el Sabio.
Caso elaborado por Jacinto Velasco y Javier Goikoetxea. Profesor: Javier Goikoetxea.

El objetivo es prever la demanda mensual de los siete segmentos de Kaido para A013
y simular cómo afecta a la producción, el stock y el beneficio en tres escenarios.

> Material de uso exclusivamente docente. Los datos y los nombres están camuflados.
> No se permite su publicación ni redistribución sin autorización de los autores.

## Estado y punto de entrada

**Las cinco fases están completadas**: datos, previsión de la demanda, simulación
determinista, escenarios con incertidumbre y entrega. `src/datos.py` carga y
comprueba los CSV; `src/demanda.py` prevé la demanda mensual por segmento y
`src/escenarios.py` traduce los sucesos de la tabla 4 a parámetros y
`src/simulacion.py` simula un año de la cadena de suministro, también con
incertidumbre. `analisis.ipynb` documenta el diagnóstico de A012, la validación, la
previsión de A013, la simulación determinista y los tres escenarios con 1.000
repeticiones. Los documentos de entrega están en `docs/`.

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
│   ├── demanda.py                    # Modelo de mercado, cuota, validación y previsión
│   ├── escenarios.py                 # Parámetros de los tres escenarios y su demanda
│   └── simulacion.py                 # Plan de llegadas, stock FIFO, costes y Monte Carlo
├── resultados/                       # Tablas y figuras regenerables
└── analisis.ipynb                    # Hilo conductor del análisis
```

`analisis.ipynb` es el hilo conductor y llama a los módulos de `src/`. Las responsabilidades de cada módulo
están en la guía.

## Puesta en marcha

Python 3.10 o superior. Desde la raíz del repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows, activar con `.venv\Scripts\activate`.
Si ya se utiliza un entorno de Conda para este proyecto, instalar las dependencias
en ese entorno en lugar de crear otro.

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

## Entrega prevista

- Resumen ejecutivo de **dos páginas**.
- Plan mensual por segmento y resultados de los tres escenarios según la tabla 5.
- Código y datos reproducibles del modelo y de la simulación.
- Presentación de **diez minutos**.

Resumen y presentación están en `docs/`: [resumen ejecutivo](docs/resumen-ejecutivo.pdf)
(Word y PDF) y [presentación](docs/presentacion.pdf) (PowerPoint y PDF). Sus cifras
proceden de `resultados/tablas/`; si cambia el análisis, hay que regenerarlos. La
sección 5 del notebook contiene la tabla 5 completa y el plan mensual recomendado.
