"""Orquesta modelo, grafo y coloreo para un umbral dado.

Trabajo correspondiente a la issue #15.
"""
from backend.datos import load_materias, load_pares
from backend.modelo import predecir
from backend.grafo import construir_grafo
from backend.coloreo import colorear


def planificar(umbral):
    """Devuelve nodos, aristas, cronograma y cantidad de turnos."""
    pares = load_pares()
    pares = pares.copy()
    pares["prediccion"] = predecir(pares)
    print("Umbral recibido:", umbral)
    print("Predicciones (estudiantes afectados):")
    print(pares["prediccion"].describe())
    materias = load_materias()
    grafo = construir_grafo(pares, umbral, materias, columna="prediccion")
    colores, n_turnos = colorear(grafo)
    print("Nodos:", grafo.number_of_nodes())
    print("Aristas:", grafo.number_of_edges())
    print("Turnos:", n_turnos)

if __name__ == "__main__":
    print("--- umbral 5 ---")
    planificar(5)
    print("--- umbral 40 ---")
    planificar(40)