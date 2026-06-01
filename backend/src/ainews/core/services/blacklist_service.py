from uuid import UUID

from ainews.core.repositories.blacklist_repository import BlacklistRepository
from sqlalchemy.ext.asyncio import AsyncSession


class BlacklistService:
    def __init__(self, session: AsyncSession):
        self.repo = BlacklistRepository(session)

    async def get_blacklist(self, source_id: UUID):
        return await self.repo.get_by_source(source_id)

    async def add_to_blacklist(self, source_id: UUID, fragment: str):
        return await self.repo.add_entry(source_id, fragment)

    async def remove_from_blacklist(self, entry_id: UUID):
        await self.repo.remove_entry(entry_id)
