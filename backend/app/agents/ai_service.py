from app.core.config import settings

from app.constants.ai import (
    OPENAI,
    OLLAMA,
    GEMINI
)

from app.agents.providers.base_provider import BaseProvider
from app.agents.providers.mock_provider import MockProvider
from app.agents.providers.openai_provider import OpenAIProvider


class AIService:

    def __init__(self):

        self.provider = self._build_provider()

    def _build_provider(
        self
    ) -> BaseProvider:

        match settings.AI_PROVIDER:

            case OPENAI:

                return OpenAIProvider()

            case OLLAMA:

                raise NotImplementedError(
                    "Ollama aún no implementado."
                )

            case GEMINI:

                raise NotImplementedError(
                    "Gemini aún no implementado."
                )

            case _:

                return MockProvider()

    def responder(
        self,
        prompt: str,
        mensaje: str,
        tools: list,
        tool_executor
    ) -> str:

        return self.provider.generate(

            prompt=prompt,

            message=mensaje,

            tools=tools,

            tool_executor=tool_executor

        )