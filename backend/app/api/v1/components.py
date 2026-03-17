from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.db.repositories.component_repo import ComponentRepository
from app.schemas.component import ComponentFilter

router = APIRouter()


@router.get("")
async def list_components(
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = ComponentRepository(db)
    filters = ComponentFilter(
        category=category, brand=brand,
        min_price=min_price, max_price=max_price,
        page=page, limit=limit
    )
    return await repo.list_with_prices(filters)


@router.get("/{component_id}")
async def get_component(component_id: str, db: AsyncSession = Depends(get_db)):
    import uuid
    repo = ComponentRepository(db)
    return await repo.get_detail(uuid.UUID(component_id))
