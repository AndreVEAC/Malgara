"""Geografía de la ruta de oficina, separada de las variantes nocturnas."""
from types import SimpleNamespace

from mapas import dentro_iglesia, iglesia_dia2, prision_dia_2, pueblo_1, pueblo_1_dia_3, pueblo_2_dia_2, pueblo_3_dia_2, tunel
from mapas.geografia_noche_2 import marcar, matriz_desde, paso, vigilante

PUEBLO = "pueblo_1_oficina"
PLAZA = "pueblo_2_dia_3"
EXTERIOR = "iglesia_dia_3"
OFICINA = "oficina_dia_3"
IGLESIA = "dentro_iglesia_dia_3"
TUNEL = "tunel_dia_3"
CUARTO = "documentos_dia_3"
BOSQUE = "bosque_dia_3"
LAB = "laboratorio_dia_3"
ACCESO = "escotilla_dia_3"
PRISION = "prision_laboratorio"
ENCUENTRO = (17, 8)
ESCRITORIO = (13, 4)
ESCOTILLA = (37, 22)
ARBUSTOS = ((36, 22), ESCOTILLA)
ENTRADA_BOSQUE = (38, 6)


def fondo(nombre):
    return f"recursos/sprites/fondos/{nombre}.png"


def nivel(nombre, matriz, entrada, *, ambiente="ultimo_paseo", **atributos):
    return SimpleNamespace(FONDO_IMG=fondo(nombre), MATRIZ=matriz, INICIO_X=entrada[0],
                           INICIO_Y=entrada[1], AMBIENTE=ambiente, **atributos)


def guardia(x, y, direccion, ruta=(), miradas=(), alcance=6, retirada=None):
    npc = vigilante(x, y, direccion, ruta, miradas)
    npc["vigilancia"].pop("luz")
    npc["vigilancia"].update(alcance_vision=alcance, retirada_tras_barril=retirada)
    return npc


m = [fila[:] for fila in pueblo_1_dia_3.MATRIZ]
marcar(m, ((0, y) for y in range(20, 25)), 94)
marcar(m, ((39, y) for y in (6, 7, 8)), 90)
marcar(m, ((39, y) for y in (21, 22, 23)), 91)
m[14][39] = 1
pueblo = nivel(
    "fondo_pueblo_1_dia_3", m, (pueblo_1_dia_3.INICIO_X, pueblo_1_dia_3.INICIO_Y),
    PORTALES={90: paso(PLAZA, 1, 7), 91: paso(PLAZA, 1, 22), 94: paso(BOSQUE, *ENTRADA_BOSQUE)},
    INTERACTUABLES={89: "desvio"},
    BARRILES=pueblo_1_dia_3.BARRILES,
    NPCS={
        "ronda_norte": guardia(20, 7, "abajo", miradas=(("abajo", 3300), ("arriba", 2000))),
        "ronda_centro": guardia(25, 14, "izq", ruta=((25, 14), (22, 14))),
        "ronda_sur": guardia(31, 23, "arriba", miradas=(("arriba", 3000), ("abajo", 1800))),
    },
    DICCIONARIO_OBJETOS=pueblo_1_dia_3.DICCIONARIO_OBJETOS,
)
m = matriz_desde(pueblo_2_dia_2)
marcar(m, ((0, y) for y in (6, 7, 8)), 90)
marcar(m, ((0, y) for y in (21, 22, 23)), 91)
marcar(m, ((39, y) for y in (6, 7, 8)), 92)
marcar(m, ((x, 29) for x in (31, 32)), 89)
plaza = nivel(
    "fondo_pueblo_2_dia_3", m, (1, 7),
    INTERACTUABLES={89: "desvio"},
    PORTALES={90: paso(PUEBLO, 38, 7), 91: paso(PUEBLO, 38, 22), 92: paso(EXTERIOR, 1, 7)},
    NPCS={
        "ronda_norte": guardia(10, 7, "abajo", ruta=((10, 7), (13, 7))),
        "ronda_plaza": guardia(24, 12, "izq", miradas=(("izq", 2800), ("der", 2700))),
        "ronda_sur": guardia(28, 22, "arriba", ruta=((28, 22), (30, 22))),
    },
    DICCIONARIO_OBJETOS=pueblo_2_dia_2.DICCIONARIO_OBJETOS,
)
m = matriz_desde(iglesia_dia2)
for y, fila in enumerate(m):
    m[y] = [0 if celda in (2, 3) else celda for celda in fila]
