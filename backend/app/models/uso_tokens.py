from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class UsoTokens(Base):

    __tablename__ = "uso_tokens"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    prospecto_id: Mapped[int | None] = mapped_column(
        ForeignKey("prospectos.id"),
        nullable=True
    )

    origen: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    modelo: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    tokens_entrada: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    tokens_salida: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    tokens_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
