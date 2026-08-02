from enum import Enum


class EntidadEvento(str, Enum):

    PROSPECTO = "prospecto"

    COTIZACION = "cotizacion"

    PEDIDO = "pedido"

    PRODUCTO = "producto"

    CONVERSACION = "conversacion"