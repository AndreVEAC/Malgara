"""Adapta el guion diurno al diálogo y al movimiento de Malgara."""
import json
from collections import deque
from functools import partial
from pathlib import Path

import pygame

import sistema_audio as audio
import sistema_dialogo as dialogo
import sistema_guardado as guardado
import sistema_mapa as mapa
from configuracion import ANCHO_PANTALLA
from estado import BUSQUEDA_DIA_2
from funciones_mapas.escena_morales import Director, Recorrido, crear_npc, mirar
from mapas.hogar_dia2 import PUERTA_EXTERIOR
from mapas.iglesia_dia2 import ESCONDITE_MORALES
from mapas.habitaciones_dia_2 import ABRIR_PUERTA, CERRAR_PUERTA


with Path("datos/dialogos_dia_2.json").open(encoding="utf-8-sig") as archivo:
    GUION = json.load(archivo)

REGLAS = GUION["reglas"]
PISTAS = set(REGLAS["pistas_cruciales"])
MINIMO = REGLAS["conversaciones_minimas"]
CONFIANZA_LUCAS = 60
HOGAR = "hogar_dia2"
CASA_ABUELA = "casa_abuela_dia_2"
CUARTO = "habitacion_abuela_dia_2"
PRISION = "prision_dia_2"
ENTRADA = "llegada_dia_2"
PLAZA = "pueblo_2_dia_2"
IGLESIA = "iglesia_dia2"
FONDO_SOSPECHA = (136, 60, 69)
DESTINO_LUCAS = (5, 5)
PUNTOS = {
    "pueblo_1_dia_2": {(5, 13): "fotografias", (24, 14): "panadero", (37, 11): "vecino"},
    PLAZA: {(3, 4): "preparativos_sur", (20, 14): "nina", (38, 14): "anciano",
            (31, 24): "amargado"},
    IGLESIA: {ESCONDITE_MORALES: "morales"},
    "pueblo_3_dia_2": {(18, 6): "hombre_calle", (16, 18): "mujer_clinica"},
    "casa_dia2": {(3, 23): "ines"},
    ENTRADA: {(15, 4): "entrada_abuela", (15, 2): "ventana_abuela"},
    HOGAR: {(2, 3): "sillon", (3, 3): "sillon", (0, 4): "sillon",
            (0, 5): "sillon", (2, 6): "sillon", (3, 6): "sillon"},
    CASA_ABUELA: {(4, 4): "abuela"},
}


def activa(estado):
    return BUSQUEDA_DIA_2 in mapa.eventos_completados and not estado.dia2["cerrada"]


def objetivo(estado):
    if estado.noche2["fase"]:
        return None
    if activa(estado) and not estado.dia2["captura_pendiente"]:
        datos = estado.dia2
        return f"Personas {min(MINIMO, len(datos['personas']))}/{MINIMO}    Pistas {len(PISTAS & datos['hallazgos'])}/3"
    if estado.dia2["resultado"]:
        if estado.dia2["rama"] == "invitados_honor":
            return "Invitados de honor · Continuará"
        return "Fin de la investigación diurna · Continuará"
    return None


def opcion(texto, al_elegir=None):
    return {"texto": texto, "al_elegir": al_elegir or (lambda: None)}


