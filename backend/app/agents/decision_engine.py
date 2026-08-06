from app.enums import EstadoProspecto


class DecisionEngine:

    def decidir(
        self,
        respuesta_ia: str,
        contexto: dict
    ):

        acciones = []

        prospecto = contexto["prospecto"]

        estado = prospecto.estado

        if estado == EstadoProspecto.NUEVO:

            acciones.append(
                {
                    "type": "actualizar_estado",
                    "estado": EstadoProspecto.CONTACTADO
                }
            )

        return {

            "contenido": respuesta_ia,

            "acciones": acciones

        }