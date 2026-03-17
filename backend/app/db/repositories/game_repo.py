from sqlalchemy import select

from app.db.repositories.base import BaseRepository
from app.models.game_software import GameRequirement, SoftwareRequirement


class GameRepository(BaseRepository[GameRequirement]):
    def __init__(self, db):
        super().__init__(db, GameRequirement)

    async def list_games(self) -> list:
        result = await self.db.execute(select(GameRequirement))
        games = result.scalars().all()
        return [
            {
                "id": str(g.id),
                "name": g.game_name,
                "aliases": g.aliases.split(",") if g.aliases else [],
                "genre": g.genre,
                "min_requirements": {
                    "cpu_benchmark": g.min_cpu_benchmark_multi,
                    "gpu_benchmark": g.min_gpu_benchmark,
                    "ram_gb": g.min_ram_gb,
                },
                "recommended_requirements": {
                    "cpu_benchmark": g.rec_cpu_benchmark_multi,
                    "gpu_benchmark": g.rec_gpu_benchmark,
                    "ram_gb": g.rec_ram_gb,
                },
            }
            for g in games
        ]

    async def list_software(self) -> list:
        result = await self.db.execute(select(SoftwareRequirement))
        items = result.scalars().all()
        return [{"id": str(s.id), "name": s.software_name, "category": s.category} for s in items]

    async def find_game_by_name(self, name: str) -> GameRequirement | None:
        result = await self.db.execute(
            select(GameRequirement).where(GameRequirement.game_name.ilike(f"%{name}%"))
        )
        return result.scalar_one_or_none()
