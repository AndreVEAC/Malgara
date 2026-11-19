FONDO_IMG = "recursos/sprites/fondos/fondo_habitaciones.png"

AMBIENTE = "Refuge"
VOLUMEN_AMBIENTE = 0.4

# Aparecer delante de la puerta, sin pisar el portal de regreso.
INICIO_X = 2
INICIO_Y = 3

# Lucas ya está durmiendo; su cama tiene un diálogo.
NPCS = {}

INTERACTUABLES = {
    2: "evento_cama_lucas",
    3: "evento_cama_mateo",
    4: "evento_mesita",
}

PORTALES = {
    98: {
        "mapa": "hogar",
        "spawn_x": 1,
        "spawn_y": 2,
        "sonido_entrada": (
            "recursos/sonidos/efectos/open_door.wav"
        ),
    },
}

TRIGGERS_PISAR = {}
DICCIONARIO_OBJETOS = {}
BLOQUEOS = []

# 200×200 píxeles: 5 columnas y 5 filas.
#
# 0 = suelo libre
# 1 = pared
# 2 = cama de Lucas
# 3 = cama de Mateo
# 4 = mesitas
# 98 = puerta de regreso
#
# MATRIZ[y][x]

MATRIZ = [
    # 0  1  2  3  4
    [1, 1, 1, 1, 1],   # y = 0
    [1, 1, 1, 1, 1],   # y = 1
    [3, 4, 0, 4, 2],   # y = 2
    [3, 0, 0, 0, 2],   # y = 3
    [0, 0,98, 0, 0],   # y = 4
]