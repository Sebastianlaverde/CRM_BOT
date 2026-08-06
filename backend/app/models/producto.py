from app.agents.tools.base_tool import BaseTool
from app.services.producto_service import ProductoService


class ProductoTool(BaseTool):

    def __init__(self, db):

        self.service = ProductoService(db)

    @property
    def name(self):

        return "buscar_productos"

    @property
    def description(self):

        return (
            "Consulta los productos disponibles de la empresa."
            " Permite listar todos los productos o buscarlos por nombre."
        )

    @property
    def parameters(self):

        return {

            "type": "object",

            "properties": {

                "accion": {

                    "type": "string",

                    "enum": [

                        "listar",

                        "buscar_nombre"

                    ]

                },

                "nombre": {

                    "type": "string"

                }

            },

            "required": [

                "accion"

            ]

        }

    def execute(
        self,
        accion,
        nombre=None
    ):

        if accion == "listar":

            productos = self.service.listar_productos()

        elif accion == "buscar_nombre":

            productos = self.service.buscar_por_nombre(
                nombre
            )

        else:

            raise ValueError(
                "Acción no soportada."
            )

        return self._serialize(
            productos
        )

    def _serialize(
        self,
        productos
    ):

        resultado = []

        for producto in productos:

            resultado.append({

                "id": producto.id,

                "nombre": producto.nombre,

                "descripcion": producto.descripcion,

                "precio": float(producto.precio)

            })

        return resultado