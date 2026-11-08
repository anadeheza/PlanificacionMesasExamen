"""Dibuja el grafo de conflictos para la interfaz.

Cada materia es un rectángulo con el nombre adentro. El turno es el color
del borde. Las aristas tienen el mismo grosor y el peso queda apoyado
sobre la línea, como si la arista lo subrayara.

Al cambiar el umbral, el dibujo parte del grafo anterior y se mueve hasta
el nuevo: los nodos viajan, los bordes cambian de color y las aristas
aparecen o se desvanecen.
"""
import html
import json
import math
from pathlib import Path

import pandas as pd
import streamlit.components.v1 as components

_COMPONENTE = components.declare_component(
    "grafo_animado",
    path=str(Path(__file__).resolve().parent / "componente_grafo"),
)

PALETA_TURNO = ["#4C78A8", "#F58518", "#54A24B", "#BF8FF0", "#B279A2"]
GROSOR_ARISTA = 2
ALTO_NODO = 46


def datos_mock():
    """Pares de ejemplo, con una materia que no tiene ningún conflicto."""
    materias = pd.DataFrame(
        [
            {"id": "ALG", "nombre": "Álgebra I", "carrera": "Informática", "anio": 1},
            {"id": "PROG", "nombre": "Programación I", "carrera": "Informática", "anio": 1},
            {"id": "AM", "nombre": "Análisis Matemático", "carrera": "Informática", "anio": 1},
            {"id": "FIS", "nombre": "Física I", "carrera": "Industrial", "anio": 1},
            {"id": "QUI", "nombre": "Química", "carrera": "Industrial", "anio": 1},
            {"id": "ELE", "nombre": "Electiva", "carrera": "Informática", "anio": 3},
        ]
    )
    pares = pd.DataFrame(
        [
            {"materia_id_1": "ALG", "materia_id_2": "PROG", "prediccion": 0.90},
            {"materia_id_1": "ALG", "materia_id_2": "AM", "prediccion": 0.75},
            {"materia_id_1": "PROG", "materia_id_2": "AM", "prediccion": 0.60},
            {"materia_id_1": "FIS", "materia_id_2": "QUI", "prediccion": 0.45},
            {"materia_id_1": "AM", "materia_id_2": "FIS", "prediccion": 0.30},
        ]
    )
    return materias, pares


def mostrar_grafo(grafo, colores, aristas, paleta=None):
    """Muestra el grafo en un componente que sigue vivo entre un umbral y otro.

    Así el dibujo no se destruye al mover el slider: los nodos se desplazan
    y las aristas aparecen o se van, sin el flash negro de recargar el iframe.
    """
    paleta = paleta or PALETA_TURNO
    escena = _escena(grafo, colores, _lista_aristas(aristas, grafo), paleta)
    _COMPONENTE(escena=escena, key="grafo_conflictos", default=None)


def svg_grafo(grafo, colores, paleta=None, aristas=None):
    """Devuelve el SVG del grafo. Sin nodos, devuelve una cadena vacía."""
    return html_transicion(grafo, colores, grafo, colores, aristas, paleta, animar=False)


def html_transicion(grafo_desde, colores_desde, grafo_hasta, colores_hasta, aristas=None, paleta=None, animar=True):
    """Dibuja el grafo de partida y, si cambia el umbral, lo anima hasta el nuevo."""
    if grafo_hasta.number_of_nodes() == 0:
        return ""

    paleta = paleta or PALETA_TURNO
    lista = _lista_aristas(aristas, grafo_hasta)
    desde = _escena(grafo_desde, colores_desde, lista, paleta)
    hasta = _escena(grafo_hasta, colores_hasta, lista, paleta)
    if not animar or desde == hasta:
        return _svg(desde, None)

    datos = json.dumps({"desde": desde, "hasta": hasta}, ensure_ascii=False).replace("<", "\\u003c")
    return _svg(desde, datos)


