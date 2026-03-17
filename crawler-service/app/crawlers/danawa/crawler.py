import httpx
import logging
from typing import List
from app.crawlers.base_crawler import BaseCrawler
from app.crawlers.danawa.parser import parse_product_list
from app.crawlers.danawa.urls import CATEGORY_URLS, SEARCH_URL
from app.config import settings

logger = logging.getLogger(__name__)


class DanawaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(rate_limit=settings.DANAWA_RATE_LIMIT)
        self.source = "danawa"

    async def crawl_prices(self, component_id: str, search_query: str) -> List[dict]:
        url = SEARCH_URL.format(query=search_query)
        await self._wait()
        async with httpx.AsyncClient(headers=self.get_headers(), timeout=30) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    products = parse_product_list(response.text, self.source)
                    # Tag with component_id
                    for p in products:
                        p["component_id"] = component_id
                    return products[:3]  # top 3 results
            except Exception as e:
                logger.error(f"Danawa crawl failed: {e}")
        return []

    async def crawl_component_list(self, category: str, page: int = 1) -> List[dict]:
        url = CATEGORY_URLS.get(category)
        if not url:
            return []
        await self._wait()
        async with httpx.AsyncClient(headers=self.get_headers(), timeout=30) as client:
            try:
                response = await client.get(f"{url}&page={page}")
                if response.status_code == 200:
                    return parse_product_list(response.text, self.source)
            except Exception as e:
                logger.error(f"Danawa category crawl failed: {e}")
        return []
