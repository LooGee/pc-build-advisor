import logging
from app.main import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.cleanup_tasks.cleanup_old_price_history")
def cleanup_old_price_history():
    """오래된 가격 이력 정리 (7일마다)"""
    logger.info("Cleaning up old price history (>90 days)...")
    # TODO: DELETE FROM price_history WHERE recorded_at < NOW() - INTERVAL '90 days'
    logger.info("Cleanup complete.")
