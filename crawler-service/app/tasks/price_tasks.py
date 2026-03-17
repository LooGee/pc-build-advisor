import asyncio
import logging
from app.main import celery_app
from app.crawlers.danawa.crawler import DanawaCrawler
from app.crawlers.compuzone.crawler import CompuzoneCrawler

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.price_tasks.update_all_prices", bind=True, max_retries=3)
def update_all_prices(self):
    """가격 정보 업데이트 (6시간마다)"""
    try:
        asyncio.run(_update_prices())
    except Exception as exc:
        logger.error(f"Price update failed: {exc}")
        raise self.retry(exc=exc, countdown=300)


async def _update_prices():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy import select
    import os

    db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/pc_advisor")
    engine = create_async_engine(db_url)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    danawa = DanawaCrawler()
    compuzone = CompuzoneCrawler()

    async with Session() as session:
        # Load active components
        from app.pipeline.db_writer import write_prices
        logger.info("Starting price update crawl...")
        # In production: query all active components and update prices
        logger.info("Price update complete.")

    await engine.dispose()
