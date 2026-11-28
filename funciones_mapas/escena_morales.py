"""Herramientas de movimiento y secuencias para las cinemáticas."""
from collections import deque

import pygame
import sistema_mapa as mapa
import sistema_dialogo as dialogo
from configuracion import TAMANO_CASILLA as T

MARCA_TENSION = 'morales_noche_1:tension'
MARCA_REGRESO = 'morales_noche_1:regreso_pendiente'
MARCA_HOGAR = 'morales_noche_1:en_hogar'


def crear_npc(nombre, carpeta, x, y, direccion='abajo', visible=True):
    mapa.npcs_activos[nombre] = dict(
        x=x, y=y, px_x=float(x*T), px_y=float(y*T),
        direccion=direccion, visible=visible, sprites=mapa.cargar_sprites_personaje(carpeta) if carpeta else {},
        comportamiento='estatico', sprite_override=None, sprites_especiales={},
        seguimiento={}, vigilancia={}, patrulla={}, pausado=True, congelado=False)


def posicion(nombre):
    if nombre == 'mateo':
        return mapa.mateo_x, mapa.mateo_y, mapa.mateo_px_x, mapa.mateo_px_y
    n = mapa.npcs_activos[nombre]
    return n['x'], n['y'], n['px_x'], n['px_y']


def mirar(nombre, direccion):
    if nombre == 'mateo': mapa.direccion_mateo = direccion
    else: mapa.npcs_activos[nombre]['direccion'] = direccion


def colocar(nombre, x, y, direccion):
    if nombre == 'mateo':
        mapa.mateo_x, mapa.mateo_y = x, y
        mapa.mateo_px_x, mapa.mateo_px_y = float(x*T), float(y*T)
    else:
        mapa.npcs_activos[nombre].update(x=x, y=y, px_x=float(x*T), px_y=float(y*T))
    mirar(nombre, direccion)


def sonido(nombre):
    try:
        efecto = pygame.mixer.Sound('recursos/sonidos/efectos/'+nombre+'.wav')
        canal = efecto.play()
        return canal
    except (pygame.error, FileNotFoundError) as e:
        print('[Morales] No se pudo reproducir el efecto:', e)


class Recorrido:
    """Waypoints explícitos: la cinemática no activa portales ni pathfinding."""
    def __init__(self, nombre, puntos, intervalo=250, retraso=0, al_llegar=None):
        self.nombre, self.puntos = nombre, list(puntos)
        self.intervalo, self.retraso = intervalo, retraso
        self.siguiente = None
        self.al_llegar = al_llegar

    def actualizar(self, ahora):
        if self.siguiente is None: self.siguiente = ahora + self.retraso
        x, y, px, py = posicion(self.nombre)
        while self.puntos and (x, y) == tuple(self.puntos[0]): self.puntos.pop(0)
        if not self.puntos:
            llego = abs(px-x*T) < .75 and abs(py-y*T) < .75
            if llego and self.al_llegar is not None:
                self.al_llegar()
                self.al_llegar = None
            return llego
        if ahora < self.siguiente: return False
        tx, ty = self.puntos[0]
        dx = (tx>x)-(tx<x)
        dy = 0 if dx else (ty>y)-(ty<y)
        mirar(self.nombre, ('der' if dx>0 else 'izq') if dx else ('abajo' if dy>0 else 'arriba'))
        if self.nombre == 'mateo': mapa.mateo_x, mapa.mateo_y = x+dx, y+dy
        else:
            mapa.npcs_activos[self.nombre].update(x=x+dx, y=y+dy, congelado=False)
        self.siguiente = ahora+self.intervalo
        return False


def ruta_a(origen, destino):
    """Buscar una ruta por casillas. El último paso puede ser una puerta."""
    pendientes = deque([origen])
    padres = {origen: None}
    while pendientes:
        x, y = actual = pendientes.popleft()
        if actual == destino:
            ruta = []
            while actual != origen:
                ruta.append(actual)
                actual = padres[actual]
            return ruta[::-1]
        for vecino in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if vecino in padres:
                continue
            if vecino != destino and mapa.casilla_bloqueada(*vecino):
                continue
            padres[vecino] = actual
            pendientes.append(vecino)

    raise ValueError(f"No hay ruta de cinemática entre {origen} y {destino}")


class Director:
    def __init__(self, secuencia):
        self.secuencia = iter(secuencia)
        self.accion = None
        self.inicio = None
        self.terminado = False

    def actualizar(self):
        if self.terminado or mapa.transicion_activa or dialogo.obtener_evento_activo() is not None:
            return
        ahora = pygame.time.get_ticks()
        if self.accion is None:
            try: self.accion = next(self.secuencia)
            except StopIteration:
                self.terminado = True
                return
            self.inicio = ahora
        tipo, valor = self.accion
        listo = False
        if tipo == 'pausa': listo = ahora-self.inicio >= valor
        elif tipo == 'esperar': listo = not valor()
        elif tipo == 'dialogo':
            if valor not in dialogo.datos_dialogo:
                raise KeyError('Falta el diálogo de la escena: '+valor)
            dialogo.iniciar_dialogo(valor)
            listo = True
        elif tipo == 'mover':
            # Evaluar TODOS, sin cortocircuitar el movimiento de los siguientes.
            listo = all([r.actualizar(ahora) for r in valor])
        elif tipo == 'hacer':
            valor()
            listo = True
        if listo: self.accion = None


def cargar_linternas():
    base = pygame.image.load('recursos/sprites/efectos/luz_3.png').convert_alpha()
    base = pygame.transform.scale(base, (120, 120))
    return {d: pygame.transform.rotate(base, a) for d, a in
            [('arriba',0), ('abajo',180), ('izq',90), ('der',-90)]}


def linterna(pantalla, luces, nombre, cx, cy):
    n = mapa.npcs_activos[nombre]
    if not n['visible']: return
    x, y = n['px_x']+T/2, n['px_y']+T/2
    img = luces[n['direccion']]
    if n['direccion'] == 'arriba': rect = img.get_rect(midbottom=(round(x),round(y)))
    elif n['direccion'] == 'abajo': rect = img.get_rect(midtop=(round(x),round(y)))
    elif n['direccion'] == 'izq': rect = img.get_rect(midright=(round(x),round(y)))
    else: rect = img.get_rect(midleft=(round(x),round(y)))
    pantalla.blit(img, rect.move(-cx,-cy))
