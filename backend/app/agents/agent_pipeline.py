from app.agents.context_builder import ContextBuilder
from app.agents.prompt_builder import PromptBuilder
from app.agents.rule_engine import RuleEngine
from app.agents.objective_engine import ObjectiveEngine
from app.agents.ai_service import AIService
from app.agents.tool_manager import ToolManager
from app.agents.decision_engine import DecisionEngine

class AgentPipeline:


    def __init__(
        self,
        db
    ):

        self.context_builder = ContextBuilder(db)

        self.prompt_builder = PromptBuilder()

        self.rule_engine = RuleEngine()

        self.objective_engine = ObjectiveEngine()

        self.ai_service = AIService()

        self.tool_manager = ToolManager(db)

        self.decision_engine = DecisionEngine()

    def execute(
        self,
        prospecto_id,
        mensaje
    ):

        contexto = self._build_context(
            prospecto_id
        )

        prompt = self._build_prompt(
            contexto,
            mensaje
        )

        tools = (
            self.tool_manager
            .get_openai_tools()
        )

        respuesta = self._call_ai(

            prompt=prompt,

            mensaje=mensaje,

            tools=tools

        )

        decision = self.decision_engine.decidir(

            respuesta_ia=respuesta,

            contexto=contexto

        )

        return decision

    def _build_context(
        self,
        prospecto_id
    ):

        return self.context_builder.build(
            prospecto_id
        )

    def _build_prompt(
        self,
        contexto,
        mensaje
    ):

        tools = (
            self.tool_manager
            .get_available_tools()
        )

        reglas = self.rule_engine.evaluate(

            contexto,

            mensaje

        )

        objetivo = (
            self.objective_engine
            .get_objective(
                contexto["prospecto"].estado
            )
        )

        return self.prompt_builder.build(

            contexto=contexto,

            reglas=reglas,

            objetivo=objetivo,

            tools=tools

        )

    def _call_ai(
        self,
        prompt,
        mensaje,
        tools
    ):

        return self.ai_service.responder(

            prompt=prompt,

            mensaje=mensaje,

            tools=tools,

            tool_executor=self.tool_manager.execute

        )
