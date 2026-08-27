from ainews.core.repositories.event_repository import EventRepository
from ainews.core.utils.logger import logger
from transformers import pipeline


class ClassificationService:
    """
    Classifies event summaries into predefined news categories
    using zero-shot classification.
    """

    def __init__(
        self,
        event_batch_size: int,
        model: str,
        device: str,
        candidate_labels: tuple[str, ...],
        multi_label: bool,
    ):
        self.event_batch_size = event_batch_size
        self.candidate_labels = candidate_labels
        self.multi_label = multi_label

        self.classifier = pipeline(
            "zero-shot-classification",
            model=model,
            device=device,
        )

    async def process_pending_events(
        self,
        event_repo: EventRepository,
    ) -> None:
        events = await event_repo.get_events_pending_classification(
            limit=self.event_batch_size,
        )

        if not events:
            return

        try:
            summaries = [event.summary for event in events if event.summary]

            results = self.classifier(
                summaries,
                candidate_labels=list(self.candidate_labels),
                multi_label=self.multi_label,
            )

            for event, result in zip(events, results):
                category = result["labels"][0]

                await event_repo.update_event(
                    event_id=event.id,
                    category=category,
                )

            await event_repo.commit()

        except Exception:
            await event_repo.rollback()

            logger.exception(
                "Classification batch failed. All changes rolled back.",
            )

            raise
