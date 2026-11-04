import streamlit as st

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
st.sidebar.metric("Turnos necesarios", "—")
st.sidebar.metric("Aristas de conflicto", "—")

tab_grafo, tab_cronograma = st.tabs(["Grafo de conflictos", "Cronograma"])

with tab_grafo:
    st.subheader("Grafo de conflictos")
    st.info("Issue #16: visualizar materias como nodos, coloreados según el turno asignado.")
    st.write(f"Umbral actual: `{umbral}`")

with tab_cronograma:
    st.subheader("Cronograma por turno")
    st.info("Issue #17: grilla o calendario con las materias que se rinden en cada turno.")
