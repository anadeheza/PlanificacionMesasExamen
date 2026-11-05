import streamlit as st
COLORES_TURNO = ["#4C78A8", "#F58518", "#54A24B", "#BF8FF0", "#B279A2"]

st.set_page_config(
    page_title="Planificación de mesas de examen",
    layout="wide",
)

st.title("Planificación de mesas de examen")
st.caption("Esqueleto del TP. El modelo, el grafo y las vistas se completan en las issues.")

umbral = st.sidebar.slider(
    "Umbral de conflicto",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
    help="Issue #18: al cambiar el umbral se recalculan el grafo y los turnos.",
)
st.sidebar.metric("Aristas de conflicto", "—")

tab_grafo, tab_cronograma = st.tabs(["Grafo de conflictos", "Cronograma"])

with tab_grafo:
    st.subheader("Grafo de conflictos")
    st.info("Issue #16: visualizar materias como nodos, coloreados según el turno asignado.")
    st.write(f"Umbral actual: `{umbral}`")

with tab_cronograma:
    st.subheader("Cronograma por turno")
    cronograma = {
        0: [
            {"nombre": "Álgebra I", "carrera": "Informática", "anio": 1},
            {"nombre": "Química", "carrera": "Industrial", "anio": 1},
        ],
        1: [
            {"nombre": "Programación I", "carrera": "Informática", "anio": 1},
        ],
        2: [
            {"nombre": "Análisis Matemático", "carrera": "Informática", "anio": 1},
            {"nombre": "Física I", "carrera": "Industrial", "anio": 1},
        ],
    }
    st.metric("Turnos necesarios", len(cronograma))
    columnas = st.columns(len(cronograma))
    for i, (turno, materias) in enumerate(sorted(cronograma.items())):
        with columnas[i]:
            color = COLORES_TURNO[turno % len(COLORES_TURNO)]
            st.markdown(f"<h3 style='border-bottom: 4px solid {color};'>Turno {turno}</h3>", unsafe_allow_html=True,)
            for materia in materias:
                st.markdown(f"**{materia['nombre']}**")
                st.caption(f"{materia['carrera']} · Año {materia['anio']}")
    st.sidebar.metric("Turnos necesarios", len(cronograma))
