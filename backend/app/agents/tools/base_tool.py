from abc import ABC, abstractmethod

class BaseTool(ABC):

```
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

        property_schema = {

            "type": info["type"]

        }

        if "description" in info:

            property_schema["description"] = (
                info["description"]
            )

        if "enum" in info:

            property_schema["enum"] = (
                info["enum"]
            )

        properties[parameter] = property_schema

        if info.get(
            "required",
            False
        ):

            required.append(
                parameter
            )

    schema = {

        "type": "object",

        "properties": properties

    }

    if required:

        schema["required"] = required

    return {

        "type": "function",

        "name": self.name,

        "description": self.description,

        "parameters": schema

    }
```
