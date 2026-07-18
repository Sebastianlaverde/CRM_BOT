from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.enums import EstadoProspecto


class HistorialEstado(Base):

    __tablename__ = "historial_estados"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    prospecto_id: Mapped[int] = mapped_column(
        ForeignKey("prospectos.id"),
        nullable=False
    )

    estado_anterior: Mapped[EstadoProspecto] = mapped_column(
        Enum(EstadoProspecto),
        nullable=False
    )

    estado_nuevo: Mapped[EstadoProspecto] = mapped_column(
        Enum(EstadoProspecto),
        nullable=False
    )

    observacion: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    prospecto = relationship(
        "Prospecto",
        back_populates="historial"
    )