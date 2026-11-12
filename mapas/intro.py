FONDO_IMG = "recursos/sprites/fondos/intro_fondo.png"  # El fondo que diseñes
INICIO_X = 7
INICIO_Y = 7

NPCS = {
    "lucas": {
        "x": 8,
        "y": 7,
        "direccion": "izq",
        "visible": True,
        "carpeta_sprite": "lucas",
        "comportamiento": "patrulla",
        "patrulla": {
            "velocidad_ms": 200,
            "hasta_x": 19,  # Camina hasta el borde derecho de la matriz (20 columnas: índices 0..19)
            "empuja_jugador": False
        }
    }
}

PORTALES = {
    99: { "mapa": "prologo", "spawn_x": 1, "spawn_y": 15 }
}

# Una matriz simple de ejemplo. 2 es carretera, 0 es tierra, 1 es límite/árbol
MATRIZ = [
    [1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 2, 2, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 2, 2, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 2, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 2, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 99],
    [1, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 99],
    [1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

DICCIONARIO_OBJETOS = {
    # Aquí puedes añadir tiles, por ejemplo:
    # 2: {"ruta": "recursos/sprites/entorno/carretera.png", "colision": False}
}