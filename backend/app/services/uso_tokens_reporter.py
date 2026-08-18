import logging
from datetime import datetime
from datetime import timezone

from app.database.database import SessionLocal
from app.integrations.control_client import ControlClient
from app.services.uso_tokens_service import UsoTokensService

logger = logging.getLogger(__name__)


def reportar_uso_tokens_periodico():
    """
    Reporta a LeadFlow Control el total de tokens consumidos hoy.
    No hay urgencia (a diferencia del estado de cuenta) -- si un
    reporte falla o el proceso se reinicia, el próximo ciclo vuelve a
    mandar el total actualizado del día y Control lo sobrescribe
    (upsert por período), así que no hace falta trackear reintentos.
    """

    db = SessionLocal()

    try:

        resumen = UsoTokensService(db).resumen_de_hoy()

    finally:

        db.close()

    exito = ControlClient().reportar_uso(

        periodo_desde=resumen["periodo_desde"],

        periodo_hasta=datetime.now(timezone.utc),

        tokens_entrada=resumen["tokens_entrada"],

        tokens_salida=resumen["tokens_salida"],

        tokens_total=resumen["tokens_total"]

    )

    if not exito:

        logger.warning(
            "No se pudo reportar el uso de tokens a Control en este "
            "ciclo -- se reintenta en el próximo con el total "
            "actualizado del día."
        )
