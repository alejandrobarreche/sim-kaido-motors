# Plan aprobado de revisión del modelo

**Fecha de aprobación:** 10 de octubre de 2026.  
**Estado:** implementado y comprobado el 10 de octubre de 2026.  
**Alcance:** revisión de las cinco fases y regeneración de la entrega.

Este documento recoge las decisiones metodológicas y de negocio aprobadas para
completar el proyecto. Es la referencia para su ejecución y consulta posterior.
Las decisiones de este plan fijan el método y los supuestos. Su ejecución y los
resultados verificados se recogen en las secciones 8 y 10; las magnitudes hipotéticas
no se convierten por ello en hechos observados.

Referencias:

- [Auditoría del modelo](auditoria-modelo.md): problemas que motivan la revisión.
- [Enunciado](kaido-motors-case-study.md): preguntas, reglas y datos del caso.
- [Guía del proyecto](guia-proyecto.md): convenciones de código, redacción y gráficos.

## 1. Objetivo y alcance aprobado

Completar una versión corregida, sencilla, reproducible y defendible del proyecto.
La cadena de razonamiento debe ser coherente:

**Datos → demanda de clientes → previsión → pedidos y llegadas → ventas y stock
→ resultado económico → recomendación.**

El modelo seguirá siendo mensual, por los siete segmentos y con la red agregada.
No es necesario simular individualmente los 64 concesionarios. Un proyecto completo
debe responder de forma verificable:

1. Qué ocurrió en A012, separando clientes, automatriculaciones, adelantos y posibles
   ventas perdidas.
2. Qué demanda se espera en A013 por mes y segmento, y qué fiabilidad tiene.
3. Qué cambia en cada escenario y qué incertidumbre existe dentro de él.
4. Qué se debe pedir y cuándo, respetando los compromisos en camino.
5. Qué política se recomienda y por qué, mostrando servicio, stock, beneficio y riesgo.

Corregir errores contables, de fechas o de presentación no requiere escoger una
política alternativa: hay que separar pedidos y llegadas, calcular correctamente
totales y percentiles, respetar los 180 días de coste y no mezclar resultados de
planes distintos.

La aprobación fija los criterios de trabajo. Los coeficientes, modelos concretos y
magnitudes aún no justificadas se resolverán con los datos y las comparaciones
descritas aquí; no se considerarán aprobados valores arbitrarios por adelantado.

## 2. Datos y demanda

### D1. Definición de demanda real

Distinguir tres conceptos:

- **Ventas a clientes:** matriculaciones descontando automatriculaciones.
- **Demanda no atendida:** clientes que habrían comprado y no pudieron por falta
  de coches; no se observa directamente en las ventas.
- **Demanda subyacente:** estimación ajustada para estudiar la evolución del negocio
  sin confundirla con desplazamientos temporales de compras.

Una compra adelantada de enero a diciembre es una compra real, pero no demuestra
que haya aparecido un cliente adicional.

**Decisión:** prever cuántos clientes querrán comprar y simular después cuántos
podrán ser atendidos. Presentar por separado el crecimiento del total de Kaido,
incluido CSUV, el de la gama comparable sin ese lanzamiento y la estimación ajustada
por adelantos y posibles restricciones de stock.

Excluir CSUV permite estudiar la gama anterior, pero no afirmar que cayó la demanda
total de la marca. Esta distinción condiciona la base del plan A013.

### D2. Compras adelantadas

El adelanto no se observa cliente a cliente: se estima frente a una referencia de
comportamiento normal. La diferencia entre las dos referencias históricas actuales
es sensibilidad al método, no un intervalo estadístico completo.

**Decisión:**

- Mantener una estimación central y alternativas razonables.
- Revisar cómo los desplazamientos de compras de A011 afectan a la comparación
  con A012; no dar por demostrada su compensación.
- Tratar CSUV aparte, por la coincidencia de lanzamiento y adelantos.
- Relacionar explícitamente el exceso estimado de A012 con la caída de A013.
- Evitar descontar el mismo efecto en la preparación de la demanda y otra vez en
  los escenarios.