class Investigacion:
    def __init__(self, estado, *, autoguardar=True):
        self.estado = estado
        self.autoguardar = autoguardar
        self.director = None
        self.revision_nivel = -1
        self.noche = None

    @property
    def datos(self):
        return self.estado.dia2

    def _paginar(self, lineas):
        if not dialogo.fuente_texto:
            dialogo.inicializar()
        for linea in lineas:
            texto = linea["texto"].format(
                pistas_obtenidas=len(PISTAS & self.datos["hallazgos"]),
                informes_pendientes=len(self.datos["hallazgos"] - self.datos["informados"]),
            )
            pagina = ""
            for palabra in texto.split():
                tentativa = f"{pagina} {palabra}".strip()
                if pagina and dialogo.fuente_texto.size(tentativa)[0] > ANCHO_PANTALLA - 105:
                    yield dict(linea, texto=pagina)
                    pagina = palabra
                else:
                    pagina = tentativa
            yield dict(linea, texto=pagina)

    def mostrar(self, evento, despues=None, *, lineas=None, opciones=None, efectos=None,
                consumo=None, decision=None, ejecutar=None):
        nodo = GUION["eventos"].get(evento, {})
        consumo = consumo or (evento if nodo.get("una_vez") else None)
        efectos = nodo.get("efectos_al_terminar", {}) if efectos is None else efectos

        def completo():
            if self.aplicar(consumo, efectos, decision):
                if ejecutar:
                    ejecutar()
                if despues:
                    despues()
                elif nodo.get("siguiente"):
                    self.mostrar(nodo["siguiente"])

        datos = {"lineas": list(self._paginar(nodo.get("lineas", []) if lineas is None else lineas)),
                 "al_completar": completo, "desplazar_opciones": True}
        if opciones is None and nodo.get("opciones"):
            opciones = [
                opcion(item["texto"], partial(self._elegir, evento, item, completo))
                for item in nodo["opciones"]
                if not item.get("condicion") or not self.datos["carta_tomada"]
            ]
        if opciones:
            datos["opciones"] = opciones
        dialogo.datos_dialogo[evento] = datos
        dialogo.iniciar_dialogo(evento)

    def _elegir(self, evento, item, completar):
        completar()
        acciones = {
            "entrar_habitacion_abuela": partial(mapa.cargar_nivel, CUARTO),
            "tomar_carta_madre": partial(self.datos.update, carta_tomada=True),
            "dejar_carta_madre": partial(self.datos.update, carta_tomada=False),
            "cerrar_dia_normal": partial(self.cerrar, "normal"),
        }
        accion = acciones.get(item.get("accion"))
        if accion:
            accion()
        if item.get("siguiente"):
            if item.get("id"):
                self.mostrar(item["siguiente"], self.menu_morales, decision=(evento, item["texto"]))
            else:
                self.mostrar(item["siguiente"])

    def aplicar(self, consumo, efectos, decision=None):
        datos = self.datos
        if consumo in datos["consumidos"]:
            return not datos["captura_pendiente"] or mapa.nombre_mapa_actual == PRISION
        if consumo:
            datos["consumidos"].add(consumo)
            datos["revelaciones_pendientes"].discard(consumo)
        if decision:
            self.estado.registrar_decision(*decision)
        sospecha = self.estado.sospecha_pueblo
        confianza = self.estado.confianza_morales
        self.estado.aplicar_efectos(efectos)
        alcanzado = len(datos["personas"]) >= MINIMO
        if efectos.get("registrar_personaje"):
            datos["personas"].add(efectos["registrar_personaje"])
        nuevos = set(efectos.get("descubrir", ())) - datos["hallazgos"]
        datos["hallazgos"].update(nuevos)
        if self.estado.sospecha_pueblo > sospecha:
            dialogo.activar_notificacion("Sospechan más de ti", fondo=FONDO_SOSPECHA)
            for umbral in REGLAS["sospecha_avisos"]:
                if sospecha < umbral <= self.estado.sospecha_pueblo:
                    datos["consumidos"].add(f"aviso_sospecha_{umbral}")
        if (
            activa(self.estado) and not datos["captura_resuelta"] and not datos["captura_pendiente"]
            and self.estado.sospecha_pueblo >= REGLAS["sospecha_captura"]
        ):
            datos["captura_pendiente"] = True
            datos["rescate_elegible"] = self.estado.confianza_morales >= REGLAS["confianza_rescate"]
            mapa.jugador_bloqueado = True
            audio.detener_musica(fade_ms=0)
            return False
        if nuevos:
            hallazgo = sorted(nuevos)[0]
            titulo = GUION["hallazgos"][hallazgo]["titulo"]
            clave = "pista" if hallazgo in PISTAS else "hallazgo"
            dialogo.activar_notificacion(GUION["notificaciones"][clave].format(
                titulo=titulo, pistas_obtenidas=len(PISTAS & datos["hallazgos"])))
        if self.estado.confianza_morales > confianza:
            aviso = GUION["notificaciones"]["confianza_morales"]
            dialogo.activar_notificacion(aviso["texto"], fondo=aviso["color_rgb"])
        if not alcanzado and len(datos["personas"]) >= MINIMO:
            dialogo.activar_notificacion(GUION["notificaciones"]["objetivo_disponible"])
        return True

    def personaje(self, nombre):
        if nombre == "abuela":
            if self.datos["abuela_salio"]:
                self.mostrar("abuela_casa_vacia")
                return
            self.datos["abuela_visitada"] = True
        persona = GUION["personajes"][nombre]
        menu = partial(self.menu_persona, nombre)
        inicio = persona["introduccion"]
        if inicio in self.datos["consumidos"]:
            menu()
        else:
            self.mostrar(inicio, menu, consumo=inicio)

    def menu_persona(self, nombre):
        persona = GUION["personajes"][nombre]
        opciones = []
        for pregunta in persona["preguntas"]:
            consumo = pregunta["id"]
            texto = pregunta["texto"]
            lineas = None
            efectos = pregunta["efectos_al_terminar"].copy()
            for variante in pregunta.get("variantes_lineas", ()):
                if variante.get("si_no_descubierto") not in self.datos["hallazgos"]:
                    texto = variante.get("texto", texto)
                    lineas = variante["lineas"]
                    if nombre == "abuela":
                        consumo += "_temprana"
                    efectos["sospecha_pueblo"] = variante.get("sospecha_override", efectos["sospecha_pueblo"])
                    break
            if consumo not in self.datos["consumidos"]:
                opciones.append(opcion(texto, partial(
                    self.mostrar, pregunta["evento"], partial(self.menu_persona, nombre),
                    lineas=lineas, efectos=efectos, consumo=consumo, decision=(pregunta["id"], texto))))
        if not opciones:
            self.mostrar(persona["repetir_agotado"])
            return
        opciones.append(opcion("Despedirme.", partial(self.mostrar, persona["despedida"])))
        self.mostrar(f"{nombre}_temas", opciones=opciones)

    def morales(self):
        if "morales_inicio" not in self.datos["consumidos"]:
            self.mostrar("morales_inicio", self.morales_despues_de_saludar)
        else:
            self.morales_despues_de_saludar()

    def morales_despues_de_saludar(self):
        if self.estado.sospecha_pueblo >= 40 and "morales_aviso_sospecha" not in self.datos["consumidos"]:
            self.mostrar("morales_aviso_sospecha", self.menu_morales)
        elif not self.datos["hallazgos"] and "morales_sin_hallazgos" not in self.datos["consumidos"]:
            self.mostrar("morales_sin_hallazgos", self.menu_morales, consumo="morales_sin_hallazgos")
        else:
            self.menu_morales()

    def menu_morales(self):
        datos = self.datos
        menu = GUION["morales"]["menu"]
        opciones = []
        for nombre, hallazgo in GUION["hallazgos"].items():
            if nombre in datos["hallazgos"] - datos["informados"]:
                texto = menu["plantilla"].format(titulo=hallazgo["titulo"])
                opciones.append(opcion(texto, partial(self.informar, nombre)))
        for item in menu["opciones_fijas"]:
            if (
                self.estado.confianza_morales >= item.get("min_confianza", 0)
                and (not item.get("ocultar_si_completado") or item["evento"] not in datos["consumidos"])
                and (not item.get("requiere_descubierto") or item["requiere_descubierto"] in datos["hallazgos"])
            ):
                evento = item["evento"]
                vuelve = evento != "morales_despedida" and not GUION["eventos"][evento].get("opciones")
                opciones.append(opcion(item["texto"], partial(self.mostrar, evento, self.menu_morales if vuelve else None)))
        self.mostrar("morales_temas", opciones=opciones)

    def informar(self, nombre, fuente_tratada=False):
        if nombre not in self.datos["hallazgos"] - self.datos["informados"]:
            return
        if nombre == "marca_media_luna" and not fuente_tratada:
            self.mostrar("morales_fuente_reservada", partial(self.informar, nombre, True))
            return
        hallazgo = GUION["hallazgos"][nombre]
        recompensa = "confianza_informe_crucial" if nombre in PISTAS else "confianza_informe_secundario"
        self.mostrar(
            hallazgo["evento_informe"], self.despues_informe, consumo=f"informe:{nombre}",
            efectos={"confianza_morales": REGLAS[recompensa]},
            ejecutar=partial(self.datos["informados"].add, nombre),
        )

    def despues_informe(self):
        pendientes = self.datos["revelaciones_pendientes"]
        pendientes.update(
            regla["evento"] for regla in REGLAS["revelaciones_morales"]
            if self.estado.confianza_morales >= regla["min_confianza"]
            and regla["evento"] not in self.datos["consumidos"]
        )
        combinacion = GUION["morales"]["evento_combinacion"]
        if (set(combinacion["requiere_informados"]) <= self.datos["informados"]
                and combinacion["evento"] not in self.datos["consumidos"]):
            self.mostrar(combinacion["evento"], self.menu_morales)
        else:
            self.menu_morales()

    def interactuar(self, x, y, evento):
        if self.noche is not None and self.noche.exterior(x, y):
            return True
        if not activa(self.estado):
            return False
        punto = PUNTOS.get(mapa.nombre_mapa_actual, {}).get((x, y))
        if punto in GUION["personajes"]:
            self.personaje(punto)
        elif punto == "morales":
            self.morales()
        elif punto == "entrada_abuela":
            mapa._reproducir_sonido_portal(ABRIR_PUERTA)
            mapa.cargar_nivel(CASA_ABUELA, sonido_llegada=CERRAR_PUERTA)
        elif punto == "ventana_abuela":
            acceso = self.datos["abuela_salio"] and bool({"cuarto_cerrado", "objetos_elena"} & self.datos["hallazgos"])
            if self.datos["abuela_salio"] and not acceso:
                self.mostrar("ventana_sin_pista", lineas=[
                    {"hablante": "Mateo", "texto": "Hay una ventana. ¿A qué cuarto dará?"},
                ])
            else:
                self.mostrar("ventana_disponible" if acceso else "ventana_no_disponible")
        elif punto == "sillon":
            self.mostrar("sillon_esperar" if len(self.datos["personas"]) >= MINIMO else "sillon_antes_cinco")
        elif evento == "abuela_puerta_cerrada":
            lineas = None
            if "abuela_pregunta_2" not in self.datos["consumidos"]:
                lineas = [{"hablante": "Mateo", "texto": "Ese cuarto está cerrado."}]
            self.mostrar(evento, lineas=lineas, efectos={"descubrir": ["cuarto_cerrado"]}, consumo=evento)
        elif evento == "cajon_inventario":
            self.mostrar("cajon_repetir" if "caja_jm" in self.datos["hallazgos"] else evento)
        elif evento == "salida_cuarto":
            self.mostrar(evento, partial(mapa.cargar_nivel, ENTRADA, 15, 1))
        elif mapa.nombre_mapa_actual in (CASA_ABUELA, CUARTO) and evento in GUION["eventos"]:
            self.mostrar(evento)
        else:
            return False
        return True

    def actualizar(self):
        if self.noche is not None and self.noche.actualizar():
            return
        actual = mapa.nombre_mapa_actual
        datos = self.datos
        if self.revision_nivel != mapa.revision_nivel:
            self.revision_nivel = mapa.revision_nivel
            self.director = None
            if actual == CASA_ABUELA:
                abuela = mapa.npcs_activos["abuela"]
                abuela["visible"] = not datos["abuela_salio"] and bool(abuela["sprites"])
        if mapa.transicion_activa or dialogo.obtener_evento_activo() is not None:
            return
        if self.director is not None and not self.director.terminado:
            self.director.actualizar()
            return
        if datos["captura_pendiente"]:
            mapa.jugador_bloqueado = True
            secuencia = self.prision() if actual == PRISION else self.captura()
            self.director = Director(secuencia)
        elif datos["cerrada"] and not datos["reencuentro"] and actual == HOGAR:
            mapa.jugador_bloqueado = True
            self.director = Director(self.reencuentro())
        elif datos["reencuentro"] and actual == HOGAR and "lucas" not in mapa.npcs_activos:
            self.colocar_aliados()
        elif activa(self.estado):
            if self.estado.confianza_lucas_separacion is None:
                self.estado.confianza_lucas_separacion = self.estado.confianza_lucas
            if actual != CASA_ABUELA and datos["abuela_visitada"] and not datos["abuela_salio"] and len(datos["personas"]) >= MINIMO:
                datos["abuela_salio"] = True
                dialogo.activar_notificacion(GUION["notificaciones"]["objetivo_abuela"])
            if actual == PLAZA and "inicio_investigacion" not in datos["consumidos"]:
                self.mostrar("inicio_investigacion")
            elif actual == CUARTO and "cuarto_entrada" not in datos["consumidos"]:
                self.mostrar("cuarto_entrada")

    def captura(self):
        audio.detener_musica(fade_ms=0)
        recorridos = []
        for numero, (origen, ruta) in enumerate(rutas_guardias()):
            nombre = f"guardia_dia2_{numero}"
            crear_npc(nombre, "loco", *origen)
            recorridos.append(Recorrido(nombre, ruta, intervalo=180))
        if recorridos:
            yield "mover", recorridos
        yield "hacer", partial(self.mostrar, "captura_entrada")
        yield "hacer", partial(mapa.cargar_nivel, PRISION)

    def prision(self):
        from funciones_mapas import funcion_prision_dia_2 as prision

        prision.colocar_guardias()
        yield "hacer", partial(self.mostrar, "prision_inicio")
        yield "pausa", 650
        if self.datos["rescate_elegible"]:
            yield "hacer", partial(crear_npc, "morales", "morales", 6, 5, "arriba")
            yield "hacer", partial(self.mostrar, "prision_rescate")
            yield "pausa", 450
            yield "hacer", prision.abrir
            yield "hacer", partial(self.mostrar, "prision_abierta")
            yield "mover", [Recorrido("mateo", [(4, 4), (4, 6)], intervalo=200)]
            yield "hacer", partial(self.cerrar, "rescate")
        else:
            yield "hacer", partial(self.mostrar, "prision_sin_rescate")
            yield "hacer", partial(self.cerrar, "invitados_honor")
            yield "hacer", partial(self.mostrar, "inicio_invitados_honor")
            yield "hacer", self.guardar_resultado

    def cerrar(self, rama):
        self.datos.update(
            cerrada=True, rama=rama, captura_pendiente=False,
            captura_resuelta=rama != "normal",
        )
        mapa.jugador_bloqueado = True
        if rama == "rescate":
            mapa.cargar_nivel(HOGAR, 4, 6)

    def colocar_aliados(self, *, desde_puerta=False):
        posiciones = [("lucas", PUERTA_EXTERIOR if desde_puerta else DESTINO_LUCAS)]
        if self.datos["rama"] == "rescate":
            posiciones.append(("morales", (6, 5)))
        ocupados = {(mapa.mateo_x, mapa.mateo_y)}
        for nombre, destino in posiciones:
            if destino in ocupados:
                destino = (4, 5)
            direccion = "arriba" if nombre == "lucas" and desde_puerta else "der"
            crear_npc(nombre, nombre, *destino, direccion)
            ocupados.add(destino)

    def reencuentro(self):
        self.colocar_aliados(desde_puerta=True)
        yield "hacer", partial(mapa._reproducir_sonido_portal, ABRIR_PUERTA)
        yield "mover", [Recorrido("lucas", [(8, 6), (5, 6), DESTINO_LUCAS], intervalo=180)]
        yield "hacer", partial(mirar, "lucas", "der")
        rama = self.datos["rama"]
        yield "hacer", partial(self.mostrar, f"reencuentro_{rama}")
        pistas = PISTAS & self.datos["hallazgos"]
        colabora = self.lucas_colabora()
        if "caja_jm" in pistas:
            nivel = "alta" if colabora else "baja"
            yield "hacer", partial(self.mostrar, f"lucas_caja_confianza_{nivel}")
            if colabora:
                evento = "lucas_tres_pistas" if pistas == PISTAS else "lucas_pistas_incompletas"
                yield "hacer", partial(self.mostrar, evento)
        elif colabora:
            yield "hacer", partial(self.mostrar, "lucas_sin_caja")
        else:
            yield "hacer", partial(self.mostrar, "lucas_sin_caja_baja", lineas=[
                {"hablante": "Lucas", "texto": "Vi movimiento cerca de la oficina municipal. No me quedé a averiguar más."},
                {"hablante": "Mateo", "texto": "Entonces todavía nos falta por dónde empezar."},
            ])
        yield "hacer", self.guardar_resultado

    def lucas_colabora(self):
        confianza = self.estado.confianza_lucas_separacion
        if confianza is None:
            confianza = self.estado.confianza_lucas
        return confianza >= CONFIANZA_LUCAS

    def guardar_resultado(self):
        datos = self.datos
        honor = datos["rama"] == "invitados_honor"
        pistas = PISTAS & datos["hallazgos"]
        lucas = self.lucas_colabora()
        datos["reencuentro"] = not honor
        datos["resultado"] = {
            "pistas": set(pistas), "informes": set(datos["informados"]),
            "lucas_colabora": lucas,
            "morales_aliado": self.estado.confianza_morales >= REGLAS["confianza_rescate"],
            "plan_llave": not honor and lucas and pistas == PISTAS,
            "continuacion": "invitados_honor" if honor else "emboscada_nocturna",
            "reencuentro_oficina": True,
            "ubicacion_llave": "oficina" if lucas and "caja_jm" in pistas and not honor else None,
        }
        if honor:
            self.estado.dia3["origen_honor"] = "dia"
            return
        # El mapa permite usar la libreta del hogar en el punto de continuación.
        mapa.jugador_bloqueado = False
        if self.autoguardar:
            guardado.solicitar("automatico", mapa_destino=mapa.nombre_mapa_actual)


def rutas_guardias():
    """Rutas cortas disjuntas desde posiciones libres alrededor de Mateo."""
    x, y = mapa.mateo_x, mapa.mateo_y
    usados = {(x, y)} | {
        (npc["x"], npc["y"]) for npc in mapa.npcs_activos.values() if npc["visible"]
    }

    def vecinos(punto):
        px, py = punto
        for candidato in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
            cx, cy = candidato
            if candidato in usados or mapa.casilla_bloqueada(cx, cy):
                continue
            casilla = mapa.matriz_activa[cy][cx]
            if casilla not in mapa.portales_activos and casilla not in mapa.triggers_pisar_activos:
                yield candidato

    destinos = list(vecinos((x, y)))[:3]
    usados.update(destinos)
    for destino in destinos:
        pendientes = deque([(destino, ())])
        vistos = {destino}
        origen, ruta = destino, ()
        while pendientes:
            origen, ruta = pendientes.popleft()
            if len(ruta) == 3:
                break
            for vecino in vecinos(origen):
                if vecino not in vistos:
                    vistos.add(vecino)
                    pendientes.append((vecino, (origen, *ruta)))
        usados.update((origen, *ruta))
        yield origen, ruta
