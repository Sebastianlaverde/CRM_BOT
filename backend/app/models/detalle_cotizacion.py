from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base


class DetalleCotizacion(Base):

    __tablename__ = "detalle_cotizacion"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    cotizacion_id: Mapped[int] = mapped_column(
        ForeignKey("cotizaciones.id"),
        nullable=False
    )

    producto_id: Mapped[int] = mapped_column(
        ForeignKey("productos.id"),
        nullable=False
    )

    cantidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    precio_unitario: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    cotizacion = relationship(
        "Cotizacion",
        back_populates="detalles"
    )

    producto = relationship(
        "Producto",
        back_populates="detalles"
    )