from app.agents.providers.base_provider import BaseProvider
from app.agents.providers.respuesta_ia import RespuestaIA


class MockProvider(BaseProvider):

    def generate(
        self,
        prompt: str,
        historial: list[dict],
        tools: list,
        tool_executor
    ) -> RespuestaIA:

        print("===== PROMPT =====")
        print(prompt)

        print("===== HISTORIAL =====")

        for turno in historial:

            print(
                f"{turno['role']}: {turno['content']}"
            )

        return RespuestaIA(

            texto=(
                "Hola, gracias por escribirnos. "
                "Un asesor revisará tu solicitud."
            ),

            modelo="mock"

        )