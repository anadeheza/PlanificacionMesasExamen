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


def _geometria(grafo, medidas):
    """Arma un lienzo donde los rectángulos no se pisan.

    El círculo crece con la cantidad de materias y deja un corredor
    entre vecinos para el peso de la arista.
    """
    conectados = sorted(nodo for nodo in grafo.nodes if grafo.degree(nodo) > 0)
    aislados = sorted(nodo for nodo in grafo.nodes if grafo.degree(nodo) == 0)
    margen = 36
    radio = _radio_minimo(conectados, medidas, 108)
    if 2 <= len(conectados) <= 8:
        radio = max(radio, 210)
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
        posiciones.update(_en_circulo(conectados, centro_x, alto / 2, radio))
        posiciones.update(_columna(aislados, medidas, margen, alto))
    elif conectados:
        ancho = diametro + 2 * margen
        alto = diametro + 2 * margen
        posiciones.update(_en_circulo(conectados, ancho / 2, alto / 2, radio))
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
    radio = _radio_minimo(nodos, medidas, 108)
    if 2 <= len(nodos) <= 8:
        radio = max(radio, 210)
    extra = 28 + max(
        math.hypot(medidas[nodo][0] / 2, medidas[nodo][1] / 2) for nodo in nodos
    )
    return 2 * (radio + extra) + 2 * margen


def _radio_minimo(nodos, medidas, espacio):
    """Menor radio cuyo círculo deja `espacio` px libres entre rectángulos."""
    cantidad = len(nodos)
    if cantidad <= 1:
        return 0.0
    delta = 2 * math.pi / cantidad

    def cabe(radio):
        centros = []
        for i, nodo in enumerate(nodos):
            angulo = -math.pi / 2 + delta * i
            centros.append((radio * math.cos(angulo), radio * math.sin(angulo), nodo))
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


def _en_circulo(nodos, centro_x, centro_y, radio):
    posiciones = {}
    cantidad = len(nodos)
    for i, nodo in enumerate(nodos):
        if cantidad == 1:
            posiciones[nodo] = (centro_x, centro_y)
            continue
        angulo = -math.pi / 2 + 2 * math.pi * i / cantidad
        posiciones[nodo] = (
            centro_x + radio * math.cos(angulo),
            centro_y + radio * math.sin(angulo),
        )
    return posiciones


def _distancia_hasta_borde(ancho, alto, ux, uy):
    if abs(ux) < 1e-9:
        return (alto / 2) / abs(uy)
    if abs(uy) < 1e-9:
        return (ancho / 2) / abs(ux)
    return min((ancho / 2) / abs(ux), (alto / 2) / abs(uy))


def _acomodar_pesos(aristas):
    """Apoya cada peso justo afuera de una materia, escalonado si no entra."""
    visibles = [arista for arista in aristas if arista["opacidad"] >= 0.5]
    for arista in aristas:
        if arista["opacidad"] < 0.5:
            arista["mx"] = (arista["x1"] + arista["x2"]) / 2
            arista["my"] = (arista["y1"] + arista["y2"]) / 2
    if not visibles:
        return

    carga = {}
    grupos = {}
    for arista in visibles:
        clave_a = (round(arista["x1"], 1), round(arista["y1"], 1))
        clave_b = (round(arista["x2"], 1), round(arista["y2"], 1))
        carga.setdefault(clave_a, 0)
        carga.setdefault(clave_b, 0)
        if carga[clave_a] <= carga[clave_b]:
            dueno = clave_a
            carga[clave_a] += 1
        else:
            dueno = clave_b
            carga[clave_b] += 1
        grupos.setdefault(dueno, []).append(arista)

    for dueno, grupo in grupos.items():
        def direccion(arista, ancla=dueno):
            if (round(arista["x1"], 1), round(arista["y1"], 1)) == ancla:
                return math.atan2(arista["y2"] - arista["y1"], arista["x2"] - arista["x1"])
            return math.atan2(arista["y1"] - arista["y2"], arista["x1"] - arista["x2"])

        grupo.sort(key=direccion)
        puestos = []
        for arista in grupo:
            desde_origen = (round(arista["x1"], 1), round(arista["y1"], 1)) == dueno
            if desde_origen:
                cx, cy = arista["x1"], arista["y1"]
                ancho_nodo, alto_nodo = arista["w1"], arista["h1"]
                dx, dy = arista["x2"] - arista["x1"], arista["y2"] - arista["y1"]
            else:
                cx, cy = arista["x2"], arista["y2"]
                ancho_nodo, alto_nodo = arista["w2"], arista["h2"]
                dx, dy = arista["x1"] - arista["x2"], arista["y1"] - arista["y2"]
            largo = math.hypot(dx, dy) or 1
            ux, uy = dx / largo, dy / largo
            salida = _distancia_hasta_borde(ancho_nodo, alto_nodo, ux, uy)
            avance = 30
            tope = max(avance, largo * 0.62)
            x = cx + ux * (salida + avance)
            y = cy + uy * (salida + avance)
            while avance < tope and any(math.hypot(x - px, y - py) < 44 for px, py in puestos):
                avance += 36
                x = cx + ux * (salida + avance)
                y = cy + uy * (salida + avance)
            arista["mx"] = x
            arista["my"] = y
            puestos.append((x, y))


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
    alto = ALTO_NODO + 2 * margen + 28
    cursor = margen
    for nodo in nodos:
        ancho_nodo = medidas[nodo][0]
        posiciones[nodo] = (cursor + ancho_nodo / 2, alto / 2)
        cursor += ancho_nodo + separacion
    return ancho, alto
