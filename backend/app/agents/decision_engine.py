from enum import Enum


class DecisionType(str, Enum):

    RESPONDER = "RESPONDER"

    USAR_HERRAMIENTA = "USAR_HERRAMIENTA"

    ESCALAR_HUMANO = "ESCALAR_HUMANO"

    FINALIZAR = "FINALIZAR"


class DecisionEngine:

    def decidir(
        self,
        respuesta_ai: str
    ):

        return {

            "tipo": DecisionType.RESPONDER,

            "contenido": respuesta_ai
        }