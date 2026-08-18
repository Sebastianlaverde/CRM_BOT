import secrets

from fastapi import Depends
from fastapi import Header
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.services.estado_cuenta_service import EstadoCuentaService


def verificar_api_key_control(
    x_api_key: str | None = Header(default=None)
):

    if not settings.EMPRESA_API_KEY:

        raise HTTPException(
            status_code=503,
            detail="EMPRESA_API_KEY no está configurada en este CRM."
        )

    if x_api_key is None or not secrets.compare_digest(
        x_api_key,
        settings.EMPRESA_API_KEY
    ):

        raise HTTPException(
            status_code=401,
            detail="api_key inválida."
        )


def verificar_cuenta_activa(
    db: Session = Depends(get_db)
):

    if not EstadoCuentaService(db).esta_activo():

        raise HTTPException(
            status_code=403,
            detail=(
                "Esta cuenta está desactivada. Contacta al "
                "administrador de la plataforma."
            )
        )
