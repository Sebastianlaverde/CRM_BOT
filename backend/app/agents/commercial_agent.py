from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.agents.agent_pipeline import AgentPipeline


class CommercialAgent(BaseAgent):

    def __init__(
        self,
        db: Session
    ):

        self.pipeline = AgentPipeline(db)

    def responder(
        self,
        prospecto_id: int,
        mensaje: str,
        canal
    ):

        return self.pipeline.execute(
            prospecto_id,
            mensaje,
            canal
        )

    def generar_seguimiento(
        self,
        prospecto_id: int,
        canal,
        dias_sin_respuesta: int
    ):

        return self.pipeline.generar_seguimiento(
            prospecto_id,
            canal,
            dias_sin_respuesta
        )