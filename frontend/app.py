import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(RAIZ / "frontend") not in sys.path:
    sys.path.insert(0, str(RAIZ / "frontend"))

import streamlit as st

from backend.planificar import planificar
from visualizar_grafo import color_de_turno, mostrar_grafo


def _color_turno(turno):
    return color_de_turno(turno)


st.set_page_config(
    page_title="Planificación de mesas de examen",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      footer { display: none; }
      .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 0.2rem !important;
      }
      h1 {
        font-size: 1.2rem !important;
        line-height: 1.5 !important;
        margin: 0 0 0.45rem 0 !important;
        padding: 0 !important;
      }
      div[data-testid="stHeading"] { margin: 0 0 0.35rem 0 !important; }
      button[data-baseweb="tab"] {
        font-size: 0.85rem !important;
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
      }
      div[data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Planificación de mesas de examen")
st.caption(
    "El modelo estima cuántos estudiantes se ven afectados si dos materias rinden juntas. "
    "El umbral arma el grafo de conflictos y el coloreo asigna un turno a cada materia."
)

st.sidebar.header("Conflicto")
umbral = st.sidebar.slider(
    "Umbral (estudiantes afectados)",
    min_value=0,
    max_value=80,
    value=20,
    step=5,
    help="Si la predicción es mayor o igual a este número, esas materias no pueden compartir turno.",
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
    if grafo.number_of_nodes() == 0:
        st.info("No hay materias para mostrar.")
    else:
        if grafo.number_of_edges() == 0:
            st.info("Ningún par llega al umbral. Las materias quedan como nodos aislados.")
        mostrar_grafo(grafo, colores, pares)
        leyenda = "".join(
            f"<span style='display:inline-flex;align-items:center;gap:6px;"
            f"margin-right:14px;font-size:13px;line-height:1'>"
            f"<span style='width:10px;height:10px;border-radius:50%;"
            f"background:{_color_turno(turno)};display:inline-block'></span>"
            f"Turno {turno + 1}</span>"
            for turno in range(n_turnos)
        )
        st.markdown(
            f"<div style='display:flex;flex-wrap:wrap;align-items:center;"
            f"margin:2px 0 0'>{leyenda}</div>",
            unsafe_allow_html=True,
        )

with tab_cronograma:
    if n_turnos == 0:
        st.info("No hay materias para armar el cronograma.")
    else:
        tarjetas = []
        for turno, materias in cronograma.items():
            filas = "".join(
                "<div style='margin:0 0 0.9rem'>"
                f"<div style='font-weight:650;line-height:1.2;overflow-wrap:anywhere'>"
                f"{html.escape(str(materia['nombre']))}</div>"
                "<div style='color:#52606d;font-size:0.8rem;line-height:1.2;"
                "margin-top:0.1rem;overflow-wrap:anywhere'>"
                f"{html.escape(str(materia['carrera']))} · Año {html.escape(str(materia['anio']))}"
                "</div></div>"
                for materia in materias
            )
            tarjetas.append(
                "<section style='flex:1 1 220px;min-width:0;max-width:100%'>"
                f"<div style='font-size:1.15rem;font-weight:650;margin:0 0 0.6rem;"
                f"padding-bottom:4px;border-bottom:4px solid {_color_turno(turno)}'>"
                f"Turno {turno + 1}</div>"
                f"{filas}"
                "</section>"
            )
        st.html(
            "<div style='display:flex;flex-wrap:wrap;gap:28px 32px;align-items:flex-start'>"
            + "".join(tarjetas)
            + "</div>"
        )
