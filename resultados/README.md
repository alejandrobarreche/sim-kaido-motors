# Resultados generados

Salidas reproducibles de los notebooks:

- `datos/{tablas,figuras}/`: diagnóstico de los datos y demanda observada.
- `demanda/{tablas,figuras}/`: validación y previsión de la demanda.
- `simulacion/{tablas,figuras}/`: simulación determinista.
- `escenarios/{tablas,figuras}/`: escenarios, costes y plan recomendado.
- `tablas/` y `figuras/`: salidas del notebook completo `analisis.ipynb`.

Cada notebook crea y sobrescribe sus salidas al ejecutarse. Los archivos de entrada
permanecen en `data/`; los documentos de entrega están en `docs/`. Las carpetas
`tablas/` y `figuras/` de la raíz conservan la versión histórica: la entrega revisada
utiliza las carpetas de los cuatro notebooks nuevos.

Nombrar cada salida por contenido y periodo, por ejemplo
`produccion_mensual_a013.csv`. Aplicar la
[guía del proyecto](../docs/guia-proyecto.md) y regenerar las salidas desde el código,
sin corregir manualmente cifras o gráficos. Conservar para la entrega los resultados
finales y su configuración de ejecución.

## Configuración de la ejecución de entrega

- Versiones y parámetros efectivos:
  [`configuracion_ejecucion.json`](escenarios/tablas/configuracion_ejecucion.json).
- Semilla 42, piloto de 200 réplicas y 1.000 finales por escenario; los mismos
  errores aleatorios se utilizan al comparar políticas y escenarios.
- Supuestos: [`parametros_escenarios_a013.csv`](escenarios/tablas/parametros_escenarios_a013.csv)
  y [`parametros_incertidumbre_a013.csv`](escenarios/tablas/parametros_incertidumbre_a013.csv).
- Resultado principal: [`tabla5_plan_recomendado_a013.csv`](escenarios/tablas/tabla5_plan_recomendado_a013.csv),
  con medias, medianas y P10–P90 del total y de cada segmento.
- Pedidos iniciales y revisados son distintos de las llegadas. Las tablas conservan
  las fechas de decisión y recepción, incluidos los compromisos destinados a A014.
- Las sensibilidades son hipótesis alternativas, no probabilidades de escenarios.
  El servicio del 95 % es un objetivo medio central por segmento, no una garantía.

`escenarios.ipynb` genera el resumen y la presentación desde estas mismas tablas.
Sus PDF requieren LibreOffice; el código del generador está incluido en el notebook.
