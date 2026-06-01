from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ainews.core.db.database import get_session
from ainews.core.schemas.pagination_schemas import PaginationParams
from ainews.core.schemas.source_schemas import (
    PaginatedSourcesResponse,
    SourceCreate,
    SourceRead,
    SourceUpdate,
)
from ainews.core.services.source_service import SourceService

router = APIRouter()


def get_source_service(session: AsyncSession = Depends(get_session)) -> SourceService:
    return SourceService(session)


@router.get("/", response_model=PaginatedSourcesResponse)
async def read_sources(
    pagination_params: PaginationParams = Depends(),
    service: SourceService = Depends(get_source_service),
):
    return await service.get_all_sources(pagination_params)


@router.post("/", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: SourceCreate, service: SourceService = Depends(get_source_service)
):
    return await service.create_source(source_data)


@router.get("/{source_id}", response_model=SourceRead)
async def read_source(
    source_id: UUID, service: SourceService = Depends(get_source_service)
):
    source = await service.get_source_by_id(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: UUID,
    data: SourceUpdate,
    service: SourceService = Depends(get_source_service),
):
    source = await service.update_source(source_id, data)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID, service: SourceService = Depends(get_source_service)
):
    success = await service.delete_source(source_id)
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")
    return None
