from enum import Enum


class EstadoConversacion(str, Enum):

    ABIERTA = "ABIERTA"

    ESPERANDO_CLIENTE = "ESPERANDO_CLIENTE"

    ESPERANDO_IA = "ESPERANDO_IA"

    ESPERANDO_ASESOR = "ESPERANDO_ASESOR"

    CERRADA = "CERRADA"