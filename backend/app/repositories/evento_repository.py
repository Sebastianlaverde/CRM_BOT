from sqlalchemy.orm import Session

from app.models.evento import Evento
from app.enums import EntidadEvento

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