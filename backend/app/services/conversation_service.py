from sqlalchemy.orm import Session

from app.enums import (
    AutorMensaje,
    TipoMensaje,
    EstadoConversacion,
)
from app.models.mensaje import Mensaje
from app.repositories.mensaje_repository import MensajeRepository
from app.repositories.prospecto_repository import ProspectoRepository
from app.services.sesion_service import SesionService
from app.services.decision_action_executor import DecisionActionExecutor
from app.agents.agent_factory import AgentFactory
from app.enums.decision_type import DecisionType

class ConversationService:

    def __init__(self, db: Session):

        self.db = db

        self.prospecto_repository = ProspectoRepository(db)

        self.sesion_service = SesionService(db)

        self.mensaje_repository = MensajeRepository(db)

        self.action_executor = DecisionActionExecutor(db)

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

        self.action_executor.ejecutar(
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

        sesion.estado = (
            EstadoConversacion.ESPERANDO_ASESOR
            if decision["type"] == DecisionType.ESCALAR_A_HUMANO
            else EstadoConversacion.ESPERANDO_CLIENTE
        )

        self.db.commit()

        return respuesta
