from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.utils.horario_laboral import es_horario_laboral

BOGOTA = ZoneInfo("America/Bogota")
UTC = ZoneInfo("UTC")

# 2024-01-01 fue lunes; 2024-01-05 viernes; 2024-01-06 sabado;
# 2024-01-07 domingo.


@pytest.mark.parametrize(
    "momento, esperado",
    [
        (datetime(2024, 1, 1, 10, 0, tzinfo=BOGOTA), True),   # lunes, dentro
        (datetime(2024, 1, 5, 16, 59, tzinfo=BOGOTA), True),  # viernes, dentro
        (datetime(2024, 1, 1, 8, 59, tzinfo=BOGOTA), False),  # lunes, antes de horario
        (datetime(2024, 1, 1, 17, 0, tzinfo=BOGOTA), False),  # lunes, borde exacto (excluido)
        (datetime(2024, 1, 6, 10, 0, tzinfo=BOGOTA), False),  # sabado
        (datetime(2024, 1, 7, 10, 0, tzinfo=BOGOTA), False),  # domingo
    ]
)
def test_es_horario_laboral_en_bogota(momento, esperado):

    assert es_horario_laboral(momento) is esperado


def test_es_horario_laboral_convierte_otras_zonas_horarias():

    # 15:00 UTC == 10:00 Bogota (UTC-5) -- lunes, dentro de horario.
    momento_utc = datetime(2024, 1, 1, 15, 0, tzinfo=UTC)

    assert es_horario_laboral(momento_utc) is True

    # 23:00 UTC == 18:00 Bogota -- lunes, fuera de horario.
    momento_utc_tarde = datetime(2024, 1, 1, 23, 0, tzinfo=UTC)

    assert es_horario_laboral(momento_utc_tarde) is False
