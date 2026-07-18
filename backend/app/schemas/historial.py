from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict

from app.enums import EstadoProspecto


class HistorialEstadoCreate(BaseModel):

    prospecto_id: int
    estado_anterior: EstadoProspecto
    estado_nuevo: EstadoProspecto
    observacion: str | None = None


class HistorialEstadoResponse(BaseModel):

    id: int
    prospecto_id: int
    estado_anterior: EstadoProspecto
    estado_nuevo: EstadoProspecto
    observacion: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)