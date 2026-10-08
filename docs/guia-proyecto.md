# Guía del proyecto

Esta es la referencia común para personas y asistentes que trabajen en Kaido Motors.
Reúne las decisiones de estructura, estilo y presentación. Cuando cambie una
convención, actualizar aquí su definición y, si corresponde, el archivo de estilo.

## 1. Objetivo y alcance

Responder a las cinco preguntas de la sección 9.1 del enunciado: demanda real,
previsión A013, escenarios, producción y stock, y recomendación económica.

Priorizar una solución que se pueda ejecutar, comprobar y explicar en clase.
Empezar por el método más sencillo que permita responder la pregunta. Añadir
complejidad solo cuando mejore la validación o represente una restricción del caso.

**Estado:** preparación del repositorio. La previsión, la simulación y las
conclusiones numéricas están pendientes.

El PDF es la fuente del caso; el Markdown es su versión de lectura adaptada a los
nombres actuales. Los CSV son la fuente para calcular resultados. Si aparecen
discrepancias, registrarlas con su localización y magnitud antes de decidir cómo
tratarlas. No corregir los datos para que encajen con una cifra narrativa.

## 2. Estructura y responsabilidades

| Ubicación | Responsabilidad |
|---|---|
| `data/` | Entradas del profesor y equivalencia de nombres |
| `docs/` | Enunciado, esta guía y futuros documentos de entrega |
| `examples/` | Referencia docente, separada de la solución |
| `config/graficos.mplstyle` | Aspecto común de las figuras |
| `src/datos.py` — futuro | Lectura, validaciones, fechas y preparación |
| `src/demanda.py` — futuro | Referencia estacional, modelos, cuota y evaluación |
| `src/escenarios.py` — futuro | Supuestos y trayectorias de los tres escenarios |
| `src/simulacion.py` — futuro | Flujo mensual, revisiones, antigüedad y costes |
| `analisis.ipynb` — futuro | Hilo conductor: preguntas, ejecución y explicación |
| `resultados/` | Tablas y figuras regenerables para el análisis y la entrega |

Crear los módulos y el notebook cuando tengan contenido ejecutable. El notebook
llamará a funciones de `src/`; los módulos no dependerán del notebook. Centralizar
los supuestos del modelo en `escenarios.py` inicialmente. Separar una configuración
de parámetros solo si el tamaño lo justifica.

## 3. Código y archivos

- Python 3.10+, con las bibliotecas de `requirements.txt`. Añadir dependencias
  únicamente si resuelven una necesidad concreta del trabajo.
- Nombres nuevos en español, `snake_case`, sin tildes ni espacios. Constantes en
  `MAYUSCULAS`; nombres propios de bibliotecas y columnas originales se conservan.
- Cuatro espacios, comillas dobles y longitud orientativa de 88 caracteres en Python.
  Archivos de texto UTF-8 con finales de línea LF y salto final.
- Preferir funciones pequeñas, entradas explícitas y resultados devueltos. Evitar
  clases, capas de abstracción y funciones genéricas que no necesite el caso.
- Añadir tipos en las funciones reutilizables cuando aclaren su contrato. Docstrings
  breves que indiquen propósito y, cuando importe, unidades y supuestos.
- Comentar el motivo de una decisión o una limitación; no narrar instrucciones obvias.
- Rutas con `pathlib.Path`. Ejecutar desde la raíz del proyecto y evitar rutas
  personales absolutas o cambios de directorio dentro del notebook.
- Mantener precisión interna; redondear al presentar. El redondeo de pedidos a
  coches enteros será una regla explícita del simulador.
- Usar `numpy.random.default_rng(42)` como punto de partida reproducible. Pasar el
  generador a las funciones; no reiniciarlo en cada mes o repetición.
- En el futuro notebook, separar explicación y código; comprobar «reiniciar y
  ejecutar todo». Evitar depender del orden manual de ejecución de celdas.
- Las comprobaciones deberán cubrir balances, plazos y casos límite relevantes;
  no crear infraestructura de pruebas extensa para cambios documentales.

## 4. Redacción y nivel de detalle

**Idioma:** español de España. **Tono:** académico, directo y comprensible para un
lector con nociones de estadística y logística. Utilizar frases cortas y términos
consistentes; definir VM, CVP, PFF y transfer en su primera aparición.

Cada apartado de análisis seguirá, cuando corresponda, esta secuencia:

1. Pregunta que se quiere responder.
2. Datos y método, con una justificación breve.
3. Resultado cuantificado y su incertidumbre.
4. Interpretación y consecuencia para la decisión.

Distinguir hechos observados, supuestos y resultados simulados. Utilizar
«se observa» para los datos, «se supone» para una hipótesis y «se estima» para una
previsión. Una correlación no se presentará como una causa demostrada.

