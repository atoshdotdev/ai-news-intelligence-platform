from collections.abc import Sequence
from uuid import UUID

from ainews.core.db.models import ArticleChunk
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(
        self,
        chunks: list[ArticleChunk],
    ) -> list[ArticleChunk]:
        """
        Bulk inserts article chunks.
        """
        self.session.add_all(chunks)
        await self.session.commit()

        return chunks

    async def get_pending_ner_chunks(
        self,
        limit: int = 100,
    ) -> Sequence[ArticleChunk]:
        """
        Returns chunks that have not been processed by NER.
        """

        result = await self.session.execute(
            select(ArticleChunk)
            .where(ArticleChunk.ner_processed_at.is_(None))
            .limit(limit)
        )

        return result.scalars().all()

    async def mark_ner_processed(
        self,
        chunk_ids: list[UUID],
    ):
        """
        Marks chunks as completed for NER processing.
        """

        await self.session.execute(
            update(ArticleChunk)
            .where(ArticleChunk.id.in_(chunk_ids))
            .values(ner_processed_at=func.now())
        )

        await self.session.commit()

    async def get_pending_embedding_chunks(
        self,
        limit: int = 100,
    ) -> Sequence[ArticleChunk]:
        """
        Returns chunks that do not have embeddings.
        """

        result = await self.session.execute(
            select(ArticleChunk).where(ArticleChunk.embedding.is_(None)).limit(limit)
        )

        return result.scalars().all()

    async def save_embeddings_batch(
        self,
        items: list[tuple[UUID, list[float]]],
    ):
        """
        Saves embeddings for chunks.
        """

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

    async def get_by_article_id(
        self,
        article_id: UUID,
    ) -> Sequence[ArticleChunk]:
        """
        Returns all chunks belonging to an article.
        """

        result = await self.session.execute(
            select(ArticleChunk)
            .where(ArticleChunk.article_id == article_id)
            .order_by(ArticleChunk.chunk_index)
        )

        return result.scalars().all()

    async def search_similar(
        self,
        query_embedding: Sequence[float],
        limit: int = 5,
    ) -> list[ArticleChunk]:
        """
        Vector similarity search for RAG retrieval.
        """

        result = await self.session.execute(
            select(ArticleChunk)
            .where(ArticleChunk.embedding.is_not(None))
            .order_by(ArticleChunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        return list(result.scalars().all())
