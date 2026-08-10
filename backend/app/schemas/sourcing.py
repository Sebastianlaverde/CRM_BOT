from pydantic import BaseModel
from pydantic import Field

from app.enums import TipoNegocio


class SourcingBuscarRequest(BaseModel):

    tipo_negocio: TipoNegocio

    zona: str

    max_resultados: int = Field(
        default=5,
        ge=1,
        le=20
    )

    dry_run: bool = True


class SourcingResultado(BaseModel):

    google_place_id: str

    nombre_empresa: str

    telefono: str | None

    direccion: str | None

    estado_resultado: str


class SourcingBuscarResponse(BaseModel):

    query: str

    dry_run: bool

    total_encontrados: int

    importados: int

    duplicados: int

    descartados_sin_telefono: int

    resultados: list[SourcingResultado]
