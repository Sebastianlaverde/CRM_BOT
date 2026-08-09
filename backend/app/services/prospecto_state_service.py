from sqlalchemy.orm import Session

from app.enums import EstadoProspecto
from app.services.evento_service import EventoService
from app.services.historial_service import HistorialService
from app.services.automation_service import AutomationService
from app.enums import (
    TipoEvento,
    OrigenEvento,
    EntidadEvento,
)
from app.repositories.prospecto_repository import ProspectoRepository

class ProspectoStateService:

    TRANSICIONES = {
        EstadoProspecto.NUEVO: [
            EstadoProspecto.CONTACTADO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.CONTACTADO: [
            EstadoProspecto.RESPONDIO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.RESPONDIO: [
            EstadoProspecto.INTERESADO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.INTERESADO: [
            EstadoProspecto.COTIZADO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.COTIZADO: [
            EstadoProspecto.NEGOCIACION,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.NEGOCIACION: [
            EstadoProspecto.CLIENTE,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.CLIENTE: [],

        EstadoProspecto.DESCARTADO: [],
    }

    def __init__(self, db: Session):
        self.db = db

        self.repository = ProspectoRepository(db)

        self.historial_service = HistorialService(db)

        self.evento_service = EventoService(db)

        self.automation_service = AutomationService()

    def validar_transicion(
        self,
        estado_actual: EstadoProspecto,
        nuevo_estado: EstadoProspecto
    ):

        permitidos = self.TRANSICIONES.get(
            estado_actual,
            []
        )

        if nuevo_estado not in permitidos:
            raise ValueError(
                f"No se puede cambiar el estado de "
                f"{estado_actual.value} a {nuevo_estado.value}."
            )

    def cambiar_estado(
        self,
        prospecto,
        nuevo_estado: EstadoProspecto,
        observacion: str | None = None
    ):

        self.validar_transicion(
            prospecto.estado,
            nuevo_estado
        )

        estado_anterior = prospecto.estado

        prospecto.estado = nuevo_estado

        self.historial_service.registrar_cambio(
            prospecto=prospecto,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            observacion=observacion
        )

        self.evento_service.registrar_evento(
            tipo=TipoEvento.ESTADO_PROSPECTO_ACTUALIZADO,
            entidad=EntidadEvento.PROSPECTO,
            entidad_id=prospecto.id,
            descripcion=(
                f"Estado cambiado de "
                f"{estado_anterior.value} "
                f"a {nuevo_estado.value}."
            ),
            origen=OrigenEvento.API
        )

        self.automation_service.ejecutar(
            prospecto=prospecto,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado
        )

        self.db.commit()

        self.db.refresh(prospecto)

        return prospecto