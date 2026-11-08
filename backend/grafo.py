import networkx as nx
import pandas as pd

_COLUMNAS_PUNTAJE = (
    "prediccion",
    "probabilidad",
    "prob",
    "cant_estudiantes_afectados",
    "hubo_conflicto",
)


def construir_grafo(predicciones, umbral, materias=None, columna=None):
    """Arma un grafo no dirigido filtrando aristas según el umbral.
    predicciones tiene materia_id_1, materia_id_2 y un puntaje. Si no se
    indica columna, se usa la primera que exista entre prediccion,
    probabilidad, prob, cant_estudiantes_afectados y hubo_conflicto.
    materias es el catálogo: una lista de ids o un dataframe
    con columna id. Esas materias son nodos aunque no aparezcan en ningún
    par (nodos aislados).
    hay arista cuando puntaje >= umbral. el peso
    queda en los atributos peso y weight.
    """
    df = _como_dataframe(predicciones)
    puntaje = _puntajes(df, columna)
    grafo = nx.Graph()
    _agregar_nodos(grafo, df, materias)

    entra = (
        (df["materia_id_1"] != df["materia_id_2"]) #me aseguro de no armar un lazo
        & puntaje.notna()
        & (puntaje >= umbral)
    )
    mejor_peso = {}

    for materia_a, materia_b, peso in zip(
        df.loc[entra, "materia_id_1"],
        df.loc[entra, "materia_id_2"],
        puntaje.loc[entra],
    ):
        if materia_a > materia_b:
            materia_a, materia_b = materia_b, materia_a
        peso = float(peso)
        clave = (materia_a, materia_b)
        if clave not in mejor_peso or peso > mejor_peso[clave]:
            mejor_peso[clave] = peso

    for (materia_a, materia_b), peso in mejor_peso.items():
        grafo.add_edge(materia_a, materia_b, peso=peso, weight=peso)
    return grafo


def _como_dataframe(predicciones):
    if not isinstance(predicciones, pd.DataFrame):
        predicciones = pd.DataFrame(predicciones)
    faltan = {"materia_id_1", "materia_id_2"} - set(predicciones.columns)
    if faltan:
        raise ValueError(
            "predicciones necesita materia_id_1 y materia_id_2, "
            "más un puntaje (prediccion, cant_estudiantes_afectados, "
            "probabilidad o hubo_conflicto)."
        )
    return predicciones


def _elegir_columna(df, columna):
    if columna is not None:
        if columna not in df.columns:
            raise ValueError(f"No existe la columna de puntaje {columna!r}.")
        return columna
    for nombre in _COLUMNAS_PUNTAJE:
        if nombre in df.columns:
            return nombre
    raise ValueError(
        "predicciones no tiene columna de puntaje. "
        f"Se espera una de: {', '.join(_COLUMNAS_PUNTAJE)}."
    )


def _puntajes(df, columna):
    serie = df[_elegir_columna(df, columna)]
    if pd.api.types.is_bool_dtype(serie):
        return serie.astype(float)
    if pd.api.types.is_object_dtype(serie) or pd.api.types.is_string_dtype(serie):
        texto = serie.map(lambda valor: str(valor).strip().lower() if pd.notna(valor) else valor)
        mapa = {"true": 1.0, "false": 0.0, "1": 1.0, "0": 0.0}
        if serie.notna().all() and set(texto.unique()).issubset(mapa):
            return texto.map(mapa).astype(float)
    return pd.to_numeric(serie, errors="coerce")


def _agregar_nodos(grafo, df, materias):
    if isinstance(materias, pd.DataFrame):
        id_col = "id" if "id" in materias.columns else "materia_id"
        if id_col not in materias.columns:
            raise ValueError("materias necesita una columna id.")
        for fila in materias.to_dict(orient="records"):
            nodo = fila.pop(id_col)
            grafo.add_node(nodo, **fila)
    elif materias is not None:
        grafo.add_nodes_from(materias)

    if len(df) == 0:
        return
    ids = pd.unique(df[["materia_id_1", "materia_id_2"]].to_numpy().ravel())
    grafo.add_nodes_from(ids.tolist())


if __name__ == "__main__":
    from pathlib import Path

    ruta = Path(__file__).resolve().parent.parent / "dataset_mesas_examen.csv"
    pares = pd.read_csv(ruta)
    umbral_bajo = 10
    umbral_alto = 40
    grafo_bajo = construir_grafo(pares, umbral_bajo)
    grafo_alto = construir_grafo(pares, umbral_alto)
    print("nodos:", grafo_bajo.number_of_nodes())
    print(f"aristas con umbral {umbral_bajo}:", grafo_bajo.number_of_edges())
    print(f"aristas con umbral {umbral_alto}:", grafo_alto.number_of_edges())
