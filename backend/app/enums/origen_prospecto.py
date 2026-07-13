from enum import Enum


class OrigenProspecto(str, Enum):
    GOOGLE_MAPS = "GOOGLE_MAPS"

    MANUAL = "MANUAL"

    EXCEL = "EXCEL"

    PAGINA_WEB = "PAGINA_WEB"

    REFERIDO = "REFERIDO"

    FACEBOOK = "FACEBOOK"

    INSTAGRAM = "INSTAGRAM"

    OTRO = "OTRO"