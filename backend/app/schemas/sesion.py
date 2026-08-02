from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

from app.enums import (
    CanalComunicacion,
    EstadoConversacion,
)


class SesionResponse(BaseModel):

    id: int

    prospecto_id: int

    canal: CanalComunicacion

    estado: EstadoConversacion

    ia_activa: bool

    ultima_actividad: datetime

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )