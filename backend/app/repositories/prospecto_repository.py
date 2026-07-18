from sqlalchemy.orm import Session

from app.enums import EstadoProspecto
from app.models.prospecto import Prospecto
from app.schemas.prospecto import (
    ProspectoCreate,
    ProspectoUpdate,
)

class ProspectoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProspectoCreate) -> Prospecto:

        prospecto = Prospecto(
            **data.model_dump()
        )

        self.db.add(prospecto)
        self.db.commit()
        self.db.refresh(prospecto)

        return prospecto

    def find_all(self):

        return (
            self.db.query(Prospecto)
            .filter(Prospecto.activo.is_(True))
            .all()
        )

    def find_by_id(self, prospecto_id: int):

        return (
            self.db.query(Prospecto)
            .filter(
                Prospecto.id == prospecto_id,
                Prospecto.activo.is_(True)
            )
            .first()
        )
    
    def update(
        self,
        prospecto: Prospecto,
        data: ProspectoUpdate
    ) -> Prospecto:

        datos = data.model_dump(exclude_unset=True)

        for campo, valor in datos.items():
            setattr(prospecto, campo, valor)

        self.db.commit()
        self.db.refresh(prospecto)

        return prospecto
    
    def cambiar_estado(
        self,
        prospecto: Prospecto,
        estado: EstadoProspecto
    ):

        prospecto.estado = estado

        self.db.commit()

        self.db.refresh(prospecto)

        return prospecto