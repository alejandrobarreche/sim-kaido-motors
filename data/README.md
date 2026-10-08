# Datos de entrada

Los siete CSV proceden del material del profesor. Se han cambiado sus nombres para
explicar mejor su contenido; se conservan sus columnas y valores originales.
El diccionario de variables está en el **Anexo 5** del
[enunciado](../docs/kaido-motors-case-study.md).

## Inventario y equivalencias

| Nombre actual | Nombre en el material original | Una fila por | Cobertura | Filas |
|---|---|---|---|---:|
| `ventas_kaido_mensuales.csv` | `ventas_mensual.csv` | Mes, segmento y canal | A003–A012 | 2.520 |
| `stock_red_mensual.csv` | `stock_mensual.csv` | Mes y segmento | A009–A012 | 336 |
| `mercado_mensual.csv` | `mercado_mensual.csv` | Mes, segmento y canal | A001–A012 | 3.024 |
| `economia_eventos_mensuales.csv` | `macro_mensual.csv` | Mes | A001–A012 | 144 |
| `catalogo_segmentos.csv` | `segmentos.csv` | Segmento | Ficha y márgenes del caso | 7 |
| `catalogo_modelos.csv` | `codigos.csv` | Código y generación | Historia y gama A013 | 76 |
| `calendario_mensual_a013.csv` | `calendario_A013.csv` | Mes | A013 | 12 |

Los nombres de archivo usan minúsculas y guiones bajos. Los identificadores dentro
de los CSV, como `A013`, `MSUV`, `NA` o `codigos_A013`, conservan su formato original.

## Lectura e interpretación

- UTF-8, separador coma y punto decimal; sin separadores de miles.
- Con pandas: `keep_default_na=False, na_values=[""]`.
- Una celda vacía no equivale a cero. Por ejemplo, la antigüedad de las ventas no
  está disponible antes de A009-02 y `wholesale` empieza en A009-02.
- `codigo_modelo` no identifica por sí solo una generación: usar también
  `generacion` al comprobar el catálogo de modelos.
- `periodo`, `anio`, `mes` y `t` describen el mismo orden temporal. No inferir el
  calendario laboral a partir del año ficticio usado por Python.
- Los campos `pct_*` y `*_pct` son proporciones (0,09 = 9 %). Las variables macro
  expresadas en porcentaje, como `paro`, vienen en puntos porcentuales
  (9,6 = 9,6 %), según la tabla 2 del enunciado.
- El mercado incluye Kaido. Las automatriculaciones están dentro de `unidades`;
  no son una categoría adicional que se deba sumar.
- `u_venta_especial` no es sinónimo de automatriculación: no restarla
  automáticamente al calcular ventas a clientes.
- La ficha de segmentos incorpora información de A011–A012 y de la tarifa A013;
  distinguir su uso para costes de su uso como predictor en una validación histórica.

## Conservación

Trabajar con estos archivos como entradas de solo lectura. Guardar datos derivados
en `resultados/`, acompañados de su procedimiento de cálculo. No duplicar los CSV
en carpetas `raw/` y `processed/` mientras no haya una necesidad real.
