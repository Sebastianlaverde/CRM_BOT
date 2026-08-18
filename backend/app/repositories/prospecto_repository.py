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

    def buscar_por_telefono(
        self,
        telefono: str
    ):

        return (
            self.db.query(Prospecto)
            .filter(
                Prospecto.telefono == telefono
            )
            .first()
        )

    def buscar_por_google_place_id(
        self,
        google_place_id: str
    ):

        return (
            self.db.query(Prospecto)
            .filter(
                Prospecto.google_place_id == google_place_id
            )
            .first()
        )

    def contar_por_estados(
        self,
        estados: list[EstadoProspecto]
    ) -> int:

        return (
            self.db.query(Prospecto)
            .filter(
                Prospecto.estado.in_(estados),
                Prospecto.activo.is_(True)
            )
            .count()
        )

    def listar_por_estado_ordenado(
        self,
        estado: EstadoProspecto,
        limite: int | None = None
    ):

        query = (
            self.db.query(Prospecto)
            .filter(
                Prospecto.estado == estado,
                Prospecto.activo.is_(True)
            )
            .order_by(
                Prospecto.created_at.asc()
            )
        )

        if limite is not None:
            query = query.limit(limite)

        return query.all()