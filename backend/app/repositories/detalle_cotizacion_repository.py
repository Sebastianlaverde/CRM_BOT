from sqlalchemy.orm import Session

from app.models.detalle_cotizacion import DetalleCotizacion


class DetalleCotizacionRepository:

    def __init__(self, db: Session):
        self.db = db

    def add(
        self,
        detalle: DetalleCotizacion
    ):

        self.db.add(detalle)