from dataclasses import dataclass

from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.config.ai_models import AIConfig
from ainews.core.config.settings import settings
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.services.chunking_service import ChunkingService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.workers.processor.pipeline import ProcessingPipeline


@dataclass
class ProcessingServices:
    chunking: ChunkingService
    embedding: EmbeddingService
    ollama: OllamaClient


def build_services(ai_config: AIConfig) -> ProcessingServices:
    ollama = OllamaClient(
        settings.ollama_host,
        ai_config,
    )

    chunking_service = ChunkingService(
        model_name=ai_config.embedding.model,
        chunk_size=512,
        chunk_overlap=50,
        batch_size=50,
    )

    embedding_service = EmbeddingService(
        model_name=ai_config.embedding.model,
        batch_size=32,
        device="cuda",
    )

    return ProcessingServices(
        chunking=chunking_service,
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
        embedding_service=services.embedding,
        ollama=services.ollama,
    )
