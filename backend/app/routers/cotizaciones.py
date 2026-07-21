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