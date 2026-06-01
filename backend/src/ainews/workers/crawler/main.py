import asyncio

from ainews.core.config.settings import settings
from ainews.core.db.database import AsyncSessionLocal
from ainews.core.services.crawler_service import CrawlerService
from ainews.core.utils.logging import logger


async def main_loop():
    logger.info("Initializing Web Crawler Background Worker...")
    CYCLE_SLEEP_SECONDS = settings.web_crawler_sleep_seconds

    while True:
        logger.info("Executing news collection synchronization layer...")

        async with AsyncSessionLocal() as session:
            crawler_service = CrawlerService(session)
            await crawler_service.run()

        logger.info(f"Cycle completed. Sleeping for {CYCLE_SLEEP_SECONDS} seconds.")
        await asyncio.sleep(CYCLE_SLEEP_SECONDS)


if __name__ == "__main__":
    asyncio.run(main_loop())
