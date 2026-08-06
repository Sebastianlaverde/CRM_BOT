import json

from openai import OpenAI

from app.core.config import settings
from app.agents.providers.base_provider import BaseProvider

class OpenAIProvider(BaseProvider):

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def generate(
        self,
        prompt: str,
        message: str,
        tools: list,
        tool_executor
    ) -> str:

        messages = self._build_messages(
            prompt,
            message
        )

        response = self._first_response(
            messages,
            tools
        )

        while self._has_tool_calls(response):

            tool_outputs = self._execute_tool_calls(
                response,
                tool_executor
            )

            messages.extend(response.output)

            messages.extend(tool_outputs)

            response = self._second_response(
                messages,
                tools
            )

        return self._extract_text(response)

    def _build_messages(
        self,
        prompt: str,
        message: str
    ):

        return [

            {
                "role": "system",
                "content": prompt
            },

            {
                "role": "user",
                "content": message
            }

        ]

    def _first_response(
        self,
        messages,
        tools
    ):

        return self._call_openai(
            messages,
            tools
        )

    def _second_response(
        self,
        messages,
        tools
    ):

        return self._call_openai(
            messages,
            tools
        )

    def _has_tool_calls(
        self,
        response
    ):

        for item in response.output:

            if item.type == "function_call":

                return True

        return False

    def _execute_tool_calls(
        self,
        response,
        tool_executor
    ):

        outputs = []

        for item in response.output:

            if item.type != "function_call":
                continue

            try:

                arguments = json.loads(
                    item.arguments
                )

                result = tool_executor(

                    item.name,

                    **arguments

                )

            except Exception as e:

                result = {

                    "error": str(e)

                }

            outputs.append({

                "type": "function_call_output",

                "call_id": item.call_id,

                "output": json.dumps(
                    result,
                    ensure_ascii=False
                )

            })

        return outputs

    def _extract_text(
        self,
        response
    ):

        try:

            return response.output_text

        except Exception:

            return ""

    def _call_openai(
        self,
        messages,
        tools
    ):

        return self.client.responses.create(

            model=settings.OPENAI_MODEL,

            input=messages,

            tools=tools

        )