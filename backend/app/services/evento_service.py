from sqlalchemy.orm import Session

from app.enums import (
    OrigenEvento,
    TipoEvento,
    EntidadEvento,
)
from app.models.evento import Evento
from app.repositories.evento_repository import EventoRepository
from app.mappers.evento_mapper import EventoMapper

class EventoService:

    def __init__(self, db: Session):

        self.repository = EventoRepository(db)

    def registrar_evento(
        self,
        tipo: TipoEvento,
        entidad: EntidadEvento,
        entidad_id: int,
        descripcion: str,
        origen: OrigenEvento
    ) -> Evento:

        evento = Evento(
            tipo=tipo,
            entidad=entidad,
            entidad_id=entidad_id,
            descripcion=descripcion,
            origen=origen
        )

        self.repository.add(evento)

        return evento

    def registrar_cotizacion_creada(
        self,
        cotizacion,
        prospecto
    ):

        return self.registrar_evento(

            tipo=TipoEvento.COTIZACION_CREADA,

            entidad=EntidadEvento.COTIZACION,

            entidad_id=cotizacion.id,

            descripcion=(
                f"Se creó la cotización #{cotizacion.id} "
                f"para el prospecto '{prospecto.nombre_empresa}'."
            ),

            origen=OrigenEvento.API
        )
    
    def registrar_escalamiento(
        self,
        prospecto,
        motivo: str
    ):

        return self.registrar_evento(

            tipo=TipoEvento.ESCALADO_A_HUMANO,

            entidad=EntidadEvento.PROSPECTO,

            entidad_id=prospecto.id,

            descripcion=(
                f"El agente comercial escaló la conversación "
                f"con '{prospecto.nombre_empresa}' a un asesor "
                f"humano. Motivo: {motivo}"
            ),

            origen=OrigenEvento.SISTEMA
        )

    def obtener_todos(self):

        eventos = self.repository.list_all()

        return EventoMapper.to_response_list(
            eventos
        )

    def obtener_por_entidad(
        self,
        entidad: EntidadEvento,
        entidad_id: int
    ):

        eventos = self.repository.find_by_entidad(
            entidad,
            entidad_id
        )

        return EventoMapper.to_response_list(
            eventos
        )