from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from ainews.api.dependencies.auth import get_current_user
from ainews.core.db.database import get_session
from ainews.core.schemas.source_schemas import (
    SourceBlacklistCreate,
    SourceBlacklistRead,
)
from ainews.core.services.blacklist_service import BlacklistService

router = APIRouter(dependencies=[Depends(get_current_user)])


def get_blacklist_service(session=Depends(get_session)) -> BlacklistService:
    return BlacklistService(session)


@router.get("/{source_id}/blacklist", response_model=list[SourceBlacklistRead])
async def get_blacklist(
    source_id: UUID, service: BlacklistService = Depends(get_blacklist_service)
):
    return await service.get_blacklist(source_id)


@router.post("/{source_id}/blacklist", response_model=SourceBlacklistRead)
async def add_blacklist(
    source_id: UUID,
    data: SourceBlacklistCreate,
    service: BlacklistService = Depends(get_blacklist_service),
):
    return await service.add_to_blacklist(source_id, data.url_fragment)


@router.delete(
    "/{source_id}/blacklist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_blacklist(
    entry_id: UUID, service: BlacklistService = Depends(get_blacklist_service)
):
    await service.remove_from_blacklist(entry_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
