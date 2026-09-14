from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ainews.core.schemas.pagination_schemas import PaginationMetadata


class SourceBlacklistBase(BaseModel):
    url_fragment: str


class SourceBlacklistCreate(SourceBlacklistBase):
    pass


class SourceBlacklistRead(SourceBlacklistBase):
    id: UUID
    source_id: UUID
    model_config = ConfigDict(from_attributes=True)


class SourceBase(BaseModel):
    name: str
    url: str
    selector: str | None = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class PaginatedSourcesResponse(BaseModel):
    data: list[SourceRead]
    metadata: PaginationMetadata
