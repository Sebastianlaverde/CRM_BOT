from sqlalchemy.orm import Session

from app.repositories.historial_repository import HistorialRepository
from app.schemas.historial import HistorialEstadoCreate


class HistorialService:

    def __init__(self, db: Session):
        self.repository = HistorialRepository(db)

    def registrar(
        self,
        data: HistorialEstadoCreate
    ):
        return self.repository.create(data)

    def listar(
        self,
        prospecto_id: int
    ):
        return self.repository.find_by_prospecto(
            prospecto_id
        )