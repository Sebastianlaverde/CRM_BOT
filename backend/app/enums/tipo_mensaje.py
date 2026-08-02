from enum import Enum


class TipoMensaje(str, Enum):

    TEXTO = "TEXTO"

    IMAGEN = "IMAGEN"

    AUDIO = "AUDIO"

    VIDEO = "VIDEO"

    DOCUMENTO = "DOCUMENTO"

    UBICACION = "UBICACION"

    CONTACTO = "CONTACTO"

    STICKER = "STICKER"