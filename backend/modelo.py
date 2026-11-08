"""Modelo predictivo de conflicto entre pares de materias.

Regresión (no clasificación): se estima cant_estudiantes_afectados
para después filtrar el grafo con un umbral.
"""

from pathlib import Path

import joblib as jb
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split

from backend.datos import load_pares

FEATURES = [
    "cant_estudiantes_compartidos_historico",
    "mismo_anio",
    "misma_carrera",
]
TARGET = "cant_estudiantes_afectados"
SEMILLA = 42
RUTA_MODELO = Path(__file__).resolve().parent / "modelo_conflicto.joblib"


def _features(pares):
    return pares[FEATURES]


def entrenar():
    """Entrena el modelo, evalúa en test y lo guarda en disco."""
    pares = load_pares()
    X = _features(pares)
    y = pares[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=SEMILLA,
    )

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("RMSE:", root_mean_squared_error(y_test, y_pred))
    print("R2:", r2_score(y_test, y_pred))

    jb.dump(modelo, RUTA_MODELO)
    print("Modelo guardado en:", RUTA_MODELO)


def predecir(pares):
    """Estima cant_estudiantes_afectados para cada par."""
    modelo = jb.load(RUTA_MODELO)
    return modelo.predict(_features(pares)).clip(min=0)


if __name__ == "__main__":
    entrenar()
    ejemplo = pd.DataFrame(
        [
            {
                "cant_estudiantes_compartidos_historico": 100,
                "mismo_anio": True,
                "misma_carrera": True,
            },
            {
                "cant_estudiantes_compartidos_historico": 5,
                "mismo_anio": False,
                "misma_carrera": False,
            },
        ]
    )
    print("Predicciones de ejemplo:", predecir(ejemplo))
