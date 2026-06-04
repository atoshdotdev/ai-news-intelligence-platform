from collections.abc import Sequence
from uuid import UUID

from ainews.core.db.models import Article
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, articles: list[Article]) -> list[Article]:
        """Bulk inserts newly discovered articles."""
        self.session.add_all(articles)
        await self.session.commit()
        return articles

    async def get_existing_hashes(
        self,
        hashes: list[str],
    ) -> set[str]:
        """
        Returns hashes already stored in DB.
        """

        if not hashes:
            return set()

        stmt = select(Article.url_hash).where(Article.url_hash.in_(hashes))

        result = await self.session.execute(stmt)

        return set(result.scalars().all())

    async def get_pending_articles(self, limit: int = 50) -> Sequence[Article]:
        """Fetches articles that have not yet been processed for embeddings."""
        result = await self.session.execute(
            select(Article).where(Article.embedding.is_(None)).limit(limit)
        )

        return result.scalars().all()

    async def save_embeddings_batch(self, items: list[tuple[UUID, Sequence[float]]]):
        """Saves a batch of embeddings for the given article IDs."""
        await self.session.execute(
            update(Article),
            [
                {"id": article_id, "embedding": embedding}
                for article_id, embedding in items
            ],
        )

        await self.session.commit()
