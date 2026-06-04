import asyncio

from ainews.core.config.ai_models import AIConfig
from ainews.core.config.settings import settings
from ainews.core.db.database import AsyncSessionLocal
from ainews.core.utils.logging import logger
from ainews.workers.processor.factory import build_pipeline

ai_config = AIConfig()


async def main_loop():
    logger.info("Initializing Processing Background Worker...")
    CYCLE_SLEEP_SECONDS = settings.processing_sleep_seconds

    while True:
        async with AsyncSessionLocal() as session:
            pipeline = build_pipeline(
                session=session,
                ai_config=ai_config,
            )

            await pipeline.run()

        logger.info(f"Cycle completed. Sleeping for {CYCLE_SLEEP_SECONDS} seconds.")
        await asyncio.sleep(CYCLE_SLEEP_SECONDS)


if __name__ == "__main__":
    asyncio.run(main_loop())
