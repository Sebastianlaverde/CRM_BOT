from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base
from app.enums import (
    TipoEvento,
    OrigenEvento,
)


class Evento(Base):

    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    tipo: Mapped[TipoEvento] = mapped_column(
        Enum(TipoEvento, native_enum=False),
        nullable=False
    )

    entidad: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    entidad_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    origen: Mapped[OrigenEvento] = mapped_column(
        Enum(OrigenEvento, native_enum=False),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )