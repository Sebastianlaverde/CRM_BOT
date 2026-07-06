from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prospecto(Base):
    __tablename__ = "prospectos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    nombre_empresa: Mapped[str] = mapped_column(String(255))

    telefono: Mapped[str] = mapped_column(String(20))

    ciudad: Mapped[str] = mapped_column(String(100))

    estado: Mapped[str] = mapped_column(String(50))