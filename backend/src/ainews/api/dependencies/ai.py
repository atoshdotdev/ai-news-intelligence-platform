from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.reranker_service import RerankerService
from fastapi import Request


def get_ollama(request: Request) -> OllamaClient:
    return request.app.state.ollama


def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service


def get_reranker_service(request: Request) -> RerankerService:
    return request.app.state.reranker_service
