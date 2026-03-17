import httpx
import logging
from bs4 import BeautifulSoup
from typing import List
from app.crawlers.base_crawler import BaseCrawler
from app.config import settings
import re

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.compuzone.co.kr/product/product_list.htm?SearchWord={query}"


class CompuzoneCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(rate_limit=settings.COMPUZONE_RATE_LIMIT)
        self.source = "compuzone"

    async def crawl_prices(self, component_id: str, search_query: str) -> List[dict]:
        url = SEARCH_URL.format(query=search_query)
        await self._wait()
        async with httpx.AsyncClient(headers=self.get_headers(), timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return self._parse(response.text, component_id)
            except Exception as e:
                logger.error(f"Compuzone crawl failed: {e}")
        return []

    def _parse(self, html: str, component_id: str) -> List[dict]:
        soup = BeautifulSoup(html, "lxml")
        products = []
        for item in soup.select(".product_list_wrap .product_item")[:3]:
            name_el = item.select_one(".product_name")
            price_el = item.select_one(".product_price")
            link_el = item.select_one("a")
            if not name_el or not price_el:
                continue
            price_str = re.sub(r"[^0-9]", "", price_el.get_text())
            if price_str:
                products.append({
                    "component_id": component_id,
                    "product_name": name_el.get_text(strip=True),
                    "price_krw": int(price_str),
                    "product_url": link_el.get("href", "") if link_el else "",
                    "source": self.source,
                    "in_stock": True,
                })
        return products

    async def crawl_component_list(self, category: str, page: int = 1) -> List[dict]:
        return []
