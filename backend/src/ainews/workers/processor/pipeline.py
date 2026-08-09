from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.services.chunking_service import ChunkingService
from ainews.core.services.embedding_service import EmbeddingService


class ProcessingPipeline:
    def __init__(
        self,
        article_repo: ArticleRepository,
        chunk_repo: ChunkRepository,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        ollama: OllamaClient,
    ):
        self.article_repo = article_repo
        self.chunk_repo = chunk_repo

        self.chunking_service = chunking_service
        self.embedding_service = embedding_service
        self.ollama = ollama

    async def run(self):
        await self.chunking_service.process_pending_articles(
            article_repo=self.article_repo,
            chunk_repo=self.chunk_repo,
        )

        await self.embedding_service.process_pending_chunks(
            chunk_repo=self.chunk_repo,
        )

        await self.embedding_service.process_pending_articles(
            article_repo=self.article_repo,
        )

        # Later:
        # await self.ner_service.process_pending_chunks(...)
        # await self.clustering_service.process_pending_articles(...)
        # await self.classification_service.process_pending_events(...)
        # await self.summarization_service.process_pending_events(...)
