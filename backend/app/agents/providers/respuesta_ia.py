from dataclasses import dataclass


@dataclass
class RespuestaIA:

    texto: str

    modelo: str = ""

    tokens_entrada: int = 0

    tokens_salida: int = 0

    tokens_total: int = 0
