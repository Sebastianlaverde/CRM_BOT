from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.routers.deps import verificar_api_key_control
from app.schemas.estado_cuenta import EstadoCuentaRequest
from app.services.estado_cuenta_service import EstadoCuentaService

router = APIRouter(
    prefix="/interno",
    tags=["Interno (LeadFlow Control)"],
    dependencies=[Depends(verificar_api_key_control)]
)


@router.post(
    "/estado-cuenta"
)
def actualizar_estado_cuenta(
    data: EstadoCuentaRequest,
    db: Session = Depends(get_db)
):

    estado = EstadoCuentaService(db).actualizar_estado(
        data.activo
    )

    return {

        "activo": estado.activo,

        "actualizado_en": estado.actualizado_en

    }
