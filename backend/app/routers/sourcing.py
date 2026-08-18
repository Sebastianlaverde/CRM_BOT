from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers.deps import verificar_cuenta_activa
from app.schemas.sourcing import (
    SourcingBuscarRequest,
    SourcingBuscarResponse,
)
from app.services.sourcing_service import SourcingService

router = APIRouter(
    prefix="/api/v1/sourcing",
    tags=["Sourcing"],
    dependencies=[Depends(verificar_cuenta_activa)]
)


@router.post(
    "/buscar",
    response_model=SourcingBuscarResponse
)
def buscar_prospectos(
    data: SourcingBuscarRequest,
    db: Session = Depends(get_db)
):

    service = SourcingService(db)

    try:

        return service.buscar(data)

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
