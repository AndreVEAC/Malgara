from funciones_mapas import final_noche_1 as final_noche

CONTROL_CINEMATICO = False

import importlib.util
import pygame
from reloj_juego import ahora_ms

import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_audio
import sistema_guardado

from configuracion import TAMANO_CASILLA


CENTRAR_FONDO = True
PANTALLA_NEGRA = True

MARCA = "habitaciones_noche_1:inicio_completado"

estado_escena = "INICIO"
ultimo_paso = 0
PASO_MS = 200

sonido_alarma = None
sonido_abrir = None
sonido_cerrar = None

canal_alarma = None
canal_puerta = None

salida_disponible = False


def iniciar():
    global PANTALLA_NEGRA, estado_escena
    global sonido_alarma, sonido_abrir, sonido_cerrar
    global canal_alarma, canal_puerta
    global ultimo_paso, salida_disponible
    global CONTROL_CINEMATICO

    CONTROL_CINEMATICO = False
    if final_noche.iniciar_habitaciones():
        PANTALLA_NEGRA = False
        CONTROL_CINEMATICO = final_noche.en_curso
        estado_escena = "FINAL_NOCHE" if CONTROL_CINEMATICO else "JUGABLE"
        _habilitar_salida()
        return

    dialogo.cargar_json(
        "datos/habitaciones_noche_1.json"
    )

    ultimo_paso = 0
    salida_disponible = False

    if canal_alarma is not None:
        canal_alarma.stop()

    canal_alarma = None
    canal_puerta = None

    sistema_audio.detener_musica(fade_ms=0)

    lucas = mapa.npcs_activos["lucas"]
    lucas["comportamiento"] = "estatico"
    lucas["sprite_override"] = None

    # Volver a la habitación o cargar una partida
    # no repite la alarma ni la conversación.
    if MARCA in mapa.eventos_completados:
        PANTALLA_NEGRA = False
        lucas["visible"] = False

        mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"

        _habilitar_salida()

        # Al regresar desde hogar, cerrar la puerta.
        if (
            not sistema_guardado.cargando
            and (mapa.mateo_x, mapa.mateo_y) == (2, 3)
        ):
            sonido = _cargar_sonido("close_door.wav")
            if sonido is not None:
                sonido.play()

        return

    PANTALLA_NEGRA = True
    mapa.jugador_bloqueado = True

    mapa.mateo_x = 1
    mapa.mateo_y = 3
    mapa.mateo_px_x = float(1 * TAMANO_CASILLA)
    mapa.mateo_px_y = float(3 * TAMANO_CASILLA)
    mapa.direccion_mateo = "der"

    lucas.update({
        "x": 3,
        "y": 3,
        "px_x": float(3 *TAMANO_CASILLA),
        "px_y": float(3 * TAMANO_CASILLA),
        "direccion": "izq",
        "visible": True,
    })

    sonido_alarma = _cargar_sonido("alarma.wav")
    sonido_abrir = _cargar_sonido("open_door.wav")
    sonido_cerrar = _cargar_sonido("close_door.wav")

    if sonido_alarma is not None:
        canal_alarma = sonido_alarma.play()

    estado_escena = "ALARMA"


