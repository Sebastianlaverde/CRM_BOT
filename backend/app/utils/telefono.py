import re

INDICATIVO_COLOMBIA = "57"

LONGITUD_LOCAL = 10

LONGITUD_CON_INDICATIVO = 12

PREFIJO_CELULAR = "3"


class TelefonoFijoError(ValueError):
    pass


def normalizar_telefono(valor: str) -> str:

    digitos = re.sub(
        r"\D",
        "",
        valor or ""
    )

    if len(digitos) == LONGITUD_LOCAL:

        digitos = INDICATIVO_COLOMBIA + digitos

    if not (
        len(digitos) == LONGITUD_CON_INDICATIVO
        and digitos.startswith(INDICATIVO_COLOMBIA)
    ):

        raise ValueError(
            f"'{valor}' no parece un número de celular colombiano "
            f"válido (se esperan 10 dígitos locales, o 12 con "
            f"indicativo '{INDICATIVO_COLOMBIA}')."
        )

    numero_local = digitos[len(INDICATIVO_COLOMBIA):]

    if not numero_local.startswith(PREFIJO_CELULAR):

        raise TelefonoFijoError(
            f"'{valor}' parece un número fijo colombiano, no un "
            f"celular — WhatsApp requiere un número celular."
        )

    return digitos
