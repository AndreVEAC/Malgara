"""Secuencia final tras una captura sin rescate."""
import json
from functools import partial
from pathlib import Path

import pygame

import sistema_audio as audio
import sistema_dialogo as dialogo
import sistema_mapa as mapa
from funciones_mapas.dia_3 import Dia3
from funciones_mapas.escena_morales import Recorrido, colocar, crear_npc, mirar, sonido
from funciones_mapas.funcion_prision_dia_2 import colocar_guardias
from mapas.dia_3 import LAB_HONOR

PRISION = "prision_dia_2"
TITULO = "Final: Invitados de honor"
CAMILLA_MS = 3800
CIERRE_OJOS_MS = 6000
GUION = json.loads((Path(__file__).resolve().parents[1] / "datos/dialogos_invitados_honor.json")
                   .read_text(encoding="utf-8"))


class FinalHonor(Dia3):
    guion = GUION

    @property
    def origen(self):
        if self.datos.get("origen_honor"):
            return self.datos["origen_honor"]
        noche = self.estado.noche2
        dia = self.estado.dia2
        if noche["fase"] == "honor" and noche.get("captura_tipo") == "nocturna_definitiva":
            return "noche"
        if dia["rama"] == "invitados_honor" and dia["captura_resuelta"] and dia["resultado"]:
            return "dia"
        return None

    @property
    def activo(self):
        return self.origen is not None

    def actualizar(self):
        if mapa.transicion_activa or dialogo.obtener_evento_activo() is not None:
            return
        if self.datos["fase"] == "fin_honor":
            return
        if self.director is None:
            self.datos["origen_honor"] = self.origen
            dialogo.limpiar_notificaciones()
            self.iniciar(self.secuencia())
        self.director.actualizar()

    def secuencia(self):
        if mapa.nombre_mapa_actual != PRISION:
            yield "hacer", partial(self.cargar, PRISION)
        colocar_guardias()
        audio.reproducir_ambiente("tension", fade_ms=0)
        mapa.ocultar_mateo = False
        yield from self.fundido_prision(hacia_negro=True)
        mapa.pantalla_negra_en = PRISION
        yield from self.decir(f"honor_espera_{self.origen}")
        colocar("mateo", 3, 4, "abajo")
        crear_npc("alvarez", "lider", 8, 7, "izq")
        mapa.pantalla_negra_en = None
        yield from self.fundido_prision(hacia_negro=False)
        yield "mover", [Recorrido("alvarez", [(3, 7), (3, 6)], 190)]
        mirar("alvarez", "arriba")
        yield from self.decir(
            "honor_alvarez_llegada", f"honor_busqueda_{self.origen}", "honor_motivos",
            "honor_descendientes", "honor_madre", "honor_banquete", "honor_ultima_respuesta",
        )

        yield from self.fundido_prision(hacia_negro=True)
        mapa.pantalla_negra_en = PRISION
        audio.detener_musica(fade_ms=0)
        yield "hacer", partial(self.cargar, LAB_HONOR)
        self.preparar_camilla()
        mapa.pantalla_negra_en = None
        mapa.script_nivel_actual.PANTALLA_NEGRA = False
        audio.reproducir_ambiente("banquete", fade_ms=0)
        yield from self.fundido_prision(hacia_negro=False)
        yield "pausa", CAMILLA_MS
        yield from self.cerrar_ojos()
        yield from self.decir("honor_epilogo")
        yield "pausa", 500
        yield from self.autobus()
        yield from self.decir("honor_nuevos_invitados")
        self.datos.update(fase="fin_honor", final_completado=True)

    def preparar_camilla(self):
        mapa.jugador_bloqueado = True
        mapa.ocultar_mateo = True
        doctor = pygame.image.load("recursos/sprites/personajes/genericos/doctor.png").convert_alpha()
        doctor_derecho = pygame.transform.flip(doctor, True, False)
        imagen = pygame.image.load("recursos/sprites/personajes/mateo/abajo_0.png").convert_alpha()
        cuerpo = pygame.transform.scale(imagen, (20, 35))

        def dibujar(pantalla, camara_x, camara_y):
            pantalla.blit(cuerpo, (211 - camara_x, 120 - camara_y))
            pantalla.blit(doctor, (177 - camara_x, 126 - camara_y))
            pantalla.blit(doctor_derecho, (235 - camara_x, 126 - camara_y))

        mapa.script_nivel_actual.dibujar_efectos = dibujar

    def cerrar_ojos(self):
        inicio = pygame.time.get_ticks()

        def dibujar(pantalla, *_):
            ancho, alto = pantalla.get_size()
            progreso = min(1, (pygame.time.get_ticks() - inicio) / CIERRE_OJOS_MS)
            superior = round(alto * 0.52 * progreso)
            inferior = round(alto * 0.48 * progreso)
            pygame.draw.rect(pantalla, (0, 0, 0), (0, 0, ancho, superior))
            pygame.draw.rect(pantalla, (0, 0, 0), (0, alto - inferior, ancho, inferior))

        mapa.script_nivel_actual.aplicar_encuadre = dibujar
        yield "pausa", CIERRE_OJOS_MS
        mapa.pantalla_negra_en = LAB_HONOR
        del mapa.script_nivel_actual.aplicar_encuadre

    def autobus(self):
        audio.detener_musica(fade_ms=0)
        marcha = sonido("sonido_camion")
        yield "pausa", 5000
        if marcha is not None:
            marcha.stop()
        sonido("inicio_camion")
