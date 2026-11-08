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
    materias = load_materias()
    grafo = construir_grafo(pares, umbral, materias, columna="prediccion")
    colores, n_turnos = colorear(grafo)
    nodos = []
    for materia_id, datos in grafo.nodes(data=True):
        nodos.append(
            {
                "id": materia_id,
                "nombre": datos.get("nombre", materia_id),
                "carrera": datos.get("carrera", ""),
                "anio": datos.get("año", datos.get("anio", "")),
                "turno": colores[materia_id],
            }
        )
    aristas = []
    for m1, m2, datos in grafo.edges(data=True):
        aristas.append(
            {
                "materia_id_1": m1,
                "materia_id_2": m2,
                "peso": datos.get("peso"),
            }
        )
    cronograma = {}
    for nodo in nodos:
        cronograma.setdefault(nodo["turno"], []).append(nodo)
    return {
        "nodos": nodos,
        "aristas": aristas,
        "cronograma": cronograma,
        "cantidad_turnos": n_turnos,
        "umbral": umbral,
        "grafo": grafo,
        "colores": colores,
        "pares": pares,
    }


if __name__ == "__main__":
    resultado = planificar(20)
    print("claves:", resultado.keys())
    print("nodos:", len(resultado["nodos"]))
    print("aristas:", len(resultado["aristas"]))
    print("turnos:", resultado["cantidad_turnos"])
    print("umbral:", resultado["umbral"])
    print("materias en turno 0:",
len(resultado["cronograma"].get(0, [])))