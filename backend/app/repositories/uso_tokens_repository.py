from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.uso_tokens import UsoTokens


class UsoTokensRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        registro: UsoTokens
    ) -> UsoTokens:

        self.db.add(registro)

        self.db.commit()

        self.db.refresh(registro)

        return registro

    def sumar_desde(
        self,
        desde: datetime
    ):

        return (
            self.db.query(
                func.coalesce(
                    func.sum(UsoTokens.tokens_entrada),
                    0
                ),
                func.coalesce(
                    func.sum(UsoTokens.tokens_salida),
                    0
                ),
                func.coalesce(
                    func.sum(UsoTokens.tokens_total),
                    0
                )
            )
            .filter(
                UsoTokens.created_at >= desde
            )
            .first()
        )
