from collections import deque

import pygame
import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_guardado

from configuracion import TAMANO_CASILLA
from mapas import hogar


CENTRAR_FONDO = True

MARCA = "hogar:cinematica_completada"
PASO_MS = 180

estado_escena = "INICIO"
ultimo_paso = {}
espera_hasta = 0

sonido_puerta = None
sonido_cerrar_puerta = None
canal_puerta = None


def iniciar():
    global estado_escena, espera_hasta
    global sonido_puerta, sonido_cerrar_puerta, canal_puerta

    dialogo.cargar_json("datos/hogar.json")
    ultimo_paso.clear()

    sonido_puerta = None
    sonido_cerrar_puerta = None
    canal_puerta = None

    lucas = mapa.npcs_activos["lucas"]
    lucas["comportamiento"] = "estatico"
    lucas["sprite_override"] = None

    # Al regresar, la cinemática no se repite.
    if MARCA in mapa.eventos_completados:
        lucas["visible"] = False
        _habilitar_habitacion()

        # Regreso desde la puerta de habitaciones.
        if (
            not sistema_guardado.cargando
            and (mapa.mateo_x, mapa.mateo_y) == (1, 2)
        ):
            sonido_cerrar_puerta = _cargar_sonido(
                "recursos/sonidos/efectos/close_door.wav"
            )

            if sonido_cerrar_puerta is not None:
                sonido_cerrar_puerta.play()

            mapa.direccion_mateo = "abajo"

        mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"
        return

    mapa.jugador_bloqueado = True

    _colocar("mateo", (8, 6), "izq")
    _colocar("lucas", (7, 6), "izq")

    lucas["visible"] = True

    sonido_puerta = _cargar_sonido(
        "recursos/sonidos/efectos/open_door.wav"
    )
    sonido_cerrar_puerta = _cargar_sonido(
        "recursos/sonidos/efectos/close_door.wav"
    )

    estado_escena = "ENTRADA"
    espera_hasta = pygame.time.get_ticks() + 400


def actualizar():
    global estado_escena, canal_puerta

    if estado_escena == "JUGABLE":
        return

    # Esperar a que termine el fundido de entrada.
    if mapa.transicion_activa:
        return

    # Los movimientos continúan cuando se cierra el diálogo.
    if dialogo.obtener_evento_activo() is not None:
        return

    ahora = pygame.time.get_ticks()

    if ahora < espera_hasta:
        return

    if estado_escena == "ENTRADA":
        if _mover_grupo(hogar.DESTINO_SOFA, ahora):
            _mirar("lucas", "der")
            _mirar("mateo", "izq")

            _dialogo(
                "hogar_charla_sofa",
                "CHARLA_SOFA"
            )

    elif estado_escena == "CHARLA_SOFA":
        estado_escena = "A_LA_MESA"

    elif estado_escena == "A_LA_MESA":
        if _mover_grupo(
            hogar.ASIENTOS,
            ahora,
            permitir_destino=True
        ):
            # Simular que están sentados mirando la mesa.
            _mirar("mateo", "der")
            _mirar("lucas", "izq")

            _dialogo(
                "hogar_charla_mesa",
                "CHARLA_MESA"
            )

    elif estado_escena == "CHARLA_MESA":
        estado_escena = "DESPEDIDA"

    elif estado_escena == "DESPEDIDA":
        destinos = {
            "mateo": (5, 4),
            "lucas": (1, 2),
        }

        # Mateo se aparta de su silla.
        # Lucas camina hasta delante de la habitación.
        if _mover_grupo(destinos, ahora):
            _mirar("mateo", "arriba")
            _mirar("lucas", "arriba")

            if sonido_puerta is not None:
                canal_puerta = sonido_puerta.play()

            estado_escena = "CRUZAR_PUERTA"

    elif estado_escena == "CRUZAR_PUERTA":
        if _avanzar(
            "lucas",
            hogar.PUERTA_HABITACION,
            ahora,
            permitir_destino=True
        ):
            lucas = mapa.npcs_activos["lucas"]
            lucas["visible"] = False

            # Cerrar después de desaparecer.
            # Si abrir sigue sonando, esperar a que termine.
            if sonido_cerrar_puerta is not None:
                if canal_puerta is not None:
                    if canal_puerta.get_busy():
                        canal_puerta.queue(
                            sonido_cerrar_puerta
                        )
                    else:
                        canal_puerta.play(
                            sonido_cerrar_puerta
                        )
                else:
                    sonido_cerrar_puerta.play()

            mapa.eventos_completados.add(MARCA)
            mapa.jugador_bloqueado = False

            estado_escena = "JUGABLE"


def _cargar_sonido(ruta):
    try:
        return pygame.mixer.Sound(ruta)
    except (pygame.error, FileNotFoundError) as error:
        print(
            f"[Hogar] No se pudo cargar '{ruta}': {error}"
        )
        return None


def _dialogo(evento, siguiente_estado):
    global estado_escena

    dialogo.iniciar_dialogo(evento)

    if dialogo.obtener_evento_activo() is None:
        raise ValueError(
            f"Falta el diálogo '{evento}' "
            "en datos/hogar.json"
        )

    estado_escena = siguiente_estado


