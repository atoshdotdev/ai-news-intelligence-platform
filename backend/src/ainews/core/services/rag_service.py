from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.repositories.article_repository import ArticleRepository


class RAGService:
    def __init__(self, article_repo: ArticleRepository, ollama: OllamaClient):
        self.article_repo = article_repo
        self.ollama = ollama

    async def retrieve(self, query: str):
        embedding = await self.ollama.embed(query)

        query_embedding = embedding[0]

        return await self.article_repo.search_similar(
            query_embedding=query_embedding,
            limit=3,
        )

    def build_context(self, articles):
        MAX_ARTICLES = 3

        return "\n\n".join(
            f"[Source {i + 1}]\nTitle: {a.title}\nURL: {a.url}\nSnippet: {a.content}"
            for i, a in enumerate(articles[:MAX_ARTICLES])
        )
