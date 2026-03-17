import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)


async def write_prices(session: AsyncSession, prices: List[dict]) -> int:
    """DB에 가격 데이터 upsert"""
    from datetime import datetime
    written = 0
    for price_data in prices:
        if not price_data.get("price_krw") or not price_data.get("component_id"):
            continue
        try:
            # Upsert price record
            stmt = """
                INSERT INTO prices (id, component_id, source, price_krw, product_url, product_name, in_stock, last_checked, created_at, updated_at)
                VALUES (gen_random_uuid(), :component_id, :source, :price_krw, :product_url, :product_name, :in_stock, NOW(), NOW(), NOW())
                ON CONFLICT (component_id, source) DO UPDATE SET
                    price_krw = EXCLUDED.price_krw,
                    product_url = EXCLUDED.product_url,
                    in_stock = EXCLUDED.in_stock,
                    last_checked = NOW(),
                    updated_at = NOW()
            """
            from sqlalchemy import text
            await session.execute(
                text(stmt),
                {
                    "component_id": price_data["component_id"],
                    "source": price_data.get("source", "unknown"),
                    "price_krw": price_data["price_krw"],
                    "product_url": price_data.get("product_url"),
                    "product_name": price_data.get("product_name"),
                    "in_stock": price_data.get("in_stock", True),
                }
            )
            written += 1
        except Exception as e:
            logger.error(f"Failed to write price: {e}")
    await session.commit()
    return written
