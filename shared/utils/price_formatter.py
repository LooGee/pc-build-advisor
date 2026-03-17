def format_krw(price: int) -> str:
    """Format Korean Won price"""
    return f"₩{price:,}"


def format_usd(price: float) -> str:
    """Format USD price"""
    return f"${price:,.2f}"


def krw_to_usd(price_krw: int, exchange_rate: float = 1350.0) -> float:
    return round(price_krw / exchange_rate, 2)


def usd_to_krw(price_usd: float, exchange_rate: float = 1350.0) -> int:
    return int(price_usd * exchange_rate)
