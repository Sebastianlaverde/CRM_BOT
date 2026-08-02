from sqlalchemy.orm import Session

from app.enums import CanalComunicacion
from app.repositories.sesion_repository import SesionRepository


class SesionService:

    def __init__(self, db: Session):

        self.repository = SesionRepository(db)

    def obtener_o_crear(
        self,
        prospecto_id: int,
        canal: CanalComunicacion
    ):

        return self.repository.obtener_o_crear(
            prospecto_id,
            canal
        )