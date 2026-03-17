from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.db.repositories.price_repo import PriceRepository

router = APIRouter()


@router.get("/components/{component_id}/prices")
async def get_component_prices(component_id: str, db: AsyncSession = Depends(get_db)):
    repo = PriceRepository(db)
    return await repo.get_prices_for_component(uuid.UUID(component_id))
