from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        message: str,
        tools: list,
        tool_executor
    ) -> str:
        pass