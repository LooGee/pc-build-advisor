from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ─── 필수 ─────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ─── 선택 (fallback 용도 — 없어도 동작) ────────────────────────────
    ANTHROPIC_API_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379/1"

    # 기본 프로바이더: openai
    LLM_PROVIDER: str = "openai"

    # ─── 역할별 모델 설정 ─────────────────────────────────────────────
    # 한국어 자연어 → 구조화 JSON 추출 (비용·성능 균형)
    LLM_MODEL_ANALYSIS: str = "gpt-4o-mini"
    # 복잡한 추론 / 분석 실패 후 재시도용 (최고 품질)
    LLM_MODEL_COMPLEX: str = "gpt-4o"

    DAILY_BUDGET_USD: float = 50.0

    class Config:
        env_file = ".env"


settings = Settings()
