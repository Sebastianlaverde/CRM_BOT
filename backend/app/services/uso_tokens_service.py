from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Session

from app.models.uso_tokens import UsoTokens
from app.repositories.uso_tokens_repository import UsoTokensRepository


class UsoTokensService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = UsoTokensRepository(db)

    def registrar(
        self,
        prospecto_id,
        origen,
        modelo,
        tokens_entrada,
        tokens_salida,
        tokens_total
    ):

        registro = UsoTokens(

            prospecto_id=prospecto_id,

            origen=origen,

            modelo=modelo,

            tokens_entrada=tokens_entrada,

            tokens_salida=tokens_salida,

            tokens_total=tokens_total

        )

        return self.repository.create(
            registro
        )

    def resumen_de_hoy(self):

        inicio_de_hoy = (
            datetime.now(timezone.utc)
            .replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
        )

        entrada, salida, total = self.repository.sumar_desde(
            inicio_de_hoy
        )

        return {

            "periodo_desde": inicio_de_hoy,

            "tokens_entrada": entrada,

            "tokens_salida": salida,

            "tokens_total": total

        }
