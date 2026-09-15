from fastapi import APIRouter, Request

from ainews.core.schemas.category_schemas import (
    CategoriesResponse,
    CategoryRead,
)

router = APIRouter()


@router.get(
    "/",
    response_model=CategoriesResponse,
)
async def get_categories(
    request: Request,
) -> CategoriesResponse:
    categories = request.app.state.config.classification.categories

    return CategoriesResponse(
        categories=[
            CategoryRead(
                id=category.id,
                name=category.name,
            )
            for category in categories
        ]
    )
