from uuid import UUID

from ainews.core.db.models import Chat
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, chat: Chat) -> Chat:
        self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)

        return chat

    async def get_by_id(
        self,
        chat_id: UUID,
        user_id: UUID,
    ) -> Chat | None:
        result = await self.session.execute(
            select(Chat).where(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all_for_user(
        self,
        user_id: UUID,
    ) -> list[Chat]:
        result = await self.session.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(
                Chat.pinned.desc(),
                Chat.updated_at.desc(),
            )
        )

        return list(result.scalars().all())

    async def update(self, chat: Chat) -> Chat:
        await self.session.commit()
        await self.session.refresh(chat)

        return chat

    async def delete(self, chat: Chat) -> None:
        await self.session.delete(chat)
        await self.session.commit()
