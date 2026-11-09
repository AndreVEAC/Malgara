import pygame
import json
from pygame.locals import K_SPACE, K_1, K_2, K_3
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, BLANCO, VERDE_MATEO, AZUL_UI

pygame.font.init()
fuente = pygame.font.SysFont("arial", 20)

datos_escena = None
indice_linea = 0
esperando_decision = False

def iniciar_dialogo(id_evento):
    global datos_escena, indice_linea, esperando_decision
    # Cargar el archivo JSON de la escena actual
    with open("datos/prologo.json", "r", encoding="utf-8") as archivo:
        datos_completos = json.load(archivo)
    
    datos_escena = datos_completos[id_evento]
    indice_linea = 0
    esperando_decision = False

def actualizar_y_dibujar(pantalla, eventos, estado_jugador):
    global indice_linea, esperando_decision
    
    # 1. MANEJO DE ENTRADAS (Input)
    for evento in eventos:
        if evento.type == pygame.KEYDOWN:
            # Si estamos leyendo líneas normales
            if not esperando_decision:
                if evento.key == K_SPACE:
                    indice_linea += 1
                    # Comprobar si se acabaron las líneas
                    if indice_linea >= len(datos_escena["lineas"]):
                        if datos_escena.get("es_decision"):
                            esperando_decision = True
                        else:
                            # Fin del diálogo normal, volvemos a movernos
                            return "EXPLORACION"
            
            # Si estamos en la toma de decisión
            else:
                opcion_elegida = None
                if evento.key == K_1: opcion_elegida = 0
                if evento.key == K_2: opcion_elegida = 1
                if evento.key == K_3: opcion_elegida = 2
                
                if opcion_elegida is not None and opcion_elegida < len(datos_escena["opciones"]):
                    # Aplicar la consecuencia en la confianza de Lucas
                    cambio = datos_escena["opciones"][opcion_elegida]["efecto_lucas"]
                    estado_jugador.aplicar_efectos({"confianza_lucas": cambio})
                    print(f"Decisión tomada. Confianza de Lucas cambió en: {cambio}")
                    return "EXPLORACION"

    # 2. DIBUJAR LA INTERFAZ
    # Caja de texto base
    caja = pygame.Surface((ANCHO_PANTALLA - 40, 150))
    caja.set_alpha(230)
    caja.fill(AZUL_UI)
    pantalla.blit(caja, (20, ALTO_PANTALLA - 170))
    pygame.draw.rect(pantalla, BLANCO, (20, ALTO_PANTALLA - 170, ANCHO_PANTALLA - 40, 150), 2)

    if not esperando_decision:
        linea_actual = datos_escena["lineas"][indice_linea]
        # Dibujar Nombre
        color_nombre = VERDE_MATEO if linea_actual["hablante"] == "Mateo" else (255, 165, 0)
        pantalla.blit(fuente.render(f"{linea_actual['hablante']}:", True, color_nombre), (40, ALTO_PANTALLA - 155))
        # Dibujar Texto
        pantalla.blit(fuente.render(linea_actual["texto"], True, BLANCO), (40, ALTO_PANTALLA - 125))
        # Ayuda visual
        pantalla.blit(fuente.render("▼ [ESPACIO]", True, BLANCO), (ANCHO_PANTALLA - 150, ALTO_PANTALLA - 45))
    
    else:
        # Dibujar Opciones de Decisión
        pantalla.blit(fuente.render("Decisión:", True, BLANCO), (40, ALTO_PANTALLA - 160))
        y_opcion = ALTO_PANTALLA - 130
        for opcion in datos_escena["opciones"]:
            pantalla.blit(fuente.render(opcion["texto"], True, BLANCO), (40, y_opcion))
            y_opcion += 30

    # Retornamos "DIALOGO" para indicar al main que seguimos en esta pantalla
    return "DIALOGO"