from mapas import casa_dia2, casa_noche_1
from mapas.geografia_noche_2 import marcar, matriz_desde, objetos, paso

FONDO_IMG = "recursos/sprites/fondos/fondo_casa_noche_2.png"
AMBIENTE = "noche_calmada"
INICIO_X, INICIO_Y = 15, 17
DICCIONARIO_OBJETOS = objetos()
MATRIZ = matriz_desde(casa_dia2)
POSTES = tuple((x, y) for y, fila in enumerate(casa_noche_1.MATRIZ)
               for x, casilla in enumerate(fila) if casilla == 20)
marcar(MATRIZ, POSTES, 20)
GUARDIAS_CAMINO_NORTE = ((2, 0), (3, 0), (4, 0))
LIMITE_CAMINO_NORTE = 5
NPCS = {
    f"loco_norte_{i}": {
        "x": x, "y": y, "direccion": "abajo", "carpeta_sprite": "loco",
        "vigilancia": {"luz": "recursos/sprites/efectos/luz_3.png"},
    }
    for i, (x, y) in enumerate(GUARDIAS_CAMINO_NORTE)
}
def cerrar_camino(matriz):
    fila = matriz[LIMITE_CAMINO_NORTE]
    for x, casilla in enumerate(fila):
        if casilla == 0:
            fila[x] = 1


cerrar_camino(MATRIZ)
MATRIZ[18][19] = 98
PORTALES = {98: paso("pueblo_3_noche_2", 1, 18)}
