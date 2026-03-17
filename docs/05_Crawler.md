# PC Build Advisor - 크롤링 시스템

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 8. 크롤링 시스템 상세 설계

### 8.1 크롤러 아키텍처

```
Celery Beat (스케줄러)
    ├─ 6시간마다: price_update_task
    ├─ 1일마다: discover_new_components_task
    └─ 3시간마다: inventory_check_task
            ↓
Celery Worker Pool (5-10개 워커)
            ↓
Crawlee Orchestrator
    ├─ Danawa Crawler (Playwright)
    ├─ CompuZone Crawler (BeautifulSoup)
    ├─ Coupang Crawler (Playwright)
    └─ PCPartPicker Crawler (BeautifulSoup)
            ↓
Price DB + History Log
            ↓
Redis Cache (업데이트)
```

### 8.2 다나와 크롤러 (Playwright)

```python
# backend/app/crawlers/danawa.py

from crawlee.beaut_soup_crawler import BeautifulSoupCrawler
from crawlee.playwright_crawler import PlaywrightCrawler
from bs4 import BeautifulSoup
import json
from datetime import datetime

class DanawaCrawler:
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.base_url = "https://www.danawa.com"

    async def crawl_cpu_prices(self) -> List[Dict]:
        """다나와 CPU 가격 크롤링"""

        crawler = PlaywrightCrawler(
            max_requests_per_crawl=1000,
            max_crawl_depth=2,
            request_handler_timeout=300,
            use_session_pool=True
        )

        @crawler.on_page
        async def handle_page(context):
            page = context.page
            await page.wait_for_load_state("networkidle")

            # 다나와는 동적 렌더링이므로 Playwright 필요
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # CPU 제품 목록 파싱
            products = soup.select('div.list_prod')

            results = []
            for product in products:
                try:
                    name = product.select_one('a.prod_name').text.strip()
                    price_text = product.select_one('span.price').text.strip()
                    price = int(price_text.replace(',', '').replace('원', ''))
                    url = product.select_one('a.prod_name')['href']

                    # 제조사 및 모델 추출
                    brand, model = self._parse_cpu_name(name)

                    results.append({
                        'source': 'danawa',
                        'component_type': 'cpu',
                        'brand': brand,
                        'model': model,
                        'full_name': name,
                        'price_krw': price,
                        'url': f"{self.base_url}{url}",
                        'in_stock': True,
                        'crawled_at': datetime.now()
                    })
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue

            return results

        await crawler.run([f"{self.base_url}/cpu"])
        return results

    def _parse_cpu_name(self, name: str) -> tuple:
        """CPU 이름에서 브랜드와 모델 추출"""
        # "Intel Core i9-14900KS" → ("Intel", "Core i9-14900KS")
        if "Intel" in name:
            return "Intel", name.replace("Intel ", "").strip()
        elif "AMD" in name:
            return "AMD", name.replace("AMD ", "").strip()
        else:
            parts = name.split()
            return parts[0], " ".join(parts[1:])
```

### 8.3 Celery 작업 정의

```python
# backend/app/tasks/crawling_tasks.py

from celery import shared_task
from app.crawlers import *
from app.db.database import SessionLocal
import redis

redis_client = redis.Redis(host='redis', port=6379)

@shared_task(bind=True, max_retries=3)
def crawl_all_prices(self):
    """모든 사이트의 부품 가격 크롤링 (6시간마다)"""

    db = SessionLocal()

    try:
        danawa = DanawaCrawler(db, redis_client)
        compuzone = CompuZoneCrawler(db, redis_client)
        coupang = CoupangCrawler(db, redis_client)

        # 병렬 크롤링
        danawa_results = danawa.crawl_cpu_prices()
        compuzone_results = compuzone.crawl_gpu_prices()
        coupang_results = coupang.crawl_all_categories()

        # DB 저장
        all_results = [*danawa_results, *compuzone_results, *coupang_results]
        _save_prices_to_db(db, all_results)

        return f"Crawled {len(all_results)} price records"

    except Exception as exc:
        # 재시도 (지수 백오프)
        self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()

def _save_prices_to_db(db, price_records):
    """가격 정보 DB 저장"""
    from app.models import Price, PriceHistory
    from datetime import datetime

    for record in price_records:
        # 기존 가격 조회
        existing = db.query(Price).filter(
            Price.component_id == record['component_id'],
            Price.source == record['source']
        ).first()

        if existing:
            # 가격 변화 감지
            if existing.price_krw != record['price_krw']:
                # 이력 기록
                history = PriceHistory(
                    component_id=record['component_id'],
                    source=record['source'],
                    price_krw=existing.price_krw,
                    recorded_at=datetime.now()
                )
                db.add(history)

                # 기존 가격 업데이트
                existing.price_krw = record['price_krw']
                existing.updated_at = datetime.now()
        else:
            # 새로운 가격 기록
            price = Price(**record)
            db.add(price)

    db.commit()
```

---
