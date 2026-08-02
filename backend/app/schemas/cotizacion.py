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

class ProspectoResumenResponse(BaseModel):

    id: int
    nombre_empresa: str
    telefono: str

    model_config = {
        "from_attributes": True
    }


class ProductoResumenResponse(BaseModel):

    id: int
    nombre: str

    model_config = {
        "from_attributes": True
    }

class DetalleCotizacionResponse(BaseModel):

    id: int
    
    producto: ProductoResumenResponse

    cantidad: int

    precio_unitario: Decimal

    subtotal: Decimal

    model_config = {
        "from_attributes": True
    }


class CotizacionResponse(BaseModel):

    id: int
    prospecto: ProspectoResumenResponse
    estado: EstadoCotizacion
    observaciones: str | None
    valor_total: Decimal

    detalles: list[DetalleCotizacionResponse]

    model_config = {
        "from_attributes": True
    }
