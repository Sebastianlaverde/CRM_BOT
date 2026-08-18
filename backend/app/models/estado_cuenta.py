from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class EstadoCuenta(Base):

    __tablename__ = "estado_cuenta"

    # Fila única (id=1 siempre) -- es el caché local de la config que
    # vive en LeadFlow Control (el nombre quedó corto: empezó siendo
    # solo el interruptor activo/inactivo, ahora también cachea
    # zona_busqueda_google_places y pausar_prospeccion -- se dejó el
    # nombre de tabla para no romper lo que ya funciona). Lo actualiza
    # el push de Control (POST /interno/estado-cuenta, solo `activo`)
    # o el chequeo periódico de respaldo cada 3 min (los 3 campos,
    # ver app/services/estado_cuenta_poller.py).

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    zona_busqueda_google_places: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    pausar_prospeccion: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    actualizado_en: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
