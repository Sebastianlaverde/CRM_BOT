from sqlalchemy.orm import Session

from app.models.mensaje import Mensaje


class MensajeRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, mensaje: Mensaje):

        self.db.add(mensaje)

        self.db.commit()

        self.db.refresh(mensaje)

        return mensaje

    def listar_por_sesion(
        self,
        sesion_id: int
    ):

        return (
            self.db.query(Mensaje)
            .filter(Mensaje.sesion_id == sesion_id)
            .order_by(Mensaje.created_at.asc())
            .all()
        )