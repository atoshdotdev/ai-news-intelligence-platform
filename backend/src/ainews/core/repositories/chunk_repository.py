from collections.abc import Sequence
from uuid import UUID

from ainews.core.db.models import ArticleChunk
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(
        self,
        chunks: list[ArticleChunk],
    ) -> list[ArticleChunk]:
        self.session.add_all(chunks)
        await self.session.commit()

        return chunks

    async def get_by_article_id(
        self,
        article_id: UUID,
    ) -> Sequence[ArticleChunk]:
        result = await self.session.execute(
            select(ArticleChunk)
            .where(ArticleChunk.article_id == article_id)
            .order_by(ArticleChunk.chunk_index)
        )

        return result.scalars().all()

    async def get_by_article_ids(
        self,
        article_ids: list[UUID],
    ) -> Sequence[ArticleChunk]:
        if not article_ids:
            return []

        result = await self.session.execute(
            select(ArticleChunk)
            .where(ArticleChunk.article_id.in_(article_ids))
            .order_by(
                ArticleChunk.article_id,
                ArticleChunk.chunk_index,
            )
        )

        return result.scalars().all()

    async def get_pending_embedding_chunks_for_articles(
        self,
        article_ids: list[UUID],
    ) -> Sequence[ArticleChunk]:
        """
        Returns chunks without embeddings belonging to the
        specified articles.

        This allows the worker to recover if article embeddings
        were committed before chunk embeddings.
        """

        if not article_ids:
            return []

        result = await self.session.execute(
            select(ArticleChunk)
            .where(
                ArticleChunk.article_id.in_(article_ids),
                ArticleChunk.embedding.is_(None),
            )
            .order_by(
                ArticleChunk.article_id,
                ArticleChunk.chunk_index,
            )
        )

        return result.scalars().all()

    async def save_embeddings_batch(
        self,
        items: list[tuple[UUID, list[float]]],
    ) -> None:
        """Saves chunk-level embeddings."""

        if not items:
            return

        await self.session.execute(
            update(ArticleChunk),
            [
                {
                    "id": chunk_id,
                    "embedding": embedding,
                }
                for chunk_id, embedding in items
            ],
        )

        await self.session.commit()

    async def search_similar(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[ArticleChunk]:
        result = await self.session.execute(
            select(ArticleChunk)
            .options(
                selectinload(ArticleChunk.article),
            )
            .where(ArticleChunk.embedding.is_not(None))
            .order_by(ArticleChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        return list(result.scalars().all())
