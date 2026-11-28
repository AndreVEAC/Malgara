import sys

import pygame
from pygame.locals import QUIT
from configuracion import ANCHO_PANTALLA, ALTO_PANTALLA, TITULO_JUEGO, FPS
from estado import BUSQUEDA_DIA_2, EstadoJuego
import sistema_mapa
import sistema_dialogo
import sistema_guardado
import sistema_audio
import reloj_juego
from interfaz_controles import GuiaControles
from interfaz_menu import MenuPausa, MenuPrincipal
from funciones_mapas.investigacion_dia_2 import Investigacion, objetivo
from funciones_mapas.noche_2 import Noche2
from funciones_mapas.epilogo_laboratorio import EpilogoLaboratorio
from funciones_mapas.invitados_honor import TITULO as TITULO_HONOR
from funciones_mapas.funcion_prologo import reiniciar_memoria
from mapas.dia_3 import PUEBLO


def detener_efectos_partida():
    for canal in range(1, pygame.mixer.get_num_channels()):
        pygame.mixer.Channel(canal).stop()


def abrir_menu(pantalla):
    sistema_audio.detener_musica(fade_ms=0)
    detener_efectos_partida()
    sistema_audio.reproducir_ambiente("menu")
    return MenuPrincipal(pantalla)


pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption(TITULO_JUEGO)
reloj = pygame.time.Clock()

estado_jugador = EstadoJuego()
modo_juego = "EXPLORACION"
menu = None
pausa = None

prueba_dia = "--prueba-dia-2" in sys.argv
prueba_noche = "--prueba-noche-2" in sys.argv
prueba_dia3 = "--prueba-dia-3" in sys.argv
investigacion = Investigacion(estado_jugador, autoguardar=not (prueba_dia or prueba_noche or prueba_dia3))
noche = Noche2(investigacion)
if not prueba_dia:
    investigacion.noche = noche
if prueba_dia3:
    ayudantes = {"lucas", "morales"}
    if "--sin-lucas" in sys.argv:
        ayudantes.discard("lucas")
    if "--sin-morales" in sys.argv:
        ayudantes.discard("morales")
    if not ayudantes:
        sys.exit("La prueba del día 3 necesita al menos un ayudante de la noche 2.")
    plan = "clinica" if "--clinica" in sys.argv else "oficina"
    estado_jugador.noche2.update(fase="dia3", plan_dia3=plan, dia_actual=3,
                                ayudantes=ayudantes, completada=True, morales_conoce_cartas=True)
    sistema_mapa.cargar_nivel("pueblo_1_dia_3" if plan == "clinica" else PUEBLO)
elif prueba_noche:
    from funciones_mapas.investigacion_dia_2 import PISTAS

    estado_jugador.confianza_lucas_separacion = 59 if "--sin-lucas" in sys.argv else 60
    estado_jugador.confianza_morales = 64 if "--sin-morales" in sys.argv else 65
    estado_jugador.dia2["hallazgos"].update(PISTAS)
    estado_jugador.dia2.update(cerrada=True, rama="normal")
    if "--emboscada" in sys.argv:
        investigacion.guardar_resultado()
        plan = "oficina" if "--oficina" in sys.argv and investigacion.lucas_colabora() else "clinica"
        estado_jugador.noche2.update(fase="llegada", plan_dia3=plan, cita=plan, morales_conoce_cartas=True)
        sistema_mapa.cargar_nivel("llegada_noche_2")
    else:
        sistema_mapa.cargar_nivel("hogar_dia2", 4, 6)
elif prueba_dia:
    sistema_mapa.eventos_completados.add(BUSQUEDA_DIA_2)
    if "--captura" in sys.argv or "--rescate" in sys.argv:
        estado_jugador.sospecha_pueblo = 99
        estado_jugador.confianza_morales = 65 if "--rescate" in sys.argv else 64
    sistema_mapa.cargar_nivel("pueblo_2_dia_2", 38, 15)
elif "--continuar" not in sys.argv or not sistema_guardado.continuar(estado_jugador):
    menu = abrir_menu(pantalla)

