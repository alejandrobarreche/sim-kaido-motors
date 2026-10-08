# Resultados generados

Salidas reproducibles de `analisis.ipynb`:

- `tablas/`: CSV numéricos de demanda, validación, producción, stock y costes.
- `figuras/`: gráficos finales en PNG y SVG.

El notebook crea y sobrescribe estas carpetas al ejecutarse. Los archivos de entrada
permanecen en `data/`; los documentos de entrega están en `docs/`.

Nombrar cada salida por contenido y periodo, por ejemplo
`produccion_mensual_a013.csv`. Aplicar la
[guía del proyecto](../docs/guia-proyecto.md) y regenerar las salidas desde el código,
sin corregir manualmente cifras o gráficos. Conservar para la entrega los resultados
finales y su configuración de ejecución.

## Configuración de la ejecución de entrega

- Python 3.13.15, numpy 2.5.3, pandas 3.0.6, statsmodels 0.15.0, scipy 1.18.1 y
  matplotlib 3.11.2.
- Semilla `numpy.random.default_rng(42)`, 1.000 repeticiones por escenario y los
  mismos errores aleatorios en los tres escenarios.
- Parámetros de los escenarios en `tablas/parametros_escenarios_a013.csv` y de la
  incertidumbre en `tablas/parametros_incertidumbre_a013.csv`.
