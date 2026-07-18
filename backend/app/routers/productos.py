from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.producto import (
    ProductoCreate,
    ProductoResponse,
    ProductoUpdate,
)
from app.services.producto_service import ProductoService

router = APIRouter(
    prefix="/api/v1/productos",
    tags=["Productos"]
)


@router.post(
    "",
    response_model=ProductoResponse,
    status_code=201
)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db)
):

    service = ProductoService(db)

    return service.crear_producto(data)


@router.get(
    "",
    response_model=list[ProductoResponse]
)
def listar_productos(
    db: Session = Depends(get_db)
):

    service = ProductoService(db)

    return service.listar_productos()


@router.get(
    "/{producto_id}",
    response_model=ProductoResponse
)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):

    service = ProductoService(db)

    producto = service.buscar_por_id(producto_id)

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return producto


@router.put(
    "/{producto_id}",
    response_model=ProductoResponse
)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db)
):

    service = ProductoService(db)

    producto = service.actualizar_producto(
        producto_id,
        data
    )

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return producto


@router.delete(
    "/{producto_id}",
    response_model=ProductoResponse
)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):

    service = ProductoService(db)

    producto = service.eliminar_producto(
        producto_id
    )

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return producto