def actualizar():
    global PANTALLA_NEGRA, estado_escena
    global canal_puerta, CONTROL_CINEMATICO

    if estado_escena == "FINAL_NOCHE":
        final_noche.actualizar()
        CONTROL_CINEMATICO = final_noche.en_curso
        if not CONTROL_CINEMATICO:
            estado_escena = "JUGABLE"
        return

    if estado_escena == "JUGABLE":
        # Permite habilitarla cuando añadamos hogar_noche_1.
        if not salida_disponible:
            _habilitar_salida()
        return

    if estado_escena == "ALARMA":
        if (
            canal_alarma is not None
            and canal_alarma.get_busy()
        ):
            return

        # Esperar también al fundido del mapa anterior.
        # Mientras tanto, el escenario sigue siendo negro.
        if mapa.transicion_activa:
            return

        # Ahora sí revelar la habitación.
        PANTALLA_NEGRA = False
        mapa.alpha_transicion = 255
        mapa.tipo_transicion = "fade_in"
        mapa.transicion_activa = True

        estado_escena = "REVELANDO"
        return

    if mapa.transicion_activa:
        return

    if estado_escena == "REVELANDO":
        dialogo.iniciar_dialogo(
            "evento_noche1_inicio"
        )

        if dialogo.obtener_evento_activo() is None:
            raise ValueError(
                "Falta evento_noche1_inicio "
                "en datos/habitaciones_noche_1.json"
            )

        estado_escena = "CONVERSACION"

    elif estado_escena == "CONVERSACION":
        if dialogo.obtener_evento_activo() is not None:
            return

        estado_escena = "HACIA_PUERTA"

    elif estado_escena == "HACIA_PUERTA":
        # Lucas se coloca en el pasillo central.
        if _caminar_lucas((2, 3)):
            mapa.npcs_activos["lucas"]["direccion"] = "abajo"

            if sonido_abrir is not None:
                canal_puerta = sonido_abrir.play()

            estado_escena = "CRUZANDO"

    elif estado_escena == "CRUZANDO":
        # Paso guionizado hacia la puerta inferior.
        if _caminar_lucas((2, 4)):
            mapa.npcs_activos["lucas"]["visible"] = False

            if sonido_cerrar is not None:
                if canal_puerta is not None:
                    if canal_puerta.get_busy():
                        canal_puerta.queue(sonido_cerrar)
                    else:
                        canal_puerta.play(sonido_cerrar)
                else:
                    canal_puerta = sonido_cerrar.play()

            estado_escena = "CERRANDO"

    elif estado_escena == "CERRANDO":
        # Esperar al cierre antes de permitir otra
        # interacción con la puerta.
        if (
            canal_puerta is not None
            and canal_puerta.get_busy()
        ):
            return

        mapa.eventos_completados.add(MARCA)
        _habilitar_salida()

        mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"


def _caminar_lucas(destino):
    global ultimo_paso

    lucas = mapa.npcs_activos["lucas"]

    objetivo_x = lucas["x"] * TAMANO_CASILLA
    objetivo_y = lucas["y"] * TAMANO_CASILLA

    # Esperar a que el movimiento visual termine.
    if (
        abs(lucas["px_x"] - objetivo_x) >= 0.5
        or abs(lucas["px_y"] - objetivo_y) >= 0.5
    ):
        return False

    if (lucas["x"], lucas["y"]) == destino:
        return True

    ahora = ahora_ms()

    if ahora - ultimo_paso < PASO_MS:
        return False

    dx = destino[0] - lucas["x"]
    dy = destino[1] - lucas["y"]

    # Ruta corta y controlada: (1,3) -> (2,3) -> (2,4).
    if dx:
        lucas["x"] += 1 if dx > 0 else -1
        lucas["direccion"] = "der" if dx > 0 else "izq"
    elif dy:
        lucas["y"] += 1 if dy > 0 else -1
        lucas["direccion"] = "abajo" if dy > 0 else "arriba"

    ultimo_paso = ahora
    return False


def _habilitar_salida():
    global salida_disponible

    # Evita un cierre del juego mientras el siguiente
    # mapa todavía no existe.
    salida_disponible = (
        importlib.util.find_spec("mapas.hogar_noche_1")
        is not None
    )

    mapa.matriz_activa[4][2] = (
        99 if salida_disponible else 1
    )


def _cargar_sonido(nombre):
    ruta = f"recursos/sonidos/efectos/{nombre}"

    try:
        return pygame.mixer.Sound(ruta)
    except (pygame.error, FileNotFoundError) as error:
        print(f"[Habitaciones noche] {ruta}: {error}")
        return None