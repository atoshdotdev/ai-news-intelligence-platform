from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.config.settings import settings
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.services.embedding_service import EmbeddingService
from ainews.workers.processor.pipeline import ProcessingPipeline


def build_pipeline(session, ai_config):
    ollama = OllamaClient(settings.ollama_url, ai_config)

    article_repo = ArticleRepository(session)

    embedding_service = EmbeddingService(
        ollama_client=ollama,
        article_repo=article_repo,
    )

    return ProcessingPipeline(embedding_service)
