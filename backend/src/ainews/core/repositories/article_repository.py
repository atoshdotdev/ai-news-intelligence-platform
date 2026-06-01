from ainews.core.db.models import Article
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, articles: list[Article]) -> list[Article]:
        """Bulk inserts newly discovered articles."""
        self.session.add_all(articles)
        await self.session.commit()
        return articles

    async def get_existing_hashes(
        self,
        hashes: list[str],
    ) -> set[str]:
        """
        Returns hashes already stored in DB.
        """

        if not hashes:
            return set()

        stmt = select(Article.url_hash).where(Article.url_hash.in_(hashes))

        result = await self.session.execute(stmt)

        return set(result.scalars().all())
