import logging
from app.main import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.discovery_tasks.discover_new_components")
def discover_new_components():
    """신규 부품 감지 (24시간마다)"""
    logger.info("Starting component discovery...")
    # TODO: Crawl category pages and detect new products
    logger.info("Component discovery complete.")