ejecutando = True
epilogo = None
salida_fin = None
guia_controles = GuiaControles()
while ejecutando:
    segundos = reloj.tick(FPS) / 1000
    # 1. GUARDAR LOS EVENTOS EN LA VARIABLE 'eventos'
    eventos = pygame.event.get()
    
    # Eventos globales (como cerrar la ventana)
    for evento in eventos:
        if evento.type == QUIT:
            ejecutando = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                pantalla = pygame.display.get_surface()
            if epilogo is not None and epilogo.terminado and evento.key == pygame.K_ESCAPE:
                sistema_guardado.pendiente = None
                menu = abrir_menu(pantalla)
                epilogo = None
                eventos = []
                break
            if (evento.key == pygame.K_ESCAPE and menu is None and pausa is None
                    and epilogo is None):
                reloj_juego.pausar()
                pygame.mixer.pause()
                pygame.mixer.music.pause()
                pausa = MenuPausa(pantalla)
                eventos = []
                break

    if not ejecutando:
        break
    if pausa is not None:
        for evento in eventos:
            accion = pausa.manejar_evento(evento)
            if accion is None:
                continue
            if accion == "reanudar":
                pygame.mixer.unpause()
                pygame.mixer.music.unpause()
                sistema_dialogo.bloqueo_espacio = True
                sistema_mapa.espacio_presionado = bool(pygame.key.get_pressed()[pygame.K_SPACE])
            elif accion == "menu":
                sistema_guardado.pendiente = None
                sistema_dialogo.cancelar_dialogo()
                menu = abrir_menu(pantalla)
            else:
                nuevo_estado = EstadoJuego()
                if not sistema_guardado.cargar(nuevo_estado, accion, desde_pausa=True):
                    pausa.error = "No se pudo cargar el último guardado."
                    break
                detener_efectos_partida()
                pygame.mixer.music.unpause()
                estado_jugador = nuevo_estado
                investigacion = Investigacion(estado_jugador)
                noche = Noche2(investigacion)
                investigacion.noche = noche
                modo_juego = "EXPLORACION"
                guia_controles = GuiaControles()
            reloj_juego.reanudar()
            pausa = None
            break
        if pausa is not None:
            pausa.dibujar(pantalla)
            pygame.display.flip()
        continue
    if menu is not None:
        for evento in eventos:
            accion = menu.manejar_evento(evento)
            if accion == "salir":
                ejecutando = False
                break
            if accion is None:
                continue

            sistema_audio.detener_musica(fade_ms=0)
            sistema_mapa.reiniciar_sesion()
            reiniciar_memoria()
            sistema_dialogo.limpiar_notificaciones()
            sistema_guardado.pendiente = None
            sistema_guardado.revision_cargada = -1
            nuevo_estado = EstadoJuego()
            if accion in ("manual", "automatico") and not sistema_guardado.cargar(nuevo_estado, accion):
                sistema_audio.reproducir_ambiente("menu")
                menu.error = "No se pudo cargar este guardado."
                break
            estado_jugador = nuevo_estado
            investigacion = Investigacion(estado_jugador)
            noche = Noche2(investigacion)
            investigacion.noche = noche
            modo_juego = "EXPLORACION"
            guia_controles = GuiaControles()
            if accion == "nueva":
                sistema_mapa.cargar_nivel("viaje")
            menu = None
            break
        if menu is not None and ejecutando:
            menu.dibujar(pantalla)
            pygame.display.flip()
        continue

    sistema_guardado.actualizar(estado_jugador)
    fase_dia3 = estado_jugador.dia3["fase"]
    if prueba_dia and noche.honor.activo:
        investigacion.noche = noche
    if noche.honor.activo and fase_dia3 == "fin_honor":
        if epilogo is None:
            epilogo = EpilogoLaboratorio(pantalla, eventos=(), fondos=(), titulo=TITULO_HONOR)
            fuente = pygame.font.Font(None, 22)
            salida_fin = fuente.render("Esc · Menú principal", True, (185, 185, 185))
        epilogo.actualizar_y_dibujar(pantalla, segundos)
        if epilogo.terminado:
            pantalla.blit(salida_fin, salida_fin.get_rect(midbottom=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 42)))
        pygame.display.flip()
        continue
    if noche.dia3.activo and fase_dia3 in ("epilogo", "fin", "epilogo_clinica", "fin_clinica"):
        es_clinica = fase_dia3 in ("epilogo_clinica", "fin_clinica")
        if epilogo is None:
            if es_clinica:
                epilogo = EpilogoLaboratorio(pantalla, eventos=(), fondos=(), titulo="Final: escape")
            else:
                epilogo = EpilogoLaboratorio(pantalla, eventos=())
            fuente = pygame.font.Font(None, 22)
            salida_fin = fuente.render("Esc · Menú principal", True, (185, 185, 185))
        epilogo.actualizar_y_dibujar(pantalla, segundos)
        if epilogo.terminado:
            estado_jugador.dia3.update(fase="fin_clinica" if es_clinica else "fin", final_completado=True)
            pantalla.blit(salida_fin, salida_fin.get_rect(midbottom=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 42)))
        pygame.display.flip()
        continue

    pantalla.fill((0, 0, 0))

    # --- MÁQUINA DE ESTADOS ---
    if modo_juego == "EXPLORACION":
        # Todo el trabajo sucio lo hace sistema_mapa
        nuevo_modo = sistema_mapa.actualizar_y_dibujar(pantalla, estado_jugador, investigacion)
        
        # Si sistema_mapa dice que pisamos un evento, cambiamos de modo
        if nuevo_modo != modo_juego:
            modo_juego = nuevo_modo

    elif modo_juego == "DIALOGO":
        
        sistema_mapa.solo_dibujar(pantalla)
        # 2. SE ELIMINÓ EL REGRESO FORZADO A EXPLORACIÓN
        # sistema_dialogo se encarga de devolver "EXPLORACION" por sí solo al terminar de leer el JSON
        modo_juego = sistema_dialogo.actualizar_y_dibujar(pantalla, eventos, estado_jugador)
        
    if not noche.honor.activo:
        rotulo = noche.objetivo() or objetivo(estado_jugador)
        if rotulo:
            sistema_dialogo.dibujar_objetivo_global(pantalla, rotulo)
        sistema_dialogo.dibujar_notificacion_global(pantalla)
    if "llegada_completada" not in sistema_mapa.eventos_completados:
        puede_moverse = (
            modo_juego == "EXPLORACION" and not sistema_mapa.transicion_activa
            and not sistema_mapa.jugador_bloqueado and not sistema_mapa.control_cinematico
        )
        guia_controles.dibujar(pantalla, sistema_mapa.nombre_mapa_actual, sistema_mapa.alpha_transicion,
                               puede_moverse=puede_moverse)
    pygame.display.flip()
pygame.quit()
