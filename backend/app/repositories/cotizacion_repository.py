from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.cotizacion import Cotizacion


class CotizacionRepository:

    def __init__(self, db: Session):
        self.db = db

    def add(self, cotizacion: Cotizacion):

        self.db.add(cotizacion)

    def find_by_id(
        self,
        cotizacion_id: int
    ) -> Cotizacion | None:

        return (
            self.db.query(Cotizacion)
            .options(
                joinedload(Cotizacion.detalles)
            )
            .filter(
                Cotizacion.id == cotizacion_id
            )
            .first()
        )

    def list_all(self):

        return (
            self.db.query(Cotizacion)
            .options(
                joinedload(Cotizacion.detalles)
            )
            .all()
        )

    def flush(self):

        self.db.flush()

    def commit(self):

        self.db.commit()

    def rollback(self):

        self.db.rollback()

    def refresh(
        self,
        cotizacion: Cotizacion
    ):

        self.db.refresh(cotizacion)