from collections.abc import Sequence

from ollama import AsyncClient

from ainews.core.config.ai_models import AIConfig


class OllamaClient:
    def __init__(self, base_url: str, config: AIConfig):
        self.client = AsyncClient(host=base_url)
        self.config = config

    async def embed(
        self, input: str | list[str], model: str | None = None
    ) -> Sequence[Sequence[float]]:
        response = await self.client.embed(
            model=model or self.config.embedding.model,
            input=input,
            dimensions=self.config.embedding.dimensions,
        )

        return response.embeddings

    async def chat(self, messages: list, model: str | None = None):
        response = await self.client.chat(
            model=model or self.config.chat.model,
            messages=messages,
            options={
                "temperature": self.config.chat.temperature,
                "top_p": self.config.chat.top_p,
                "num_predict": self.config.chat.max_tokens,
            },
        )

        return response["message"]["content"]
