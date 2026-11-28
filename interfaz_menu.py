"""Menú principal y selector de guardados de Malgara."""
from datetime import datetime
from math import cos, pi

import pygame

import sistema_guardado as guardado


FONDO = "recursos/sprites/fondos/fondo_menu.png"
LOGO = "recursos/sprites/objetos/titulo_malgara.png"
FUENTE = "recursos/fuentes/VT323-Regular.ttf"
CLARO = (239, 229, 211)
SUAVE = (180, 168, 154)
DORADO = (240, 197, 128)
NOMBRES_RANURAS = {"manual": "Guardado manual", "automatico": "Guardado automático"}
NOMBRES_MAPAS = {
    "pueblo_1_oficina": "Pueblo 1", "pueblo_1_clinica": "Pueblo 1", "pueblo_2_clinica": "Pueblo 2",
    "documentos_dia_3": "Habitación de la llave", "escotilla_dia_3": "Escotilla",
    "acceso_servicio_dia_3": "Acceso de servicio", "hogar_dia2": "Casa de Elena",
}


def resumen(partida):
    mapa = partida["mapa"]
    nombre = NOMBRES_MAPAS.get(mapa)
    if nombre is None:
        for sufijo in ("_dia_3", "_dia_2", "_dia2", "_noche_2", "_noche_1"):
            mapa = mapa.removesuffix(sufijo)
        nombre = mapa.replace("_", " ").capitalize()
    return f'Día {partida["dia"]} · {nombre}'


class MenuOpciones:
    def __init__(self):
        self.partidas = guardado.listar_partidas()
        self.vista = "principal"
        self.seleccion = 0 if self.partidas else 2
        self.error = ""
        self.fuente = pygame.font.Font(FUENTE, 32)
        self.detalle = pygame.font.Font(FUENTE, 21)
        self.fuente_teclas = pygame.font.Font(FUENTE, 21)
        self.fuente_teclas.set_bold(True)
        self.titulo = pygame.font.Font(FUENTE, 36)
        self.sonido_teclas = pygame.mixer.Sound("recursos/sonidos/efectos/teclas_menu.wav")
        self.sonido_teclas.set_volume(0.5)
        self.sonido_aceptar = pygame.mixer.Sound("recursos/sonidos/efectos/aceptar_menu.mp3")
        self.sonido_aceptar.set_volume(0.6)
        pygame.mixer.set_reserved(1)
        self.canal_menu = pygame.mixer.Channel(0)

    def cambiar_vista(self, vista):
        self.vista = vista
        self.error = ""
        self.seleccion = next(i for i, (_, _, accion) in enumerate(self.opciones()) if accion)

    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN:
            return None
        if evento.key == pygame.K_ESCAPE and self.vista != "principal":
            self.canal_menu.play(self.sonido_aceptar)
            self.cambiar_vista("principal")
            return None
        opciones = self.opciones()
        if evento.key in (pygame.K_UP, pygame.K_DOWN):
            seleccion_anterior = self.seleccion
            paso = 1 if evento.key == pygame.K_DOWN else -1
            self.seleccion = (self.seleccion + paso) % len(opciones)
            while not opciones[self.seleccion][2]:
                self.seleccion = (self.seleccion + paso) % len(opciones)
            if self.seleccion != seleccion_anterior:
                self.canal_menu.play(self.sonido_teclas)
        if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            accion = opciones[self.seleccion][2]
            if accion:
                self.canal_menu.play(self.sonido_aceptar)
            if accion in ("cargar", "confirmar", "volver"):
                self.cambiar_vista("principal" if accion == "volver" else accion)
            else:
                return accion
        return None

    def dibujar_opciones(self, pantalla, base_y):
        centro_x = pantalla.get_rect().centerx
        for indice, (nombre, detalle, accion) in enumerate(self.opciones()):
            rect = pygame.Rect(0, 0, min(470, pantalla.get_width() - 48), 61 if detalle else 49)
            rect.midtop = (centro_x, base_y)
            elegido = self.seleccion == indice
            pygame.draw.rect(pantalla, (45, 31, 29) if elegido else (25, 20, 22), rect, border_radius=4)
            pygame.draw.rect(pantalla, DORADO if elegido else (73, 57, 51), rect, 1, border_radius=4)
            if elegido:
                pygame.draw.rect(pantalla, DORADO, (rect.left + 1, rect.top + 10, 3, rect.height - 20))
            color = DORADO if elegido else CLARO if accion else SUAVE
            texto = self.fuente.render(nombre, True, color)
            pantalla.blit(texto, (rect.left + 19, rect.top + (4 if detalle else 8)))
            if detalle:
                linea = self.detalle.render(detalle, True, SUAVE)
                pantalla.blit(linea, (rect.left + 20, rect.top + 33))
            base_y += rect.height + 9
        if self.error:
            self.dibujar_texto(pantalla, self.error, self.detalle, DORADO, (centro_x, base_y + 8))

    @staticmethod
    def dibujar_texto(pantalla, texto, fuente, color, centro):
        imagen = fuente.render(texto, True, color)
        pantalla.blit(imagen, imagen.get_rect(center=centro))

    def dibujar_atajos(self, pantalla, *, volver=False, pantalla_completa=False):
        atajos = [("Flechas", "Mover"), ("Enter / Espacio", "Elegir")]
        if volver:
            atajos.append(("Esc", "Volver"))
        if pantalla_completa:
            atajos.append(("F11", "Pantalla completa"))

        grupos = [(self.fuente_teclas.render(tecla, True, CLARO), self.detalle.render(accion, True, SUAVE))
                  for tecla, accion in atajos]
        ancho = sum(tecla.get_width() + accion.get_width() + 8 for tecla, accion in grupos)
        ancho += 22 * (len(grupos) - 1)
        x = (pantalla.get_width() - ancho) // 2
        y = pantalla.get_height() - 31
        for tecla, accion in grupos:
            pantalla.blit(tecla, tecla.get_rect(midleft=(x, y)))
            x += tecla.get_width() + 8
            pantalla.blit(accion, accion.get_rect(midleft=(x, y)))
            x += accion.get_width() + 22


