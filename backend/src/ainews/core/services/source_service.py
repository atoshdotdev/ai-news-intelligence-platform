from uuid import UUID

from ainews.core.repositories.source_repository import SourceRepository
from ainews.core.schemas.pagination_schemas import PaginationMetadata, PaginationParams
from ainews.core.schemas.source_schemas import (
    PaginatedSourcesResponse,
    SourceCreate,
    SourceRead,
    SourceUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession


class SourceService:
    def __init__(self, session: AsyncSession):
        self.repo = SourceRepository(session)

    async def get_all_sources(
        self, pagination: PaginationParams
    ) -> PaginatedSourcesResponse:
        offset, limit = pagination.to_sqlalchemy_pagination()

        items = await self.repo.get_active_sources(offset, limit)
        total_items = await self.repo.count_all()

        sources = [SourceRead.model_validate(item) for item in items]

        metadata = PaginationMetadata.get_metadata(
            current_page=pagination.page,
            page_size=pagination.size,
            total_items=total_items,
        )

        return PaginatedSourcesResponse(data=sources, metadata=metadata)

    async def create_source(self, source_data: SourceCreate):
        return await self.repo.create(source_data)

    async def update_source(self, source_id: UUID, data: SourceUpdate):
        return await self.repo.update(source_id, data)

    async def delete_source(self, source_id: UUID):
        return await self.repo.delete(source_id)
