from abc import ABC
from abc import abstractmethod


class BaseAgent(ABC):

    @abstractmethod
    def responder(
        self,
        prospecto_id: int,
        mensaje: str,
        canal
    ):
        pass