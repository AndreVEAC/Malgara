"""Verifica la noche 2 con el bucle real y guardados temporales."""
import os
import sys
from importlib import import_module
from pathlib import Path
from collections import deque
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import sistema_dialogo as dialogo
import sistema_guardado as guardado
import sistema_escondites as escondites
import sistema_mapa as mapa
import sistema_vigilancia as vigilancia
from estado import EstadoJuego
from funciones_mapas.investigacion_dia_2 import Investigacion, PISTAS
from funciones_mapas.noche_2 import Noche2, AMANECER, LLEGADA
from funciones_mapas.escena_morales import ruta_a
from funciones_mapas.escena_morales import colocar
from mapas import casa_noche_2, pueblo_2_dia_2, pueblo_2_noche_2


def avanzar(juego, hasta, decision=0):
    global tiempo
    vistos = set()
    ronda_entro = False
    for _ in range(6000):
        tiempo += 125
        evento = dialogo.obtener_evento_activo()
        if evento:
            vistos.add(evento)
            if evento == "n2_despertar_negro":
                mapa.solo_dibujar(pantalla)
                assert pantalla.get_at((400, 300))[:3] == (0, 0, 0)
            elif evento == "n2_desvio":
                assert mapa.calcular_camara() == (0, 0)
                assert (mapa.mateo_x, mapa.mateo_y) == (15, 17)
            eventos = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
            if dialogo.en_modo_decision and decision:
                eventos.insert(0, pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
            dialogo.actualizar_y_dibujar(pantalla, eventos, juego.estado)
        else:
            mapa.actualizar_y_dibujar(pantalla, juego.estado, juego)
            if "ronda_1" in mapa.npcs_activos and not ronda_entro:
                ronda_entro = True
                assert mapa.ocultar_mateo
                assert all(mapa.npcs_activos[n]["x"] < 0 for n in ("ronda_1", "ronda_2"))
        if juego.estado.noche2["fase"] == hasta:
            return vistos
    raise AssertionError((mapa.nombre_mapa_actual, juego.estado.noche2, juego.noche.director.accion))


def cargar(nombre, spawn=None):
    mapa.transicion_activa = False
    mapa.alpha_transicion = 0
    mapa.spawn_pendiente = spawn
    mapa._ejecutar_carga_real(nombre)


def partida(lucas, morales, oficina, rescate=False):
    dialogo.limpiar_notificaciones()
    estado = EstadoJuego()
    estado.confianza_lucas_separacion = 60 if lucas else 59
    estado.confianza_morales = 65 if morales else 64
    estado.dia2.update(cerrada=True, rama="rescate" if rescate else "normal")
    estado.dia2["hallazgos"].update(PISTAS)
    juego = Investigacion(estado, autoguardar=False)
    juego.noche = Noche2(juego)
    cargar("hogar_dia2", (4, 6))
    vistos = avanzar(juego, "sigilo", int(oficina))
    assert {"n2_confesion_cartas", "n2_despertar_negro", "n2_despertar_visible", "n2_desvio"} <= vistos
    assert juego.estado.noche2["morales_conoce_cartas"]
    assert juego.estado.noche2["plan_dia3"] == ("oficina" if oficina else "clinica")
    assert ("n2_elegir_destino" in vistos) == lucas
    assert not estado.objetos_clave
    assert {"lucas", "morales"} <= mapa.npcs_activos.keys()
    assert mapa.calcular_camara()[1] > 0
    assert {(npc["x"], npc["y"]) for nombre, npc in mapa.npcs_activos.items()
            if nombre.startswith("loco_norte_")} == set(casa_noche_2.GUARDIAS_CAMINO_NORTE)
    assert all(mapa.casilla_bloqueada(x, casa_noche_2.LIMITE_CAMINO_NORTE)
               for x in range(mapa.columnas_mapa))
    assert all(mapa.matriz_activa[y][x] == 20 for x, y in casa_noche_2.POSTES)
    assert len(mapa.script_nivel_actual.obtener_zonas_iluminadas()) == len(casa_noche_2.POSTES) == 3
    assert all(npc["vigilancia"]["luz"] in vigilancia._luces
               for nombre, npc in mapa.npcs_activos.items() if nombre.startswith("loco_norte_"))
    cargar(LLEGADA)
    vistos = avanzar(juego, "dia3" if lucas or morales else "honor")
    assert estado.noche2["ayudantes"] == {n for n, ayuda in (("lucas", lucas), ("morales", morales)) if ayuda}
    if lucas or morales:
        assert "n2_amanecer" in vistos
        assert mapa.nombre_mapa_actual == AMANECER
        assert not mapa.npcs_activos and not mapa.ocultar_mateo
        assert not mapa.jugador_bloqueado and not mapa.control_cinematico
        guardar_y_cargar(juego)
        juego.actualizar()
        assert juego.estado.noche2["fase"] == "dia3"
        assert dialogo.obtener_evento_activo() is None
    else:
        assert "n2_prision_cierre" in vistos
        assert ("n2_prision_reincidente" in vistos) == rescate
        assert estado.noche2["captura_tipo"] == "nocturna_definitiva"
        assert mapa.casilla_bloqueada(4, 5)


def guardar_y_cargar(juego):
    original = guardado.CARPETA
    with TemporaryDirectory() as temporal:
        guardado.CARPETA = Path(temporal)
        try:
            guardado.guardar(juego.estado, "manual")
            assert guardado.cargar(juego.estado, "manual")
        finally:
            guardado.CARPETA = original


def camino_seguro(origen, portal):
    peligros = set()
    posiciones = []
    for npc in vigilancia._vigilantes(mapa):
        punto = (npc["x"], npc["y"])
        ruta = npc["vigilancia"]["ruta"]
        miradas = [dir for dir, _ in npc["vigilancia"]["miradas"]]
        if ruta:
            for destino in (*ruta, punto):
                posiciones.extend((celda, ("arriba", "abajo", "izq", "der"))
                                  for celda in [punto, *ruta_a(punto, destino)])
                punto = destino
        else:
            posiciones.append((punto, miradas or [npc["direccion"]]))
    for y in range(mapa.filas_mapa):
        for x in range(mapa.columnas_mapa):
            mapa.mateo_x, mapa.mateo_y = x, y
            mapa.mateo_px_x, mapa.mateo_px_y = x * 40, y * 40
            if vigilancia._en_luz(mapa) or any(
                abs(gx - x) <= 3 and abs(gy - y) <= 3
                and any(vigilancia._ve_jugador(mapa, dict(x=gx, y=gy, direccion=dir)) for dir in miradas)
                for (gx, gy), miradas in posiciones
            ):
                peligros.add((x, y))

    assert origen not in peligros, (mapa.nombre_mapa_actual, origen, "entrada expuesta")
    vistos = {origen}
    cola = deque([(origen, 0)])
    while cola:
        (x, y), pasos = cola.popleft()
        if mapa.matriz_activa[y][x] == portal:
            return pasos
        for a, b in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (a, b) in vistos or (a, b) in peligros or mapa.casilla_bloqueada(a, b):
                continue
            if mapa.matriz_activa[b][a] in mapa.portales_activos and mapa.matriz_activa[b][a] != portal:
                continue
            vistos.add((a, b))
            cola.append(((a, b), pasos + 1))
    raise AssertionError((mapa.nombre_mapa_actual, origen, portal, len(vistos)))


def prueba_rodeo():
    mapa.control_cinematico = False
    for nivel, entrada, portal in (
        ("casa_noche_2", (casa_noche_2.INICIO_X, casa_noche_2.INICIO_Y), 98),
        ("pueblo_3_noche_2", (1, 18), 98),
        ("pueblo_2_noche_2", (31, 28), 97),
        ("pueblo_1_noche_2", (38, 22), 97),
    ):
        cargar(nivel, entrada)
        camino_seguro(entrada, portal)
        conexiones = dict(mapa.portales_activos)
        for enlace in conexiones.values():
            destino = enlace["mapa"]
            punto = (enlace["spawn_x"], enlace["spawn_y"])
            cargar(destino, punto)
            assert not mapa.casilla_bloqueada(*punto), (nivel, destino, punto)
            assert mapa.matriz_activa[punto[1]][punto[0]] not in mapa.portales_activos
            modulo = import_module(f"mapas.{destino}")
            assert Path(modulo.FONDO_IMG).is_file()
    cargar("pueblo_1_noche_2", (38, 7))
    camino_seguro((38, 7), 97)
    assert all(mapa.matriz_activa[y][0] == 22 and mapa.casilla_bloqueada(0, y)
               for y in (21, 22, 23))
    postes = lambda matriz: {(x, y) for y, fila in enumerate(matriz)
                             for x, celda in enumerate(fila) if celda == 20}
    assert postes(pueblo_2_noche_2.MATRIZ) == postes(pueblo_2_dia_2.MATRIZ)


def prueba_reinicio_y_barril():
    global tiempo
    estado = EstadoJuego()
    estado.noche2.update(fase="sigilo", plan_dia3="clinica")
    juego = Investigacion(estado, autoguardar=False)
    juego.noche = Noche2(juego)
    entrada = (38, 7)
    cargar("pueblo_1_noche_2", entrada)
    juego.actualizar()
    colocar("mateo", 17, 7, "izq")
    assert vigilancia._en_luz(mapa)
    guardias = vigilancia._vigilantes(mapa)
    vigilancia.actualizar(tiempo)
    assert all(npc["_vigilancia"]["estado"] == "PERSIGUIENDO" for npc in guardias)
    assert vigilancia.persecucion_activa
    colocar("mateo", 9, 6, "arriba")
    assert (9, 5) in escondites.barriles
    escondites._entrar(mapa)
    vigilancia.actualizar(tiempo)
    assert all(npc["_vigilancia"]["estado"] == "ESPERANDO" for npc in guardias)
    assert all(not mapa.npcs_activos[n]["visible"] for n in ("lucas", "morales"))
    tiempo += 5001
    vigilancia.actualizar(tiempo)
    assert not any(npc["_vigilancia"]["estado"] == "PERSIGUIENDO" for npc in guardias)
    escondites._salir(mapa)
    assert all(mapa.npcs_activos[n]["visible"] for n in ("lucas", "morales"))
    colocar("mateo", 12, 7, "der")
    guardar_y_cargar(juego)
    juego.actualizar()
    assert mapa.reinicio_entrada == entrada
    for _ in range(20):
        mapa.actualizar_y_dibujar(pantalla, estado, juego)
    nombre = next(n for n, npc in mapa.npcs_activos.items() if npc["comportamiento"] == "vigilante")
    colocar(nombre, mapa.mateo_x, mapa.mateo_y, "izq")
    mapa.npcs_activos[nombre]["_vigilancia"]["estado"] = "PERSIGUIENDO"
    vigilancia.actualizar(tiempo)
    assert mapa.transicion_activa and mapa.spawn_pendiente == entrada
    for _ in range(40):
        mapa.actualizar_y_dibujar(pantalla, estado, juego)
    assert (mapa.mateo_x, mapa.mateo_y) == entrada
    assert estado.noche2["plan_dia3"] == "clinica"
    assert not vigilancia.persecucion_activa


if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((800, 600))
    tiempo = 0
    pygame.time.get_ticks = lambda: tiempo
    prueba_rodeo()
    prueba_reinicio_y_barril()
    for lucas, morales, oficina, rescate in (
        (True, True, True, False), (True, True, False, True),
        (True, False, True, False), (True, False, False, False),
        (False, True, False, False), (False, False, False, False),
        (False, False, False, True),
    ):
        partida(lucas, morales, oficina, rescate)
    print("Noche 2: planes, confesión, despertar, emboscada, prisión y amanecer verificados.")
