"""Comprueba las ramas del Día 3 con Pygame y guardados temporales."""
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import sistema_audio as audio
import sistema_dialogo as dialogo
import sistema_escondites as escondites
import sistema_guardado as guardado
import sistema_mapa as mapa
import sistema_vigilancia as vigilancia
from estado import EstadoJuego
from funciones_mapas.clinica_dia_3 import ESCONDITE_SERVICIO
from funciones_mapas.epilogo_laboratorio import DURACION_FONDO, DURACION_TUMBAS, EpilogoLaboratorio, FUNDIDO
from funciones_mapas.escena_morales import colocar, ruta_a
from funciones_mapas.investigacion_dia_2 import Investigacion
from funciones_mapas.invitados_honor import CAMILLA_MS
from funciones_mapas.noche_2 import Noche2
from mapas import dia_3 as niveles, tunel

TECLAS = frozenset()
TIEMPO = 0
VISITADOS = set()
MOVIMIENTO = {
    "izq": pygame.K_LEFT, "der": pygame.K_RIGHT,
    "arriba": pygame.K_UP, "abajo": pygame.K_DOWN,
}


def fotograma(juego, *teclas):
    global TIEMPO, TECLAS
    TECLAS = frozenset(teclas)
    TIEMPO += 34
    guardado.actualizar(juego.estado)
    evento = dialogo.obtener_evento_activo()
    if evento is not None:
        VISITADOS.add(evento)
        mapa.solo_dibujar(pantalla)
        dialogo._completar_evento(TIEMPO)
    else:
        mapa.actualizar_y_dibujar(pantalla, juego.estado, juego)


def avanzar(juego, hasta=lambda: True):
    for _ in range(4500):
        fotograma(juego)
        if (hasta() and not mapa.transicion_activa
                and juego.noche.dia3.revision == mapa.revision_nivel
                and dialogo.obtener_evento_activo() is None and juego.noche.dia3.director is None):
            return
    raise AssertionError((mapa.nombre_mapa_actual, juego.estado.dia3, dialogo.obtener_evento_activo()))


def cargar(juego, nivel):
    mapa.alpha_transicion = 0
    mapa.transicion_activa = False
    mapa.spawn_pendiente = None
    mapa._ejecutar_carga_real(nivel)
    avanzar(juego)


def cerca(x, y, direccion):
    colocar("mateo", x, y, direccion)


def pisar(juego, x, y, direccion, destino):
    for _ in range(9):
        fotograma(juego)
    cerca(x, y, direccion)
    fotograma(juego, MOVIMIENTO[direccion])
    assert mapa.transicion_activa or dialogo.obtener_evento_activo() is not None, (
        mapa.nombre_mapa_actual, (x, y, direccion), mapa.jugador_bloqueado,
        mapa.control_cinematico, mapa.tiempo_ultimo_paso_mateo, TIEMPO,
        (mapa.mateo_x, mapa.mateo_y), mapa.portales_activos,
    )
    avanzar(juego, lambda: mapa.nombre_mapa_actual == destino)


def interactuar(juego, x, y, direccion):
    for _ in range(18):
        fotograma(juego)
    cerca(x, y, direccion)
    fotograma(juego, pygame.K_SPACE)
    avanzar(juego)


def preparar(ayudantes, plan="oficina", rama="normal", autoguardar=False):
    estado = EstadoJuego()
    estado.dia2["rama"] = rama
    estado.noche2.update(fase="dia3", plan_dia3=plan, ayudantes=set(ayudantes), completada=True)
    juego = Investigacion(estado, autoguardar=autoguardar)
    juego.noche = Noche2(juego)
    return juego


def probar_variantes():
    for ayudantes, variante in (({"lucas"}, "lucas"), ({"morales"}, "morales"),
                               ({"lucas", "morales"}, "ambos")):
        juego = preparar(ayudantes)
        assert juego.noche.dia3.activo
        juego.estado.dia3["encuentro_oficina_revisado"] = True
        cargar(juego, niveles.IGLESIA)
        assert f"d3_reunion_ayuda_{variante}" in VISITADOS
        assert not juego.estado.dia3.get("companeros_listos")
        assert set(mapa.npcs_activos) == {"lucas", "morales"}
        assert all(npc["comportamiento"] == "estatico" for npc in mapa.npcs_activos.values())
        juego.estado.dia3.update(llave_pasadizo=True, telefono_localizado=True)
        cargar(juego, niveles.IGLESIA)
        assert all(npc["comportamiento"] == "sigue_jugador" for npc in mapa.npcs_activos.values())
        assert juego.estado.noche2["ayudantes"] == ayudantes
    assert preparar({"lucas"}, "clinica").noche.dia3.activo
    assert not preparar(set(), rama="invitados_honor").noche.dia3.activo


