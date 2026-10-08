# Reglas de trabajo

Estas reglas se aplican a cualquier agente que trabaje en este repositorio.
Las convenciones de código, gráficos, redacción y metodología están en
[docs/guia-proyecto.md](docs/guia-proyecto.md). Mantener esa guía como referencia
única de estilo, sin duplicarla en instrucciones de agentes.

## Alcance y sencillez

- Resolver lo solicitado con el cambio más sencillo que sea correcto.
- No ampliar el alcance ni añadir dependencias, archivos, abstracciones o procesos
  sin una necesidad concreta de la tarea.
- Respetar el trabajo existente y las convenciones del proyecto.
- Si se pide un plan o una explicación antes de ejecutar, esperar la aprobación.

## Subagentes y modelos

- El agente principal conserva la planificación, las decisiones metodológicas,
  la interpretación de resultados y la revisión e integración del trabajo.
- Delegar tareas mecánicas y acotadas en un auxiliar con un modelo más económico:
  búsquedas delimitadas, renombrados, actualización de referencias, formato,
  funciones con especificación cerrada y comprobaciones concretas.
- Delegar solo si compensa la coordinación y el contexto adicional. Un cambio
  trivial puede hacerlo directamente el principal; no crear un subagente por archivo.
- Agrupar tareas relacionadas. Paralelizar únicamente trabajos independientes que
  no modifiquen los mismos archivos.
- Al configurar un auxiliar, usar el mecanismo nativo de la herramienta y un modelo
  económico disponible. Comprobar su identificador exacto; no inventarlo ni asumir
  que un subagente usa un modelo más barato por defecto.
- Reutilizar los auxiliares configurados. Empezar con uno de propósito general y
  crear especializaciones solo cuando haya una necesidad recurrente.
- Si falta un modelo económico configurado, resolver directamente las tareas
  pequeñas y acordar esa configuración antes de implantar delegación habitual.
- Cada encargo debe incluir objetivo, contexto mínimo, archivos que puede modificar,
  restricciones y criterio de finalización. No trasladar todo el chat por defecto.
- El auxiliar devolverá un resumen breve de cambios y cualquier duda o bloqueo.
  Revisar lo relevante sin repetir automáticamente todo su trabajo.

## Documentación y comentarios

- Documentar decisiones importantes, supuestos, restricciones e instrucciones
  necesarias para entender, ejecutar o mantener el proyecto.
- Los archivos deben describir el estado actual, no narrar la conversación ni el
  proceso seguido para modificarlos.
- No añadir comentarios como «cambiado a petición del usuario», «antes era azul»
  o «se ha renombrado este archivo» cuando no aporten información necesaria.
- Actualizar documentación cuando el cambio afecte a su exactitud o al uso del
  proyecto. No crear una nota, informe o historial por cada modificación.
- Comentar por qué existe una decisión no evidente, no qué hace una línea obvia.

## Comprobaciones proporcionales

- Ajustar la verificación al cambio y a sus consecuencias, no al tamaño del repositorio.
- Renombrado: comprobar las referencias afectadas. No comparar hashes, releer todos
  los datos ni ejecutar el modelo completo solo por cambiar un nombre.
- Texto o formato: revisar el fragmento modificado y sus enlaces, si los hay.
- Cambio visual: revisar su aspecto cuando sea pertinente, sin pruebas ajenas al cambio.
- Código: comprobar el comportamiento afectado con el caso o prueba más directo.
- Datos, cálculos o simulación: comprobar los valores afectados, unidades, balances
  y casos límite relevantes. Profundizar si aparecen discrepancias o riesgos reales.
- No crear pruebas que solo repitan la implementación ni infraestructura de pruebas
  para modificaciones documentales o mecánicas.
- No repetir comprobaciones que ya han pasado salvo que nuevos cambios, fallos o
  dudas concretas lo justifiquen.
- No afirmar que algo está comprobado si no se ha verificado. Indicar una limitación
  solo cuando afecte a la confianza en el resultado o al siguiente paso.

## Interacción con el usuario

- Hablar en español, de forma directa y breve.
- Ejecutar con autonomía cuando el objetivo esté claro. Preguntar solo si falta una
  decisión que afecte de manera relevante al alcance, la corrección o el resultado.
- No narrar lecturas, búsquedas, ediciones ni comprobaciones rutinarias.
- Dar avances solo cuando aporten un bloqueo, una decisión necesaria o un
  descubrimiento importante.
- Al terminar, indicar brevemente qué se ha hecho. Añadir problemas o pendientes
  únicamente si los hay y son relevantes.
- Evitar listas de verificaciones, explicaciones extensas y propuestas adicionales
  salvo que se soliciten o sean necesarias para entender el resultado.
- Ante una pregunta de análisis o una petición de detalle, aportar la evidencia y
  explicación necesarias: la brevedad no debe ocultar supuestos ni incertidumbre.
