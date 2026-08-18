from datetime import datetime
from zoneinfo import ZoneInfo

ZONA_HORARIA_NEGOCIO = ZoneInfo("America/Bogota")

DIA_SEMANA_INICIO = 0  # lunes

DIA_SEMANA_FIN = 4  # viernes

HORA_INICIO = 9

HORA_FIN = 17


def es_horario_laboral(
    ahora: datetime | None = None
) -> bool:

    if ahora is None:

        ahora = datetime.now(
            ZONA_HORARIA_NEGOCIO
        )

    else:

        ahora = ahora.astimezone(
            ZONA_HORARIA_NEGOCIO
        )

    if not (DIA_SEMANA_INICIO <= ahora.weekday() <= DIA_SEMANA_FIN):
        return False

    return HORA_INICIO <= ahora.hour < HORA_FIN