def probar_vision():
    escenario = SimpleNamespace(mateo_x=5, mateo_y=9, casilla_bloqueada=lambda x, y: False)
    guardia = {"x": 5, "y": 5, "direccion": "abajo", "vigilancia": {}}
    assert not vigilancia._ve_jugador(escenario, guardia)
    guardia["vigilancia"]["alcance_vision"] = 6
    assert vigilancia._ve_jugador(escenario, guardia)
    escenario.mateo_y = 3
    assert not vigilancia._ve_jugador(escenario, guardia)
    escenario.mateo_y = 4
    assert vigilancia._ve_jugador(escenario, guardia)
    escenario.mateo_y = 9
    escenario.casilla_bloqueada = lambda x, y: (x, y) == (5, 7)
    assert not vigilancia._ve_jugador(escenario, guardia)


def correr(juego, direccion):
    origen = (mapa.mateo_x, mapa.mateo_y)
    for _ in range(10):
        fotograma(juego, MOVIMIENTO[direccion], pygame.K_LSHIFT)
        if (mapa.mateo_x, mapa.mateo_y) != origen:
            assert not mapa.transicion_activa and dialogo.obtener_evento_activo() is None
            return
    raise AssertionError((origen, direccion, mapa.nombre_mapa_actual))


def probar_bosque(juego):
    assert len(mapa.npcs_activos) == 3
    guardia = mapa.npcs_activos["vigia_bosque"]
    for _ in range(niveles.ENTRADA_BOSQUE[0] - 14):
        correr(juego, "izq")
    for _ in range(22 - niveles.ENTRADA_BOSQUE[1]):
        correr(juego, "abajo")
    for _ in range(6):
        correr(juego, "izq")
    assert (mapa.mateo_x, mapa.mateo_y) == (8, 22)
    assert vigilancia.persecucion_activa
    cerca(8, 22, "izq")
    fotograma(juego, pygame.K_SPACE)
    assert escondites.escondido
    assert not any(mapa.npcs_activos[n]["visible"] for n in ("lucas", "morales"))
    for _ in range(12):
        fotograma(juego, pygame.K_SPACE)
    fotograma(juego)
    assert not escondites.escondido
    assert guardia["_vigilancia"]["estado"] == "PERSIGUIENDO"
    fotograma(juego)
    fotograma(juego, pygame.K_SPACE)
    assert escondites.escondido
    for _ in range(420):
        fotograma(juego, pygame.K_SPACE)
        if juego.estado.dia3.get("guardia_aviso"):
            break
    assert juego.estado.dia3.get("guardia_aviso")
    assert "vigia_bosque" not in mapa.npcs_activos
    assert "d3_bosque_guardia_ausente" not in VISITADOS
    fotograma(juego)
    avanzar(juego)
    assert "d3_bosque_guardia_ausente" in VISITADOS
    assert all(mapa.npcs_activos[n]["visible"] for n in ("lucas", "morales"))


def sufrir_captura(juego, nombre):
    npc = mapa.npcs_activos[nombre]
    cerca(npc["x"], npc["y"], npc["direccion"])
    fotograma(juego)
    assert mapa.transicion_activa
    avanzar(juego)


