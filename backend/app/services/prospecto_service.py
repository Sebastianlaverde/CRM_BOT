from sqlalchemy.orm import Session

from app.repositories.prospecto_repository import ProspectoRepository
from app.schemas.prospecto import ProspectoCreate


class ProspectoService:

    def __init__(self, db: Session):
        self.repository = ProspectoRepository(db)

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