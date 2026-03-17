# PC Build Advisor - AI/LLM 설계

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 7. LLM 기반 요구사항 분석 상세 설계

### 7.1 분석 프로세스 플로우

```
사용자 입력: "배틀그라운드 고사양으로 돌리고 싶어, 예산 150만원"
        ↓
[Step 1] 입력 전처리 (정규화, 오류 제거)
        ↓
[Step 2] LLM 분석 (Claude API)
        ├─ System Prompt: PC 빌드 전문가 역할 설정
        ├─ User Prompt: 요구사항 분석 요청
        └─ Response: JSON 구조화된 요구사항
        ↓
[Step 3] 응답 파싱 및 검증
        ├─ game_names 추출
        ├─ performance_tier 매핑 (min/mid/max)
        ├─ budget 파싱
        └─ preferences 추출
        ↓
[Step 4] Game Requirements 조회
        ├─ PUBG 벤치마크 조회: min_gpu_benchmark = 8500, rec_gpu_benchmark = 11000
        └─ 성능 목표 설정
        ↓
[Step 5] 견적 생성 엔진 호출
        ├─ Minimum: 벤치마크 8500 초과
        ├─ Balanced: 벤치마크 11000 초과 + 가성비
        └─ Maximum: 최고 성능 (예산 내)
        ↓
[Step 6] 호환성 검사 + 가격 조회
        ↓
[Step 7] 결과 렌더링 (UI에 JSON 전송)
```

### 7.2 Claude API 시스템 프롬프트

```
You are an expert PC hardware advisor. Your task is to analyze user's natural language input and extract structured PC build requirements.

You MUST respond with valid JSON (no markdown, pure JSON).

User input will be in Korean. You should understand context like:
- Game names: "배그" → PUBG, "로스트아크" → Lost Ark, "월드오브워크래프트" → World of Warcraft
- Use cases: "게이밍" → gaming, "영상편집" → video_editing, "3D 렌더링" → 3d_rendering, "코딩" → programming
- Performance tiers: "고사양", "최고사양", "무조건 최고" → max, "적당한" → mid, "저사양" → min
- Budget terms: "150만원" → {"max": 1500000, "currency": "KRW"}

Extract the following structure:
{
  "primary_use": "gaming" | "workstation" | "office" | "streaming" | "development" | "mixed",
  "specific_software_games": ["PUBG", "Lost Ark", ...],
  "performance_tier": "min" | "mid" | "max",
  "budget": {
    "min": 500000 | null,
    "max": 2000000,
    "currency": "KRW" | "USD"
  },
  "preferences": {
    "color": "Black" | "White" | null,
    "size": "SFF" | "Mini Tower" | "Mid Tower" | "Full Tower" | null,
    "brands": ["Intel", "NVIDIA", ...] | [],
    "features": ["quiet", "RGB", "portable", ...] | [],
    "monitor_resolution": "1080p" | "1440p" | "4K" | null,
    "target_fps": 60 | 144 | 240 | null
  },
  "priority": "performance" | "value" | "aesthetics" | "quiet" | "balanced",
  "additional_notes": "string"
}
```

### 7.3 Claude API 호출 (Python)

```python
# backend/app/services/llm_service.py

import anthropic
import json
from typing import Dict, Any
from app.schemas import AnalyzedRequirements
import redis

class LLMService:
    def __init__(self, api_key: str, redis_client: redis.Redis):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.redis = redis_client
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_requirements(
        self,
        user_input: str
    ) -> AnalyzedRequirements:
        """자연어 요구사항 분석"""

        # 캐시 확인
        cache_key = f"llm_analysis:{hash(user_input)}"
        cached = await self.redis.get(cache_key)
        if cached:
            return AnalyzedRequirements(**json.loads(cached))

        system_prompt = """You are an expert PC hardware advisor...
        [위의 시스템 프롬프트 전문 포함]
        """

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        response_text = message.content[0].text
        analyzed = json.loads(response_text)

        # 캐시에 저장 (1시간)
        await self.redis.setex(
            cache_key,
            3600,
            json.dumps(analyzed)
        )

        return AnalyzedRequirements(**analyzed)

    async def analyze_with_gpt4(
        self,
        user_input: str
    ) -> AnalyzedRequirements:
        """OpenAI GPT-4 Fallback"""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "[시스템 프롬프트]"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        analyzed = json.loads(response.choices[0].message.content)
        return AnalyzedRequirements(**analyzed)
```