Si se atribuyen 100 compras de A012 a un adelanto desde A013, esa transferencia no
debe convertirse en dos descuentos de 100 coches. Distinguir la duración de su
devolución —uno, tres o seis meses— de una caída económica adicional: son efectos
distintos y deben tener justificaciones separadas.

### D3. Posibles ventas perdidas históricas

El stock bajo es una señal de restricción, no una medida exacta de demanda perdida.
Si había diez coches y se vendieron diez, la demanda pudo ser diez, quince o veinte.

**Decisión:** conservar las ventas observadas como dato comprobado, marcar los meses
con indicios de restricciones y estudiar una demanda alternativa mediante una
referencia explícita. Comprobar cuánto cambia la previsión al utilizarla.

No evaluar el modelo contra una demanda reconstruida por él mismo como si esa
reconstrucción fuera la verdad observada. Cuando los datos no identifican una cifra
exacta, presentar la estimación y su sensibilidad es una respuesta válida al caso.

### D4. Automatriculaciones en A013

Quitarlas del histórico para medir demanda de clientes es una depuración. Hacerlas
desaparecer en A013 es una política comercial. La categoría histórica también
incluye coches de demostración.

**Decisión:** caso base sin automatriculaciones programadas en A013, declarado
explícitamente. No mantener promesas de incorporarlas si no se simulan.

Una alternativa con automatriculaciones requeriría definir cantidades, gasto
comercial, destino posterior de los vehículos e ingresos o valor recuperado. No
bastaría con retirarlos del stock y contarlos como clientes satisfechos. Su inclusión
cambiaría las salidas, el suministro y el resultado económico.

## 3. Previsión

### D5. Estructura y elección del modelo

Mantener la estructura del enunciado: demanda de Kaido como mercado del segmento
multiplicado por la relación comercial de Kaido con ese mercado. Así se separan la
evolución del mercado y la posición de la marca.

**Decisión:**

- Recuperar el histórico completo de mercado desde A001.
- Utilizar la historia interna disponible para estimar la posición de Kaido.
- Comparar una referencia estacional con un pequeño número de modelos económicos.
- Preferir el modelo más sencillo que funcione suficientemente bien en evaluaciones
  temporales; más histórico o complejidad no garantizan mejor previsión.

El mercado contiene matriculaciones y el numerador de Kaido será ventas a clientes.
La relación puede utilizarse para predecir, pero debe explicarse: no es sin más una
cuota de mercado calculada sobre magnitudes homogéneas.

La selección del algoritmo se resolverá mediante evidencia, no por preferencia
previa por una técnica.

### D6. Validación temporal

Validar significa situarse en una fecha pasada, prever lo siguiente y compararlo
con lo ocurrido, respetando la información disponible en esa fecha.

**Decisión:** comparar alternativas con años anteriores a A012, fijar las reglas,
evaluar A012 y reajustar después el modelo elegido con los datos hasta A012 para
prever A013.

A012 ya influyó en decisiones del modelo inicial. Repetir la evaluación no lo
convierte en un año nunca visto: se presentará como evaluación retrospectiva con
esa limitación.

Mostrar error medio en coches, sesgo, error relativo con denominador explicado,
resultados por segmento y total comparable, y error acumulado durante el plazo de
tres meses. Separar la evaluación anual inicial de la evaluación de revisiones
mensuales. Mantener la convención de error de la guía: previsión menos observado.

### D7. Economía futura

Un retraso de tres meses solo proporciona variables conocidas para los primeros
meses del horizonte; el resto de A013 sigue requiriendo supuestos.

**Decisión:**

- Central: continuidad de las condiciones del cierre de A012, salvo cambios
  explícitos del caso.
- Optimista y pesimista: trayectorias coherentes y cuantificadas.
- Pocas variables económicas, elegidas mediante validación.
- Separación visible entre evaluación operativa y evaluación condicionada a conocer
  la economía futura.

Las cifras A013 son previsiones condicionadas a estos supuestos, no resultados
obtenidos con información futura disponible.

### D8. Renovaciones de producto

Estimar con matriculaciones totales un efecto que se aplicará a compras de clientes
mezcla objetivos diferentes.

**Decisión:** reestimar el efecto con ventas a clientes, considerando la evolución
del mercado, y definir su inicio y duración. Incorporar las renovaciones previstas
también al central; representar en los extremos una acogida mejor o un retraso.

