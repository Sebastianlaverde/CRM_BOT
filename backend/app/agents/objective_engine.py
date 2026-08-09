from app.enums import EstadoProspecto


class ObjectiveEngine:

    def get_objective(
        self,
        estado: EstadoProspecto
    ):

        objetivos = {

            EstadoProspecto.NUEVO:
                "Lograr que el prospecto responda.",

            EstadoProspecto.CONTACTADO:
                "Descubrir las necesidades del cliente.",

            EstadoProspecto.RESPONDIO:
                "Calificar el prospecto.",

            EstadoProspecto.INTERESADO:
                "Preparar una cotización.",

            EstadoProspecto.COTIZADO:
                "Resolver dudas sobre la cotización.",

            EstadoProspecto.NEGOCIACION:
                "Cerrar la venta.",

            EstadoProspecto.CLIENTE:
                "Mantener una buena relación comercial.",

            EstadoProspecto.DESCARTADO:
                "Finalizar la conversación cordialmente.",
        }

        return objetivos.get(
            estado,
            ""
        )