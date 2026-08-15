from collections import defaultdict
from typing import Any
from uuid import UUID

from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.chunk_repository import ChunkRepository
from gliner import GLiNER


class NERService:
    """
    Owns the GLiNER model.

    The model is loaded once when the service is created.
    Repositories are supplied per operation.
    """

    def __init__(
        self,
        model_name: str,
        labels: tuple[str, ...],
        threshold: float,
        device: str,
        article_batch_size: int,
    ):
        self.labels = list(labels)
        self.threshold = threshold
        self.article_batch_size = article_batch_size

        self.model = GLiNER.from_pretrained(
            model_name,
        )

        self.model = self.model.to(device)

    def extract_entities(
        self,
        text: str,
    ) -> list[dict[str, Any]]:
        entities = self.model.predict_entities(
            text,
            self.labels,
            threshold=self.threshold,
        )

        return [
            {
                "text": entity["text"],
                "label": entity["label"],
                "score": float(entity["score"]),
                "start": entity.get("start"),
                "end": entity.get("end"),
            }
            for entity in entities
        ]

    @staticmethod
    def deduplicate_entities(
        entities: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        seen: dict[tuple[str, str], dict[str, Any]] = {}

        for entity in entities:
            key = (
                entity["text"].strip().lower(),
                entity["label"],
            )

            existing = seen.get(key)

            if existing is None or entity["score"] > existing["score"]:
                seen[key] = entity

        return list(seen.values())

    async def process_pending_articles(
        self,
        article_repo: ArticleRepository,
        chunk_repo: ChunkRepository,
    ) -> None:
        """
        Processes NER for a batch of articles.

        For each article:
        1. Get all of its chunks.
        2. Run NER on every chunk.
        3. Combine all entities.
        4. Deduplicate entities.
        5. Save the final entity list to the article.

        The article is only marked as NER processed after all
        of its chunks have been successfully processed.
        """

        articles = await article_repo.get_articles_pending_ner(
            limit=self.article_batch_size,
        )

        if not articles:
            return

        article_ids = [article.id for article in articles]

        chunks = await chunk_repo.get_by_article_ids(article_ids)

        entities_by_article: dict[UUID, list[dict[str, Any]]] = defaultdict(list)

        for chunk in chunks:
            entities = self.extract_entities(chunk.content)

            entities_by_article[chunk.article_id].extend(entities)

        results: list[tuple[UUID, list[dict[str, Any]]]] = []

        for article in articles:
            entities = entities_by_article[article.id]

            entities = self.deduplicate_entities(entities)

            results.append(
                (
                    article.id,
                    entities,
                )
            )

        await article_repo.save_article_entities_batch(results)
