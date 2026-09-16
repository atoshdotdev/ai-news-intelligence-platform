from collections.abc import AsyncGenerator
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from ainews.core.config.config import Config
from ainews.core.schemas.chat_schemas import LLMMessage
from ainews.core.schemas.rag_schemas import RAGDecision


class LLMClient:
    def __init__(
        self,
        base_url: str,
        config: Config,
    ):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="ollama",
        )
        self.config = config

    async def chat_stream(
        self, messages: list[LLMMessage]
    ) -> AsyncGenerator[str, None]:
        openai_messages = cast(
            list[ChatCompletionMessageParam],
            [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
        )

        stream = await self.client.chat.completions.create(
            model=self.config.chat.model,
            messages=openai_messages,
            temperature=self.config.chat.temperature,
            max_completion_tokens=self.config.chat.max_tokens,
            stream=True,
            reasoning_effort="none",
            extra_body={"options": {"num_ctx": self.config.chat.context_size}},
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            choice = chunk.choices[0]

            if choice.finish_reason == "stop":
                continue

            content = choice.delta.content

            if content:
                yield content

    async def classify_rag(
        self,
        messages: list[LLMMessage],
        system_prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        context_size: int,
    ) -> bool:
        openai_messages = cast(
            list[ChatCompletionMessageParam],
            [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
        )

        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                *openai_messages,
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            stream=False,
            reasoning_effort="none",
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "rag_decision",
                    "strict": True,
                    "schema": RAGDecision.model_json_schema(),
                },
            },
            extra_body={
                "options": {
                    "num_ctx": context_size,
                }
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("RAG decision model returned empty content")

        decision = RAGDecision.model_validate_json(content)

        return decision.requires_rag

    async def generate_title(
        self,
        message: str,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.config.chat.title_model,
            messages=[
                {
                    "role": "system",
                    "content": self.config.chat.title_system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=self.config.chat.title_temperature,
            max_completion_tokens=self.config.chat.title_max_tokens,
            stream=False,
            reasoning_effort="none",
            extra_body={
                "options": {
                    "num_ctx": self.config.chat.title_context_size,
                }
            },
        )

        content = response.choices[0].message.content

        if not content:
            return "New chat"

        return content.strip().strip('"').strip("'")

    async def summarize(
        self,
        prompt: str,
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.config.summarization.model,
            messages=[
                {
                    "role": "system",
                    "content": self.config.summarization.system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=self.config.summarization.temperature,
            max_completion_tokens=self.config.summarization.max_tokens,
            stream=False,
            reasoning_effort="none",
            extra_body={"options": {"num_ctx": self.config.summarization.context_size}},
        )

        content = response.choices[0].message.content

        return content.strip() if content else ""
