from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.repositories.event_repository import EventRepository
from ainews.core.services.chunking_service import ChunkingService
from ainews.core.services.classification_service import ClassificationService
from ainews.core.services.clustering_service import ClusteringService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.ner_service import NERService
from ainews.core.services.summarization_service import SummarizationService
from ainews.core.utils.logger import logger


class ProcessingPipeline:
    def __init__(
        self,
        article_repo: ArticleRepository,
        chunk_repo: ChunkRepository,
        event_repo: EventRepository,
        chunking_service: ChunkingService,
        ner_service: NERService,
        embedding_service: EmbeddingService,
        clustering_service: ClusteringService,
        summarization_service: SummarizationService,
        classification_service: ClassificationService,
        ollama: OllamaClient,
    ):
        self.article_repo = article_repo
        self.chunk_repo = chunk_repo
        self.event_repo = event_repo
        self.chunking_service = chunking_service
        self.ner_service = ner_service
        self.embedding_service = embedding_service
        self.clustering_service = clustering_service
        self.summarization_service = summarization_service
        self.classification_service = classification_service
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

        logger.info("Starting clustering...")

        await self.clustering_service.process_pending_articles(
            article_repo=self.article_repo,
            event_repo=self.event_repo,
        )

        logger.info("Clustering completed.")

        logger.info("Starting summarization...")

        await self.summarization_service.process_pending_events(
            event_repo=self.event_repo,
        )

        logger.info("Summarization completed.")

        logger.info("Starting classification...")

        await self.classification_service.process_pending_events(
            event_repo=self.event_repo,
        )

        logger.info("Classification completed.")
