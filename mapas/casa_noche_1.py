FONDO_IMG = "recursos/sprites/fondos/fondo_casa_noche_1.png"
AMBIENTE = "noche_calmada"
VOLUMEN_AMBIENTE = 0.4

# Frente a la puerta de la casa roja.
INICIO_X = 18
INICIO_Y = 17

NPCS = {
    "lucas": {
        "x": 17,
        "y": 17,
        "direccion": "izq",
        "visible": True,
        "carpeta_sprite": "lucas",
        "comportamiento": "sigue_jugador",
        "seguimiento": {
            "velocidad_ms": 300,
        },
    },
    "loco": {
        "x": 5,
        "y": 5,
        "direccion": "izq",
        "visible": True,
        "carpeta_sprite": "loco",
        "comportamiento": "vigilante",
        "vigilancia": {
            "luz": "recursos/sprites/efectos/luz_3.png",
            "ruta": [],
            "miradas": [
                ("izq", 4000),
                ("der", 3500),
            ],
        },
    },
}

INTERACTUABLES = {}
TRIGGERS_PISAR = {}
BLOQUEOS = []
# Coordenadas (columna, fila).
BARRILES = {
    (1, 16),
}

DICCIONARIO_OBJETOS = {
    20: {
        "ruta": "recursos/sprites/objetos/Poste_prendido.png",
        "colision": True,
        "profundidad": True,
        "ancho_casillas": 1,
        "alto_casillas": 4,
    },
    21: {
        "ruta": "recursos/sprites/natural/arbol_grande_noche.png",
        "colision": True,
        "profundidad": True,
        "ancho_casillas": 4,
        "alto_casillas": 4,
    },
}

PORTALES = {
    97: {
        "mapa": "hogar_noche_1",
        "spawn_x": 8,
        "spawn_y": 6,
        "sonido_entrada": "recursos/sonidos/efectos/open_door.wav",
    },
    98: {
        "mapa": "pueblo_1_noche_1",
        "spawn_x": 9,
        "spawn_y": 28,
    },
}

# 800 × 1000: 20 columnas × 25 filas.
# 0 = libre
# 1 = colisión sin diálogo
# 20 = poste con colisión en su base
# 21 = árbol con colisión en su casilla base
# 97 = hogar nocturno
# 98 = pueblo nocturno

MATRIZ = [
    #0  1  2   3  4   5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
    [0, 0, 0, 98, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],  # 0
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 1
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 2
    [21, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],  # 3
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 4
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 5
    [21, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 6
    [0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 7
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 8
    [21, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],  # 9
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],   # 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 11
    [21, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # 12
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 13
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 14
    [21, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],  # 15
    [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 97, 0],  # 16
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],   # 17
    [21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 18
    [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 19
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 20
    [21, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],  # 21
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],   # 22
    [0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],   # 23
    [21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 24
]