from datetime import datetime

from sqlalchemy.orm import Session

from app.models.evento import Evento
from app.enums import EntidadEvento, TipoEvento

class EventoRepository:

    def __init__(self, db: Session):

        self.db = db

    def add(
        self,
        evento: Evento
    ):

        self.db.add(evento)

    def list_all(self):

        return (
            self.db.query(Evento)
            .order_by(
                Evento.created_at.desc()
            )
            .all()
        )

    def find_by_entidad(
        self,
        entidad: EntidadEvento,
        entidad_id: int
    ):

        return (
            self.db.query(Evento)
            .filter(
                Evento.entidad == entidad.value,
                Evento.entidad_id == entidad_id
            )
            .order_by(
                Evento.created_at.desc()
            )
            .all()
        )

    def contar_por_tipo_desde(
        self,
        tipo: TipoEvento,
        desde: datetime
    ) -> int:

        return (
            self.db.query(Evento)
            .filter(
                Evento.tipo == tipo.value,
                Evento.created_at >= desde
            )
            .count()
        )

    def contar_por_tipo_y_entidad(
        self,
        tipo: TipoEvento,
        entidad: EntidadEvento,
        entidad_id: int
    ) -> int:

        return (
            self.db.query(Evento)
            .filter(
                Evento.tipo == tipo.value,
                Evento.entidad == entidad.value,
                Evento.entidad_id == entidad_id
            )
            .count()
        )