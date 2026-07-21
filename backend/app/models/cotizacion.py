from decimal import Decimal

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums import EstadoCotizacion


class Cotizacion(Base):

    __tablename__ = "cotizaciones"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    prospecto_id: Mapped[int] = mapped_column(
        ForeignKey("prospectos.id"),
        nullable=False
    )

    estado: Mapped[EstadoCotizacion] = mapped_column(
        Enum(EstadoCotizacion),
        nullable=False,
        default=EstadoCotizacion.BORRADOR
    )

    observaciones: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    valor_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00")
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

    prospecto = relationship(
        "Prospecto",
        back_populates="cotizaciones"
    )

    detalles = relationship(
        "DetalleCotizacion",
        back_populates="cotizacion",
        cascade="all, delete-orphan"
    )