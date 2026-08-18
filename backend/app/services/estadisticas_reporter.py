import logging

from app.database.database import SessionLocal
from app.enums import EstadoProspecto
from app.integrations.control_client import ControlClient
from app.repositories.prospecto_repository import ProspectoRepository

logger = logging.getLogger(__name__)

# "Contactados" = llegaron a responder en algún momento (RESPONDIO en
# adelante). Ojo: DESCARTADO también puede alcanzarse directo desde
# NUEVO/CONTACTADO sin que el prospecto haya respondido nunca (ver
# ProspectoStateService.TRANSICIONES) -- se cuenta igual acá, es un
# margen de error chico aceptado a propósito por simplicidad, no un
# descuido.
ESTADOS_CONTACTADO = [

    EstadoProspecto.RESPONDIO,

    EstadoProspecto.INTERESADO,

    EstadoProspecto.COTIZADO,

    EstadoProspecto.NEGOCIACION,

    EstadoProspecto.CLIENTE,

    EstadoProspecto.DESCARTADO,

]

ESTADOS_EXITO = [

    EstadoProspecto.CLIENTE,

]


def reportar_estadisticas_periodico():
    """
    Reporta a LeadFlow Control cuántos prospectos han respondido y
    cuántos llegaron a CLIENTE. Snapshot del estado actual, no
    histórico -- Control sobrescribe el número anterior, no acumula.
    """

    db = SessionLocal()

    try:

        repository = ProspectoRepository(db)

        contactados = repository.contar_por_estados(
            ESTADOS_CONTACTADO
        )

        exitosos = repository.contar_por_estados(
            ESTADOS_EXITO
        )

    finally:

        db.close()

    exito = ControlClient().reportar_estadisticas(
        prospectos_contactados=contactados,
        negociaciones_exitosas=exitosos
    )

    if not exito:

        logger.warning(
            "No se pudieron reportar estadísticas a Control en este "
            "ciclo -- se reintenta en el próximo con los números "
            "actualizados."
        )
