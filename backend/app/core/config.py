from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PC Build Advisor"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pc_advisor"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # LLM — 기본 프로바이더: openai
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""          # 선택사항 (fallback 용도)
    LLM_PROVIDER: str = "openai"         # openai | claude
    LLM_MODEL_ANALYSIS: str = "gpt-4o-mini"   # 요구사항 분석 (비용·성능 균형)
    LLM_MODEL_COMPLEX: str = "gpt-4o"         # 복잡한 추론 / 재시도 (최고 품질)
    LLM_DAILY_BUDGET_USD: float = 50.0

    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"

    # Cache TTL (seconds)
    CACHE_TTL_COMPONENT: int = 86400    # 24h
    CACHE_TTL_PRICE: int = 21600        # 6h
    CACHE_TTL_SESSION: int = 3600       # 1h
    CACHE_TTL_LLM: int = 3600           # 1h

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
