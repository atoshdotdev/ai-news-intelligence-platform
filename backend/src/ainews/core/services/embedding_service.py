from collections import defaultdict
from uuid import UUID

from ainews.core.db.models import Article, ArticleChunk
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Owns the embedding model.

    Articles are the unit of work.

    One worker batch contains up to `article_batch_size` articles
    and all of their chunks.

    `processing_batch_size` controls how many texts are sent through
    the embedding model at once.

    Article-level embeddings are used for semantic filtering and
    event clustering. Chunk-level embeddings are used for RAG retrieval.
    """

    def __init__(
        self,
        model_name: str,
        article_batch_size: int,
        processing_batch_size: int,
        device: str,
    ):
        self.article_batch_size = article_batch_size
        self.processing_batch_size = processing_batch_size

        self.model = SentenceTransformer(
            model_name,
            device=device,
        )

    def encode(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Encodes multiple texts.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=self.processing_batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return [embedding.tolist() for embedding in embeddings]

    def encode_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Encodes a single query for vector search.
        """

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding.tolist()

    @staticmethod
    def build_article_embedding_text(
        article: Article,
        first_chunk: ArticleChunk,
    ) -> str:
        """
        Builds the compact representation used for the article-level
        embedding.

        The article embedding is intended for semantic filtering and
        event clustering, not detailed RAG retrieval.
        """

        parts = [
            f"Title: {article.title}",
            f"Lead: {first_chunk.content}",
        ]

        if article.entities:
            entities = ", ".join(
                entity["text"] for entity in article.entities if entity.get("text")
            )

            if entities:
                parts.append(f"Entities: {entities}")

        return "\n\n".join(parts)

    async def process_pending_articles(
        self,
        article_repo: ArticleRepository,
        chunk_repo: ChunkRepository,
    ) -> None:
        """
        Processes one batch of articles.

        `article_batch_size` represents the number of articles.

        For every selected article:

        1. Fetch all of its chunks.
        2. Create the article-level embedding if needed.
        3. Create embeddings for all chunks that are missing them.
        """

        articles = await article_repo.get_articles_pending_embedding(
            limit=self.article_batch_size,
        )

        if not articles:
            return

        article_ids = [article.id for article in articles]

        all_chunks = await chunk_repo.get_by_article_ids(
            article_ids,
        )

        chunks_by_article: dict[
            UUID,
            list[ArticleChunk],
        ] = defaultdict(list)

        for chunk in all_chunks:
            chunks_by_article[chunk.article_id].append(chunk)

        articles_needing_embedding = [
            article for article in articles if article.embedding is None
        ]

        if articles_needing_embedding:
            article_texts: list[str] = []
            articles_with_chunks: list[Article] = []

            for article in articles_needing_embedding:
                article_chunks = chunks_by_article.get(article.id)

                if not article_chunks:
                    continue

                first_chunk = article_chunks[0]

                article_texts.append(
                    self.build_article_embedding_text(
                        article,
                        first_chunk,
                    )
                )

                articles_with_chunks.append(article)

            article_embeddings = self.encode(article_texts)

            article_items = [
                (article.id, embedding)
                for article, embedding in zip(
                    articles_with_chunks,
                    article_embeddings,
                    strict=True,
                )
            ]

            await article_repo.save_article_embeddings_batch(
                article_items,
            )

        pending_chunks = [chunk for chunk in all_chunks if chunk.embedding is None]

        if not pending_chunks:
            return

        chunk_texts = [chunk.content for chunk in pending_chunks]

        chunk_embeddings = self.encode(chunk_texts)

        chunk_items = [
            (chunk.id, embedding)
            for chunk, embedding in zip(
                pending_chunks,
                chunk_embeddings,
                strict=True,
            )
        ]

        await chunk_repo.save_embeddings_batch(
            chunk_items,
        )