No sustituir automáticamente el 11 % por el 2,37 % citado en la auditoría: esa
comparación identifica el problema, pero no valida por sí sola el nuevo parámetro.
Una comparación antes/después tampoco demuestra causalidad.

Si faltan fechas de lanzamiento, definir un calendario supuesto y comprobar la
sensibilidad a su desplazamiento.

### D9. Tratamiento de CSUV

Su historia breve y el lanzamiento impiden asignarle la misma fiabilidad que a los
segmentos maduros.

**Decisión:** utilizar los meses disponibles con tratamiento explícito de lanzamiento
y adelantos, comprobar la sensibilidad a la selección de meses y presentar una
previsión central con incertidumbre específica.

Si se utilizan errores de otros segmentos, declararlo como aproximación y estudiar
alternativas. El error del total sin CSUV no valida la precisión del total que sí
lo incluye.

## 4. Escenarios e incertidumbre

### D10. Factores de cada escenario

Cada escenario debe traducirse a una tabla de supuestos cuantificados y trazables.

| Factor | Parte del modelo que modifica |
|---|---|
| Economía y crédito | Demanda del mercado |
| Adelantos y ayudas | Distribución temporal y nivel de demanda |
| Nuevos productos | Posición comercial de Kaido |
| Turismo | Demanda asociada a alquiladores |
| Combustible | Demanda, mediante una hipótesis explícita |
| Tipo de cambio y arancel | Costes de los vehículos afectados |
| Prima de CO₂ | Resultado de las ventas sujetas a ella |
| Interrupciones de fábrica | Producción disponible y llegadas posteriores |

**Decisión:** cubrir los factores del enunciado distinguiendo efectos estimados con
el histórico, supuestos apoyados en episodios comparables y sensibilidades sin datos
suficientes para una estimación directa.

Evitar impactos superpuestos: si la confianza ya recoge parte del deterioro
económico, otra penalización genérica puede duplicarlo. No aplicar porcentajes de
arancel o cambio de divisa al PVP sin base económica. Estudiar costes adicionales
por vehículo y puntos de equilibrio, diferenciando stock ya importado de nuevas
importaciones.

### D11. Incertidumbre simulada

Distinguir la variación mensual dentro de un escenario de la incertidumbre sobre
sus supuestos. Mil réplicas de un mismo supuesto no resuelven la duda sobre ese
supuesto.

**Decisión:** revisar sesgos persistentes antes de generar errores; corregirlos
solo si existe evidencia suficiente y mejora la validación. Conservar la dependencia
entre meses y segmentos y añadir sensibilidades para los supuestos más dudosos.

Errores que persisten varios meses exigen más protección que errores que se
compensan. No imponer una previsión sin sesgo como si fuera un hecho demostrado.

Mostrar media, mediana y P10–P90. El rango describe resultados dentro del escenario
supuesto; no asigna probabilidades a los tres escenarios. No atribuir esas
probabilidades sin justificación.

## 5. Funcionamiento logístico

### D12. Pedidos, fabricación y llegadas

Separar mes de decisión del pedido, mes de producción asignada bajo la aproximación
del caso y mes de llegada a la red.

**Decisión:** mantener el plazo mensual simplificado de tres meses. Al cerrar
diciembre, enero y febrero están comprometidos y marzo es la primera llegada
ajustable. Mostrar pedidos y llegadas en tablas diferenciadas y declarar cómo se
aproxima la fabricación a partir del pedido.

Incluir pedidos de final de A013 destinados a A014. Recibir coches en A013 no
equivale a haberlos encargado o fabricado durante A013.

### D13. Llegadas iniciales comprometidas

El stock inicial es observado, pero las llegadas iniciales deben estimarse. La
referencia actual es la facturación media de los últimos seis meses de A012.

**Decisión:** conservarla como candidata y compararla con una referencia más reciente
y adecuada por segmento. Revisar especialmente CSUV y evaluar estimaciones inferiores
y superiores. Los tres escenarios empezarán con el mismo stock y los mismos
compromisos iniciales.

La incertidumbre de estos compromisos puede condicionar los primeros meses más que
pequeñas mejoras estadísticas de la previsión.

