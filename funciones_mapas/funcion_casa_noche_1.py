import importlib.util
import pygame

import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_guardado

from configuracion import TAMANO_CASILLA


MARCA_INICIO = "casa_noche_1:dialogo_salida"

estado_escena = "INICIO"
sonido_cerrar = None
imagen_luz = None
posiciones_luces = []

# Tamaño provisional del halo: independiente de la colisión.
TAMANO_LUZ = (160, 160)
OPACIDAD_LUZ = 140


def iniciar():
    global estado_escena, sonido_cerrar
    global imagen_luz, posiciones_luces

    dialogo.cargar_json("datos/casa_noche_1.json")

    # Preparar luces según las bases de los postes.
    posiciones_luces = []

    for y, fila in enumerate(mapa.matriz_activa):
        for x, casilla in enumerate(fila):
            if casilla == 20:
                # Poste de cuatro casillas:
                # la superior está tres filas sobre la base.
                posiciones_luces.append((
                    (x + 0.5) * TAMANO_CASILLA,
                    (y - 3 + 0.5) * TAMANO_CASILLA,
                ))

    imagen_luz = pygame.image.load(
        "recursos/sprites/efectos/luz_2.png"
    ).convert_alpha()

    imagen_luz = pygame.transform.scale(
        imagen_luz,
        TAMANO_LUZ,
    )
    imagen_luz.set_alpha(OPACIDAD_LUZ)

    # Evitar entrar en un mapa que todavía no hemos creado.
    if importlib.util.find_spec("mapas.pueblo_1_noche_1") is None:
        mapa.matriz_activa[0][3] = 1

    lucas = mapa.npcs_activos["lucas"]
    lucas["visible"] = True
    lucas["sprite_override"] = None

    viene_de_casa = (mapa.mateo_x, mapa.mateo_y) == (18, 17)

    if viene_de_casa and not sistema_guardado.cargando:
        try:
            sonido_cerrar = pygame.mixer.Sound(
                "recursos/sonidos/efectos/close_door.wav"
            )
            sonido_cerrar.play()
        except (pygame.error, FileNotFoundError) as error:
            print(f"[AUDIO] No se pudo cerrar la puerta: {error}")

    if viene_de_casa and MARCA_INICIO not in mapa.eventos_completados:
        mapa.direccion_mateo = "izq"
        mapa.jugador_bloqueado = True

        lucas["comportamiento"] = "estatico"
        lucas["x"] = 17
        lucas["y"] = 17
        lucas["px_x"] = float(17 * TAMANO_CASILLA)
        lucas["px_y"] = float(17 * TAMANO_CASILLA)
        lucas["direccion"] = "izq"

        estado_escena = "ESPERAR_ENTRADA"
    else:
        lucas["comportamiento"] = "sigue_jugador"
        mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"


def actualizar():
    global estado_escena

    if mapa.transicion_activa:
        return

    if estado_escena == "ESPERAR_ENTRADA":
        dialogo.iniciar_dialogo("evento_noche1_salida")
        estado_escena = "DIALOGO_SALIDA"

    elif estado_escena == "DIALOGO_SALIDA":
        if dialogo.obtener_evento_activo() is not None:
            return

        mapa.eventos_completados.add(MARCA_INICIO)
        mapa.npcs_activos["lucas"]["comportamiento"] = "sigue_jugador"
        mapa.jugador_bloqueado = False
        estado_escena = "JUGABLE"


def obtener_zonas_iluminadas():
    """Rectángulos en coordenadas del mapa, sin descontar la cámara."""
    if imagen_luz is None:
        return []

    return [
        imagen_luz.get_rect(center=(round(x), round(y)))
        for x, y in posiciones_luces
    ]


def dibujar_efectos(pantalla, camara_x, camara_y):
    if imagen_luz is None:
        return

    for zona in obtener_zonas_iluminadas():
        rect = zona.move(-camara_x, -camara_y)

        if pantalla.get_rect().colliderect(rect):
            pantalla.blit(imagen_luz, rect)