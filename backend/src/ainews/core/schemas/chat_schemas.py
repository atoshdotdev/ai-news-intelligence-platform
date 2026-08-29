from typing import Literal

from pydantic import BaseModel


class ChatMessagePart(BaseModel):
    type: str
    text: str | None = None


class ChatMessage(BaseModel):
    id: str
    role: Literal["user", "assistant", "system"]
    parts: list[ChatMessagePart]

    @property
    def text(self) -> str:
        return "".join(
            part.text for part in self.parts if part.type == "text" and part.text
        )


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