### D14. Revisión mensual e información disponible

Cuando falta stock, vender poco no implica necesariamente tener poca demanda.

**Decisión:** revisar con la información disponible hasta cada cierre, utilizando
la relación entre ventas acumuladas y previsión acumulada de los últimos tres meses,
y tratar específicamente los meses con restricciones de stock.

Modificar solo llegadas todavía ajustables e incorporar sucesos cuando se conocen.
El planificador no debe conocer por adelantado el escenario o la demanda futura
simulados.

Calcular los umbrales sobre esa misma relación entre sumas, no sobre una media
geométrica distinta, y resolver explícitamente el tratamiento de CSUV. Separar la
revisión rutinaria de una señal que exige reconsiderar los supuestos.

### D15. Stock, edades, unidades e interrupciones

**Decisión:** mantener FIFO, es decir, vender primero el stock más antiguo, con una
aproximación por lotes para las edades iniciales.

- Aplicar los 15 días del caso a vehículos facturados y vendidos dentro del mes.
- Respetar la antigüedad acumulada y el límite total de 180 días de coste de la marca.
- Aplicar VM según la edad de venta.
- Declarar la imputación del VM ausente para CSUV y comprobar su sensibilidad.
- Mantener pedidos y ventas simuladas enteros, con redondeo explícito; previsiones y
  medias pueden tener decimales.

No es necesario simular cada día, pero las convenciones mensuales deben ser
coherentes. Una interrupción de fábrica afectará a las llegadas correspondientes a
su plazo, sin eliminar coches ya en tránsito. Declarar si la producción perdida se
recupera posteriormente o se cancela.

### D16. Transfers y ventas perdidas

Un transfer es un coche traído del stock de otro país. Calcular su coste hipotético
no equivale a introducirlo en los flujos de la simulación.

**Decisión:**

- Caso base conservador: sin transfers garantizados.
- Alternativa: transfers dentro del mes con disponibilidad limitada y explícita.
- Disponibilidad suficiente: referencia favorable, no garantía operativa.

Su coste adicional es el 20 % del beneficio bruto, junto con los demás conceptos
aplicables. Si se plantea un plazo hasta el mes siguiente, habrá que definir cuántos
clientes esperan. Sin datos, la demanda no atendida se pierde en el caso base, sin
inventar una cartera de pedidos pendientes.

Una recomendación dependiente de transfers deberá identificar claramente la
disponibilidad supuesta y necesaria.

## 6. Economía y selección de la política

### D17. Resultado económico

Separar beneficio bruto, gasto comercial (VM), contribución después de VM (CVP),
coste de stock, transfers, CO₂, otros costes adicionales y resultado tras los costes
modelizados. Mostrar aparte los intereses del concesionario.

**Decisión:** no descontar VM dos veces ni restar ventas perdidas como gasto adicional
cuando el margen ya se calcula solo sobre ventas realizadas. Informar del coste de
oportunidad por separado, descontando los costes que se evitan al no vender.

Ejemplo ilustrativo del anexo 1: un CVP real medio de C de 1.187 € menos una prima
de 1.952 € deja −765 €, antes de otros efectos. No es una estimación actualizada del
modelo, pero muestra que una venta adicional no siempre mejora la contribución.

Frenar nuevas reposiciones no equivale a rechazar ventas del stock existente. Parte
de su coste ya está comprometido; hay que distinguir los ingresos y costes que
todavía pueden cambiar.

### D18. Objetivo y nivel de servicio

Se puede priorizar margen central, protección ante el escenario desfavorable o
atención a la demanda. Son criterios diferentes.

**Decisión:** elegir el mejor margen medio central entre las políticas que cumplan
el objetivo de servicio y mostrar por separado su comportamiento pesimista y
optimista. No promediar los escenarios como si fueran igualmente probables.

El objetivo inicial aprobado es **atender al menos el 95 % de la demanda anual en
los segmentos económicamente viables**, sujeto a comprobar su factibilidad. Es una
decisión de negocio, no un dato observado. Mide unidades atendidas, no una probabilidad
del 95 % de pasar el año sin roturas.

