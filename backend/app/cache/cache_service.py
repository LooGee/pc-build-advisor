import json
from typing import Optional, Any
from app.cache.cache_keys import *
from app.core.config import settings


class CacheService:
    def __init__(self, redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        val = await self.redis.get(key)
        if val:
            return json.loads(val)
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        await self.redis.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def get_component(self, component_id: str) -> Optional[dict]:
        return await self.get(component_key(component_id))

    async def set_component(self, component_id: str, data: dict) -> None:
        await self.set(component_key(component_id), data, settings.CACHE_TTL_COMPONENT)

    async def get_prices(self, component_id: str) -> Optional[list]:
        return await self.get(price_key(component_id))

    async def set_prices(self, component_id: str, data: list) -> None:
        await self.set(price_key(component_id), data, settings.CACHE_TTL_PRICE)

    async def get_llm_analysis(self, text: str) -> Optional[dict]:
        return await self.get(llm_analysis_key(hash(text)))

    async def set_llm_analysis(self, text: str, data: dict) -> None:
        await self.set(llm_analysis_key(hash(text)), data, settings.CACHE_TTL_LLM)
