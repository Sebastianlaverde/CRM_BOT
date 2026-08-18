from abc import ABC, abstractmethod

from app.agents.providers.respuesta_ia import RespuestaIA


class BaseProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        historial: list[dict],
        tools: list,
        tool_executor
    ) -> RespuestaIA:
        pass