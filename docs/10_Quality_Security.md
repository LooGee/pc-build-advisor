# PC Build Advisor - 품질, 보안 및 로드맵

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 11. 구현 로드맵

### Phase 1 (2주): 기초 인프라
- ✅ PostgreSQL 스키마 설계 및 마이그레이션
- ✅ FastAPI 프로젝트 구조 설정
- ✅ Redis 설정 및 캐시 레이어
- ✅ 다나와 기본 크롤러 구현 (HTML 파싱)
- ✅ 부품 조회 API (GET /components)
- ✅ 호환성 규칙 DB 저장
- ✅ 테스트 및 문서화

### Phase 2 (2주): AI 및 견적 생성
- ✅ Claude API 통합
- ✅ 자연어 요구사항 분석 (LLM 서비스)
- ✅ 견적 생성 엔진 (3단계)
- ✅ 호환성 검사 엔진
- ✅ Game/Software Requirements DB
- ✅ POST /quotes/generate 엔드포인트
- ✅ 성능 예측 모듈

### Phase 3 (2주): 프론트엔드 및 추가 크롤러
- ✅ Next.js 프로젝트 초기화 (App Router)
- ✅ 메인 페이지 UI (채팅 인터페이스)
- ✅ 견적 결과 페이지 (3단계 탭)
- ✅ 부품 교체 UI
- ✅ 가격 비교 차트
- ✅ 추가 크롤러 (컴퓨존, 쿠팡, PCPartPicker)
- ✅ Celery 작업 스케줄링

### Phase 4 (1주): 테스트 및 배포
- ✅ E2E 테스트 (Playwright)
- ✅ 유닛 테스트 (pytest)
- ✅ 성능 최적화 (DB 인덱스, 캐싱)
- ✅ Docker 배포 설정
- ✅ 모니터링 (Prometheus + Grafana)
- ✅ 문서화 완성

---

## 12. 기술적 도전 과제 및 해결 방안

### 12.1 크롤링 차단 (Blocking)

**문제**
- 다나와, 쿠팡 등 anti-bot 기술 적용
- CloudFlare, WAF 우회 필요

**해결 방안**
```python
# Rate Limiting
CRAWL_DELAYS = {
    'danawa': 3,  # 3초 간격
    'compuzone': 2,
    'coupang': 5,  # 더 보수적
    'pcpartpicker': 2
}

# User-Agent 로테이션
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    # ... 20+ 더 추가
]

# Proxy Rotation (선택사항)
PROXIES = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    # ...
]

# Playwright로 JavaScript 렌더링
await page.set_extra_http_headers({
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'
})
```

### 12.2 가격 데이터 일관성

**문제**
- 사이트별 가격 차이 (같은 부품, 다른 가격)
- 정가와 할인가 혼재
- 배송료 포함 여부 불명확

**해결 방안**
```python
# 정규화된 가격 저장
class NormalizedPrice(Base):
    # 가격 + 배송료
    total_price_krw = Column(Integer)  # 사용자가 실제 지불할 가격

    # 가격 변화 추적
    price_history = relationship("PriceHistory")

    # 신뢰도 점수
    confidence_score = Column(Float)  # 0.0 ~ 1.0
    # 신뢰도 = (평가 수 + 리뷰 긍정도 + 판매기간) / 100

# 이상치 감지
def detect_price_anomaly(new_price, historical_prices):
    """
    과거 30일 평균에서 50% 이상 차이 → 경고
    """
    avg = np.mean(historical_prices[-30:])
    deviation = abs(new_price - avg) / avg
    return deviation > 0.5
```

### 12.3 LLM 비용 최적화

**문제**
- Claude API 고비용 (프롬프트 비용 발생)
- 사용량 급증 시 비용 폭발

