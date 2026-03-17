from sqlalchemy import select
from uuid import UUID
from typing import Optional

from app.db.repositories.base import BaseRepository
from app.models.quote import Quote


class QuoteRepository(BaseRepository[Quote]):
    def __init__(self, db):
        super().__init__(db, Quote)

    async def get_by_id(self, quote_id: UUID) -> Optional[Quote]:
        return await self.db.get(Quote, quote_id)