m[7][0] = 90
m[4][5] = 91
m[12][15] = 92
exterior = nivel(
    "fondo_iglesia_dia_3", m, (1, 7),
    DICCIONARIO_OBJETOS=iglesia_dia2.DICCIONARIO_OBJETOS,
    PORTALES={90: paso(PLAZA, 38, 7), 91: paso(IGLESIA, 9, 13), 92: paso(OFICINA, 3, 9)},
)
m = [[1] * 15 for _ in range(4)] + [[0] * 15 for _ in range(6)]
marcar(m, ((x, y) for y in (4, 5) for x in (6, 7, 8, 9, 11)), 1)
marcar(m, ((x, y) for y in (7, 8) for x in (0, 1, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14)), 1)
marcar(m, ((12, 4), (14, 4)), 35)
m[ESCRITORIO[1]][ESCRITORIO[0]] = 2
m[ESCRITORIO[1] - 1][ESCRITORIO[0]] = 34
m[5][7], m[5][14], m[9][0], m[9][2] = 3, 1, 1, 90
oficina = nivel(
    "fondo_oficina_dia_3", m, (3, 9), CENTRAR_FONDO=True,
    PORTALES={90: paso(EXTERIOR, 15, 13)},
    INTERACTUABLES={2: "escritorio", 3: "archivero", 34: "escritorio", 35: "papeles"},
    NPCS={
        "archivo_norte": guardia(10, 4, "abajo", miradas=(("abajo", 2700), ("arriba", 2400)), alcance=3),
        "archivo_sur": guardia(8, 8, "arriba", miradas=(("arriba", 2500), ("abajo", 3000)), alcance=3),
        "ronda": guardia(3, 5, "arriba", ruta=((3, 5), (3, 4), (5, 4), (2, 4), (2, 5)), alcance=2),
    },
)
m = [fila[:] for fila in dentro_iglesia.MATRIZ]
m[0][2], m[14][9] = 90, 91
iglesia = nivel(
    "fondo_dentro_iglesia", m, (9, 13),
    PORTALES={90: paso(TUNEL, 1, 1), 91: paso(EXTERIOR, 5, 5)},
    INTERACTUABLES={i: "mobiliario" for i in (2, 3, 4, 5)},
    NPCS=dentro_iglesia.NPCS,
)
m = [fila[:] for fila in tunel.MATRIZ]
m[1][0] = 90
tunel_dia = nivel(
    "fondo_tunel", m, (1, 1), CENTRAR_FONDO=True,
    PORTALES={90: paso(IGLESIA, 2, 1)}, INTERACTUABLES={2: "puerta_tunel"},
    NPCS={nombre: datos for nombre, datos in tunel.NPCS.items() if nombre.startswith("vigilante_")},
)
documentos = nivel("fondo_habitacion_llave", [[1, 1, 1], [0, 0, 0], [0, 0, 0]],
                   (1, 2), CENTRAR_FONDO=True)
m = [[1] * 40 for _ in range(30)]
for y in range(2, 21):
    marcar(m, ((x, y) for x in (13, 14, 15)), 0)
for y in (5, 6):
    marcar(m, ((x, y) for x in range(14, 39)), 0)
for y in range(19, 26):
    marcar(m, ((x, y) for x in range(1, 39)), 0)
for y in range(23, 26):
    marcar(m, ((x, y) for x in range(1, 12)), 1)
m[6][39] = 90
marcar(m, ((27, 22), (31, 24), (34, 21), (39, 24)), 21)
marcar(m, ARBUSTOS[:1], 31)
m[ESCOTILLA[1]][ESCOTILLA[0]] = 33
vigia_bosque = guardia(14, 4, "abajo", retirada=(14, 4))
vigia_bosque["vigilancia"]["paso_persecucion_ms"] = 175
arboles_escotilla = {21: {**pueblo_1.DICCIONARIO_OBJETOS[21], "colision": False}}
bosque = nivel(
    "Fondo_bosque", m, ENTRADA_BOSQUE, BARRILES={(7, 22)},
    PORTALES={90: paso(PUEBLO, 1, 22)},
    INTERACTUABLES={31: "escotilla", 32: "escotilla", 33: "escotilla"},
    DICCIONARIO_OBJETOS={
        **arboles_escotilla,
        31: {"ruta": "recursos/sprites/natural/arbusto_1.png", "colision": True,
             "profundidad": True, "ancho_casillas": 1.15, "alto_casillas": 1.15},
        33: {"ruta": "recursos/sprites/natural/arbusto_2.png", "colision": True,
             "profundidad": True, "ancho_casillas": 1.2, "alto_casillas": 1.2},
    },
    NPCS={"vigia_bosque": vigia_bosque},
)
acceso = nivel("Fondo_bosque", m, (37, 23), DICCIONARIO_OBJETOS=arboles_escotilla)
m = [[1] * 10 for _ in range(3)] + [[0] * 10 for _ in range(5)]
marcar(m, ((x, 3) for x in (1, 3, 5, 7)), 1)
marcar(m, ((x, 5) for x in (1, 3, 5, 7, 9)), 1)
laboratorio = nivel("fondo_laboratorio", m, (8, 7), ambiente="tension", CENTRAR_FONDO=True)
prision = nivel("fondo_prision", prision_dia_2.MATRIZ, (3, 4), CENTRAR_FONDO=True)

