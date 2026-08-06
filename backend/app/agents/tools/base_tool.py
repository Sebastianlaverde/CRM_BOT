from abc import ABC, abstractmethod


class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    @abstractmethod
    def parameters(self):
        pass

    @abstractmethod
    def execute(
        self,
        **kwargs
    ):
        pass

    def to_openai_function(
        self
    ):

        properties = {}

        required = []

        for parameter, info in self.parameters.items():

            properties[parameter] = {

                "type": info["type"]

            }

            if info.get(
                "required",
                False
            ):

                required.append(
                    parameter
                )

        return {

            "type": "function",

            "name": self.name,

            "description": self.description,

            "parameters": {

                "type": "object",

                "properties": properties,

                "required": required

            }

        }