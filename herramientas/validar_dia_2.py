"""Pruebas del motor diurno con Pygame a 800 × 600 y guardados temporales."""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from collections import deque

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import sistema_dialogo as dialogo
import sistema_guardado as guardado
import sistema_mapa as mapa
from estado import BUSQUEDA_DIA_2, EstadoJuego
from funciones_mapas import investigacion_dia_2 as dia
from funciones_mapas import funcion_prision_dia_2 as prision


def cargar(nombre, x=None, y=None):
    mapa.transicion_activa = False
    mapa.alpha_transicion = 0
    mapa.spawn_pendiente = (x, y) if x is not None else None
    mapa._ejecutar_carga_real(nombre)


def pulsar(tecla):
    eventos = [pygame.event.Event(pygame.KEYDOWN, key=tecla)]
    return dialogo.actualizar_y_dibujar(pantalla, eventos, juego.estado)


def leer():
    evento = dialogo.obtener_evento_activo()
    for _ in range(100):
        if dialogo.obtener_evento_activo() != evento or dialogo.en_modo_decision:
            return
        if not dialogo.evento_actual["lineas"]:
            dialogo.actualizar_y_dibujar(pantalla, [], juego.estado)
        else:
            pulsar(pygame.K_SPACE)
    raise AssertionError(evento)


def elegir(indice):
    for _ in range(10):
        if dialogo.en_modo_decision:
            break
        assert dialogo.obtener_evento_activo() is not None
        leer()
    assert dialogo.en_modo_decision
    for _ in range(indice):
        pulsar(pygame.K_DOWN)
    pulsar(pygame.K_SPACE)


def nuevo():
    global juego
    dialogo.evento_actual = dialogo.nombre_evento_activo = None
    mapa.eventos_completados.clear()
    mapa.eventos_completados.add(BUSQUEDA_DIA_2)
    juego = dia.Investigacion(EstadoJuego(), autoguardar=False)
    return juego


def dar_respuesta(persona, indice=0):
    juego.personaje(persona)
    elegir(indice)
    leer()


def prueba_pistas():
    for invertido in (False, True):
        nuevo()
        cargar(dia.CASA_ABUELA)
        dar_respuesta("abuela", 2)
        assert "abuela_pregunta_3_temprana" in juego.datos["consumidos"]
        assert "abuela_pregunta_3" not in juego.datos["consumidos"]
        if invertido:
            cargar(dia.CUARTO)
            juego.interactuar(1, 2, "cajon_inventario")
            leer()
            assert juego.datos["hallazgos"] == {"caja_jm"}
            juego.informar("marca_media_luna")
            assert dialogo.obtener_evento_activo() == "cajon_correspondencia"
        dar_respuesta("ines", 2)
        dar_respuesta("anciano", 1)
        dar_respuesta("abuela", 2)
        assert "abuela_pregunta_3" in juego.datos["consumidos"]
        if not invertido:
            cargar(dia.CUARTO)
            juego.interactuar(1, 2, "cajon_inventario")
            leer()
        assert dia.PISTAS <= juego.datos["hallazgos"]
        assert len(juego.datos["personas"]) == 3
        assert juego.estado.sospecha_pueblo == 5
        juego.informar("caja_jm")
        leer()
        assert juego.estado.confianza_morales == 57
        assert dialogo.obtener_evento_activo() == "morales_temas"
        juego.informar("marca_media_luna")
        leer()
        leer()
        assert dialogo.obtener_evento_activo() == "morales_caja_marca"
        leer()
        assert juego.estado.confianza_morales == 64
        juego.informar("caja_jm")
        assert juego.estado.confianza_morales == 64


def avanzar_escena():
    global tiempo
    vistos = set()
    for _ in range(1500):
        tiempo += 120
        if dialogo.obtener_evento_activo() is not None:
            vistos.add(dialogo.obtener_evento_activo())
            leer()
        else:
            mapa.actualizar_y_dibujar(pantalla, juego.estado, juego)
        if juego.datos["resultado"]:
            return vistos
    raise AssertionError((mapa.nombre_mapa_actual, juego.datos))


