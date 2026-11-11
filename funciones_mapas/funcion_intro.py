import pygame
import sistema_mapa
import sistema_dialogo

estado_escena = "INICIO"
tiempo_inicio = 0
tiempo_paso = 0  # Temporizador para los pasos de Lucas

def iniciar():
    """Se ejecuta una sola vez cuando el nivel carga."""
    global estado_escena, tiempo_inicio
    
    sistema_dialogo.cargar_json("datos/intro.json")
    
    sistema_mapa.jugador_bloqueado = True
    sistema_mapa.lucas_x, sistema_mapa.lucas_y = 8, 7
    sistema_mapa.direccion_lucas = "izq"
    sistema_mapa.direccion_mateo = "der"
    
    estado_escena = "ESPERA_INICIAL"
    tiempo_inicio = pygame.time.get_ticks()

def actualizar():
    """Se ejecuta en cada fotograma mientras estés en este mapa."""
    global estado_escena, tiempo_inicio, tiempo_paso
    tiempo_actual = pygame.time.get_ticks()

    if estado_escena == "ESPERA_INICIAL":
        if tiempo_actual - tiempo_inicio > 1500:
            sistema_dialogo.iniciar_dialogo("evento_intro_1")
            estado_escena = "ESPERANDO_DIALOGO"

    elif estado_escena == "ESPERANDO_DIALOGO":
        if sistema_dialogo.obtener_evento_activo() is None:
            estado_escena = "LUCAS_SE_VA"
            tiempo_paso = tiempo_actual  # Iniciamos el reloj de pasos

    elif estado_escena == "LUCAS_SE_VA":
        sistema_mapa.direccion_lucas = "der"
        
        # Le decimos a la IA de Lucas que avance 1 casilla lógicamente cada 200ms
        # El motor (LERP) se encargará de suavizar los píxeles automáticamente
        if tiempo_actual - tiempo_paso > 200:
            sistema_mapa.lucas_x += 1
            tiempo_paso = tiempo_actual
        
        # Si ya caminó hasta la orilla (columna 25)
        if sistema_mapa.lucas_x > 25: 
            sistema_mapa.jugador_bloqueado = False  # ¡Mateo es libre!
            estado_escena = "JUGABLE"

    elif estado_escena == "JUGABLE":
        if sistema_mapa.mateo_x >= len(sistema_mapa.matriz_activa[0]) - 2:
            sistema_mapa.cargar_nivel("prologo")