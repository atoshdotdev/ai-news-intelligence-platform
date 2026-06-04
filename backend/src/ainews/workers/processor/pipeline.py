from ainews.core.services.embedding_service import EmbeddingService


class ProcessingPipeline:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    async def run(self):
        await self.embedding_service.process_pending_articles()
