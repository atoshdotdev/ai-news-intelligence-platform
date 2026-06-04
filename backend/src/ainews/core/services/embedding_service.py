from ainews.core.clients.ollama_client import OllamaClient
from ainews.core.repositories.article_repository import ArticleRepository


class EmbeddingService:
    def __init__(self, ollama_client: OllamaClient, article_repo: ArticleRepository):
        self.article_repo = article_repo
        self.ollama = ollama_client

    async def process_pending_articles(self):
        articles = await self.article_repo.get_pending_articles(limit=10)

        if not articles:
            return

        inputs = [article.title + " " + article.content for article in articles]

        embeddings = await self.ollama.embed(inputs)

        embeddings_batch = [
            (article.id, embedding) for article, embedding in zip(articles, embeddings)
        ]

        await self.article_repo.save_embeddings_batch(embeddings_batch)