NIVELES = dict(zip(
    (PUEBLO, PLAZA, EXTERIOR, OFICINA, IGLESIA, TUNEL, CUARTO, BOSQUE, LAB, ACCESO, PRISION),
    (pueblo, plaza, exterior, oficina, iglesia, tunel_dia, documentos, bosque, laboratorio, acceso, prision),
))

CLINICA_PUEBLO = "pueblo_1_clinica"
CLINICA_PLAZA = "pueblo_2_clinica"
CLINICA_EXTERIOR = "pueblo_3_dia_3"
CLINICA_INTERIOR = "clinica_dia_3"
CLINICA_ACCESO = "acceso_servicio_dia_3"
CLINICA_DESVIO = "desvio_clinica"
PUERTA_CLINICA = (19, 16)
ENTRADA_SERVICIO = (9, 1)
REJA = tuple((x, 14) for x in range(8, 12))

m = [fila[:] for fila in pueblo.MATRIZ]
marcar(m, ((0, y) for y in range(20, 25)), 94)
marcar(m, ((x, y) for x, y in ((0, 7), (39, 14), (9, 29))), 94)
clinica_pueblo = nivel(
    "fondo_pueblo_1_dia_3", m, (pueblo.INICIO_X, pueblo.INICIO_Y),
    PORTALES={90: paso(CLINICA_PLAZA, 1, 7), 91: paso(CLINICA_PLAZA, 1, 22),
              94: paso(CLINICA_DESVIO, 0, 0)},
    DICCIONARIO_OBJETOS=pueblo.DICCIONARIO_OBJETOS, BARRILES=pueblo.BARRILES, NPCS=pueblo.NPCS,
)
m = [fila[:] for fila in plaza.MATRIZ]
marcar(m, ((x, 29) for x in (31, 32)), 93)
clinica_plaza = nivel(
    "fondo_pueblo_2_dia_3", m, (1, 7),
    PORTALES={90: paso(CLINICA_PUEBLO, 38, 7), 91: paso(CLINICA_PUEBLO, 38, 22),
              92: paso(CLINICA_DESVIO, 0, 0), 93: paso(CLINICA_EXTERIOR, 12, 1)},
    DICCIONARIO_OBJETOS=plaza.DICCIONARIO_OBJETOS, NPCS=plaza.NPCS,
)
m = matriz_desde(pueblo_3_dia_2, conservar_postes=True)
marcar(m, ((x, 0) for x in (11, 12, 13)), 90)
marcar(m, ((x, 29) for x in (11, 12, 13)), 91)
m[PUERTA_CLINICA[1]][PUERTA_CLINICA[0]] = 92
m[18][0] = 93
clinica_exterior = nivel(
    "fondo_pueblo_3_dia_2", m, (12, 1),
    PORTALES={90: paso(CLINICA_PLAZA, 31, 28), 91: paso(CLINICA_ACCESO, *ENTRADA_SERVICIO),
              92: paso(CLINICA_INTERIOR, 1, 3), 93: paso(CLINICA_DESVIO, 0, 0)},
    DICCIONARIO_OBJETOS=pueblo_3_dia_2.DICCIONARIO_OBJETOS,
    NPCS={"ronda_clinica": guardia(12, 12, "arriba", miradas=(("arriba", 2300), ("abajo", 2400)), alcance=3)},
)
m = [[1] * 10 for _ in range(3)] + [[0] * 10 for _ in range(5)]
marcar(m, ((x, y) for y in (4, 5) for x in range(3)), 1)
marcar(m, ((x, y) for x, y in ((8, 3), (9, 3), (7, 5), (8, 5), (0, 6), (1, 6),
                                     (3, 6), (1, 7), (3, 7))), 1)
clinica_interior = nivel("fondo_clinica", m, (1, 3), CENTRAR_FONDO=True)

m = [[1] * 20 for _ in range(25)]
for y in range(13):
    marcar(m, ((x, y) for x in range(5, 15)), 0)
for y in range(13, 25):
    marcar(m, ((x, y) for x in range(8, 12)), 0)
marcar(m, REJA, 1)
clinica_acceso = nivel(
    "fondo_salida", m, ENTRADA_SERVICIO,
    NPCS={"ronda_servicio": guardia(14, 9, "izq", miradas=(("izq", 1800), ("der", 2500)), alcance=3)},
)

CLINICA_NIVELES = {
    CLINICA_PUEBLO: clinica_pueblo, CLINICA_PLAZA: clinica_plaza, CLINICA_EXTERIOR: clinica_exterior,
    CLINICA_INTERIOR: clinica_interior, CLINICA_ACCESO: clinica_acceso,
}
NIVELES.update(CLINICA_NIVELES)
