# Auditoría de las cinco fases del modelo

**Fecha:** 8 de octubre de 2026.  
**Versión auditada:** commit `2b3303d`, con revisión de los commits de implementación
`386c558`, `b450fa8`, `1d9c389` y `2b3303d`.

**Seguimiento:** esta auditoría conserva la evaluación de la versión inicial.
La revisión ejecutada en los cuatro notebooks de fase, sus comprobaciones y los
límites que permanecen se documentan en el
[plan de revisión](plan-revision-modelo.md#10-ejecución-verificada-y-puntos-de-consulta).

## 1. Alcance y conclusión

La auditoría contrasta el [PDF original](kaido-motors-case-study.pdf), su
[versión de lectura](kaido-motors-case-study.md), los CSV originales, los cuatro
módulos de `src/`, el [notebook](../analisis.ipynb), las tablas de resultados y los
documentos de entrega.

**Hay errores importantes en la interpretación de la demanda, la calibración de los
escenarios y la traducción de los resultados a recomendaciones.** La base de código
funciona y muchas cuentas son correctas, pero no se pueden dar por cerradas las cinco
fases sin resolver esos problemas.

Se han recalculado en memoria la previsión, la simulación determinista y las 3.000
réplicas del plan recomendado. Reproducen los resultados guardados, salvo diferencias
numéricas despreciables. Por tanto, varios hallazgos afectan a los supuestos, al
método o a la interpretación, no a la correspondencia entre código y tablas.

Las 25 comprobaciones de datos pasan. Los balances de unidades comprobados también
se cumplen. No se ha ejecutado el notebook completo con sus exportaciones ni se han
modificado el código, los datos o los resultados para realizar esta auditoría.

Los hallazgos distinguen errores comprobados de limitaciones metodológicas. Las
comparaciones alternativas sirven para cuantificar su importancia; no constituyen
un modelo corregido ni una recomendación sustitutiva.

## 2. Fase 1: datos y demanda real

### 1. Se confunde la demanda total con la evolución de la gama sin CSUV

**Importancia: alta.**

El cálculo del −3,2 % elimina las automatriculaciones, todas las ventas a clientes
del nuevo segmento CSUV —1.192 coches— y el adelanto estimado de compras.

Las ventas del lanzamiento son demanda de clientes. Excluirlas permite estudiar la
evolución de la gama anterior, pero no concluir que la demanda total de Kaido cayó.

Manteniendo CSUV y descontando únicamente el adelanto estimado en los otros
segmentos, sus mismas cuentas dan aproximadamente **+2,9 %**, no −3,2 %. Esto
tampoco determina el crecimiento real exacto: falta estimar el adelanto de CSUV y
la demanda no atendida. Sí demuestra que el titular de la presentación, «En A012 la
demanda de clientes cayó; no creció», no está justificado por ese cálculo.

**Evidencia:** `analisis.ipynb`, sección 1.6;
[`crecimiento_demanda_a012.csv`](../resultados/tablas/crecimiento_demanda_a012.csv);
[`presentacion.pdf`](presentacion.pdf), diapositiva 2.

### 2. La incertidumbre del crecimiento se comunica con demasiada contundencia

**Importancia: media.**

El rango de adelanto, aproximadamente 2–1.190 coches, procede de comparar dos
referencias estacionales: A009 y A010. No es un intervalo estadístico que cubra
todas las fuentes de incertidumbre.

Además:

- Se supone, sin comprobarlo, que el adelanto y la caída de A011 se compensaron.
- No se cuantifican las ventas perdidas por falta de stock.
- CSUV queda fuera de la estimación.

El notebook reconoce buena parte de estas limitaciones, pero la entrega transforma
esa estimación parcial en una conclusión firme sobre la demanda.

**Evidencia:** `analisis.ipynb`, secciones 1.4 y 1.6;
[`resumen-ejecutivo.pdf`](resumen-ejecutivo.pdf), apartado 2.

La lectura de `NA`, la separación de automatriculaciones y los controles básicos
son correctos. Las discrepancias del balance histórico están identificadas y no se
han manipulado los datos para ocultarlas.

## 3. Fase 2: previsión

### 3. Se desaprovecha parte del histórico de mercado

**Importancia: alta.**

Existe una función que carga el mercado desde A001, pero la previsión utiliza el
mercado incorporado a la tabla de ventas de Kaido, que empieza en A003. Después,
las diferencias interanuales y el crecimiento retrasado hacen que el ajuste final
utilice observaciones desde A005, aunque hay mercado y economía desde A001.

| Comparación con las mismas reglas de ajuste | Observaciones | Demanda A013 (coches) |
|---|---:|---:|
| Entrada utilizada por el modelo | 576 | 18.471 |
| Serie completa de mercado | 715 | 17.686 |

La segunda cifra no es necesariamente mejor. La comparación demuestra que se pierde
información sin una justificación metodológica y con un efecto apreciable.

**Evidencia:** [`src/demanda.py`](../src/demanda.py), funciones `matrices_serie`,
`ajustar_mercado` y `prever_demanda`; `analisis.ipynb`, sección 2.

### 4. A012 no es una validación independiente de la selección del modelo

**Importancia: alta.**

Los coeficientes se entrenan hasta A011, lo cual es correcto. Sin embargo, el propio
notebook indica que se eligió la confianza comparando errores en A010–A012 y que se
eliminó la constante porque sobrestimaba A012.

A012 interviene, por tanto, en la selección del modelo y después en su evaluación.
El error obtenido no tiene la misma fuerza que una evaluación sobre un año que no
haya intervenido en esas decisiones.

Además, se conocen los sucesos futuros del año validado. Esto está declarado, pero
hace que la evaluación siga siendo condicionada.

**Evidencia:** `analisis.ipynb`, secciones 2.1–2.3;
[`src/demanda.py`](../src/demanda.py), documentación de `ajustar_mercado`.

### 5. La fiabilidad anunciada no cubre realmente los siete segmentos

**Importancia: media.**

El error total del 12–13 % se calcula sin CSUV, mientras que la previsión A013 incluye
unos 2.768 coches de ese segmento. Su cuota procede de septiembre y octubre de A012,
no tiene validación y su incertidumbre se toma prestada de otros segmentos.

Es una aproximación posible, pero el «error mensual esperado del 13 % en el total»
de la entrega no está validado para ese total ampliado.

Tampoco se modelan las renovaciones de producto en la cuota central. El notebook
reconoce esta omisión, por lo que la pregunta sobre previsión «con economía,
calendario y producto» queda resuelta solo parcialmente.

**Evidencia:** `analisis.ipynb`, secciones 2.1, 2.4 y 3.1;
[`validacion_a012_metricas.csv`](../resultados/tablas/validacion_a012_metricas.csv).

## 4. Fase 3: simulación determinista

### 6. Coste cero para los coches que llegan y se venden en el mismo mes

**Importancia: media; efecto económico comprobado.**

El simulador coloca tanto la llegada como la venta a mitad de mes. Esos coches
permanecen cero días y no generan coste de stock. El anexo 5 del caso utiliza
15 días para los coches facturados y vendidos dentro del mismo mes.

Es una diferencia respecto a la convención del caso, aunque el notebook declara su
aproximación. Aplicando esos 15 días únicamente a las ventas afectadas, sin cambiar
los flujos, el coste adicional sería:

| Simulación | Coste adicional de stock (€) |
|---|---:|
| Central determinista | 153.647 |
| Plan recomendado, media pesimista | 81.001 |
| Plan recomendado, media central | 108.270 |
| Plan recomendado, media optimista | 268.004 |

**Evidencia:** [`src/simulacion.py`](../src/simulacion.py), `avanzar_mes`, líneas
182–199; PDF original, anexo 5, página 16.

### 7. Se confunden llegadas, pedidos y fabricación

**Importancia: alta.**

Las tablas calculan y suman `llegadas`, pero las presentan como «coches fabricados».
No hay una tabla separada con el mes en que debe cursarse cada pedido.

La confusión llega a la recomendación «No pedir C hasta septiembre ni CSUV hasta
junio». Esos son los meses de llegada. Con la regla `t + 3`, para recibir C en
septiembre hay que decidirlo en junio; para recibir CSUV en junio, en marzo.
Seguir literalmente la instrucción retrasaría tres meses el abastecimiento.

Además, las llegadas de A013 incluyen producción comprometida en A012 y no recogen
los pedidos de final de A013 destinados a A014. **17.367 llegadas no equivalen a una
cifra comprobada de fabricación durante A013.**

**Evidencia:** `analisis.ipynb`, secciones 3 y 5;
[`plan_mensual_recomendado_a013.csv`](../resultados/tablas/plan_mensual_recomendado_a013.csv);
resumen ejecutivo, apartado 1; presentación, diapositiva 6.

### 8. Las automatriculaciones quedan pendientes

**Tipo: limitación relevante e incoherencia documental.**

En las fases 1 y 2 se afirma que se tratarán aparte en el simulador. Finalmente no
se simulan.

Esto puede defenderse como una política explícita de cero automatriculaciones, pero
implica cambiar el funcionamiento histórico del negocio. En A012 fueron 2.469
coches; su desaparición afecta a salidas de stock, necesidades de suministro y
costes.

El supuesto aparece en las limitaciones finales, pero las afirmaciones anteriores
siguen diciendo que se incorporarán.

**Evidencia:** `analisis.ipynb`, secciones 1.7, 2.4 y 3.1.

### 9. El cierre anual limita la recomendación económica

**Tipo: limitación relevante.**

Se elige el stock de seguridad buscando el mejor resultado de A013, pero no se
evalúa la continuidad operativa en A014 ni se incorpora el efecto económico
posterior del stock final.

El escenario central recomendado termina con unos 1.816 coches de stock, como media
entre réplicas. Ese remanente importa para comparar políticas, especialmente las
que dejan colchones distintos.

El resultado puede describirse como la mejor elección dentro del experimento
realizado, pero no como un óptimo económico completo.

**Evidencia:** `analisis.ipynb`, secciones 3.1 y 5;
[`simulacion_plan_recomendado_resumen_a013.csv`](../resultados/tablas/simulacion_plan_recomendado_resumen_a013.csv).

### Error histórico ya corregido: VM ausente de CSUV

En el commit de la fase 3 (`b450fa8`), el VM ausente de CSUV para más de 180 días
producía valores `NaN` que las sumas omitían. La fase 4 (`1d9c389`) lo corrigió y
regeneró las tablas: el resultado determinista total pasó de 63,18 a 65,21 M€.

Este fallo histórico ya no está presente. La solución actual imputa el VM del tramo
anterior para CSUV con más de 180 días.

## 5. Fase 4: escenarios e incertidumbre

### 10. El efecto de producto se estima con automatriculaciones incluidas

**Importancia: alta.**

La previsión representa compras de clientes, pero `efecto_renovacion` calcula el
efecto del producto usando matriculaciones totales. Repitiendo la misma comparación
y cambiando únicamente el numerador a ventas sin automatriculaciones:

| Efecto mediano de renovación | Variación |
|---|---:|
| Con matriculaciones totales | +11,23 % |
| Con ventas a clientes | +2,37 % |

El escenario utiliza +11 % para aumentar la demanda de clientes de cuatro segmentos
durante todo el año. Traslada a demanda real un efecto que incluye
automatriculaciones.

Con la misma regla de redondeo del proyecto, usar el efecto neto cambia la demanda
optimista de 24.346 a 22.713 coches: unos 1.633 menos. La comparación antes/después
tampoco demuestra por sí sola un efecto causal del lanzamiento.

**Evidencia:** [`src/escenarios.py`](../src/escenarios.py), líneas 61–71 y 127–128;
`analisis.ipynb`, sección 4.1.

### 11. La simulación elimina los sesgos de previsión observados

**Importancia: alta.**

Los errores aleatorios tienen media multiplicativa 1: en promedio, la demanda
coincide con la previsión. Sin embargo, la validación muestra errores sistemáticos:

- MD está sobreprevisto un 38,5 % en A012, con economía congelada.
- En las tres validaciones, la media de `observado / previsto` para MD es
  aproximadamente 0,783.

La simulación utiliza la dispersión, pero no reproduce ese sesgo ni lo corrige
previamente en el modelo. Estudia una demanda centrada en una previsión que la
evidencia histórica cuestiona.

Los rangos son válidos bajo el supuesto de previsión sin sesgo, no como reproducción
completa de los errores encontrados.

**Evidencia:** [`src/simulacion.py`](../src/simulacion.py), `factores_demanda`, líneas
335–361; `analisis.ipynb`, secciones 2.2 y 4.1.

### 12. Los escenarios no representan todos los factores de la tabla 4

**Tipo: alcance incompleto, reconocido parcialmente.**

Quedan fuera paro, crédito, combustible, tipo de cambio y arancel. La falta de
columnas directas justifica no estimar automáticamente ciertos efectos, pero no
convierte esos riesgos en inexistentes. El arancel se menciona como sensibilidad
económica y después no entra en los resultados pesimistas.

Los 7,1 M€ del pesimista corresponden al conjunto reducido de supuestos
implementados, no a toda la historia pesimista del enunciado.

**Evidencia:** [`src/escenarios.py`](../src/escenarios.py); `analisis.ipynb`,
sección 4.1; enunciado, tabla 4.

## 6. Fase 5: recomendación y entrega

### 13. Se atribuye toda la diferencia central–pesimista al CO2

**Importancia: alta.**

La entrega dice que la prima de CO2 cambia el resultado de 63,5 a 7,1 M€. Entre
esos escenarios también cambian demanda, producto, turismo y suministro.

Al aislar la prima sobre las mismas réplicas centrales, manteniendo todo lo demás:

| Comparación | Resultado mediano (M€) |
|---|---:|
| Central sin prima | 63,50 |
| Central con prima | 9,26 |
| Pesimista completo | 7,10 |

La prima sigue siendo decisiva, pero la atribución cuantitativa está mal formulada.

**Evidencia:** resumen ejecutivo, apartado 6; presentación, diapositiva 8;
`analisis.ipynb`, conclusión final. Comparación recalculada con las mismas réplicas.

### 14. El coste de quedarse corto en el pesimista no descuenta el CO2 evitado

**Importancia: alta para la interpretación económica.**

Las ventas perdidas se valoran con el CVP sin prima, aunque en el pesimista vender
también obliga a pagar CO2. Con las medias del plan recomendado:

| Concepto | Importe (M€) |
|---|---:|
| CVP no obtenido | 1,339 |
| Prima evitada por no vender esos coches | 1,424 |
| Margen neto no obtenido, antes de otros efectos | −0,086 |

El CVP perdido sin prima puede mostrarse como indicador separado. El error es
interpretarlo como pérdida económica neta: en B y C, algunas ventas adicionales
darían pérdidas bajo ese escenario.

**Evidencia:** [`src/simulacion.py`](../src/simulacion.py), líneas 404–407;
[`coste_de_equivocarse_a013.csv`](../resultados/tablas/coste_de_equivocarse_a013.csv);
resumen por segmento del plan recomendado y `prima_co2_eur` del catálogo.

### 15. La figura del resumen corresponde al plan anterior

**Importancia: alta.**

La tabla del resumen utiliza el plan recomendado, pero su figura procede de
`escenarios_ventas_stock_mensual_a013.png`, generado con el plan base de
`z = 1,28`.

Por ejemplo, el stock central de diciembre tiene una mediana de 1.112,5 coches con
el plan del gráfico y de 1.810,5 con el plan recomendado. El mismo documento mezcla
resultados de dos políticas distintas sin indicarlo.

**Evidencia:** [`resumen-ejecutivo.pdf`](resumen-ejecutivo.pdf), página 2; imagen
incrustada en el Word; generación de la figura en la fase 4 del notebook.

### 16. Los umbrales de revisión se calculan sobre otra magnitud

**Importancia: media.**

La regla operativa compara el cociente entre la suma de ventas de tres meses y la
suma de previsiones de esos meses. Los umbrales, en cambio, se obtienen promediando
errores logarítmicos y exponenciando: una media geométrica de cocientes mensuales,
que no es la misma magnitud.

En C, el rango publicado es 0,822–1,460. Calculando los percentiles sobre el cociente
de sumas anunciado, se obtiene 0,863–1,376. Además, falta un umbral específico para
CSUV.

**Evidencia:** última celda de código de `analisis.ipynb`;
[`umbrales_revision_a013.csv`](../resultados/tablas/umbrales_revision_a013.csv).

### 17. La comparación de ocho años parado contradice el límite de coste

**Importancia: media.**

El notebook divide el margen de MSUV entre 60 €/mes y afirma que un coche tendría
que sobrar más de ocho años para igualar una venta perdida. El coste para la marca
se detiene a los 180 días, con un máximo de 360 € por coche: no puede extrapolarse
linealmente durante ocho años.

La conclusión de que una venta perdida de MSUV cuesta mucho puede mantenerse; esa
justificación concreta es incorrecta.

**Evidencia:** `analisis.ipynb`, fase 5, explicación de economía unitaria;
[`economia_unitaria_segmento.csv`](../resultados/tablas/economia_unitaria_segmento.csv);
enunciado, sección 2.4.

### 18. Otros errores de presentación y trazabilidad

- **Suma de medianas.** El gráfico del plan recomendado suma medianas por segmento
  y lo etiqueta como mediana del total. En diciembre muestra 1.825 coches, frente a
  la mediana total correcta de 1.810,5. Evidencia: celda de generación de
  `plan_recomendado_segmento_a013.png` y resumen del plan recomendado.
- **Coberturas intercambiadas.** La conclusión final asigna 8,7 meses a C y 10,6 a
  CSUV; la tabla tiene C: 10,6 y CSUV: 8,7. Además, incluyen coches en camino, no
  solo stock disponible. Evidencia: conclusión de la fase 5 y
  [`estado_inicial_a013.csv`](../resultados/tablas/estado_inicial_a013.csv).
- **Tabla 5 incompleta en la entrega.** Se presenta el total, pero no todos los
  indicadores por segmento. Los datos están en CSV; el notebook solo muestra la
  tabla completa para el total, pese a lo anunciado en el README. Evidencia:
  llamadas a `tabla5` en el notebook y resumen ejecutivo.
- **Documentos no regenerables desde el código entregado.** Están los Word,
  PowerPoint y PDF, pero no el procedimiento que los genera.
- **Texto desactualizado.** La sensibilidad determinista afirma que no hay pérdidas
  con `z = 0` o `1,65`; la tabla registra 1,63 coches perdidos en ambos casos.
  Evidencia: final de la fase 3 y
  [`sensibilidad_simulacion_central_a013.csv`](../resultados/tablas/sensibilidad_simulacion_central_a013.csv).

## 7. Valoración final

Los balances, FIFO, reproducibilidad y gran parte de la contabilidad están bien
implementados. El trabajo proporciona una base aprovechable, pero no se pueden dar
por cerradas las cinco fases con la interpretación y la entrega actuales.

Los problemas que más comprometen las conclusiones son:

1. La interpretación del −3,2 % como caída de demanda de Kaido.
2. La calibración del +11 % por producto con automatriculaciones incluidas.
3. Una incertidumbre que ignora los sesgos observados.
4. La confusión entre pedir, fabricar y recibir.
5. La mezcla de planes y la atribución incorrecta del efecto del CO2.

Estos problemas afectan a qué se recomienda y a cómo puede defenderse el resultado,
no únicamente a la redacción.
