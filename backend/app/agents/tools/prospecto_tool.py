from app.agents.tools.base_tool import BaseTool
from app.enums import EstadoProspecto
from app.services.prospecto_service import ProspectoService

class ProspectoTool(BaseTool):


    def __init__(
        self,
        db
    ):

        self.service = ProspectoService(db)

    @property
    def name(
        self
    ):

        return "actualizar_estado"

    @property
    def description(
        self
    ):

        return (
            "Permite consultar el estado actual de un prospecto "
            "y actualizarlo cuando avance o cambie dentro "
            "del proceso comercial."
        )

    @property
    def parameters(
        self
    ):

        return {

            "accion": {

                "type": "string",

                "description": (
                    "Acción que se desea realizar."
                ),

                "enum": [

                    "consultar",

                    "cambiar_estado"

                ],

                "required": True

            },

            "prospecto_id": {

                "type": "integer",

                "description": (
                    "Identificador del prospecto."
                ),

                "required": True

            },

            "estado": {

                "type": "string",

                "description": (
                    "Nuevo estado comercial del prospecto."
                ),

                "enum": [

                    estado.value
                    for estado in EstadoProspecto

                ],

                "required": False

            },

            "observacion": {

                "type": "string",

                "description": (
                    "Observación relacionada con "
                    "el cambio de estado."
                ),

                "required": False

            }

        }

    def execute(
        self,
        accion,
        prospecto_id,
        estado=None,
        observacion=None
    ):

        prospecto = self.service.buscar_por_id(
            prospecto_id
        )

        if prospecto is None:

            return {

                "success": False,

                "message": (
                    "No se encontró el prospecto."
                )

            }

        if accion == "consultar":

            return {

                "success": True,

                "data": self._serialize(
                    prospecto
                )

            }

        if accion == "cambiar_estado":

            if estado is None:

                raise ValueError(
                    "Se requiere el estado."
                )

            try:

                nuevo_estado = (
                    EstadoProspecto(estado)
                )

            except ValueError:

                raise ValueError(
                    f"Estado de prospecto no válido: "
                    f"{estado}"
                )

            actualizado = (
                self.service.cambiar_estado(

                    prospecto_id=prospecto_id,

                    estado=nuevo_estado,

                    observacion=observacion

                )
            )

            if actualizado is None:

                return {

                    "success": False,

                    "message": (
                        "No fue posible actualizar "
                        "el estado del prospecto."
                    )

                }

            return {

                "success": True,

                "data": self._serialize(
                    actualizado
                ),

                "message": (
                    "Prospecto actualizado correctamente."
                )

            }

        raise ValueError(
            f"Acción no soportada: {accion}"
        )

    def _serialize(
        self,
        prospecto
    ):

        return {

            "id": prospecto.id,

            "nombre_empresa": (
                prospecto.nombre_empresa
            ),

            "nombre_contacto": (
                prospecto.nombre_contacto
            ),

            "telefono": (
                prospecto.telefono
            ),

            "correo": (
                prospecto.correo
            ),

            "ciudad": (
                prospecto.ciudad
            ),

            "direccion": (
                prospecto.direccion
            ),

            "tipo_negocio": (
                prospecto.tipo_negocio
            ),

            "origen": (
                prospecto.origen
            ),

            "estado": (
                prospecto.estado.value
                if prospecto.estado
                else None
            ),

            "observaciones": (
                prospecto.observaciones
            ),

            "activo": prospecto.activo

        }
