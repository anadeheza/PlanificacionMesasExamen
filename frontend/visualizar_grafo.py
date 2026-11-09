"""Dibuja el grafo de conflictos para la interfaz.

Cada materia es un punto. El turno es el color del punto. Las materias
de una misma carrera quedan juntas en el círculo. El grosor de la arista
crece con la cantidad de estudiantes. El peso y el nombre aparecen al
pasar el mouse, en tamaño de pantalla, para que se puedan leer.

Al cambiar el umbral, el dibujo parte del grafo anterior y se mueve hasta
el nuevo: los nodos viajan, los bordes cambian de color y las aristas
aparecen o se desvanecen.
"""
import colorsys
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

PALETA_TURNO = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#72B7B2",
    "#B279A2",
    "#EECA3B",
    "#FF9DA6",
    "#9D755D",
    "#499894",
    "#D67195",
    "#8CD17D",
]


def color_de_turno(turno, paleta=None):
    """Un color distinto por turno. Los primeros son fijos; el resto no se repite."""
    paleta = paleta or PALETA_TURNO
    indice = int(turno)
    if indice < len(paleta):
        return paleta[indice]
    tono = (0.07 + indice * 0.61803398875) % 1
    rojo, verde, azul = colorsys.hsv_to_rgb(tono, 0.72, 0.78)
    return "#{:02X}{:02X}{:02X}".format(round(rojo * 255), round(verde * 255), round(azul * 255))
GROSOR_ARISTA = 2
TAMANO_PUNTO = 26
ESPACIO_PUNTOS = 52


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
    medidas = {
        nodo: _medida(grafo.nodes[nodo].get("nombre") or str(nodo))
        for nodo in grafo.nodes
    }
    ancho, alto, posiciones = _geometria(grafo, medidas)
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
                "color": color_de_turno(turno, paleta),
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
        identificador = f"{clave[0]}|{clave[1]}"
        opacidad = 1 if grafo.has_edge(materia_a, materia_b) else 0
        previo = next((item for item in dibujo_aristas if item["id"] == identificador), None)
        if previo is not None:
            if opacidad > previo["opacidad"]:
                previo["opacidad"] = opacidad
                previo["peso"] = peso
            continue
        dibujo_aristas.append(
            {
                "id": identificador,
                "peso": peso,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "w1": medidas[materia_a][0],
                "h1": medidas[materia_a][1],
                "w2": medidas[materia_b][0],
                "h2": medidas[materia_b][1],
                "origen": str(materia_a),
                "destino": str(materia_b),
                "grosor": _grosor(peso),
                "angulo": _angulo(x1, y1, x2, y2),
                "opacidad": opacidad,
            }
        )
    _acomodar_pesos(dibujo_aristas)
    return {"nodos": nodos, "aristas": dibujo_aristas, "ancho": ancho, "alto": alto}