class MenuPrincipal(MenuOpciones):
    def __init__(self, pantalla):
        super().__init__()
        self.inicio_fondo = pygame.time.get_ticks()
        self.preparar_fondo(pantalla.get_size())

        logo = pygame.image.load(LOGO).convert_alpha()
        logo = logo.subsurface(logo.get_bounding_rect())
        self.logo_original = logo.copy()
        self.ajustar_logo(pantalla.get_width())

    def ajustar_logo(self, ancho_pantalla):
        ancho = min(550, ancho_pantalla - 64)
        alto = round(self.logo_original.get_height() * ancho / self.logo_original.get_width())
        self.logo = pygame.transform.smoothscale(self.logo_original, (ancho, alto))

    def preparar_fondo(self, tamano):
        imagen = pygame.image.load(FONDO).convert()
        ancho, alto = tamano
        self.recorrido_fondo = round(ancho * 0.09)
        escala = max((ancho + self.recorrido_fondo) / imagen.get_width(), alto / imagen.get_height())
        self.fondo = pygame.transform.scale(imagen, (round(imagen.get_width() * escala),
                                                       round(imagen.get_height() * escala)))
        self.sombra = pygame.Surface(tamano, pygame.SRCALPHA)
        for y in range(alto):
            opacidad = round(164 + 71 * (y / max(1, alto - 1)))
            pygame.draw.line(self.sombra, (15, 11, 13, opacidad), (0, y), (ancho, y))

    def opciones(self):
        if self.vista == "cargar":
            ranuras = {partida["ranura"]: partida for partida in self.partidas}
            filas = []
            for clave, etiqueta in NOMBRES_RANURAS.items():
                partida = ranuras.get(clave)
                if partida:
                    fecha = datetime.fromtimestamp(partida["fecha_ns"] // 1_000_000_000)
                    detalle = f'{resumen(partida)} · {fecha:%d/%m/%Y %H:%M}'
                else:
                    detalle = "Ranura vacía"
                filas.append((etiqueta, detalle, clave if partida else None))
            return [*filas, ("Volver", "", "volver")]
        if self.vista == "confirmar":
            return [("Volver", "", "volver"), ("Empezar nueva partida", "", "nueva")]
        reciente = self.partidas[0] if self.partidas else None
        detalle = (f'{resumen(reciente)} · {NOMBRES_RANURAS[reciente["ranura"]]}'
                   if reciente else "Todavía no hay una partida guardada")
        return [
            ("Continuar", detalle, reciente["ranura"] if reciente else None),
            ("Cargar partida", "", "cargar" if reciente else None),
            ("Nueva partida", "", "confirmar" if reciente else "nueva"),
            ("Salir", "", "salir"),
        ]

    def dibujar(self, pantalla):
        if self.sombra.get_size() != pantalla.get_size():
            self.preparar_fondo(pantalla.get_size())
            self.ajustar_logo(pantalla.get_width())
        transcurrido = pygame.time.get_ticks() - self.inicio_fondo
        progreso = (1 - cos(2 * pi * (transcurrido % 48_000) / 48_000)) / 2
        fondo = self.fondo.get_rect(center=pantalla.get_rect().center)
        fondo.x += round((progreso - 0.5) * self.recorrido_fondo)
        pantalla.blit(self.fondo, fondo)
        pantalla.blit(self.sombra, (0, 0))
        centro_x, centro_y = pantalla.get_rect().center
        pantalla.blit(self.logo, self.logo.get_rect(center=(centro_x, centro_y - 171)))
        base_y = centro_y - 84
        if self.vista == "cargar":
            self.dibujar_texto(pantalla, "Cargar partida", self.titulo, CLARO, (centro_x, base_y))
            base_y += 33
        elif self.vista == "confirmar":
            self.dibujar_texto(pantalla, "¿Empezar una nueva partida?", self.titulo, CLARO, (centro_x, base_y))
            hay_automatico = any(partida["ranura"] == "automatico" for partida in self.partidas)
            aviso = ("El próximo autoguardado puede reemplazar el anterior." if hay_automatico
                     else "Tu guardado manual se conserva.")
            self.dibujar_texto(pantalla, aviso, self.detalle, SUAVE, (centro_x, base_y + 37))
            base_y += 74

        self.dibujar_opciones(pantalla, base_y)
        self.dibujar_atajos(pantalla, volver=self.vista != "principal", pantalla_completa=True)


class MenuPausa(MenuOpciones):
    def __init__(self, pantalla):
        super().__init__()
        self.seleccion = 0
        self.fotograma = pantalla.copy()
        sombra = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        sombra.fill((14, 11, 14, 164))
        self.fotograma.blit(sombra, (0, 0))

    def opciones(self):
        if self.vista == "confirmar":
            ranura = self.partidas[0]["ranura"]
            return [("Volver", "", "volver"), ("Cargar último guardado", "", ranura)]
        reciente = self.partidas[0] if self.partidas else None
        detalle = (f'{resumen(reciente)} · {NOMBRES_RANURAS[reciente["ranura"]]}'
                   if reciente else "Todavía no hay una partida guardada")
        return [("Reanudar", "", "reanudar"),
                ("Cargar partida", detalle, "confirmar" if reciente else None),
                ("Regresar al menú", "", "menu")]

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE and self.vista == "principal":
            self.canal_menu.play(self.sonido_aceptar)
            return "reanudar"
        return super().manejar_evento(evento)

    def dibujar(self, pantalla):
        tamano = pantalla.get_size()
        fondo = self.fotograma if self.fotograma.get_size() == tamano else pygame.transform.scale(self.fotograma, tamano)
        pantalla.blit(fondo, (0, 0))
        centro_x, centro_y = pantalla.get_rect().center
        confirmar = self.vista == "confirmar"
        titulo = "¿Cargar el último guardado?" if confirmar else "Pausa"
        self.dibujar_texto(pantalla, titulo, self.titulo, CLARO, (centro_x, centro_y - 106))
        if confirmar:
            self.dibujar_texto(pantalla, "Perderás el progreso sin guardar.",
                               self.detalle, SUAVE, (centro_x, centro_y - 68))
        self.dibujar_opciones(pantalla, centro_y - 40)
        self.dibujar_atajos(pantalla, volver=True)
