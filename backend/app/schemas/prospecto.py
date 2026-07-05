from pydantic import BaseModel


class ProspectoBase(BaseModel):
    nombre_empresa: str
    telefono: str
    ciudad: str
    estado: str


class ProspectoResponse(ProspectoBase):
    id: int

    class Config:
        from_attributes = True