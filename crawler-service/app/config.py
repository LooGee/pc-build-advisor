from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pc_advisor"
    REDIS_URL: str = "redis://localhost:6379/2"
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/3"

    # Rate limiting (seconds between requests)
    DANAWA_RATE_LIMIT: float = 3.0
    COMPUZONE_RATE_LIMIT: float = 5.0
    COUPANG_RATE_LIMIT: float = 4.0
    PCPARTPICKER_RATE_LIMIT: float = 2.0

    class Config:
        env_file = ".env"


settings = Settings()
