from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from ainews.core.db.models import Source
from ainews.core.schemas.source_schemas import SourceCreate, SourceUpdate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class SourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_all(self) -> int:
        stmt = select(func.count(Source.id)).where(Source.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_active_sources(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        include_blacklisted: bool = False,
    ) -> Sequence[Source]:
        """Fetches active sources with optional pagination. If offset and limit are provided, applies pagination to the query."""
        stmt = select(Source).where(Source.deleted_at.is_(None)).order_by(Source.name)

        if include_blacklisted:
            stmt = stmt.options(selectinload(Source.blacklist_entries))

        if offset is not None and limit is not None:
            stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: SourceCreate) -> Source:
        """Creates a new source record in the database."""
        db_source = Source(**data.model_dump())
        self.session.add(db_source)
        await self.session.commit()
        await self.session.refresh(db_source)
        return db_source

    async def update(self, source_id: UUID, data: SourceUpdate) -> Source | None:
        """Updates an existing source record with new data."""
        stmt = select(Source).where(Source.id == source_id)
        result = await self.session.execute(stmt)
        source = result.scalar_one_or_none()

        if source:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(source, key, value)
            await self.session.commit()
            await self.session.refresh(source)
        return source

    async def delete(self, source_id: UUID) -> bool:
        """Soft-deletes a source by setting its deleted_at timestamp."""
        stmt = select(Source).where(Source.id == source_id)
        result = await self.session.execute(stmt)
        source = result.scalar_one_or_none()

        if source:
            source.deleted_at = datetime.now(timezone.utc)
            await self.session.commit()
            return True
        return False
