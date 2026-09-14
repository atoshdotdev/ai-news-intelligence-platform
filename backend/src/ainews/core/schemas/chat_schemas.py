from typing import Literal

from pydantic import BaseModel


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
    id: str
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
