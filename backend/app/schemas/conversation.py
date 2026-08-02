from pydantic import BaseModel

from app.enums import CanalComunicacion


class MensajeEntrante(BaseModel):

    telefono: str

    contenido: str

    canal: CanalComunicacion