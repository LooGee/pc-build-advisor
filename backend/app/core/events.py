from app.db.database import engine, Base
from app.cache.redis_client import get_redis_pool
import logging

logger = logging.getLogger(__name__)


async def startup_handler():
    logger.info("Starting up PC Build Advisor API...")
    # Redis connection pool
    await get_redis_pool()
    logger.info("Startup complete.")


async def shutdown_handler():
    logger.info("Shutting down...")
    await engine.dispose()
