from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.repositories.game_repo import GameRepository

router = APIRouter()


@router.get("/games")
async def list_games(db: AsyncSession = Depends(get_db)):
    repo = GameRepository(db)
    return await repo.list_games()


@router.get("/software")
async def list_software(db: AsyncSession = Depends(get_db)):
    repo = GameRepository(db)
    return await repo.list_software()