| Pieza | Nivel de detalle |
|---|---|
| README | Cómo orientarse y ejecutar; sin desarrollar la metodología |
| Notebook | Método suficiente para reproducirlo; tras cada resultado importante, 2–4 frases de interpretación |
| Funciones | Contrato y decisiones no evidentes; sin duplicar la explicación del notebook |
| Resumen ejecutivo | Dos páginas: recomendación primero, cifras, riesgo y acciones; sin código |
| Presentación | Diez minutos, orientativamente 6–8 diapositivas, una idea principal por diapositiva |

Evitar párrafos de relleno, adjetivos como «óptimo» sin criterio demostrado y
conclusiones que no puedan vincularse a una tabla o figura. Identificar la fuente
con archivo y periodo; para una restricción del caso, citar su sección.

En Markdown, usar un título principal, encabezados jerárquicos y negrita solo para
destacar una idea. Fórmulas en LaTeX, con símbolos y unidades explicados junto a ellas.

Para maquetar la entrega, partir de un diseño común: fondo blanco, texto oscuro y
azul como acento. Resumen en A4, márgenes de 2 cm, cuerpo de 11 puntos e interlineado
1,15; títulos de 16 puntos y subtítulos de 12. Presentación en 16:9, títulos de
28–32 puntos y cuerpo de 20–24. Usar DejaVu Sans cuando esté disponible, o Arial como
alternativa, de forma consistente dentro de cada documento. Reducir contenido antes
que encoger la letra para cumplir las dos páginas o los diez minutos.

## 5. Tablas, cifras y unidades

- Presentación española: `23.175 coches`, `3.450 €`, `8,5 %`, `2,3 M€`.
- Coches: enteros en planes operativos; las medias pueden llevar un decimal si es
  necesario y deben identificarse como medias.
- Euros: sin decimales por defecto; costes diarios, dos decimales. Porcentajes y
  cobertura en meses, un decimal por defecto. No mostrar más precisión de la útil.
- Distinguir porcentajes de puntos porcentuales. Declarar el denominador de cuotas,
  coberturas y métricas relativas.
- Tablas con título, periodo y unidad en la cabecera. Números alineados a la derecha;
  no mezclar euros totales y euros por coche en una misma columna sin indicarlo.
- Orden de segmentos: `B`, `C`, `MD`, `SSUV`, `CSUV`, `MSUV`, `S`, y total al final.
  En una clasificación por ventas o margen, ordenar por ese criterio y declararlo.
- Orden de escenarios en tablas: **pesimista, central, optimista**, como la tabla 5.
- Usar `—` para un valor no disponible o no aplicable, con nota aclaratoria. El cero
  representa una cantidad calculada u observada igual a cero.
- CSV generados: formato largo cuando resulte útil, UTF-8, coma, punto decimal,
  sin separadores de miles y sin índice de pandas. Mantener códigos temporales
  del caso y separar los datos numéricos de su formato de presentación.

## 6. Estilo de gráficos

Usar Matplotlib y cargar el estilo común antes de crear figuras:

```python
import matplotlib.pyplot as plt

plt.style.use("config/graficos.mplstyle")
```

### Aspecto y significado

Fondo blanco, tipografía DejaVu Sans, cuadrícula horizontal tenue y sin bordes
superior ni derecho. Tamaño base de 9 × 4,8 pulgadas; adaptar las figuras con varios
paneles manteniendo legibilidad. Títulos breves, alineados a la izquierda.

| Serie | Color | HEX | Trazo |
|---|---|---|---|
| Histórico observado | Gris oscuro | `#333333` | Continuo |
| Previsión / escenario central | Azul | `#0072B2` | Discontinuo |
| Escenario optimista | Verde azulado | `#009E73` | Raya y punto |
| Escenario pesimista | Naranja rojizo | `#D55E00` | Punteado |
| Referencia estacional | Gris medio | `#888888` | Punteado |

Asignar explícitamente estos colores y trazos por significado: el ciclo automático
del archivo de estilo solo ofrece una paleta general, no reconoce escenarios.
La leyenda y el trazo deben permitir entender la figura sin depender del color.

- Una pregunta por figura. Líneas para tiempo, barras para comparación y bandas
  para incertidumbre; evitar 3D, doble eje y decoración innecesaria.
- Etiquetar ejes con unidad: `Ventas (coches)`, `Margen (M€)`, `Cobertura (meses)`.
- Mostrar `A012`, `A013` o `ene`–`dic` con el año en el título; nunca presentar
  2012 o 2013 como si fueran años reales del caso.
- Separar visualmente histórico y previsión. Las bandas usarán el color de la
  serie con transparencia aproximada de 0,15 e indicarán su nivel o percentiles.
- Para simulación, presentar mediana y P10–P90 como resumen inicial, además de la
  media cuando se hable de costes o margen esperados. Esos percentiles describen
  variabilidad dentro de un escenario, no la probabilidad de los tres escenarios.
- En barras de cantidades, empezar en cero; si hay valores negativos, mostrar
  claramente el cero. En series temporales, cualquier recorte del eje debe ser claro.
