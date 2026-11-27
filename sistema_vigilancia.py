from collections import deque

import pygame
import sistema_audio as audio
import sistema_escondites as escondites
import sistema_dialogo as dialogo

from configuracion import TAMANO_CASILLA as T


persecucion_activa = False
_luces = {}


def configurar():
    """Preparar los vigilantes al cargar un mapa."""
    import sistema_mapa as mapa

    global persecucion_activa
    persecucion_activa = False
    if not mapa.control_cinematico:
        audio.establecer_persecucion(False)
    for npc in mapa.npcs_activos.values():
        if npc.get("comportamiento") == "vigilante":
            npc["congelado"] = False
            npc["_vigilancia"] = {
                "estado": "NORMAL",
                "origen": (npc["x"], npc["y"]),
                "direccion": npc["direccion"],
                "hasta": 0,
                "ultimo_paso": pygame.time.get_ticks(),
                "indice": 0,
            }

        ruta = npc.get("vigilancia", {}).get("luz")

        if ruta and ruta not in _luces:
            original = pygame.image.load(ruta).convert_alpha()
            original = pygame.transform.scale(
                original, (3 * T, 3 * T)
            )

            # La imagen original apunta hacia arriba.
            _luces[ruta] = {
                direccion: pygame.transform.rotate(original, angulo)
                for direccion, angulo in (
                    ("arriba", 0),
                    ("izq", 90),
                    ("abajo", 180),
                    ("der", -90),
                )
            }


def _vigilantes(mapa):
    return [
        npc
        for npc in mapa.npcs_activos.values()
        if npc.get("comportamiento") == "vigilante"
        and npc.get("visible", True)
        and not npc.get("pausado", False)
    ]


def _linea_libre(mapa, inicio, destino):
    """Comprobar obstáculos entre dos casillas, incluidas esquinas."""
    x, y = inicio
    dx, dy = destino[0] - x, destino[1] - y

    ax, ay = abs(dx), abs(dy)
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1

    ix = iy = 0

    while ix < ax or iy < ay:
        comparacion = (
            (1 + 2 * ix) * ay
            - (1 + 2 * iy) * ax
        )

        if comparacion == 0:
            if (
                mapa.casilla_bloqueada(x + sx, y)
                or mapa.casilla_bloqueada(x, y + sy)
            ):
                return False

            x, y = x + sx, y + sy
            ix, iy = ix + 1, iy + 1

        elif comparacion < 0:
            x += sx
            ix += 1

        else:
            y += sy
            iy += 1

        if mapa.casilla_bloqueada(x, y):
            return False

    return True


def _ve_jugador(mapa, npc):
    dx = mapa.mateo_x - npc["x"]
    dy = mapa.mateo_y - npc["y"]

    # Las ocho casillas pegadas al vigilante.
    cercano = max(abs(dx), abs(dy)) <= 1

    ux, uy = {
        "arriba": (0, -1),
        "abajo": (0, 1),
        "izq": (-1, 0),
        "der": (1, 0),
    }[npc["direccion"]]

    delante = dx * ux + dy * uy
    lateral = dx * (-uy) + dy * ux

    # Rectángulo frontal: tres casillas de largo y tres de ancho.
    frontal = 1 <= delante <= 3 and abs(lateral) <= 1

    return (cercano or frontal) and _linea_libre(
        mapa,
        (npc["x"], npc["y"]),
        (mapa.mateo_x, mapa.mateo_y),
    )


def _en_luz(mapa):
    obtener = getattr(
        mapa.script_nivel_actual,
        "obtener_zonas_iluminadas",
        None,
    )

    if not callable(obtener):
        return False

    # Comprobar los pies de Mateo contra las luces del escenario.
    pies = (
        mapa.mateo_px_x + T / 2,
        mapa.mateo_px_y + T - 2,
    )

    return any(
        rect.collidepoint(pies)
        for rect in obtener()
    )


def _primer_paso(mapa, npc, destino):
    """Buscar un camino sin atravesar obstáculos ni portales."""
    inicio = (npc["x"], npc["y"])

    ocupadas = {
        (otro["x"], otro["y"])
        for otro in mapa.npcs_activos.values()
        if otro is not npc
        and otro.get("visible", True)
        and otro.get("comportamiento") != "sigue_jugador"
    }

    pendientes = deque([(inicio, None)])
    visitadas = {inicio}

    while pendientes:
        (x, y), primero = pendientes.popleft()

        if (x, y) == destino:
            return primero

        vecinos = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        vecinos.sort(
            key=lambda p: (
                abs(p[0] - destino[0])
                + abs(p[1] - destino[1])
            )
        )

        for nx, ny in vecinos:
            posicion = (nx, ny)

            if posicion in visitadas:
                continue

            visitadas.add(posicion)

            if (
                posicion in ocupadas
                or mapa.casilla_bloqueada(nx, ny)
            ):
                continue

            if mapa.matriz_activa[ny][nx] in mapa.portales_activos:
                continue

            pendientes.append((
                posicion,
                posicion if primero is None else primero,
            ))

    return None


