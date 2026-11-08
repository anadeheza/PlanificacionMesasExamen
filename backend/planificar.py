"""Orquesta modelo, grafo y coloreo para un umbral dado.

Trabajo correspondiente a la issue #15.
"""
from backend.datos import load_pares
from backend.modelo import predecir


def planificar(umbral):
    """Devuelve nodos, aristas, cronograma y cantidad de turnos."""
    pares = load_pares()
    pares = pares.copy()
    pares["prediccion"] = predecir(pares)
    print("Umbral recibido:", umbral)
    print("Predicciones (estudiantes afectados):")
    print(pares["prediccion"].describe())

if __name__ == "__main__":
    planificar(20)