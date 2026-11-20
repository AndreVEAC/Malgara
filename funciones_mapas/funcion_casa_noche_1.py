from collections import deque
import importlib.util
import pygame

import sistema_mapa as mapa
import sistema_dialogo as dialogo
import sistema_guardado
import sistema_audio as audio
import sistema_escondites as escondites
import sistema_vigilancia as vigilancia

from configuracion import TAMANO_CASILLA as T, ALTO_PANTALLA


MARCA_INICIO = "casa_noche_1:dialogo_salida"
MARCA_FINAL = "casa_noche_1:tutorial_completado"

CONTROL_CINEMATICO = False
CAMARA_CINEMATICA = None

estado_escena = "INICIO"
espera_hasta = 0
ultimo_paso = {}

imagen_luz = None
sonido_cerrar = None
posiciones_luces = []

TAMANO_LUZ = (160, 160)
OPACIDAD_LUZ = 140

# Cuatro casillas de activación, sin modificar la matriz.
TRIGGER = {(3, y) for y in range(16, 20)}


def iniciar():
    global CONTROL_CINEMATICO, CAMARA_CINEMATICA
    global estado_escena, espera_hasta
    global imagen_luz, posiciones_luces, sonido_cerrar

    dialogo.cargar_json("datos/casa_noche_1.json")

    ultimo_paso.clear()
    espera_hasta = 0
    CAMARA_CINEMATICA = None
    escondites.escondido = False
    audio.establecer_persecucion(False)

    CONTROL_CINEMATICO = (
        MARCA_FINAL not in mapa.eventos_completados
    )

    posiciones_luces = [
        ((x + 0.5) * T, (y - 3 + 0.5) * T)
        for y, fila in enumerate(mapa.matriz_activa)
        for x, numero in enumerate(fila)
        if numero == 20
    ]

    imagen_luz = pygame.image.load(
        "recursos/sprites/efectos/luz_2.png"
    ).convert_alpha()

    imagen_luz = pygame.transform.scale(
        imagen_luz, TAMANO_LUZ
    )
    imagen_luz.set_alpha(OPACIDAD_LUZ)

    if importlib.util.find_spec("mapas.pueblo_1_noche_1") is None:
        mapa.matriz_activa[0][3] = 1

    lucas = mapa.npcs_activos["lucas"]
    lucas["visible"] = True
    lucas["sprite_override"] = None
    lucas["comportamiento"] = "sigue_jugador"

    mapa.jugador_bloqueado = False

    estado_escena = (
        "ESPERAR_TRIGGER"
        if CONTROL_CINEMATICO
        else "JUGABLE"
    )

    if (mapa.mateo_x, mapa.mateo_y) == (18, 17):
        if not sistema_guardado.cargando:
            try:
                sonido_cerrar = pygame.mixer.Sound(
                    "recursos/sonidos/efectos/close_door.wav"
                )
                sonido_cerrar.play()

            except (pygame.error, FileNotFoundError) as error:
                print(
                    f"[AUDIO] No se pudo cerrar la puerta: {error}"
                )

        if (
            CONTROL_CINEMATICO
            and MARCA_INICIO not in mapa.eventos_completados
        ):
            mapa.jugador_bloqueado = True
            mapa.direccion_mateo = "izq"

            lucas["comportamiento"] = "estatico"
            _colocar("lucas", (17, 17), "izq")

            estado_escena = "ENTRADA"


def _posicion(nombre):
    if nombre == "mateo":
        return mapa.mateo_x, mapa.mateo_y

    npc = mapa.npcs_activos[nombre]
    return npc["x"], npc["y"]


def _pixeles(nombre):
    if nombre == "mateo":
        return mapa.mateo_px_x, mapa.mateo_px_y

    npc = mapa.npcs_activos[nombre]
    return npc["px_x"], npc["px_y"]


def _mirar(nombre, direccion):
    if nombre == "mateo":
        mapa.direccion_mateo = direccion
    else:
        mapa.npcs_activos[nombre]["direccion"] = direccion


def _colocar(nombre, posicion, direccion):
    x, y = posicion

    if nombre == "mateo":
        mapa.mateo_x, mapa.mateo_y = x, y
        mapa.mateo_px_x = float(x * T)
        mapa.mateo_px_y = float(y * T)

    else:
        mapa.npcs_activos[nombre].update(
            x=x,
            y=y,
            px_x=float(x * T),
            px_y=float(y * T),
        )

    _mirar(nombre, direccion)


def _llego(nombre, destino):
    px, py = _pixeles(nombre)

    return (
        _posicion(nombre) == destino
        and abs(px - destino[0] * T) < 0.75
        and abs(py - destino[1] * T) < 0.75
    )


