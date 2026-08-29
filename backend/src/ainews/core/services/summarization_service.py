from ainews.core.clients.llm_client import LLMClient
from ainews.core.db.models import Article
from ainews.core.repositories.event_repository import EventRepository
from ainews.core.utils.logger import logger


class SummarizationService:
    """
    Generates summaries for events using a representative selection
    of the articles belonging to each event.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        event_batch_size: int,
        max_articles_per_event: int,
        article_max_chars: int,
        refresh_hours: int,
        system_prompt: str,
        user_prompt: str,
    ):
        self.llm_client = llm_client
        self.max_articles_per_event = max_articles_per_event
        self.article_max_chars = article_max_chars
        self.event_batch_size = event_batch_size
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.refresh_hours = refresh_hours

    async def process_pending_events(
        self,
        event_repo: EventRepository,
    ) -> None:
        events = await event_repo.get_events_pending_summary(
            limit=self.event_batch_size,
            refresh_hours=self.refresh_hours,
        )

        if not events:
            return

        try:
            for event in events:
                articles = await event_repo.get_articles(event.id)

                if not articles:
                    logger.warning(
                        "Skipping event without articles: event=%s",
                        event.id,
                    )
                    continue

                selected_articles = self._select_articles(articles)

                prompt = self._build_prompt(selected_articles)

                summary = await self.llm_client.summarize(prompt)

                if not summary:
                    logger.warning(
                        "Empty summary returned: event=%s",
                        event.id,
                    )
                    continue

                await event_repo.update_event(
                    event_id=event.id,
                    summary=summary,
                    summary_last_published_at=event.last_published_at,
                )

            await event_repo.commit()
        except Exception:
            await event_repo.rollback()

            logger.exception(
                "Summarization batch failed. All changes rolled back.",
            )

            raise

    def _select_articles(
        self,
        articles: list[Article],
    ) -> list[Article]:
        """
        Selects a representative subset of articles while prioritizing
        the latest developments and preserving some chronological context.
        """

        max_articles = self.max_articles_per_event

        if len(articles) <= max_articles:
            return articles

        first_count = 1
        last_count = max_articles - 2
        middle_count = 1

        first_articles = articles[:first_count]

        middle_start = (len(articles) - middle_count) // 2
        middle_end = middle_start + middle_count

        middle_articles = articles[middle_start:middle_end]

        last_articles = articles[-last_count:]

        return [
            *first_articles,
            *middle_articles,
            *last_articles,
        ]

    def _build_prompt(
        self,
        articles: list[Article],
    ) -> str:
        """
        Builds the user prompt using the configured prompt template
        and selected article content.
        """

        max_chars = self.article_max_chars

        article_sections: list[str] = []

        for index, article in enumerate(articles, start=1):
            content = article.content.strip()

            if len(content) > max_chars:
                content = content[:max_chars]

            published_at = article.published_at

            article_sections.append(
                f"""ARTICLE {index}
                Published: {published_at}
                Title: {article.title}

                Content:
                {content}"""
            )

        return self.user_prompt.format(
            articles="\n\n".join(article_sections),
        )
