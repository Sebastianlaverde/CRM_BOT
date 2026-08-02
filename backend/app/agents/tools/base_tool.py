from abc import ABC
from abc import abstractmethod


class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def parameters(self) -> dict:
        pass

    @abstractmethod
    def execute(
        self,
        **kwargs
    ):
        pass

    @property
    def requires_confirmation(self):

        return True