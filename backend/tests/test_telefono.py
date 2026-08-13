import pytest

from app.utils.telefono import (
    normalizar_telefono,
    TelefonoFijoError,
)


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


@pytest.mark.parametrize(
    "entrada",
    [
        # Caso real encontrado en la prueba de sourcing contra
        # Google Places (New): "Comidas Rápidas Odie" en Palmira.
        "576022864126",
        # Mismo fijo de Cali/Valle sin indicativo.
        "6022864126",
        # Fijo de Bogotá.
        "+57 601 2345678",
    ]
)
def test_normalizar_telefono_rechaza_numeros_fijos(
    entrada
):

    with pytest.raises(TelefonoFijoError):
        normalizar_telefono(entrada)


def test_telefono_fijo_error_es_value_error():

    # TelefonoFijoError debe seguir siendo capturable como
    # ValueError generico (lo usan los validadores de Pydantic y
    # el manejo de errores existente en SourcingService).
    assert issubclass(TelefonoFijoError, ValueError)
