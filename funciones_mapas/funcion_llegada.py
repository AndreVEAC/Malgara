import pygame
import sistema_mapa
import sistema_dialogo

estado_escena = "INICIO"
tiempo_inicio = 0
tiempo_paso = 0

def iniciar():
    global estado_escena, tiempo_inicio
    
    sistema_dialogo.cargar_json("datos/llegada.json")
    sistema_mapa.jugador_bloqueado = True
    
    # Posiciones iniciales de los protagonistas
    sistema_mapa.mateo_x, sistema_mapa.mateo_y = 2, 9
    sistema_mapa.lucas_x, sistema_mapa.lucas_y = 2, 8
    sistema_mapa.direccion_mateo = "der"
    sistema_mapa.direccion_lucas = "der"
    
    # Posición inicial de la abuela
    sistema_mapa.abuela_x, sistema_mapa.abuela_y = 16, 5
    sistema_mapa.direccion_abuela = "abajo"
    sistema_mapa.abuela_visible = True
    
    estado_escena = "ESPERA_INICIAL"
    tiempo_inicio = pygame.time.get_ticks()

def actualizar():
    global estado_escena, tiempo_inicio, tiempo_paso
    tiempo_actual = pygame.time.get_ticks()

    if estado_escena == "ESPERA_INICIAL":
        if tiempo_actual - tiempo_inicio > 1000:
            sistema_dialogo.iniciar_dialogo("evento_llegada_1")
            estado_escena = "DIALOGO_1"

    elif estado_escena == "DIALOGO_1":
        if sistema_dialogo.obtener_evento_activo() is None:
            estado_escena = "ABUELA_BAJA"
            tiempo_paso = tiempo_actual

    elif estado_escena == "ABUELA_BAJA":
        sistema_mapa.direccion_abuela = "abajo"
        if tiempo_actual - tiempo_paso > sistema_mapa.RETRASO_LUCAS:
            sistema_mapa.abuela_y += 1
            tiempo_paso = tiempo_actual

        if sistema_mapa.abuela_y >= 9:
            estado_escena = "ABUELA_ACERCA"

    elif estado_escena == "ABUELA_ACERCA":
        sistema_mapa.direccion_abuela = "izq"
        if tiempo_actual - tiempo_paso > sistema_mapa.RETRASO_LUCAS:
            sistema_mapa.abuela_x -= 1
            tiempo_paso = tiempo_actual

        if sistema_mapa.abuela_x <= 3:
            sistema_mapa.direccion_abuela = "izq"
            sistema_mapa.direccion_mateo = "der"
            sistema_dialogo.iniciar_dialogo("evento_llegada_2")
            estado_escena = "DIALOGO_2"

    elif estado_escena == "DIALOGO_2":
        if sistema_dialogo.obtener_evento_activo() is None:
            estado_escena = "ABUELA_SE_VA"
            tiempo_paso = tiempo_actual

    elif estado_escena == "ABUELA_SE_VA":
        sistema_mapa.direccion_abuela = "der"
        if tiempo_actual - tiempo_paso > sistema_mapa.RETRASO_LUCAS:
            sistema_mapa.abuela_x += 1
            tiempo_paso = tiempo_actual

        if sistema_mapa.abuela_x > 20: 
            sistema_mapa.abuela_visible = False
            sistema_dialogo.iniciar_dialogo("evento_llegada_3")
            estado_escena = "DIALOGO_3"

    elif estado_escena == "DIALOGO_3":
        if sistema_dialogo.obtener_evento_activo() is None:
            estado_escena = "LUCAS_SE_VA"
            tiempo_paso = tiempo_actual

    elif estado_escena == "LUCAS_SE_VA":
        sistema_mapa.direccion_lucas = "der"
        if tiempo_actual - tiempo_paso > sistema_mapa.RETRASO_LUCAS:
            sistema_mapa.lucas_x += 1
            tiempo_paso = tiempo_actual

        if sistema_mapa.lucas_x > 20:
            sistema_mapa.jugador_bloqueado = False
            estado_escena = "JUGABLE"