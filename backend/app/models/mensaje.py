from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums import (
    AutorMensaje,
    TipoMensaje,
)


class Mensaje(Base):

    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    sesion_id: Mapped[int] = mapped_column(
        ForeignKey("sesiones_conversacion.id"),
        nullable=False
    )

    autor: Mapped[AutorMensaje] = mapped_column(
        Enum(AutorMensaje, native_enum=False),
        nullable=False
    )

    tipo: Mapped[TipoMensaje] = mapped_column(
        Enum(TipoMensaje, native_enum=False),
        nullable=False
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    proveedor_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    adjunto_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    sesion = relationship(
        "SesionConversacion",
        back_populates="mensajes"
    )