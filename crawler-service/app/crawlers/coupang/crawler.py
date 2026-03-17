import logging
from typing import List
from app.crawlers.base_crawler import BaseCrawler
from app.config import settings

logger = logging.getLogger(__name__)


class CoupangCrawler(BaseCrawler):
    """Coupang requires Playwright for dynamic rendering."""

    def __init__(self):
        super().__init__(rate_limit=settings.COUPANG_RATE_LIMIT)
        self.source = "coupang"

    async def crawl_prices(self, component_id: str, search_query: str) -> List[dict]:
        # Playwright-based dynamic crawling
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.set_extra_http_headers(self.get_headers())
                url = f"https://www.coupang.com/np/search?q={search_query}"
                await page.goto(url, timeout=30000)
                await page.wait_for_timeout(2000)
                products = await self._extract_products(page, component_id)
                await browser.close()
                return products
        except Exception as e:
            logger.error(f"Coupang crawl failed: {e}")
            return []

    async def _extract_products(self, page, component_id: str) -> List[dict]:
        products = []
        items = await page.query_selector_all("li.search-product")
        for item in items[:3]:
            try:
                name_el = await item.query_selector(".name")
                price_el = await item.query_selector(".price-value")
                link_el = await item.query_selector("a.search-product-link")
                if not name_el or not price_el:
                    continue
                name = await name_el.text_content()
                price_str = await price_el.text_content()
                import re
                price = int(re.sub(r"[^0-9]", "", price_str)) if price_str else None
                href = await link_el.get_attribute("href") if link_el else ""
                if price:
                    products.append({
                        "component_id": component_id,
                        "product_name": name.strip(),
                        "price_krw": price,
                        "product_url": f"https://www.coupang.com{href}",
                        "source": self.source,
                        "in_stock": True,
                        "rocket_delivery": True,
                    })
            except Exception as e:
                logger.debug(f"Error parsing coupang item: {e}")
        return products

    async def crawl_component_list(self, category: str, page: int = 1) -> List[dict]:
        return []
