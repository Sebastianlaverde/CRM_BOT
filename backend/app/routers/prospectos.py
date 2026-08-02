from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.prospecto_service import ProspectoService
from app.schemas.prospecto import (
    CambiarEstadoRequest,
    ProspectoCreate,
    ProspectoResponse,
    ProspectoUpdate,
)

router = APIRouter(
    prefix="/api/v1/prospectos",
    tags=["Prospectos"]
)


@router.post(
    "",
    response_model=ProspectoResponse,
    status_code=201
)
def crear_prospecto(
    data: ProspectoCreate,
    db: Session = Depends(get_db)
):

    service = ProspectoService(db)

    return service.crear_prospecto(data)


@router.get(
    "",
    response_model=list[ProspectoResponse]
)
def listar_prospectos(
    db: Session = Depends(get_db)
):

    service = ProspectoService(db)

    return service.listar_prospectos()


@router.get(
    "/{prospecto_id}",
    response_model=ProspectoResponse
)
def obtener_prospecto(
    prospecto_id: int,
    db: Session = Depends(get_db)
):

    service = ProspectoService(db)

    prospecto = service.buscar_por_id(prospecto_id)

    if not prospecto:
        raise HTTPException(
            status_code=404,
            detail="Prospecto no encontrado"
        )

    return prospecto

@router.put(
    "/{prospecto_id}",
    response_model=ProspectoResponse
)
def actualizar_prospecto(
    prospecto_id: int,
    data: ProspectoUpdate,
    db: Session = Depends(get_db)
):

    service = ProspectoService(db)

    prospecto = service.actualizar_prospecto(
        prospecto_id,
        data
    )

    if not prospecto:
        raise HTTPException(
            status_code=404,
            detail="Prospecto no encontrado"
        )

    return prospecto

@router.patch(
    "/{prospecto_id}/estado",
    response_model=ProspectoResponse
)
def cambiar_estado(
    prospecto_id: int,
    data: CambiarEstadoRequest,
    db: Session = Depends(get_db)
):

    service = ProspectoService(db)

    try:

        prospecto = service.cambiar_estado(
            prospecto_id=prospecto_id,
            estado=data.estado,
            observacion=data.observacion
        )

        if not prospecto:
            raise HTTPException(
                status_code=404,
                detail="Prospecto no encontrado"
            )

        return prospecto

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )