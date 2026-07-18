from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.historial import HistorialEstadoResponse
from app.services.historial_service import HistorialService

router = APIRouter(
    prefix="/api/v1/historial",
    tags=["Historial"]
)


@router.get(
    "/{prospecto_id}",
    response_model=list[HistorialEstadoResponse]
)
def listar_historial(
    prospecto_id: int,
    db: Session = Depends(get_db)
):

    service = HistorialService(db)

    return service.listar(prospecto_id)