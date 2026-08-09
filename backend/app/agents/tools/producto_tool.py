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
            "Permite consultar los productos disponibles de la empresa. "
            "Puede listar todos los productos, buscar por nombre o por referencia."
        )

    @property
    def parameters(self):

        return {

            "accion": {

                "type": "string",

                "description": (
                    "Acción a realizar sobre el catálogo "
                    "de productos."
                ),

                "enum": [

                    "listar",

                    "buscar_nombre",

                    "buscar_referencia"

                ],

                "required": True

            },

            "nombre": {

                "type": "string",

                "description": (
                    "Nombre o parte del nombre del "
                    "producto a buscar."
                ),

                "required": False

            },

            "referencia": {

                "type": "string",

                "description": (
                    "Referencia o código del "
                    "producto a buscar."
                ),

                "required": False

            }

        }

    def execute(
        self,
        accion,
        nombre=None,
        referencia=None
    ):

        if accion == "listar":

            productos = self.service.listar_productos()

        elif accion == "buscar_nombre":

            productos = self.service.buscar_por_nombre(
                nombre
            )

        elif accion == "buscar_referencia":

            productos = self.service.buscar_por_referencia(
                referencia
            )

        else:

            raise ValueError(
                "Acción no soportada."
            )

        return self._serializar(
            productos
        )

    def _serializar(
        self,
        productos
    ):

        resultado = []

        for producto in productos:

            resultado.append({

                "id": producto.id,

                "nombre": producto.nombre,

                "referencia": producto.referencia,

                "descripcion": producto.descripcion,

                "precio": float(producto.precio),

                "activo": producto.activo

            })

        return resultado