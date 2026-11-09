"""Carga del catálogo de materias y de los pares de conflicto."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RUTA_MATERIAS = ROOT / "materias.csv"
RUTA_PARES = ROOT / "dataset_mesas_examen.csv"


def load_materias():
    """Catálogo de nodos: id, nombre, carrera, año."""
    return pd.read_csv(RUTA_MATERIAS, encoding="utf-8")


def load_pares():
    """Pares de materias con las columnas del enunciado."""
    df = pd.read_csv(RUTA_PARES, encoding="utf-8")
    for col in ("mismo_anio", "misma_carrera", "hubo_conflicto"):
        df[col] = (
            df[col].astype(str).str.lower().map({"true": True, "false": False})
        )
    return df


if __name__ == "__main__":
    materias = load_materias()
    pares = load_pares()
    print("Materias:", materias.shape, materias.columns.tolist())
    print(materias.head())
    print("Pares:", pares.shape, pares.columns.tolist())
    print(pares.head())
