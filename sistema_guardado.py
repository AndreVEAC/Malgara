import importlib
import json
import os
import sys
import time
from pathlib import Path


CARPETA = Path(__file__).resolve().parent / "partidas"
VERSION = 1

pendiente = None
cargando = False
revision_cargada = -1

# Solo datos del NPC; nunca imágenes ni sonidos.
CAMPOS_NPC = (
    "x",
    "y",
    "direccion",
    "visible",
    "pausado",
    "comportamiento",
    "_esperas_resueltas",
    "sprite_override",
)


def _especial(objeto):
    """Permitir guardar conjuntos como objetos_clave."""
    if isinstance(objeto, set):
        return {"__conjunto__": list(objeto)}

    raise TypeError(
        f"No se puede guardar {type(objeto).__name__}"
    )


def _recuperar(objeto):
    if set(objeto) == {"__conjunto__"}:
        return set(objeto["__conjunto__"])

    return objeto


def _ruta(ranura):
    if ranura not in ("manual", "automatico"):
        raise ValueError("Ranura desconocida")

    return CARPETA / f"{ranura}.json"


def solicitar(ranura="manual", mapa_destino=None):
    """Guardar cuando termine el diálogo o cambio de mapa."""
    global pendiente

    _ruta(ranura)
    pendiente = (ranura, mapa_destino)


def actualizar(estado_jugador):
    global pendiente

    import sistema_mapa as mapa
    import sistema_dialogo as dialogo
    import sistema_vigilancia as vigilancia

    if pendiente is None or cargando:
        return

    ranura, destino = pendiente

    if destino and mapa.nombre_mapa_actual != destino:
        return

    if (
        mapa.transicion_activa
        or mapa.jugador_bloqueado
        or mapa.control_cinematico
        or (estado_jugador.noche2["fase"] in ("sigilo", "dia3") and vigilancia.persecucion_activa)
        or dialogo.obtener_evento_activo() is not None
    ):
        return

    pendiente = None

    libreta_disponible = mapa.nombre_mapa_actual == "hogar_dia2" or (
        mapa.nombre_mapa_actual == "hogar"
        and "hogar:cinematica_completada" in mapa.eventos_completados
    )
    if ranura == "manual" and not libreta_disponible:
        dialogo.activar_notificacion(
            "Solo puedes guardar en la libreta de casa."
        )
        return

    try:
        guardar(estado_jugador, ranura)

    except (OSError, TypeError, ValueError) as error:
        print(f"[Guardado] {error}")

        dialogo.activar_notificacion(
            "No se pudo guardar la partida."
        )

    else:
        texto = (
            "Partida guardada."
            if ranura == "manual"
            else "Autoguardado completado."
        )

        dialogo.activar_notificacion(texto)


def guardar(estado_jugador, ranura):
    """Escribir la partida. Para el juego, usar solicitar()."""
    import sistema_mapa as mapa

    prologo = sys.modules.get(
        "funciones_mapas.funcion_prologo"
    )

    memoria_prologo = {}

    if prologo is not None:
        for campo in (
            "progreso_lucas_guardado",
            "esperas_desbloqueadas",
        ):
            if hasattr(prologo, campo):
                memoria_prologo[campo] = getattr(
                    prologo, campo
                )

    datos = {
        "version": VERSION,
        "fecha_ns": time.time_ns(),
        "mapa": mapa.nombre_mapa_actual,
        "jugador": {
            "x": mapa.mateo_x,
            "y": mapa.mateo_y,
            "direccion": mapa.direccion_mateo,
        },
        "estado": vars(estado_jugador),
        "eventos": mapa.eventos_completados,
        "memoria_npcs": mapa.estado_npcs_guardado,
        "prologo": memoria_prologo,
        "matriz": mapa.matriz_activa,
        "npcs": {
            nombre: {
                campo: npc[campo]
                for campo in CAMPOS_NPC
                if campo in npc
            }
            for nombre, npc in mapa.npcs_activos.items()
        },
    }

    contenido = json.dumps(
        datos,
        ensure_ascii=False,
        indent=2,
        default=_especial,
        allow_nan=False,
    )

    ruta = _ruta(ranura)
    CARPETA.mkdir(parents=True, exist_ok=True)

    temporal = ruta.with_suffix(".tmp")

    try:
        # Escribir primero un temporal para proteger
        # el guardado anterior si falla la escritura.
        with temporal.open("w", encoding="utf-8") as archivo:
            archivo.write(contenido)
            archivo.flush()
            os.fsync(archivo.fileno())

        os.replace(temporal, ruta)

    finally:
        temporal.unlink(missing_ok=True)


def _leer(ranura):
    with _ruta(ranura).open(encoding="utf-8") as archivo:
        datos = json.load(
            archivo,
            object_hook=_recuperar
        )

    if datos["version"] != VERSION:
        raise ValueError("Versión de guardado incompatible")

    nombre = datos["mapa"]

    if (
        not isinstance(nombre, str)
        or not nombre.isidentifier()
    ):
        raise ValueError("Nombre de mapa inválido")

    if type(datos["fecha_ns"]) is not int:
        raise ValueError("Fecha inválida")

    matriz = datos["matriz"]

    if not matriz or not all(
        isinstance(fila, list)
        and len(fila) == len(matriz[0])
        for fila in matriz
    ):
        raise ValueError("Matriz inválida")

    if not all(
        type(casilla) is int
        for fila in matriz
        for casilla in fila
    ):
        raise ValueError("Casillas inválidas")

    jugador = datos["jugador"]
    x, y = jugador["x"], jugador["y"]

    if (
        type(x) is not int
        or type(y) is not int
        or not (
            0 <= y < len(matriz)
            and 0 <= x < len(matriz[0])
        )
    ):
        raise ValueError("Posición inválida")

    if jugador["direccion"] not in (
        "arriba", "abajo", "izq", "der"
    ):
        raise ValueError("Dirección inválida")

    if (
        not isinstance(datos["eventos"], set)
        or not isinstance(datos["estado"], dict)
    ):
        raise ValueError("Estado inválido")

    if not isinstance(
        datos["estado"].get("objetos_clave"), set
    ):
        raise ValueError("Inventario inválido")

    for clave in ("npcs", "memoria_npcs", "prologo"):
        if not isinstance(datos[clave], dict):
            raise ValueError(f"{clave} inválido")

    return datos


