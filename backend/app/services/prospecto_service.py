from sqlalchemy.orm import Session

from app.enums import EstadoProspecto
from app.repositories.prospecto_repository import ProspectoRepository
from app.schemas.prospecto import (
    ProspectoCreate,
    ProspectoUpdate,
)
from app.core.prospecto_flow import ProspectoFlow
from app.services.historial_service import HistorialService
from app.schemas.historial import HistorialEstadoCreate

class ProspectoService:

    def __init__(self, db: Session):
        self.repository = ProspectoRepository(db)
        self.historial_service = HistorialService(db)

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
        estado: EstadoProspecto
    ):

        prospecto = self.repository.find_by_id(prospecto_id)

        if not prospecto:
            return None

        estado_actual = prospecto.estado

        if estado_actual == estado:
            return prospecto

        if not ProspectoFlow.puede_cambiar(
            estado_actual,
            estado
        ):
            raise ValueError(
                f"No se puede cambiar de {estado_actual.value} a {estado.value}"
            )

        estado_anterior = prospecto.estado

        prospecto_actualizado = self.repository.cambiar_estado(
            prospecto,
            estado
        )

        self.historial_service.registrar(
            HistorialEstadoCreate(
                prospecto_id=prospecto.id,
                estado_anterior=estado_anterior,
                estado_nuevo=estado,
                observacion=None
            )
        )

        return prospecto_actualizado
        