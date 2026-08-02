from sqlalchemy.orm import Session

from app.repositories.historial_repository import HistorialRepository
from app.schemas.historial import HistorialEstadoCreate
from app.enums import EstadoProspecto
from app.models.prospecto import Prospecto

class HistorialService:

    def __init__(self, db: Session):
        self.repository = HistorialRepository(db)

    def registrar(
        self,
        data: HistorialEstadoCreate
    ):
        return self.repository.create(data)

    def registrar_cambio(
        self,
        prospecto: Prospecto,
        estado_anterior: EstadoProspecto,
        estado_nuevo: EstadoProspecto,
        observacion: str | None = None
    ):

        data = HistorialEstadoCreate(
            prospecto_id=prospecto.id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            observacion=observacion
        )

        return self.repository.create(data)

    def listar(
        self,
        prospecto_id: int
    ):
        return self.repository.find_by_prospecto(
            prospecto_id
        )