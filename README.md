# Kaido Motors España: demanda, stock y beneficio

Trabajo de **Simulación de Sistemas Logísticos**, Universidad Alfonso X el Sabio.
Caso elaborado por Jacinto Velasco y Javier Goikoetxea. Profesor: Javier Goikoetxea.

El proyecto prevé la demanda mensual de los siete segmentos de Kaido para A013 y
simula cómo afecta a la producción, el stock y el beneficio en tres escenarios.

> Material de uso exclusivamente docente. Los datos y los nombres están camuflados.
> No se permite su publicación ni redistribución sin autorización de los autores.

## El caso en breve

Kaido Motors España importa coches fabricados fuera de Europa y los vende a través
de 64 concesionarios. En A012 el mercado cayó y Kaido vendió más que nunca, pero la
red se llenó de coches viejos y el beneficio real quedó muy por debajo del previsto.
Hay que decidir cuántos coches fabricar en A013 sabiendo que lo que llegará en los
próximos tres meses ya está pedido.

El trabajo responde en cuatro fases:

1. **Datos**: comprobar los CSV, reconstruir la demanda observada por segmento y
   separar las compras adelantadas por sucesos de A011–A012.
2. **Demanda**: elegir el modelo con validación temporal antes de A012, evaluarlo
   en A012 y prever A013 por segmento en los escenarios central, optimista y pesimista.
3. **Simulación**: simular mes a mes llegadas, ventas y stock por cohortes (FIFO),
   con costes de stock, transferencias, CO2, aranceles y tipo de cambio.
4. **Escenarios**: repetir el año con errores aleatorios, elegir el colchón de
   seguridad de cada segmento y obtener la tabla 5 del enunciado.

Enunciado completo: [versión Markdown](docs/kaido-motors-case-study.md) y
[PDF original](docs/kaido-motors-case-study.pdf).

## Resultado principal

Plan recomendado para A013, media de 1.000 réplicas por escenario
([tabla 5 completa](results/escenarios/tablas/tabla5_plan_recomendado_a013.csv),
con medianas, P10–P90 y detalle por segmento):

| Escenario | Demanda (coches) | Ventas (coches) | Servicio | Resultado (M€) |
|---|---:|---:|---:|---:|
| Pesimista | 15.652 | 12.151 | 77,8 % | 3,1 |
| Central | 19.017 | 18.539 | 97,6 % | 62,9 |
| Optimista | 28.445 | 24.952 | 87,9 % | 91,4 |

El objetivo del 95 % se refiere al **servicio anual medio del escenario central**
en cada segmento viable; no garantiza ese nivel en cada réplica ni en los extremos.
Los escenarios no tienen probabilidades asignadas y las sensibilidades son
hipótesis alternativas. A012 es una evaluación retrospectiva y CSUV, al no tener
historia suficiente, usa una incertidumbre específica.

Otras tablas de consulta en `results/escenarios/tablas/`:

- [`politica_recomendada_a013.csv`](results/escenarios/tablas/politica_recomendada_a013.csv):
  colchón (`z`) y servicio por segmento.
- [`plan_pedidos_inicial_a013_a014.csv`](results/escenarios/tablas/plan_pedidos_inicial_a013_a014.csv):
  pedidos con fecha de decisión y de llegada, incluidos los destinados a A014.
- [`coste_de_equivocarse_a013.csv`](results/escenarios/tablas/coste_de_equivocarse_a013.csv):
  coste de aplicar el plan de un escenario cuando ocurre otro.
- [`parametros_escenarios_a013.csv`](results/escenarios/tablas/parametros_escenarios_a013.csv)
  y [`parametros_incertidumbre_a013.csv`](results/escenarios/tablas/parametros_incertidumbre_a013.csv):
  supuestos.
- [`sensibilidades_plan_recomendado.csv`](results/escenarios/tablas/sensibilidades_plan_recomendado.csv):
  límites del resultado.

## Documentos

- [Informe didáctico en LaTeX](docs/report/report.pdf): explicación completa de
  las fases, resultados y anexos ([instrucciones de compilación](docs/report/README.md)).
- [Resumen ejecutivo](docs/resumen-ejecutivo/resumen-ejecutivo.pdf) para el comité
  de dirección (dos páginas, fuente LaTeX en la misma carpeta).