**해결 방안**
```python
# 1. 프롬프트 캐싱
CACHED_REQUIREMENTS = {
    "배그": {
        "primary_use": "gaming",
        "specific_software": ["PUBG"],
        "performance_tier": "max",
        # ...
    },
    # 자주 나오는 요구사항 미리 저장
}

# 2. 입력값 해싱으로 캐시
cache_key = hashlib.sha256(user_input.encode()).hexdigest()
cached = redis_client.get(f"llm_analysis:{cache_key}")

# 3. GPT-4o Mini 또는 Claude 3.5 Haiku로 간단한 요청 처리
if simple_query(user_input):
    use_model = "claude-3-5-haiku"  # 더 저렴
else:
    use_model = "claude-3-5-sonnet"

# 4. Fallback 전략
try:
    result = await analyze_with_claude(user_input)
except RateLimitError:
    result = await analyze_with_gpt4(user_input)  # 대안으로 전환
```

### 12.4 부품 DB 자동 업데이트

**문제**
- 신규 출시 부품 자동 감지 어려움
- 구식 부품 제거 시점 결정

**해결 방안**
```python
# 신규 부품 감지
@shared_task
def discover_new_components():
    """
    각 사이트의 신규 부품 감지
    """
    danawa_new = danawa_crawler.get_new_products()

    for product in danawa_new:
        if not product_exists(product['model']):
            # 신규 부품 추가
            add_component(product)

            # 자동 스펙 추출 (LLM 또는 ONNX 모델)
            specs = extract_specs_from_description(product['description'])
            update_component_specs(product['id'], specs)

# 부품 라이프사이클 관리
class ComponentLifecycle:
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISCONTINUED = "discontinued"

    # 6개월 동안 판매처 없음 → 단종 가능성
    # 2년 동안 구매량 0 → 단종 처리
```

---

## 13. 성능 최적화 전략

### 13.1 데이터베이스 최적화
```sql
-- 자주 사용되는 조인 최적화
CREATE INDEX idx_cpu_benchmark ON cpus(cinebench_r23_multi_core);
CREATE INDEX idx_gpu_benchmark ON gpus(3dmark_timespy_score);

-- 가격 조회 고속화
CREATE INDEX idx_prices_component_source ON prices(component_id, source);

-- 캐시 워밍
SELECT * FROM components WHERE is_active = true;  -- 메모리에 로드
```

### 13.2 캐싱 전략
```python
# 3-Tier 캐싱
# L1: Redis (부품 정보, 가격) - TTL 6시간
# L2: Application Memory (자주 조회하는 부품) - TTL 1시간
# L3: Database (원본 데이터)

CACHE_TIERS = {
    "components": {"l1_ttl": 86400, "l2_ttl": 3600},  # 24시간, 1시간
    "prices": {"l1_ttl": 21600, "l2_ttl": 1800},      # 6시간, 30분
    "compatibility_rules": {"l1_ttl": 604800},        # 7일
}
```

### 13.3 API 응답 최적화
```python
# 1. 부분 응답 (Partial Response)
GET /quotes/12345?fields=components,total_price

# 2. 페이징
GET /components?page=1&limit=20

# 3. 응답 압축 (gzip)
@app.middleware("http")
async def gzip_middleware(request, call_next):
    response = await call_next(request)
    if "gzip" in request.headers.get("accept-encoding", ""):
        response.headers["content-encoding"] = "gzip"
```

---

## 14. 모니터링 및 로깅

### 14.1 주요 메트릭
```
• API 응답 시간 (평균, p95, p99)
• 크롤링 성공률 (사이트별)
• 견적 생성 성공률
• LLM API 비용 추적
• DB 쿼리 성능
• 캐시 히트율
```

### 14.2 ELK 스택 설정
```yaml
# docker-compose.yml에 추가
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
```

---

## 15. 보안 고려사항

### 15.1 API 보안
```python
# 1. Rate Limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/quotes/generate")
@limiter.limit("10/minute")
async def generate_quote(request):
    pass

# 2. CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 3. API Key / JWT
@app.post("/quotes/generate")
async def generate_quote(
    request: QuoteRequest,
    api_key: str = Header(None)
):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401)
```

### 15.2 데이터 보호
- 사용자 입력 sanitization (SQL injection 방지)
- 민감 정보 암호화 (PII, 결제정보)
- HTTPS 강제

---

## 21. 종합 점검 체크리스트

### 21.1 기능 완성도 체크

