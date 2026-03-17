from fastapi import Depends
from app.cache.redis_client import get_redis
from app.cache.cache_service import CacheService
from app.core.config import settings
import httpx


async def get_cache_service(redis=Depends(get_redis)) -> CacheService:
    return CacheService(redis)


async def get_ai_client():
    """Returns httpx client for AI service"""
    async with httpx.AsyncClient(base_url=settings.AI_SERVICE_URL, timeout=60.0) as client:
        yield client
