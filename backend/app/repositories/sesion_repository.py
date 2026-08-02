from sqlalchemy.orm import Session

from app.enums import (
    CanalComunicacion,
    EstadoConversacion,
)
from app.models.sesion_conversacion import SesionConversacion


class SesionRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener_sesion_activa(
        self,
        prospecto_id: int,
        canal: CanalComunicacion
    ):

        return (
            self.db.query(SesionConversacion)
            .filter(
                SesionConversacion.prospecto_id == prospecto_id,
                SesionConversacion.canal == canal,
                SesionConversacion.estado == EstadoConversacion.ABIERTA,
            )
            .first()
        )

    def crear(
        self,
        prospecto_id: int,
        canal: CanalComunicacion
    ):

        sesion = SesionConversacion(
            prospecto_id=prospecto_id,
            canal=canal
        )

        self.db.add(sesion)

        self.db.commit()

        self.db.refresh(sesion)

        return sesion

    def obtener_o_crear(
        self,
        prospecto_id: int,
        canal: CanalComunicacion
    ):

        sesion = self.obtener_sesion_activa(
            prospecto_id,
            canal
        )

        if sesion:
            return sesion

        return self.crear(
            prospecto_id,
            canal
        )