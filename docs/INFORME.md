# Informe de trabajo

**Materia:** Lógica y Teoría de Grafos
**Trabajo práctico final:** Planificación de mesas de examen
**Integrantes:** Ana Deheza - Julieta Segovia

## 1. Problema

Una facultad necesita organizar los turnos de mesas de examenes de manera tal que las materias que se rinden en el mismo turno tengan la menor cantidad de estudiantes adeudores en comun. La facultad a su vez quiere tener la menor cantidad de turnos distintos posibles. O sea que sabiendo que va a haber materias que si o si tienen que compartir turno, tenemos que hallar la manera de perjudicar a la menor cantidad de estudiantes adeudores.

Para esto generamos un dataset mock que representaria el historial de estudiantes de semestres anteriores que han adeudado esas materias. Usando este dataset entrenamos un modelo de regresion lineal para que estime cuantos alumnos se van a llevar un par de materias simultaneamente. El modelo predice cuántos estudiantes se verían afectados.

En base a esas predicciones, asignamos un valor a cada par de materias al que llamamos `peso`. Un peso bajo indica pocos alumnos afectados por la coincidencia de turnos de un par de materias, un peso alto indica lo contrario. Nuestro grafo se construye a partir de ese peso. Como la facultad no ofrece un limite de turnos, implementamos un minimo de peso dinamico al que llamamos `umbral`. En el grafo, todas las materias se representan como nodos, pero solo aquellas parejas de materias con peso mayor o igual al umbral se consideran *"conflictivas"* y sus nodos se unen por una arista.

Luego, el algoritmo de coloreo greedy se asegura que ningun par de materias que compartan una arista se pinten del mismo color. Entonces, si los colores del grafo representan cada uno un turno de mesa, esta asegurado que las materias con mayor conflictividad no se van a rendir en el mismo turno.

El sistema combina tres piezas:

1. Un **modelo de regresión** que, para cada par de materias, estima cuántos estudiantes se verían afectados.
2. Un **grafo de conflictos** no dirigido: nodo = materia, arista = conflicto por encima de un umbral, peso = magnitud del conflicto.
3. **Coloreo greedy** (Welsh-Powell): cada color es un turno. Dos materias unidas por una arista no pueden tener el mismo color.

La interfaz (Streamlit) muestra el grafo, el cronograma por turno y un slider para el umbral.

## 2. Datos

No hay un historial real de la facultad. Se genera un dataset **sintético** con `dataset.py` (semilla `42`, para que el CSV sea reproducible).

- 3 carreras, 5 años, 3 materias por año → **45 materias** (nodos).
- Todos los pares no ordenados → **990 filas**.

Cada fila es un par, no una materia suelta. Columnas:

| Campo                                      | Rol                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------- |
| `materia_id_1`, `materia_id_2`         | identificadores del par                                               |
| `cant_estudiantes_compartidos_historico` | feature                                                               |
| `mismo_anio`, `misma_carrera`          | features                                                              |
| `cant_estudiantes_afectados`             | variable a predecir (regresión)                                      |
| `hubo_conflicto`                         | alternativa de clasificación; **no se usa** en el modelo final |

La generación imita solapamiento académico: más estudiantes compartidos si son la misma carrera y el mismo año, menos si están lejos en el plan. `cant_estudiantes_afectados` es una fracción ruidosa de los compartidos.

Los CSV no se versionan en git. Se regeneran con `python dataset.py`.

## 3. Modelo predictivo

Se eligió **regresión lineal** y no clasificación. El enunciado pedía una de las dos. La regresión da un número (estudiantes afectados) que después se corta con un umbral para armar aristas. En nuestra opinión, un sí/no no alcanzaría para que el slider tenga sentido en una escala continua.

- Features: `cant_estudiantes_compartidos_historico`, `mismo_anio`, `misma_carrera`.
- No se usan los `materia_id`: el modelo tiene que generalizar por características, no memorizar materias.
- Split **80% train / 20% test**, `random_state=42`.
- Librería: scikit-learn, `LinearRegression`.

Métricas **solo sobre test** (198 pares):