En segmentos de contribución negativa, estudiar frenar nuevas reposiciones. Si se
plantea mantener un servicio por motivos estratégicos, mostrar su coste de forma
explícita. Si los objetivos resultan incompatibles, exponer el conflicto en lugar
de modificarlos silenciosamente.

### D19. Stock de seguridad y comparación de políticas

El stock de seguridad cubre errores durante el plazo de reposición. El factor
raíz de tres de la fórmula del caso supone independencia mensual; si hay
persistencia, puede proporcionar protección insuficiente.

**Decisión:** estimar el error acumulado durante tres meses y comparar pocas
políticas interpretables: menor protección, referencia, mayor protección y
protección diferenciada por segmento. Refinar donde cambie materialmente la decisión.

Utilizar los mismos errores aleatorios para comparar políticas. Revisar la
tolerancia actual de 20.000 € respecto al máximo: el mismo importe no tiene igual
significado en todos los segmentos.

Ante resultados próximos, comprobar si la diferencia es estable o ruido de
simulación. Puede ser preferible inmovilizar menos stock cuando la ganancia adicional
no sea robusta. Denominar la elección «mejor política entre las evaluadas», no
«óptimo global».

### D20. Cierre de A013 y continuidad en A014

Dejar de pedir al terminar el año puede mejorar artificialmente A013 a costa de
desabastecer enero. Dejar exceso de stock puede desplazar sus costes al año siguiente.

**Decisión:** mantener A013 como periodo principal, prever lo necesario para pedidos
destinados a enero–marzo de A014 y evaluar las políticas finalistas con una
prolongación de seis meses como sensibilidad. Mostrar stock final, edades y
compromisos pendientes.

La prolongación requiere supuestos de continuidad; no constituye una previsión
validada de A014. No añadir al resultado el supuesto valor de venta de todo el stock
final sin una contabilidad coherente de sus costes. Utilizar la extensión para
observar consecuencias posteriores sin inventar ganancias de cierre.

### D21. Significado de «empujar» un segmento

Un segmento rentable con ventas perdidas puede merecer más disponibilidad. Eso no
demuestra que cualquier aumento de descuentos o publicidad resulte rentable.

**Decisión:** separar prioridad de abastecimiento, objetivos de servicio y prioridad
comercial cualitativa. No calcular un presupuesto comercial supuestamente óptimo
sin conocer la respuesta de la demanda al gasto.

Indicar dónde conviene asegurar coches, revisar precios o frenar reposición,
distinguiendo lo respaldado por el modelo de lo que requiere análisis adicional.

## 7. Implementación y entrega

### D22. Ubicación de los cambios

**Decisión:** los cambios de lógica y código se realizarán en los nuevos notebooks.
`analisis.ipynb` queda intacto. Esta revisión no trasladará las correcciones a los
módulos históricos de `src/`; los datos originales se conservarán.

| Notebook | Responsabilidad |
|---|---|
| `datos.ipynb` | Diagnóstico, demanda observada y ajustes históricos |
| `demanda.ipynb` | Modelos, validación y previsiones |
| `simulacion.ipynb` | Pedidos, llegadas, stock, edades y costes |
| `escenarios.ipynb` | Incertidumbre, políticas y recomendación |

La conexión entre notebooks debe utilizar resultados corregidos, evitando que
llamadas a funciones antiguas reintroduzcan supuestos descartados. Evitar versiones
divergentes de un mismo cálculo. Cada resultado importante irá acompañado de una
explicación breve de su significado, supuestos y consecuencia para la decisión.

Las salidas se regenerarán en las ubicaciones establecidas en la guía. La
documentación y los documentos de entrega deberán reflejar el modelo resultante.

### D23. Contenido y coherencia de la entrega

**Decisión:** producir:

- Diagnóstico A012 del total de marca y la gama comparable.
- Previsión mensual A013 por segmento y evaluación de fiabilidad.
- Tabla de supuestos de los tres escenarios.
- Plan inicial de pedidos y llegadas.
- Resultados de revisiones mensuales, separados del plan inicial.
- Tabla 5 completa para el total y los siete segmentos.
- Comparación de políticas, servicio, costes y riesgos.
- Reglas de seguimiento mensual.
- Resumen ejecutivo de dos páginas y presentación de diez minutos.

Todo procederá de la misma política recomendada y de la misma ejecución final.
Además:

