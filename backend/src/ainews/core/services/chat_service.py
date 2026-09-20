from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import cast
from uuid import UUID

from ainews.core.clients.llm_client import LLMClient
from ainews.core.db.models import Chat, ChatMessage
from ainews.core.db.models.chat_message import ChatMessageRole
from ainews.core.repositories.chat_message_repository import ChatMessageRepository
from ainews.core.repositories.chat_repository import ChatRepository
from ainews.core.schemas.chat_schemas import (
    ChatDetailRead,
    ChatMessageRead,
    ChatSource,
    LLMMessage,
)
from ainews.core.services.rag_service import RAGService
from ainews.core.tools.news_search import NewsSearchArguments
from fastapi import HTTPException, status
from openai.types.chat import (
    ChatCompletionMessageParam,
)


class AgentTextEvent:
    type: str = "text"

    def __init__(self, delta: str):
        self.delta = delta


class AgentSearchEvent:
    def __init__(
        self,
        type: str,
        query: str,
    ):
        self.type = type
        self.query = query


class AgentSourcesEvent:
    type: str = "sources"

    def __init__(self, sources: list[ChatSource]):
        self.sources = sources


AgentEvent = AgentTextEvent | AgentSearchEvent | AgentSourcesEvent


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str,
        retrieval_system_prompt: str,
        final_response_system_prompt: str,
        chat_repository: ChatRepository,
        chat_message_repository: ChatMessageRepository,
        history_max_chars: int,
        max_tool_rounds: int,
    ):
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.retrieval_system_prompt = retrieval_system_prompt
        self.final_response_system_prompt = final_response_system_prompt
        self.chat_repository = chat_repository
        self.chat_message_repository = chat_message_repository
        self.history_max_chars = history_max_chars
        self.max_tool_rounds = max_tool_rounds

    def _build_system_prompt(self, additional_prompt: str) -> str:
        current_datetime = datetime.now(timezone.utc).isoformat()

        base_prompt = self.system_prompt.format(
            current_datetime=current_datetime,
        )

        return f"{base_prompt}\n\n{additional_prompt}"

    def _prepare_final_messages(
        self,
        messages: list[ChatCompletionMessageParam],
    ) -> list[ChatCompletionMessageParam]:
        final_messages = list(messages)

        if not final_messages:
            raise ValueError("No messages provided")

        if final_messages[0]["role"] != "system":
            raise ValueError("First message must be a system message")

        final_messages[0] = {
            "role": "system",
            "content": self._build_system_prompt(
                self.final_response_system_prompt,
            ),
        }

        return final_messages

    async def run_agent(
        self,
        messages: list[LLMMessage],
        rag_service: RAGService,
    ) -> AsyncGenerator[AgentEvent, None]:
        if not messages:
            raise ValueError("No messages provided")

        last_message = messages[-1]

        if last_message.role != "user":
            raise ValueError("Last message must be from the user")

        history = self.trim_history(
            messages=messages[:-1],
            max_chars=self.history_max_chars,
        )

        agent_messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self._build_system_prompt(
                    self.retrieval_system_prompt,
                ),
            },
            *[
                cast(
                    ChatCompletionMessageParam,
                    {
                        "role": message.role,
                        "content": message.content,
                    },
                )
                for message in history
            ],
            {
                "role": "user",
                "content": last_message.content,
            },
        ]

        seen_source_ids: set[str] = set()

        for _ in range(self.max_tool_rounds):
            text_content = ""
            tool_calls: dict[int, dict[str, str]] = {}

            async for chunk in self.llm_client.agent_stream(
                messages=agent_messages,
            ):
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                delta = choice.delta

                if delta.content:
                    text_content += delta.content
                    yield AgentTextEvent(
                        delta=delta.content,
                    )

                if not delta.tool_calls:
                    continue

                for tool_call in delta.tool_calls:
                    index = tool_call.index

                    if index not in tool_calls:
                        tool_calls[index] = {
                            "id": "",
                            "name": "",
                            "arguments": "",
                        }

                    accumulated = tool_calls[index]

                    if tool_call.id:
                        accumulated["id"] += tool_call.id

                    if tool_call.function:
                        if tool_call.function.name:
                            accumulated["name"] += tool_call.function.name

                        if tool_call.function.arguments:
                            accumulated["arguments"] += tool_call.function.arguments

            if not tool_calls:
                return

            function_tool_calls: list[dict[str, str]] = []

            for tool_call in tool_calls.values():
                if not tool_call["id"] or not tool_call["name"]:
                    continue

                function_tool_calls.append(tool_call)

            if not function_tool_calls:
                return

            assistant_tool_calls = [
                {
                    "id": tool_call["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                    },
                }
                for tool_call in function_tool_calls
            ]

            agent_messages.append(
                cast(
                    ChatCompletionMessageParam,
                    {
                        "role": "assistant",
                        "content": text_content or None,
                        "tool_calls": assistant_tool_calls,
                    },
                )
            )

            for tool_call in function_tool_calls:
                tool_call_id = tool_call["id"]
                tool_name = tool_call["name"]

                if tool_name != "search_news":
                    agent_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": f"Unknown tool: {tool_name}",
                            },
                        )
                    )
                    continue

                try:
                    arguments = NewsSearchArguments.model_validate_json(
                        tool_call["arguments"],
                    )
                except Exception:
                    agent_messages.append(
                        cast(
                            ChatCompletionMessageParam,
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": (
                                    "The search request was invalid. "
                                    "Try formulating a different search query."
                                ),
                            },
                        )
                    )
                    continue

                yield AgentSearchEvent(
                    type="search-start",
                    query=arguments.query,
                )

                try:
                    chunks = await rag_service.retrieve(arguments.query)
                    context = rag_service.build_context(chunks)

                    retrieved_sources: list[ChatSource] = []

                    for source in rag_service.build_sources(chunks):
                        if source.source_id in seen_source_ids:
                            continue

                        seen_source_ids.add(source.source_id)
                        retrieved_sources.append(source)

                    if retrieved_sources:
                        yield AgentSourcesEvent(
                            sources=retrieved_sources,
                        )

                    tool_content = context if context else "No relevant news was found."

                except Exception:
                    tool_content = (
                        "The news search could not be completed. "
                        "Try a different search query if necessary."
                    )

                agent_messages.append(
                    cast(
                        ChatCompletionMessageParam,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_content,
                        },
                    )
                )

                yield AgentSearchEvent(
                    type="search-end",
                    query=arguments.query,
                )

        final_messages = self._prepare_final_messages(agent_messages)

        async for token in self.llm_client.chat_stream(
            messages=final_messages,
        ):
            yield AgentTextEvent(delta=token)

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

        return "\n".join(
            user_messages[-max_user_messages:],
        )

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
            chat_id=chat_id,
            user_id=user_id,
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
            chat_id=chat_id,
            user_id=user_id,
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
            chat_id=chat_id,
            user_id=user_id,
        )

        chat.pinned = not chat.pinned

        return await self.chat_repository.update(chat)

    async def update_chat(self, chat: Chat) -> Chat:
        return await self.chat_repository.update(chat)

    async def delete_chat(
        self,
        chat_id: UUID,
        user_id: UUID,
    ) -> None:
        chat = await self.get_chat_entity(
            chat_id=chat_id,
            user_id=user_id,
        )

        await self.chat_repository.delete(chat)
