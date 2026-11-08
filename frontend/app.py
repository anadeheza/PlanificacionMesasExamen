import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "frontend") not in sys.path:
    sys.path.insert(0, str(RAIZ / "frontend"))

import streamlit as st

from backend.planificar import planificar
from visualizar_grafo import PALETA_TURNO, mostrar_grafo


def _color_turno(turno):
    return PALETA_TURNO[turno % len(PALETA_TURNO)]


st.set_page_config(
    page_title="Planificación de mesas de examen",
    layout="wide",
)

st.title("Planificación de mesas de examen")

umbral = st.sidebar.slider(
    "Umbral de conflicto",
    min_value=0,
    max_value=80,
    value=20,
    step=5,
    help="Estudiantes afectados predichos. Por encima de este número hay arista de conflicto.",
)

resultado = planificar(umbral)
grafo = resultado["grafo"]
colores = resultado["colores"]
pares = resultado["pares"]
n_turnos = resultado["cantidad_turnos"]
cronograma = resultado["cronograma"]

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
            leyenda[turno].markdown(
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"<span style='width:14px;height:14px;border-radius:3px;"
                f"background:#ffffff;border:3px solid {_color_turno(turno)};"
                f"display:inline-block;box-sizing:border-box'></span>"
                f"Turno {turno}</div>",
                unsafe_allow_html=True,
            )
        mostrar_grafo(grafo, colores, pares, PALETA_TURNO)

with tab_cronograma:
    st.subheader("Cronograma por turno")
    if n_turnos == 0:
        st.info("No hay materias para armar el cronograma.")
    else:
        st.metric("Turnos necesarios", n_turnos)
        columnas = st.columns(n_turnos)
        for turno, materias in cronograma.items():
            with columnas[turno]:
                st.markdown(
                    f"<h3 style='border-bottom: 4px solid {_color_turno(turno)};'>"
                    f"Turno {turno}</h3>",
                    unsafe_allow_html=True,
                )
                for materia in materias:
                    st.markdown(f"**{materia['nombre']}**")
                    st.caption(f"{materia['carrera']} · Año {materia['anio']}")
