from ainews.core.clients.ollama_client import OllamaClient
from fastapi import Request


def get_ollama(request: Request) -> OllamaClient:
    return request.app.state.ollama