def _paso(nombre, destino):
    """Buscar un camino evitando obstáculos y otros personajes."""
    ocupadas = set()
    actores = ["mateo"] + list(mapa.npcs_activos)

    for otro in actores:
        if otro == nombre:
            continue

        visible = (
            not escondites.escondido
            if otro == "mateo"
            else mapa.npcs_activos[otro].get("visible", True)
        )

        if visible:
            ocupadas.add(_posicion(otro))

            # Reservar también la posición visual durante un paso.
            px, py = _pixeles(otro)
            ocupadas.add((round(px / T), round(py / T)))

    inicio = _posicion(nombre)
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

        for posicion in vecinos:
            if posicion in visitadas:
                continue

            visitadas.add(posicion)

            if (
                posicion in ocupadas
                or mapa.casilla_bloqueada(*posicion)
            ):
                continue

            x2, y2 = posicion

            if mapa.matriz_activa[y2][x2] in mapa.portales_activos:
                continue

            pendientes.append((
                posicion,
                posicion if primero is None else primero,
            ))

    return None


def _caminar(nombre, destino, ahora, corriendo=False):
    if nombre != "mateo":
        mapa.npcs_activos[nombre]["congelado"] = False

    if _llego(nombre, destino):
        return True

    intervalo = (
        mapa.RETRASO_MATEO // 2
        if corriendo
        else mapa.RETRASO_MATEO
    )

    if ahora - ultimo_paso.get(nombre, 0) <= intervalo:
        return False

    ultimo_paso[nombre] = ahora
    paso = _paso(nombre, destino)

    if paso is not None:
        x, y = _posicion(nombre)
        dx, dy = paso[0] - x, paso[1] - y

        if dx:
            direccion = "der" if dx > 0 else "izq"
        else:
            direccion = "abajo" if dy > 0 else "arriba"

        _mirar(nombre, direccion)

        if nombre == "mateo":
            mapa.mateo_x, mapa.mateo_y = paso
        else:
            npc = mapa.npcs_activos[nombre]
            npc["x"], npc["y"] = paso

    return False


def _pareja(destino_mateo, destino_lucas, ahora, corriendo=False):
    # Actualizar ambos aunque uno todavía no haya llegado.
    mateo_listo = _caminar(
        "mateo", destino_mateo, ahora, corriendo
    )
    lucas_listo = _caminar(
        "lucas", destino_lucas, ahora, corriendo
    )

    return mateo_listo and lucas_listo


def _hablar(evento, siguiente_estado):
    global estado_escena

    dialogo.iniciar_dialogo(evento)

    if dialogo.obtener_evento_activo() is None:
        raise ValueError(
            f"Falta el diálogo de la cinemática: {evento}"
        )

    estado_escena = siguiente_estado


def _camara(normal=False):
    global CAMARA_CINEMATICA

    if CAMARA_CINEMATICA is None:
        return True

    if normal:
        objetivo = mapa.mateo_px_y - ALTO_PANTALLA / 2

    else:
        alturas = [
            _pixeles(nombre)[1]
            for nombre in ("mateo", "lucas", "loco")
        ]

        objetivo = (
            (min(alturas) + max(alturas) + T) / 2
            - ALTO_PANTALLA / 2
        )

    limite = max(0, mapa.filas_mapa * T - ALTO_PANTALLA)
    objetivo = max(0, min(objetivo, limite))

    actual = CAMARA_CINEMATICA[1]

    CAMARA_CINEMATICA = (
        0,
        actual + (objetivo - actual) * 0.12,
    )

    return abs(CAMARA_CINEMATICA[1] - objetivo) < 1


