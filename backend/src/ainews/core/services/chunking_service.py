from ainews.core.db.models import ArticleChunk
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer


class ChunkingService:
    """
    Owns the tokenizer used for chunking.

    The tokenizer is loaded once when the service is created.
    Repositories are supplied per processing operation.
    """

    def __init__(
        self,
        model_name: str,
        chunk_size: int,
        chunk_overlap: int,
        article_batch_size: int,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.article_batch_size = article_batch_size

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
        )

    async def process_pending_articles(
        self,
        article_repo: ArticleRepository,
        chunk_repo: ChunkRepository,
    ) -> None:
        """
        Finds articles without chunks, creates their chunks,
        and persists them.
        """

        articles = await article_repo.get_articles_without_chunks(
            limit=self.article_batch_size,
        )

        for article in articles:
            chunks = self.split_article(article.content)

            chunk_models = [
                ArticleChunk(
                    article_id=article.id,
                    chunk_index=index,
                    content=chunk,
                    token_count=self.count_tokens(chunk),
                )
                for index, chunk in enumerate(chunks)
            ]

            if chunk_models:
                await chunk_repo.create_many(chunk_models)

    def split_article(
        self,
        text: str,
    ) -> list[str]:
        splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            self.tokenizer,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

        return splitter.split_text(text)

    def count_tokens(
        self,
        text: str,
    ) -> int:
        return len(
            self.tokenizer.encode(
                text,
                add_special_tokens=False,
            )
        )
