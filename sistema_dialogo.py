import pygame
import json
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA
import sistema_mapa

# ==========================================
# VARIABLES GLOBALES DEL SISTEMA DE DIÁLOGOS
# ==========================================
datos_dialogo = {}
evento_actual = None
nombre_evento_activo = None
indice_linea = 0

# Estado de Selección de Opciones
en_modo_decision = False
opciones_actuales = []
opcion_seleccionada = 0

# Notificación estilo Telltale
texto_notificacion = ""
tiempo_inicio_notificacion = 0
tiempo_ultima_interaccion = 0
DURACION_NOTIFICACION = 3500

# Animación tipo máquina de escribir
indice_letra = 0
tiempo_ultima_letra = 0
VELOCIDAD_ESCRITURA = 30

# Avance rápido al MANTENER ESPACIO
RETRASO_MANTENER = 250          # ms que hay que sostener ESPACIO para activar el avance rápido
INTERVALO_SALTO_RAPIDO = 150    # ms entre una línea y la siguiente mientras se mantiene
tiempo_inicio_espacio = 0       # momento en que se presionó ESPACIO por última vez
tiempo_ultimo_salto_rapido = 0  # momento del último salto automático de línea
bloqueo_espacio = False         # evita que un ESPACIO ya mantenido salte la línea de un diálogo nuevo

# Recursos visuales y auditivos
fuente_texto = None
fuente_nombre = None
fuente_notificacion = None
sonido_bip = None
sonido_notificacion = None

tiempo_ultimo_cierre_dialogo = 0

# Colores de la interfaz
COLOR_CUADRO = (15, 15, 25, 230)
COLOR_BORDE = (220, 220, 240)
COLOR_TEXTO = (255, 255, 255)
COLOR_OPCION_INACTIVA = (160, 160, 180)
COLOR_OPCION_ACTIVA = (255, 220, 80)
COLOR_LUCAS = (255, 170, 50)
COLOR_MATEO = (50, 220, 130)

# Colores de la Notificación
COLOR_NOTIF_FONDO = (43, 27, 23, 230)
COLOR_NOTIF_BORDE = (212, 175, 55)
COLOR_NOTIF_TEXTO = (245, 230, 200)


def inicializar():
    global fuente_texto, fuente_nombre, fuente_notificacion, sonido_bip, sonido_notificacion
    pygame.font.init()
    pygame.mixer.init()

    try:
        fuente_texto = pygame.font.Font("recursos/fuentes/pixel.ttf", 20)
        fuente_nombre = pygame.font.Font("recursos/fuentes/pixel.ttf", 22)
        fuente_notificacion = pygame.font.Font("recursos/fuentes/pixel.ttf", 16)
    except (pygame.error, FileNotFoundError):
        fuente_texto = pygame.font.SysFont("Consolas", 18, bold=True)
        fuente_nombre = pygame.font.SysFont("Consolas", 20, bold=True)
        fuente_notificacion = pygame.font.SysFont("Consolas", 14, italic=True, bold=True)

    try:
        sonido_bip = pygame.mixer.Sound("recursos/sonidos/texto/blip.wav")
        sonido_bip.set_volume(0.25)
    except (pygame.error, FileNotFoundError):
        sonido_bip = None

    try:
        sonido_notificacion = pygame.mixer.Sound("recursos/sonidos/notificacion.wav")
        sonido_notificacion.set_volume(0.6)
    except (pygame.error, FileNotFoundError):
        sonido_notificacion = None

# FUNCIÓN PARA LA ARQUITECTURA DINÁMICA
def cargar_json(ruta="datos/prologo.json"):
    global datos_dialogo
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos_dialogo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error cargando {ruta}: {e}")
        datos_dialogo = {}


def iniciar_dialogo(nombre_evento):
    global evento_actual, nombre_evento_activo, indice_linea, indice_letra, tiempo_ultima_letra
    global en_modo_decision, opcion_seleccionada, opciones_actuales
    global bloqueo_espacio

    if not fuente_texto:
        inicializar()

    if nombre_evento in datos_dialogo:
        evento_actual = datos_dialogo[nombre_evento]
        nombre_evento_activo = nombre_evento
        indice_linea = 0
        indice_letra = 0
        tiempo_ultima_letra = pygame.time.get_ticks()
        en_modo_decision = False
        opciones_actuales = []
        opcion_seleccionada = 0
        # Si el jugador ya traía ESPACIO presionado, que no salte la primera línea
        bloqueo_espacio = True
        print(f"[DEBUG] Diálogo iniciado: {nombre_evento}")
    else:
        print(f"[DEBUG] Evento NO encontrado: {nombre_evento}. Disponibles: {list(datos_dialogo.keys())}")
        evento_actual = None
        nombre_evento_activo = None


def obtener_evento_activo():
    return nombre_evento_activo


