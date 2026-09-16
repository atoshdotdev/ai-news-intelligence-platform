from uuid import UUID

from ainews.core.db.models import ChatMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ChatMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message: ChatMessage) -> ChatMessage:
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        return message

    async def get_for_chat(
        self,
        chat_id: UUID,
    ) -> list[ChatMessage]:
        result = await self.session.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at)
        )

        return list(result.scalars().all())
