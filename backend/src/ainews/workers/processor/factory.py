from dataclasses import dataclass

from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.config.ai_models import AIConfig
from ainews.core.config.settings import settings
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.services.chunking_service import ChunkingService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.ner_service import NERService
from ainews.workers.processor.pipeline import ProcessingPipeline


@dataclass
class ProcessingServices:
    chunking: ChunkingService
    ner: NERService
    embedding: EmbeddingService
    ollama: OllamaClient


def build_services(ai_config: AIConfig) -> ProcessingServices:
    ollama = OllamaClient(
        settings.ollama_host,
        ai_config,
    )

    chunking_service = ChunkingService(
        model_name=ai_config.embedding.model,
        chunk_size=ai_config.chunking.chunk_token_size,
        chunk_overlap=ai_config.chunking.chunk_token_overlap,
        article_batch_size=ai_config.chunking.article_batch_size,
    )

    ner_service = NERService(
        model_name=ai_config.ner.model,
        labels=ai_config.ner.labels,
        threshold=ai_config.ner.threshold,
        device=ai_config.ner.device,
        article_batch_size=ai_config.ner.article_batch_size,
    )

    embedding_service = EmbeddingService(
        model_name=ai_config.embedding.model,
        processing_batch_size=ai_config.embedding.processing_batch_size,
        article_batch_size=ai_config.embedding.article_batch_size,
        device=ai_config.embedding.device,
    )

    return ProcessingServices(
        chunking=chunking_service,
        ner=ner_service,
        embedding=embedding_service,
        ollama=ollama,
    )


def build_pipeline(
    session,
    services: ProcessingServices,
) -> ProcessingPipeline:
    article_repo = ArticleRepository(session)
    chunk_repo = ChunkRepository(session)

    return ProcessingPipeline(
        article_repo=article_repo,
        chunk_repo=chunk_repo,
        chunking_service=services.chunking,
        ner_service=services.ner,
        embedding_service=services.embedding,
        ollama=services.ollama,
    )
