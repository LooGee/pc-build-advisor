from sqlalchemy import select
from uuid import UUID

from app.db.repositories.base import BaseRepository
from app.models.price import Price
from app.models.component import Component


class PriceRepository(BaseRepository[Price]):
    def __init__(self, db):
        super().__init__(db, Price)

    async def get_prices_for_component(self, component_id: UUID) -> dict:
        comp = await self.db.get(Component, component_id)
        if not comp:
            return {}

        result = await self.db.execute(
            select(Price).where(Price.component_id == component_id)
        )
        prices = result.scalars().all()

        price_list = []
        for p in prices:
            price_list.append({
                "source": p.source,
                "price_krw": p.price_krw,
                "shipping_cost_krw": p.shipping_cost_krw or 0,
                "total_price_krw": p.total_price_krw,
                "in_stock": p.in_stock,
                "url": p.product_url,
                "rocket_delivery": p.rocket_delivery,
            })

        cheapest = min(price_list, key=lambda x: x["total_price_krw"]) if price_list else None

        return {
            "component_id": str(component_id),
            "brand": comp.brand,
            "model": comp.model,
            "prices": price_list,
            "average_price_krw": int(sum(p["price_krw"] for p in price_list) / len(price_list)) if price_list else None,
            "cheapest": cheapest,
        }
