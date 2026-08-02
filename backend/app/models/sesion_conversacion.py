from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums import (
    CanalComunicacion,
    EstadoConversacion,
)


class SesionConversacion(Base):

    __tablename__ = "sesiones_conversacion"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    prospecto_id: Mapped[int] = mapped_column(
        ForeignKey("prospectos.id"),
        nullable=False,
    )

    canal: Mapped[CanalComunicacion] = mapped_column(
        Enum(CanalComunicacion, native_enum=False),
        nullable=False,
    )

    estado: Mapped[EstadoConversacion] = mapped_column(
        Enum(EstadoConversacion, native_enum=False),
        default=EstadoConversacion.ABIERTA,
        nullable=False,
    )

    ia_activa: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    ultima_actividad: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    prospecto = relationship(
        "Prospecto",
        back_populates="sesiones",
    )

    mensajes = relationship(
        "Mensaje",
        back_populates="sesion",
        cascade="all, delete-orphan",
    )
    