def activar_notificacion(texto):
    global texto_notificacion, tiempo_inicio_notificacion
    texto_notificacion = texto
    tiempo_inicio_notificacion = pygame.time.get_ticks()
    if sonido_notificacion:
        sonido_notificacion.play()


def actualizar_y_dibujar(pantalla, eventos, estado_jugador):
    global evento_actual, nombre_evento_activo, indice_linea, indice_letra, tiempo_ultima_letra
    global en_modo_decision, opciones_actuales, opcion_seleccionada
    global tiempo_inicio_espacio, tiempo_ultimo_salto_rapido, bloqueo_espacio
    global tiempo_ultimo_cierre_dialogo

    tiempo_actual = pygame.time.get_ticks()

    if not evento_actual:
        nombre_evento_activo = None
        return "EXPLORACION"

    lineas = evento_actual.get("lineas", [])

    # REVISIÓN DE FIN DE EVENTO AUTOMÁTICO
    if indice_linea >= len(lineas):
        if "opciones" in evento_actual and not en_modo_decision:
            en_modo_decision = True
            opciones_actuales = evento_actual["opciones"]
            opcion_seleccionada = 0
        elif not en_modo_decision:
            siguiente = evento_actual.get("siguiente_evento")
            if siguiente and siguiente in datos_dialogo:
                iniciar_dialogo(siguiente)
                return "DIALOGO"  # <--- ¡ARREGLO 1!
            else:
                evento_actual = None
                nombre_evento_activo = None
                tiempo_ultimo_cierre_dialogo = tiempo_actual
                return "EXPLORACION"

    # ----------------------------------------------------
    # LÓGICA DE TEXTO NORMAL (soporta mantener presionado ESPACIO)
    # ----------------------------------------------------
    if not en_modo_decision:
        linea_actual = lineas[indice_linea]
        texto_completo = linea_actual.get("texto", "")

        # 1. Un toque de ESPACIO (KEYDOWN)
        toque_espacio = False
        for ev in eventos:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                toque_espacio = True
                tiempo_inicio_espacio = tiempo_actual
                bloqueo_espacio = False  # una pulsación nueva siempre es intencional

        # 2. ESPACIO mantenido. Solo cuenta si lleva presionado más de RETRASO_MANTENER ms,
        #    para que un toque normal (que dura unos pocos frames) no rellene la línea siguiente.
        teclas = pygame.key.get_pressed()
        if not teclas[pygame.K_SPACE]:
            bloqueo_espacio = False
        espacio_mantenido = (
            teclas[pygame.K_SPACE]
            and not bloqueo_espacio
            and tiempo_actual - tiempo_inicio_espacio > RETRASO_MANTENER
        )

        # Si el texto aún se está escribiendo...
        if indice_letra < len(texto_completo):
            # Toque o espacio mantenido: rellenar de golpe
            if toque_espacio or espacio_mantenido:
                indice_letra = len(texto_completo)
            # Escritura normal por goteo
            elif tiempo_actual - tiempo_ultima_letra > VELOCIDAD_ESCRITURA:
                indice_letra += 1
                tiempo_ultima_letra = tiempo_actual

                char_actual = texto_completo[indice_letra - 1]
                if char_actual != " " and sonido_bip:
                    sonido_bip.play()

        # Si el texto YA terminó de escribirse...
        else:
            avanzar_linea = toque_espacio

            # Si MANTIENE espacio, avanza solo cada INTERVALO_SALTO_RAPIDO ms
            if espacio_mantenido and (tiempo_actual - tiempo_ultimo_salto_rapido > INTERVALO_SALTO_RAPIDO):
                avanzar_linea = True
                tiempo_ultimo_salto_rapido = tiempo_actual

            if avanzar_linea:
                indice_linea += 1
                indice_letra = 0
                tiempo_ultima_letra = tiempo_actual

                # Si llegamos al final de las líneas normales, pasamos a opciones o cerramos
                if indice_linea >= len(lineas) and "opciones" in evento_actual:
                    en_modo_decision = True
                    opciones_actuales = evento_actual["opciones"]
                    opcion_seleccionada = 0
                elif indice_linea >= len(lineas):
                    siguiente = evento_actual.get("siguiente_evento")
                    if siguiente and siguiente in datos_dialogo:
                        iniciar_dialogo(siguiente)
                        return "DIALOGO"  # <--- ¡ARREGLO 2!
                    else:
                        evento_actual = None
                        nombre_evento_activo = None
                        tiempo_ultimo_cierre_dialogo = tiempo_actual
                        return "EXPLORACION"

    # LÓGICA DE MENÚ DE DECISIONES
    # LÓGICA DE MENÚ DE DECISIONES
    else:
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones_actuales)
                elif ev.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones_actuales)
                elif ev.key == pygame.K_SPACE:
                    
                    eleccion = opciones_actuales[opcion_seleccionada]
                    # Avisar al director antes de cambiar al diálogo de respuesta.

                    director = sistema_mapa.script_nivel_actual
                    if director and hasattr(director, "al_elegir_opcion"):
                        director.al_elegir_opcion(nombre_evento_activo)

                    # 1. Impacto de confianza de Lucas
                    if "efecto_lucas" in eleccion:
                        impacto = eleccion["efecto_lucas"]
                        if hasattr(estado_jugador, "confianza_lucas"):
                            estado_jugador.confianza_lucas += impacto

                        texto_noti = eleccion.get("notificacion", "Lucas recordará esto.")
                        activar_notificacion(texto_noti)

                    # 2. Guardar bandera de estado en el jugador si existe
                    if "variable_estado" in eleccion:
                        nombre_var = eleccion["variable_estado"]
                        valor_var = eleccion.get("valor_estado", True)
                        setattr(estado_jugador, nombre_var, valor_var)

                    # 3. Avanzar al siguiente evento o cerrar el diálogo
                    siguiente_evento = eleccion.get("siguiente_evento")
                    if siguiente_evento and siguiente_evento in datos_dialogo:
                        iniciar_dialogo(siguiente_evento)
                        return "DIALOGO"
                    else:
                        evento_actual = None
                        nombre_evento_activo = None
                        en_modo_decision = False
                        tiempo_ultimo_cierre_dialogo = tiempo_actual   # si lo tienes
                        return "EXPLORACION"
    # RENDERIZADO VISUAL
    ancho_caja = ANCHO_PANTALLA - 60
    alto_caja = 140
    pos_x = 30
    pos_y = ALTO_PANTALLA - alto_caja - 20

    superficie_caja = pygame.Surface((ancho_caja, alto_caja), pygame.SRCALPHA)
    superficie_caja.fill(COLOR_CUADRO)
    pygame.draw.rect(superficie_caja, COLOR_BORDE, (0, 0, ancho_caja, alto_caja), width=2)
    pantalla.blit(superficie_caja, (pos_x, pos_y))

    if not en_modo_decision:
        linea_actual = lineas[indice_linea]
        hablante = linea_actual.get("hablante", "???")
        color_nombre = COLOR_MATEO if hablante.upper() == "MATEO" else (COLOR_LUCAS if hablante.upper() == "LUCAS" else COLOR_TEXTO)

        surf_nombre = fuente_nombre.render(hablante, True, color_nombre)
        pantalla.blit(surf_nombre, (pos_x + 20, pos_y + 15))

        texto_parcial = texto_completo[:indice_letra]
        surf_texto = fuente_texto.render(texto_parcial, True, COLOR_TEXTO)
        pantalla.blit(surf_texto, (pos_x + 20, pos_y + 50))

        if indice_letra >= len(texto_completo):
            if (tiempo_actual // 400) % 2 == 0:
                surf_indicador = fuente_texto.render("▼", True, COLOR_TEXTO)
                pantalla.blit(surf_indicador, (pos_x + ancho_caja - 35, pos_y + alto_caja - 30))
    else:
        surf_titulo = fuente_nombre.render("¿Qué responder?", True, COLOR_TEXTO)
        pantalla.blit(surf_titulo, (pos_x + 20, pos_y + 12))

        for idx, opc in enumerate(opciones_actuales):
            es_seleccionada = (idx == opcion_seleccionada)
            prefix = "► " if es_seleccionada else "  "
            color = COLOR_OPCION_ACTIVA if es_seleccionada else COLOR_OPCION_INACTIVA

            texto_opcion = f"{prefix}{opc.get('texto', '')}"
            surf_opc = fuente_texto.render(texto_opcion, True, color)
            pantalla.blit(surf_opc, (pos_x + 20, pos_y + 45 + (idx * 28)))

    return "DIALOGO"


def dibujar_notificacion_global(pantalla):
    global texto_notificacion, tiempo_inicio_notificacion
    tiempo_actual = pygame.time.get_ticks()

    if texto_notificacion and (tiempo_actual - tiempo_inicio_notificacion < DURACION_NOTIFICACION):
        if not fuente_notificacion:
            inicializar()

        surf_txt_notif = fuente_notificacion.render(texto_notificacion, True, COLOR_NOTIF_TEXTO)

        ancho_notif = surf_txt_notif.get_width() + 30
        alto_notif = 40
        margin_right = 20
        margin_top = 20
        pos_x = ANCHO_PANTALLA - ancho_notif - margin_right
        pos_y = margin_top

        superficie_notif = pygame.Surface((ancho_notif, alto_notif), pygame.SRCALPHA)
        superficie_notif.fill(COLOR_NOTIF_FONDO)
        pygame.draw.rect(superficie_notif, COLOR_NOTIF_BORDE, (0, 0, ancho_notif, alto_notif), width=2)

        pantalla.blit(superficie_notif, (pos_x, pos_y))
        pantalla.blit(surf_txt_notif, (pos_x + 15, pos_y + 10))
    else:
        texto_notificacion = ""
        
def obtener_tiempo_ultimo_cierre():
    return tiempo_ultimo_cierre_dialogo