def _mover(mapa, npc, destino, ahora, intervalo):
    datos = npc["_vigilancia"]

    if ahora - datos["ultimo_paso"] <= intervalo:
        return

    datos["ultimo_paso"] = ahora
    paso = _primer_paso(mapa, npc, destino)

    if paso is None:
        return

    dx = paso[0] - npc["x"]
    dy = paso[1] - npc["y"]

    if dx:
        npc["direccion"] = "der" if dx > 0 else "izq"
    else:
        npc["direccion"] = "abajo" if dy > 0 else "arriba"

    npc["x"], npc["y"] = paso


def _ha_llegado(npc, destino):
    return (
        (npc["x"], npc["y"]) == destino
        and abs(npc["px_x"] - destino[0] * T) < 1
        and abs(npc["px_y"] - destino[1] * T) < 1
    )

def _actualizar_mirada(npc, ahora):
    datos = npc["_vigilancia"]
    config = npc.get("vigilancia", {})
    miradas = config.get("miradas", [])

    # Los giros periódicos solo funcionan estando quieto.
    if (
        datos["estado"] != "NORMAL"
        or config.get("ruta")
        or not miradas
    ):
        datos.pop("mirada_hasta", None)
        return

    if "mirada_hasta" not in datos:
        datos["indice_mirada"] = 0

    elif ahora >= datos["mirada_hasta"]:
        datos["indice_mirada"] = (
            datos["indice_mirada"] + 1
        ) % len(miradas)

    else:
        return

    direccion, duracion = miradas[datos["indice_mirada"]]

    npc["direccion"] = direccion
    datos["mirada_hasta"] = ahora + max(1, duracion)


def _mirar_a_mateo(mapa, npc):
    dx = mapa.mateo_x - npc["x"]
    dy = mapa.mateo_y - npc["y"]

    if abs(dx) >= abs(dy) and dx:
        npc["direccion"] = "der" if dx > 0 else "izq"

    elif dy:
        npc["direccion"] = "abajo" if dy > 0 else "arriba"

