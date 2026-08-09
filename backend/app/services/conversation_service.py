from sqlalchemy.orm import Session
import logging

from app.enums import (
    AutorMensaje,
    TipoMensaje,
    EstadoProspecto,
)
from app.models.mensaje import Mensaje
from app.repositories.mensaje_repository import MensajeRepository
from app.repositories.prospecto_repository import ProspectoRepository
from app.services.sesion_service import SesionService
from app.services.evento_service import EventoService
from app.services.prospecto_service import ProspectoService
from app.agents.agent_factory import AgentFactory
from app.enums.decision_type import DecisionType

logger = logging.getLogger(__name__)

class ConversationService:

    def __init__(self, db: Session):

        self.db = db

        self.prospecto_repository = ProspectoRepository(db)

        self.sesion_service = SesionService(db)

        self.mensaje_repository = MensajeRepository(db)

        self.evento_service = EventoService(db)

        self.prospecto_service = ProspectoService(db)

        self.agent = AgentFactory.get_agent(
            "commercial",
            db
        )

    def recibir_mensaje(
        self,
        telefono: str,
        contenido: str,
        canal
    ):

        prospecto = self.prospecto_repository.buscar_por_telefono(
            telefono
        )

        if prospecto is None:
            raise ValueError(
                "No existe un prospecto con ese teléfono."
            )

        sesion = self.sesion_service.obtener_o_crear(
            prospecto.id,
            canal
        )

        mensaje = Mensaje(

            sesion_id=sesion.id,

            autor=AutorMensaje.CLIENTE,

            tipo=TipoMensaje.TEXTO,

            contenido=contenido,
        )

        self.mensaje_repository.create(
            mensaje
        )

        decision = self.agent.responder(
            prospecto.id,
            contenido,
            canal
        )

        match decision["type"]:

            case DecisionType.RESPONDER:

                respuesta = decision["contenido"]

            case DecisionType.ESCALAR_A_HUMANO:

                respuesta = decision["contenido"]

            case _:

                raise NotImplementedError(
                    f"Tipo de decisión "
                    f"'{decision['type']}' no soportado."
                )

        self._execute_actions(
            decision["acciones"],
            prospecto
        )

        respuesta_ia = Mensaje(

            sesion_id=sesion.id,

            autor=AutorMensaje.IA,

            tipo=TipoMensaje.TEXTO,

            contenido=respuesta
        )

        self.mensaje_repository.create(
            respuesta_ia
        )

        return respuesta

    def _execute_actions(
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