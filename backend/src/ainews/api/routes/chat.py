import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ainews.api.dependencies.ai import get_ollama
from ainews.core.db.database import get_session
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.schemas.chat_schemas import ChatRequest
from ainews.core.services.chat_service import ChatService
from ainews.core.services.rag_service import RAGService

router = APIRouter()


def get_services(session=Depends(get_session), ollama=Depends(get_ollama)):
    repo = ArticleRepository(session)

    rag = RAGService(repo, ollama)
    chat = ChatService(ollama)

    return rag, chat


@router.post("/stream")
async def chat_stream(payload: ChatRequest, deps=Depends(get_services)):
    message = payload.message
    rag, chat = deps

    articles = await rag.retrieve(message)
    context = rag.build_context(articles)

    async def event_stream():
        sent_sources = False

        try:
            async for token in chat.stream_chat(
                [{"role": "user", "content": message}],
                context,
            ):
                if articles and not sent_sources:
                    sources = [{"title": a.title, "url": a.url} for a in articles]
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
                    sent_sources = True

                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
