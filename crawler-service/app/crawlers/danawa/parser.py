from bs4 import BeautifulSoup
from typing import List, Optional
import re
import logging

logger = logging.getLogger(__name__)


def parse_price(price_str: str) -> Optional[int]:
    if not price_str:
        return None
    cleaned = re.sub(r"[^0-9]", "", price_str)
    return int(cleaned) if cleaned else None


def parse_product_list(html: str, source: str = "danawa") -> List[dict]:
    soup = BeautifulSoup(html, "lxml")
    products = []

    for item in soup.select("ul.product_list li.prod_item"):
        try:
            name_el = item.select_one("p.prod_name a")
            price_el = item.select_one("p.price_sect a strong")
            link_el = item.select_one("p.prod_name a")

            if not name_el or not price_el:
                continue

            name = name_el.get_text(strip=True)
            price = parse_price(price_el.get_text(strip=True))
            link = link_el.get("href", "") if link_el else ""

            if price:
                products.append({
                    "product_name": name,
                    "price_krw": price,
                    "product_url": f"https://prod.danawa.com{link}" if link.startswith("/") else link,
                    "source": source,
                    "in_stock": True,
                })
        except Exception as e:
            logger.debug(f"Error parsing product item: {e}")
            continue

    return products
