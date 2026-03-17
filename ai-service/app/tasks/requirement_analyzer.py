import json
import logging
from app.providers.provider_factory import get_provider
from app.schemas.analysis import AnalyzedRequirements, BudgetSchema, PreferencesSchema

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert PC hardware advisor. Your task is to analyze user's natural language input and extract structured PC build requirements.

You MUST respond with valid JSON only (no markdown, no explanation, pure JSON).

User input will be in Korean. Understand context like:
- Game names: "배그" → PUBG, "로스트아크" → Lost Ark, "오버워치" → Overwatch 2, "사이버펑크" → Cyberpunk 2077
- Use cases: "게이밍" → gaming, "영상편집" → video_editing, "3D 렌더링" → 3d_rendering, "코딩" → programming
- Performance tiers: "고사양", "최고사양" → max, "적당한", "중간" → mid, "저사양", "저예산" → min
- Budget: "150만원" → {"max": 1500000, "currency": "KRW"}

Respond with exactly this JSON structure:
{
  "primary_use": "gaming",
  "specific_software_games": ["PUBG"],
  "performance_tier": "max",
  "budget": {"min": null, "max": 1500000, "currency": "KRW"},
  "preferences": {
    "color": null,
    "size": null,
    "brands": [],
    "features": [],
    "monitor_resolution": "1080p",
    "target_fps": 144
  },
  "priority": "performance",
  "additional_notes": ""
}"""


async def analyze_requirements(user_input: str, provider: str = "openai") -> AnalyzedRequirements:
    try:
        # role="analysis" → gpt-4o-mini (비용 효율)
        llm = get_provider(provider, role="analysis")
        raw = await llm.complete(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_input,
            max_tokens=1024,
            temperature=0.2,
        )
        data = json.loads(raw)
        budget_data = data.get("budget", {})
        pref_data = data.get("preferences", {})
        return AnalyzedRequirements(
            primary_use=data.get("primary_use", "gaming"),
            specific_software_games=data.get("specific_software_games", []),
            performance_tier=data.get("performance_tier", "mid"),
            budget=BudgetSchema(
                min=budget_data.get("min"),
                max=budget_data.get("max", 1500000),
                currency=budget_data.get("currency", "KRW"),
            ),
            preferences=PreferencesSchema(**pref_data),
            priority=data.get("priority", "balanced"),
            additional_notes=data.get("additional_notes", ""),
        )
    except Exception as e:
        logger.warning(f"gpt-4o-mini analysis failed: {e}. Retrying with gpt-4o...")
        try:
            # role="complex" → gpt-4o 로 재시도
            llm_complex = get_provider(provider, role="complex")
            raw = await llm_complex.complete(
                system_prompt=SYSTEM_PROMPT,
                user_message=user_input,
                max_tokens=1024,
                temperature=0.2,
            )
            data = json.loads(raw)
            budget_data = data.get("budget", {})
            pref_data = data.get("preferences", {})
            return AnalyzedRequirements(
                primary_use=data.get("primary_use", "gaming"),
                specific_software_games=data.get("specific_software_games", []),
                performance_tier=data.get("performance_tier", "mid"),
                budget=BudgetSchema(
                    min=budget_data.get("min"),
                    max=budget_data.get("max", 1500000),
                    currency=budget_data.get("currency", "KRW"),
                ),
                preferences=PreferencesSchema(**pref_data),
                priority=data.get("priority", "balanced"),
                additional_notes=data.get("additional_notes", ""),
            )
        except Exception as e2:
            logger.error(f"gpt-4o fallback also failed: {e2}. Using regex parser.")
            return _fallback_parse(user_input)


def _fallback_parse(user_input: str) -> AnalyzedRequirements:
    budget_max = 1500000
    for token in user_input.replace(",", "").split():
        if "만원" in token:
            try:
                amount = int(token.replace("만원", "")) * 10000
                budget_max = amount
            except ValueError:
                pass

    tier = "mid"
    if any(kw in user_input for kw in ["고사양", "최고", "최상"]):
        tier = "max"
    elif any(kw in user_input for kw in ["저사양", "저예산", "싸게"]):
        tier = "min"

    return AnalyzedRequirements(
        primary_use="gaming",
        performance_tier=tier,
        budget=BudgetSchema(max=budget_max),
    )
