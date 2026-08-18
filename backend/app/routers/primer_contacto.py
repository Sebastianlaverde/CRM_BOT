from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers.deps import verificar_cuenta_activa
from app.schemas.primer_contacto import (
    PrimerContactoEjecutarRequest,
    PrimerContactoEjecutarResponse,
)
from app.services.primer_contacto_service import PrimerContactoService

router = APIRouter(
    prefix="/api/v1/primer-contacto",
    tags=["Primer contacto"],
    dependencies=[Depends(verificar_cuenta_activa)]
)


@router.post(
    "/ejecutar",
    response_model=PrimerContactoEjecutarResponse
)
def ejecutar_primer_contacto(
    data: PrimerContactoEjecutarRequest = PrimerContactoEjecutarRequest(),
    db: Session = Depends(get_db)
):

    service = PrimerContactoService(db)

    return service.ejecutar(
        dry_run=data.dry_run
    )
