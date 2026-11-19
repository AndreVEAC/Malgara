FONDO_IMG = (
    "recursos/sprites/fondos/fondo_habitaciones_noche_1.png"
)

INICIO_X = 3
INICIO_Y = 3

NPCS = {
    "lucas": {
        "x": 1,
        "y": 3,
        "direccion": "der",
        "visible": True,
        "carpeta_sprite": "lucas",
        "comportamiento": "estatico",
    }
}

# De noche, los muebles solo tienen colisión.
INTERACTUABLES = {}
TRIGGERS_PISAR = {}
DICCIONARIO_OBJETOS = {}
BLOQUEOS = []

PORTALES = {
    99: {
        "mapa": "hogar_noche_1",
        "spawn_x": 1,
        "spawn_y": 2,
        "sonido_entrada": (
            "recursos/sonidos/efectos/open_door.wav"
        ),
    }
}

# La puerta comienza bloqueada.
# El director la habilita al terminar la escena,
# cuando exista el siguiente mapa.
MATRIZ = [
    # 0  1  2  3  4
    [1, 1, 1, 1, 1],  # y = 0
    [1, 1, 1, 1, 1],  # y = 1
    [1, 1, 0, 1, 1],  # y = 2
    [1, 0, 0, 0, 1],  # y = 3
    [0, 0, 99, 0, 0],  # y = 4
]