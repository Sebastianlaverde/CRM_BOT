from app.agents.tools.base_tool import BaseTool

from app.services.producto_service import ProductoService


class ProductoTool(BaseTool):

    def __init__(
        self,
        db
    ):

        self.service = ProductoService(
            db
        )

    @property
    def name(self):

        return "buscar_productos"

    @property
    def description(self):

        return (
            "Busca productos disponibles en el catálogo."
        )

    @property
    def parameters(self):

        return {

            "nombre": {

                "type": "string",

                "required": False

            }

        }

    def execute(
        self,
        **kwargs
    ):

        return self.service.listar_productos(
            kwargs.get("nombre")
        )