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


class EventArticleRead(BaseModel):
    id: UUID
    title: str
    url: str
    source_name: str
    published_at: datetime | None
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)


class EventEntityRead(BaseModel):
    label: str
    value: str


class EventDetailRead(BaseModel):
    id: UUID
    title: str | None
    summary: str | None
    category: str | None
    image_url: str | None
    entities: list[EventEntityRead] | None
    last_published_at: datetime | None
    articles: list[EventArticleRead]

    model_config = ConfigDict(from_attributes=True)


class EventFilters(BaseModel):
    category: str | None = None
    search: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None


class PaginatedEventsResponse(BaseModel):
    items: list[EventRead]
    pagination: PaginationMetadata
