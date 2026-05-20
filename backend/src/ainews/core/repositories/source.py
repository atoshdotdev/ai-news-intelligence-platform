from collections.abc import Sequence

from ainews.core.db.models import Source
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_sources(self) -> Sequence[Source]:
        """Fetches all sources marked for active crawling."""
        stmt = select(Source).where(Source.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalars().all()