### 7.4 게임 벤치마크 매핑

```python
# backend/app/services/game_mapper.py

GAME_NAME_MAPPING = {
    # 정확한 이름
    "PUBG": "PlayerUnknown's Battlegrounds",
    "배그": "PlayerUnknown's Battlegrounds",
    "배틀그라운드": "PlayerUnknown's Battlegrounds",

    # 로스트아크
    "Lost Ark": "Lost Ark",
    "로스트아크": "Lost Ark",

    # 월드오브워크래프트
    "WoW": "World of Warcraft",
    "와우": "World of Warcraft",
    "월드오브워크래프트": "World of Warcraft",

    # 오버워치 2
    "OW2": "Overwatch 2",
    "오버워치": "Overwatch 2",
    "오버워치2": "Overwatch 2",

    # 스팀 게임
    "Baldur's Gate 3": "Baldur's Gate 3",
    "발더스게이트3": "Baldur's Gate 3",

    # 추가 매핑...
}

async def normalize_game_names(game_list: List[str]) -> List[str]:
    """자연어 게임명을 정규화"""
    normalized = []
    for game in game_list:
        normalized_name = GAME_NAME_MAPPING.get(
            game.strip(),
            game.strip()
        )
        normalized.append(normalized_name)
    return normalized
```

---

## 19. LLM 모델 역할별 분리 전략

### 19.1 모델 티어 분류

| 역할 | 모델 | 비용 | 이유 |
|------|------|------|------|
| **자연어 요구사항 분석** | Claude Sonnet 4 / GPT-4o | 중간 | 한국어 이해 + 구조화된 JSON 추출 필요 |
| **게임/소프트웨어 매핑** | Claude Haiku 4.5 / GPT-4o-mini | 저가 | 단순 키워드 매칭, 사전 정의 매핑 테이블 활용 |
| **견적 최적화 추천** | Claude Sonnet 4 / GPT-4o | 중간 | 부품 간 가성비 분석, 예산 최적화 |
| **호환성 설명 생성** | Claude Haiku 4.5 / GPT-4o-mini | 저가 | 템플릿 기반 메시지 생성, 복잡한 추론 불필요 |
| **사용자 후속 질문 응답** | Claude Sonnet 4 / GPT-4o | 중간 | 맥락 유지 대화, 자연스러운 응답 |
| **부품 스펙 자동 추출** (크롤링 후) | Claude Haiku 4.5 / GPT-4o-mini | 저가 | 정형화된 HTML에서 스펙 파싱 |
| **복잡한 비교 분석** (사용자 요청 시) | Claude Opus 4 / GPT-4o | 고가 | 깊은 분석, 전문적 설명 필요 시에만 |

### 19.2 구현 코드

