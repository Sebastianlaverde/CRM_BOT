from decimal import Decimal

from pydantic import BaseModel

from app.enums import EstadoCotizacion

class DetalleCotizacionCreate(BaseModel):

    producto_id: int
    cantidad: int


class CotizacionCreate(BaseModel):

    prospecto_id: int
    observaciones: str | None = None
    productos: list[DetalleCotizacionCreate]


class DetalleCotizacionResponse(BaseModel):

    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = {
        "from_attributes": True
    }


class CotizacionResponse(BaseModel):

    id: int
    prospecto_id: int
    estado: EstadoCotizacion
    observaciones: str | None
    valor_total: Decimal

    detalles: list[DetalleCotizacionResponse]

    model_config = {
        "from_attributes": True
    }