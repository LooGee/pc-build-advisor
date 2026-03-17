import httpx
import logging
from bs4 import BeautifulSoup
from typing import List
from app.crawlers.base_crawler import BaseCrawler
from app.config import settings
import re

logger = logging.getLogger(__name__)

BASE_URL = "https://pcpartpicker.com"
SEARCH_URL = f"{BASE_URL}/search/#W={{}}"


class PCPartPickerCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(rate_limit=settings.PCPARTPICKER_RATE_LIMIT)
        self.source = "pcpartpicker"

    async def crawl_prices(self, component_id: str, search_query: str) -> List[dict]:
        url = SEARCH_URL.format(search_query.replace(" ", "+"))
        await self._wait()
        async with httpx.AsyncClient(headers=self.get_headers(), timeout=30) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return self._parse(response.text, component_id)
            except Exception as e:
                logger.error(f"PCPartPicker crawl failed: {e}")
        return []

    def _parse(self, html: str, component_id: str) -> List[dict]:
        soup = BeautifulSoup(html, "lxml")
        products = []
        for row in soup.select("tr.tr__product")[:3]:
            name_el = row.select_one("td.td__name a")
            price_el = row.select_one("td.td__price a")
            if not name_el or not price_el:
                continue
            price_str = re.sub(r"[^0-9.]", "", price_el.get_text())
            if price_str:
                try:
                    price_usd = float(price_str)
                    price_krw = int(price_usd * 1350)
                    products.append({
                        "component_id": component_id,
                        "product_name": name_el.get_text(strip=True),
                        "price_krw": price_krw,
                        "price_usd": price_usd,
                        "product_url": f"{BASE_URL}{price_el.get('href', '')}",
                        "source": self.source,
                        "in_stock": True,
                    })
                except ValueError:
                    pass
        return products

    async def crawl_component_list(self, category: str, page: int = 1) -> List[dict]:
        return []
