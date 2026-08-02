from enum import Enum


class AutorMensaje(str, Enum):

    CLIENTE = "CLIENTE"

    IA = "IA"

    ASESOR = "ASESOR"

    SISTEMA = "SISTEMA"