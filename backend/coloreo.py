"""Coloreo greedy para asignar turnos de examen.

Welsh-Powell: se pintan primero las materias con más conflictos
(mayor grado). A cada una se le da el menor color que no usen sus vecinas.

Trabajo correspondiente a la issue #13.
"""
import networkx as nx


def colorear(grafo):
    """Asigna un turno (color) a cada materia sin superponer conflictos."""
    orden = sorted(
        grafo.nodes(),
        key=lambda materia: grafo.degree(materia),
        reverse=True,
    )
    colores = {}
    for materia in orden:
        usados = []
        for vecino in grafo.neighbors(materia):
            if vecino in colores:
                usados.append(colores[vecino])
        color = 0
        while color in usados:
            color = color + 1
        colores[materia] = color
    if len(colores) == 0:
        cantidad = 0
    else:
        cantidad = max(colores.values()) + 1
    return colores, cantidad


if __name__ == "__main__":
    triangulo = nx.Graph()
    triangulo.add_edges_from(
        [
            ("MAT_A", "MAT_B"),
            ("MAT_B", "MAT_C"),
            ("MAT_C", "MAT_A"),
        ]
    )
    colores, turnos = colorear(triangulo)
    print("Triángulo:", colores, "→", turnos, "turnos")
    bipartito = nx.Graph()
    bipartito.add_edges_from(
        [
            ("MAT_A", "MAT_B"),
            ("MAT_C", "MAT_D"),
        ]
    )
    colores, turnos = colorear(bipartito)
    print("Bipartito:", colores, "→", turnos, "turnos")
    con_aislada = nx.Graph()
    con_aislada.add_edges_from([("MAT_A", "MAT_B")])
    con_aislada.add_node("MAT_Z")
    colores, turnos = colorear(con_aislada)
    print("Con aislada:", colores, "→", turnos, "turnos")