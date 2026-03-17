from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
from typing import List, Optional
from uuid import UUID

from app.db.repositories.base import BaseRepository
from app.models.component import Component
from app.models.price import Price
from app.schemas.component import ComponentFilter


class ComponentRepository(BaseRepository[Component]):
    def __init__(self, db):
        super().__init__(db, Component)

    async def list_with_prices(self, filters: ComponentFilter) -> dict:
        query = select(Component).where(Component.is_active == True)

        if filters.category:
            query = query.where(Component.category == filters.category)
        if filters.brand:
            query = query.where(Component.brand.ilike(f"%{filters.brand}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)
        result = await self.db.execute(query)
        components = result.scalars().all()

        items = []
        for comp in components:
            prices_result = await self.db.execute(
                select(Price).where(Price.component_id == comp.id, Price.in_stock == True)
            )
            prices = prices_result.scalars().all()

            price_list = [{"source": p.source, "price_krw": p.price_krw, "in_stock": p.in_stock} for p in prices]
            price_values = [p.price_krw for p in prices]

            items.append({
                "id": str(comp.id),
                "brand": comp.brand,
                "model": comp.model,
                "category": comp.category,
                "image_url": comp.image_url,
                "prices": price_list,
                "average_price_krw": int(sum(price_values) / len(price_values)) if price_values else None,
                "min_price_krw": min(price_values) if price_values else None,
                "max_price_krw": max(price_values) if price_values else None,
            })

        return {"total": total, "page": filters.page, "limit": filters.limit, "items": items}

    async def get_detail(self, component_id: UUID) -> Optional[dict]:
        comp = await self.db.get(Component, component_id)
        if not comp:
            return None
        return {"id": str(comp.id), "brand": comp.brand, "model": comp.model, "category": comp.category}

    async def find_by_category_and_specs(
        self, category: str, min_benchmark: Optional[int] = None, max_price: Optional[int] = None, limit: int = 10
    ) -> List[Component]:
        query = select(Component).where(
            and_(Component.category == category, Component.is_active == True)
        ).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
