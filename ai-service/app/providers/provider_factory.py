from app.providers.base_provider import BaseProvider
from app.providers.openai_provider import OpenAIProvider
from app.config import settings


# 역할별 모델 매핑
# - "analysis" : 한국어 NL → 구조화 JSON (비용·성능 균형)
# - "complex"  : 복잡한 추론 / 재시도 (최고 품질)
ROLE_MODELS = {
    "analysis": settings.LLM_MODEL_ANALYSIS,   # gpt-4o-mini
    "complex":  settings.LLM_MODEL_COMPLEX,    # gpt-4o
}


def get_provider(provider: str = None, task_model: str = None, role: str = None) -> BaseProvider:
    """
    provider: "openai" | "claude" (기본값: settings.LLM_PROVIDER = "openai")
    role:     "analysis" | "complex"  — role 지정 시 task_model 보다 우선
    task_model: 직접 모델명 지정 시 사용
    """
    p = provider or settings.LLM_PROVIDER

    # 모델 결정 우선순위: role > task_model > 기본값(gpt-4o-mini)
    if role and role in ROLE_MODELS:
        model = ROLE_MODELS[role]
    elif task_model:
        model = task_model
    else:
        model = settings.LLM_MODEL_ANALYSIS  # 기본: gpt-4o-mini

    # Claude fallback (ANTHROPIC_API_KEY 가 있을 때만 가능)
    if p == "claude" and settings.ANTHROPIC_API_KEY:
        try:
            from app.providers.claude_provider import ClaudeProvider
            claude_model = "claude-3-5-haiku-20241022" if role == "analysis" else "claude-sonnet-4-20250514"
            return ClaudeProvider(model=task_model or claude_model)
        except ImportError:
            pass  # anthropic 패키지 없으면 openai로 fall through

    return OpenAIProvider(model=model)
