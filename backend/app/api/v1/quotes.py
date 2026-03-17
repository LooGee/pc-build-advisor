from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import time
import uuid

from app.db.session import get_db
from app.schemas.quote import QuoteGenerateRequest, QuoteGenerateResponse, QuoteCustomizeRequest
from app.services.quote_engine import QuoteEngine
from app.services.compatibility.checker import CompatibilityChecker
from app.cache.cache_service import CacheService
from app.dependencies import get_cache_service, get_ai_client

router = APIRouter()


@router.post("/generate", response_model=QuoteGenerateResponse)
async def generate_quote(
    request: QuoteGenerateRequest,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
    ai_client=Depends(get_ai_client),
):
    start = time.time()
    engine = QuoteEngine(db, cache, ai_client)
    result = await engine.generate(request)
    result.quotes  # ensure populated
    elapsed_ms = int((time.time() - start) * 1000)
    return result


@router.get("/{quote_id}")
async def get_quote(quote_id: str, db: AsyncSession = Depends(get_db)):
    from app.db.repositories.quote_repo import QuoteRepository
    repo = QuoteRepository(db)
    quote = await repo.get_by_id(uuid.UUID(quote_id))
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return quote


@router.post("/{quote_id}/customize")
async def customize_quote(
    quote_id: str,
    request: QuoteCustomizeRequest,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
):
    from app.services.quote_engine import QuoteEngine
    engine = QuoteEngine(db, cache, None)
    result = await engine.customize(uuid.UUID(quote_id), request)
    return result
