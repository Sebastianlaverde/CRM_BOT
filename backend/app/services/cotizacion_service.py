from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cotizacion import Cotizacion
from app.models.detalle_cotizacion import DetalleCotizacion
from app.services.evento_service import EventoService

from app.enums import (
    EstadoCotizacion,
    EstadoProspecto,
    OrigenEvento,
    TipoEvento,
    EntidadEvento,
)

from app.repositories.cotizacion_repository import CotizacionRepository
from app.repositories.detalle_cotizacion_repository import DetalleCotizacionRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.prospecto_repository import ProspectoRepository
from app.schemas.cotizacion import CotizacionCreate
from app.mappers.cotizacion_mapper import CotizacionMapper

class CotizacionService:

    def __init__(self, db: Session):

        self.db = db

        self.cotizacion_repository = CotizacionRepository(db)
        self.detalle_repository = DetalleCotizacionRepository(db)
        self.producto_repository = ProductoRepository(db)
        self.prospecto_repository = ProspectoRepository(db)
        self.evento_service = EventoService(db)

    def crear_cotizacion(
        self,
        data: CotizacionCreate
    ):
    
        try:

            prospecto = self.prospecto_repository.find_by_id(
                data.prospecto_id
            )

            if prospecto is None:
                raise ValueError(
                    "El prospecto no existe."
                )

            if not prospecto.activo:
                raise ValueError(
                    "El prospecto está inactivo."
                )

            if prospecto.estado == EstadoProspecto.DESCARTADO:
                raise ValueError(
                    "No es posible crear cotizaciones para un prospecto descartado."
                )

            if not data.productos:
                raise ValueError(
                    "Debe agregar al menos un producto."
                )
            
            cotizacion = Cotizacion(

                prospecto_id=data.prospecto_id,

                estado=EstadoCotizacion.BORRADOR,

                observaciones=data.observaciones,

                valor_total=Decimal("0.00")
            )

            self.cotizacion_repository.add(
                cotizacion
            )

            self.cotizacion_repository.flush()

            total = Decimal("0.00")

            for item in data.productos:

                if item.cantidad <= 0:
                    raise ValueError(
                        "La cantidad debe ser mayor que cero."
                    )
                
                producto = self.producto_repository.find_by_id(
                    item.producto_id
                )

                if producto is None:
                    raise ValueError(
                        f"El producto con ID {item.producto_id} no existe."
                    )

                if not producto.activo:
                    raise ValueError(
                        f"El producto {producto.nombre} está inactivo."
                    )

                if producto.precio <= 0:
                    raise ValueError(
                        f"El producto '{producto.nombre}' no tiene un precio válido."
                    )

                subtotal = producto.precio * item.cantidad

                detalle = DetalleCotizacion(

                    cotizacion_id=cotizacion.id,

                    producto_id=producto.id,

                    cantidad=item.cantidad,

                    precio_unitario=producto.precio,

                    subtotal=subtotal
                )

                self.detalle_repository.add(
                    detalle
                )

                total += subtotal
            
            cotizacion.valor_total = total

            self.evento_service.registrar_cotizacion_creada(
                cotizacion,
                prospecto
            )
                        

            self.cotizacion_repository.commit()

            self.cotizacion_repository.refresh(
                cotizacion
            )

            return CotizacionMapper.to_response(
                cotizacion
            )
        
        except Exception:

            self.cotizacion_repository.rollback()

            raise

    def obtener_todas(self) -> list[Cotizacion]:

        cotizaciones = self.cotizacion_repository.list_all()

        return CotizacionMapper.to_response_list(
            cotizaciones
        )


    def obtener_por_id(
        self,
        cotizacion_id: int
    ) -> Cotizacion:

        cotizacion = self.cotizacion_repository.find_by_id(
            cotizacion_id
        )

        if cotizacion is None:
            raise ValueError(
                "La cotización no existe."
            )

        return CotizacionMapper.to_response(
            cotizacion
        )