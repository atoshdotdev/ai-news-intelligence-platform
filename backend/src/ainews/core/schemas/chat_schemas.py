from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChatMessagePart(BaseModel):
    type: str
    text: str | None = None
    state: str | None = None


class ChatMessage(BaseModel):
    id: str
    role: Literal["system", "user", "assistant"]
    parts: list[ChatMessagePart]

    @property
    def text(self) -> str:
        return "".join(
            part.text for part in self.parts if part.type == "text" and part.text
        )


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    chat_id: UUID | None = None
    messages: list[ChatMessage]
    trigger: str | None = None

    @property
    def last_user_message(self) -> ChatMessage | None:
        for message in reversed(self.messages):
            if message.role == "user" and message.text:
                return message

        return None


class ChatSource(BaseModel):
    source_id: str
    url: str
    title: str


class ChatRead(BaseModel):
    id: UUID
    title: str
    pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageRead(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailRead(ChatRead):
    messages: list[ChatMessageRead]
