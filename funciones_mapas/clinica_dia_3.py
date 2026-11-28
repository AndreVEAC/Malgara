"""Rama del Día 3 que termina en el acceso de servicio."""
import json
from functools import partial
from pathlib import Path

import pygame

import sistema_dialogo as dialogo
import sistema_mapa as mapa
from funciones_mapas.dia_3 import Dia3
from funciones_mapas.escena_morales import Recorrido, crear_npc, mirar, posicion, sonido
from funciones_mapas.investigacion_dia_2 import PISTAS
from mapas import dia_3 as niveles
from mapas.geografia_noche_2 import marcar

GUION = json.loads(Path("datos/dialogos_clinica_dia_3.json").read_text(encoding="utf-8"))
PREPARATIVOS = "clinica_d3_preparativos"
FRENTE_CLINICA = (19, 17)
ACOMPANANTES = ("lucas", "morales", "ines")
SPRITES = {"lucas": "lucas", "morales": "morales", "ines": "abuela"}
TIEMPO_REJA = 650


class ClinicaDia3(Dia3):
    guion = GUION

    @property
    def activo(self):
        noche = self.estado.noche2
        return (noche["fase"] == "dia3" and noche["plan_dia3"] == "clinica"
                and bool(self.ayudantes) and self.estado.dia2["rama"] != "invitados_honor")

    @property
    def llave_localizada(self):
        resultado = self.estado.dia2.get("resultado") or {}
        return (resultado.get("ubicacion_llave") == "oficina"
                or (resultado.get("lucas_colabora") and PISTAS <= set(resultado.get("pistas", ()))))

    def objetivo(self):
        if self.director:
            return None
        actual = mapa.nombre_mapa_actual
        if actual == niveles.CLINICA_ACCESO:
            return "Baja por el camino hasta el portón"
        if self.datos["fase"] == "hacia_servicio":
            return "Busca el acceso de servicio al sur de la clínica"
        return "Reúnete con Lucas y Morales en la clínica"

    def interactuar(self, x, y):
        return False

    def interceptar_portal(self, destino):
        if not self.activo:
            return False
        hacia_servicio = self.datos["fase"] == "hacia_servicio"
        bloqueado = (
            destino in (niveles.CLINICA_DESVIO, niveles.CLINICA_INTERIOR)
            or (destino == niveles.CLINICA_ACCESO and not hacia_servicio)
            or (destino == niveles.CLINICA_PLAZA and hacia_servicio)
        )
        if bloqueado:
            evento = "clinica_d3_hacia_el_sur" if hacia_servicio else "clinica_d3_desvio"
            self.aviso(evento)
        return bloqueado

    def poner_grupo(self, **puntos):
        for nombre, (x, y) in puntos.items():
            crear_npc(nombre, SPRITES[nombre], x, y)

    def activar_seguidores(self, nombres):
        for nombre in nombres:
            if nombre not in mapa.npcs_activos:
                self.poner_grupo(**{nombre: posicion("mateo")[:2]})
            mapa.npcs_activos[nombre].update(comportamiento="sigue_jugador", pausado=False,
                                            seguimiento={"velocidad_ms": 170})
        mapa.colocar_seguidores_cerca()

    def configurar(self, actual):
        nivel = niveles.CLINICA_NIVELES[actual]
        mapa.reinicio_entrada = posicion("mateo")[:2]
        if self.director:
            mapa.jugador_bloqueado = True
        if actual == niveles.CLINICA_PUEBLO:
            self.iniciar_cartel("clinica_d3_objetivo")
        elif actual == niveles.CLINICA_EXTERIOR:
            if self.datos["fase"] == "hacia_servicio":
                if self.director:
                    self.poner_grupo(lucas=(18, 17), morales=(20, 17), ines=(19, 18))
                else:
                    self.activar_seguidores(ACOMPANANTES)
            else:
                self.poner_grupo(lucas=(17, 17), morales=(21, 17))
                for nombre in ("lucas", "morales"):
                    mapa.npcs_activos[nombre]["visible"] = False
        elif actual == niveles.CLINICA_INTERIOR:
            self.poner_grupo(lucas=(2, 3), morales=(0, 3), ines=(5, 4))
            if not self.director:
                self.iniciar(self.conversacion())
        elif actual == niveles.CLINICA_ACCESO:
            mapa.reinicio_entrada = (nivel.INICIO_X, nivel.INICIO_Y)
            self.reja = pygame.image.load("recursos/sprites/objetos/puerta_desliza.png").convert_alpha()
            self.reja_inicio = None
            self.reja_abierta = False
            mapa.script_nivel_actual.dibujar_efectos = self.dibujar_reja
            if self.datos["fase"] == "escape_clinica":
                self.activar_seguidores(("lucas", "ines"))
            else:
                self.poner_grupo(lucas=(10, 1), morales=(8, 1), ines=(9, 2))
                self.iniciar(self.distraccion())

    def actualizar(self):
        actual = mapa.nombre_mapa_actual
        if actual == "pueblo_1_dia_3":
            if not mapa.transicion_activa:
                mapa.ocultar_mateo = False
                self.cargar(niveles.CLINICA_PUEBLO, *posicion("mateo")[:2])
            return
        if actual not in niveles.CLINICA_NIVELES:
            return
        if self.revision != mapa.revision_nivel:
            self.revision = mapa.revision_nivel
            self.configurar(actual)
        if mapa.transicion_activa or dialogo.obtener_evento_activo() is not None:
            return
        if self.director:
            self.director.actualizar()
            if self.director.terminado:
                self.director = None
                mapa.control_cinematico = mapa.jugador_bloqueado = False
            return
        x, y = posicion("mateo")[:2]
        if (actual == niveles.CLINICA_EXTERIOR and self.datos["fase"] == "recorrido"
                and abs(x - FRENTE_CLINICA[0]) + abs(y - FRENTE_CLINICA[1]) <= 2):
            self.iniciar(self.reencuentro())
        elif actual == niveles.CLINICA_ACCESO and y == 11 and 8 <= x <= 11:
            self.iniciar(self.cruce())

    def reencuentro(self):
        for nombre in ("lucas", "morales"):
            mapa.npcs_activos[nombre]["visible"] = True
        variante = "ambos" if len(self.ayudantes) == 2 else f"solo_{next(iter(self.ayudantes))}"
        yield from self.decir("clinica_d3_reencuentro", f"clinica_d3_reencuentro_{variante}")
        yield "mover", [self.caminar("mateo", niveles.PUERTA_CLINICA),
                        self.caminar("lucas", (18, 17)), self.caminar("morales", (20, 17))]
        yield "hacer", partial(sonido, "open_door")
        self.datos["fase"] = "conversacion_clinica"
        yield "hacer", partial(self.cargar, niveles.CLINICA_INTERIOR)
        yield from self.conversacion()

    def conversacion(self):
        yield "mover", [self.caminar("mateo", (4, 5)), self.caminar("lucas", (3, 5)),
                        self.caminar("morales", (5, 5))]
        yield from self.decir(*(f"clinica_d3_{evento}" for evento in (
            "entrada", "cartas", "padre", "visitantes", "ancianos", "alvarez", "pruebas",
        )))
        localizada = self.llave_localizada
        variante = "localizada" if localizada else "desconocida"
        yield from self.decir(f"clinica_d3_llave_{variante}", "clinica_d3_salir", "clinica_d3_ninos",
                              "clinica_d3_acceso", "clinica_d3_morales_se_queda")
        intencion = ("Voy a volver a la oficina a buscar esa llave" if localizada
                     else "Voy a seguir buscando la llave del pasadizo")
        primer_dialogo, ultimo_dialogo = GUION[PREPARATIVOS]["lineas"]
        lineas = [primer_dialogo, {"hablante": "Morales", "texto": intencion}, ultimo_dialogo]
        if PREPARATIVOS not in self.datos["consumidos"]:
            yield "hacer", partial(self.mostrar, PREPARATIVOS, lineas=lineas)
        yield "mover", [self.caminar("mateo", (1, 2)), self.caminar("lucas", (2, 3)),
                        self.caminar("morales", (0, 3)), self.caminar("ines", (3, 3))]
        yield "hacer", partial(sonido, "open_door")
        self.datos["fase"] = "hacia_servicio"
        yield "hacer", partial(self.cargar, niveles.CLINICA_EXTERIOR, *FRENTE_CLINICA)
        yield from self.decir("clinica_d3_hacia_el_sur")
        yield "mover", [Recorrido("ines", [(19, 20)], 140), Recorrido("mateo", [(19, 19)], 150),
                        Recorrido("lucas", [(18, 19)], 150), Recorrido("morales", [(20, 19)], 150)]
        self.activar_seguidores(ACOMPANANTES)

    def distraccion(self):
        yield from self.decir("clinica_d3_salida_servicio", "clinica_d3_despedida")
        yield "hacer", partial(crear_npc, "vigia_lateral", "loco", 6, 6, "arriba")
        yield "mover", [Recorrido("morales", [(8, 4), (5, 4), (5, 0)], 125),
                        Recorrido("vigia_lateral", [(6, 4), (5, 4), (5, 0)], 175, retraso=500)]
        for nombre in ("morales", "vigia_lateral"):
            mapa.npcs_activos.pop(nombre)
        self.datos["fase"] = "escape_clinica"
        self.activar_seguidores(("lucas", "ines"))

    def mover_reja(self, abierta):
        self.reja_abierta = abierta
        self.reja_inicio = pygame.time.get_ticks()
        marcar(mapa.matriz_activa, niveles.REJA, 0 if abierta else 1)
        sonido("open_door" if abierta else "close_door")

    def dibujar_reja(self, pantalla, camara_x, camara_y):
        ancho, alto = self.reja.get_size()
        progreso = 1 if self.reja_inicio is None else min(
            1, (pygame.time.get_ticks() - self.reja_inicio) / TIEMPO_REJA,
        )
        desplazamiento = round((progreso if self.reja_abierta else 1 - progreso) * ancho / 2)
        mitad = ancho // 2
        pantalla.blit(self.reja, (325 - camara_x - desplazamiento, 508 - camara_y),
                      (0, 0, mitad, alto))
        pantalla.blit(self.reja, (325 + mitad - camara_x + desplazamiento, 508 - camara_y),
                      (mitad, 0, ancho - mitad, alto))

    def cruce(self):
        for nombre in ("ines", "lucas"):
            mapa.npcs_activos[nombre].update(comportamiento="estatico", pausado=True)
        yield "mover", [self.caminar("mateo", (9, 13)), self.caminar("lucas", (8, 13)),
                        self.caminar("ines", (10, 13))]
        yield from self.decir("clinica_d3_reja")
        yield "hacer", partial(self.mover_reja, True)
        yield "pausa", TIEMPO_REJA
        yield "mover", [Recorrido("mateo", [(9, 16)], 155), Recorrido("ines", [(10, 17)], 145)]
        yield "hacer", partial(mirar, "mateo", "arriba")
        yield "mover", [Recorrido("lucas", [(8, 16)], 145)]
        yield "hacer", partial(self.mover_reja, False)
        yield "pausa", TIEMPO_REJA
        yield from self.decir("clinica_d3_fuera")
        yield "mover", [Recorrido(nombre, [(x, 25)], 145)
                        for nombre, x in (("mateo", 9), ("lucas", 8), ("ines", 10))]
        yield from self.fundido_prision(hacia_negro=True)
        self.datos["fase"] = "epilogo_clinica"
