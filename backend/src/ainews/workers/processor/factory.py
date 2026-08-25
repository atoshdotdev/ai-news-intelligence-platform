from dataclasses import dataclass

from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.config.config import Config
from ainews.core.config.settings import settings
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.repositories.event_repository import EventRepository
from ainews.core.services.chunking_service import ChunkingService
from ainews.core.services.clustering_service import ClusteringService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.ner_service import NERService
from ainews.core.services.summarization_service import SummarizationService
from ainews.workers.processor.pipeline import ProcessingPipeline


@dataclass
class ProcessingServices:
    chunking: ChunkingService
    ner: NERService
    embedding: EmbeddingService
    clustering: ClusteringService
    summarization: SummarizationService
    ollama: OllamaClient


def build_services(config: Config) -> ProcessingServices:
    ollama = OllamaClient(
        settings.ollama_host,
        config,
    )

    chunking_service = ChunkingService(
        model_name=config.embedding.model,
        chunk_size=config.chunking.chunk_token_size,
        chunk_overlap=config.chunking.chunk_token_overlap,
        article_batch_size=config.chunking.article_batch_size,
    )

    ner_service = NERService(
        model_name=config.ner.model,
        labels=config.ner.labels,
        threshold=config.ner.threshold,
        device=config.ner.device,
        article_batch_size=config.ner.article_batch_size,
    )

    embedding_service = EmbeddingService(
        model_name=config.embedding.model,
        processing_batch_size=config.embedding.processing_batch_size,
        article_batch_size=config.embedding.article_batch_size,
        device=config.embedding.device,
    )

    clustering_service = ClusteringService(
        article_batch_size=config.clustering.article_batch_size,
        similarity_threshold=config.clustering.similarity_threshold,
        final_score_threshold=config.clustering.final_score_threshold,
        max_event_age_days=config.clustering.max_event_age_days,
        time_decay_hours=config.clustering.time_decay_hours,
        embedding_weight=config.clustering.embedding_weight,
        entity_weight=config.clustering.entity_weight,
        time_weight=config.clustering.time_weight,
    )

    summarization_service = SummarizationService(
        ollama=ollama,
        event_batch_size=config.summarization.event_batch_size,
        max_articles_per_event=config.summarization.max_articles_per_event,
        article_max_chars=config.summarization.article_max_chars,
        system_prompt=config.summarization.system_prompt,
        user_prompt=config.summarization.user_prompt,
        refresh_hours=config.summarization.refresh_hours,
    )

    return ProcessingServices(
        chunking=chunking_service,
        ner=ner_service,
        embedding=embedding_service,
        ollama=ollama,
        clustering=clustering_service,
        summarization=summarization_service,
    )


def build_pipeline(
    session,
    services: ProcessingServices,
) -> ProcessingPipeline:
    article_repo = ArticleRepository(session)
    chunk_repo = ChunkRepository(session)
    event_repo = EventRepository(session)

    return ProcessingPipeline(
        article_repo=article_repo,
        chunk_repo=chunk_repo,
        event_repo=event_repo,
        chunking_service=services.chunking,
        ner_service=services.ner,
        embedding_service=services.embedding,
        ollama=services.ollama,
        clustering_service=services.clustering,
        summarization_service=services.summarization,
    )
