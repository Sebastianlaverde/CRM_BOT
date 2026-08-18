from sqlalchemy.orm import Session

from app.repositories.estado_cuenta_repository import EstadoCuentaRepository


class EstadoCuentaService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = EstadoCuentaRepository(db)

    def esta_activo(self) -> bool:

        estado = self.repository.obtener()

        if estado is None:

            # Instalación nueva, todavía sin contacto con Control --
            # no bloquear por defecto.
            return True

        return estado.activo

    def esta_pausada_prospeccion(self) -> bool:

        estado = self.repository.obtener()

        if estado is None:
            return False

        return estado.pausar_prospeccion

    def obtener_zona_busqueda(self) -> str | None:

        estado = self.repository.obtener()

        if estado is None:
            return None

        return estado.zona_busqueda_google_places

    def actualizar_estado(
        self,
        activo: bool,
        zona_busqueda_google_places=None,
        pausar_prospeccion=None
    ):

        return self.repository.actualizar(
            activo=activo,
            zona_busqueda_google_places=zona_busqueda_google_places,
            pausar_prospeccion=pausar_prospeccion
        )
