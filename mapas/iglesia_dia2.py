from mapas import casa


FONDO_IMG = "recursos/sprites/fondos/fondo_iglesia_dia2.png"
INICIO_X, INICIO_Y = 1, 7
ENTRADA_IGLESIA = (5, 4)
REGRESO_INTERIOR = (5, 5)
ESCONDITE_MORALES = (10, 3)
PUERTA_OFICINA = (15, 12)
ARBOL_RETIRADO = (18, 14)
FACHADA_OFICINA = tuple((x, y) for y in range(9, 13) for x in range(14, 20))
SALIDA_PUEBLO = (0, 7)
REGRESO_PUEBLO = (1, 7)
POSICIONES_NINOS = ((5, 10), (6, 11), (7, 12))
NINOS = tuple(f"nino_{indice}" for indice in range(1, 4))
DICCIONARIO_OBJETOS = casa.DICCIONARIO_OBJETOS
AMBIENTE = "miradas"
VOLUMEN_AMBIENTE = 0.4

NPCS = {
    "lucas": {
        "x": 2,
        "y": 7,
        "direccion": "izq",
        "carpeta_sprite": "lucas",
        "comportamiento": "estatico",
        "seguimiento": {"velocidad_ms": 300},
    },
    "morales": {
        "x": ESCONDITE_MORALES[0],
        "y": ESCONDITE_MORALES[1],
        "direccion": "izq",
        "carpeta_sprite": "morales",
    },
}

for indice, (nombre, (x, y)) in enumerate(zip(NINOS, POSICIONES_NINOS), 1):
    carpeta = "recursos/sprites/personajes/genericos"
    NPCS[nombre] = {
        "x": x,
        "y": y,
        "sprites_especiales": {
            "jugando": f"{carpeta}/nino_jugando_{indice}.png",
            "espaldas": f"{carpeta}/nino_espaldas_{indice}.png",
        },
        "sprite_override": "jugando",
    }

INTERACTUABLES = {2: "evento_reunion_morales", 3: "evento_ninos_jugando"}
PORTALES = {97: {"mapa": "pueblo_2_dia_2", "spawn_x": 38, "spawn_y": 7}}

# Colisiones de iglesia, setos, troncos y fuente. La senda queda libre.
MATRIZ = [
    # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

x, y = ESCONDITE_MORALES
MATRIZ[y][x] = 2
for x, y in POSICIONES_NINOS:
    MATRIZ[y][x] = 3
for x in (2, 8, 14):
    MATRIZ[9][x] = 20
for fila in MATRIZ:
    fila[-1] = 1
for x, y in ((18, 2), (19, 3), (17, 5), (19, 6), (18, 7), (19, 7), (18, 8),
             (19, 9), (17, 11), (19, 12)):
    MATRIZ[y][x] = 21

# Fachada municipal incorporada al fondo, al este de la fuente.
for x, y in FACHADA_OFICINA:
    MATRIZ[y][x] = 1
