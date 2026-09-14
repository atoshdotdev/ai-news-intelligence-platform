from uuid import UUID

from ainews.core.repositories.event_repository import EventRepository
from ainews.core.schemas.event_schemas import (
    EventFilters,
    EventRead,
    PaginatedEventsResponse,
)
from ainews.core.schemas.pagination_schemas import (
    PaginationMetadata,
    PaginationParams,
)


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    async def get_all_events(
        self,
        pagination_params: PaginationParams,
        filters: EventFilters,
    ) -> PaginatedEventsResponse:
        offset, limit = pagination_params.to_sqlalchemy_pagination()

        rows, total_items = await self.repository.get_all(
            filters=filters,
            offset=offset,
            limit=limit,
        )

        items = [
            EventRead(
                id=row.id,
                title=row.title,
                summary=row.summary,
                category=row.category,
                image_url=row.image_url,
                last_published_at=row.last_published_at,
                article_count=row.article_count,
            )
            for row in rows
        ]

        pagination = PaginationMetadata.get_metadata(
            current_page=pagination_params.page,
            page_size=pagination_params.size,
            total_items=total_items,
        )

        return PaginatedEventsResponse(
            items=items,
            pagination=pagination,
        )

    async def get_event_by_id(self, event_id: UUID):
        return await self.repository.get_by_id(event_id)
