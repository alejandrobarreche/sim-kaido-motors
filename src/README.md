# Código del proyecto

`datos.py` carga y comprueba los CSV y prepara la serie mensual por segmento.
`demanda.py` ajusta el modelo de mercado y la cuota, valida con A012 y prevé A013.
`simulacion.py` planifica las llegadas, simula un año con stock FIFO, calcula costes,
comprueba el balance de unidades y repite el año con errores aleatorios.
`escenarios.py` traduce los sucesos de la tabla 4 del enunciado a parámetros de
demanda, cuota y suministro.
`analisis.ipynb`, en la raíz, llama a sus funciones.

Las responsabilidades, convenciones y comprobaciones están en la
[guía del proyecto](../docs/guia-proyecto.md).
