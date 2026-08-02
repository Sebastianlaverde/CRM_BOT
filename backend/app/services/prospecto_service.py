from sqlalchemy.orm import Session

from app.enums import EstadoProspecto
from app.repositories.prospecto_repository import ProspectoRepository
from app.schemas.prospecto import (
    ProspectoCreate,
    ProspectoUpdate,
)
from app.services.historial_service import HistorialService
from app.schemas.historial import HistorialEstadoCreate
from app.services.prospecto_state_service import ProspectoStateService


class ProspectoService:

    def __init__(self, db: Session):
        self.repository = ProspectoRepository(db)
        self.historial_service = HistorialService(db)
        self.state_service = ProspectoStateService(db)

    def crear_prospecto(self, data: ProspectoCreate):
        return self.repository.create(data)

    def listar_prospectos(self):

        prospectos = self.repository.find_all()

        prospectos.sort(
            key=lambda p: p.created_at,
            reverse=True
        )

        return prospectos

    def buscar_por_id(self, prospecto_id: int):
        return self.repository.find_by_id(prospecto_id)
    
    def actualizar_prospecto(
        self,
        prospecto_id: int,
        data: ProspectoUpdate
    ):

        prospecto = self.repository.find_by_id(prospecto_id)

        if not prospecto:
            return None

        return self.repository.update(
            prospecto,
            data
        )
    
    def cambiar_estado(
        self,
        prospecto_id: int,
        estado: EstadoProspecto,
        observacion: str | None = None
    ):

        prospecto = self.repository.find_by_id(prospecto_id)

        if prospecto is None:
            return None

        return self.state_service.cambiar_estado(
            prospecto=prospecto,
            nuevo_estado=estado,
            observacion=observacion
        )
                