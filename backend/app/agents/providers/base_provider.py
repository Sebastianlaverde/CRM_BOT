from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        historial: list[dict],
        tools: list,
        tool_executor
    ) -> str:
        pass