def actualizar(ahora):
    import sistema_mapa as mapa

    global persecucion_activa

    # Durante la cinemática, el director controla al loco.
    if mapa.control_cinematico or getattr(
        mapa.script_nivel_actual,
        "CONTROL_CINEMATICO",
        False,
    ):
        persecucion_activa = False
        return

    guardias = _vigilantes(mapa)

    # Esconderse bloquea al jugador, pero NO pausa a los vigilantes.
    if (
        mapa.transicion_activa
        or dialogo.obtener_evento_activo() is not None
        or (
            mapa.jugador_bloqueado
            and not escondites.escondido
        )
    ):
        for npc in guardias:
            npc["congelado"] = True
        return

    luz = not escondites.escondido and _en_luz(mapa)

    for npc in guardias:
        datos = npc["_vigilancia"]
        npc["congelado"] = False

        # Girar periódicamente si está quieto y sin perseguir.
        _actualizar_mirada(npc, ahora)

        # Resolver primero la espera junto al barril.
        if datos["estado"] == "ESPERANDO":
            if ahora >= datos["hasta"]:
                datos["estado"] = "REGRESANDO"
                datos["ultimo_paso"] = ahora

            elif not escondites.escondido:
                # Saliste antes de tiempo: sigue recordando dónde estás.
                datos["estado"] = "PERSIGUIENDO"

            else:
                # Conservar posición visual y orientación.
                npc["congelado"] = True
                continue

        # Detectar también mientras regresa o patrulla.
        # La luz alerta a todos, independientemente de su orientación.
        if (
            not escondites.escondido
            and (luz or _ve_jugador(mapa, npc))
        ):
            if luz and datos["estado"] != "PERSIGUIENDO":
                # Simular que justo voltea y descubre a Mateo.
                _mirar_a_mateo(mapa, npc)

            datos["estado"] = "PERSIGUIENDO"

        if datos["estado"] == "PERSIGUIENDO":
            if escondites.escondido:
                datos["estado"] = "ESPERANDO"
                datos["hasta"] = ahora + 5000
                npc["congelado"] = True
                continue

            # Solo Mateo puede ser capturado.
            distancia2 = (
                (npc["px_x"] - mapa.mateo_px_x) ** 2
                + (npc["px_y"] - mapa.mateo_px_y) ** 2
            )

            if distancia2 <= (T * 0.3) ** 2:
                mapa.jugador_bloqueado = True

                # Restaurar el mapa en su punto de entrada con un fundido.
                mapa.cargar_nivel(mapa.nombre_mapa_actual, *(mapa.reinicio_entrada or (None, None)))

                persecucion_activa = False
                audio.establecer_persecucion(False)

                for otro in guardias:
                    otro["congelado"] = True

                return

            _mover(
                mapa,
                npc,
                (mapa.mateo_x, mapa.mateo_y),
                ahora,
                max(1, mapa.RETRASO_MATEO // 2),
            )

        elif datos["estado"] == "REGRESANDO":
            if _ha_llegado(npc, datos["origen"]):
                datos["estado"] = "NORMAL"
                datos["indice"] = 0
                npc["direccion"] = datos["direccion"]

            else:
                _mover(
                    mapa,
                    npc,
                    datos["origen"],
                    ahora,
                    mapa.RETRASO_MATEO,
                )

        else:
            ruta = npc.get("vigilancia", {}).get("ruta", [])

            if ruta:
                destino = tuple(ruta[datos["indice"]])

                if _ha_llegado(npc, destino):
                    datos["indice"] = (
                        datos["indice"] + 1
                    ) % len(ruta)

                else:
                    _mover(
                        mapa,
                        npc,
                        destino,
                        ahora,
                        mapa.RETRASO_MATEO,
                    )

    # Mantener la persecución mientras quede alguien persiguiendo
    # o esperando junto al barril.
    # Lucas también usa esta variable para correr.
    persecucion_activa = any(
        npc["_vigilancia"]["estado"]
        in ("PERSIGUIENDO", "ESPERANDO")
        for npc in guardias
    )

    audio.establecer_persecucion(persecucion_activa)


def _ocultar_luz_en_copas(capa_luces, mapa, camara_x, camara_y):
    # Reutilizar la máscara para los árboles que comparten imagen
    # durante este dibujado.
    mascaras = {}
    ventana = capa_luces.get_rect()

    for fila, casillas in enumerate(mapa.matriz_activa):
        for col, numero in enumerate(casillas):
            # El objeto 21 es el árbol grande.
            if numero != 21:
                continue

            objeto = mapa.imagenes_objetos.get(numero)

            if objeto is None:
                continue

            imagen = objeto["img"]

            # Misma colocación que utiliza el render del escenario.
            if objeto.get("profundidad", False):
                base_y = (fila + 1) * T
                centro_x = (col + 0.5) * T

                x = int(centro_x - imagen.get_width() / 2)
                y = int(base_y - imagen.get_height())
            else:
                x = col * T
                y = fila * T

            x = round(x - camara_x)
            y = round(y - camara_y)

            # Solo la franja superior de una casilla de alto.
            alto_copa = min(T, imagen.get_height())

            rect_copa = pygame.Rect(
                x,
                y,
                imagen.get_width(),
                alto_copa,
            )

            if not rect_copa.colliderect(ventana):
                continue

            clave = id(imagen)

            if clave not in mascaras:
                copa = imagen.subsurface(
                    (0, 0, imagen.get_width(), alto_copa)
                ).copy()

                # Conservar únicamente la transparencia del árbol.
                copa.fill(
                    (0, 0, 0, 255),
                    special_flags=pygame.BLEND_RGBA_MULT,
                )

                # Invertir su transparencia:
                # árbol opaco -> borrar luz;
                # árbol transparente -> conservar luz.
                mascara = pygame.Surface(
                    copa.get_size(),
                    pygame.SRCALPHA,
                )
                mascara.fill((255, 255, 255, 255))
                mascara.blit(
                    copa,
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_SUB,
                )

                mascaras[clave] = mascara

            capa_luces.blit(
                mascaras[clave],
                (x, y),
                special_flags=pygame.BLEND_RGBA_MULT,
            )


def dibujar_linternas(pantalla, camara_x, camara_y):
    import sistema_mapa as mapa

    # Dibujar las linternas separadas del escenario para poder
    # recortarlas sin borrar personajes ni otros elementos.
    capa_luces = pygame.Surface(
        pantalla.get_size(),
        pygame.SRCALPHA,
    )

    for npc in mapa.npcs_activos.values():
        if not npc.get("visible", True):
            continue

        config = npc.get("vigilancia", {})
        imagenes = _luces.get(config.get("luz"))

        if not imagenes:
            continue

        direccion = npc["direccion"]
        imagen = imagenes[direccion]

        ajustes = config.get("anclajes_luz", {
            "arriba": (26, 18),
            "abajo": (7, 25),
            "izq": (3, 23),
            "der": (29, 23),
        })

        ax, ay = ajustes[direccion]

        punto = (
            round(npc["px_x"] + ax - camara_x),
            round(npc["px_y"] + ay - camara_y),
        )

        rect = imagen.get_rect()

        ancla = {
            "arriba": "midbottom",
            "abajo": "midtop",
            "izq": "midright",
            "der": "midleft",
        }[direccion]

        setattr(rect, ancla, punto)
        capa_luces.blit(imagen, rect)

    # Recortar únicamente donde está la copa superior.
    _ocultar_luz_en_copas(
        capa_luces,
        mapa,
        camara_x,
        camara_y,
    )

    recortar = getattr(mapa.script_nivel_actual, "recortar_linternas", None)
    if callable(recortar):
        recortar(capa_luces, camara_x, camara_y)

    pantalla.blit(capa_luces, (0, 0))
