"""Orquesta modelo, grafo y coloreo para un umbral dado."""

from backend.coloreo import colorear
from backend.datos import load_materias, load_pares
from backend.grafo import construir_grafo
from backend.modelo import predecir


def planificar(umbral):
    """Predice conflictos, arma el grafo, colorea y arma el cronograma."""
    pares = load_pares().copy()
    pares["prediccion"] = predecir(pares)
    materias = load_materias()
    grafo = construir_grafo(pares, umbral, materias, columna="prediccion")
    colores, n_turnos = colorear(grafo)
    nodos = _nodos(grafo, colores)
    return {
        "nodos": nodos,
        "aristas": _aristas(grafo),
        "cronograma": _cronograma(nodos),
        "cantidad_turnos": n_turnos,
        "umbral": umbral,
        "grafo": grafo,
        "colores": colores,
        "pares": pares,
    }


def _nodos(grafo, colores):
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
    return nodos


def _aristas(grafo):
    aristas = []
    for m1, m2, datos in grafo.edges(data=True):
        aristas.append(
            {
                "materia_id_1": m1,
                "materia_id_2": m2,
                "peso": datos.get("peso"),
            }
        )
    return aristas


def _cronograma(nodos):
    cronograma = {}
    for nodo in nodos:
        cronograma.setdefault(nodo["turno"], []).append(nodo)
    for materias in cronograma.values():
        materias.sort(key=lambda materia: materia["nombre"])
    return dict(sorted(cronograma.items()))


if __name__ == "__main__":
    resultado = planificar(20)
    print("claves:", list(resultado.keys()))
    print("nodos:", len(resultado["nodos"]))
    print("aristas:", len(resultado["aristas"]))
    print("turnos:", resultado["cantidad_turnos"])
    print("umbral:", resultado["umbral"])
    print("materias en turno 0:", len(resultado["cronograma"].get(0, [])))
