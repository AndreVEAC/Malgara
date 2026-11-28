"""Continuación del segundo día y director de la segunda noche."""
import json
from functools import partial
from pathlib import Path

import sistema_audio as audio
import sistema_dialogo as dialogo
import sistema_guardado as guardado
import sistema_mapa as mapa
from funciones_mapas.clinica_dia_3 import ClinicaDia3
from funciones_mapas.dia_3 import Dia3
from funciones_mapas.escena_morales import Director, Recorrido, crear_npc, mirar, posicion, ruta_a
from funciones_mapas.investigacion_dia_2 import HOGAR, PISTAS, PRISION, opcion
from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA
from mapas.hogar_dia2 import PUERTA_EXTERIOR
from mapas.iglesia_dia2 import PUERTA_OFICINA
from mapas.pueblo_1_noche_2 import JUNTO_BARRIL

NOCHE_HOGAR = "hogar_noche_2"
CASA = "casa_noche_2"
LLEGADA = "llegada_noche_2"
BARDA = "barda_noche_2"
PUEBLO = "pueblo_1_noche_2"
AMANECER = "pueblo_1_dia_3"
ALIADOS = ("lucas", "morales")

with Path("datos/dialogos_noche_2.json").open(encoding="utf-8-sig") as archivo:
    GUION = json.load(archivo)


