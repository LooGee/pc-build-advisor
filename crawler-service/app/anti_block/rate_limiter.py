import asyncio
import time
from typing import Dict

_last_request_time: Dict[str, float] = {}


async def wait_for_rate_limit(site: str, delay: float):
    last = _last_request_time.get(site, 0)
    elapsed = time.time() - last
    if elapsed < delay:
        await asyncio.sleep(delay - elapsed)
    _last_request_time[site] = time.time()
