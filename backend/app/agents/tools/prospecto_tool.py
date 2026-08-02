class ProspectoTool(BaseTool):

    @property
    def name(self):

        return "actualizar_estado"

    def __init__(self, db):

        self.service = ProspectoService(db)

    def execute(
        self,
        **kwargs
    ):

        return {

            "success": True,

            "data": prospecto,

            "message": "Prospecto actualizado."

        }