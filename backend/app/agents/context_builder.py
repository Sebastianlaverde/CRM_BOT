from sqlalchemy.orm import Session

from app.enums import EntidadEvento
from app.repositories.prospecto_repository import ProspectoRepository
from app.repositories.mensaje_repository import MensajeRepository
from app.repositories.cotizacion_repository import CotizacionRepository
from app.repositories.evento_repository import EventoRepository
from app.repositories.sesion_repository import SesionRepository


class ContextBuilder:

    def __init__(self, db: Session):

        self.db = db

        self.prospectos = ProspectoRepository(db)

        self.sesiones = SesionRepository(db)

        self.mensajes = MensajeRepository(db)

        self.cotizaciones = CotizacionRepository(db)

        self.eventos = EventoRepository(db)

    def build(
        self,
        prospecto_id: int,
        canal
    ):

        prospecto = self.prospectos.find_by_id(
            prospecto_id
        )

        if not prospecto:
            return None

        sesion = self.sesiones.obtener_sesion_activa(
            prospecto_id,
            canal
        )

        mensajes = []

        if sesion:

            mensajes = self.mensajes.listar_por_sesion(
                sesion.id
            )

        cotizaciones = self.cotizaciones.listar_por_prospecto(
            prospecto.id
        )

        eventos = self.eventos.find_by_entidad(
            EntidadEvento.PROSPECTO,
            prospecto.id
        )

        return {

            "prospecto": prospecto,

            "sesion": sesion,

            "mensajes": mensajes,

            "cotizaciones": cotizaciones,

            "eventos": eventos,
        }