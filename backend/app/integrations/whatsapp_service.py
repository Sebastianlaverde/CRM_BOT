import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Envío de plantillas de WhatsApp Business Cloud API. Sin
    credenciales configuradas (WHATSAPP_TOKEN vacío, como hoy -- no
    hay número verificado todavía), corre en modo SIMULADO: no manda
    nada real, pero deja probar el resto del orquestador (dedup, tope
    de embudo, tope diario, cambio de estado, reintentos) de verdad.
    Mismo patrón que AIService con MockProvider/OpenAIProvider.
    """

    def enviar_plantilla(
        self,
        telefono: str,
        nombre_plantilla: str,
        variables: list[str]
    ) -> dict:

        if not settings.WHATSAPP_TOKEN:

            logger.info(
                f"[SIMULADO] Se habría enviado la plantilla "
                f"'{nombre_plantilla}' a {telefono} con variables "
                f"{variables}."
            )

            return {

                "exitoso": True,

                "detalle": "simulado, sin credenciales de Meta configuradas"

            }

        # Envío real -- pendiente de construir cuando haya número
        # verificado y credenciales reales (WHATSAPP_TOKEN/PHONE_ID).
        # No lanza excepción a propósito: una falla acá no debe tumbar
        # el resto del orquestador, solo este candidato puntual (que
        # queda registrado como fallido y se reintenta después).
        logger.error(
            "WHATSAPP_TOKEN está configurada pero el envío real "
            "todavía no está implementado."
        )

        return {

            "exitoso": False,

            "detalle": "envío real de WhatsApp no implementado todavía"

        }