| 기능 | 상태 | 세부 사항 |
|------|------|-----------|
| 자연어 입력 분석 | ✅ 설계 완료 | Claude + GPT 이중 지원, 캐싱 |
| 3단계 견적 생성 | ✅ 설계 완료 | min/balanced/max 구조 |
| 호환성 검사 엔진 | ✅ 설계 완료 | 18개 규칙 + 상세 오류 메시지 |
| 브랜드 선택 기능 | ✅ 설계 완료 (v2) | strict/non-strict 모드 |
| 호환 불가 상세 오류 | ✅ 설계 완료 (v2) | 카탈로그 기반 한국어 메시지 + 대안 제시 |
| 예산 이슈 알림 | ✅ 설계 완료 (v2) | 초과/부족/불균형/실현불가 |
| LLM 모델 역할별 분리 | ✅ 설계 완료 (v2) | 7가지 역할별 최적 모델, 59% 비용 절감 |
| 구매 링크 안내 | ✅ 설계 완료 (v2) | 부품별 사이트 비교 + 최적 구매 전략 |
| 실시간 가격 크롤링 | ✅ 설계 완료 | 다나와/컴퓨존/쿠팡/PCPartPicker |
| 가격 이력 추적 | ✅ 설계 완료 | price_history 테이블 |
| 부품 교체 기능 | ✅ 설계 완료 | 교체 시 자동 호환성 재검사 |
| 재고 확인 | ✅ 설계 완료 | 품절/재고 상태 표시 |
| 성능 예측 | ✅ 설계 완료 | 벤치마크 기반 FPS 추정 |

### 21.2 아키텍처 점검

| 항목 | 상태 | 비고 |
|------|------|------|
| 프론트/백 분리 | ✅ | Next.js + FastAPI |
| DB 정규화 | ✅ | 16개 테이블, 적절한 인덱스 |
| 캐시 전략 | ✅ | Redis 3-tier, TTL 설정 |
| API 설계 | ✅ | RESTful, Pydantic 스키마 |
| 보안 | ✅ | Rate limit, CORS, JWT |
| 모니터링 | ✅ | Prometheus + Grafana + ELK |
| 배포 | ✅ | Docker Compose |
| 테스트 | ✅ | pytest + Playwright E2E |

### 21.3 리스크 및 대응

| 리스크 | 영향 | 확률 | 대응 |
|--------|------|------|------|
| 크롤링 차단 | 높음 | 높음 | Proxy 풀, Rate limit 준수, Headless 브라우저 |
| LLM API 장애 | 높음 | 낮음 | 이중 LLM 지원 (Claude ↔ GPT Fallback) |
| 가격 데이터 부정확 | 중간 | 중간 | 이상치 감지, 주기적 검증, 마지막 확인 시간 표시 |
| 호환성 규칙 누락 | 높음 | 중간 | 커뮤니티 피드백, 정기 규칙 업데이트 |
| 부품 DB 노후화 | 중간 | 높음 | 자동 신규 부품 감지, LLM 기반 스펙 추출 |
| 비용 초과 (LLM) | 중간 | 중간 | 역할별 모델 분리, 캐싱, 일일 예산 제한 |

---

## 22. 코드 주석 및 문서화 표준

### 22.1 Python (Backend / AI Service / Crawler)

