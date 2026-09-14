import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from ainews.api.dependencies.ai import (
    get_embedding_service,
    get_llm_client,
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
from ainews.core.utils.chat import to_llm_messages

router = APIRouter()


def get_services(
    request: Request,
    session=Depends(get_session),
    llm_client=Depends(get_llm_client),
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

    chat = ChatService(
        llm_client,
        system_prompt=config.chat.system_prompt,
        user_prompt=config.chat.user_prompt,
    )

    return rag, chat


@router.post("/")
async def chat_stream(
    payload: ChatRequest,
    deps: tuple[RAGService, ChatService] = Depends(get_services),
):
    print("Received chat request:", payload)
    message = payload.last_user_message

    if message is None:
        raise HTTPException(
            status_code=400,
            detail="No user message found",
        )

    query = message.text

    rag_service, chat_service = deps

    chunks = await rag_service.retrieve(query)
    context = rag_service.build_context(chunks)
    sources = rag_service.build_sources(chunks)

    messages = to_llm_messages(payload.messages)

    async def event_stream():
        message_id = str(uuid4())
        text_id = str(uuid4())

        yield f"data: {
            json.dumps(
                {
                    'type': 'start',
                    'messageId': message_id,
                }
            )
        }\n\n"

        yield f"data: {
            json.dumps(
                {
                    'type': 'text-start',
                    'id': text_id,
                }
            )
        }\n\n"

        async for token in chat_service.stream_chat(
            messages=messages,
            context=context,
        ):
            yield f"data: {
                json.dumps(
                    {
                        'type': 'text-delta',
                        'id': text_id,
                        'delta': token,
                    }
                )
            }\n\n"

        yield f"data: {
            json.dumps(
                {
                    'type': 'text-end',
                    'id': text_id,
                }
            )
        }\n\n"

        for source in sources:
            yield f"data: {
                json.dumps(
                    {
                        'type': 'source-url',
                        'sourceId': source.source_id,
                        'url': source.url,
                        'title': source.title,
                    }
                )
            }\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "x-vercel-ai-ui-message-stream": "v1",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
