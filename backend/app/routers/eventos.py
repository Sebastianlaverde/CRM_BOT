from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.enums import EntidadEvento
from app.schemas.evento import EventoResponse
from app.services.evento_service import EventoService

router = APIRouter(
    prefix="/api/v1/eventos",
    tags=["Eventos"]
)

@router.get(
    "",
    response_model=list[EventoResponse]
)
def listar_eventos(
    db: Session = Depends(get_db)
):

    service = EventoService(db)

    return service.obtener_todos()

@router.get(
    "/{entidad}/{entidad_id}",
    response_model=list[EventoResponse]
)
def listar_eventos_entidad(
    entidad: EntidadEvento,
    entidad_id: int,
    db: Session = Depends(get_db)
):

    service = EventoService(db)

    return service.obtener_por_entidad(
        entidad,
        entidad_id
    )