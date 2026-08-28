from ainews.core.clients.ollama_client import OllamaClient


class ChatService:
    def __init__(self, ollama: OllamaClient, user_prompt: str):
        self.ollama = ollama
        self.user_prompt = user_prompt

    async def stream_chat(
        self,
        question: str,
        context: str,
    ):
        user_prompt = self.user_prompt.format(
            context=context,
            question=question,
        )

        async for token in self.ollama.chat_stream(user_prompt=user_prompt):
            yield token
