from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.enums import (
    EstadoProspecto,
    OrigenProspecto,
    TipoNegocio,
)
from app.utils.telefono import normalizar_telefono


class ProspectoBase(BaseModel):
    nombre_empresa: str
    nombre_contacto: Optional[str] = None
    telefono: str
    correo: Optional[EmailStr] = None
    ciudad: str
    direccion: Optional[str] = None
    tipo_negocio: TipoNegocio
    origen: OrigenProspecto = OrigenProspecto.MANUAL
    google_place_id: Optional[str] = None
    observaciones: Optional[str] = None


class ProspectoCreate(ProspectoBase):

    @field_validator("telefono")
    @classmethod
    def _normalizar_telefono(cls, valor: str) -> str:
        return normalizar_telefono(valor)


class ProspectoUpdate(BaseModel):
    nombre_empresa: Optional[str] = None
    nombre_contacto: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    tipo_negocio: Optional[TipoNegocio] = None
    origen: Optional[OrigenProspecto] = None
    estado: Optional[EstadoProspecto] = None
    observaciones: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("telefono")
    @classmethod
    def _normalizar_telefono(
        cls,
        valor: Optional[str]
    ) -> Optional[str]:

        if valor is None:
            return None

        return normalizar_telefono(valor)


class ProspectoResponse(ProspectoBase):
    id: int
    estado: EstadoProspecto
    activo: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CambiarEstadoRequest(BaseModel):
    estado: EstadoProspecto
    observacion: str | None = None