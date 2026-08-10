from app.core.config import settings

from app.constants.ai import (
    OPENAI,
    OLLAMA,
    GEMINI,
    MOCK
)

from app.agents.providers.base_provider import BaseProvider
from app.agents.providers.mock_provider import MockProvider
from app.agents.providers.openai_provider import OpenAIProvider


class AIService:

    def __init__(self):

        self.provider = self._build_provider()

    def _build_provider(self) -> BaseProvider:

        provider_name = settings.AI_PROVIDER

        if provider_name == OPENAI:

            return OpenAIProvider()

        if provider_name == MOCK:

            return MockProvider()

        if provider_name in (OLLAMA, GEMINI):

            raise NotImplementedError(
                f"El proveedor '{provider_name}' aún "
                f"no tiene una implementación disponible."
            )

        raise ValueError(
            f"AI_PROVIDER '{provider_name}' no es válido. "
            f"Valores soportados: {OPENAI}, {MOCK}, {OLLAMA}, {GEMINI}."
        )

    def responder(
        self,
        prompt,
        historial,
        tools,
        tool_executor
    ):

        return self.provider.generate(

            prompt,

            historial,

            tools,

            tool_executor

        )