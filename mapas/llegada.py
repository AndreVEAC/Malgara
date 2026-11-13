INICIO_X = 2
INICIO_Y = 7
FONDO_IMG = "recursos/sprites/fondos/fondo_entrada.png"

INTERACTUABLES = {
    10: "evento_pozo",
    11: "evento_casa"
}

# --- SISTEMA GENÉRICO DE NPCs ---
NPCS = {
    "lucas": {
        "x": 2,
        "y": 8,
        "direccion": "der",
        "carpeta_sprite": "lucas",
        "visible": True,
        "comportamiento": "estatico"
    },
    "abuela": {
        "x": 16,
        "y": 5,
        "direccion": "abajo",
        "carpeta_sprite": "abuela",
        "visible": True,
        "comportamiento": "estatico"
    }
}

PORTALES = {
    98: {
        "mapa": "prologo",
        "spawn_x": 37,
        "spawn_y": 15
    },
    99: {
        "mapa": "pueblo_1",
        "spawn_x": 2,
        "spawn_y": 8
    }
}
# Matriz completa para exploración y cinemática (15 filas x 20 columnas)
# 1 = Colisión de la casa / muros
# 10 = Colisión interactuable del pozo
# 11 = Colisión interactuable de la casa
MATRIZ = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 11, 11, 11, 11, 11, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 11, 11, 11, 11, 11, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 11, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [98, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 99],
    [98, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 99],
    [98, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 99],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

DICCIONARIO_OBJETOS = {}