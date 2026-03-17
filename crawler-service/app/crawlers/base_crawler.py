import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    def __init__(self, rate_limit: float = 3.0):
        self.rate_limit = rate_limit
        self.ua = UserAgent()

    def get_headers(self) -> dict:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    async def _wait(self):
        await asyncio.sleep(self.rate_limit)

    @abstractmethod
    async def crawl_prices(self, component_id: str, search_query: str) -> List[dict]:
        pass

    @abstractmethod
    async def crawl_component_list(self, category: str, page: int = 1) -> List[dict]:
        pass
