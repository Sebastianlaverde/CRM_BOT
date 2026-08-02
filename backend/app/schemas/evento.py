from datetime import datetime

from pydantic import BaseModel

from app.enums import (
    OrigenEvento,
    TipoEvento,
)


class EventoCreate(BaseModel):

    tipo: TipoEvento

    entidad: str

    entidad_id: int

    descripcion: str

    origen: OrigenEvento


class EventoResponse(BaseModel):

    id: int

    tipo: TipoEvento

    entidad: str

    entidad_id: int

    descripcion: str

    origen: OrigenEvento

    created_at: datetime

    model_config = {
        "from_attributes": True
    }