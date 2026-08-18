from datetime import datetime

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

    def registrar_seguimiento_enviado(
        self,
        prospecto,
        dias_sin_respuesta: int
    ):

        return self.registrar_evento(

            tipo=TipoEvento.SEGUIMIENTO_ENVIADO,

            entidad=EntidadEvento.PROSPECTO,

            entidad_id=prospecto.id,

            descripcion=(
                f"Se envió un mensaje de seguimiento a "
                f"'{prospecto.nombre_empresa}' tras "
                f"{dias_sin_respuesta} día(s) sin respuesta."
            ),

            origen=OrigenEvento.SISTEMA
        )

    def registrar_primer_contacto_enviado(
        self,
        prospecto
    ):

        return self.registrar_evento(

            tipo=TipoEvento.PRIMER_CONTACTO_ENVIADO,

            entidad=EntidadEvento.PROSPECTO,

            entidad_id=prospecto.id,

            descripcion=(
                f"Se envió el primer contacto por WhatsApp a "
                f"'{prospecto.nombre_empresa}'."
            ),

            origen=OrigenEvento.SISTEMA
        )

    def registrar_primer_contacto_fallido(
        self,
        prospecto,
        motivo: str
    ):

        return self.registrar_evento(

            tipo=TipoEvento.PRIMER_CONTACTO_FALLIDO,

            entidad=EntidadEvento.PROSPECTO,

            entidad_id=prospecto.id,

            descripcion=(
                f"Falló el envío del primer contacto a "
                f"'{prospecto.nombre_empresa}'. Motivo: {motivo}"
            ),

            origen=OrigenEvento.SISTEMA
        )

    def contar_primer_contacto_enviado_desde(
        self,
        desde: datetime
    ) -> int:

        return self.repository.contar_por_tipo_desde(
            TipoEvento.PRIMER_CONTACTO_ENVIADO,
            desde
        )

    def contar_primer_contacto_fallido_de_prospecto(
        self,
        prospecto_id: int
    ) -> int:

        return self.repository.contar_por_tipo_y_entidad(
            TipoEvento.PRIMER_CONTACTO_FALLIDO,
            EntidadEvento.PROSPECTO,
            prospecto_id
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