# Informe de Trabajo

## Planteo del problema
Una facultad necesita organizar los turnos de mesas de examenes de manera tal que las materias que se rinden en el mismo turno tengan la menor cantidad de estudiantes adeudores en comun. La facultad a su vez quiere tener la menor cantidad de turnos distintos posibles. O sea que sabiendo que va a haber materias que si o si tienen que compartir turno, tenemos que hallar la manera de perjudicar a la menor cantidad de estudiantes adeudores.

Para esto generamos un dataset mock que representaria el historial de estudiantes de semestres anteriores que han adeudado esas materias. Usando este dataset entrenamos un modelo de regresion lineal para que estime cuantos alumnos se van a llevar un par de materias simultaneamente. El modelo predice cuántos estudiantes se verían afectados.

En base a esas predicciones, asignamos un valor entre 0 y 1 a cada par de materias al que llamamos `peso`. Un peso bajo indica pocos alumnos afectados por la coincidencia de turnos de un par de materias, un peso alto indica lo contrario. Nuestro grafo se construye a partir de ese peso. Como la facultad no ofrece un limite de turnos, implementamos un minimo de peso dinamico al que llamamos `umbral`. En el grafo, todas las materias se representan como nodos, pero solo aquellas parejas de materias con peso mayor o igual al umbral se consideran *"conflictivas"* y sus nodos se unen por una arista.

Luego, el algoritmo de coloreo greedy se asegura que ningun par de materias que compartan una arista se pinten del mismo color. Entonces, si los colores del grafo representan cada uno un turno de mesa, esta asegurado que las materias con mayor conflictividad no se van a rendir en el mismo turno.

## El Modelo

## El Grafo

### Construir el Grafo

### Colorear el Grafo

## El Frontend

## El uso de IA
Nos apoyamos ampliamente en el uso de inteligencia artificial para este trabajo. Consideramos que actualmente es infima o casi nula la cantidad de codigo escrito a mano en el mundo profesional y que las materias en particular a las que refiere este trabajo no se enfoncan en el codgio en si, si no en la teoria logica y matematica que viene detras del mismo. Es por eso que decidimos invertir nuestro tiempo mas en plantear el problema y disenar la solucion que en escribir el codigo en si.

Cabe aclarar que esto no significa que le pasamos el enunciado de una vez y esperamos a ver que nos devolvia. Todos los prompts fueron pensados y todas las generaciones fueron leidas, estudiadas y modificadas para que sastifazcan mejor nuestra idea del trabajo. Creemos haber hecho un uso conciente y haber utilizado la IA como herramienta mas que como solucion directa.

### Para que la usamos?

- **Dataset:** Como sugirio el propio enunciado, nuestro dataset fue generado a partir del script `dataset.py` que a su vez fue generado por Gemini AI.

- **Codigo:** En su mayoria, el codigo de este trabajo fue generado por inteligencia artificial, en particular por Cursor Agent.

### Para que no la usamos?

- **Documentacion:** Este propio informe fue escrito a mano para hacer justicia a nuestro entendimiento del problema e incluso de nuestra propia solucion.

- **Prompts y Revision de codigo:** Si bien la mayoria del codigo fue generado quisimos darle instrucciones claras a nuestros agentes sobre como encarar el problema. Luego nos encargamos de leer el codigo generado, comprenderlo y decidir si satisfacia nuestras necesidades o no.

### Errores o Desentendimientos de la IA
Un ejemplo puntual de mi parte (Julieta) es que cuando promptee la generacion del codigo para la construccion del grafo explique la funcion de nuestro `umbral`. Quizas mi explicacion del umbral no fue lo suficientemente precisa porque cuando revise el codigo antes de probarlo note la existencia de un umbral minimo y un umbral maximo. Un umbral maximo frustra el objetivo del problema siendo que ignoramos los pesos mas altos. Ignorar los pesos mas altos implica quitarle prioridad a los pares de materias con mayor conflictividad, posiblemente asignandoles el mismo turno (exactamente lo opuesto a lo que queremos conseguir).

### Reflexion final
En general, creemos que la IA deberia utilizarse para el trabajo que a uno como programador le genera problemas y perdidas de tiempo. El programador deberia ser capaz de plantear un problema, descomponerlo en problemas mas chicos y encontrar soluciones chicas para generar un gran sistema que resuelva el problema inicial. A partir de una idea bien planteada es cuando el programador debe delegarle el codigo a la herramienta. La IA nos sirve para desocuparnos de debuggear y de memorizar sintaxis pero no deberiamos depender de ella para plantar las bases de nuestro trabajo, especialmente en una instancia evaluativa donde se requiere que empleemos lo aprendido en clases para resolver un problema.