def listar_partidas():
    """Resumen de las ranuras disponibles, de más reciente a más antigua."""
    from estado import BUSQUEDA_DIA_2

    partidas = []

    for ranura in ("manual", "automatico"):
        try:
            datos = _leer(ranura)

        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            IndexError,
        ):
            continue

        noche = datos["estado"].get("noche2", {})
        dia = noche.get("dia_actual", 2) if noche.get("fase") or BUSQUEDA_DIA_2 in datos["eventos"] else 1
        partidas.append({
            "ranura": ranura,
            "mapa": datos["mapa"],
            "fecha_ns": datos["fecha_ns"],
            "dia": dia,
        })

    return sorted(
        partidas,
        key=lambda partida: partida["fecha_ns"],
        reverse=True,
    )


def continuar(estado_jugador):
    """Cargar la ranura válida más reciente."""
    partidas = listar_partidas()

    if not partidas:
        return False

    return cargar(
        estado_jugador,
        partidas[0]["ranura"]
    )


def cargar(estado_jugador, ranura="manual", *, desde_pausa=False):
    global revision_cargada
    global cargando, pendiente

    import sistema_mapa as mapa
    import sistema_dialogo as dialogo
    from configuracion import TAMANO_CASILLA
    from mapas.dia_3 import NIVELES

    if not desde_pausa and (
        mapa.transicion_activa
        or dialogo.obtener_evento_activo() is not None
    ):
        return False

    try:
        datos = _leer(ranura)

        modulo = mapa.datos_nivel(datos["mapa"])
        if datos["mapa"] not in NIVELES:
            importlib.import_module("funciones_mapas.funcion_" + datos["mapa"])

        if (
            [len(fila) for fila in datos["matriz"]]
            != [len(fila) for fila in modulo.MATRIZ]
        ):
            raise ValueError(
                "El tamaño del mapa cambió desde el guardado"
            )

    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
        ImportError,
    ) as error:
        print(f"[Carga] {error}")
        return False

    cargando = True
    pendiente = None

    try:
        if desde_pausa:
            dialogo.cancelar_dialogo()
        # Conservar valores predeterminados que agreguemos
        # a EstadoJuego en el futuro.
        valores = vars(type(estado_jugador)()).copy()
        valores.update(datos["estado"])

        vars(estado_jugador).clear()
        vars(estado_jugador).update(valores)

        # Restaurar ANTES de iniciar el director:
        # así no se repiten las cinemáticas completadas.
        mapa.eventos_completados.clear()
        mapa.eventos_completados.update(datos["eventos"])

        mapa.estado_npcs_guardado.clear()
        mapa.estado_npcs_guardado.update(
            datos["memoria_npcs"]
        )

        if datos["prologo"]:
            prologo = importlib.import_module(
                "funciones_mapas.funcion_prologo"
            )

            for campo in (
                "progreso_lucas_guardado",
                "esperas_desbloqueadas",
            ):
                if campo in datos["prologo"]:
                    setattr(
                        prologo,
                        campo,
                        datos["prologo"][campo],
                    )

        jugador = datos["jugador"]
        mapa.control_cinematico = False
        mapa.pantalla_negra_en = None
        mapa.ocultar_mateo = False

        mapa.spawn_pendiente = (
            jugador["x"],
            jugador["y"],
        )

        # Carga inmediata para restaurar los datos antes
        # de mostrar el primer fotograma de la partida.
        mapa._ejecutar_carga_real(datos["mapa"])
        revision_cargada = mapa.revision_nivel

        mapa.matriz_activa = [
            fila[:] for fila in datos["matriz"]
        ]

        mapa.mateo_x = jugador["x"]
        mapa.mateo_y = jugador["y"]

        mapa.mateo_px_x = float(
            jugador["x"] * TAMANO_CASILLA
        )
        mapa.mateo_px_y = float(
            jugador["y"] * TAMANO_CASILLA
        )

        mapa.direccion_mateo = jugador["direccion"]

        for nombre, guardado in datos["npcs"].items():
            npc = mapa.npcs_activos.get(nombre)

            if npc is None:
                continue

            npc.update({
                campo: valor
                for campo, valor in guardado.items()
                if campo in CAMPOS_NPC
            })

            npc["px_x"] = float(
                npc["x"] * TAMANO_CASILLA
            )
            npc["px_y"] = float(
                npc["y"] * TAMANO_CASILLA
            )

        # Revelar la partida desde negro.
        mapa.mapa_pendiente = None
        mapa.alpha_transicion = 255
        mapa.tipo_transicion = "fade_in"
        mapa.transicion_activa = True

        dialogo.limpiar_notificaciones()

        return True

    finally:
        cargando = False
