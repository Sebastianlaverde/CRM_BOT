import logging

from sqlalchemy.orm import Session

from app.enums import EstadoProspecto
from app.services.prospecto_service import ProspectoService
from app.services.evento_service import EventoService

logger = logging.getLogger(__name__)


class DecisionActionExecutor:

    def __init__(self, db: Session):

        self.prospecto_service = ProspectoService(db)

        self.evento_service = EventoService(db)

    def ejecutar(
        self,
        acciones,
        prospecto
    ):

        for accion in acciones:

            match accion["type"]:

                case "actualizar_estado":

                    self._actualizar_estado(
                        prospecto,
                        accion
                    )

                case "escalar_a_humano":

                    self.evento_service.registrar_escalamiento(
                        prospecto=prospecto,
                        motivo=accion["motivo"]
                    )

                case _:

                    pass

    def _actualizar_estado(
        self,
        prospecto,
        accion
    ):

        try:

            self.prospecto_service.cambiar_estado(
                prospecto_id=prospecto.id,
                estado=EstadoProspecto(accion["estado"]),
                observacion=accion.get("observacion")
            )

        except ValueError as e:

            logger.warning(
                f"No se pudo aplicar la transición de "
                f"estado del prospecto {prospecto.id}: {e}"
            )
