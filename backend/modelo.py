"""Modelo predictivo de conflicto entre pares de materias.

Regresión (no clasificación): se estima cant_estudiantes_afectados
para después filtrar el grafo con un umbral.

Trabajo correspondiente a la issue #9.
"""
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
import pandas as pd
import joblib as jb



def entrenar():
    """Entrena el modelo y lo guarda en disco."""
    ruta = Path(__file__).resolve().parent.parent / "dataset_mesas_examen.csv"
    pares = pd.read_csv(ruta)
    X = pares[
        [
            "cant_estudiantes_compartidos_historico",
            "mismo_anio",
            "misma_carrera",
        ]
    ]
    y = pares["cant_estudiantes_afectados"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print("MAE:", mae)
    print("RMSE:", rmse)
    print("R2:", r2)

    ruta_modelo = Path(__file__).resolve().parent / "modelo_conflicto.joblib"
    jb.dump(modelo, ruta_modelo)
    print("Modelo guardado en:", ruta_modelo)



def predecir(pares):
    """Devuelve la predicción de conflicto para cada par de materias."""
    ruta_modelo = Path(__file__).resolve().parent / "modelo_conflicto.joblib"
    modelo = jb.load(ruta_modelo)
    X = pares[
        [
            "cant_estudiantes_compartidos_historico",
            "mismo_anio",
            "misma_carrera",
        ]
    ]
    pred = modelo.predict(X)
    return pred.clip(min=0)


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