def probar_recorrido():
    juego = preparar({"lucas", "morales"}, autoguardar=True)
    cargar(juego, "pueblo_1_dia_3")
    avanzar(juego, lambda: mapa.nombre_mapa_actual == niveles.PUEBLO)
    assert (mapa.mateo_x, mapa.mateo_y) == (9, 6)
    assert ruta_a((9, 6), (38, 7))
    pisar(juego, 1, 22, "izq", niveles.PUEBLO)
    assert "d3_desvio_antes_reunion" in VISITADOS
    pisar(juego, 38, 7, "der", niveles.PLAZA)
    pisar(juego, 38, 7, "der", niveles.EXTERIOR)
    pisar(juego, 5, 5, "arriba", niveles.EXTERIOR)
    assert "d3_iglesia_primera_sin_oficina" in VISITADOS
    cerca(*niveles.ENCUENTRO, "abajo")
    avanzar(juego)
    assert juego.estado.dia3["encuentro_oficina_revisado"]
    pisar(juego, 5, 5, "arriba", niveles.IGLESIA)
    assert "d3_reunion_sin_llave" in VISITADOS
    pisar(juego, 9, 13, "abajo", niveles.EXTERIOR)
    pisar(juego, 15, 13, "arriba", niveles.OFICINA)
    assert len(mapa.npcs_activos) == 3 and 34 in mapa.imagenes_objetos
    interactuar(juego, 13, 5, "arriba")
    assert {"llave_pasadizo"} <= juego.estado.objetos_clave
    assert juego.estado.dia3["telefono_localizado"]
    assert 34 not in mapa.imagenes_objetos
    fotograma(juego)
    assert guardado._leer("automatico")["estado"]["dia3"]["telefono_localizado"]
    assert guardado.cargar(juego.estado, "automatico")
    avanzar(juego)
    assert 34 not in mapa.imagenes_objetos
    sufrir_captura(juego, "archivo_norte")
    assert (mapa.mateo_x, mapa.mateo_y) == (3, 9)
    assert juego.estado.dia3["telefono_localizado"] and 34 not in mapa.imagenes_objetos
    pisar(juego, 3, 9, "izq", niveles.EXTERIOR)
    pisar(juego, 5, 5, "arriba", niveles.IGLESIA)
    assert "d3_regreso_con_llave" in VISITADOS
    pisar(juego, 2, 1, "arriba", niveles.TUNEL)
    assert len([n for n in mapa.npcs_activos.values() if n["comportamiento"] == "vigilante"]) == 3
    interactuar(juego, *tunel.FRENTE_A_PUERTA, "arriba")
    avanzar(juego, lambda: mapa.nombre_mapa_actual == niveles.TUNEL)
    assert juego.estado.dia3["ubicacion_laboratorio_conocida"]
    assert (mapa.mateo_x, mapa.mateo_y) == tunel.FRENTE_A_PUERTA
    pisar(juego, 1, 1, "izq", niveles.IGLESIA)
    pisar(juego, 9, 13, "abajo", niveles.EXTERIOR)
    pisar(juego, 1, 7, "izq", niveles.PLAZA)
    pisar(juego, 1, 7, "izq", niveles.PUEBLO)
    VISITADOS.discard("d3_bosque_guardia_ausente")
    pisar(juego, 1, 22, "izq", niveles.BOSQUE)
    sufrir_captura(juego, "vigia_bosque")
    assert not juego.estado.dia3.get("guardia_aviso")
    assert (mapa.mateo_x, mapa.mateo_y) == niveles.ENTRADA_BOSQUE
    probar_bosque(juego)
    cargar(juego, niveles.BOSQUE)
    assert "vigia_bosque" not in mapa.npcs_activos
    interactuar(juego, 37, 23, "arriba")
    assert juego.estado.dia3["arbustos_retirados"] and mapa.nombre_mapa_actual == niveles.BOSQUE
    assert mapa.matriz_activa[22][36] == 0
    interactuar(juego, 37, 23, "arriba")
    avanzar(juego, lambda: juego.estado.dia3["fase"] == "epilogo")
    assert juego.estado.dia3["laboratorio_destruido"]
    assert juego.estado.dia3["mateo_expuesto"] and juego.estado.dia3["lucas_expuesto"]
    assert "morales" not in juego.estado.dia3["companeros_actuales"]
    assert juego.estado.dia3["llamada_confirmada"] and juego.estado.dia3["rescate_policial"]
    assert guardado._leer("automatico")["mapa"] == niveles.BOSQUE
    assert "d3_rescate_policial" in VISITADOS
    assert "d3_d3_epilogo_operativo" in VISITADOS
    assert not any(nombre.startswith("guardia_prision_") for nombre in mapa.npcs_activos)


