from pydantic import BaseModel


class EstadoCuentaRequest(BaseModel):

    activo: bool
