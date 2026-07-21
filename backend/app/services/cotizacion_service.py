from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cotizacion import Cotizacion
from app.models.detalle_cotizacion import DetalleCotizacion
from app.enums import EstadoCotizacion

from app.repositories.cotizacion_repository import CotizacionRepository
from app.repositories.detalle_cotizacion_repository import DetalleCotizacionRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.prospecto_repository import ProspectoRepository
from app.schemas.cotizacion import CotizacionCreate

class CotizacionService:

    def __init__(self, db: Session):

        self.db = db

        self.cotizacion_repository = CotizacionRepository(db)
        self.detalle_repository = DetalleCotizacionRepository(db)
        self.producto_repository = ProductoRepository(db)
        self.prospecto_repository = ProspectoRepository(db)

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
                
                producto = self.producto_repository.find_by_id(
                    item.producto_id
                )

                if producto is None:
                    raise ValueError(
                        f"El producto con ID {item.producto_id} no existe."
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

            self.cotizacion_repository.commit()

            self.cotizacion_repository.refresh(
                cotizacion
            )

            return cotizacion
        
        except Exception:

            self.cotizacion_repository.rollback()

            raise