from ainews.core.db.models import ArticleChunk
from sentence_transformers import CrossEncoder


class RerankerService:
    """
    Re-ranks retrieved article chunks using a cross-encoder.

    The initial vector search should retrieve a relatively large candidate
    set. This service then scores those candidates against the user's query
    and returns them ordered by relevance.
    """

    def __init__(
        self,
        model_name: str,
        device: str,
        threshold: float,
    ):
        self.model = CrossEncoder(
            model_name,
            device=device,
        )
        self.threshold = threshold

    def rank(
        self,
        query: str,
        chunks: list[ArticleChunk],
    ) -> list[ArticleChunk]:
        if not chunks:
            return []

        pairs = [(query, chunk.content) for chunk in chunks]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        ranked = sorted(
            zip(chunks, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [chunk for chunk, score in ranked if float(score) >= self.threshold]
