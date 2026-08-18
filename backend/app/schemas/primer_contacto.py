from pydantic import BaseModel


class PrimerContactoEjecutarRequest(BaseModel):

    dry_run: bool = True


class PrimerContactoResultado(BaseModel):

    prospecto_id: int

    nombre_empresa: str

    telefono: str

    estado_resultado: str


class PrimerContactoEjecutarResponse(BaseModel):

    dry_run: bool

    evaluados: int

    enviados: int

    motivo_corte: str | None = None

    resultados: list[PrimerContactoResultado]
