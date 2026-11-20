import pygame
import sistema_dialogo


escondido = False
barriles = set()

_espacio_anterior = False
_esperar_soltar_movimiento = False
_seguidores_ocultos = []
_bloqueo_anterior = False

_imagen_tecla = None
_texto_aviso = None


def configurar(mapa_datos):
    """Preparar los escondites al cargar cada mapa."""
    global escondido, barriles
    global _espacio_anterior, _esperar_soltar_movimiento
    global _seguidores_ocultos, _bloqueo_anterior
    global _imagen_tecla, _texto_aviso

    escondido = False
    barriles = set(getattr(mapa_datos, "BARRILES", set()))

    _seguidores_ocultos = []
    _bloqueo_anterior = False
    _esperar_soltar_movimiento = False

    # Si llegamos manteniendo Espacio, exigir soltarlo primero.
    _espacio_anterior = bool(
        pygame.key.get_pressed()[pygame.K_SPACE]
    )

    if barriles and _imagen_tecla is None:
        imagen = pygame.image.load(
            "recursos/sprites/objetos/tecla_espacio.png"
        ).convert_alpha()

        ancho = 72
        alto = max(
            1,
            round(imagen.get_height() * ancho / imagen.get_width()),
        )

        _imagen_tecla = pygame.transform.scale(
            imagen, (ancho, alto)
        )

        fuente = sistema_dialogo.fuente_texto

        if fuente is None:
            fuente = pygame.font.Font(
                "recursos/fuentes/VT323-Regular.ttf", 20
            )
        _texto_aviso = fuente.render(
            "Mantén pulsado",
            True,
            (255, 255, 255),
        )


def actualizar(teclas):
    """
    Devuelve True cuando este sistema consume el control del jugador.
    Se llama cada fotograma, incluso estando escondido.
    """
    import sistema_mapa as mapa

    global _espacio_anterior, _esperar_soltar_movimiento

    espacio = bool(teclas[pygame.K_SPACE])
    acaba_de_pulsar = espacio and not _espacio_anterior
    _espacio_anterior = espacio
    
    # El director decide cuándo entran y salen durante la escena.
    if getattr(
        mapa.script_nivel_actual,
        "CONTROL_CINEMATICO",
        False,
    ):
        return False

    if escondido:
        if not espacio:
            _salir(mapa)

        # También bloquear el movimiento en el fotograma de salida.
        return True

    if _esperar_soltar_movimiento:
        hay_direccion = any(
            teclas[tecla]
            for tecla in (
                pygame.K_UP,
                pygame.K_DOWN,
                pygame.K_LEFT,
                pygame.K_RIGHT,
            )
        )

        if not hay_direccion:
            _esperar_soltar_movimiento = False

        return True

    if (
        not acaba_de_pulsar
        or mapa.jugador_bloqueado
        or mapa.transicion_activa
        or sistema_dialogo.obtener_evento_activo() is not None
    ):
        return False

    desplazamientos = {
        "arriba": (0, -1),
        "abajo": (0, 1),
        "izq": (-1, 0),
        "der": (1, 0),
    }

    dx, dy = desplazamientos.get(
        mapa.direccion_mateo, (0, 0)
    )

    frente = (mapa.mateo_x + dx, mapa.mateo_y + dy)

    if frente not in barriles:
        return False

    # Una caja colocada delante del barril impide utilizarlo.
    if frente in mapa.bloqueos_activos:
        return False

    _entrar(mapa)
    return True


def _entrar(mapa):
    global escondido, _bloqueo_anterior
    global _seguidores_ocultos

    escondido = True
    _bloqueo_anterior = mapa.jugador_bloqueado
    mapa.jugador_bloqueado = True
    mapa.tiempo_ultima_interaccion = pygame.time.get_ticks()

    _seguidores_ocultos = []

    for npc in mapa.npcs_activos.values():
        if (
            npc.get("visible", True)
            and npc.get("comportamiento") == "sigue_jugador"
        ):
            # Guardar la referencia: conservamos posición y orientación.
            _seguidores_ocultos.append(npc)
            npc["visible"] = False


def _salir(mapa):
    global escondido, _esperar_soltar_movimiento
    global _seguidores_ocultos

    escondido = False

    # No desbloquear un cambio de mapa iniciado por otro sistema.
    if not mapa.transicion_activa:
        mapa.jugador_bloqueado = _bloqueo_anterior

    ahora = pygame.time.get_ticks()

    for npc in _seguidores_ocultos:
        npc["visible"] = True
        npc["_tiempo_ultimo_paso"] = ahora

    _seguidores_ocultos = []

    mapa.tiempo_ultima_interaccion = ahora
    mapa.tiempo_ultimo_paso_mateo = ahora

    # Evitar salir caminando por una flecha que seguía presionada.
    _esperar_soltar_movimiento = True


def dibujar_aviso(pantalla):
    
    import sistema_mapa as mapa

    # El aviso aparecerá al usar un barril jugando normalmente.
    if getattr(
        mapa.script_nivel_actual,
        "CONTROL_CINEMATICO",
        False,
    ):
        return
    
    if not escondido or _imagen_tecla is None or _texto_aviso is None:
        return

    separacion = 12

    ancho = (
        _imagen_tecla.get_width()
        + separacion
        + _texto_aviso.get_width()
    )

    alto = max(
        _imagen_tecla.get_height(),
        _texto_aviso.get_height(),
    )

    x = (pantalla.get_width() - ancho) // 2
    y = pantalla.get_height() - alto - 24

    # Tecla, sin panel de fondo.
    pantalla.blit(
        _imagen_tecla,
        (
            x,
            y + (alto - _imagen_tecla.get_height()) // 2,
        ),
    )

    # Texto con la fuente de los diálogos.
    pantalla.blit(
        _texto_aviso,
        (
            x + _imagen_tecla.get_width() + separacion,
            y + (alto - _texto_aviso.get_height()) // 2,
        ),
    )