```python
# backend/app/services/llm_router.py

from enum import Enum
from typing import Optional

class LLMTask(str, Enum):
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    GAME_MAPPING = "game_mapping"
    QUOTE_OPTIMIZATION = "quote_optimization"
    COMPATIBILITY_EXPLANATION = "compatibility_explanation"
    USER_FOLLOWUP = "user_followup"
    SPEC_EXTRACTION = "spec_extraction"
    DEEP_ANALYSIS = "deep_analysis"

class LLMModelConfig:
    """역할별 LLM 모델 라우팅"""

    MODEL_ROUTING = {
        "claude": {
            LLMTask.REQUIREMENT_ANALYSIS: {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "temperature": 0.2,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
            },
            LLMTask.GAME_MAPPING: {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 512,
                "temperature": 0.0,
                "cost_per_1k_input": 0.0008,
                "cost_per_1k_output": 0.004,
            },
            LLMTask.QUOTE_OPTIMIZATION: {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2048,
                "temperature": 0.3,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
            },
            LLMTask.COMPATIBILITY_EXPLANATION: {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 512,
                "temperature": 0.1,
                "cost_per_1k_input": 0.0008,
                "cost_per_1k_output": 0.004,
            },
            LLMTask.USER_FOLLOWUP: {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2048,
                "temperature": 0.5,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015,
            },
            LLMTask.SPEC_EXTRACTION: {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1024,
                "temperature": 0.0,
                "cost_per_1k_input": 0.0008,
                "cost_per_1k_output": 0.004,
            },
            LLMTask.DEEP_ANALYSIS: {
                "model": "claude-opus-4-20250514",
                "max_tokens": 4096,
                "temperature": 0.4,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075,
            },
        },
        "openai": {
            LLMTask.REQUIREMENT_ANALYSIS: {
                "model": "gpt-4o",
                "max_tokens": 1024,
                "temperature": 0.2,
            },
            LLMTask.GAME_MAPPING: {
                "model": "gpt-4o-mini",
                "max_tokens": 512,
                "temperature": 0.0,
            },
            LLMTask.QUOTE_OPTIMIZATION: {
                "model": "gpt-4o",
                "max_tokens": 2048,
                "temperature": 0.3,
            },
            LLMTask.COMPATIBILITY_EXPLANATION: {
                "model": "gpt-4o-mini",
                "max_tokens": 512,
                "temperature": 0.1,
            },
            LLMTask.USER_FOLLOWUP: {
                "model": "gpt-4o",
                "max_tokens": 2048,
                "temperature": 0.5,
            },
            LLMTask.SPEC_EXTRACTION: {
                "model": "gpt-4o-mini",
                "max_tokens": 1024,
                "temperature": 0.0,
            },
            LLMTask.DEEP_ANALYSIS: {
                "model": "gpt-4o",
                "max_tokens": 4096,
                "temperature": 0.4,
            },
        }
    }

    @classmethod
    def get_model_config(cls, provider: str, task: LLMTask) -> dict:
        return cls.MODEL_ROUTING[provider][task]


class SmartLLMRouter:
    """비용 최적화를 위한 스마트 LLM 라우팅"""

    def __init__(self, primary_provider: str = "claude"):
        self.primary = primary_provider
        self.fallback = "openai" if primary_provider == "claude" else "claude"
        self.daily_cost_tracker = {}
        self.daily_budget_limit = 50.0

    async def route_request(
        self,
        task: LLMTask,
        input_text: str,
        force_provider: Optional[str] = None
    ) -> dict:
        """작업 유형에 따라 최적 모델로 라우팅"""

        provider = force_provider or self.primary

        if self._is_budget_exceeded():
            if task in [LLMTask.REQUIREMENT_ANALYSIS, LLMTask.QUOTE_OPTIMIZATION]:
                task = LLMTask.COMPATIBILITY_EXPLANATION

        config = LLMModelConfig.get_model_config(provider, task)

        cached = await self._check_cache(task, input_text)
        if cached:
            return cached

        try:
            result = await self._call_llm(provider, config, input_text)
            self._track_cost(config)
            await self._save_cache(task, input_text, result)
            return result
        except Exception:
            fallback_config = LLMModelConfig.get_model_config(self.fallback, task)
            return await self._call_llm(self.fallback, fallback_config, input_text)

    def _is_budget_exceeded(self) -> bool:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return self.daily_cost_tracker.get(today, 0) >= self.daily_budget_limit
```

### 19.3 비용 예측 시뮬레이션

```
시나리오: 일 1,000건 견적 요청

모델 통일 사용 (Claude Sonnet만):
- 요구사항 분석:   1,000 × $0.003 × 0.5K + 1,000 × $0.015 × 1K  = $16.5/일
- 게임 매핑:       1,000 × $0.003 × 0.3K + 1,000 × $0.015 × 0.5K = $8.4/일
- 견적 최적화:     1,000 × $0.003 × 1K   + 1,000 × $0.015 × 2K   = $33.0/일
- 호환성 설명:     1,000 × $0.003 × 0.3K + 1,000 × $0.015 × 0.5K = $8.4/일
→ 총: 약 $66.3/일 ≈ ₩89,500/일 ≈ ₩2,685,000/월

역할별 분리 사용 (Haiku + Sonnet + Opus 혼합):
- 요구사항 분석 (Sonnet):  1,000 × $0.003 × 0.5K + 1,000 × $0.015 × 1K  = $16.5/일
- 게임 매핑 (Haiku):       1,000 × $0.0008 × 0.3K + 1,000 × $0.004 × 0.5K = $2.24/일
- 견적 최적화 (Sonnet):    1,000 × $0.003 × 1K + 1,000 × $0.015 × 2K     = $33.0/일
- 호환성 설명 (Haiku):     1,000 × $0.0008 × 0.3K + 1,000 × $0.004 × 0.5K = $2.24/일
→ 총: 약 $53.98/일 ≈ ₩72,900/일 ≈ ₩2,187,000/월

+ 캐시 히트율 50% 적용 시: ≈ ₩1,093,500/월

절감액: 약 ₩1,591,500/월 (59% 절감)
```

---