def prueba_cierre():
    nuevo()
    cargar(dia.HOGAR)
    for persona in ("vecino", "panadero", "amargado", "fotografias"):
        juego.aplicar(persona, {"registrar_personaje": persona})
    juego.interactuar(2, 3, None)
    assert dialogo.obtener_evento_activo() == "sillon_antes_cinco"
    leer()
    juego.aplicar("nina", {"registrar_personaje": "nina"})
    cargar(dia.ENTRADA)
    juego.actualizar()
    assert not juego.datos["abuela_salio"]
    cargar(dia.CASA_ABUELA)
    juego.personaje("abuela")
    elegir(3)
    leer()
    juego.actualizar()
    assert not juego.datos["abuela_salio"]
    cargar(dia.ENTRADA)
    juego.actualizar()
    assert juego.datos["abuela_salio"]
    cargar(dia.HOGAR)
    juego.interactuar(2, 3, None)
    elegir(0)
    elegir(1)
    assert not juego.datos["cerrada"]
    juego.interactuar(2, 3, None)
    elegir(0)
    elegir(0)
    juego.actualizar()
    juego.actualizar()
    lucas = mapa.npcs_activos["lucas"]
    assert (lucas["x"], lucas["y"]) == dia.PUERTA_EXTERIOR
    assert dialogo.obtener_evento_activo() is None
    avanzar_escena()
    assert juego.datos["reencuentro"]
    assert juego.datos["resultado"]["pistas"] == set()
    assert "lucas" in mapa.npcs_activos
    assert (lucas["x"], lucas["y"]) == dia.DESTINO_LUCAS


def prueba_captura():
    for confianza in (64, 65):
        nuevo()
        cargar(dia.PLAZA, 38, 15)
        juego.estado.confianza_morales = confianza
        juego.estado.sospecha_pueblo = 39
        juego.aplicar("umbral40", {"sospecha_pueblo": 1})
        assert "aviso_sospecha_40" in juego.datos["consumidos"]
        juego.estado.sospecha_pueblo = 69
        juego.aplicar("umbral70", {"sospecha_pueblo": 1})
        assert "aviso_sospecha_70" in juego.datos["consumidos"]
        juego.estado.sospecha_pueblo = 99
        juego.datos["personas"].update(("vecino", "panadero", "ines", "fotografias"))
        juego.datos["hallazgos"].add("marca_media_luna")
        dar_respuesta("anciano", 2)
        assert len(juego.datos["personas"]) == 5
        assert juego.datos["captura_pendiente"] and mapa.jugador_bloqueado
        assert dialogo.obtener_evento_activo() is None
        assert juego.datos["rescate_elegible"] == (confianza == 65)
        with TemporaryDirectory() as carpeta:
            original = guardado.CARPETA
            guardado.CARPETA = Path(carpeta)
            try:
                guardado.guardar(juego.estado, "manual")
                assert guardado.cargar(juego.estado, "manual")
            finally:
                guardado.CARPETA = original
        assert juego.datos["captura_pendiente"]
        assert list(dia.rutas_guardias())
        avanzar_escena()
        assert not juego.datos["captura_pendiente"]
        assert juego.datos["captura_resuelta"]
        assert juego.datos["resultado"]["pistas"] == {"marca_media_luna"}
        assert juego.datos["rama"] == ("rescate" if confianza == 65 else "invitados_honor")


def prueba_lucas():
    casos = (
        (59, set(), {"lucas_sin_caja_baja"}),
        (60, {"marca_media_luna"}, {"lucas_sin_caja"}),
        (59, dia.PISTAS, {"lucas_caja_confianza_baja"}),
        (60, {"caja_jm"}, {"lucas_caja_confianza_alta", "lucas_pistas_incompletas"}),
        (60, dia.PISTAS, {"lucas_caja_confianza_alta", "lucas_tres_pistas"}),
    )
    for confianza, pistas, esperados in casos:
        nuevo()
        cargar(dia.HOGAR)
        juego.estado.confianza_lucas_separacion = confianza
        juego.estado.confianza_lucas = 100 - confianza
        juego.datos["hallazgos"].update(pistas)
        juego.cerrar("normal")
        vistos = avanzar_escena()
        assert {evento for evento in vistos if evento.startswith("lucas_")} == esperados
        assert juego.datos["resultado"]["plan_llave"] == (confianza >= 60 and pistas == dia.PISTAS)
        assert juego.estado.objetos_clave == set()


