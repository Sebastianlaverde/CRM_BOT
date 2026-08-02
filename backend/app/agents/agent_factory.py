from sqlalchemy.orm import Session

from app.agents.commercial_agent import CommercialAgent


class AgentFactory:

    @staticmethod
    def get_agent(
        agent_type: str,
        db: Session
    ):

        if agent_type == "commercial":
            return CommercialAgent(db)

        raise ValueError(
            f"Agente '{agent_type}' no soportado."
        )