"""
Seed runner: loads component JSON files into the database.
Usage: python -m app.db.seeds.run_seeds
"""
import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.component import Component
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.motherboard import Motherboard
from app.models.ram import RAM
from app.models.storage import Storage
from app.models.psu import PSU
from app.models.case import Case
from app.models.cooler import Cooler
from app.models.price import Price
from app.models.game_software import GameRequirement

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDS_DIR = Path(__file__).parent

CATEGORY_MODEL_MAP = {
    "cpu": CPU,
    "gpu": GPU,
    "motherboard": Motherboard,
    "ram": RAM,
    "storage": Storage,
    "psu": PSU,
    "case": Case,
    "cooler": Cooler,
}

SEED_FILES = [
    ("cpu", "cpus.json"),
    ("gpu", "gpus.json"),
    ("motherboard", "motherboards.json"),
    ("ram", "rams.json"),
    ("storage", "storages.json"),
    ("psu", "psus.json"),
    ("case", "cases.json"),
    ("cooler", "coolers.json"),
    ("game", "game_requirements.json"),
]


async def seed_components(session: AsyncSession, category: str, items: list) -> int:
    model_class = CATEGORY_MODEL_MAP[category]
    count = 0

    for item in items:
        comp_data = item["component"]
        spec_data = item.get("spec", {})
        price_data = item.get("prices", [])

        # Check if component already exists
        existing = await session.execute(
            select(Component).where(
                Component.category == category,
                Component.brand == comp_data["brand"],
                Component.model == comp_data["model"],
            )
        )
        if existing.scalar_one_or_none():
            logger.info(f"  Skip (exists): {comp_data['brand']} {comp_data['model']}")
            continue

        # Insert Component
        comp_id = uuid.uuid4()
        comp = Component(
            id=comp_id,
            category=category,
            brand=comp_data["brand"],
            model=comp_data["model"],
            description=comp_data.get("description"),
            image_url=comp_data.get("image_url"),
            is_active=comp_data.get("is_active", True),
        )
        session.add(comp)

        # Insert spec row
        spec_obj = model_class(id=comp_id, **spec_data)
        session.add(spec_obj)

        # Insert prices
        for p in price_data:
            price = Price(
                id=uuid.uuid4(),
                component_id=comp_id,
                source=p.get("source", "danawa"),
                price_krw=p["price_krw"],
                in_stock=p.get("in_stock", True),
                product_url=p.get("product_url"),
                product_name=f"{comp_data['brand']} {comp_data['model']}",
                last_checked=datetime.utcnow(),
            )
            session.add(price)

        count += 1
        logger.info(f"  Added: {comp_data['brand']} {comp_data['model']}")

    return count


async def seed_games(session: AsyncSession, items: list) -> int:
    count = 0
    for item in items:
        existing = await session.execute(
            select(GameRequirement).where(GameRequirement.game_name == item["game_name"])
        )
        if existing.scalar_one_or_none():
            logger.info(f"  Skip (exists): {item['game_name']}")
            continue

        game = GameRequirement(id=uuid.uuid4(), **item)
        session.add(game)
        count += 1
        logger.info(f"  Added game: {item['game_name']}")
    return count


async def run():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            for category, filename in SEED_FILES:
                path = SEEDS_DIR / filename
                if not path.exists():
                    logger.warning(f"Seed file not found: {path}")
                    continue

                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                logger.info(f"\n[{category.upper()}] Seeding {len(data)} items from {filename}...")

                if category == "game":
                    count = await seed_games(session, data)
                else:
                    count = await seed_components(session, category, data)

                logger.info(f"  → Inserted {count} new records")

    await engine.dispose()
    logger.info("\nSeeding complete.")


if __name__ == "__main__":
    asyncio.run(run())
