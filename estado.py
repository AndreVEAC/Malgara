from configuracion import CORDURA_MAX, SOSPECHA_MAX, CONFIANZA_MAX

class EstadoJuego:
    def __init__(self):
        self.confianza_lucas = 50
        self.confianza_morales = 50
        self.cordura = CORDURA_MAX
        self.sospecha_pueblo = 0
        self.decisiones_tomadas = 0
        self.objetos_clave = set()
        self.historial_decisiones = []

    def aplicar_efectos(self, efectos: dict):
        """Aplica cambios a las métricas del jugador según las elecciones en el JSON."""
        if not efectos:
            return

        self.confianza_lucas = max(0, min(CONFIANZA_MAX, self.confianza_lucas + efectos.get("confianza_lucas", 0)))
        self.confianza_morales = max(0, min(CONFIANZA_MAX, self.confianza_morales + efectos.get("confianza_morales", 0)))
        self.cordura = max(0, min(CORDURA_MAX, self.cordura + efectos.get("cordura", 0)))
        self.sospecha_pueblo = max(0, min(SOSPECHA_MAX, self.sospecha_pueblo + efectos.get("sospecha_pueblo", 0)))
        
        if "obtener_objeto" in efectos:
            self.objetos_clave.add(efectos["obtener_objeto"])

    def registrar_decision(self, id_nodo: str, texto_opcion: str):
        self.decisiones_tomadas += 1
        self.historial_decisiones.append({
            "paso": self.decisiones_tomadas,
            "nodo": id_nodo,
            "eleccion": texto_opcion
        })