| Métrica | Valor |
| -------- | ----- |
| MAE      | 2.36  |
| RMSE     | 4.66  |
| R²      | 0.87  |

El MAE se lee como “en promedio nos desviamos ~2.4 estudiantes”. El R² indica que el modelo explica buena parte de la variación del test, coherente con que los afectados sintéticos son aproximadamente una fracción de los estudiantes compartidos.

El artefacto se guarda en `backend/modelo_conflicto.joblib` (tampoco va a git). Se reentrena con `python -m backend.modelo`.

## 4. Grafo de conflictos

`construir_grafo` recibe las predicciones, el umbral y el catálogo de materias.

- Grafo **no dirigido**, sin lazos.
- **Todas** las materias son nodos, aunque no tengan aristas (aisladas: pueden ir a cualquier turno).
- Hay arista si `prediccion >= umbral`.
- El **peso** de la arista es esa predicción.

El umbral está en la misma escala que el modelo (estudiantes afectados), no entre 0 y 1. En la UI va de **0 a 80**, con default **20**. Un valor tipo 0.5 dejaría casi todos los pares como conflicto, porque la mediana de las predicciones es baja (~2.6) y el máximo ~79.

Efecto observado sobre los 45 nodos:

| Umbral | Aristas | Turnos |
| ------ | ------- | ------ |
| 5      | 257     | 9      |
| 20     | 114     | 5      |
| 40     | 31      | 3      |

Subir el umbral recorta conflictos leves: las materias estan mas dispersas y hacen falta menos colores. El costo es ignorar choques más chicos.

## 5. Coloreo greedy (Welsh-Powell)

Encontrar el número cromático exacto es difícil en grafos grandes. Se implementó un greedy a mano (no se usa `networkx.coloring` como única solución).

**Welsh-Powell:**

1. Ordenar los vértices por **grado descendente** (primero las materias con más conflictos).
2. Recorrerlos en ese orden.
3. A cada uno asignarle el **menor color** que no estén usando sus vecinos ya pintados.

El resultado es siempre un coloreo **válido** (nadie en conflicto comparte turno). Puede usar más colores que el mínimo teórico; el orden por grado suele mejorar el greedy.

Se comprobó con grafos de prueba: triángulo → 3 colores; bipartito (dos aristas sueltas) → 2; nodo aislado recibe un color y aparece en el diccionario.

En el sistema, **color = turno de examen**.

## 6. Interfaz

Streamlit (`frontend/app.py`):

- Pestaña **grafo**: nodos = materias, color de borde = turno, aristas = conflictos (con peso).
- Pestaña **cronograma**: una columna por turno, con nombre, carrera y año.
- **Slider de umbral**: al moverlo se llama a `planificar(umbral)`, que vuelve a predecir, armar el grafo y colorear. Cambian aristas, colores y cantidad de turnos juntos.

`planificar` es la capa que une modelo, grafo y coloreo. El frontend no reimplementa el ML.

## 7. Cómo ejecutar

El detalle está en el [README](README.md).

Resumen:

Python 3.12,

`pip install -r requirements.txt`,

`python dataset.py`,

`python -m backend.modelo`,

`streamlit run frontend/app.py`.

## 8. Limitaciones

- Los datos son sintéticos: el modelo aprende la regla con la que se fabricó el CSV, no un historial verdadero de mesas.
- El greedy no garantiza al 100% el mínimo de turnos posible.
- Cada movimiento del slider vuelve a leer el CSV y a predecir; con 990 pares es aceptable.
- No se exploró un modelo no lineal (por ejemplo un random forest); la lineal alcanza en este dataset.

## 9. Uso de inteligencia artificial

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

## 10. Fuentes

- Coloreo greedy: [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/graph-coloring-set-2-greedy-algorithm/), [Cornell](https://www.cs.cornell.edu/courses/JavaAndDS/files/graphColoring.pdf)
- [scikit-learn LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [NetworkX](https://networkx.org/documentation/stable/reference/algorithms/coloring.html)
- [Streamlit](https://docs.streamlit.io/)