def alcanzables():
    origen = (mapa.mateo_x, mapa.mateo_y)
    pendientes = deque([origen])
    vistos = {origen}
    while pendientes:
        x, y = pendientes.popleft()
        for a, b in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if (a, b) in vistos or mapa.casilla_bloqueada(a, b):
                continue
            if mapa.matriz_activa[b][a] in mapa.portales_activos:
                continue
            vistos.add((a, b))
            pendientes.append((a, b))
    return vistos


def prueba_mapas():
    nuevo()
    for nivel, puntos in dia.PUNTOS.items():
        cargar(nivel)
        vistos = alcanzables()
        for x, y in puntos:
            assert any(vecino in vistos for vecino in
                       ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))), (nivel, x, y)
    cargar(dia.PRISION)
    mapa.solo_dibujar(pantalla)
    assert all(mapa.casilla_bloqueada(x, 5) for x in range(10))
    assert all(sprite.get_size() == (400, 120) and sprite.get_at((35, 70)).a == 0
               for sprite in prision.barrotes.values())
    prision.abrir()
    mapa.solo_dibujar(pantalla)
    assert [x for x in range(10) if not mapa.casilla_bloqueada(x, 5)] == [4]

    # En una celda estrecha no hay destinos para guardias, pero la escena continúa.
    mapa.mateo_x, mapa.mateo_y = 0, 0
    assert list(dia.rutas_guardias()) == []

    cargar("pueblo_1_noche_1")
    mapa.eventos_completados.discard(BUSQUEDA_DIA_2)
    juego.actualizar()
    assert juego.director is None
    assert any(npc["comportamiento"] == "vigilante" for npc in mapa.npcs_activos.values())


def prueba_interaccion_y_avisos():
    global tiempo
    nuevo()
    dialogo.limpiar_notificaciones()
    cargar(dia.PLAZA)
    juego.actualizar()
    assert "morales" not in mapa.npcs_activos
    leer()
    assert juego.interactuar(3, 4, None)
    assert dialogo.obtener_evento_activo() == "preparativos_sur_inicio"
    assert dialogo.evento_actual["lineas"][0]["hablante"] == "Mujer organizadora"
    assert juego.interactuar(31, 24, None)
    assert dialogo.obtener_evento_activo() == "amargado_inicio"
    cargar(dia.IGLESIA)
    assert mapa.npcs_activos["morales"]["visible"]
    assert not mapa.jugador_bloqueado
    assert juego.interactuar(*dia.ESCONDITE_MORALES, None)
    assert dialogo.obtener_evento_activo() == "morales_inicio"
    juego.aplicar("subida", {"sospecha_pueblo": 1})
    juego.aplicar("confianza", {"confianza_morales": 1})
    assert dialogo.texto_notificacion == "Sospechan más de ti"
    assert dialogo.fondo_notificacion == dia.FONDO_SOSPECHA
    tiempo += 3999
    dialogo.dibujar_notificacion_global(pantalla)
    assert dialogo.texto_notificacion == "Sospechan más de ti"
    tiempo += 1
    dialogo.dibujar_notificacion_global(pantalla)
    assert dialogo.texto_notificacion == "Morales confía más en ti"
    assert tuple(dialogo.fondo_notificacion) == (65, 111, 162)
    tiempo += 4000
    dialogo.dibujar_notificacion_global(pantalla)
    assert not dialogo.texto_notificacion


if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((800, 600))
    tiempo = 2000
    pygame.time.get_ticks = lambda: tiempo
    assert len(dia.GUION["personajes"]) == 11
    assert all(len(persona["preguntas"]) == 3 for persona in dia.GUION["personajes"].values())
    prueba_mapas()
    prueba_pistas()
    prueba_cierre()
    prueba_captura()
    prueba_lucas()
    prueba_interaccion_y_avisos()
    pygame.quit()
    print("Día 2: mapas, diálogos, guardado, cierre, captura y rescate verificados.")
