# Correr el proyecto

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

### Entrenar el modelo de conflictos

Se usa **regresión lineal** (no clasificación): hay que estimar *cuántos* estudiantes se ven afectados, no solo si hay conflicto. Ese número después se corta con un umbral para armar el grafo.

- Features: `cant_estudiantes_compartidos_historico`, `mismo_anio`, `misma_carrera`
- Target: `cant_estudiantes_afectados`
- Split 80/20 con semilla `42`
- Métricas (MAE, RMSE, R²) calculadas solo sobre test

```bash
python -m backend.modelo
```

El archivo `.joblib` no se sube a git (está en `.gitignore`). En otra máquina se reentrena con el mismo comando.
