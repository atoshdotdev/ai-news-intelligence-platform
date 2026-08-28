import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ainews.api.dependencies.ai import (
    get_embedding_service,
    get_ollama,
    get_reranker_service,
)
from ainews.core.config.config import Config
from ainews.core.db.database import get_session
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.schemas.chat_schemas import ChatRequest
from ainews.core.services.chat_service import ChatService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.rag_service import RAGService
from ainews.core.services.reranker_service import RerankerService

router = APIRouter()


def get_services(
    request: Request,
    session=Depends(get_session),
    ollama=Depends(get_ollama),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    reranker_service: RerankerService = Depends(get_reranker_service),
):
    config: Config = request.app.state.config
    chunk_repo = ChunkRepository(session)

    rag = RAGService(
        chunk_repo=chunk_repo,
        embedding_service=embedding_service,
        reranker_service=reranker_service,
        retrieval_limit=config.rag.retrieval_limit,
        result_limit=config.rag.result_limit,
        max_context_chars=config.rag.max_context_chars,
    )

    chat = ChatService(ollama, user_prompt=config.chat.user_prompt)

    return rag, chat


@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    deps: tuple[RAGService, ChatService] = Depends(get_services),
):
    message = payload.message
    rag_service, chat_service = deps

    chunks = await rag_service.retrieve(message)
    context = rag_service.build_context(chunks)

    async def event_stream():
        try:
            if chunks:
                seen_articles = set()
                sources = []

                for chunk in chunks:
                    article = chunk.article

                    if article.id in seen_articles:
                        continue

                    seen_articles.add(article.id)

                    sources.append(
                        {
                            "title": article.title,
                            "url": article.url,
                        }
                    )

                yield (
                    f"data: {
                        json.dumps(
                            {
                                'type': 'sources',
                                'sources': sources,
                            }
                        )
                    }\n\n"
                )

            async for token in chat_service.stream_chat(
                question=message,
                context=context,
            ):
                yield (
                    f"data: {
                        json.dumps(
                            {
                                'type': 'token',
                                'content': token,
                            }
                        )
                    }\n\n"
                )

            yield (
                f"data: {
                    json.dumps(
                        {
                            'type': 'done',
                        }
                    )
                }\n\n"
            )

        except Exception as e:
            yield (
                f"data: {
                    json.dumps(
                        {
                            'type': 'error',
                            'message': str(e),
                        }
                    )
                }\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )
