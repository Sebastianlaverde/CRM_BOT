import re

INDICATIVO_COLOMBIA = "57"

LONGITUD_LOCAL = 10

LONGITUD_CON_INDICATIVO = 12


def normalizar_telefono(valor: str) -> str:

    digitos = re.sub(
        r"\D",
        "",
        valor or ""
    )

    if len(digitos) == LONGITUD_LOCAL:

        digitos = INDICATIVO_COLOMBIA + digitos

    if (
        len(digitos) == LONGITUD_CON_INDICATIVO
        and digitos.startswith(INDICATIVO_COLOMBIA)
    ):

        return digitos

    raise ValueError(
        f"'{valor}' no parece un número de celular colombiano "
        f"válido (se esperan 10 dígitos locales, o 12 con "
        f"indicativo '{INDICATIVO_COLOMBIA}')."
    )
