from app.agents.tools.base_tool import BaseTool
from app.services.cotizacion_service import CotizacionService
from app.schemas.cotizacion import (
    CotizacionCreate,
    DetalleCotizacionCreate,
)


class CotizacionTool(BaseTool):

    def __init__(
        self,
        db
    ):

        self.service = CotizacionService(db)

    @property
    def name(
        self
    ):

        return "gestionar_cotizacion"

    @property
    def description(
        self
    ):

        return (
            "Permite crear cotizaciones formales para un prospecto "
            "(con productos y cantidades) y consultarlas por ID o "
            "por prospecto."
        )

    @property
    def parameters(
        self
    ):

        return {

            "accion": {

                "type": "string",

                "description": (
                    "Acción a realizar sobre las cotizaciones."
                ),

                "enum": [

                    "crear",

                    "consultar_por_id",

                    "consultar_por_prospecto"

                ],

                "required": True

            },

            "prospecto_id": {

                "type": "integer",

                "description": (
                    "ID del prospecto dueño de la cotización. "
                    "Requerido para 'crear' y "
                    "'consultar_por_prospecto'."
                ),

                "required": False

            },

            "productos": {

                "type": "array",

                "description": (
                    "Lista de productos a incluir en la cotización, "
                    "cada uno con producto_id y cantidad. Requerido "
                    "para 'crear'."
                ),

                "items": {

                    "type": "object",

                    "properties": {

                        "producto_id": {

                            "type": "integer",

                            "description": "ID del producto."

                        },

                        "cantidad": {

                            "type": "integer",

                            "description": (
                                "Cantidad solicitada del producto."
                            )

                        }

                    },

                    "required": [

                        "producto_id",

                        "cantidad"

                    ]

                },

                "required": False

            },

            "observaciones": {

                "type": "string",

                "description": (
                    "Observaciones adicionales para la cotización."
                ),

                "required": False

            },

            "cotizacion_id": {

                "type": "integer",

                "description": (
                    "ID de la cotización a consultar. Requerido "
                    "para 'consultar_por_id'."
                ),

                "required": False

            }

        }

    def execute(
        self,
        accion,
        prospecto_id=None,
        productos=None,
        observaciones=None,
        cotizacion_id=None
    ):

        if accion == "crear":

            return self._crear(
                prospecto_id,
                productos,
                observaciones
            )

        if accion == "consultar_por_id":

            return self._consultar_por_id(
                cotizacion_id
            )

        if accion == "consultar_por_prospecto":

            return self._consultar_por_prospecto(
                prospecto_id
            )

        raise ValueError(
            f"Acción no soportada: {accion}"
        )

    def _crear(
        self,
        prospecto_id,
        productos,
        observaciones
    ):

        if prospecto_id is None:

            raise ValueError(
                "Se requiere el prospecto_id."
            )

        if not productos:

            raise ValueError(
                "Se requiere al menos un producto."
            )

        data = CotizacionCreate(

            prospecto_id=prospecto_id,

            observaciones=observaciones,

            productos=[

                DetalleCotizacionCreate(
                    producto_id=item["producto_id"],
                    cantidad=item["cantidad"]
                )

                for item in productos

            ]

        )

        try:

            cotizacion = self.service.crear_cotizacion(
                data
            )

        except ValueError as e:

            return {

                "success": False,

                "message": str(e)

            }

        return {

            "success": True,

            "data": self._serialize(
                cotizacion
            ),

            "message": (
                "Cotización creada correctamente."
            )

        }

    def _consultar_por_id(
        self,
        cotizacion_id
    ):

        if cotizacion_id is None:

            raise ValueError(
                "Se requiere el cotizacion_id."
            )

        try:

            cotizacion = self.service.obtener_por_id(
                cotizacion_id
            )

        except ValueError as e:

            return {

                "success": False,

                "message": str(e)

            }

        return {

            "success": True,

            "data": self._serialize(
                cotizacion
            )

        }

    def _consultar_por_prospecto(
        self,
        prospecto_id
    ):

        if prospecto_id is None:

            raise ValueError(
                "Se requiere el prospecto_id."
            )

        cotizaciones = self.service.obtener_por_prospecto(
            prospecto_id
        )

        return {

            "success": True,

            "data": [

                self._serialize(cotizacion)

                for cotizacion in cotizaciones

            ]

        }

    def _serialize(
        self,
        cotizacion
    ):

        return {

            "id": cotizacion.id,

            "prospecto_id": cotizacion.prospecto.id,

            "estado": cotizacion.estado.value,

            "observaciones": cotizacion.observaciones,

            "valor_total": float(
                cotizacion.valor_total
            ),

            "detalles": [

                {

                    "producto_id": detalle.producto.id,

                    "producto_nombre": detalle.producto.nombre,

                    "cantidad": detalle.cantidad,

                    "precio_unitario": float(
                        detalle.precio_unitario
                    ),

                    "subtotal": float(
                        detalle.subtotal
                    )

                }

                for detalle in cotizacion.detalles

            ]

        }