def _posicion(nombre):
    if nombre == "mateo":
        return mapa.mateo_x, mapa.mateo_y

    npc = mapa.npcs_activos[nombre]
    return npc["x"], npc["y"]


def _mirar(nombre, direccion):
    if nombre == "mateo":
        mapa.direccion_mateo = direccion
    else:
        mapa.npcs_activos[nombre]["direccion"] = direccion


def _colocar(nombre, posicion, direccion):
    x, y = posicion

    if nombre == "mateo":
        mapa.mateo_x = x
        mapa.mateo_y = y

        mapa.mateo_px_x = float(x * TAMANO_CASILLA)
        mapa.mateo_px_y = float(y * TAMANO_CASILLA)

    else:
        npc = mapa.npcs_activos[nombre]

        npc["x"] = x
        npc["y"] = y
        npc["px_x"] = float(x * TAMANO_CASILLA)
        npc["px_y"] = float(y * TAMANO_CASILLA)

    _mirar(nombre, direccion)


def _quieto(nombre):
    x, y = _posicion(nombre)

    if nombre == "mateo":
        px = mapa.mateo_px_x
        py = mapa.mateo_px_y

    else:
        npc = mapa.npcs_activos[nombre]
        px = npc["px_x"]
        py = npc["px_y"]

    return (
        abs(px - x * TAMANO_CASILLA) < 0.5
        and abs(py - y * TAMANO_CASILLA) < 0.5
    )


def _mover_grupo(
    destinos,
    ahora,
    permitir_destino=False
):
    resultados = []

    # Actualizar a todos antes de comprobar si llegaron.
    for nombre, destino in destinos.items():
        llego = _avanzar(
            nombre,
            destino,
            ahora,
            permitir_destino
        )
        resultados.append(llego)

    return all(resultados)


def _avanzar(
    nombre,
    destino,
    ahora,
    permitir_destino=False
):
    origen = _posicion(nombre)

    # Esperar a que termine visualmente el paso anterior.
    if not _quieto(nombre):
        return False

    if origen == destino:
        return True

    if ahora - ultimo_paso.get(nombre, 0) < PASO_MS:
        return False

    ocupadas = set()

    actores = [
        (
            "mateo",
            mapa.mateo_x,
            mapa.mateo_y,
            mapa.mateo_px_x,
            mapa.mateo_px_y,
        )
    ]

    for npc_nombre, npc in mapa.npcs_activos.items():
        if npc["visible"]:
            actores.append(
                (
                    npc_nombre,
                    npc["x"],
                    npc["y"],
                    npc["px_x"],
                    npc["px_y"],
                )
            )

    for otro, x, y, px, py in actores:
        if otro == nombre:
            continue

        # Reservar la casilla lógica y la posición visual.
        ocupadas.add((x, y))
        ocupadas.add(
            (
                round(px / TAMANO_CASILLA),
                round(py / TAMANO_CASILLA),
            )
        )

    paso = _buscar_paso(
        origen,
        destino,
        ocupadas,
        permitir_destino
    )

    if paso is None:
        return False

    dx = paso[0] - origen[0]
    dy = paso[1] - origen[1]

    if dx > 0:
        direccion = "der"
    elif dx < 0:
        direccion = "izq"
    elif dy > 0:
        direccion = "abajo"
    else:
        direccion = "arriba"

    _mirar(nombre, direccion)

    if nombre == "mateo":
        mapa.mateo_x, mapa.mateo_y = paso
    else:
        npc = mapa.npcs_activos[nombre]
        npc["x"], npc["y"] = paso

    # El motor interpola los píxeles hacia esta casilla.
    ultimo_paso[nombre] = ahora

    return False


def _buscar_paso(
    origen,
    destino,
    ocupadas,
    permitir_destino
):
    if origen == destino:
        return None

    pendientes = deque([origen])
    padres = {origen: None}

    while pendientes:
        actual = pendientes.popleft()

        if actual == destino:
            # Reconstruir hasta obtener el primer paso.
            while padres[actual] != origen:
                actual = padres[actual]

            return actual

        x, y = actual

        for dx, dy in (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
        ):
            nx = x + dx
            ny = y + dy
            posicion = (nx, ny)

            # Comprobar los límites antes de leer la matriz.
            if not (
                0 <= ny < len(mapa.matriz_activa)
                and 0 <= nx < len(mapa.matriz_activa[ny])
            ):
                continue

            if posicion in padres:
                continue

            if posicion in ocupadas:
                continue

            destino_autorizado = (
                permitir_destino
                and posicion == destino
            )

            # Las sillas y la puerta solo se pueden ocupar
            # si son el destino autorizado de la cinemática.
            if (
                mapa.casilla_bloqueada(nx, ny)
                and not destino_autorizado
            ):
                continue

            padres[posicion] = actual
            pendientes.append(posicion)

    return None

def _habilitar_habitacion():
    x, y = hogar.PUERTA_HABITACION
    mapa.matriz_activa[y][x] = 97
    
def al_elegir_opcion(nombre_evento):
    if nombre_evento != "hogar_libreta":
        return

    if estado_escena != "JUGABLE":
        return

    eleccion = dialogo.opciones_actuales[
        dialogo.opcion_seleccionada
    ]

    if eleccion.get("accion") == "guardar_partida":
        sistema_guardado.solicitar("manual")