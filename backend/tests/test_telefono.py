import pytest

from app.utils.telefono import normalizar_telefono


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        (
            "+57 318 1329452",
            "573181329452"
        ),
        (
            "3001234567",
            "573001234567"
        ),
        (
            "573001234567",
            "573001234567"
        ),
    ]
)
def test_normalizar_telefono_casos_validos(
    entrada,
    esperado
):

    assert normalizar_telefono(entrada) == esperado


def test_normalizar_telefono_es_idempotente():

    normalizado_una_vez = normalizar_telefono(
        "+57 318 1329452"
    )

    normalizado_dos_veces = normalizar_telefono(
        normalizado_una_vez
    )

    assert normalizado_una_vez == normalizado_dos_veces


@pytest.mark.parametrize(
    "entrada",
    [
        "12345",
        "string",
        "",
        None,
        "+1 555 0100",
    ]
)
def test_normalizar_telefono_casos_invalidos(
    entrada
):

    with pytest.raises(ValueError):
        normalizar_telefono(entrada)
