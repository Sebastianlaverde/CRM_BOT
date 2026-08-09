from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.conversation import MensajeEntrante
from app.services.conversation_service import ConversationService

router = APIRouter(
    prefix="/api/v1/conversaciones",
    tags=["Conversaciones"]
)


@router.post(
    "/mensajes"
)
def recibir_mensaje(
    data: MensajeEntrante,
    db: Session = Depends(get_db)
):

    service = ConversationService(db)

    try:

        respuesta = service.recibir_mensaje(
            telefono=data.telefono,
            contenido=data.contenido,
            canal=data.canal
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    return {

        "respuesta": respuesta

    }