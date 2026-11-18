# mapas/casa.py

FONDO_IMG = "recursos/sprites/fondos/fondo_casa.png"

# Sin AMBIENTE: conservar la música que ya está sonando.
INICIO_X = 3
INICIO_Y = 1

NPCS = {
    "lucas": {
        "x": 3,
        "y": 2,
        "direccion": "abajo",
        "visible": True,
        "carpeta_sprite": "lucas",
        "comportamiento": "sigue_jugador",
        "seguimiento": {
            "velocidad_ms": 300,
        },
    },
}

INTERACTUABLES = {
    # Diálogos de datos/comunes.json.
    2: "evento_casa",
    3: "evento_maceta",
    7: "evento_maceta_pequena",
    8: "evento_barril",
    9: "evento_banca",

    # Diálogos propios de este mapa.
    12: "evento_niña_aro",
    13: "evento_banca_rayada",
    14: "evento_vecino",
    15: "evento_tronco_zapatos",
    16: "evento_casa_puerta",
}

TRIGGERS_PISAR = {}
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
BLOQUEOS = []

# La puerta empieza como interactuable 16.
# El director la convierte en portal 97 al terminar su diálogo.
PUERTA_X = 18
PUERTA_Y = 16

PORTALES = {
    98: {
        "mapa": "pueblo_1",
        "spawn_x": 9,
        "spawn_y": 28,
    },
    97: {
        "mapa": "hogar",
        # Cuando exista hogar, usará su INICIO_X e INICIO_Y.
    },
}

# 800 × 1000 píxeles: 20 columnas × 25 filas.
#
# 0 = suelo libre
# 1 = colisión sin diálogo
# 2, 3, 7, 8, 9 = objetos con diálogo común
# 12 = niña
# 13 = parte rayada de la banca derecha
# 14 = vecino
# 15 = tronco
# 16 = puerta antes de abrirse
# 97 = puerta habilitada
# 98 = regreso a Pueblo_1
#
# Las filas inferiores de las casas quedan libres,
# excepto donde hay un objeto, una banca o la puerta especial.

MATRIZ = [
    #0  1  2   3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
    [0, 0, 0, 98, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 0
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 1
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 2
    [21, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 7, 3, 0, 0, 0, 0, 7],  # y = 3
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 4
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0],  # y = 5
    [21, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 6
    [0, 0, 0, 0, 3, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 7
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 8
    [21, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 9
    [0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 9, 9, 0, 7, 0, 0, 0, 9, 13, 0],  # y = 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 11
    [21, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 12
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1],  # y = 13
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1],  # y = 14
    [21, 0, 0, 0, 3, 0, 0, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1],  # y = 15
    [0, 8, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 7, 7, 0, 0, 0, 0, 16, 0],  # y = 16
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 17
    [21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 18
    [0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 19
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 20
    [21, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 21
    [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2],  # y = 22
    [0, 0, 15, 15, 15, 0, 7, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0],  # y = 23
    [21, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # y = 24
]