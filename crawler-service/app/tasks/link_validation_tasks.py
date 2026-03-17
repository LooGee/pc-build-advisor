import asyncio
import logging
import httpx
from app.main import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.link_validation_tasks.validate_all_links")
def validate_all_links():
    """구매 링크 유효성 검증 (12시간마다)"""
    asyncio.run(_validate_links())


async def _validate_links():
    logger.info("Validating purchase links...")
    # TODO: Check all product URLs for 404/redirects
    logger.info("Link validation complete.")
