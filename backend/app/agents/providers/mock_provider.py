from app.agents.providers.base_provider import BaseProvider


class MockProvider(BaseProvider):

    def generate(
        self,
        prompt: str,
        message: str,
        tools: list,
        tool_executor
    ) -> str:

        print("===== PROMPT =====")
        print(prompt)

        print("===== MENSAJE =====")
        print(message)

        return (
            "Hola, gracias por escribirnos. "
            "Un asesor revisará tu solicitud."
        )