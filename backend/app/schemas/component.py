from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid


class ComponentFilter(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    page: int = 1
    limit: int = 20


class PriceSummary(BaseModel):
    source: str
    price_krw: int
    in_stock: bool = True


class ComponentListItem(BaseModel):
    id: str
    brand: str
    model: str
    category: str
    image_url: Optional[str] = None
    specifications: Dict[str, Any] = {}
    prices: List[PriceSummary] = []
    average_price_krw: Optional[int] = None
    min_price_krw: Optional[int] = None
    max_price_krw: Optional[int] = None


class ComponentDetail(ComponentListItem):
    description: Optional[str] = None
    release_date: Optional[str] = None
