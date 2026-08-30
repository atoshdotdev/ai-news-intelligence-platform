from collections.abc import AsyncGenerator

from ainews.core.clients.llm_client import LLMClient
from ainews.core.schemas.chat_schemas import LLMMessage


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        user_prompt: str,
    ):
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    async def stream_chat(
        self,
        messages: list[LLMMessage],
        context: str,
    ) -> AsyncGenerator[str, None]:

        if not messages:
            raise ValueError("No messages provided")

        last_message = messages[-1]

        if last_message.role != "user":
            raise ValueError("Last message must be from the user")

        final_messages: list[LLMMessage] = [
            LLMMessage(
                role="system",
                content=self.system_prompt,
            ),
            *messages[:-1],
        ]

        final_user_message = self.user_prompt.format(
            context=context,
            question=last_message.content,
        )

        final_messages.append(
            LLMMessage(
                role="user",
                content=final_user_message,
            )
        )

        async for token in self.llm_client.chat_stream(final_messages):
            yield token
