from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.events import startup_handler, shutdown_handler
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_handler()
    yield
    await shutdown_handler()


app = FastAPI(
    title="PC Build Advisor API",
    description="AI 기반 PC 견적 자동 추천 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)

# Exception handlers
register_exception_handlers(app)

# Routes
app.include_router(api_router, prefix="/api")
