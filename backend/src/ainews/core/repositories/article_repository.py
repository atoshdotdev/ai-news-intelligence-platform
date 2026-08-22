from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from ainews.core.db.models import Article, ArticleChunk
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(
        self,
        articles: list[Article],
    ) -> list[Article]:
        self.session.add_all(articles)
        await self.session.commit()

        return articles

    async def get_existing_hashes(
        self,
        hashes: list[str],
    ) -> set[str]:
        if not hashes:
            return set()

        stmt = select(Article.url_hash).where(Article.url_hash.in_(hashes))

        result = await self.session.execute(stmt)

        return set(result.scalars().all())

    async def get_articles_without_chunks(
        self,
        limit: int = 50,
    ) -> Sequence[Article]:
        stmt = (
            select(Article)
            .outerjoin(
                ArticleChunk,
                ArticleChunk.article_id == Article.id,
            )
            .where(ArticleChunk.id.is_(None))
            .order_by(
                Article.published_at.asc().nulls_last(),
                Article.scraped_at.asc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_articles_pending_ner(
        self,
        limit: int,
    ) -> Sequence[Article]:
        """
        Fetches articles that are ready for NER processing.

        An article is ready when:
        - NER has not been completed
        - at least one chunk exists

        The limit represents the number of articles, not chunks.
        """

        has_chunks = (
            select(ArticleChunk.id)
            .where(
                ArticleChunk.article_id == Article.id,
            )
            .exists()
        )

        stmt = (
            select(Article)
            .where(
                Article.ner_processed_at.is_(None),
                has_chunks,
            )
            .order_by(
                Article.published_at.asc().nulls_last(),
                Article.scraped_at.asc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_articles_pending_embedding(
        self,
        limit: int,
    ) -> Sequence[Article]:
        """
        Fetches articles that are ready for embedding but are not
        fully embedded yet.

        An article is ready when:
        - NER has completed
        - at least one chunk exists
        - either the article embedding is missing
        or at least one chunk embedding is missing
        """

        has_chunks = (
            select(ArticleChunk.id)
            .where(
                ArticleChunk.article_id == Article.id,
            )
            .exists()
        )

        has_pending_chunks = (
            select(ArticleChunk.id)
            .where(
                ArticleChunk.article_id == Article.id,
                ArticleChunk.embedding.is_(None),
            )
            .exists()
        )

        stmt = (
            select(Article)
            .where(
                Article.ner_processed_at.is_not(None),
                has_chunks,
                (Article.embedding.is_(None) | has_pending_chunks),
            )
            .order_by(
                Article.published_at.asc().nulls_last(),
                Article.scraped_at.asc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def save_article_embeddings_batch(
        self,
        items: list[tuple[UUID, list[float]]],
    ) -> None:
        """Saves article-level embeddings."""

        if not items:
            return

        await self.session.execute(
            update(Article),
            [
                {
                    "id": article_id,
                    "embedding": embedding,
                }
                for article_id, embedding in items
            ],
        )

        await self.session.commit()

    async def save_article_entities_batch(
        self,
        items: list[tuple[UUID, list[dict[str, Any]]]],
    ) -> None:
        """
        Saves final article-level NER entities and marks
        the articles as NER processed.
        """

        if not items:
            return

        processed_at = datetime.now(timezone.utc)

        await self.session.execute(
            update(Article),
            [
                {
                    "id": article_id,
                    "entities": entities,
                    "ner_processed_at": processed_at,
                }
                for article_id, entities in items
            ],
        )

        await self.session.commit()

    async def search_similar(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[Article]:
        stmt = (
            select(Article)
            .where(Article.embedding.is_not(None))
            .order_by(Article.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def get_articles_pending_clustering(
        self,
        limit: int,
    ) -> Sequence[Article]:
        stmt = (
            select(Article)
            .where(
                Article.embedding.is_not(None),
                Article.event_id.is_(None),
            )
            .order_by(
                Article.published_at.asc().nulls_last(),
                Article.scraped_at.asc(),
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
