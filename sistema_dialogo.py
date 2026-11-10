import pygame
import json
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA

# ==========================================
# VARIABLES GLOBALES DEL SISTEMA DE DIÁLOGOS
# ==========================================
datos_dialogo = {}
evento_actual = None
indice_linea = 0

# Estado de Selección de Opciones (Decisiones)
en_modo_decision = False
opciones_actuales = []
opcion_seleccionada = 0

# Notificación "Lucas recordará esto" (Estilo Telltale)
texto_notificacion = ""
tiempo_inicio_notificacion = 0
DURACION_NOTIFICACION = 3500  # Milisegundos visible (3.5 segundos)

# Animación tipo máquina de escribir
indice_letra = 0
tiempo_ultima_letra = 0
VELOCIDAD_ESCRITURA = 30

# Recursos visuales y auditivos
fuente_texto = None
fuente_nombre = None
fuente_notificacion = None
sonido_bip = None

# Colores de la interfaz
COLOR_CUADRO = (15, 15, 25, 230)
COLOR_BORDE = (220, 220, 240)
COLOR_TEXTO = (255, 255, 255)
COLOR_OPCION_INACTIVA = (160, 160, 180)
COLOR_OPCION_ACTIVA = (255, 220, 80)
COLOR_LUCAS = (255, 170, 50)
COLOR_MATEO = (50, 220, 130)

# Colores de la Notificación ("Lucas recordará esto")
COLOR_NOTIF_FONDO = (43, 27, 23, 230)   # Café oscuro semitransparente
COLOR_NOTIF_BORDE = (212, 175, 55)      # Dorado elegante (#D4AF37)
COLOR_NOTIF_TEXTO = (245, 230, 200)     # Crema/Dorado muy claro


def inicializar():
    """Carga fuentes y efectos de sonido al arrancar el motor."""
    global fuente_texto, fuente_nombre, fuente_notificacion, sonido_bip
    
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

    cargar_json_dialogos()


def cargar_json_dialogos():
    global datos_dialogo
    try:
        with open("datos/prologo.json", "r", encoding="utf-8") as f:
            datos_dialogo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error cargando los diálogos del JSON: {e}")
        datos_dialogo = {}


def iniciar_dialogo(nombre_evento):
    """Inicia una secuencia de diálogo según el trigger pisado."""
    global evento_actual, indice_linea, indice_letra, tiempo_ultima_letra
    global en_modo_decision, opcion_seleccionada, opciones_actuales
    
    if not fuente_texto:
        inicializar()

    if nombre_evento in datos_dialogo:
        evento_actual = datos_dialogo[nombre_evento]
        indice_linea = 0
        indice_letra = 0
        tiempo_ultima_letra = pygame.time.get_ticks()
        en_modo_decision = False
        opciones_actuales = []
        opcion_seleccionada = 0
    else:
        print(f"Advertencia: El evento '{nombre_evento}' no existe en prologo.json")
        evento_actual = None