def probar_epilogo():
    secuencia = EpilogoLaboratorio(pantalla)
    secuencia.actualizar_y_dibujar(pantalla, FUNDIDO)
    assert pantalla.get_at((5, 5))[:3] == (0, 0, 0)
    secuencia.actualizar_y_dibujar(pantalla, sum(t[1] for t in secuencia.tarjetas))
    assert secuencia.indice == len(secuencia.tarjetas)
    assert pantalla.get_at((5, 5))[:3] != (0, 0, 0)
    secuencia.actualizar_y_dibujar(pantalla, DURACION_FONDO * len(secuencia.fondos))
    assert secuencia.indice == len(secuencia.tarjetas) + len(secuencia.fondos) - 1
    secuencia.actualizar_y_dibujar(pantalla, DURACION_TUMBAS - DURACION_FONDO + FUNDIDO)
    assert secuencia.terminado


def probar_clinica():
    casos = (
        ({"lucas"}, "solo_lucas", True),
        ({"morales"}, "solo_morales", False),
        ({"lucas", "morales"}, "ambos", True),
    )
    for ayudantes, variante, llave in casos:
        VISITADOS.clear()
        juego = preparar(ayudantes, "clinica")
        if llave:
            juego.estado.dia2["resultado"] = {"ubicacion_llave": "oficina"}
        cargar(juego, "pueblo_1_dia_3")
        pisar(juego, 1, 22, "izq", niveles.CLINICA_PUEBLO)
        assert "d3_clinica_d3_desvio" in VISITADOS
        pisar(juego, 38, 7, "der", niveles.CLINICA_PLAZA)
        pisar(juego, 31, 28, "abajo", niveles.CLINICA_EXTERIOR)
        assert ruta_a((12, 1), (19, 17))
        cerca(19, 18, "arriba")
        avanzar(juego, lambda: juego.estado.dia3["fase"] == "hacia_servicio")
        assert mapa.nombre_mapa_actual == niveles.CLINICA_EXTERIOR
        assert f"d3_clinica_d3_reencuentro_{variante}" in VISITADOS
        assert "d3_clinica_d3_hacia_el_sur" in VISITADOS
        preparativos = dialogo.datos_dialogo["d3_clinica_d3_preparativos"]["lineas"]
        intencion = ("Voy a volver a la oficina a buscar esa llave" if llave
                     else "Voy a seguir buscando la llave del pasadizo")
        assert intencion in " ".join(linea["texto"] for linea in preparativos)
        assert all(mapa.npcs_activos[n]["comportamiento"] == "sigue_jugador"
                   for n in ("lucas", "morales", "ines"))
        assert ruta_a((19, 19), (12, 28))
        pisar(juego, 12, 28, "abajo", niveles.CLINICA_ACCESO)
        assert (mapa.mateo_x, mapa.mateo_y) == ESCONDITE_SERVICIO
        assert set(mapa.npcs_activos) == {"lucas", "ines"}
        ines = mapa.npcs_activos["ines"]
        assert ines["sprite_override"] is None
        assert len(ines["sprites"]) == 4
        assert all(len(cuadros) == 2 and all(cuadro.get_bounding_rect().width for cuadro in cuadros)
                   for cuadros in ines["sprites"].values())
        assert all(mapa.casilla_bloqueada(*punto) for punto in niveles.REJA)
        for _ in range(ESCONDITE_SERVICIO[0] - 9):
            correr(juego, "izq")
        for _ in range(11 - ESCONDITE_SERVICIO[1]):
            correr(juego, "abajo")
        for _ in range(500):
            fotograma(juego)
            if juego.noche.clinica.reja_abierta:
                break
        assert juego.noche.clinica.reja_abierta and mapa.control_cinematico
        assert all(mapa.casilla_bloqueada(*punto) for punto in niveles.REJA)
        for _ in range(100):
            fotograma(juego)
            if not any(mapa.casilla_bloqueada(*punto) for punto in niveles.REJA):
                break
        assert not any(mapa.casilla_bloqueada(*punto) for punto in niveles.REJA)
        assert TIEMPO - juego.noche.clinica.reja_inicio >= juego.noche.clinica.duracion_reja
        avanzar(juego, lambda: juego.estado.dia3["fase"] == "epilogo_clinica")
        assert "d3_clinica_d3_reja" in VISITADOS
        assert "d3_clinica_d3_epilogo_denuncia" in VISITADOS
        assert all(mapa.casilla_bloqueada(*punto) for punto in niveles.REJA)
        assert mapa.mateo_y == 25
        assert audio.pista_actual == "falta_uno"
        mapa.pantalla_negra_en = None


