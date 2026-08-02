class ProductoTool(BaseTool):

    @property
    def name(self):

        return "buscar_productos"
    
    @property
    def description(self):

        return (
            "Busca productos disponibles."
        )

    @property
    def parameters(self):

        return {

            "nombre": {

                "type": "string",

                "required": False
            }

        }

    def __init__(
        self,
        db: Session
    ):

        self.db = db

        self.service = ProductoService(db)

    def execute(
        self,
        **kwargs
    ):

        try:

            nombre = kwargs.get("nombre")

            if nombre:

                productos = self.service.buscar_por_nombre(
                    nombre
                )

            else:

                productos = self.service.listar_productos()

            return {

                "success": True,

                "data": productos,

                "message": "Productos encontrados."

            }

        except Exception as e:

            return {

                "success": False,

                "data": None,

                "message": str(e)

            }