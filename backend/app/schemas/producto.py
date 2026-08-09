from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict


class ProductoBase(BaseModel):

    nombre: str

    referencia: Optional[str] = None

    descripcion: Optional[str] = None

    precio: Decimal


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):

    nombre: Optional[str] = None

    referencia: Optional[str] = None

    descripcion: Optional[str] = None

    precio: Optional[Decimal] = None

    activo: Optional[bool] = None


class ProductoResponse(ProductoBase):

    id: int

    activo: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)