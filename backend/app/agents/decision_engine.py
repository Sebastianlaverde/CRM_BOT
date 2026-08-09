from app.enums import EstadoProspecto
from app.enums.decision_type import DecisionType

ESCALAR_TAG = "[ESCALAR_A_HUMANO]"

# Transiciones mecánicas: no requieren criterio del modelo, se
# disparan solo por el hecho de estar procesando un mensaje
# entrante mientras el prospecto está en ese estado.
TRANSICIONES_AUTOMATICAS = {

    EstadoProspecto.NUEVO: (
        EstadoProspecto.CONTACTADO,
        "El prospecto recibió su primer contacto."
    ),

    EstadoProspecto.CONTACTADO: (
        EstadoProspecto.RESPONDIO,
        "El prospecto respondió al contacto inicial."
    ),

}


class DecisionEngine:

    def decidir(
        self,
        respuesta_ia: str,
        contexto: dict
    ):

        acciones = []

        prospecto = contexto["prospecto"]

        estado = prospecto.estado

        transicion = TRANSICIONES_AUTOMATICAS.get(
            estado
        )

        if transicion:

            nuevo_estado, observacion = transicion

            acciones.append({

                "type": "actualizar_estado",

                "prospecto_id": prospecto.id,

                "estado": nuevo_estado.value,

                "observacion": observacion

            })

        tipo_decision, contenido, motivo = (
            self._resolver_tipo(respuesta_ia)
        )

        if tipo_decision == DecisionType.ESCALAR_A_HUMANO:

            acciones.append({

                "type": "escalar_a_humano",

                "motivo": motivo

            })

        return {

            "type": tipo_decision,

            "contenido": contenido,

            "acciones": acciones

        }

    def _resolver_tipo(
        self,
        respuesta_ia: str
    ):

        texto = (respuesta_ia or "").strip()

        if texto.startswith(ESCALAR_TAG):

            contenido = texto[
                len(ESCALAR_TAG):
            ].strip()

            motivo = (
                contenido
                if contenido
                else "El agente solicitó apoyo de un asesor humano."
            )

            return (
                DecisionType.ESCALAR_A_HUMANO,
                contenido,
                motivo
            )

        return (
            DecisionType.RESPONDER,
            texto,
            None
        )