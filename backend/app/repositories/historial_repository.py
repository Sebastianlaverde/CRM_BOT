from sqlalchemy.orm import Session

from app.models.historial_estado import HistorialEstado
from app.schemas.historial import HistorialEstadoCreate


class HistorialRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        data: HistorialEstadoCreate
    ):

        historial = HistorialEstado(
            **data.model_dump()
        )

        self.db.add(historial)
        self.db.commit()
        self.db.refresh(historial)

        return historial

    def find_by_prospecto(
        self,
        prospecto_id: int
    ):

        return (
            self.db.query(HistorialEstado)
            .filter(
                HistorialEstado.prospecto_id == prospecto_id
            )
            .order_by(
                HistorialEstado.created_at.desc()
            )
            .all()
        )