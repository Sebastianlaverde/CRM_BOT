from sqlalchemy.orm import Session

from app.models.producto import Producto
from app.schemas.producto import (
    ProductoCreate,
    ProductoUpdate,
)


class ProductoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ProductoCreate):

        producto = Producto(
            **data.model_dump()
        )

        self.db.add(producto)

        self.db.commit()

        self.db.refresh(producto)

        return producto

    def find_all(self):

        return (
            self.db.query(Producto)
            .filter(Producto.activo.is_(True))
            .all()
        )

    def find_by_id(self, producto_id: int):

        return (
            self.db.query(Producto)
            .filter(
                Producto.id == producto_id,
                Producto.activo.is_(True)
            )
            .first()
        )

    def update(
        self,
        producto: Producto,
        data: ProductoUpdate
    ):

        datos = data.model_dump(exclude_unset=True)

        for campo, valor in datos.items():
            setattr(producto, campo, valor)

        self.db.commit()

        self.db.refresh(producto)

        return producto

    def delete(
        self,
        producto: Producto
    ):

        producto.activo = False

        self.db.commit()

        self.db.refresh(producto)

        return producto

    def find_by_nombre(
        self,
        nombre: str
    ):

        return (
            self.db.query(Producto)
            .filter(
                Producto.nombre.ilike(f"%{nombre}%"),
                Producto.activo.is_(True)
            )
            .all()
        )


    def find_by_referencia(
        self,
        referencia: str
    ):

        return (
            self.db.query(Producto)
            .filter(
                Producto.referencia.ilike(f"%{referencia}%"),
                Producto.activo.is_(True)
            )
            .all()
        )