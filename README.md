# Planificación de mesas de examen

Sistema que estima conflictos entre pares de materias y arma un cronograma de mesas con la menor cantidad de turnos posible, combinando un **modelo predictivo** y **coloreo de grafos**.

Flujo:

1. El modelo estima cuántos estudiantes se verían afectados si dos materias rinden juntas.
2. Con un **umbral** se decide qué pares son aristas del grafo de conflictos.
3. Un **coloreo greedy** (Welsh-Powell) asigna un turno a cada materia: dos materias en conflicto no comparten color.
4. La interfaz muestra el grafo, el cronograma y deja cambiar el umbral.

## Integrantes

- Ana Deheza
- Julieta Segovia

## Estructura

```
backend/
  datos.py         # carga materias.csv y dataset_mesas_examen.csv
  modelo.py        # regresión lineal (entrenar / predecir)
  grafo.py         # construye el grafo según el umbral
  coloreo.py       # Welsh-Powell
  planificar.py    # pega modelo + grafo + coloreo
frontend/
  app.py           # Streamlit: grafo, cronograma y slider
  visualizar_grafo.py
dataset.py         # genera el dataset sintético
requirements.txt
INFORME.md
```

Los CSV y el `.joblib` **no están en git**. Hay que generarlos en cada máquina (pasos 4 y 5).

## Cómo ejecutar

Hace falta **Python 3.12** (en PCs con 3.14, usar 3.12 para que scikit-learn y Streamlit instalen bien).

### 1. Clonar

```bash
git clone https://github.com/anadeheza/PlanificacionMesasExamen.git
cd PlanificacionMesasExamen
```

### 2. Entorno virtual

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

bash / macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Dependencias

```bash
pip install -r requirements.txt
```

### 4. Generar el dataset

```bash
python dataset.py
```

Escribe en la raíz:

- `materias.csv` — catálogo de nodos (`id`, `nombre`, `carrera`, `año`)
- `dataset_mesas_examen.csv` — pares de materias

Los datos son **sintéticos** (semilla 42): 3 carreras, 5 años, 3 materias por año (~45 materias, ~990 pares).

Columnas de los pares:

| Columna | Uso |
|---------|-----|
| `materia_id_1`, `materia_id_2` | par |
| `cant_estudiantes_compartidos_historico` | feature |
| `mismo_anio`, `misma_carrera` | features |
| `cant_estudiantes_afectados` | target (regresión) |
| `hubo_conflicto` | no se usa en el modelo actual |

### 5. Entrenar el modelo

```bash
python -m backend.modelo
```

Guarda `backend/modelo_conflicto.joblib`. Sin este archivo Streamlit no puede predecir.

### 6. Interfaz

```bash
streamlit run frontend/app.py
```

Queda en [http://localhost:8501](http://localhost:8501).

El slider de **umbral** está en escala de **estudiantes afectados** (0–80, default **20**), no entre 0 y 1. Si el predicho es ≥ umbral, hay arista.

- Umbral **bajo** → más aristas → en general más turnos.
- Umbral **alto** → menos aristas → en general menos turnos.

## Modelo

**Regresión lineal**, no clasificación: hace falta un número (cuántos afectados) para recortar el grafo con el umbral.

- Features: `cant_estudiantes_compartidos_historico`, `mismo_anio`, `misma_carrera`
- Target: `cant_estudiantes_afectados`
- Split 80/20, semilla `42`
- Métricas **solo en test:** MAE ≈ 2.36, RMSE ≈ 4.66, R² ≈ 0.87

```bash
python -m backend.modelo
```

## Grafo y coloreo

`construir_grafo(predicciones, umbral, materias)` arma un grafo no dirigido. Todas las materias son nodos (aunque queden aisladas). El peso de la arista es la predicción de afectados.

`colorear(grafo)` usa **Welsh-Powell**: ordena las materias por grado descendente (más conflictos primero) y a cada una le asigna el menor color que no usen sus vecinas. **Color = turno de examen.**

```bash
python -m backend.planificar
```

Prueba el pegamento con umbral 20 y muestra nodos, aristas y turnos.

## Indices

Recurso | Fuente
--------|--------
Informe de Trabajo | [INFORME.md](INFORME.md)
Coloreo greedy | https://www.geeksforgeeks.org/dsa/graph-coloring-set-2-greedy-algorithm/
Coloreo greedy | https://www.cs.cornell.edu/courses/JavaAndDS/files/graphColoring.pdf
scikit-learn | https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
NetworkX | https://networkx.org/documentation/stable/reference/algorithms/coloring.html
Streamlit | https://docs.streamlit.io/

## Fuentes

### Coloreo Greedy

- https://www.geeksforgeeks.org/dsa/graph-coloring-set-2-greedy-algorithm/
- https://www.cs.cornell.edu/courses/JavaAndDS/files/graphColoring.pdf