def actualizar_y_dibujar(pantalla, eventos, estado_jugador):
    """Procesa animaciones, entrada de teclado y renderiza recuadros de diálogo y notificaciones."""
    global evento_actual, indice_linea, indice_letra, tiempo_ultima_letra
    global en_modo_decision, opciones_actuales, opcion_seleccionada
    global texto_notificacion, tiempo_inicio_notificacion
    
    tiempo_actual = pygame.time.get_ticks()

    if not evento_actual:
        # Si no hay diálogo activo, de todos modos dibujamos la notificación si sigue activa
        dibujar_notificacion_si_corresponde(pantalla, tiempo_actual)
        return "EXPLORACION"

    lineas = evento_actual.get("lineas", [])
    
    if indice_linea >= len(lineas):
        if "opciones" in evento_actual and not en_modo_decision:
            en_modo_decision = True
            opciones_actuales = evento_actual["opciones"]
            opcion_seleccionada = 0
        elif not en_modo_decision:
            evento_actual = None
            dibujar_notificacion_si_corresponde(pantalla, tiempo_actual)
            return "EXPLORACION"

    # ----------------------------------------------------
    # 1. LÓGICA DE TEXTO NORMAL
    # ----------------------------------------------------
    if not en_modo_decision:
        linea_actual = lineas[indice_linea]
        texto_completo = linea_actual.get("texto", "")

        if indice_letra < len(texto_completo):
            if tiempo_actual - tiempo_ultima_letra > VELOCIDAD_ESCRITURA:
                indice_letra += 1
                tiempo_ultima_letra = tiempo_actual
                
                char_actual = texto_completo[indice_letra - 1]
                if char_actual != " " and sonido_bip:
                    sonido_bip.play()

        for ev in eventos:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                if indice_letra < len(texto_completo):
                    indice_letra = len(texto_completo)
                else:
                    indice_linea += 1
                    indice_letra = 0
                    tiempo_ultima_letra = tiempo_actual
                    
                    if indice_linea >= len(lineas) and "opciones" in evento_actual:
                        en_modo_decision = True
                        opciones_actuales = evento_actual["opciones"]
                        opcion_seleccionada = 0
                    elif indice_linea >= len(lineas):
                        evento_actual = None
                        dibujar_notificacion_si_corresponde(pantalla, tiempo_actual)
                        return "EXPLORACION"

    # ----------------------------------------------------
    # 2. LÓGICA DE MENÚ DE DECISIONES
    # ----------------------------------------------------
    else:
        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones_actuales)
                elif ev.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones_actuales)
                elif ev.key == pygame.K_SPACE:
                    eleccion = opciones_actuales[opcion_seleccionada]
                    
                    # Impacto en métrica y activación de notificación
                    if "impacto" in eleccion:
                        impacto = eleccion["impacto"]
                        if hasattr(estado_jugador, "confianza_lucas"):
                            estado_jugador.confianza_lucas += impacto.get("confianza_lucas", 0)
                        
                        # Disparar aviso visual
                        texto_notificacion = "Lucas recordará esto."
                        tiempo_inicio_notificacion = tiempo_actual
                    
                    siguiente_evento = eleccion.get("siguiente_evento")
                    if siguiente_evento and siguiente_evento in datos_dialogo:
                        iniciar_dialogo(siguiente_evento)
                    else:
                        evento_actual = None
                        en_modo_decision = False
                        dibujar_notificacion_si_corresponde(pantalla, tiempo_actual)
                        return "EXPLORACION"

    # ----------------------------------------------------
    # 3. RENDERIZADO VISUAL CAJA DE DIÁLOGO
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # 4. RENDERIZADO DE LA NOTIFICACIÓN
    # ----------------------------------------------------
    dibujar_notificacion_si_corresponde(pantalla, tiempo_actual)

    return "DIALOGO"


def dibujar_notificacion_si_corresponde(pantalla, tiempo_actual):
    """Dibuja el recuadro emergente arriba a la derecha si está dentro del tiempo límite."""
    global texto_notificacion, tiempo_inicio_notificacion

    if texto_notificacion and (tiempo_actual - tiempo_inicio_notificacion < DURACION_NOTIFICACION):
        surf_txt_notif = fuente_notificacion.render(texto_notificacion, True, COLOR_NOTIF_TEXTO)
        
        ancho_notif = surf_txt_notif.get_width() + 30
        alto_notif = 40
        margin_right = 20
        margin_top = 20
        pos_x = ANCHO_PANTALLA - ancho_notif - margin_right
        pos_y = margin_top

        # Superficie café oscura con transparencia
        superficie_notif = pygame.Surface((ancho_notif, alto_notif), pygame.SRCALPHA)
        superficie_notif.fill(COLOR_NOTIF_FONDO)
        
        # Borde dorado doble línea de adorno
        pygame.draw.rect(superficie_notif, COLOR_NOTIF_BORDE, (0, 0, ancho_notif, alto_notif), width=2)
        
        pantalla.blit(superficie_notif, (pos_x, pos_y))
        pantalla.blit(surf_txt_notif, (pos_x + 15, pos_y + 10))
    else:
        texto_notificacion = ""