from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ainews.core.schemas.pagination_schemas import PaginationMetadata


class EventListItem(BaseModel):
    id: UUID
    title: str | None
    summary: str | None
    category: str | None
    image_url: str | None
    last_published_at: datetime | None
    article_count: int


class EventRead(BaseModel):
    id: UUID
    title: str | None
    summary: str | None
    category: str | None
    image_url: str | None
    last_published_at: datetime | None
    article_count: int

    model_config = ConfigDict(from_attributes=True)


class EventFilters(BaseModel):
    category: str | None = None
    search: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None


class PaginatedEventsResponse(BaseModel):
    items: list[EventRead]
    pagination: PaginationMetadata
