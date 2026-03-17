import redis.asyncio as redis
from app.core.config import settings

_pool = None


async def get_redis_pool():
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool


async def get_redis():
    pool = await get_redis_pool()
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.aclose()