def _lista_aristas(aristas, grafo):
    if aristas is None:
        return [
            (a, b, float(dato.get("peso", dato.get("weight", 1))))
            for a, b, dato in grafo.edges(data=True)
        ]
    if isinstance(aristas, pd.DataFrame):
        if "prediccion" in aristas.columns:
            columna = "prediccion"
        elif "cant_estudiantes_afectados" in aristas.columns:
            columna = "cant_estudiantes_afectados"
        else:
            columna = "peso"
        return [
            (fila.materia_id_1, fila.materia_id_2, float(getattr(fila, columna)))
            for fila in aristas.itertuples(index=False)
        ]
    return [(a, b, float(peso)) for a, b, peso in aristas]


def _escena(grafo, colores, aristas, paleta):
    ancho, alto = 960, 540
    medidas = {
        nodo: _medida(grafo.nodes[nodo].get("nombre") or str(nodo))
        for nodo in grafo.nodes
    }
    posiciones = _posiciones(grafo, medidas, ancho, alto)
    nodos = []
    for nodo in grafo.nodes:
        x, y = posiciones[nodo]
        ancho_nodo, alto_nodo = medidas[nodo]
        turno = int(colores.get(nodo, 0))
        nodos.append(
            {
                "id": str(nodo),
                "nombre": grafo.nodes[nodo].get("nombre") or str(nodo),
                "x": x,
                "y": y,
                "w": ancho_nodo,
                "h": alto_nodo,
                "color": paleta[turno % len(paleta)],
                "turno": turno,
                "aislado": grafo.degree(nodo) == 0,
            }
        )
    dibujo_aristas = []
    for materia_a, materia_b, peso in aristas:
        if materia_a not in posiciones or materia_b not in posiciones:
            continue
        x1, y1 = posiciones[materia_a]
        x2, y2 = posiciones[materia_b]
        clave = tuple(sorted((str(materia_a), str(materia_b))))
        dibujo_aristas.append(
            {
                "id": f"{clave[0]}|{clave[1]}",
                "peso": peso,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "mx": (x1 + x2) / 2,
                "my": (y1 + y2) / 2,
                "angulo": _angulo(x1, y1, x2, y2),
                "opacidad": 1 if grafo.has_edge(materia_a, materia_b) else 0,
            }
        )
    return {"nodos": nodos, "aristas": dibujo_aristas}


def _svg(escena, datos_animacion):
    partes = [
        '<svg viewBox="0 0 960 540" xmlns="http://www.w3.org/2000/svg" '
        'role="img" aria-label="Grafo de conflictos" '
        'preserveAspectRatio="xMidYMid meet" '
        'style="width:100%;height:500px;display:block;background:#f7f8fa;border-radius:12px;">'
    ]
    for arista in escena["aristas"]:
        partes.append(
            f'<line x1="{arista["x1"]:.1f}" y1="{arista["y1"]:.1f}" '
            f'x2="{arista["x2"]:.1f}" y2="{arista["y2"]:.1f}" '
            f'stroke="#5c6770" stroke-width="{GROSOR_ARISTA}" stroke-linecap="butt" '
            f'opacity="{arista["opacidad"]}" '
            f'data-arista="{html.escape(arista["id"])}">'
            f"<title>{html.escape(arista['id'])}: {arista['peso']:.2f}</title>"
            f"</line>"
        )
    for nodo in escena["nodos"]:
        partes.append(
            f'<rect x="{nodo["x"] - nodo["w"] / 2:.1f}" y="{nodo["y"] - nodo["h"] / 2:.1f}" '
            f'width="{nodo["w"]:.1f}" height="{nodo["h"]:.1f}" rx="6" '
            f'fill="#ffffff" stroke="{nodo["color"]}" stroke-width="3" '
            f'data-nodo="{html.escape(nodo["id"])}" data-turno="{nodo["turno"]}" '
            f'data-aislado="{1 if nodo["aislado"] else 0}">'
            f"<title>{html.escape(nodo['nombre'])} · Turno {nodo['turno']}</title>"
            f"</rect>"
        )
        partes.append(
            f'<text x="{nodo["x"]:.1f}" y="{nodo["y"]:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="15" font-family="sans-serif" fill="#1f2933" '
            f'data-nombre="{html.escape(nodo["id"])}">'
            f"{html.escape(nodo['nombre'])}</text>"
        )
    for arista in escena["aristas"]:
        partes.append(
            f'<text transform="translate({arista["mx"]:.1f},{arista["my"]:.1f}) '
            f'rotate({arista["angulo"]:.1f})" x="0" y="-5" text-anchor="middle" '
            f'font-size="14" font-weight="600" font-family="sans-serif" fill="#1f2933" '
            f'opacity="{arista["opacidad"]}" data-peso="{html.escape(arista["id"])}">'
            f"{arista['peso']:.2f}</text>"
        )
    partes.append("</svg>")
    if datos_animacion:
        partes.append("<script>")
        partes.append(_SCRIPT.replace("__DATOS__", datos_animacion))
        partes.append("</script>")
    return "".join(partes)