def actualizar():
    global estado_escena, espera_hasta
    global CONTROL_CINEMATICO, CAMARA_CINEMATICA

    if mapa.transicion_activa or estado_escena == "JUGABLE":
        return

    ahora = pygame.time.get_ticks()
    loco = mapa.npcs_activos["loco"]
    lucas = mapa.npcs_activos["lucas"]

    # Solo las fases con movimiento vuelven a habilitar su interpolación.
    loco["congelado"] = True

    camara_lista = _camara(
        normal=estado_escena == "DEVOLVER_CONTROL"
    )

    if dialogo.obtener_evento_activo() is not None:
        return

    if estado_escena == "ENTRADA":
        _hablar("evento_noche1_salida", "FIN_SALIDA")

    elif estado_escena == "FIN_SALIDA":
        mapa.eventos_completados.add(MARCA_INICIO)
        lucas["comportamiento"] = "sigue_jugador"
        mapa.jugador_bloqueado = False
        estado_escena = "ESPERAR_TRIGGER"

    elif estado_escena == "ESPERAR_TRIGGER":
        if _posicion("mateo") in TRIGGER:
            CAMARA_CINEMATICA = mapa.calcular_camara()
            mapa.jugador_bloqueado = True
            lucas["comportamiento"] = "estatico"
            estado_escena = "COLOCAR_PAREJA"

    elif estado_escena == "COLOCAR_PAREJA":
        if _pareja((3, 17), (4, 17), ahora):
            _mirar("mateo", "arriba")
            _mirar("lucas", "arriba")

            if camara_lista:
                _hablar("evento_noche1_avistar", "ACERCARSE")

    elif estado_escena == "ACERCARSE":
        # Ambos quedan dentro de la luz del segundo poste.
        if _pareja((4, 10), (5, 10), ahora):
            _mirar("mateo", "arriba")
            _mirar("lucas", "arriba")

            if camara_lista:
                _hablar(
                    "evento_noche1_acercarse",
                    "FIN_ACERCARSE",
                )

    elif estado_escena == "FIN_ACERCARSE":
        espera_hasta = ahora + 2000
        estado_escena = "ANTES_GIRO"

    elif estado_escena == "ANTES_GIRO":
        if ahora >= espera_hasta:
            _mirar("loco", "abajo")
            
            try:
                golpe = pygame.mixer.Sound(
                    "recursos/sonidos/efectos/susto.wav"
                )
                golpe.set_volume(0.7)
                golpe.play()

            except (pygame.error, FileNotFoundError) as error:
                print(f"[AUDIO] No se pudo reproducir el susto: {error}")
            espera_hasta = ahora + 2000
            estado_escena = "MIRADA"

    elif estado_escena == "MIRADA":
        if ahora >= espera_hasta:
            estado_escena = "LOCO_SE_ACERCA"

    elif estado_escena == "LOCO_SE_ACERCA":
        # Rodea el poste; se acerca caminando.
        if _caminar("loco", (5, 8), ahora):
            _mirar("loco", "abajo")
            _hablar("evento_noche1_corre", "HUIR")

    elif estado_escena == "HUIR":
        # Comienza al correr y continúa mientras están escondidos.
        # La función evita reiniciar la canción en cada fotograma.
        audio.establecer_persecucion(True)

        llegaron = _pareja(
            (2, 16),
            (1, 17),
            ahora,
            corriendo=True,
        )

        # Él continúa caminando mientras ellos corren.
        _caminar("loco", (3, 16), ahora)

        if llegaron:
            _mirar("mateo", "izq")
            _mirar("lucas", "arriba")

            escondites.escondido = True
            lucas["visible"] = False

            estado_escena = "LOCO_AL_BARRIL"

    elif estado_escena == "LOCO_AL_BARRIL":
        if _caminar("loco", (3, 16), ahora):
            _mirar("loco", "izq")
            espera_hasta = ahora + 5000
            estado_escena = "ESPERA_BARRIL"

    elif estado_escena == "ESPERA_BARRIL":
        if ahora >= espera_hasta:
            # Terminar la música de peligro al completar los 5 segundos.
            audio.establecer_persecucion(False)
            estado_escena = "LOCO_REGRESA"

    elif estado_escena == "LOCO_REGRESA":
        if _caminar("loco", (5, 5), ahora):
            _mirar("loco", "izq")

            if camara_lista:
                _hablar(
                    "evento_noche1_escondidos",
                    "SALIR_BARRIL",
                )

    elif estado_escena == "SALIR_BARRIL":
        escondites.escondido = False
        lucas["visible"] = True

        _hablar(
            "evento_noche1_despues_barril",
            "DEVOLVER_CONTROL",
        )

    elif estado_escena == "DEVOLVER_CONTROL":
        teclas = pygame.key.get_pressed()

        retenidas = any(
            teclas[tecla]
            for tecla in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
            )
        )

        if camara_lista and not retenidas:
            # El loco ya volvió a su puesto.
            vigilancia.configurar()

            lucas["comportamiento"] = "sigue_jugador"
            lucas["_tiempo_ultimo_paso"] = ahora

            mapa.eventos_completados.add(MARCA_FINAL)
            mapa.tiempo_ultima_interaccion = ahora
            mapa.tiempo_ultimo_paso_mateo = ahora

            mapa.jugador_bloqueado = False
            CONTROL_CINEMATICO = False
            CAMARA_CINEMATICA = None
            estado_escena = "JUGABLE"


def obtener_zonas_iluminadas():
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