# Planificación de mesas de examen

Sistema que estima conflictos entre pares de materias y arma un cronograma de mesas de examen con la menor cantidad de turnos posible (coloreo de grafos).

## Integrantes

- Ana Deheza
- Julieta Segovia

## Estructura

```
backend/          # datos, modelo, grafo y coloreo
  datos.py       # issue #7
  modelo.py      # issue #9
  grafo.py       # issue #11
  coloreo.py     # issue #13
  planificar.py  # issue #15
frontend/
  app.py         # interfaz Streamlit (issues #16, #17, #18)
dataset.py       # genera el dataset sintético de pares
requirements.txt
```

## Cómo ejecutar

Hace falta **Python 3.12**. En esta máquina también está 3.14; usar 3.12 para que scikit-learn y Streamlit instalen bien.

### 1. Clonar e ir al repo

```bash
git clone https://github.com/anadeheza/PlanificacionMesasExamen.git
cd PlanificacionMesasExamen
```

### 2. Crear el entorno virtual

En PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En bash / macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Levantar la interfaz

```bash
streamlit run frontend/app.py
```

Queda en [http://localhost:8501](http://localhost:8501). Por ahora es el esqueleto (sidebar de umbral y pestañas vacías).

### Regenerar el dataset

```bash
python dataset.py
```

Escribe `dataset_mesas_examen.csv` en la raíz del repo.

## Indices

Recurso | Fuente
--------|--------

## Fuentes

### Coloreo Greedy

- https://www.geeksforgeeks.org/dsa/graph-coloring-set-2-greedy-algorithm/
- https://www.cs.cornell.edu/courses/JavaAndDS/files/graphColoring.pdf
