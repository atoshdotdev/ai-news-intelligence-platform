from collections.abc import Sequence
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
        """
        Bulk inserts newly discovered articles.
        """
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

    async def get_articles_without_chunks(
        self,
        limit: int = 50,
    ) -> Sequence[Article]:
        """
        Fetches articles that do not have chunks created yet.
        """

        stmt = (
            select(Article)
            .outerjoin(
                ArticleChunk,
                ArticleChunk.article_id == Article.id,
            )
            .where(ArticleChunk.id.is_(None))
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_articles_pending_embedding(
        self,
        limit: int = 50,
    ) -> Sequence[Article]:
        """
        Fetches articles that do not have article-level embeddings.
        Used for event clustering embeddings.
        """

        stmt = select(Article).where(Article.embedding.is_(None)).limit(limit)

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def save_article_embeddings_batch(
        self,
        items: list[tuple[UUID, list[float]]],
    ):
        """
        Saves article-level embeddings.
        """

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

    async def search_similar(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[Article]:
        """
        Searches similar articles using article embeddings.
        Used for event clustering.
        """

        stmt = (
            select(Article)
            .where(Article.embedding.is_not(None))
            .order_by(Article.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
