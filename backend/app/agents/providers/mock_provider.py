from app.agents.providers.base_provider import BaseProvider


class MockProvider(BaseProvider):

    def generate(
        self,
        prompt: str,
        historial: list[dict],
        tools: list,
        tool_executor
    ) -> str:

        print("===== PROMPT =====")
        print(prompt)

        print("===== HISTORIAL =====")

        for turno in historial:

            print(
                f"{turno['role']}: {turno['content']}"
            )

        return (
            "Hola, gracias por escribirnos. "
            "Un asesor revisará tu solicitud."
        )