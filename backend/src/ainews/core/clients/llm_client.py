from collections.abc import AsyncGenerator

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionChunk,
    ChatCompletionMessageParam,
)

from ainews.core.config.config import Config
from ainews.core.tools.news_search import (
    NEWS_SEARCH_TOOL,
)


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

    async def agent_stream(
        self,
        messages: list[ChatCompletionMessageParam],
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        stream = await self.client.chat.completions.create(
            model=self.config.chat.model,
            messages=messages,
            temperature=self.config.chat.temperature,
            max_completion_tokens=self.config.chat.max_tokens,
            stream=True,
            tools=[NEWS_SEARCH_TOOL],
            reasoning_effort="high",
            extra_body={
                "options": {
                    "num_ctx": self.config.chat.context_size,
                },
            },
        )

        async for chunk in stream:
            yield chunk

    async def chat_stream(
        self,
        messages: list[ChatCompletionMessageParam],
    ) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.config.chat.model,
            messages=messages,
            temperature=self.config.chat.temperature,
            max_completion_tokens=self.config.chat.max_tokens,
            stream=True,
            reasoning_effort="high",
            extra_body={
                "options": {
                    "num_ctx": self.config.chat.context_size,
                },
            },
        )

        async for chunk in stream:
            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                yield content

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
