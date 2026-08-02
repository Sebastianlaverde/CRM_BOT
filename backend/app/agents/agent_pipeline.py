class AgentPipeline:

    def __init__(self, db):

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
    
        contexto = self.context_builder.build(
            prospecto_id
        )

        reglas = self.rule_engine.evaluate(
            contexto,
            mensaje
        )

        objetivo = self.objective_engine.get_objective(
            contexto["prospecto"].estado
        )

        prompt = self.prompt_builder.build(
            contexto=contexto,
            reglas=reglas,
            objetivo=objetivo
        )

        respuesta = self.ai_service.responder(
            prompt,
            mensaje
        )

        decision = self.decision_engine.decidir(
            respuesta
        )

        return decision