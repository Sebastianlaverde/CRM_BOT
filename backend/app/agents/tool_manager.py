from sqlalchemy.orm import Session

from app.agents.tools.producto_tool import ProductoTool
from app.agents.tools.prospecto_tool import ProspectoTool

class ToolManager:


    def __init__(
        self,
        db: Session
    ):

        self.tools = {}

        self.register(
            ProductoTool(db)
        )

        self.register(
            ProspectoTool(db)
        )

    def register(
        self,
        tool
    ):

        self.tools[tool.name] = tool

    def get_available_tools(
        self
    ):

        tools = []

        for tool in self.tools.values():

            openai_function = tool.to_openai_function()

            tools.append({

                "name": tool.name,

                "description": tool.description,

                "parameters": openai_function["parameters"]

            })

        return tools

    def get_openai_tools(
        self
    ):

        return [

            tool.to_openai_function()

            for tool in self.tools.values()

        ]

    def execute(
        self,
        tool_name,
        **kwargs
    ):

        tool = self.tools.get(
            tool_name
        )

        if tool is None:

            raise ValueError(
                f"Herramienta "
                f"'{tool_name}' "
                f"no encontrada."
            )

        return tool.execute(
            **kwargs
        )