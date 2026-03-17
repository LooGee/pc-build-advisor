import re
from typing import Optional


def normalize_price(price: int, source: str) -> int:
    """가격 정규화 (이상 가격 필터링)"""
    if price < 1000 or price > 50_000_000:
        return 0
    return price


def normalize_product_name(name: str) -> str:
    """상품명 정규화"""
    name = re.sub(r"\s+", " ", name.strip())
    name = re.sub(r"\[.*?\]", "", name)  # Remove bracket notes
    return name.strip()


def normalize_component_data(raw: dict) -> dict:
    raw["price_krw"] = normalize_price(raw.get("price_krw", 0), raw.get("source", ""))
    raw["product_name"] = normalize_product_name(raw.get("product_name", ""))
    return raw