- [Presentación](docs/presentacion/presentacion.pdf) de diez minutos (LaTeX/Beamer).

## Estructura

```text
Kaido-Motors/
├── README.md
├── requirements.txt
├── config/graficos.mplstyle      # Estilo común de Matplotlib
├── data/                         # CSV de entrada (solo lectura) y su inventario
├── docs/
│   ├── kaido-motors-case-study.pdf / .md   # Enunciado
│   ├── img/                      # Figuras del enunciado
│   ├── report/                   # Informe LaTeX y su PDF
│   ├── resumen-ejecutivo/        # Resumen de dos páginas (entrega)
│   └── presentacion/             # Presentación de diez minutos (entrega)
├── examples/                     # Ejemplo del Anexo 4 del profesor
├── notebooks/
│   ├── datos.ipynb               # Fase 1: datos y demanda observada
│   ├── demanda.ipynb             # Fase 2: validación y previsión
│   ├── simulacion.ipynb          # Fase 3: simulación determinista
│   └── escenarios.ipynb          # Fase 4: incertidumbre y recomendación
├── results/                      # Salidas de cada notebook: tablas/ y figuras/
└── src/                          # Módulos de Python
```

Cada notebook escribe en `results/<notebook>/tablas/` y `results/<notebook>/figuras/`
y sobrescribe sus salidas al ejecutarse. Los notebooks posteriores no leen esas
salidas para reconstruir el modelo: cargan únicamente las celdas de definiciones
etiquetadas `api` de los notebooks anteriores, en espacios independientes.
`src/datos.py` contiene la lectura y las comprobaciones de los CSV; el resto de
módulos de `src/` corresponde a la primera versión del modelo
(véase [`src/README.md`](src/README.md)).

## Puesta en marcha

Python 3.10 o superior (la ejecución de referencia usó 3.13). Desde la raíz:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m ipykernel install --user --name kaido-motors --display-name "Python (kaido-motors)"
jupyter lab
```

Ejecutar cada notebook con «reiniciar y ejecutar todo», en este orden:

```text
datos.ipynb → demanda.ipynb → simulacion.ipynb → escenarios.ipynb
```

Las rutas de los notebooks son relativas a la carpeta `notebooks/`. La simulación
de escenarios es la parte más lenta. Semilla, número de réplicas (piloto de 200 y
1.000 finales), horizonte y versiones de las bibliotecas se guardan en
[`configuracion_ejecucion.json`](results/escenarios/tablas/configuracion_ejecucion.json).
Los mismos errores aleatorios se reutilizan al comparar políticas y escenarios.

## Datos

Siete CSV del material del profesor, renombrados para describir su contenido
(ventas, stock de la red, mercado, economía, segmentos, modelos y calendario A013).
El inventario, las equivalencias con los nombres originales y las reglas de
interpretación están en [`data/README.md`](data/README.md). Lo esencial:

- Coma como separador y punto decimal. **Solo las celdas vacías son datos
  ausentes**: `NA` es un código de modelo válido.

  ```python
  import pandas as pd

  mercado = pd.read_csv("data/mercado_mensual.csv", keep_default_na=False, na_values=[""])
  ```

- Los CSV de `data/` no se modifican. No abrirlos ni guardarlos con Excel, que puede
  cambiar separadores, decimales o el código `NA`.
- Los años van de A001 a A012; A013 es el futuro y solo tiene calendario. Para las
  librerías, A001 se representa como 2001; en textos y gráficos se usan los códigos
  del caso.

## Ejemplo del profesor

[`examples/annex4_demand_baseline.ipynb`](examples/annex4_demand_baseline.ipynb) y su
versión en script [`annex4_demand_baseline.py`](examples/annex4_demand_baseline.py)
aplican STL y SARIMAX al mercado del SUV medio: entrenan hasta A011 y prevén A012
con los valores económicos reales de ese año. Es material de referencia, no la
solución del trabajo.

```bash
python examples/annex4_demand_baseline.py
```

## Entrega

Según el enunciado: resumen ejecutivo de dos páginas, plan mensual por segmento con
los resultados de los tres escenarios (tabla 5), código y datos reproducibles, y
presentación de diez minutos. Las cifras de todos los documentos proceden de
`results/escenarios/`.
