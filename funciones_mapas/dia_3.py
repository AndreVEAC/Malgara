"""Director de la rama de oficina y del final del laboratorio."""
import json
from functools import partial
from pathlib import Path

import pygame

import sistema_audio as audio
import sistema_dialogo as dialogo
import sistema_escondites as escondites
import sistema_guardado as guardado
import sistema_mapa as mapa
import sistema_vigilancia as vigilancia
from configuracion import ALTO_PANTALLA, ANCHO_PANTALLA, TAMANO_CASILLA as T
from funciones_mapas import funcion_prision_dia_2 as barrotes
from funciones_mapas.escena_morales import Director, Recorrido, crear_npc, mirar, posicion, ruta_a, sonido
from mapas import dia_3 as niveles, tunel
from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA

GUION = json.loads((Path(__file__).resolve().parents[1] / "datos/dialogos_dia_3.json").read_text(encoding="utf-8"))
EPILOGO = json.loads((Path(__file__).resolve().parents[1] / "datos/epilogo_laboratorio.json")
                     .read_text(encoding="utf-8"))["eventos"]
GUION.update(EPILOGO)
ALIADOS = ("lucas", "morales")
FUNDIDO_PRISION_MS = 750


class Dia3:
    guion = GUION

    def __init__(self, investigacion):
        self.investigacion = investigacion
        self.estado = investigacion.estado
        self.revision = -1
        self.director = None
        self.aviso_hasta = 0

    @property
    def datos(self):
        return self.estado.dia3

    @property
    def ayudantes(self):
        noche = self.estado.noche2
        guardados = noche.get("ayudantes")
        return guardados if guardados is not None else noche.get("companeros_disponibles", set())

    @property
    def activo(self):
        noche = self.estado.noche2
        return (noche["fase"] == "dia3" and noche["plan_dia3"] == "oficina"
                and bool(self.ayudantes) and self.estado.dia2["rama"] != "invitados_honor")

    def mostrar(self, evento, despues=None, lineas=None):
        nodo = self.guion[evento]
        identificador = f"d3_{evento}"

        def completar():
            self.datos.update(nodo.get("efectos_al_terminar", {}))
            self.datos["consumidos"].add(evento)
            if evento == "caja_jm":
                self.estado.objetos_clave.add("llave_pasadizo")
                mapa.imagenes_objetos.pop(34, None)
            if despues:
                despues()

        dialogo.datos_dialogo[identificador] = {
            "lineas": list(self.investigacion._paginar(nodo["lineas"] if lineas is None else lineas)),
            "al_completar": completar,
        }
        dialogo.iniciar_dialogo(identificador)

    def decir(self, *eventos):
        for evento in eventos:
            if evento not in self.datos["consumidos"]:
                yield "hacer", partial(self.mostrar, evento)

    def narrar_epilogo(self, eventos):
        mapa.pantalla_negra_en = mapa.nombre_mapa_actual
        dialogo.limpiar_notificaciones()
        for evento in eventos:
            if evento not in self.datos["consumidos"]:
                lineas = [dict(linea, hablante="") if linea["hablante"] == "Narración" else linea
                          for linea in self.guion[evento]["lineas"]]
                yield "hacer", partial(self.mostrar, evento, lineas=lineas)

    def aviso(self, evento):
        ahora = pygame.time.get_ticks()
        if ahora >= self.aviso_hasta:
            self.aviso_hasta = ahora + 1500
            self.mostrar(evento)

    def solicitar_guardado(self, destino=None):
        if self.investigacion.autoguardar:
            guardado.solicitar("automatico", mapa_destino=destino)

    def objetivo(self):
        if not self.activo or self.director or self.datos["fase"] in ("epilogo", "fin"):
            return None
        actual = mapa.nombre_mapa_actual
        if not self.datos.get("encuentro_oficina_revisado"):
            return "Reúnete con tus aliados detrás de la oficina municipal"
        if not self.datos.get("telefono_localizado"):
            return "Busca la caja J. M. en el escritorio de la oficina"
        if not self.datos.get("companeros_listos"):
            return "Busca a Lucas y Morales en la iglesia"
        if not self.datos.get("ubicacion_laboratorio_conocida"):
            return "Abre la puerta de hierro al final del pasadizo"
        if actual == niveles.BOSQUE:
            if not self.datos.get("guardia_aviso"):
                return "Cruza el sendero hacia el fondo del bosque"
            return "Localiza la escotilla oculta"
        return "Ve al bosque por la salida inferior izquierda del pueblo"

    def desvio(self):
        if not self.datos.get("companeros_reunidos"):
            return "desvio_antes_reunion"
        if not self.datos.get("telefono_localizado"):
            return "desvio_buscar_llave"
        if not self.datos.get("ubicacion_laboratorio_conocida"):
            return "desvio_antes_documentos"
        return "desvio_hacia_bosque"

    def interceptar_portal(self, destino):
        if not self.activo:
            return False
        evento = None
        if destino in (niveles.OFICINA, niveles.IGLESIA) and not self.datos.get("encuentro_oficina_revisado"):
            if destino == niveles.IGLESIA:
                evento = "iglesia_primera_sin_oficina"
            else:
                dialogo.activar_notificacion("Comprueba el punto de encuentro detrás de la oficina.")
                return True
        elif destino == niveles.TUNEL and not self.datos.get("companeros_listos"):
            evento = "desvio_buscar_llave"
        elif destino == niveles.BOSQUE and not self.datos.get("ubicacion_laboratorio_conocida"):
            evento = self.desvio()
        if evento:
            self.aviso(evento)
        return evento is not None

    def interactuar(self, x, y):
        if not self.activo or mapa.nombre_mapa_actual not in niveles.NIVELES:
            return False
        evento = mapa.interactuables_activos.get(mapa.matriz_activa[y][x])
        if evento == "desvio":
            self.aviso(self.desvio())
        elif evento == "escritorio":
            if self.datos.get("llave_pasadizo") or "llave_pasadizo" in self.estado.objetos_clave:
                self.datos["llave_pasadizo"] = True
                if self.datos.get("telefono_localizado"):
                    self.mostrar("escritorio_repetir")
                else:
                    self.mostrar("telefono_descubrimiento", self.solicitar_guardado)
            else:
                terminar = partial(self.mostrar, "telefono_descubrimiento", self.solicitar_guardado)
                self.mostrar("caja_jm", terminar)
        elif evento == "archivero":
            self.mostrar("archivero")
        elif evento == "papeles":
            self.mostrar("oficina_cartas_cerradas")
        elif evento == "puerta_tunel":
            if not self.datos.get("llave_pasadizo"):
                self.mostrar("puerta_sin_llave")
            elif self.datos.get("ubicacion_laboratorio_conocida"):
                self.mostrar("cuarto_repetir")
            elif not self.datos.get("telefono_localizado"):
                self.mostrar("desvio_buscar_llave")
            else:
                self.mostrar("puerta_abrir", partial(self.cargar, niveles.CUARTO))
        elif evento == "escotilla":
            if not self.datos.get("guardia_aviso"):
                self.aviso("escotilla_con_vigilante")
            elif not self.datos.get("arbustos_retirados"):
                self.mostrar("arbustos", self.revelar_escotilla)
            else:
                self.preparar_laboratorio()
        else:
            return False
        return True

    def revelar_escotilla(self):
        self.aplicar_arbustos()
        self.mostrar("escotilla_descubierta", self.solicitar_guardado)

    def aplicar_arbustos(self):
        for x, y in niveles.ARBUSTOS:
            mapa.matriz_activa[y][x] = 32 if (x, y) == niveles.ESCOTILLA else 0

    def preparar_laboratorio(self):
        if self.investigacion.autoguardar:
            try:
                guardado.guardar(self.estado, "automatico")
            except (OSError, TypeError, ValueError) as error:
                print(f"[Guardado antes del laboratorio] {error}")
                dialogo.activar_notificacion("No se pudo guardar antes de bajar.")
            guardado.pendiente = None
        self.datos["fase"] = "laboratorio"
        self.iniciar(self.laboratorio())
        self.cargar(niveles.LAB)

    def cargar(self, destino, *entrada):
        mapa.jugador_bloqueado = True
        mapa.cargar_nivel(destino, *entrada, sonido_llegada=CERRAR_PUERTA if destino in (
            niveles.CUARTO, niveles.LAB, niveles.TUNEL,
        ) else None)

    def iniciar(self, secuencia):
        mapa.control_cinematico = True
        mapa.jugador_bloqueado = True
        audio.establecer_persecucion(False)
        self.director = Director(secuencia)

    def actualizar(self):
        actual = mapa.nombre_mapa_actual
        if actual == "pueblo_1_dia_3":
            if not mapa.transicion_activa:
                self.cargar(niveles.PUEBLO, *posicion("mateo")[:2])
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
        if actual == niveles.EXTERIOR:
            x, y = posicion("mateo")[:2]
            ex, ey = niveles.ENCUENTRO
            if not self.datos.get("encuentro_oficina_revisado") and abs(x-ex) + abs(y-ey) <= 1:
                self.mostrar("oficina_encuentro_vacio", self.solicitar_guardado)
        elif actual == niveles.BOSQUE:
            self.actualizar_bosque()

    def configurar(self, actual):
        if actual not in niveles.NIVELES:
            return
        nivel = niveles.NIVELES[actual]
        mapa.reinicio_entrada = (nivel.INICIO_X, nivel.INICIO_Y)
        if actual == niveles.PUEBLO:
            # Las entradas del este y del bosque quedan lejos de las rondas.
            x, y = posicion("mateo")[:2]
            if x >= 35:
                mapa.reinicio_entrada = (38, 7 if y < 15 else 22)
            elif x <= 3 and y >= 19:
                mapa.reinicio_entrada = (1, 22)
        elif actual == niveles.PLAZA:
            x, y = posicion("mateo")[:2]
            mapa.reinicio_entrada = (38, 7) if x >= 35 else (1, 22 if y >= 18 else 7)
        elif actual == niveles.TUNEL and mapa.mateo_x >= 17:
            mapa.reinicio_entrada = (18, 1)

        if self.director:
            mapa.jugador_bloqueado = True
        if actual == niveles.OFICINA:
            if not self.datos.get("llave_pasadizo"):
                self.dibujar_llave()
            self.iniciar_cartel("oficina_entrada")
        elif actual == niveles.IGLESIA:
            from funciones_mapas.funcion_dentro_iglesia import dibujar_efectos
            mapa.script_nivel_actual.dibujar_efectos = dibujar_efectos
            if not self.datos.get("companeros_listos"):
                if not self.datos.get("companeros_reunidos"):
                    self.iniciar(self.reunion())
                elif self.datos.get("telefono_localizado"):
                    self.iniciar(self.reunion_con_llave("regreso_con_llave"))
        elif actual == niveles.TUNEL:
            from funciones_mapas.funcion_tunel import recortar_linternas
            mapa.script_nivel_actual.recortar_linternas = recortar_linternas
            self.iniciar_cartel("tunel_entrada")
        elif actual == niveles.CUARTO:
            self.reparto(lucas=(0, 2), morales=(2, 2))
            mirar("lucas", "der")
            mirar("morales", "izq")
            self.iniciar(self.documentos())
        elif actual == niveles.BOSQUE:
            if self.datos.get("guardia_aviso"):
                mapa.npcs_activos.pop("vigia_bosque", None)
            if self.datos.get("arbustos_retirados"):
                self.aplicar_arbustos()
            self.iniciar_cartel("bosque_entrada")
        elif actual == niveles.LAB:
            mapa.ocultar_mateo = False
            if self.datos.get("climax_iniciado"):
                self.reparto(lucas=(8, 6))
            else:
                self.reparto(lucas=(7, 7), morales=(9, 7))
        elif actual == niveles.ACCESO:
            capturados = not self.datos["acceso_cerrado"]
            mapa.ocultar_mateo = not capturados
            self.exterior_escotilla(capturados)
        elif actual == niveles.PRISION:
            self.reparto(lucas=(5, 4), morales=(4, 3))
            barrotes.iniciar()
            mapa.script_nivel_actual.capa_profundidad = barrotes.capa_profundidad

        if self.datos.get("companeros_listos") and actual in (
            niveles.PUEBLO, niveles.PLAZA, niveles.EXTERIOR, niveles.IGLESIA, niveles.TUNEL, niveles.BOSQUE,
        ):
            self.seguidores()

    def iniciar_cartel(self, evento):
        if not self.director and evento not in self.datos["consumidos"]:
            self.iniciar(self.decir(evento))

    def dibujar_llave(self):
        imagen = pygame.Surface((T, T), pygame.SRCALPHA)
        color = (226, 188, 94)
        pygame.draw.circle(imagen, color, (11, 5), 4, 2)
        pygame.draw.lines(imagen, color, False, [(14, 6), (23, 9), (23, 12), (21, 11)], 2)
        mapa.imagenes_objetos[34] = {"img": imagen, "colision": True, "profundidad": False}

    def seguidores(self):
        for nombre in ALIADOS:
            if nombre == "morales" and self.datos.get("morales_sale_a_llamar"):
                mapa.npcs_activos.pop(nombre, None)
                continue
            if nombre not in mapa.npcs_activos:
                crear_npc(nombre, nombre, *posicion("mateo")[:2])
            mapa.npcs_activos[nombre].update(comportamiento="sigue_jugador", pausado=False,
                                            seguimiento={"velocidad_ms": 170})
        mapa.colocar_seguidores_cerca()

    def caminar(self, nombre, destino, intervalo=170):
        return Recorrido(nombre, ruta_a(posicion(nombre)[:2], destino), intervalo)

    def reparto(self, **posiciones):
        for nombre, punto in posiciones.items():
            crear_npc(nombre, nombre, *punto, "arriba")

    def reunion(self):
        yield "mover", [self.caminar("lucas", (10, 12)), self.caminar("morales", (9, 12))]
        yield from self.decir("iglesia_reunion")
        ayudas = self.ayudantes
        variante = "ambos" if len(ayudas) == 2 else next(iter(ayudas))
        yield from self.decir(f"reunion_ayuda_{variante}")
        if self.datos.get("telefono_localizado"):
            yield from self.reunion_con_llave("reunion_con_llave")
        else:
            yield from self.decir("reunion_sin_llave")
            self.solicitar_guardado()

    def reunion_con_llave(self, evento):
        yield from self.decir(evento)
        self.datos["companeros_listos"] = True
        self.datos["companeros_actuales"] = set(ALIADOS)
        self.solicitar_guardado()
        self.seguidores()

    def documentos(self):
        yield from self.decir("cuarto_entrada")
        yield "mover", [self.caminar("lucas", (0, 1))]
        yield "pausa", 400
        yield from self.decir("cuarto_lucas_documento")
        yield "mover", [self.caminar("morales", (2, 1))]
        yield "pausa", 400
        yield from self.decir("cuarto_morales_documento", "cuarto_plan_telefono")
        self.solicitar_guardado(niveles.TUNEL)
        yield "hacer", partial(self.cargar, niveles.TUNEL, *tunel.FRENTE_A_PUERTA)

    def actualizar_bosque(self):
        vigia = mapa.npcs_activos.get("vigia_bosque")
        estado = vigia["_vigilancia"]["estado"] if vigia else None
        if estado in ("PERSIGUIENDO", "ESPERANDO") and not self.datos.get("guardia_detecto"):
            self.datos["guardia_detecto"] = True
            texto = "  ".join(linea["texto"] for linea in GUION["bosque_descubiertos"]["lineas"])
            dialogo.activar_notificacion(texto)
        if estado == "AVISO_DADO":
            self.datos["guardia_aviso"] = True
            mapa.npcs_activos.pop("vigia_bosque")
        if (self.datos.get("guardia_aviso") and not escondites.escondido
                and "bosque_guardia_ausente" not in self.datos["consumidos"]):
            self.mostrar("bosque_guardia_ausente", self.solicitar_guardado)

    def exterior_escotilla(self, capturados=False):
        crear_npc("alvarez", "lider", 37, 21, "abajo")
        puntos = (
            (35, 21), (34, 22), (35, 24), (36, 24), (38, 24),
            (38, 22), (38, 20), (36, 20), (33, 24), (39, 23),
        )
        for indice, (x, y) in enumerate(puntos, 1):
            crear_npc(f"guardia_{indice}", "loco", x, y)
        if capturados:
            self.reparto(lucas=(37, 24))

    def humo(self, pantalla, camara_x, camara_y):
        superficie = pygame.Surface((400, 320), pygame.SRCALPHA)
        tiempo = (pygame.time.get_ticks() - self.inicio_humo) / 1000
        for x, y, radio in ((70, 190, 46), (155, 218, 66), (223, 175, 58), (304, 218, 70), (371, 221, 60)):
            avance = min(tiempo, 2)
            pygame.draw.circle(superficie, (149, 143, 127, round(107 * min(1, tiempo))),
                               (x, round(y - 16 * avance)), round(radio + 13 * avance))
        pantalla.blit(superficie, (-camara_x, -camara_y + round(2 * (int(tiempo * 20) % 2))))

    def temblor(self, pantalla, *_):
        transcurrido = pygame.time.get_ticks() - self.inicio_humo
        if transcurrido < 900:
            desplazamiento = (3, -2, 2, -1)[(transcurrido // 55) % 4]
            escena = pantalla.copy()
            pantalla.fill((0, 0, 0))
            pantalla.blit(escena, (desplazamiento, 0))

    def laboratorio(self):
        self.datos["acceso_cerrado"] = True
        yield "hacer", partial(sonido, "cerrojo")
        yield from self.decir("laboratorio_entrada")
        yield "mover", [self.caminar("mateo", (2, 6)), self.caminar("lucas", (1, 6)),
                        self.caminar("morales", (3, 6))]
        yield from self.decir("lab_registro_victimas", "lab_registro_menores")
        yield "mover", [self.caminar("mateo", (4, 4)), self.caminar("lucas", (3, 4)),
                        self.caminar("morales", (5, 4))]
        yield from self.decir("lab_cura", "lab_pacientes")
        yield "mover", [self.caminar("morales", (8, 4))]
        yield from self.decir("lab_advertencia", "lab_urgencia")
        yield "mover", [self.caminar("morales", (8, 7))]
        yield "hacer", partial(sonido, "open_door")
        mapa.npcs_activos.pop("morales")
        self.datos["companeros_actuales"].discard("morales")
        yield "hacer", partial(sonido, "cerrojo")
        yield "mover", [self.caminar("mateo", (6, 4)), self.caminar("lucas", (7, 4))]
        yield from self.decir("lab_expediente_mateo", "lab_programa", "lab_cartas_madre",
                              "lab_mateo_reaccion", "lab_padre_lucas", "lab_ruptura")
        self.datos["climax_iniciado"] = True
        if Path("recursos/sonidos/efectos/pasos.wav").is_file():
            canal = sonido("pasos")
            if canal is not None:
                yield "esperar", canal.get_busy
        yield from self.decir("lab_llegan")
        yield "mover", [self.caminar("lucas", (8, 6))]
        yield "hacer", partial(sonido, "cerrojo")
        yield "hacer", partial(self.cargar, niveles.ACCESO)
        yield from self.decir("alvares_entrada", "alvares_madre", "alvares_justificacion", "alvares_morales")
        yield "mover", [Recorrido("guardia_1", [(19, 21)], intervalo=95)]
        yield "hacer", partial(self.cargar, niveles.LAB, 6, 4)
        yield "mover", [self.caminar("lucas", (6, 6))]
        yield from self.decir("alvares_amenaza", "mateo_decide")
        yield "mover", [self.caminar("mateo", (8, 4), 90), self.caminar("lucas", (8, 5), 95)]
        yield from self.decir("destruccion")
        yield "mover", [self.caminar("lucas", (8, 6), 80)]
        self.inicio_humo = pygame.time.get_ticks()
        mapa.script_nivel_actual.dibujar_efectos = self.humo
        mapa.script_nivel_actual.aplicar_encuadre = self.temblor
        yield "hacer", partial(sonido, "alarma")
        yield "pausa", 1350
        yield from self.decir("destruccion_salida")
        yield "hacer", partial(sonido, "open_door")
        self.datos["acceso_cerrado"] = False
        crear_npc("guardia_acceso", "loco", 8, 7, "arriba")
        yield "mover", [self.caminar("guardia_acceso", (9, 6))]
        yield "mover", [self.caminar("mateo", (8, 7)), self.caminar("lucas", (7, 7))]
        yield "hacer", partial(self.cargar, niveles.ACCESO, 37, 23)
        yield from self.decir("alvares_despues")
        self.datos["fase"] = "captura_final_laboratorio"
        yield "hacer", partial(self.cargar, niveles.PRISION)
        yield from self.prision()

    def prision(self):
        yield from self.decir("prision_reunion")
        self.datos["llamada_confirmada"] = True
        yield from self.decir("prision_espera")
        yield from self.fundido_prision(hacia_negro=True)
        mapa.pantalla_negra_en = niveles.PRISION
        yield "pausa", 900
        rescate = GUION["rescate_policial"]["lineas"]
        yield "hacer", partial(self.mostrar, "rescate_policial", lineas=rescate[:1])
        mapa.pantalla_negra_en = None
        yield from self.fundido_prision(hacia_negro=False)
        yield "hacer", partial(self.mostrar, "rescate_policial", lineas=rescate[1:])
        yield "hacer", barrotes.abrir
        yield "mover", [self.caminar("mateo", (4, 6)), self.caminar("lucas", (5, 6)),
                        self.caminar("morales", (3, 6))]
        self.datos["rescate_policial"] = True
        yield from self.fundido_prision(hacia_negro=True)
        audio.reproducir_ambiente("ultima_cura", volumen=0.35)
        yield from self.narrar_epilogo(EPILOGO)
        self.datos["fase"] = "epilogo"

    def fundido_prision(self, *, hacia_negro):
        inicio = pygame.time.get_ticks()
        negro = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))

        def dibujar(pantalla, *_):
            progreso = min(1, (pygame.time.get_ticks() - inicio) / FUNDIDO_PRISION_MS)
            negro.set_alpha(round(255 * (progreso if hacia_negro else 1 - progreso)))
            pantalla.blit(negro, (0, 0))

        mapa.script_nivel_actual.aplicar_encuadre = dibujar
        yield "pausa", FUNDIDO_PRISION_MS
        del mapa.script_nivel_actual.aplicar_encuadre
