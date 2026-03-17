from fastapi import APIRouter
from app.api.v1 import quotes, components, prices, compatibility, games, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/v1", tags=["health"])
api_router.include_router(quotes.router, prefix="/v1/quotes", tags=["quotes"])
api_router.include_router(components.router, prefix="/v1/components", tags=["components"])
api_router.include_router(prices.router, prefix="/v1", tags=["prices"])
api_router.include_router(compatibility.router, prefix="/v1/compatibility", tags=["compatibility"])
api_router.include_router(games.router, prefix="/v1", tags=["games"])
