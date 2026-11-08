import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "frontend") not in sys.path:
    sys.path.insert(0, str(RAIZ / "frontend"))

import streamlit as st

from backend.coloreo import colorear
from backend.grafo import construir_grafo
from visualizar_grafo import PALETA_TURNO, datos_mock, mostrar_grafo

COLORES_TURNO = PALETA_TURNO


def _cronograma(catalogo, colores):
    """Agrupa las materias por el turno que les asignó el coloreo."""
    filas = {fila["id"]: fila for fila in catalogo.to_dict(orient="records")}
    grupos = {}
    for materia_id, turno in colores.items():
        fila = filas.get(
            materia_id,
            {"nombre": str(materia_id), "carrera": "", "anio": ""},
        )
        grupos.setdefault(int(turno), []).append(fila)
    for materias in grupos.values():
        materias.sort(key=lambda materia: materia["nombre"])
    return dict(sorted(grupos.items()))

st.set_page_config(
    page_title="Planificación de mesas de examen",
    layout="wide",
)

st.title("Planificación de mesas de examen")
umbral = st.sidebar.slider(
    "Umbral de conflicto",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
    help="Issue #18: al cambiar el umbral se recalculan el grafo y los turnos.",
)

catalogo, pares = datos_mock()
grafo = construir_grafo(pares, umbral, catalogo)
colores, n_turnos = colorear(grafo)

st.sidebar.metric("Aristas de conflicto", grafo.number_of_edges())
st.sidebar.metric("Turnos necesarios", n_turnos)

tab_grafo, tab_cronograma = st.tabs(["Grafo de conflictos", "Cronograma"])

with tab_grafo:
    st.subheader("Grafo de conflictos")
    if grafo.number_of_nodes() == 0:
        st.info("No hay materias para mostrar.")
    else:
        if grafo.number_of_edges() == 0:
            st.info("Ningún par llega al umbral. Las materias quedan como nodos aislados.")
        leyenda = st.columns(max(n_turnos, 1))
        for turno in range(n_turnos):
            color = COLORES_TURNO[turno % len(COLORES_TURNO)]
            leyenda[turno].markdown(
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"<span style='width:14px;height:14px;border-radius:3px;background:#ffffff;border:3px solid {color};display:inline-block;box-sizing:border-box'></span>"
                f"Turno {turno}</div>",
                unsafe_allow_html=True,
            )
        mostrar_grafo(grafo, colores, pares, COLORES_TURNO)

with tab_cronograma:
    st.subheader("Cronograma por turno")
    if n_turnos == 0:
        st.info("No hay materias para armar el cronograma.")
    else:
        cronograma = _cronograma(catalogo, colores)
        st.metric("Turnos necesarios", n_turnos)
        columnas = st.columns(n_turnos)
        for turno, materias in cronograma.items():
            with columnas[turno]:
                color = COLORES_TURNO[turno % len(COLORES_TURNO)]
                st.markdown(
                    f"<h3 style='border-bottom: 4px solid {color};'>Turno {turno}</h3>",
                    unsafe_allow_html=True,
                )
                for materia in materias:
                    st.markdown(f"**{materia['nombre']}**")
                    st.caption(f"{materia['carrera']} · Año {materia['anio']}")
