from sqlalchemy.orm import Session

from app.models.estado_cuenta import EstadoCuenta


class EstadoCuentaRepository:

    def __init__(self, db: Session):
        self.db = db

    def obtener(self):

        return (
            self.db.query(EstadoCuenta)
            .filter(EstadoCuenta.id == 1)
            .first()
        )

    def actualizar(
        self,
        activo: bool,
        zona_busqueda_google_places=None,
        pausar_prospeccion=None
    ):

        estado = self.obtener()

        if estado is None:

            estado = EstadoCuenta(
                id=1,
                activo=activo,
                zona_busqueda_google_places=zona_busqueda_google_places,
                pausar_prospeccion=pausar_prospeccion or False
            )

            self.db.add(estado)

        else:

            estado.activo = activo

            if zona_busqueda_google_places is not None:
                estado.zona_busqueda_google_places = (
                    zona_busqueda_google_places
                )

            if pausar_prospeccion is not None:
                estado.pausar_prospeccion = pausar_prospeccion

        self.db.commit()

        self.db.refresh(estado)

        return estado
