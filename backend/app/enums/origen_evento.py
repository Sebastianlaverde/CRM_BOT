from enum import Enum


class OrigenEvento(str, Enum):

    API = "API"

    N8N = "N8N"

    WHATSAPP = "WHATSAPP"

    WEB = "WEB"

    SISTEMA = "SISTEMA"