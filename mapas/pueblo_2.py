# mapas/pueblo_2_cinematica.py

FONDO_IMG = "recursos/sprites/fondos/fondo_pueblo_2.png"

INICIO_X = 1
INICIO_Y = 7

NPCS = {
    "lucas": {
        "x": 20,
        "y": 14,
        "direccion": "arriba",
        "visible": True,
        "carpeta_sprite": "lucas",
        "comportamiento": "sigue_jugador",
        "seguimiento": {
            "velocidad_ms": 300
        }
    }
}

INTERACTUABLES = {
    2: "evento_casa",
    3: "evento_estatua",
    4: "evento_carreta",
    5: "evento_altar",
    6: "evento_maceta_grande",
    7: "evento_maceta_pequena",
    8: "evento_barril",
    9: "evento_banca",

    12: "evento_pers_1_musico",
    13: "evento_pers_2_cocinera",
    14: "evento_pers_3_niño",
    15: "evento_pers_4_amargado",
    16: "evento_pers_5_borracho",
    17: "evento_pers_6_niña",
}
# El director detectará la posición (9, 7).
# No usamos TRIGGERS_PISAR porque esos abren diálogos
# directamente, mientras aquí necesitamos dirigir la escena.
TRIGGERS_PISAR = {}

PORTALES = {
    98: {
        "mapa": "pueblo_1",
        "spawn_x": 38,
        "spawn_y": 7
    },
    97: {
        "mapa": "pueblo_1",
        "spawn_x": 38,
        "spawn_y": 14
    },
    96: {
        "mapa": "pueblo_1",
        "spawn_x": 38,
        "spawn_y": 21
    }
}

# mapas/pueblo_1.py

BLOQUEOS = [
    {
        "id": "acceso_casa",
        "ruta": "recursos/sprites/objetos/caja_bloqueo.png",
        "casillas": [
            (31, 29),
            (32, 29),
            (39,6),
            (39,7),
            (39,8)
        ],
        "dialogo": "evento_camino_bloqueado",
        "desbloquear_con": None,
    },
]

DICCIONARIO_OBJETOS = {
    20: {
        "ruta": "recursos/sprites/objetos/poste apagado.png",
        "colision": True,
        "profundidad": True,
        "ancho_casillas": 1,
        "alto_casillas": 4
    },
    21: {
        "ruta": "recursos/sprites/natural/arbol grande.png",
        "colision": True,
        "profundidad": True,
        "ancho_casillas": 4,
        "alto_casillas": 4
    }
}

# Coordenadas de la escena, para que las utilice el director.
TRIGGER_CINEMATICA = (9, 7)

DESTINO_MATEO = (19, 14)
DESTINO_LUCAS = (20, 14)

# 1600 × 1200 píxeles.
# 40 columnas × 30 filas.
#
# 0 = libre
# 1 = bloqueado
#
# MATRIZ[y][x]

MATRIZ = [
    #0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],  # y = 0
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 5, 5, 5, 5, 0],  # y = 1
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 5, 5, 5, 5, 13],  # y = 2
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],  # y = 3
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 4
    [0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 1, 0, 0, 1, 20, 0, 0, 0, 0, 0, 1, 0, 14, 20, 0, 0, 1, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0],  # y = 5
    [98, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 6
    [98, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 7
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 8
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # y = 9
    [97, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 10
    [97, 1, 1, 0, 1, 1, 0, 1, 21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 15, 1, 0],  # y = 11
    [97, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 0, 0, 0, 0, 21],  # y = 12
    [97, 0, 3, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 13
    [97, 0, 3, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0],  # y = 14
    [97, 0, 3, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 15
    [97, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 0, 0, 0, 0, 21],  # y = 16
    [97, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0],  # y = 17
    [97, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0],  # y = 18
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0],  # y = 19
    [0, 1, 0, 0, 17, 0, 1, 0, 21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0],  # y = 20
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 0],  # y = 21
    [96, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 16, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 22
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 23
    [0, 0, 0, 21, 0, 0, 0, 20, 0, 0, 0, 21, 0, 0, 0, 0, 0, 20, 0, 0, 0, 21, 0, 0, 0, 0, 20, 0, 0, 0, 1, 0, 0, 1, 0, 20, 0, 0, 0, 21],  # y = 24
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 25
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 26
    [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # y = 27
    [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],  # y = 28
    [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 21, 0, 0, 0, 0, 21, 0, 0, 1, 1, 1],  # y = 29
]

# Casas superiores.
for izquierda, derecha in ((0, 5), (9, 14), (18, 23), (27, 32)):
    for y in range(0, 4):
        for x in range(izquierda, derecha + 1):
            MATRIZ[y][x] = 2

# Casas inferiores.
for izquierda, derecha in ((1, 6), (10, 15), (19, 24), (37, 39)):
    for y in range(27, 30):
        for x in range(izquierda, derecha + 1):
            MATRIZ[y][x] = 2

# Macetas grandes: mismas casillas de colisión de la matriz anterior.
for x, y in (
    (34, 9),
    (30, 23),
    (30, 24),
    (33, 24),
):
    MATRIZ[y][x] = 6

# Macetas pequeñas.
for x, y in (
    (1, 4),
    (12, 5),
    (22, 5),
    (28, 5),
    (1, 20),
    (6, 20),
):
    MATRIZ[y][x] = 7

# Barriles rojos.
for x, y in ((15, 5), (19, 22)):
    MATRIZ[y][x] = 8

# Bancas del jardín.
for x in (1, 2, 4, 5):
    MATRIZ[11][x] = 9

# Bancas de la derecha.
for y in (11, 14):
    for x in (34, 35, 37, 38):
        # No reemplazar al personaje sentado.
        if MATRIZ[y][x] == 1:
            MATRIZ[y][x] = 9