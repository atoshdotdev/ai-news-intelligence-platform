from ollama import AsyncClient

from ainews.core.config.config import Config
from ainews.core.utils.logger import logger


class OllamaClient:
    def __init__(self, base_url: str, config: Config):
        self.client = AsyncClient(host=base_url)
        self.config = config

    async def chat_stream(
        self,
        messages: list,
        model: str | None = None,
    ):
        stream = await self.client.chat(
            model=model or self.config.chat.model,
            messages=messages,
            options={
                "temperature": self.config.chat.temperature,
                "top_p": self.config.chat.top_p,
                "num_predict": self.config.chat.max_tokens,
            },
            stream=True,
        )

        async for chunk in stream:
            yield chunk["message"]["content"]

    async def summarize(
        self,
        messages: list,
    ) -> str:
        response = await self.client.chat(
            model=self.config.summarization.model,
            messages=messages,
            options={
                "temperature": self.config.summarization.temperature,
                "top_p": self.config.summarization.top_p,
                "num_predict": self.config.summarization.max_tokens,
                "num_ctx": self.config.summarization.context_size,
            },
            stream=False,
            think=False,
        )

        logger.info(
            "Ollama summarization response: %r",
            response,
        )

        content = response["message"]["content"]

        logger.info(
            "Ollama summarization content length: %d",
            len(content) if content else 0,
        )

        return content.strip() if content else ""
