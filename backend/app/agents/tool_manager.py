from sqlalchemy.orm import Session

from app.agents.tools.producto_tool import ProductoTool
from app.agents.tools.prospecto_tool import ProspectoTool
from app.agents.tools.cotizacion_tool import CotizacionTool
from app.agents.tools.historial_tool import HistorialTool


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

        self.register(
            CotizacionTool(db)
        )

        self.register(
            HistorialTool(db)
        )

    def register(
        self,
        tool
    ):

        self.tools[
            tool.name
        ] = tool

    def get_available_tools(
        self
    ):

        return [

            {

                "name": tool.name,

                "description": tool.description,

                "parameters": tool.parameters

            }

            for tool in self.tools.values()

        ]

    def get_openai_tools(
        self
    ):

        return [

            tool.to_openai_function()

            for tool in self.tools.values()

        ]

    def execute(
        self,
        tool_name: str,
        **kwargs
    ):

        tool = self.tools.get(
            tool_name
        )

        if tool is None:

            raise ValueError(
                f"Herramienta '{tool_name}' no encontrada."
            )

        return tool.execute(
            **kwargs
        )