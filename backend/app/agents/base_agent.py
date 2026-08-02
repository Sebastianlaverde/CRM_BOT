from abc import ABC
from abc import abstractmethod


class BaseAgent(ABC):

    @abstractmethod
    def responder(
        self,
        contexto: dict,
        mensaje: str
    ):
        pass