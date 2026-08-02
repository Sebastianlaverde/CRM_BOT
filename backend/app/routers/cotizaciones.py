from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.cotizacion import (
    CotizacionCreate,
    CotizacionResponse,
)
from app.services.cotizacion_service import CotizacionService

router = APIRouter(
    prefix="/api/v1/cotizaciones",
    tags=["Cotizaciones"]
)

@router.post(
    "",
    response_model=CotizacionResponse,
    status_code=201
)
def crear_cotizacion(
    data: CotizacionCreate,
    db: Session = Depends(get_db)
):

    service = CotizacionService(db)

    try:

        return service.crear_cotizacion(data)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get(
    "",
    response_model=List[CotizacionResponse]
)
def listar_cotizaciones(
    db: Session = Depends(get_db)
):

    service = CotizacionService(db)

    return service.obtener_todas()


@router.get(
    "/{cotizacion_id}",
    response_model=CotizacionResponse
)
def obtener_cotizacion(
    cotizacion_id: int,
    db: Session = Depends(get_db)
):

    service = CotizacionService(db)

    try:

        return service.obtener_por_id(
            cotizacion_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )