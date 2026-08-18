from app.agents.context_builder import ContextBuilder
from app.agents.prompt_builder import PromptBuilder
from app.agents.rule_engine import RuleEngine
from app.agents.objective_engine import ObjectiveEngine
from app.agents.ai_service import AIService
from app.agents.tool_manager import ToolManager
from app.agents.decision_engine import DecisionEngine
from app.enums import AutorMensaje
from app.services.uso_tokens_service import UsoTokensService

ROL_OPENAI_POR_AUTOR = {

    AutorMensaje.CLIENTE: "user",

    AutorMensaje.IA: "assistant",

    AutorMensaje.ASESOR: "assistant",

}

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

        self.uso_tokens_service = UsoTokensService(db)

    def execute(
        self,
        prospecto_id,
        mensaje,
        canal
    ):

        contexto = self._build_context(
            prospecto_id,
            canal
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

            contexto=contexto,

            tools=tools,

            origen="conversacion"

        )

        decision = self.decision_engine.decidir(

            respuesta_ia=respuesta,

            contexto=contexto

        )

        return decision

    def generar_seguimiento(
        self,
        prospecto_id,
        canal,
        dias_sin_respuesta
    ):

        contexto = self._build_context(
            prospecto_id,
            canal
        )

        prompt = self._build_prompt(

            contexto,

            mensaje=None,

            dias_sin_respuesta=dias_sin_respuesta

        )

        tools = (
            self.tool_manager
            .get_openai_tools()
        )

        respuesta = self._call_ai(

            prompt=prompt,

            contexto=contexto,

            tools=tools,

            origen="seguimiento"

        )

        decision = self.decision_engine.decidir(

            respuesta_ia=respuesta,

            contexto=contexto

        )

        return decision

    def _build_context(
        self,
        prospecto_id,
        canal
    ):

        return self.context_builder.build(
            prospecto_id,
            canal
        )

    def _build_prompt(
        self,
        contexto,
        mensaje,
        dias_sin_respuesta=None
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

            tools=tools,

            dias_sin_respuesta=dias_sin_respuesta

        )

    def _call_ai(
        self,
        prompt,
        contexto,
        tools,
        origen
    ):

        historial = self._build_historial(
            contexto["mensajes"]
        )

        respuesta_ia = self.ai_service.responder(

            prompt=prompt,

            historial=historial,

            tools=tools,

            tool_executor=self.tool_manager.execute

        )

        self.uso_tokens_service.registrar(

            prospecto_id=contexto["prospecto"].id,

            origen=origen,

            modelo=respuesta_ia.modelo,

            tokens_entrada=respuesta_ia.tokens_entrada,

            tokens_salida=respuesta_ia.tokens_salida,

            tokens_total=respuesta_ia.tokens_total

        )

        return respuesta_ia.texto

    def _build_historial(
        self,
        mensajes
    ):

        historial = []

        for mensaje in mensajes:

            rol = ROL_OPENAI_POR_AUTOR.get(
                mensaje.autor
            )

            if rol is None:
                continue

            historial.append({

                "role": rol,

                "content": mensaje.contenido

            })

        return historial