from enum import Enum


class TipoNegocio(str, Enum):
    PIZZERIA = "PIZZERIA"

    PANADERIA = "PANADERIA"

    RESTAURANTE = "RESTAURANTE"

    CAFETERIA = "CAFETERIA"

    HAMBURGUESERIA = "HAMBURGUESERIA"

    OTRO = "OTRO"