_SCRIPT = """
const datos = __DATOS__;
const duracion = 560;
const nodosDesde = Object.fromEntries(datos.desde.nodos.map((nodo) => [nodo.id, nodo]));
const nodosHasta = Object.fromEntries(datos.hasta.nodos.map((nodo) => [nodo.id, nodo]));
const aristasDesde = Object.fromEntries(datos.desde.aristas.map((arista) => [arista.id, arista]));
const aristasHasta = Object.fromEntries(datos.hasta.aristas.map((arista) => [arista.id, arista]));
const reducir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function mezclar(origen, destino, t) {
  return origen + (destino - origen) * t;
}
function suave(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}
function color(origen, destino, t) {
  const a = parseInt(origen.slice(1), 16);
  const b = parseInt(destino.slice(1), 16);
  const canales = [16, 8, 0].map((desplazamiento) => {
    const desde = (a >> desplazamiento) & 255;
    const hasta = (b >> desplazamiento) & 255;
    return Math.round(mezclar(desde, hasta, t)).toString(16).padStart(2, "0");
  });
  return "#" + canales.join("");
}
function angulo(origen, destino, t) {
  let delta = destino - origen;
  while (delta > 180) delta -= 360;
  while (delta < -180) delta += 360;
  return origen + delta * t;
}
function cuadro(t) {
  for (const id of Object.keys(nodosHasta)) {
    const desde = nodosDesde[id];
    const hasta = nodosHasta[id];
    const x = mezclar(desde.x, hasta.x, t);
    const y = mezclar(desde.y, hasta.y, t);
    const rect = document.querySelector('[data-nodo="' + id + '"]');
    rect.setAttribute("x", (x - desde.w / 2).toFixed(1));
    rect.setAttribute("y", (y - desde.h / 2).toFixed(1));
    rect.setAttribute("stroke", color(desde.color, hasta.color, t));
    const nombre = document.querySelector('[data-nombre="' + id + '"]');
    nombre.setAttribute("x", x.toFixed(1));
    nombre.setAttribute("y", y.toFixed(1));
  }
  for (const id of Object.keys(aristasHasta)) {
    const desde = aristasDesde[id];
    const hasta = aristasHasta[id];
    const linea = document.querySelector('[data-arista="' + id + '"]');
    linea.setAttribute("x1", mezclar(desde.x1, hasta.x1, t).toFixed(1));
    linea.setAttribute("y1", mezclar(desde.y1, hasta.y1, t).toFixed(1));
    linea.setAttribute("x2", mezclar(desde.x2, hasta.x2, t).toFixed(1));
    linea.setAttribute("y2", mezclar(desde.y2, hasta.y2, t).toFixed(1));
    const opacidad = mezclar(desde.opacidad, hasta.opacidad, t).toFixed(3);
    linea.setAttribute("opacity", opacidad);
    const peso = document.querySelector('[data-peso="' + id + '"]');
    const mx = mezclar(desde.mx, hasta.mx, t);
    const my = mezclar(desde.my, hasta.my, t);
    peso.setAttribute(
      "transform",
      "translate(" + mx.toFixed(1) + "," + my.toFixed(1) + ") rotate(" + angulo(desde.angulo, hasta.angulo, t).toFixed(1) + ")"
    );
    peso.setAttribute("opacity", opacidad);
  }
}
if (reducir) {
  cuadro(1);
} else {
  const inicio = performance.now();
  function paso(ahora) {
    const t = Math.min(1, (ahora - inicio) / duracion);
    cuadro(suave(t));
    if (t < 1) requestAnimationFrame(paso);
  }
  requestAnimationFrame(paso);
}
"""


