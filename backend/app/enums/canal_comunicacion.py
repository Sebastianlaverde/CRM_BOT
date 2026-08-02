from enum import Enum


class CanalComunicacion(str, Enum):

    WHATSAPP = "WHATSAPP"

    INSTAGRAM = "INSTAGRAM"

    FACEBOOK = "FACEBOOK"

    TELEGRAM = "TELEGRAM"

    EMAIL = "EMAIL"

    WEBCHAT = "WEBCHAT"