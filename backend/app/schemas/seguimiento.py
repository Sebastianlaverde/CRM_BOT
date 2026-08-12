from pydantic import BaseModel


class SeguimientoEjecutarRequest(BaseModel):

    dry_run: bool = True


class SeguimientoResultado(BaseModel):

    prospecto_id: int

    nombre_empresa: str

    dias_sin_respuesta: int

    mensaje: str

    canal_envio: str

    plantilla: str | None = None

    estado_resultado: str


class SeguimientoEjecutarResponse(BaseModel):

    dry_run: bool

    evaluados: int

    enviados: int

    resultados: list[SeguimientoResultado]
