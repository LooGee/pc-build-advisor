from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PriceDetail(BaseModel):
    source: str
    price_krw: int
    shipping_cost_krw: int = 0
    total_price_krw: int
    in_stock: bool = True
    url: Optional[str] = None
    updated_at: Optional[datetime] = None
    rocket_delivery: bool = False


class PriceComparisonResponse(BaseModel):
    component_id: str
    brand: str
    model: str
    prices: List[PriceDetail] = []
    average_price_krw: Optional[int] = None
    cheapest: Optional[dict] = None