def probar_invitados_honor():
    for origen in ("dia", "noche"):
        VISITADOS.clear()
        juego = preparar(set())
        juego.estado.noche2.update(fase=None, plan_dia3=None)
        if origen == "dia":
            juego.estado.dia2["captura_pendiente"] = True
        else:
            juego.estado.noche2.update(fase="prision", captura_tipo="nocturna_definitiva")
        mapa.transicion_activa = False
        mapa.spawn_pendiente = None
        mapa._ejecutar_carga_real("prision_dia_2")
        assert not juego.noche.honor.activo
        efectos = []
        camilla_visible = False
        inicio_dialogo_final = None

        def sonido(efecto):
            assert audio.pista_actual is None
            efectos.append((efecto, TIEMPO))
            return SimpleNamespace(stop=lambda: None, get_busy=lambda: False)

        with patch("funciones_mapas.invitados_honor.sonido", side_effect=sonido):
            for _ in range(2500):
                fotograma(juego)
                evento = dialogo.obtener_evento_activo()
                if evento == "d3_honor_alvarez_llegada":
                    assert audio.pista_actual == "tension"
                    assert {"guardia_prision_oeste", "guardia_prision_este"} <= mapa.npcs_activos.keys()
                director = juego.noche.honor.director
                if not camilla_visible and director and director.accion == ("pausa", CAMILLA_MS):
                    imagen = pygame.Surface(pantalla.get_size())
                    mapa.solo_dibujar(imagen)
                    cx, cy = mapa.calcular_camara()
                    for x, y, ancho, alto in ((211, 120, 20, 35), (177, 126, 30, 37), (235, 126, 30, 37)):
                        fondo = mapa.fondo_actual.subsurface((x, y, ancho, alto))
                        frente = imagen.subsurface((x - cx, y - cy, ancho, alto))
                        assert pygame.image.tobytes(fondo, "RGB") != pygame.image.tobytes(frente, "RGB")
                    camilla_visible = True
                if evento == "d3_honor_epilogo":
                    assert audio.pista_actual == "banquete"
                    mapa.solo_dibujar(pantalla)
                    assert pantalla.get_at((400, 300))[:3] == (0, 0, 0)
                if evento == "d3_honor_nuevos_invitados":
                    inicio_dialogo_final = TIEMPO
                if juego.estado.dia3["fase"] == "fin_honor":
                    break
        assert juego.estado.dia3["origen_honor"] == origen
        assert juego.estado.dia3["final_completado"]
        assert f"d3_honor_espera_{origen}" in VISITADOS
        assert f"d3_honor_busqueda_{origen}" in VISITADOS
        assert len({evento for evento in VISITADOS if evento.startswith("d3_honor_busqueda_")}) == 1
        assert "d3_honor_nuevos_invitados" in VISITADOS
        assert camilla_visible
        assert [efecto for efecto, _ in efectos] == ["sonido_camion", "inicio_camion"]
        assert 5000 <= efectos[1][1] - efectos[0][1] <= 5100
        assert inicio_dialogo_final == efectos[1][1]
        assert mapa.nombre_mapa_actual == niveles.LAB_HONOR
        assert mapa.control_cinematico and mapa.jugador_bloqueado
        mapa.pantalla_negra_en = None


if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((800, 600))
    pygame.time.get_ticks = lambda: TIEMPO
    pygame.key.get_pressed = lambda: {tecla: tecla in TECLAS for tecla in (
        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT,
    )}
    try:
        with TemporaryDirectory() as temporal:
            guardado.CARPETA = Path(temporal)
            probar_vision()
            probar_variantes()
            probar_recorrido()
            probar_epilogo()
            probar_clinica()
            probar_invitados_honor()
        print("Día 3 validado: laboratorio, clínica e Invitados de honor.")
    finally:
        pygame.quit()
