from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.services.chunking_service import ChunkingService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.ner_service import NERService
from ainews.core.utils.logger import logger


class ProcessingPipeline:
    def __init__(
        self,
        article_repo: ArticleRepository,
        chunk_repo: ChunkRepository,
        chunking_service: ChunkingService,
        ner_service: NERService,
        embedding_service: EmbeddingService,
        ollama: OllamaClient,
    ):
        self.article_repo = article_repo
        self.chunk_repo = chunk_repo
        self.chunking_service = chunking_service
        self.ner_service = ner_service
        self.embedding_service = embedding_service
        self.ollama = ollama

    async def run(self) -> None:
        logger.info("Starting chunking...")

        await self.chunking_service.process_pending_articles(
            article_repo=self.article_repo,
            chunk_repo=self.chunk_repo,
        )

        logger.info("Chunking completed.")

        logger.info("Starting NER...")

        await self.ner_service.process_pending_articles(
            article_repo=self.article_repo,
            chunk_repo=self.chunk_repo,
        )

        logger.info("NER completed.")

        logger.info("Starting embeddings...")

        await self.embedding_service.process_pending_articles(
            article_repo=self.article_repo,
            chunk_repo=self.chunk_repo,
        )

        logger.info("Embeddings completed.")