```python
# ============================================================================
# 파일 헤더 주석 (모든 .py 파일 필수)
# ============================================================================
"""
quote_engine.py - 3단계 견적 생성 엔진

사용자의 분석된 요구사항(AnalyzedRequirements)을 입력받아
최소(Minimum), 균형(Balanced), 최대(Maximum) 3가지 PC 견적을 생성합니다.

주요 로직:
    1. 요구사항에서 필요 벤치마크 점수 산출
    2. 예산 범위별 부품 후보군 필터링
    3. 호환성 검사를 통과하는 조합 생성
    4. 가격 최적화 적용

Dependencies:
    - CompatibilityChecker: 부품 간 호환성 검증
    - PriceService: 실시간 가격 조회
    - BenchmarkService: 성능 벤치마크 매핑

Author: PC Build Advisor Team
Created: 2026-03-17
Updated: 2026-03-17
"""


# ============================================================================
# 클래스 주석
# ============================================================================
class QuoteEngine:
    """
    3단계 PC 견적 생성 엔진.

    사용자의 자연어 요구사항을 분석한 결과를 기반으로
    최소/균형/최대 3가지 PC 빌드를 자동으로 구성합니다.

    Attributes:
        db (AsyncSession): 데이터베이스 비동기 세션
        compatibility_checker (CompatibilityChecker): 호환성 검증 인스턴스
        price_service (PriceService): 가격 비교 서비스
        benchmark_service (BenchmarkService): 벤치마크 조회 서비스

    Example:
        >>> engine = QuoteEngine(db, checker, price_svc, bench_svc)
        >>> quotes = await engine.generate_quotes(requirements)
        >>> len(quotes)  # 항상 3개 (min, balanced, max)
        3
    """


# ============================================================================
# 메서드 주석
# ============================================================================
async def generate_quotes(
    self,
    requirements: AnalyzedRequirements,
    brand_preferences: Optional[BrandPreference] = None
) -> List[Quote]:
    """
    분석된 요구사항을 기반으로 3단계 견적을 생성합니다.

    Args:
        requirements: LLM이 분석한 사용자 요구사항.
            - primary_use: 주 용도 (gaming, workstation 등)
            - budget: 예산 범위 {min, max, currency}
            - performance_tier: 성능 등급 (min/mid/max)
        brand_preferences: 사용자 브랜드 선호도 (선택사항).
            - None이면 가성비 기준 자동 선택

    Returns:
        List[Quote]: 3개의 견적 리스트
            - [0] minimum: 최소 요구사항 충족
            - [1] balanced: 가성비 최적화
            - [2] maximum: 최고 성능 (예산 내)

    Raises:
        BudgetTooLowError: 예산이 최소 견적 구성에도 부족한 경우
        NoComponentsFoundError: 조건에 맞는 부품이 없는 경우
        CompatibilityError: 유효한 호환 조합을 찾을 수 없는 경우

    Notes:
        - 각 견적은 호환성 검사를 통과한 것만 반환됩니다
        - 가격은 호출 시점의 캐시된 최저가 기준입니다 (TTL 6시간)
        - 브랜드 strict 모드에서 부품을 찾지 못하면 BrandNotAvailableError 발생
    """


# ============================================================================
# 인라인 주석 (복잡한 비즈니스 로직에만)
# ============================================================================
# GPU 예산 비율: 게이밍 PC는 전체 예산의 35~45%를 GPU에 할당
# 참고: https://www.logicalincrements.com/
gpu_budget_ratio = 0.40 if requirements.primary_use == "gaming" else 0.25

# PSU 여유 계산: 총 TDP의 1.2배 이상 필요 (안정성 마진 20%)
# 이유: 순간 부스트 시 TDP보다 높은 전력을 소비할 수 있음
recommended_psu = int((cpu_tdp + gpu_tdp + 100) * 1.2)
```

### 22.2 TypeScript (Frontend)

```typescript
// ============================================================================
// 파일 헤더 주석 (모든 .ts/.tsx 파일 필수)
// ============================================================================
/**
 * QuoteTabs.tsx - 3단계 견적 탭 컴포넌트
 *
 * 최소/균형/최대 3가지 견적을 탭으로 전환하며 표시합니다.
 * 각 탭에는 부품 목록, 가격, 호환성 상태, 구매 링크가 포함됩니다.
 *
 * @module components/quote
 * @requires QuoteCard - 개별 견적 카드
 * @requires CompatibilityBadge - 호환성 상태 배지
 */


// ============================================================================
// 컴포넌트 주석
// ============================================================================
/**
 * 3단계 견적을 탭으로 표시하는 메인 컴포넌트.
 *
 * @param quotes - 3개의 견적 배열 [minimum, balanced, maximum]
 * @param onComponentChange - 부품 교체 시 호출되는 콜백
 * @param activeTier - 현재 활성화된 탭 (default: "balanced")
 *
 * @example
 * ```tsx
 * <QuoteTabs
 *   quotes={quoteData.quotes}
 *   onComponentChange={handleComponentSwap}
 *   activeTier="balanced"
 * />
 * ```
 */
interface QuoteTabsProps {
  /** 3개의 견적 (최소/균형/최대) */
  quotes: Quote[];
  /** 부품 교체 콜백 (category, oldId, newId) */
  onComponentChange: (category: string, oldId: string, newId: string) => void;
  /** 초기 활성 탭 */
  activeTier?: "minimum" | "balanced" | "maximum";
}


// ============================================================================
// 훅 주석
// ============================================================================
/**
 * 견적 생성 요청을 관리하는 커스텀 훅.
 *
 * 자연어 입력을 서버에 전송하고, 스트리밍 응답을 처리합니다.
 * 로딩 상태, 에러 핸들링, 재시도 로직을 포함합니다.
 *
 * @returns {Object} 견적 생성 상태 및 함수
 * @returns {Function} generateQuote - 견적 생성 요청 함수
 * @returns {Quote[] | null} quotes - 생성된 견적 (3개)
 * @returns {boolean} isLoading - 로딩 상태
 * @returns {string | null} error - 에러 메시지
 *
 * @example
 * ```tsx
 * const { generateQuote, quotes, isLoading, error } = useQuoteGeneration();
 * await generateQuote("배그를 고사양으로 돌리고 싶어요");
 * ```
 */
```

