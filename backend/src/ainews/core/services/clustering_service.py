from datetime import datetime, timezone
from math import exp
from typing import Any

import numpy as np
from ainews.core.db.models import Article, Event
from ainews.core.repositories.article_repository import ArticleRepository
from ainews.core.repositories.event_repository import EventRepository
from ainews.core.utils.logger import logger


class ClusteringService:
    """
    Assigns articles to events using embedding similarity,
    entity overlap, and temporal decay.
    """

    def __init__(
        self,
        article_batch_size: int,
        similarity_threshold: float,
        final_score_threshold: float,
        max_event_age_days: int,
        time_decay_hours: float,
        embedding_weight: float,
        entity_weight: float,
        time_weight: float,
    ):
        self.article_batch_size = article_batch_size
        self.similarity_threshold = similarity_threshold
        self.final_score_threshold = final_score_threshold
        self.max_event_age_days = max_event_age_days
        self.time_decay_hours = time_decay_hours
        self.embedding_weight = embedding_weight
        self.entity_weight = entity_weight
        self.time_weight = time_weight

    async def process_pending_articles(
        self,
        article_repo: ArticleRepository,
        event_repo: EventRepository,
    ) -> None:
        articles = await article_repo.get_articles_pending_clustering(
            limit=self.article_batch_size,
        )

        if not articles:
            return

        try:
            for article in articles:
                if article.embedding is None:
                    continue

                reference_time = self._get_reference_time(article)

                events = await event_repo.get_candidate_events(
                    reference_time=reference_time,
                    max_event_age_days=self.max_event_age_days,
                )

                best_event, best_score = self._find_best_event(
                    article=article,
                    events=events,
                    reference_time=reference_time,
                )

                if best_event is None or best_score < self.final_score_threshold:
                    await event_repo.create_from_article(article)

                    continue

                await event_repo.add_article(
                    event_id=best_event.id,
                    article_id=article.id,
                )

                event_articles = await event_repo.get_articles(
                    best_event.id,
                )

                event_embedding = self._calculate_centroid(
                    event_articles,
                )

                event_entities = self._aggregate_entities(
                    event_articles,
                )

                last_published_at = max(
                    (
                        self._get_reference_time(event_article)
                        for event_article in event_articles
                    ),
                    default=None,
                )

                image_url = next(
                    (
                        event_article.image_url
                        for event_article in event_articles
                        if event_article.image_url
                    ),
                    None,
                )

                await event_repo.update_event(
                    event_id=best_event.id,
                    embedding=event_embedding,
                    entities=event_entities,
                    image_url=image_url,
                    last_published_at=last_published_at,
                )

            await event_repo.commit()

        except Exception:
            await event_repo.rollback()

            logger.exception("Clustering batch failed. All changes rolled back.")

            raise

    def _find_best_event(
        self,
        article: Article,
        events: list[Event],
        reference_time: datetime,
    ) -> tuple[Event | None, float]:
        article_embedding = article.embedding

        if article_embedding is None:
            return None, 0.0

        best_event: Event | None = None
        best_score = 0.0

        for event in events:
            event_embedding = event.embedding

            if event_embedding is None:
                continue

            embedding_similarity = self._cosine_similarity(
                article_embedding,
                event_embedding,
            )

            if embedding_similarity < self.similarity_threshold:
                logger.debug(
                    "Event rejected by embedding threshold: "
                    "article=%s event=%s similarity=%.4f threshold=%.4f",
                    article.id,
                    event.id,
                    embedding_similarity,
                    self.similarity_threshold,
                )
                continue

            entity_overlap = self._entity_overlap(
                article.entities,
                event.entities,
            )

            time_score = self._time_decay(
                reference_time=reference_time,
                event_last_published_at=event.last_published_at,
            )

            final_score = (
                self.embedding_weight * embedding_similarity
                + self.entity_weight * entity_overlap
                + self.time_weight * time_score
            )

            if final_score > best_score:
                best_score = final_score
                best_event = event

        return best_event, best_score

    def _time_decay(
        self,
        reference_time: datetime,
        event_last_published_at: datetime | None,
    ) -> float:
        if event_last_published_at is None:
            return 0.0

        if event_last_published_at.tzinfo is None:
            event_last_published_at = event_last_published_at.replace(
                tzinfo=timezone.utc,
            )

        age_hours = max(
            0.0,
            (reference_time - event_last_published_at).total_seconds() / 3600.0,
        )

        return exp(
            -age_hours / self.time_decay_hours,
        )

    @staticmethod
    def _cosine_similarity(
        first: list[float],
        second: list[float],
    ) -> float:
        first_vector = np.asarray(first, dtype=np.float32)
        second_vector = np.asarray(second, dtype=np.float32)

        first_norm = np.linalg.norm(first_vector)
        second_norm = np.linalg.norm(second_vector)

        if first_norm == 0.0 or second_norm == 0.0:
            return 0.0

        return float(np.dot(first_vector, second_vector) / (first_norm * second_norm))

    @staticmethod
    def _entity_overlap(
        article_entities: list[dict[str, Any]] | None,
        event_entities: list[dict[str, Any]] | None,
    ) -> float:
        article_set = ClusteringService._entity_set(article_entities)
        event_set = ClusteringService._entity_set(event_entities)

        if not article_set or not event_set:
            return 0.0

        return len(article_set & event_set) / len(article_set | event_set)

    @staticmethod
    def _entity_set(
        entities: list[dict[str, Any]] | None,
    ) -> set[tuple[str, str]]:
        if not entities:
            return set()

        result: set[tuple[str, str]] = set()

        for entity in entities:
            text = entity.get("text")
            label = entity.get("label")

            if not text or not label:
                continue

            text = " ".join(text.strip().lower().split())
            label = label.strip().lower()

            if text and label:
                result.add((label, text))

        return result

    @staticmethod
    def _calculate_centroid(
        articles: list[Article],
    ) -> list[float] | None:
        embeddings = [
            article.embedding for article in articles if article.embedding is not None
        ]

        if not embeddings:
            return None

        matrix = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        return matrix.mean(axis=0).tolist()

    @staticmethod
    def _aggregate_entities(
        articles: list[Article],
    ) -> list[dict[str, Any]]:
        entities: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}

        for article in articles:
            if not article.entities:
                continue

            for entity in article.entities:
                text = entity.get("text")
                label = entity.get("label")
                score = entity.get("score")

                if not text or not label:
                    continue

                text = text.strip()

                if not text:
                    continue

                key = (
                    label.strip().lower(),
                    text.lower(),
                )

                existing = entities.get(key)

                if existing is None:
                    entities[key] = {
                        "text": text,
                        "label": label,
                        "score": (float(score) if score is not None else None),
                    }
                    continue

                if score is not None and (
                    existing["score"] is None or float(score) > existing["score"]
                ):
                    existing["score"] = float(score)

        return list(entities.values())

    @staticmethod
    def _get_reference_time(
        article: Article,
    ) -> datetime:
        reference_time = article.published_at

        if reference_time.tzinfo is None:
            reference_time = reference_time.replace(
                tzinfo=timezone.utc,
            )

        return reference_time
