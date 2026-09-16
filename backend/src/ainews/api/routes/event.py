from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ainews.api.dependencies.auth import get_current_user
from ainews.core.db.database import get_session
from ainews.core.repositories.event_repository import EventRepository
from ainews.core.schemas.event_schemas import (
    EventDetailRead,
    EventFilters,
    PaginatedEventsResponse,
)
from ainews.core.schemas.pagination_schemas import PaginationParams
from ainews.core.services.event_service import EventService

router = APIRouter(dependencies=[Depends(get_current_user)])


def get_event_service(
    session: AsyncSession = Depends(get_session),
) -> EventService:
    repository = EventRepository(session)
    return EventService(repository)


@router.get("/", response_model=PaginatedEventsResponse)
async def read_events(
    pagination_params: PaginationParams = Depends(),
    filters: EventFilters = Depends(),
    service: EventService = Depends(get_event_service),
):
    return await service.get_all_events(
        pagination_params,
        filters,
    )


@router.get("/{event_id}", response_model=EventDetailRead)
async def read_event(
    event_id: UUID,
    service: EventService = Depends(get_event_service),
):
    event = await service.get_event_by_id(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event