class Noche2:
    def __init__(self, investigacion):
        self.investigacion = investigacion
        self.estado = investigacion.estado
        self.director = None
        self.escena = None
        self.revision = -1
        self.oficina = Dia3(investigacion)
        self.clinica = ClinicaDia3(investigacion)

    @property
    def dia3(self):
        return self.clinica if self.datos["plan_dia3"] == "clinica" else self.oficina

    @property
    def datos(self):
        return self.estado.noche2

    @property
    def dia(self):
        return self.estado.dia2

    def mostrar(self, evento):
        nodo = GUION["eventos"][evento]

        def terminar():
            efectos = nodo.get("efectos_al_terminar", {}).copy()
            if "noche2_completada" in efectos:
                efectos["completada"] = efectos.pop("noche2_completada")
            self.datos.update(efectos)
            self.datos["consumidos"].add(evento)

        datos = {
            "lineas": list(self.investigacion._paginar(nodo["lineas"])),
            "al_completar": terminar,
            "desplazar_opciones": True,
        }
        if nodo.get("opciones"):
            datos["opciones"] = [opcion(item["texto"], partial(self.elegir, evento, item))
                                 for item in nodo["opciones"]]
        dialogo.datos_dialogo[evento] = datos
        dialogo.iniciar_dialogo(evento)

    def elegir(self, evento, item):
        if evento in self.datos["consumidos"]:
            return
        self.estado.registrar_decision(evento, item["texto"])
        self.datos.update(item["efectos"])
        self.datos["consumidos"].add(evento)
        self.mostrar(item["siguiente"])

    def decir(self, evento):
        if evento not in self.datos["consumidos"]:
            yield "hacer", partial(self.mostrar, evento)

    def actualizar(self):
        fase = self.datos["fase"]
        if self.dia3.activo:
            self.dia3.actualizar()
            return True
        if not fase:
            if not (self.dia["reencuentro"] and self.dia["resultado"]
                    and mapa.nombre_mapa_actual == HOGAR):
                return False
            fase = self.datos["fase"] = "casa"
        actual = mapa.nombre_mapa_actual
        if fase == "sigilo" and actual == LLEGADA:
            fase = self.datos["fase"] = "llegada"

        cinematico = fase not in ("sigilo", "dia3", "honor")
        mapa.control_cinematico = cinematico
        if cinematico:
            mapa.jugador_bloqueado = True
            mapa.pantalla_negra_en = NOCHE_HOGAR if (
                fase == "despertar" and "n2_despertar_negro" not in self.datos["consumidos"]
            ) else None
            mapa.ocultar_mateo = self.datos.get("barril_oculto", False)
        if not cinematico:
            if self.revision != mapa.revision_nivel:
                self.revision = mapa.revision_nivel
                if fase == "sigilo":
                    self.registrar_entrada()
            return True
        if mapa.transicion_activa:
            return True
        if self.escena != (fase, mapa.revision_nivel):
            self.escena = (fase, mapa.revision_nivel)
            self.director = Director(getattr(self, fase)())
        self.director.actualizar()
        return True

    def exterior(self, x, y):
        if self.dia3.interactuar(x, y):
            return True
        if mapa.nombre_mapa_actual == "iglesia_dia2" and (x, y) == PUERTA_OFICINA:
            self.mostrar("n2_oficina_dia2_exterior")
            return True
        if mapa.nombre_mapa_actual == AMANECER and mapa.matriz_activa[y][x] == 89:
            dialogo.datos_dialogo["dia3_camino_pendiente"] = {
                "lineas": [{"hablante": "Mateo", "texto": "El camino sigue cerrado."}],
            }
            dialogo.iniciar_dialogo("dia3_camino_pendiente")
            return True
        return False

    def objetivo(self):
        if self.dia3.activo:
            return self.dia3.objetivo()
        if self.datos["fase"] == "dia3":
            destino = "la oficina municipal" if self.datos["plan_dia3"] == "oficina" else "la clínica"
            return f"Reúnete con tus aliados detrás de {destino}"
        if self.datos["fase"] == "honor":
            return "Invitados de honor · Continuará"
        if self.datos["fase"] == "sigilo":
            return "Rodea el pueblo hasta la casa de Elena"
        return None

    def cambio(self, fase, destino, posicion=None, **kwargs):
        self.datos["fase"] = fase
        mapa.cargar_nivel(destino, *(posicion or (None, None)), **kwargs)

    def caminar(self, nombre, destino, intervalo=160, retraso=0):
        origen = posicion(nombre)[:2]
        return Recorrido(nombre, ruta_a(origen, destino), intervalo=intervalo, retraso=retraso)

    def casa(self):
        rescate = self.dia["rama"] == "rescate"
        if "lucas" not in mapa.npcs_activos:
            self.investigacion.colocar_aliados()
        if not rescate:
            crear_npc("morales", "morales", *PUERTA_EXTERIOR, "arriba")
            yield "hacer", partial(mapa._reproducir_sonido_portal, ABRIR_PUERTA)
            yield "mover", [Recorrido("morales", [(8, 6), (6, 6), (6, 5)], intervalo=180)]
            yield "hacer", partial(mapa._reproducir_sonido_portal, CERRAR_PUERTA)
        yield from self.decir("n2_entrada_rescate" if rescate else "n2_entrada_normal")

        resultado = self.dia["resultado"]
        pistas = set(resultado["pistas"])
        if not resultado.get("reencuentro_oficina"):
            if "caja_jm" in pistas and resultado["lucas_colabora"]:
                yield from self.decir("n2_correccion_oficina")
                resultado["ubicacion_llave"] = "oficina"
            resultado["reencuentro_oficina"] = True

        yield "mover", [self.caminar("mateo", (4, 3))]
        yield "hacer", partial(mirar, "mateo", "izq")
        for evento in ("n2_carta_hallazgo", "n2_carta_lectura", "n2_confesion_cartas", "n2_decision_intro"):
            yield from self.decir(evento)
        if not self.datos["plan_dia3"]:
            evento = "n2_elegir_destino" if PISTAS <= pistas and resultado["lucas_colabora"] else "n2_plan_unico"
            yield from self.decir(evento)
        plan = self.datos["plan_dia3"]
        self.datos["cita"] = plan
        for evento in ("n2_refugio", f"n2_cita_{plan}", "n2_descanso"):
            yield from self.decir(evento)
        yield "hacer", partial(self.cambio, "despertar", NOCHE_HOGAR)

    def despertar(self):
        crear_npc("lucas", "lucas", 5, 5, "izq")
        crear_npc("morales", "morales", 6, 5, "izq")
        yield from self.decir("n2_despertar_negro")
        yield "hacer", self.revelar_hogar
        yield from self.decir("n2_despertar_visible")
        yield "mover", [self.caminar("mateo", (8, 6)),
                        self.caminar("lucas", (7, 6), retraso=340),
                        self.caminar("morales", (6, 6), retraso=630)]
        yield "hacer", partial(mapa._reproducir_sonido_portal, ABRIR_PUERTA)
        yield "hacer", partial(self.cambio, "salida", CASA, sonido_llegada=CERRAR_PUERTA)

    def revelar_hogar(self):
        mapa.pantalla_negra_en = None
        mapa.alpha_transicion = 255
        mapa.tipo_transicion = "fade_in"
        mapa.transicion_activa = True

    def salida(self):
        from funciones_mapas import funcion_casa_noche_2 as exterior

        crear_npc("lucas", "lucas", 14, 17, "arriba")
        crear_npc("morales", "morales", 15, 18, "arriba")
        yield "hacer", partial(mirar, "mateo", "arriba")
        yield "hacer", exterior.enfocar
        yield "pausa", exterior.DURACION_ENCUADRE
        yield from self.decir("n2_desvio")
        yield "hacer", exterior.desenfocar
        yield "pausa", exterior.DURACION_ENCUADRE
        yield "hacer", self.iniciar_sigilo

    def iniciar_sigilo(self):
        self.datos["fase"] = "sigilo"
        self.registrar_entrada()
        self.checkpoint()

    def registrar_entrada(self):
        if mapa.reinicio_entrada is not None:
            return
        anterior = self.datos["checkpoint"]
        if anterior and anterior["mapa"] == mapa.nombre_mapa_actual and guardado.revision_cargada == mapa.revision_nivel:
            entrada = tuple(anterior["entrada"])
        else:
            entrada = (mapa.mateo_x, mapa.mateo_y)
        self.datos["checkpoint"] = {"mapa": mapa.nombre_mapa_actual, "entrada": entrada}
        mapa.reinicio_entrada = entrada
        for nombre in ALIADOS:
            if nombre not in mapa.npcs_activos:
                crear_npc(nombre, nombre, *entrada)
            npc = mapa.npcs_activos[nombre]
            npc.update(comportamiento="sigue_jugador", pausado=False)
            npc["seguimiento"] = {"velocidad_ms": 170}
        mapa.colocar_seguidores_cerca()

    def checkpoint(self):
        mapa.control_cinematico = False
        mapa.jugador_bloqueado = False
        if self.investigacion.autoguardar:
            guardado.solicitar("automatico", mapa_destino=mapa.nombre_mapa_actual)

    def llegada(self):
        crear_npc("morales", "morales", 17, 7, "izq")
        crear_npc("lucas", "lucas", 18, 8, "arriba")
        yield from self.decir("n2_llegada_guia")
        yield "mover", [self.caminar("morales", (10, 0)),
                        self.caminar("mateo", (10, 1), retraso=340),
                        self.caminar("lucas", (10, 2), retraso=700)]
        yield "hacer", partial(self.cambio, "barda", BARDA)

    def barda(self):
        crear_npc("morales", "morales", 10, 21, "arriba")
        crear_npc("lucas", "lucas", 10, 22, "arriba")
        yield from self.decir("n2_barda_camino")
        yield "mover", [Recorrido("morales", [(10, 8)], 110),
                        Recorrido("lucas", [(10, 9)], 110, 220),
                        Recorrido("mateo", [(10, 10)], 110, 440)]
        yield from self.decir("n2_barda_cruce")
        yield "mover", [Recorrido("morales", [(10, 4), (9, 4)], 160),
                        Recorrido("lucas", [(10, 4), (11, 4)], 160, 320),
                        Recorrido("mateo", [(10, 8)], 160, 640)]
        yield "hacer", partial(audio.establecer_persecucion, True)
        crear_npc("guardia", "loco", 10, 18, "arriba")
        yield "mover", [Recorrido("guardia", [(10, 9)], 105)]
        yield from self.decir("n2_agarre")

        if self.datos["ayudantes"] is None:
            resultado = self.dia["resultado"]
            elegibles = {"lucas": resultado["lucas_colabora"], "morales": resultado["morales_aliado"]}
            self.datos["ayudantes"] = {nombre for nombre, ayuda in elegibles.items() if ayuda}
        ayudas = self.datos["ayudantes"]
        variante = {frozenset(v["ayudantes"]): k for k, v in GUION["variantes_emboscada"].items()}[frozenset(ayudas)]
        if not ayudas:
            yield from self.decir("n2_ninguno_abandono")
            yield "mover", [Recorrido("morales", [(9, 0)], 95), Recorrido("lucas", [(11, 0)], 95)]
            self.ocultar_aliados(ALIADOS)
            yield from self.decir("n2_ninguno_final")
            yield "mover", self.refuerzos(bloquear_paso=False)
            audio.establecer_persecucion(False)
            self.datos["captura_tipo"] = "nocturna_definitiva"
            yield "hacer", partial(self.cambio, "prision", PRISION)
            return

        yield from self.decir(f"n2_{variante}_regreso")
        ausentes = set(ALIADOS) - ayudas
        if ausentes:
            yield "mover", [self.caminar(nombre, (posicion(nombre)[0], 0), 95) for nombre in ausentes]
            self.ocultar_aliados(ausentes)
        ayuda = "morales" if "morales" in ayudas else "lucas"
        yield "mover", [Recorrido(ayuda, [(10, 4), (10, 8), (9, 8)], 110)]
        yield "mover", [Recorrido("guardia", [(11, 9), (11, 11)], 110),
                        Recorrido("mateo", [(10, 10)], 130)]
        yield "pausa", 330
        yield from self.decir(f"n2_{variante}_caida")
        yield "mover", [Recorrido(ayuda, [(10, 8), (10, 4)], 110), *self.refuerzos()]
        yield from self.decir(f"n2_{variante}_separacion")
        yield "mover", [Recorrido("mateo", [(10, 23)], 88),
                        *[self.caminar(nombre, (posicion(nombre)[0], 0), 95) for nombre in ayudas]]
        self.ocultar_aliados(ayudas)
        yield "hacer", partial(self.cambio, "huida_llegada", LLEGADA, (10, 1))

    def refuerzos(self, *, bloquear_paso=True):
        crear_npc("refuerzo_izq", "loco", -1, 9, "der")
        crear_npc("refuerzo_der", "loco", 20, 9, "izq")
        derecha = [(11, 9), (11, 8)]
        if bloquear_paso:
            derecha.append((10, 8))
        return [Recorrido("refuerzo_izq", [(9, 9), (9, 8)], 140),
                Recorrido("refuerzo_der", derecha, 140)]

    def ocultar_aliados(self, nombres):
        for nombre in nombres:
            mapa.npcs_activos[nombre]["visible"] = False

    def huida_llegada(self):
        yield "mover", [self.caminar("mateo", (19, 7), 95)]
        yield "hacer", partial(self.cambio, "barril", PUEBLO, (1, 7))

    def barril(self):
        mapa.npcs_activos.clear()
        yield from self.decir("n2_barril_aproximacion")
        yield "mover", [self.caminar("mateo", JUNTO_BARRIL, 95)]
        yield "hacer", partial(mirar, "mateo", "arriba")
        yield from self.decir("n2_barril_entrada")
        self.datos["barril_oculto"] = mapa.ocultar_mateo = True
        crear_npc("ronda_1", "loco", -3, 7, "der")
        crear_npc("ronda_2", "loco", -4, 8, "der")
        yield "mover", [
            Recorrido("ronda_1", [(1, 7), *ruta_a((1, 7), (19, 7))], 110),
            Recorrido("ronda_2", [(2, 8), *ruta_a((2, 8), (19, 8))], 120, 240),
        ]
        yield "pausa", 5000
        yield "hacer", partial(audio.establecer_persecucion, False)
        yield from self.decir("n2_barril_espera")
        yield "pausa", 480
        yield "hacer", partial(self.cambio, "amanecer", AMANECER, JUNTO_BARRIL)

    def amanecer(self):
        yield "pausa", 400
        yield "hacer", self.salir_barril
        yield from self.decir("n2_amanecer")
        ayudas = self.datos["ayudantes"]
        variante = next(k for k, v in GUION["variantes_emboscada"].items() if set(v["ayudantes"]) == ayudas)
        yield from self.decir(f"n2_amanecer_{variante}")
        yield from self.decir(f"n2_amanecer_{self.datos['plan_dia3']}")
        self.datos.update(fase="dia3", dia_actual=3, completada=True,
                          companeros_disponibles=set(ayudas),
                          checkpoint={"mapa": AMANECER, "entrada": JUNTO_BARRIL})
        self.checkpoint()

    def salir_barril(self):
        self.datos["barril_oculto"] = mapa.ocultar_mateo = False
        mirar("mateo", "abajo")

    def prision(self):
        yield from self.decir("n2_prision")
        if self.dia["rama"] == "rescate":
            yield from self.decir("n2_prision_reincidente")
        yield "pausa", 850
        yield from self.decir("n2_prision_cierre")
        self.datos.update(fase="honor", completada=True,
                          checkpoint={"mapa": PRISION, "entrada": posicion("mateo")[:2]})
        self.checkpoint()
