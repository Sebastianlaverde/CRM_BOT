from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers.deps import verificar_cuenta_activa
from app.schemas.seguimiento import (
    SeguimientoEjecutarRequest,
    SeguimientoEjecutarResponse,
)
from app.services.seguimiento_service import SeguimientoService

router = APIRouter(
    prefix="/api/v1/seguimiento",
    tags=["Seguimiento"],
    dependencies=[Depends(verificar_cuenta_activa)]
)


@router.post(
    "/ejecutar",
    response_model=SeguimientoEjecutarResponse
)
def ejecutar_seguimiento(
    data: SeguimientoEjecutarRequest = SeguimientoEjecutarRequest(),
    db: Session = Depends(get_db)
):

    service = SeguimientoService(db)

    return service.ejecutar(
        dry_run=data.dry_run
    )