- Comparar segmentos preferentemente con paneles pequeños. Mantener escalas iguales
  para comparar magnitudes; señalar si las escalas son distintas para ver patrones.
- Acompañar cada figura de fuente, periodo, método y una interpretación breve en el
  notebook o documento. No incrustar párrafos dentro del área de datos.

### Exportación

Guardar las figuras finales en `resultados/figuras/` como PNG a 300 ppp y SVG para
ampliaciones. Fondo blanco, márgenes ajustados y nombre descriptivo, por ejemplo
`demanda_msuv_a013_escenarios.png`. Revisar etiquetas y leyendas en el tamaño final.
Para una presentación, aumentar la tipografía de forma consistente, sin cambiar
colores ni significados. Las figuras originales del enunciado conservan su diseño.

## 7. Reglas del caso que debe respetar el futuro código

- Preservar `NA`, distinguir vacíos de ceros y usar el calendario facilitado.
- Distinguir demanda, matriculaciones y ventas a clientes. Restar automatriculaciones
  no resuelve por sí solo compras adelantadas o demanda limitada por falta de stock.
- Verificar el stock histórico con las matriculaciones que correspondan al balance
  original; no sustituirlas sin más por ventas depuradas de automatriculaciones.
- Evaluar con separación temporal: entrenar hasta A011 y comprobar A012. Cualquier
  variable, transformación o ajuste debe respetar la información disponible al
  decidir. Identificar por separado las evaluaciones con economía futura conocida.
- Un retraso de tres meses no proporciona por sí solo toda la economía de los doce
  meses de A013: los horizontes restantes también necesitan supuestos.
- Tratar CSUV como lanzamiento desde agosto de A012: no tiene una historia de cuota
  comparable a los demás segmentos antes de ese año.
- Empezar los tres escenarios con el mismo plan central. Revisar mensualmente solo
  llegadas a tres meses vista, con la información disponible en ese momento.
- Separar mes del pedido/producción y mes de llegada. El stock inicial es el de
  diciembre de A012; las llegadas iniciales comprometidas deben estimarse y documentarse.
- Vender primero el stock más antiguo (FIFO) y documentar la aproximación de edades
  dentro de los tramos iniciales y de días dentro de cada mes.
- Contar el coste para la marca a 2 €/coche/día hasta 180 días de antigüedad total,
  sin reiniciar ese límite en enero. Separar los intereses del concesionario.
- El transfer cuesta el 20 % del beneficio bruto, no el 20 % del CVP.
- Distinguir beneficio bruto, VM, CVP y resultado tras costes logísticos. No restar
  dos veces VM ni descontar ventas perdidas como un gasto adicional si ya se calcula
  el margen solo sobre ventas realizadas; su coste de oportunidad se informa aparte.
- No asignar probabilidades a los escenarios ni impactos a sucesos sin justificarlos.

### Decisiones metodológicas pendientes

Antes de implementar cada parte, anotar en el notebook el supuesto, su fuente o
justificación y su efecto esperado. Quedan por resolver:

- Ajustes por compras adelantadas y señales de falta de stock.
- Variables, cuota y tratamiento del lanzamiento de CSUV.
- Llegadas iniciales, edad del stock y revisión mensual de la previsión.
- Nivel de servicio, disponibilidad/plazo de transfers y redondeo de pedidos.
- Traducción cuantitativa de los sucesos, distribución y dependencia de los errores.
- Tratamiento del combustible y tipo de cambio: se mencionan en los escenarios,
  pero no tienen una columna directa en el CSV económico.
- Pedidos de fin de A013 que llegarían en A014 y valoración del stock final.

## 8. Orden de implementación y criterios de finalización

| Fase | Trabajo | Resultado verificable |
|---|---|---|
| 1. Datos | Cargar y comprobar claves, periodos, ausencias y balances; preparar demanda | Series por segmento y diagnóstico documentado de A012 |
| 2. Previsión | Referencia estacional, modelo sencillo de mercado y cuota; validar A012 | MAE y sesgo por segmento, limitaciones y previsión A013 |
| 3. Simulación básica | Un año determinista, llegadas, ventas, FIFO y costes | Reproduce la cuenta de la tabla 3 y conserva el balance de unidades |
| 4. Escenarios | Cuantificar sucesos y añadir incertidumbre; inicialmente 1.000 repeticiones | Mismo plan de partida, resultados reproducibles y rangos por escenario |
| 5. Entrega | Interpretar, recomendar y preparar documentos | Tabla 5, plan mensual, resumen de dos páginas y presentación de diez minutos |

Para la evaluación, definir el error como `prevision - observado`: sesgo positivo
significa sobreprevisión. Ajustar los modelos y calcular sus métricas sobre una
variable objetivo claramente identificada, especialmente si la demanda se estima.

Al cerrar cada fase: reiniciar y ejecutar el notebook completo, revisar las
comprobaciones pertinentes y actualizar el estado en el README. Registrar versiones
de Python y bibliotecas, semilla y parámetros usados en la ejecución de entrega.
