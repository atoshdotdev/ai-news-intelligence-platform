from uuid import UUID

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
        max_chunks_per_article: int,
        neighbor_chunks: int,
    ):
        self.chunk_repo = chunk_repo
        self.embedding_service = embedding_service
        self.reranker_service = reranker_service
        self.retrieval_limit = retrieval_limit
        self.result_limit = result_limit
        self.max_chunks_per_article = max_chunks_per_article
        self.neighbor_chunks = neighbor_chunks

    async def retrieve(self, query: str) -> list[ArticleChunk]:
        query_embedding = self.embedding_service.encode_query(query)

        chunks = await self.chunk_repo.search_similar(
            query_embedding=query_embedding,
            limit=self.retrieval_limit,
        )

        if not chunks:
            return []

        ranked_chunks = self.reranker_service.rank(
            query=query,
            chunks=chunks,
        )

        selected: list[ArticleChunk] = []
        article_counts: dict[UUID, int] = {}

        for chunk in ranked_chunks:
            article_id = chunk.article.id
            count = article_counts.get(article_id, 0)

            if count >= self.max_chunks_per_article:
                continue

            selected.append(chunk)
            article_counts[article_id] = count + 1

            if len(selected) >= self.result_limit:
                break

        if not selected:
            return []

        if self.neighbor_chunks > 0:
            selected = await self.chunk_repo.get_neighbors(
                chunks=selected,
                neighbor_chunks=self.neighbor_chunks,
            )

        return selected

    def build_context(self, chunks: list[ArticleChunk]) -> str:
        sections: list[str] = []

        for chunk in chunks:
            article = chunk.article

            sections.append(
                f"Title: {article.title}\n"
                f"Published: {article.published_at}\n"
                f"URL: {article.url}\n\n"
                f"{chunk.content}"
            )

        return "\n\n".join(sections)

    def build_sources(
        self,
        chunks: list[ArticleChunk],
    ) -> list[ChatSource]:
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
