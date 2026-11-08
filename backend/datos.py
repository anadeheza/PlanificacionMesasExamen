"""Carga del catálogo de materias y de los pares de conflicto.

Trabajo correspondiente a la issue #7.
"""
from pathlib import Path
import pandas as pd

def load_materias():
    """Devuelve el catálogo de materias (nodos del grafo)."""
    ruta = Path(__file__).resolve().parent.parent / "materias.csv"
    return pd.read_csv(ruta, encoding="utf-8")


def load_pares():
    """Devuelve el dataset de pares de materias."""
    ruta = Path(__file__).resolve().parent.parent / "dataset_mesas_examen.csv"
    df = pd.read_csv(ruta, encoding="utf-8")
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