#!/bin/bash
set -e

echo "Seeding database..."

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed game requirements
docker-compose exec backend python -c "
import asyncio
import json
from app.db.database import AsyncSessionLocal, Base, engine
from app.models.game_software import GameRequirement

async def seed():
    async with AsyncSessionLocal() as session:
        with open('app/db/seeds/game_requirements.json') as f:
            games = json.load(f)
        for g in games:
            game = GameRequirement(**g)
            session.add(game)
        await session.commit()
        print(f'Seeded {len(games)} games')

asyncio.run(seed())
"

echo "Database seeding complete!"
