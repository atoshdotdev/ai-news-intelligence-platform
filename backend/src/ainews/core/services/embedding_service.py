from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Owns the embedding model.

    The model is loaded once when the service is created.
    Database repositories are supplied per operation so this service
    can be reused by both workers and the API.
    """

    def __init__(
        self,
        model_name: str,
        batch_size: int = 32,
        device: str = "cuda",
    ):
        self.batch_size = batch_size

        self.model = SentenceTransformer(
            model_name,
            device=device,
            local_files_only=True,
        )

    def encode(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Encodes arbitrary texts.

        This is the generic method that can be used by RAG,
        workers, or any other service.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
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

    async def process_pending_chunks(
        self,
        chunk_repo: ChunkRepository,
    ) -> None:
        """
        Embeds chunks that do not have embeddings yet.
        """

        chunks = await chunk_repo.get_pending_embedding_chunks(
            limit=self.batch_size,
        )

        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]

        embeddings = self.encode(texts)

        items = [(chunk.id, embedding) for chunk, embedding in zip(chunks, embeddings)]

        await chunk_repo.save_embeddings_batch(items)

    async def process_pending_articles(
        self,
        article_repo: ArticleRepository,
    ) -> None:
        """
        Creates article-level embeddings used for event clustering.
        """

        articles = await article_repo.get_articles_pending_embedding(
            limit=self.batch_size,
        )

        if not articles:
            return

        texts = [f"{article.title}\n\n{article.content}" for article in articles]

        embeddings = self.encode(texts)

        items = [
            (article.id, embedding) for article, embedding in zip(articles, embeddings)
        ]

        await article_repo.save_article_embeddings_batch(items)
