import logging

from app.database.database import SessionLocal
from app.integrations.control_client import ControlClient
from app.services.estado_cuenta_service import EstadoCuentaService

logger = logging.getLogger(__name__)


def verificar_estado_cuenta_periodico():
    """
    Red de seguridad: revisa el estado activo/inactivo contra
    LeadFlow Control cada pocos minutos, por si el push directo
    (POST /interno/estado-cuenta) falló (ej. este CRM estaba
    temporalmente inaccesible cuando Control intentó avisar).

    De paso, cachea acá mismo `zona_busqueda_google_places` (para el
    sourcing automático) y `pausar_prospeccion` (para el orquestador
    de primer contacto) -- mismo GET /empresas/mi-config, sin
    mecanismo de comunicación nuevo.
    """

    config = ControlClient().obtener_mi_config()

    if config is None:

        # Ya se logueó el motivo en ControlClient. No tocar el
        # estado local -- mejor mantener el último valor conocido
        # que asumir algo sin confirmar.
        return

    db = SessionLocal()

    try:

        EstadoCuentaService(db).actualizar_estado(
            activo=config["activo"],
            zona_busqueda_google_places=config.get(
                "zona_busqueda_google_places"
            ),
            pausar_prospeccion=config.get(
                "pausar_prospeccion"
            )
        )

    finally:

        db.close()
