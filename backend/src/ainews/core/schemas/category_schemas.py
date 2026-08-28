from pydantic import BaseModel


class CategoryRead(BaseModel):
    id: str
    name: str


class CategoriesResponse(BaseModel):
    categories: list[CategoryRead]
