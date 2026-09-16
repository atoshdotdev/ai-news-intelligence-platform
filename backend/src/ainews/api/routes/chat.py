import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ainews.api.dependencies.ai import (
    get_embedding_service,
    get_llm_client,
    get_reranker_service,
)
from ainews.api.dependencies.auth import get_current_user
from ainews.core.config.config import Config
from ainews.core.db.database import get_session
from ainews.core.db.models import User
from ainews.core.db.models.chat_message import ChatMessageRole
from ainews.core.repositories.chat_message_repository import ChatMessageRepository
from ainews.core.repositories.chat_repository import ChatRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.schemas.chat_schemas import (
    ChatDetailRead,
    ChatRead,
    ChatRequest,
)
from ainews.core.services.chat_service import ChatService
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.rag_service import RAGService
from ainews.core.services.reranker_service import RerankerService
from ainews.core.utils.chat import to_llm_messages

router = APIRouter(
    dependencies=[Depends(get_current_user)],
)


def get_chat_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
    llm_client=Depends(get_llm_client),
) -> ChatService:
    config: Config = request.app.state.config

    chat_repo = ChatRepository(session)
    chat_message_repo = ChatMessageRepository(session)

    return ChatService(
        llm_client=llm_client,
        system_prompt=config.chat.system_prompt,
        user_prompt=config.chat.user_prompt,
        chat_repository=chat_repo,
        chat_message_repository=chat_message_repo,
    )


def get_rag_service(
    request: Request,
    session: AsyncSession = Depends(get_session),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    reranker_service: RerankerService = Depends(get_reranker_service),
) -> RAGService:
    config: Config = request.app.state.config

    chunk_repo = ChunkRepository(session)

    return RAGService(
        chunk_repo=chunk_repo,
        embedding_service=embedding_service,
        reranker_service=reranker_service,
        retrieval_limit=config.rag.retrieval_limit,
        result_limit=config.rag.result_limit,
        max_context_chars=config.rag.max_context_chars,
    )


@router.post("/")
async def chat_stream(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
    chat_service: ChatService = Depends(get_chat_service),
):
    message = payload.last_user_message

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message found",
        )

    if payload.chat_id is None:
        chat = await chat_service.create_chat(
            user_id=current_user.id,
            title="New chat",
        )

        is_new_chat = True
    else:
        chat = await chat_service.get_chat_entity(
            chat_id=payload.chat_id,
            user_id=current_user.id,
        )

        is_new_chat = False

    await chat_service.save_message(
        chat_id=chat.id,
        role=ChatMessageRole.USER,
        content=message.text,
    )

    query = message.text

    chunks = await rag_service.retrieve(query)
    context = rag_service.build_context(chunks)
    sources = rag_service.build_sources(chunks)

    messages = to_llm_messages(payload.messages)

    async def event_stream():
        message_id = str(uuid4())
        text_id = str(uuid4())
        assistant_text = ""

        yield f"data: {
            json.dumps(
                {
                    'type': 'start',
                    'messageId': message_id,
                }
            )
        }\n\n"

        if is_new_chat:
            yield f"data: {
                json.dumps(
                    {
                        'type': 'data-chatId',
                        'data': str(chat.id),
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
            assistant_text += token

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

        await chat_service.save_message(
            chat_id=chat.id,
            role=ChatMessageRole.ASSISTANT,
            content=assistant_text,
        )

        chat.updated_at = datetime.now(timezone.utc)
        await chat_service.update_chat(chat)

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


@router.get("/", response_model=list[ChatRead])
async def read_chats(
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    return await service.get_user_chats(current_user.id)


@router.get("/{chat_id}", response_model=ChatDetailRead)
async def read_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    return await service.get_chat(
        chat_id,
        current_user.id,
    )


@router.patch("/{chat_id}/pin", response_model=ChatRead)
async def toggle_chat_pin(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    return await service.toggle_pin(
        chat_id,
        current_user.id,
    )


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    await service.delete_chat(
        chat_id,
        current_user.id,
    )
