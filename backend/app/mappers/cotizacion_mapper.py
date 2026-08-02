from app.models.cotizacion import Cotizacion

from app.schemas.cotizacion import (
    CotizacionResponse,
    DetalleCotizacionResponse,
    ProductoResumenResponse,
    ProspectoResumenResponse,
)


class CotizacionMapper:

    @staticmethod
    def to_response(
        cotizacion: Cotizacion
    ) -> CotizacionResponse:

        return CotizacionResponse(

            id=cotizacion.id,

            estado=cotizacion.estado,

            observaciones=cotizacion.observaciones,

            valor_total=cotizacion.valor_total,

            prospecto=ProspectoResumenResponse(

                id=cotizacion.prospecto.id,

                nombre_empresa=cotizacion.prospecto.nombre_empresa,

                telefono=cotizacion.prospecto.telefono
            ),

            detalles=[

                DetalleCotizacionResponse(

                    id=detalle.id,

                    producto=ProductoResumenResponse(

                        id=detalle.producto.id,

                        nombre=detalle.producto.nombre
                    ),

                    cantidad=detalle.cantidad,

                    precio_unitario=detalle.precio_unitario,

                    subtotal=detalle.subtotal

                )

                for detalle in cotizacion.detalles

            ]

        )

    @staticmethod
    def to_response_list(
        cotizaciones: list[Cotizacion]
    ) -> list[CotizacionResponse]:

        return [

            CotizacionMapper.to_response(
                cotizacion
            )

            for cotizacion in cotizaciones

        ]