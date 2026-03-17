from typing import List, Optional


def detect_price_anomaly(new_price: int, historical_prices: List[int]) -> bool:
    """가격 이상 감지 (평균 대비 50% 이상 차이)"""
    if not historical_prices:
        return False
    avg = sum(historical_prices) / len(historical_prices)
    deviation = abs(new_price - avg) / avg
    return deviation > 0.5


def filter_anomalies(prices: List[dict], component_id: str) -> List[dict]:
    valid_prices = [p for p in prices if p.get("price_krw", 0) > 0]
    return valid_prices
