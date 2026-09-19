from uuid import UUID

from ainews.core.clients.llm_client import LLMClient
from ainews.core.db.models.article_chunk import ArticleChunk
from ainews.core.repositories.chunk_repository import ChunkRepository
from ainews.core.schemas.chat_schemas import ChatSource, LLMMessage
from ainews.core.services.embedding_service import EmbeddingService
from ainews.core.services.reranker_service import RerankerService


class RAGService:
    def __init__(
        self,
        chunk_repo: ChunkRepository,
        embedding_service: EmbeddingService,
        reranker_service: RerankerService,
        llm_client: LLMClient,
        retrieval_limit: int,
        result_limit: int,
        decision_model: str,
        decision_temperature: float,
        decision_context_size: int,
        decision_max_tokens: int,
        decision_system_prompt: str,
        max_chunks_per_article: int,
        neighbor_chunks: int,
    ):
        self.chunk_repo = chunk_repo
        self.embedding_service = embedding_service
        self.reranker_service = reranker_service
        self.llm_client = llm_client
        self.retrieval_limit = retrieval_limit
        self.result_limit = result_limit
        self.decision_model = decision_model
        self.decision_temperature = decision_temperature
        self.decision_context_size = decision_context_size
        self.decision_max_tokens = decision_max_tokens
        self.decision_system_prompt = decision_system_prompt
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
        sections = []

        for index, chunk in enumerate(chunks, start=1):
            article = chunk.article

            sections.append(
                f"Title: {article.title}\n"
                f"Published: {article.published_at}\n"
                f"URL: {article.url}\n\n"
                f"{chunk.content}"
            )

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

    async def requires_rag(
        self,
        messages: list[LLMMessage],
    ) -> bool:
        if not messages:
            return True

        decision_input = self._build_decision_input(messages)

        return await self.llm_client.classify_rag(
            user_message=decision_input,
            system_prompt=self.decision_system_prompt,
            model=self.decision_model,
            temperature=self.decision_temperature,
            max_tokens=self.decision_max_tokens,
            context_size=self.decision_context_size,
        )

    def _build_decision_input(
        self,
        messages: list[LLMMessage],
    ) -> str:
        history = messages[:-1]
        current_message = messages[-1]

        history_text = "\n".join(
            f"{message.role.upper()}: {message.content}" for message in history
        )

        return f"""\
            CONVERSATION HISTORY:
            {history_text or "(none)"}

            CURRENT USER MESSAGE:
            {current_message.content}
        """
