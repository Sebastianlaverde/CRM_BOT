from sqlalchemy import Column, Integer, String

from app.database.base import Base


class Prospecto(Base):

    __tablename__ = "prospectos"

    id = Column(Integer, primary_key=True, index=True)

    nombre_empresa = Column(String)

    telefono = Column(String)

    ciudad = Column(String)

    estado = Column(String)