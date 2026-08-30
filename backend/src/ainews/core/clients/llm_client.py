from collections.abc import AsyncGenerator
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from ainews.core.config.config import Config
from ainews.core.schemas.chat_schemas import LLMMessage


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
            extra_body={"options": {"num_ctx": self.config.chat.context_size}},
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content

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
