from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class PriceUpdateEvent(BaseModel):
    """가격 업데이트 이벤트 (크롤러 → 백엔드)"""
    component_id: str
    source: str
    price_krw: int
    in_stock: bool
    product_url: Optional[str] = None
    timestamp: datetime = None

    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


class ComponentDiscoveredEvent(BaseModel):
    """새 부품 발견 이벤트"""
    source: str
    category: str
    brand: str
    model: str
    price_krw: int
    product_url: str
    raw_data: dict = {}


class QuoteGeneratedEvent(BaseModel):
    """견적 생성 완료 이벤트"""
    quote_id: str
    user_session_id: Optional[str] = None
    tier: str
    total_price_krw: int
    generation_time_ms: int
