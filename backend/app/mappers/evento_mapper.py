from app.models.evento import Evento
from app.schemas.evento import EventoResponse


class EventoMapper:

    @staticmethod
    def to_response(evento: Evento) -> EventoResponse:
        return EventoResponse.model_validate(evento)

    @staticmethod
    def to_response_list(eventos: list[Evento]) -> list[EventoResponse]:
        return [
            EventoMapper.to_response(evento)
            for evento in eventos
        ]