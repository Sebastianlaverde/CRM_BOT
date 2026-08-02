import logging
from datetime import datetime
from uuid import uuid4

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookService:

    def enviar(
        self,
        evento: str,
        payload: dict
    ) -> bool:

        if not settings.N8N_ENABLED:

            logger.info(
                "Integración con n8n deshabilitada."
            )

            return False

        envelope = {

            "event_id": str(uuid4()),

            "event": evento,

            "source": "leadflow",

            "version": "1.0",

            "timestamp": datetime.utcnow().isoformat(),

            "payload": payload
        }

        try:

            response = httpx.post(

                settings.N8N_WEBHOOK_URL,

                json=envelope,

                timeout=10
            )

            response.raise_for_status()

            logger.info(
                f"Webhook enviado correctamente: {evento}"
            )

            return True

        except Exception as e:

            logger.exception(
                f"Error enviando webhook: {e}"
            )

            return False