def _svg(escena, datos_animacion):
    ancho = escena.get("ancho", 960)
    alto = escena.get("alto", 540)
    partes = [
        f'<svg viewBox="0 0 {ancho:.0f} {alto:.0f}" xmlns="http://www.w3.org/2000/svg" '
        'role="img" aria-label="Grafo de conflictos" '
        f'style="width:{ancho:.0f}px;height:{alto:.0f}px;display:block;background:#f7f8fa;">'
    ]
    for arista in escena["aristas"]:
        partes.append(
            f'<line x1="{arista["x1"]:.1f}" y1="{arista["y1"]:.1f}" '
            f'x2="{arista["x2"]:.1f}" y2="{arista["y2"]:.1f}" '
            f'stroke="#5c6770" stroke-width="{arista.get("grosor", GROSOR_ARISTA):.2f}" '
            f'vector-effect="non-scaling-stroke" stroke-linecap="round" '
            f'opacity="{arista["opacidad"]}" '
            f'data-arista="{html.escape(arista["id"])}">'
            f"<title>{html.escape(arista['id'])}: {arista['peso']:.2f}</title>"
            f"</line>"
        )
    for nodo in escena["nodos"]:
        radio = nodo["w"] / 2
        partes.append(
            f'<circle cx="{nodo["x"]:.1f}" cy="{nodo["y"]:.1f}" r="{radio:.1f}" '
            f'fill="{nodo["color"]}" stroke="#ffffff" stroke-width="2" '
            f'data-nodo="{html.escape(nodo["id"])}" data-turno="{nodo["turno"]}" '
            f'data-aislado="{1 if nodo["aislado"] else 0}">'
            f"<title>{html.escape(nodo['nombre'])} · Turno {nodo['turno']}</title>"
            f"</circle>"
        )
    for arista in escena["aristas"]:
        partes.append(
            f'<text transform="translate({arista["mx"]:.1f},{arista["my"]:.1f}) '
            f'rotate({arista["angulo"]:.1f})" x="0" y="-5" text-anchor="middle" '
            f'font-size="14" font-weight="600" font-family="sans-serif" fill="#1f2933" '
            f'stroke="#f7f8fa" stroke-width="5" paint-order="stroke" stroke-linejoin="round" '
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
    const punto = document.querySelector('[data-nodo="' + id + '"]');
    punto.setAttribute("cx", x.toFixed(1));
    punto.setAttribute("cy", y.toFixed(1));
    punto.setAttribute("fill", color(desde.color, hasta.color, t));
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
    return TAMANO_PUNTO, TAMANO_PUNTO


def _grosor(peso):
    """Grosor en píxeles de pantalla: la arista pesada se distingue de la leve."""
    proporcion = max(0.0, min(1.0, (float(peso) - 15) / 60))
    return 1.4 + proporcion * 2.4


def _clave(grafo, nodo):
    datos = grafo.nodes[nodo]
    anio = datos.get("año", datos.get("anio", 0))
    try:
        anio = int(anio)
    except (TypeError, ValueError):
        pass
    return (str(datos.get("carrera") or ""), anio, str(datos.get("nombre") or nodo))


def _angulos(grafo, nodos):
    """Reparte el círculo por carrera y deja un hueco entre una y otra."""
    if not nodos:
        return {}
    grupos = []
    carrera = None
    for nodo in nodos:
        actual = _clave(grafo, nodo)[0]
        if actual != carrera:
            grupos.append([])
            carrera = actual
        grupos[-1].append(nodo)
    huecos = max(0, len(grupos) - 1)
    pasos = max(1, len(nodos) + huecos)
    angulos = {}
    indice = 0
    for i, grupo in enumerate(grupos):
        for nodo in grupo:
            angulos[nodo] = -math.pi / 2 + 2 * math.pi * indice / pasos
            indice += 1
        if i < len(grupos) - 1:
            indice += 1
    return angulos


def _angulo(x1, y1, x2, y2):
    """Deja el texto de pie: la arista queda debajo del peso, nunca al revés."""
    angulo = math.atan2(y2 - y1, x2 - x1)
    if angulo > math.pi / 2 or angulo < -math.pi / 2:
        angulo += math.pi
    return math.degrees(angulo)


def _geometria(grafo, medidas):
    """Arma un lienzo donde los puntos no se pisan.

    El círculo crece con la cantidad de materias y deja un corredor
    entre vecinos para el peso de la arista.
    """
    conectados = sorted(
        (nodo for nodo in grafo.nodes if grafo.degree(nodo) > 0),
        key=lambda nodo: _clave(grafo, nodo),
    )
    aislados = sorted(
        (nodo for nodo in grafo.nodes if grafo.degree(nodo) == 0),
        key=lambda nodo: _clave(grafo, nodo),
    )
    margen = 36
    angulos = _angulos(grafo, conectados)
    radio = _radio_minimo(conectados, medidas, ESPACIO_PUNTOS, angulos)
    if 2 <= len(conectados) <= 8:
        radio = max(radio, 120)
    extra = 28
    if conectados:
        extra += max(
            math.hypot(medidas[nodo][0] / 2, medidas[nodo][1] / 2) for nodo in conectados
        )
    diametro = 2 * (radio + extra)
    posiciones = {}

    if conectados and aislados:
        ancho_columna = max(medidas[nodo][0] for nodo in aislados)
        alto_columna = sum(medidas[nodo][1] for nodo in aislados) + 22 * (len(aislados) - 1)
        ancho = margen + ancho_columna + 80 + diametro + margen
        alto = max(diametro, alto_columna) + 2 * margen
        centro_x = margen + ancho_columna + 80 + extra + radio
        posiciones.update(_en_circulo(conectados, centro_x, alto / 2, radio, angulos))
        posiciones.update(_columna(aislados, medidas, margen, alto))
    elif conectados:
        ancho = diametro + 2 * margen
        alto = diametro + 2 * margen
        posiciones.update(_en_circulo(conectados, ancho / 2, alto / 2, radio, angulos))
    else:
        ancho, alto = _fila(aislados, medidas, margen, posiciones)

    lado = max(ancho, alto, _lado_maximo(list(grafo.nodes), medidas))
    desplazamiento_x = (lado - ancho) / 2
    desplazamiento_y = (lado - alto) / 2
    if desplazamiento_x or desplazamiento_y:
        posiciones = {
            nodo: (x + desplazamiento_x, y + desplazamiento_y)
            for nodo, (x, y) in posiciones.items()
        }
    return lado, lado, posiciones


def _lado_maximo(nodos, medidas):
    """Lado del lienzo con todas las materias en círculo: no cambia con el umbral."""
    margen = 36
    if not nodos:
        return 960
    radio = _radio_minimo(nodos, medidas, ESPACIO_PUNTOS)
    if 2 <= len(nodos) <= 8:
        radio = max(radio, 120)
    extra = 28 + max(
        math.hypot(medidas[nodo][0] / 2, medidas[nodo][1] / 2) for nodo in nodos
    )
    return 2 * (radio + extra) + 2 * margen


def _radio_minimo(nodos, medidas, espacio, angulos=None):
    """Menor radio cuyo círculo deja `espacio` px libres entre puntos."""
    cantidad = len(nodos)
    if cantidad <= 1:
        return 0.0
    if angulos is None:
        angulos = {
            nodo: -math.pi / 2 + 2 * math.pi * i / cantidad
            for i, nodo in enumerate(nodos)
        }

    def cabe(radio):
        centros = [
            (radio * math.cos(angulos[nodo]), radio * math.sin(angulos[nodo]), nodo)
            for nodo in nodos
        ]
        for i in range(cantidad):
            for j in range(i + 1, cantidad):
                dx = abs(centros[i][0] - centros[j][0])
                dy = abs(centros[i][1] - centros[j][1])
                ancho = (medidas[centros[i][2]][0] + medidas[centros[j][2]][0]) / 2 + espacio
                alto = (medidas[centros[i][2]][1] + medidas[centros[j][2]][1]) / 2 + espacio
                if dx < ancho and dy < alto:
                    return False
        return True

    lo, hi = 0.0, 240.0
    while not cabe(hi):
        hi *= 2
    for _ in range(26):
        medio = (lo + hi) / 2
        if cabe(medio):
            hi = medio
        else:
            lo = medio
    return hi


def _en_circulo(nodos, centro_x, centro_y, radio, angulos):
    if len(nodos) == 1:
        return {nodos[0]: (centro_x, centro_y)}
    return {
        nodo: (
            centro_x + radio * math.cos(angulos[nodo]),
            centro_y + radio * math.sin(angulos[nodo]),
        )
        for nodo in nodos
    }


def _acomodar_pesos(aristas):
    """Guarda el punto medio: el visor lo usa cuando el mouse está sobre la arista."""
    for arista in aristas:
        arista["mx"] = (arista["x1"] + arista["x2"]) / 2
        arista["my"] = (arista["y1"] + arista["y2"]) / 2


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


def _fila(nodos, medidas, margen, posiciones):
    """Centra en una fila el caso en que todas las materias están aisladas."""
    separacion = 26
    if not nodos:
        return 960, 540
    total = sum(medidas[nodo][0] for nodo in nodos) + separacion * (len(nodos) - 1)
    ancho = total + 2 * margen
    alto = TAMANO_PUNTO + 2 * margen + 28
    cursor = margen
    for nodo in nodos:
        ancho_nodo = medidas[nodo][0]
        posiciones[nodo] = (cursor + ancho_nodo / 2, alto / 2)
        cursor += ancho_nodo + separacion
    return ancho, alto