def _medida(nombre):
    ancho = max(124, len(str(nombre)) * 8.6 + 36)
    return ancho, ALTO_NODO


def _angulo(x1, y1, x2, y2):
    """Deja el texto de pie: la arista queda debajo del peso, nunca al revés."""
    angulo = math.atan2(y2 - y1, x2 - x1)
    if angulo > math.pi / 2 or angulo < -math.pi / 2:
        angulo += math.pi
    return math.degrees(angulo)


def _posiciones(grafo, medidas, ancho, alto):
    conectados = sorted(nodo for nodo in grafo.nodes if grafo.degree(nodo) > 0)
    aislados = sorted(nodo for nodo in grafo.nodes if grafo.degree(nodo) == 0)
    posiciones = {}
    margen = 20

    if conectados and aislados:
        ancho_columna = max(medidas[nodo][0] for nodo in aislados)
        izquierda = margen + ancho_columna + 56
    else:
        ancho_columna = 0
        izquierda = margen

    if conectados:
        derecha = ancho - margen
        centro_x = (izquierda + derecha) / 2
        medio_ancho = max(medidas[nodo][0] for nodo in conectados) / 2
        radio_tope = min(
            (derecha - izquierda) / 2 - medio_ancho - 8,
            alto / 2 - ALTO_NODO / 2 - margen,
        )
        radio = 0 if len(conectados) == 1 else max(90, radio_tope)
        for i, nodo in enumerate(conectados):
            angulo = -math.pi / 2 + 2 * math.pi * i / len(conectados)
            posiciones[nodo] = (
                centro_x + radio * math.cos(angulo),
                alto / 2 + radio * math.sin(angulo),
            )

    if aislados and conectados:
        posiciones.update(_columna(aislados, medidas, margen, alto))
    elif aislados:
        posiciones.update(_fila(aislados, medidas, alto / 2, ancho))
    return posiciones


def _columna(nodos, medidas, margen, alto):
    """Apila los nodos aislados a la izquierda, alineados por el borde izquierdo."""
    separacion = 22
    total = sum(medidas[nodo][1] for nodo in nodos) + separacion * (len(nodos) - 1)
    cursor = max(16, (alto - total) / 2)
    posiciones = {}
    for nodo in nodos:
        ancho_nodo, alto_nodo = medidas[nodo]
        posiciones[nodo] = (margen + ancho_nodo / 2, cursor + alto_nodo / 2)
        cursor += alto_nodo + separacion
    return posiciones


def _fila(nodos, medidas, y, ancho):
    separacion = 26
    total = sum(medidas[nodo][0] for nodo in nodos) + separacion * (len(nodos) - 1)
    cursor = (ancho - total) / 2
    posiciones = {}
    for nodo in nodos:
        ancho_nodo = medidas[nodo][0]
        posiciones[nodo] = (cursor + ancho_nodo / 2, y)
        cursor += ancho_nodo + separacion
    return posiciones