- Sumar segmentos dentro de cada réplica antes de calcular percentiles del total.
- Separar stock disponible de coches en camino y etiquetar sus coberturas.
- Aislar el efecto del CO₂ manteniendo los demás factores constantes.
- Eliminar la comparación de ocho años de almacenamiento: el coste de la marca
  está limitado a 180 días.
- Identificar las figuras del plan base y las del recomendado; no mezclarlas.
- Hacer regenerables los documentos desde las salidas finales, sin copiar cifras
  manualmente.

## 8. Orden de ejecución y comprobación

| Paso | Trabajo | Condición para continuar | Estado |
|---|---|---|---|
| 1 | Corregir interpretación de demanda | Objetivo y ajustes definidos | Ejecutado y comprobado |
| 2 | Revisar previsión y validación | Modelo elegido con criterios documentados | Ejecutado y comprobado |
| 3 | Corregir simulación determinista | Fechas, balances, edades y costes coherentes | Ejecutado y comprobado |
| 4 | Completar escenarios e incertidumbre | Supuestos trazables y sin duplicidades | Ejecutado y comprobado |
| 5 | Comparar políticas | Servicio, beneficio y continuidad evaluados | Ejecutado y comprobado |
| 6 | Regenerar resultados y entrega | Una única recomendación coherente | Generado y validado |

Empezar con comprobaciones y simulaciones pequeñas. Reservar las 1.000 réplicas por
escenario para las políticas finalistas y ampliar solo si la comparación sigue
siendo inestable. Aplicar las comprobaciones proporcionales de la guía y las reglas
de trabajo del repositorio.

Para revisiones globales, utilizar auxiliares económicos disponibles con encargos
acotados y contexto mínimo. La integración, las decisiones metodológicas y la
interpretación corresponden al agente principal. No delegar una tarea trivial si
la coordinación cuesta más que resolverla directamente.

Los auxiliares utilizarán modelos de OpenAI, comprobando su identificador disponible:
Luna para tareas mecánicas y acotadas, Terra para implementación técnica y Sol para
problemas de mayor dificultad o revisiones metodológicas delicadas. **No utilizar
versiones Fast.** La elección debe considerar la corrección, el contexto y el coste
total del trabajo, incluidas las revisiones necesarias.

## 9. Resumen de decisiones de negocio aprobadas

| Decisión | Criterio aprobado |
|---|---|
| Demanda real | Separar observado, estimado y gama comparable; mantener CSUV en el total |
| Información insuficiente | Supuestos explícitos y sensibilidades; no presentar estimaciones como hechos |
| Automatriculaciones A013 | Cero en el caso base |
| Transfers | No garantizados en el caso base; alternativa de capacidad limitada |
| Objetivo del plan | Margen medio central sujeto a servicio; riesgos de los otros escenarios separados |
| Servicio inicial | 95 % de unidades anuales en segmentos económicamente viables, sujeto a factibilidad |
| Segmentos con pérdidas | Estudiar frenar nuevas reposiciones, distinguiendo el stock comprometido |
| Continuidad | Pedidos hacia A014 y sensibilidad de seis meses |
| Elección técnica | Validación temporal y sencillez, sin elegir un algoritmo de antemano |

Las magnitudes resultantes se documentan en los notebooks y sus tablas. Donde los
datos no permiten identificar un efecto —producto, CSUV, compromisos iniciales o
ciertos costes geopolíticos— se mantiene la distinción entre estimación, hipótesis y
sensibilidad. No se sustituyen esos límites por una supuesta validación completa.

## 10. Ejecución verificada y puntos de consulta

Los cuatro notebooks se ejecutaron desde salidas regenerables vacías, con el kernel
`kaido-motors`, y conservan sus resultados. La lógica revisada reside en ellos;
`analisis.ipynb`, los módulos históricos y los CSV de entrada se conservaron.

### Resultados principales

- **A012:** ventas observadas a clientes +6,0 % en el total y −0,1 % en la gama
  comparable. El ajuste parcial de episodios estima +2,5 % total; retira el pico y
  restituye la caída posterior estimada de A011. No es una medida exacta de toda la
  demanda potencial. Véanse el [crecimiento](../resultados/datos/tablas/crecimiento_demanda_a012.csv)
  y sus [sensibilidades](../resultados/datos/tablas/sensibilidad_crecimiento_a012.csv).