### 22.3 주석 원칙

| 원칙 | 설명 | 예시 |
|------|------|------|
| **WHY, not WHAT** | 코드가 "무엇"을 하는지가 아닌 "왜" 하는지 설명 | `# PSU 20% 여유: 부스트 시 순간 전력 급증 대비` |
| **파일 헤더 필수** | 모든 파일에 목적, 의존성, 작성자 기록 | docstring 또는 JSDoc |
| **복잡한 로직만** | 자명한 코드에는 주석 금지 | `price = 1000  # 가격을 1000으로 설정` ← 금지 |
| **TODO 태그** | 미완성 부분에 `# TODO(이름): 설명` 형식 | `# TODO(kyungshin): 쿠팡 크롤러 동적 대기 개선` |
| **FIXME 태그** | 알려진 버그에 `# FIXME: 설명` 형식 | `# FIXME: 다나와 셀렉터 변경 시 파싱 실패` |
| **한국어 허용** | 비즈니스 로직 주석은 한국어 OK | `# 게이밍인데 GPU 비중이 25% 미만이면 경고` |

---

## 결론

이 문서는 PC Build Advisor의 전체 시스템 아키텍처를 다룹니다. v2 업데이트에서는 다음 6가지 핵심 보강이 이루어졌습니다:

1. **브랜드 선택 기능**: 사용자가 부품별 제조사/시리즈를 지정하고, strict 모드로 해당 브랜드만 선택하거나 우선순위만 부여 가능
2. **상세 호환 불가 오류**: 15개 이상의 오류 유형별 한국어 메시지, 기술적 설명, 해결 방법, 대안 부품까지 제공
3. **예산 이슈 알림**: 초과/부족/불균형/실현불가 4가지 유형의 예산 문제를 사전 감지하고 구체적 해결 방안 제시
4. **LLM 역할별 모델 분리**: 7가지 역할에 맞는 모델 배치로 월 59% 비용 절감 (₩2,685,000 → ₩1,093,500)
5. **구매 링크 시스템**: 부품별 4개 사이트 가격 비교 + 최적 구매 전략 + 링크 유효성 검증
6. **종합 점검**: 13개 기능 항목, 8개 아키텍처 항목, 6개 리스크 대응 확인 완료

각 섹션은 독립적으로 개발 가능하며, Phase별 로드맵을 따라 구현할 수 있습니다.

**핵심 성공 요소**
1. 정확한 호환성 검증 + 상세한 한국어 오류 메시지
2. 빠른 API 응답 (<2초) + 역할별 LLM 최적화
3. 신뢰할 수 있는 가격 정보 + 직접 구매 링크
4. 사용자 친화적 UI/UX (브랜드 선택, 예산 알림)
5. 지속적인 크롤링과 데이터 업데이트
7. **초절약 플랜 (v4)**: DeepSeek V3.2 + Serverless 전환으로 월 ₩264,000 달성 (기존 대비 82% 절감). 개발 단계는 ₩20,000/월로 시작 가능
