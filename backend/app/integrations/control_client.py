import logging
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ControlClient:

    def obtener_mi_config(self) -> dict | None:

        if not settings.CONTROL_BASE_URL or not settings.EMPRESA_API_KEY:

            logger.warning(
                "CONTROL_BASE_URL o EMPRESA_API_KEY no configuradas, "
                "no se puede consultar LeadFlow Control."
            )

            return None

        url = (
            settings.CONTROL_BASE_URL.rstrip("/")
            + "/empresas/mi-config"
        )

        try:

            response = httpx.get(
                url,
                headers={"X-API-Key": settings.EMPRESA_API_KEY},
                timeout=10
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            logger.warning(
                f"No se pudo consultar mi-config en LeadFlow Control: {e}"
            )

            return None

    def reportar_uso(
        self,
        periodo_desde: datetime,
        periodo_hasta: datetime,
        tokens_entrada: int,
        tokens_salida: int,
        tokens_total: int
    ) -> bool:

        if not settings.CONTROL_BASE_URL or not settings.EMPRESA_API_KEY:

            logger.warning(
                "CONTROL_BASE_URL o EMPRESA_API_KEY no configuradas, "
                "no se puede reportar uso de tokens a LeadFlow Control."
            )

            return False

        url = (
            settings.CONTROL_BASE_URL.rstrip("/")
            + "/empresas/reportar-uso"
        )

        try:

            response = httpx.post(
                url,
                json={

                    "periodo_desde": periodo_desde.isoformat(),

                    "periodo_hasta": periodo_hasta.isoformat(),

                    "tokens_entrada": tokens_entrada,

                    "tokens_salida": tokens_salida,

                    "tokens_total": tokens_total

                },
                headers={"X-API-Key": settings.EMPRESA_API_KEY},
                timeout=10
            )

            response.raise_for_status()

            return True

        except Exception as e:

            logger.warning(
                f"No se pudo reportar uso de tokens a LeadFlow Control: {e}"
            )

            return False

    def reportar_estadisticas(
        self,
        prospectos_contactados: int,
        negociaciones_exitosas: int
    ) -> bool:

        if not settings.CONTROL_BASE_URL or not settings.EMPRESA_API_KEY:

            logger.warning(
                "CONTROL_BASE_URL o EMPRESA_API_KEY no configuradas, "
                "no se pueden reportar estadísticas a LeadFlow Control."
            )

            return False

        url = (
            settings.CONTROL_BASE_URL.rstrip("/")
            + "/empresas/reportar-estadisticas"
        )

        try:

            response = httpx.post(
                url,
                json={

                    "prospectos_contactados": prospectos_contactados,

                    "negociaciones_exitosas": negociaciones_exitosas

                },
                headers={"X-API-Key": settings.EMPRESA_API_KEY},
                timeout=10
            )

            response.raise_for_status()

            return True

        except Exception as e:

            logger.warning(
                f"No se pudieron reportar estadísticas a LeadFlow "
                f"Control: {e}"
            )

            return False
