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

    def responder(
        self,
        prompt,
        mensaje,
        tools,
        tool_executor
    ):

        return self.provider.generate(

            prompt,

            mensaje,

            tools,

            tool_executor

        )