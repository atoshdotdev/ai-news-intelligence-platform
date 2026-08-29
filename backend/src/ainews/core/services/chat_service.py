from ainews.core.clients.llm_client import LLMClient


class ChatService:
    def __init__(self, llm_client: LLMClient, user_prompt: str):
        self.llm_client = llm_client
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

        async for token in self.llm_client.chat_stream(user_prompt=user_prompt):
            yield token
