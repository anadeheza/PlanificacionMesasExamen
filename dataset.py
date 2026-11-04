from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
PATH_MATERIAS = BASE / "materias.csv"
PATH_PARES = BASE / "dataset_mesas_examen.csv"

CARRERAS = [
    "Ingeniería Informática",
    "Ingeniería Industrial",
    "Licenciatura en Sistemas",
]
ANIOS = [1, 2, 3, 4, 5]


def generar_datasets():
    """Genera materias.csv y dataset_mesas_examen.csv con semilla fija."""
    np.random.seed(42)

    materias = []
    materia_id = 1

    for carrera in CARRERAS:
        for anio in ANIOS:
            # 3 materias por año y carrera
            for j in range(1, 4):
                materias.append(
                    {
                        "materia_id": f"MAT_{materia_id:03d}",
                        "carrera": carrera,
                        "anio": anio,
                        "nombre": f"{carrera.split()[0]} - Año {anio} - Mat {j}",
                    }
                )
                materia_id += 1

    df_materias = pd.DataFrame(materias)

    pares = []
    n_materias = len(df_materias)

    for i in range(n_materias):
        for j in range(i + 1, n_materias):
            m1 = df_materias.iloc[i]
            m2 = df_materias.iloc[j]

            misma_carrera = bool(m1["carrera"] == m2["carrera"])
            mismo_anio = bool(m1["anio"] == m2["anio"])

            if misma_carrera and mismo_anio:
                base_estudiantes = np.random.randint(40, 120)
                prob_conflicto_base = 0.85
            elif misma_carrera and abs(m1["anio"] - m2["anio"]) == 1:
                base_estudiantes = np.random.randint(10, 45)
                prob_conflicto_base = 0.50
            elif misma_carrera:
                base_estudiantes = np.random.randint(0, 15)
                prob_conflicto_base = 0.20
            else:
                if mismo_anio and (m1["anio"] in [1, 2]):
                    base_estudiantes = np.random.randint(15, 60)
                    prob_conflicto_base = 0.60
                else:
                    base_estudiantes = np.random.randint(0, 8)
                    prob_conflicto_base = 0.05

            cant_estudiantes_compartidos_historico = int(
                base_estudiantes * np.random.uniform(0.8, 1.2)
            )

            factor_conflicto = np.random.uniform(0.3, 0.95)
            cant_estudiantes_afectados = int(
                cant_estudiantes_compartidos_historico * factor_conflicto
            )

            hubo_conflicto = bool(
                cant_estudiantes_afectados > 10
                or (np.random.rand() < prob_conflicto_base)
            )

            pares.append(
                {
                    "materia_id_1": m1["materia_id"],
                    "materia_id_2": m2["materia_id"],
                    "cant_estudiantes_compartidos_historico": cant_estudiantes_compartidos_historico,
                    "mismo_anio": mismo_anio,
                    "misma_carrera": misma_carrera,
                    "cant_estudiantes_afectados": cant_estudiantes_afectados,
                    "hubo_conflicto": hubo_conflicto,
                }
            )

    df_dataset = pd.DataFrame(pares)

    df_materias.rename(columns={"materia_id": "id", "anio": "año"})[
        ["id", "nombre", "carrera", "año"]
    ].to_csv(PATH_MATERIAS, index=False, encoding="utf-8")

    df_dataset.to_csv(PATH_PARES, index=False, encoding="utf-8")
    print(f"Materias: {len(df_materias)}. Pares: {len(df_dataset)}.")


def load_materias(path=None):
    """Catálogo de nodos: id, nombre, carrera, año."""
    path = Path(path) if path else PATH_MATERIAS
    return pd.read_csv(path, encoding="utf-8")


def load_dataset(path=None):
    """Pares (aristas candidatas) con las columnas del enunciado."""
    path = Path(path) if path else PATH_PARES
    df = pd.read_csv(path, encoding="utf-8")
    for col in ("mismo_anio", "misma_carrera", "hubo_conflicto"):
        df[col] = (
            df[col].astype(str).str.lower().map({"true": True, "false": False})
        )
    return df


if __name__ == "__main__":
    generar_datasets()