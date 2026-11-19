"""Interior de 400x300; casillas de 40 px. MATRIZ[y][x]."""
FONDO_IMG = "recursos/sprites/fondos/fondo_hogar_noche_1.png"
CENTRAR_FONDO = True
INICIO_X, INICIO_Y = 1, 2

# Sin AMBIENTE: continúa la música del mapa anterior.
NPCS = {}
INTERACTUABLES = {}
PORTALES = {
    97: {
        "mapa": "habitaciones_noche_1",
        "spawn_x": 2,
        "spawn_y": 3,
        "sonido_entrada": (
            "recursos/sonidos/efectos/open_door.wav"
        ),
    },
}
TRIGGERS_PISAR = {}
DICCIONARIO_OBJETOS = {}  # Los muebles ya están dibujados en el fondo.
BLOQUEOS = []

# 0 libre; 1 muro; los otros números bloquean y permiten interactuar.
# La fila 7 solo tiene 20 píxeles visibles: está totalmente bloqueada.
MATRIZ = [
    # 0  1  2  3  4  5  6  7  8  9
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],       # 0
    [1, 97, 1, 1, 1, 1, 1, 1, 1, 1],       # 1
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],       # 2
    [0, 0, 1, 1, 0, 0, 0, 1, 1, 0],       # 3
    [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],       # 4
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 0],       # 5
    [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],       # 6
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],       # 7
]
