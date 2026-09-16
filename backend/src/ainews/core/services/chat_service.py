from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import UUID

from ainews.core.clients.llm_client import LLMClient
from ainews.core.db.models import Chat, ChatMessage
from ainews.core.db.models.chat_message import ChatMessageRole
from ainews.core.repositories.chat_message_repository import ChatMessageRepository
from ainews.core.repositories.chat_repository import ChatRepository
from ainews.core.schemas.chat_schemas import (
    ChatDetailRead,
    ChatMessageRead,
    LLMMessage,
)
from fastapi import HTTPException, status


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        direct_system_prompt: str,
        user_prompt: str,
        chat_repository: ChatRepository,
        chat_message_repository: ChatMessageRepository,
        history_max_chars: int,
    ):
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.direct_system_prompt = direct_system_prompt
        self.user_prompt = user_prompt
        self.chat_repository = chat_repository
        self.chat_message_repository = chat_message_repository
        self.history_max_chars = history_max_chars

    async def stream_chat(
        self,
        messages: list[LLMMessage],
        context: str,
        use_rag: bool,
    ) -> AsyncGenerator[str, None]:
        if not messages:
            raise ValueError("No messages provided")

        last_message = messages[-1]

        if last_message.role != "user":
            raise ValueError("Last message must be from the user")

        if use_rag:
            system_prompt = self.system_prompt.format(
                current_datetime=datetime.now(timezone.utc).isoformat(),
            )
        else:
            system_prompt = self.direct_system_prompt

        history = self.trim_history(
            messages=messages[:-1],
            max_chars=self.history_max_chars,
        )

        final_messages: list[LLMMessage] = [
            LLMMessage(
                role="system",
                content=system_prompt,
            ),
            *history,
        ]

        if use_rag:
            final_user_message = self.user_prompt.format(
                context=context,
                question=last_message.content,
            )
        else:
            final_user_message = last_message.content

        final_messages.append(
            LLMMessage(
                role="user",
                content=final_user_message,
            )
        )

        async for token in self.llm_client.chat_stream(final_messages):
            yield token

    def trim_history(
        self,
        messages: list[LLMMessage],
        max_chars: int,
    ) -> list[LLMMessage]:
        selected: list[LLMMessage] = []
        current_chars = 0

        for message in reversed(messages):
            message_chars = len(message.content)

            if selected and current_chars + message_chars > max_chars:
                break

            selected.append(message)
            current_chars += message_chars

        return list(reversed(selected))

    async def generate_title(
        self,
        message: str,
    ) -> str:
        return await self.llm_client.generate_title(message)

    def build_retrieval_query(
        self,
        messages: list[LLMMessage],
        max_user_messages: int = 2,
    ) -> str:
        user_messages = [
            message.content for message in messages if message.role == "user"
        ]

        return "\n".join(user_messages[-max_user_messages:])

    async def create_chat(
        self,
        user_id: UUID,
        title: str,
    ) -> Chat:
        chat = Chat(
            user_id=user_id,
            title=title,
        )

        return await self.chat_repository.create(chat)

    async def get_chat_entity(
        self,
        chat_id: UUID,
        user_id: UUID,
    ) -> Chat:
        chat = await self.chat_repository.get_by_id(
            chat_id,
            user_id,
        )

        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return chat

    async def save_message(
        self,
        chat_id: UUID,
        role: ChatMessageRole,
        content: str,
    ) -> ChatMessage:
        message = ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content,
        )

        return await self.chat_message_repository.create(message)

    async def get_chat(
        self,
        chat_id: UUID,
        user_id: UUID,
    ) -> ChatDetailRead:
        chat = await self.get_chat_entity(
            chat_id,
            user_id,
        )

        messages = await self.chat_message_repository.get_for_chat(chat.id)

        return ChatDetailRead(
            id=chat.id,
            title=chat.title,
            pinned=chat.pinned,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            messages=[ChatMessageRead.model_validate(message) for message in messages],
        )

    async def get_user_chats(
        self,
        user_id: UUID,
    ) -> list[Chat]:
        return await self.chat_repository.get_all_for_user(user_id)

    async def toggle_pin(
        self,
        chat_id: UUID,
        user_id: UUID,
    ) -> Chat:
        chat = await self.get_chat_entity(
            chat_id,
            user_id,
        )

        chat.pinned = not chat.pinned

        return await self.chat_repository.update(chat)

    async def update_chat(
        self,
        chat: Chat,
    ) -> Chat:
        return await self.chat_repository.update(chat)

    async def delete_chat(
        self,
        chat_id: UUID,
        user_id: UUID,
    ) -> None:
        chat = await self.get_chat_entity(
            chat_id,
            user_id,
        )

        await self.chat_repository.delete(chat)