- **Previsión:** mercado completo y modelo con confianza e intercepto elegido con
  A009–A011. El MAE mensual relativo del total comparable en A012 es 14,8 %;
  CSUV queda fuera de esa evaluación. La
  [evaluación retrospectiva](../resultados/demanda/tablas/evaluacion_retrospectiva_a012.csv)
  se separa de la economía futura conocida y de las revisiones mensuales.
- **Política:** seis niveles de colchón en el piloto de 200 réplicas y verificación
  final con 1.000 por escenario. Los siete segmentos superan el 95 % de servicio
  medio central. El total es 97,6 %; no se garantiza el objetivo en cada réplica ni
  en los otros escenarios. Véase la [política](../resultados/escenarios/tablas/politica_recomendada_a013.csv).
- **Contribución media A013 tras costes modelizados:** 3,1 M€ pesimista, 62,9 M€
  central y 91,4 M€ optimista. Son resultados condicionados, no beneficios netos
  garantizados ni una media ponderada por probabilidades de escenarios.
- **Plan inicial:** 16.144 coches asignados a pedidos decididos durante A013 y
  18.114 llegadas previstas durante A013. El
  [plan de pedidos](../resultados/escenarios/tablas/plan_pedidos_inicial_a013_a014.csv)
  separa fechas y los [pedidos revisados](../resultados/escenarios/tablas/pedidos_revisados_a013.csv)
  muestran los cambios posteriores a la observación de ventas.
- **Continuidad:** la comparación con el plan base sigue siendo favorable para la
  política recomendada al extender hasta junio de A014, bajo los supuestos de
  continuidad. Véase la [comparación](../resultados/escenarios/tablas/comparacion_continuidad_politicas.csv).

### Límites que siguen siendo relevantes

- El efecto central de renovación se fija en cero por identificación causal
  insuficiente. Se conserva una sensibilidad empírica de producto y una prueba
  específica del retraso de MSUV; un calendario sin efecto estimable no demuestra
  que el producto sea irrelevante.
- CSUV utiliza su propia sensibilidad de meses y un proxy de dispersión de segmentos
  próximos. No se valida con los ceros anteriores al lanzamiento.
- Combustible, arancel y cambio utilizan tamaños exploratorios: ±3 % residual de
  demanda, 500 €/nueva importación en el pesimista y ahorro de 250 €/nueva importación
  en el optimista, con valores alternativos. El combustible se aplica antes de
  descontar el adelanto absoluto, no multiplicando también ese adelanto.
- En el optimista, la caída supuesta de un solo mes no permite descontar 235,3 coches
  del adelanto estimado sin demanda negativa. Se informa esa parte no aplicada y no
  se traslada silenciosamente a otro mes. Véase el
  [registro de aplicación](../resultados/escenarios/tablas/ledger_aplicado_escenarios_finales.csv).
- La fabricación se aproxima por la asignación ejecutada del pedido, sin un modelo
  adicional de capacidad fabril. La continuación A014 y la disponibilidad de
  transfers son supuestos, no datos futuros observados.

### Entrega y comprobaciones

La [tabla 5](../resultados/escenarios/tablas/tabla5_plan_recomendado_a013.csv) incluye
los siete segmentos y el total. El [resumen ejecutivo](resumen-ejecutivo.pdf) tiene
dos páginas y la [presentación](presentacion.pdf), ocho diapositivas con notas para
diez minutos. Sus versiones Word y PowerPoint, incluidas las gráficas editables de
la presentación, se regeneran desde `escenarios.ipynb`.

Se comprobaron datos, ausencia de fugas temporales, ledger sin duplicidades, FIFO,
fronteras de intereses y coste a 180 días, transfers, unidades enteras, balances,
plazos y coincidencia de plan inicial. La revisión independiente contrastó la
integración económica y las tablas. Se revisaron los gráficos y documentos, y la
validación estructural de Word y PowerPoint pasó. Las
[versiones y parámetros efectivos](../resultados/escenarios/tablas/configuracion_ejecucion.json)
permiten identificar la ejecución de entrega.
