from collections.abc import Sequence
from datetime import datetime, timedelta
from uuid import UUID

from ainews.core.db.models import Article, Event
from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def get_candidate_events(
        self,
        reference_time: datetime,
        max_event_age_days: int,
    ) -> list[Event]:
        """
        Returns events that existed by the time the article was published
        and have been active within the previous max_event_age_days.
        """

        cutoff = reference_time - timedelta(
            days=max_event_age_days,
        )

        stmt = (
            select(Event)
            .where(
                Event.embedding.is_not(None),
                Event.last_published_at.is_not(None),
                Event.last_published_at >= cutoff,
                Event.last_published_at <= reference_time,
            )
            .order_by(Event.last_published_at.desc())
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def create_from_article(
        self,
        article: Article,
    ) -> Event:
        """
        Creates a new event using the article as its initial
        representative.
        """

        event = Event(
            title=article.title,
            embedding=article.embedding,
            entities=article.entities,
            last_published_at=article.published_at,
        )

        self.session.add(event)

        await self.session.flush()

        await self.add_article(
            event_id=event.id,
            article_id=article.id,
        )

        return event

    async def add_article(
        self,
        event_id: UUID,
        article_id: UUID,
    ) -> None:
        """
        Assigns an article to an event.
        """

        stmt = update(Article).where(Article.id == article_id).values(event_id=event_id)

        await self.session.execute(stmt)

    async def update_event(
        self,
        event_id: UUID,
        *,
        title: str | None = None,
        summary: str | None = None,
        embedding: Sequence[float] | None = None,
        entities: list[dict] | None = None,
        last_published_at: datetime | None = None,
        summary_last_published_at: datetime | None = None,
    ) -> None:
        values: dict[str, object] = {}

        if title is not None:
            values["title"] = title

        if summary is not None:
            values["summary"] = summary

        if embedding is not None:
            values["embedding"] = list(embedding)

        if entities is not None:
            values["entities"] = entities

        if last_published_at is not None:
            values["last_published_at"] = last_published_at

        if summary_last_published_at is not None:
            values["summary_last_published_at"] = summary_last_published_at

        if not values:
            return

        values["updated_at"] = func.now()

        stmt = update(Event).where(Event.id == event_id).values(**values)

        await self.session.execute(stmt)

    async def get_by_id(
        self,
        event_id: UUID,
    ) -> Event | None:
        """
        Gets an event by ID.
        """

        stmt = select(Event).where(
            Event.id == event_id,
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_articles(
        self,
        event_id: UUID,
    ) -> list[Article]:
        """
        Gets all articles belonging to an event.

        Articles are ordered chronologically by their published date,
        with creation time used as a fallback.
        """

        stmt = (
            select(Article)
            .where(
                Article.event_id == event_id,
            )
            .order_by(
                Article.published_at.asc(),
                Article.scraped_at.asc(),
            )
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def get_recent_events(
        self,
        updated_after: datetime,
        limit: int,
    ) -> list[Event]:
        """
        Gets recently updated events.
        """

        stmt = (
            select(Event)
            .where(
                Event.updated_at >= updated_after,
            )
            .order_by(
                Event.updated_at.desc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def get_events_pending_summary(
        self, limit: int, refresh_hours: int
    ) -> list[Event]:
        refresh_interval = timedelta(hours=refresh_hours)

        stmt = (
            select(Event)
            .where(
                or_(
                    Event.summary.is_(None),
                    Event.last_published_at - Event.summary_last_published_at
                    >= refresh_interval,
                ),
            )
            .order_by(
                Event.last_published_at.asc(),
                Event.created_at.asc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
