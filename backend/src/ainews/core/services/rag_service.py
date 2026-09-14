from ainews.core.db.models.article_chunk import ArticleChunk
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.schemas.chat_schemas import ChatSource
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.reranker_service import RerankerService


class RAGService:
    def __init__(
        self,
        chunk_repo: ChunkRepository,
        embedding_service: EmbeddingService,
        reranker_service: RerankerService,
        retrieval_limit: int,
        result_limit: int,
        max_context_chars: int,
    ):
        self.chunk_repo = chunk_repo
        self.embedding_service = embedding_service
        self.reranker_service = reranker_service
        self.retrieval_limit = retrieval_limit
        self.result_limit = result_limit
        self.max_context_chars = max_context_chars

    async def retrieve(self, query: str):
        query_embedding = self.embedding_service.encode_query(query)

        chunks = await self.chunk_repo.search_similar(
            query_embedding=query_embedding,
            limit=self.retrieval_limit,
        )

        if not chunks:
            return []

        chunks = self.reranker_service.rank(
            query=query,
            chunks=chunks,
        )

        return chunks[: self.result_limit]

    def build_context(self, chunks: list[ArticleChunk]) -> str:
        sections = []
        current_chars = 0

        for index, chunk in enumerate(chunks, start=1):
            article = chunk.article

            section = (
                f"[Source {index}]\n"
                f"Title: {article.title}\n"
                f"Published: {article.published_at}\n"
                f"URL: {article.url}\n\n"
                f"{chunk.content}"
            )

            if current_chars + len(section) > self.max_context_chars:
                break

            sections.append(section)
            current_chars += len(section)

        return "\n\n".join(sections)

    def build_sources(self, chunks: list[ArticleChunk]) -> list[ChatSource]:
        seen: set[str] = set()
        sources: list[ChatSource] = []

        for chunk in chunks:
            article = chunk.article
            source_id = str(article.id)

            if source_id in seen:
                continue

            seen.add(source_id)

            sources.append(
                ChatSource(
                    source_id=source_id,
                    url=article.url,
                    title=article.title,
                )
            )

        return sources
