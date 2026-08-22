import asyncio

from ainews.core.config.config import Config
from ainews.core.config.settings import settings
from ainews.core.db.database import AsyncSessionLocal
from ainews.core.utils.logger import logger
from ainews.workers.processor.factory import build_pipeline, build_services

config = Config()


async def main_loop():
    logger.info("Initializing Processing Background Worker...")

    cycle_sleep_seconds = settings.processing_sleep_seconds

    services = build_services(config)

    while True:
        try:
            logger.info("Starting processing cycle...")
            async with AsyncSessionLocal() as session:
                pipeline = build_pipeline(
                    session=session,
                    services=services,
                )

                await pipeline.run()

        except Exception:
            logger.exception("Processing cycle failed.")

        logger.info(f"Cycle completed. Sleeping for {cycle_sleep_seconds} seconds.")

        await asyncio.sleep(cycle_sleep_seconds)


if __name__ == "__main__":
    asyncio.run(main_loop())
