from typing import List, Optional
import itertools


class ProxyPool:
    def __init__(self, proxies: List[str] = None):
        self._proxies = proxies or []
        self._cycle = itertools.cycle(self._proxies) if self._proxies else None

    def get_next(self) -> Optional[str]:
        if self._cycle:
            return next(self._cycle)
        return None

    @property
    def has_proxies(self) -> bool:
        return len(self._proxies) > 0


proxy_pool = ProxyPool()
