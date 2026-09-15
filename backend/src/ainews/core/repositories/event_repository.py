from collections.abc import Sequence
from datetime import datetime, timedelta
from uuid import UUID

from ainews.core.db.models import Article, Event
from ainews.core.db.models.source import Source
from ainews.core.schemas.event_schemas import (
    EventArticleRead,
    EventDetailRead,
    EventEntityRead,
    EventFilters,
    EventListItem,
)
from sqlalchemy import ColumnElement, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def get_all(
        self,
        filters: EventFilters,
        offset: int,
        limit: int,
    ) -> tuple[list[EventListItem], int]:
        conditions: list[ColumnElement[bool]] = [
            Event.summary.is_not(None),
            Event.category.is_not(None),
        ]

        if filters.category:
            conditions.append(Event.category == filters.category)

        if filters.search:
            search = f"%{filters.search}%"

            conditions.append(
                or_(
                    Event.title.ilike(search),
                    Event.summary.ilike(search),
                )
            )

        if filters.from_date:
            conditions.append(Event.last_published_at >= filters.from_date)

        if filters.to_date:
            conditions.append(Event.last_published_at <= filters.to_date)

        count_query = select(func.count(Event.id)).where(*conditions)

        total_items = await self.session.scalar(count_query) or 0

        query = (
            select(
                Event.id,
                Event.title,
                Event.summary,
                Event.category,
                Event.image_url,
                Event.last_published_at,
                Event.created_at,
                func.count(Article.id).label("article_count"),
            )
            .outerjoin(
                Article,
                Article.event_id == Event.id,
            )
            .where(*conditions)
            .group_by(Event.id)
            .order_by(
                Event.last_published_at.desc().nullslast(),
                Event.created_at.desc(),
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)

        rows = [
            EventListItem(
                id=row.id,
                title=row.title,
                summary=row.summary,
                category=row.category,
                image_url=row.image_url,
                last_published_at=row.last_published_at,
                article_count=row.article_count,
            )
            for row in result
        ]

        return rows, total_items

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
            image_url=article.image_url,
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
        image_url: str | None = None,
        last_published_at: datetime | None = None,
        summary_last_published_at: datetime | None = None,
        category: str | None = None,
    ) -> None:
        values: dict[str, object] = {}

        if title is not None:
            values["title"] = title

        if summary is not None:
            values["summary"] = summary

        if category is not None:
            values["category"] = category

        if embedding is not None:
            values["embedding"] = list(embedding)

        if entities is not None:
            values["entities"] = entities

        if image_url is not None:
            values["image_url"] = image_url

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
    ) -> EventDetailRead | None:
        event_query = select(
            Event.id,
            Event.title,
            Event.summary,
            Event.category,
            Event.image_url,
            Event.entities,
            Event.last_published_at,
        ).where(
            Event.id == event_id,
            Event.summary.is_not(None),
            Event.category.is_not(None),
        )

        event_result = await self.session.execute(event_query)
        event = event_result.one_or_none()

        if event is None:
            return None

        articles_query = (
            select(
                Article.id,
                Article.title,
                Article.url,
                Article.published_at,
                Article.image_url,
                Source.name.label("source_name"),
            )
            .join(
                Source,
                Source.id == Article.source_id,
            )
            .where(Article.event_id == event_id)
            .order_by(
                Article.published_at.desc().nullslast(),
            )
        )

        articles_result = await self.session.execute(articles_query)

        articles = [
            EventArticleRead(
                id=row.id,
                title=row.title,
                url=row.url,
                source_name=row.source_name,
                published_at=row.published_at,
                image_url=row.image_url,
            )
            for row in articles_result
        ]

        entities = [
            EventEntityRead(
                label=entity["label"],
                value=entity["text"],
            )
            for entity in event.entities or []
        ]

        return EventDetailRead(
            id=event.id,
            title=event.title,
            summary=event.summary,
            category=event.category,
            image_url=event.image_url,
            entities=entities,
            last_published_at=event.last_published_at,
            articles=articles,
        )

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

    async def get_events_pending_classification(
        self,
        limit: int,
    ) -> list[Event]:
        stmt = (
            select(Event)
            .where(
                Event.summary.is_not(None),
                Event.category.is_(None),
            )
            .order_by(
                Event.updated_at.asc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
