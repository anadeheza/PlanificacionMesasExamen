"""Carga del catálogo de materias y de los pares de conflicto."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RUTA_MATERIAS = ROOT / "materias.csv"
RUTA_PARES = ROOT / "dataset_mesas_examen.csv"


def asegurar_csv():
    """Genera los CSV si no están (en Cloud no se suben a git)."""
    if RUTA_MATERIAS.exists() and RUTA_PARES.exists():
        return
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from dataset import generar_datasets

    generar_datasets()


def load_materias():
    """Catálogo de nodos: id, nombre, carrera, año."""
    asegurar_csv()
    return pd.read_csv(RUTA_MATERIAS, encoding="utf-8")


def load_pares():
    """Pares de materias con las columnas del enunciado."""
    asegurar_csv()
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
