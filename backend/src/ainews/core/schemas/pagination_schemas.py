from math import ceil
from typing import Self

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number for pagination")
    size: int = Field(10, ge=1, le=51, description="Number of items per page")

    def to_sqlalchemy_pagination(self):
        offset = (self.page - 1) * self.size
        return offset, self.size


class PaginationMetadata(BaseModel):
    total_items: int = Field(
        ..., description="Total number of items matching the query."
    )
    total_pages: int = Field(..., description="Total number of pages available.")
    current_page: int = Field(..., description="The current page number.")
    page_size: int = Field(..., description="Number of items per page.")
    has_next: bool = Field(..., description="True if there is a next page.")
    has_prev: bool = Field(..., description="True if there is a previous page.")

    @classmethod
    def get_metadata(cls, current_page: int, page_size: int, total_items: int) -> Self:
        total_pages = ceil(total_items / page_size) if page_size > 0 else 0
        if total_items == 0:
            total_pages = 0

        has_next = (current_page * page_size) < total_items
        has_prev = current_page > 1

        return cls(
            total_items=total_items,
            total_pages=total_pages,
            current_page=current_page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev,
        )
