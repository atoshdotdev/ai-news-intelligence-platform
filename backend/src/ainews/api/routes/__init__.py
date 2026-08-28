from fastapi import APIRouter

from ainews.api.routes.blacklist import router as blacklist_router
from ainews.api.routes.category import router as category_router
from ainews.api.routes.chat import router as chat_router
from ainews.api.routes.source import router as source_router

router = APIRouter()

router.include_router(source_router, prefix="/sources", tags=["sources"])
router.include_router(blacklist_router, prefix="/sources", tags=["source_blacklist"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(category_router, prefix="/categories", tags=["categories"])
