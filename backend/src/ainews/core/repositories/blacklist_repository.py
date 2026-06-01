from uuid import UUID

from ainews.core.db.models import SourceBlacklist
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


class BlacklistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_source(self, source_id: UUID):
        stmt = select(SourceBlacklist).where(SourceBlacklist.source_id == source_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_entry(self, source_id: UUID, fragment: str):
        entry = SourceBlacklist(source_id=source_id, url_fragment=fragment)
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def remove_entry(self, entry_id: UUID):
        stmt = delete(SourceBlacklist).where(SourceBlacklist.id == entry_id)
        await self.session.execute(stmt)
        await self.session.commit()
