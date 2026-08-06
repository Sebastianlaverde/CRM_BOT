from sqlalchemy.orm import Session

from app.repositories.producto_repository import ProductoRepository
from app.schemas.producto import (
    ProductoCreate,
    ProductoUpdate,
)


class ProductoService:

    def __init__(self, db: Session):
        self.repository = ProductoRepository(db)

    def crear_producto(
        self,
        data: ProductoCreate
    ):
        return self.repository.create(data)

    def listar_productos(self):

        productos = self.repository.find_all()

        productos.sort(
            key=lambda p: p.created_at,
            reverse=True
        )

        return productos

    def buscar_por_id(
        self,
        producto_id: int
    ):
        return self.repository.find_by_id(producto_id)

    def actualizar_producto(
        self,
        producto_id: int,
        data: ProductoUpdate
    ):

        producto = self.repository.find_by_id(producto_id)

        if not producto:
            return None

        return self.repository.update(
            producto,
            data
        )

    def eliminar_producto(
        self,
        producto_id: int
    ):

        producto = self.repository.find_by_id(producto_id)

        if not producto:
            return None

        return self.repository.delete(producto)

    def buscar_por_nombre(
        self,
        nombre: str
    ):

        return self.repository.find_by_nombre(
            nombre
        )


    def buscar_por_referencia(
        self,
        referencia: str
    ):

        return self.repository.find_by_referencia(
            referencia
        )