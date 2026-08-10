from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums import (
    EstadoProspecto,
    OrigenProspecto,
    TipoNegocio,
)


class Prospecto(Base):

    __tablename__ = "prospectos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre_empresa: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    nombre_contacto: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    telefono: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )

    correo: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True
    )

    ciudad: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    direccion: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    tipo_negocio: Mapped[TipoNegocio] = mapped_column(
        Enum(TipoNegocio, native_enum=False),
        nullable=False
    )
    
    origen: Mapped[OrigenProspecto] = mapped_column(
        Enum(OrigenProspecto, native_enum=False),
        nullable=False,
        default=OrigenProspecto.MANUAL
    )

    google_place_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True
    )

    estado: Mapped[EstadoProspecto] = mapped_column(
        Enum(EstadoProspecto, native_enum=False),
        nullable=False,
        default=EstadoProspecto.NUEVO
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    historial = relationship(
        "HistorialEstado",
        back_populates="prospecto",
        cascade="all, delete-orphan"

    )

    cotizaciones = relationship(
        "Cotizacion",
        back_populates="prospecto"
    )

    sesiones = relationship(
        "SesionConversacion",
        back_populates="prospecto",
        cascade="all, delete-orphan"
    )