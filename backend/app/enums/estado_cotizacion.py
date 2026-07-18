from enum import Enum


class EstadoCotizacion(str, Enum):

    BORRADOR = "BORRADOR"

    ENVIADA = "ENVIADA"

    ACEPTADA = "ACEPTADA"

    RECHAZADA = "RECHAZADA"

    VENCIDA = "VENCIDA"