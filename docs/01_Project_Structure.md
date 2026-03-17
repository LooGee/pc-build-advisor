# PC Build Advisor - 프로젝트 디렉토리 구조

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 4. 프로젝트 디렉토리 구조

```
pc-build-advisor/
│
├── ======================================
├── 📁 FRONTEND (Next.js 14+ App Router)
├── ======================================
├── frontend/
│   ├── app/                              # Next.js App Router 페이지
│   │   ├── layout.tsx                    # 루트 레이아웃 (공통 헤더/푸터)
│   │   ├── page.tsx                      # 메인 랜딩 페이지
│   │   ├── globals.css                   # 전역 스타일
│   │   ├── loading.tsx                   # 전역 로딩 UI
│   │   ├── error.tsx                     # 전역 에러 바운더리
│   │   ├── not-found.tsx                 # 404 페이지
│   │   │
│   │   ├── (chat)/                       # 견적 채팅 라우트 그룹
│   │   │   ├── layout.tsx                # 채팅 레이아웃
│   │   │   └── page.tsx                  # 자연어 입력 + 실시간 응답
│   │   │
│   │   ├── quotes/                       # 견적 관련 페이지
│   │   │   ├── page.tsx                  # 견적 목록 (내 견적 히스토리)
│   │   │   └── [id]/
│   │   │       ├── page.tsx              # 견적 상세 (3단계 탭)
│   │   │       ├── loading.tsx           # 견적 로딩 스켈레톤
│   │   │       └── customize/
│   │   │           └── page.tsx          # 부품 교체/커스터마이징
│   │   │
│   │   ├── components/                   # 부품 탐색 페이지
│   │   │   ├── page.tsx                  # 부품 카탈로그 (필터/정렬)
│   │   │   └── [id]/
│   │   │       └── page.tsx              # 부품 상세 (스펙+가격비교)
│   │   │
│   │   └── api/                          # BFF (Backend for Frontend)
│   │       ├── quotes/route.ts           # 견적 프록시 API
│   │       ├── components/route.ts       # 부품 프록시 API
│   │       └── health/route.ts           # 헬스체크
│   │
│   ├── components/                       # 재사용 가능한 UI 컴포넌트
│   │   ├── common/                       # 공통 컴포넌트 ─────────────────
│   │   │   ├── Header.tsx                #   사이트 헤더/네비게이션
│   │   │   ├── Footer.tsx                #   푸터
│   │   │   ├── Sidebar.tsx               #   사이드바 (필터 패널)
│   │   │   ├── Modal.tsx                 #   공통 모달
│   │   │   ├── Toast.tsx                 #   알림 토스트
│   │   │   ├── Badge.tsx                 #   상태 배지 (호환/경고/에러)
│   │   │   ├── Skeleton.tsx              #   로딩 스켈레톤
│   │   │   └── ErrorBoundary.tsx         #   에러 바운더리
│   │   │
│   │   ├── chat/                         # 채팅 관련 컴포넌트 ──────────
│   │   │   ├── ChatInput.tsx             #   자연어 입력 (자동완성)
│   │   │   ├── ChatBubble.tsx            #   대화 말풍선
│   │   │   ├── ChatHistory.tsx           #   대화 히스토리
│   │   │   └── SuggestedPrompts.tsx      #   추천 질문 칩
│   │   │
│   │   ├── quote/                        # 견적 관련 컴포넌트 ──────────
│   │   │   ├── QuoteTabs.tsx             #   3단계 탭 (최소/균형/최대)
│   │   │   ├── QuoteCard.tsx             #   개별 견적 카드
│   │   │   ├── QuoteSummary.tsx          #   견적 요약 (총가격/성능)
│   │   │   ├── QuoteComparison.tsx       #   3견적 나란히 비교
│   │   │   └── QuoteShareButton.tsx      #   견적 공유 버튼
│   │   │
│   │   ├── component/                    # 부품 관련 컴포넌트 ──────────
│   │   │   ├── ComponentCard.tsx         #   부품 카드 (이미지+스펙 요약)
│   │   │   ├── ComponentDetail.tsx       #   부품 상세 스펙 테이블
│   │   │   ├── ComponentSelector.tsx     #   부품 교체 드롭다운
│   │   │   ├── BrandFilter.tsx           #   브랜드 필터 UI
│   │   │   └── SpecificationTable.tsx    #   상세 스펙 표
│   │   │
│   │   ├── compatibility/                # 호환성 관련 컴포넌트 ────────
│   │   │   ├── CompatibilityBadge.tsx    #   호환성 상태 배지
│   │   │   ├── CompatibilityReport.tsx   #   전체 호환성 리포트
│   │   │   ├── IssueCard.tsx             #   개별 이슈 카드
│   │   │   └── AutoFixSuggestion.tsx     #   자동 수정 제안 UI
│   │   │
│   │   ├── price/                        # 가격 관련 컴포넌트 ──────────
│   │   │   ├── PriceComparison.tsx       #   사이트별 가격 비교 테이블
│   │   │   ├── PriceChart.tsx            #   가격 추이 차트 (Recharts)
│   │   │   ├── PurchaseLinks.tsx         #   구매 링크 카드
│   │   │   ├── OptimalStrategy.tsx       #   최적 구매 전략 표시
│   │   │   └── BudgetAlert.tsx           #   예산 초과/부족 알림
│   │   │
│   │   └── brand/                        # 브랜드 선택 컴포넌트 ────────
│   │       ├── BrandSelector.tsx         #   브랜드 선택 패널
│   │       ├── BrandChip.tsx             #   브랜드 칩 (선택 표시)
│   │       └── BrandPreference.tsx       #   strict/non-strict 토글
│   │
│   ├── hooks/                            # 커스텀 React 훅
│   │   ├── useQuoteGeneration.ts         # 견적 생성 요청/응답 관리
│   │   ├── useComponentSearch.ts         # 부품 검색 + 무한 스크롤
│   │   ├── usePriceComparison.ts         # 가격 비교 데이터
│   │   ├── useCompatibilityCheck.ts      # 실시간 호환성 체크
│   │   ├── useBrandPreference.ts         # 브랜드 선호도 상태
│   │   ├── useBudgetTracker.ts           # 예산 추적
│   │   └── useDebounce.ts               # 디바운스 유틸 훅
│   │
│   ├── stores/                           # 전역 상태 관리 (Zustand)
│   │   ├── quoteStore.ts                 # 견적 상태
│   │   ├── componentStore.ts             # 부품 선택 상태
│   │   ├── brandStore.ts                 # 브랜드 선호도 상태
│   │   └── uiStore.ts                    # UI 상태 (모달, 토스트 등)
│   │
│   ├── lib/                              # 유틸리티 및 설정
│   │   ├── api-client.ts                 # Axios 인스턴스 + 인터셉터
│   │   ├── types/                        # TypeScript 타입 정의
│   │   │   ├── quote.ts                  #   견적 관련 타입
│   │   │   ├── component.ts              #   부품 관련 타입
│   │   │   ├── price.ts                  #   가격 관련 타입
│   │   │   ├── compatibility.ts          #   호환성 관련 타입
│   │   │   └── api.ts                    #   API 요청/응답 타입
│   │   ├── constants.ts                  # 상수 (카테고리명, 사이트 정보 등)
│   │   ├── formatters.ts                 # 가격/날짜 포매팅 함수
│   │   └── validators.ts                 # 클라이언트 유효성 검사
│   │
│   ├── styles/                           # 스타일 관련
│   │   └── theme.ts                      # 테마 설정 (다크모드 등)
│   │
│   ├── public/                           # 정적 자산
│   │   ├── images/
│   │   │   ├── components/               # 부품 카테고리 아이콘
│   │   │   ├── logos/                    # 쇼핑몰 로고 (다나와/쿠팡 등)
│   │   │   └── hero/                    # 히어로 배너 이미지
│   │   ├── icons/                       # SVG 아이콘
│   │   └── fonts/                       # 웹 폰트
│   │
│   ├── __tests__/                        # 프론트엔드 테스트
│   │   ├── components/                   # 컴포넌트 단위 테스트
│   │   ├── hooks/                       # 훅 테스트
│   │   ├── pages/                       # 페이지 통합 테스트
│   │   └── e2e/                         # E2E 테스트 (Playwright)
│   │       ├── quote-generation.spec.ts
│   │       ├── compatibility-check.spec.ts
│   │       └── purchase-flow.spec.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── .eslintrc.json
│   ├── .prettierrc
│   └── Dockerfile
│
├── ======================================
├── 📁 BACKEND (FastAPI Python)
├── ======================================
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI 앱 진입점 + 미들웨어 등록
│   │   ├── dependencies.py               # 의존성 주입 (DB, Redis, LLM)
│   │   │
│   │   ├── api/                          # ── API 라우트 계층 ──
│   │   │   ├── __init__.py
│   │   │   ├── router.py                 # 전체 라우터 통합 등록
│   │   │   └── v1/                       # API 버전 v1
│   │   │       ├── __init__.py
│   │   │       ├── quotes.py             #   POST /quotes/generate
│   │   │       │                         #   GET  /quotes/{id}
│   │   │       │                         #   POST /quotes/{id}/customize
│   │   │       ├── components.py         #   GET  /components
│   │   │       │                         #   GET  /components/{id}
│   │   │       ├── prices.py             #   GET  /components/{id}/prices
│   │   │       ├── compatibility.py      #   POST /compatibility/check
│   │   │       ├── games.py              #   GET  /games
│   │   │       │                         #   GET  /software
│   │   │       ├── brands.py             #   GET  /brands/{category}
│   │   │       └── health.py             #   GET  /health
│   │   │
│   │   ├── core/                         # ── 핵심 설정 계층 ──
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 #   환경변수 기반 설정 (Pydantic Settings)
│   │   │   ├── security.py               #   JWT 토큰, API Key 검증
│   │   │   ├── constants.py              #   상수 (카테고리명, 소켓 매핑 등)
│   │   │   ├── exceptions.py             #   커스텀 예외 클래스
│   │   │   └── events.py                 #   앱 시작/종료 이벤트 핸들러
│   │   │
│   │   ├── schemas/                      # ── Pydantic 요청/응답 스키마 ──
│   │   │   ├── __init__.py
│   │   │   ├── quote.py                  #   QuoteRequest, QuoteResponse
│   │   │   ├── component.py              #   ComponentResponse, ComponentFilter
│   │   │   ├── price.py                  #   PriceComparison, PurchaseLink
│   │   │   ├── compatibility.py          #   CompatibilityResult, Issue
│   │   │   ├── brand.py                  #   BrandPreference, BrandCatalog
│   │   │   ├── budget.py                 #   BudgetIssue, BudgetValidation
│   │   │   └── common.py                 #   Pagination, ErrorResponse
│   │   │
│   │   ├── models/                       # ── SQLAlchemy ORM 모델 ──
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   #   Base 클래스 + 공통 Mixin
│   │   │   ├── component.py              #   Component, CPU, GPU, RAM 등
│   │   │   ├── motherboard.py            #   Motherboard (복잡한 관계)
│   │   │   ├── storage.py                #   Storage, PSU
│   │   │   ├── case_cooler.py            #   Case, Cooler
│   │   │   ├── quote.py                  #   Quote, QuoteComponent
│   │   │   ├── price.py                  #   Price, PriceHistory
│   │   │   ├── compatibility_rule.py     #   CompatibilityRule
│   │   │   └── game_software.py          #   GameRequirement, SoftwareRequirement
│   │   │
│   │   ├── services/                     # ── 비즈니스 로직 계층 ──
│   │   │   ├── __init__.py
│   │   │   ├── quote_engine.py           #   견적 생성 엔진 (3단계)
│   │   │   ├── compatibility/            #   호환성 체크 서브모듈 ──────
│   │   │   │   ├── __init__.py
│   │   │   │   ├── checker.py            #     메인 CompatibilityChecker
│   │   │   │   ├── rules/                #     개별 규칙 구현
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── socket_rules.py   #       CPU-MB 소켓 규칙
│   │   │   │   │   ├── memory_rules.py   #       RAM-MB DDR 규칙
│   │   │   │   │   ├── physical_rules.py #       물리적 크기 규칙
│   │   │   │   │   ├── power_rules.py    #       전력/커넥터 규칙
│   │   │   │   │   └── storage_rules.py  #       스토리지 슬롯 규칙
│   │   │   │   └── messages.py           #     한국어 오류 메시지 카탈로그
│   │   │   ├── price_service.py          #   가격 비교 + 최적 구매 전략
│   │   │   ├── brand_service.py          #   브랜드 필터링/검증
│   │   │   ├── budget_validator.py       #   예산 검증 + 이슈 알림
│   │   │   ├── benchmark_service.py      #   성능 벤치마크 매핑
│   │   │   └── purchase_link_service.py  #   구매 링크 생성/검증
│   │   │
│   │   ├── db/                           # ── 데이터베이스 계층 ──
│   │   │   ├── __init__.py
│   │   │   ├── database.py               #   AsyncEngine, SessionFactory
│   │   │   ├── session.py                #   세션 의존성 (get_db)
│   │   │   ├── repositories/             #   Repository 패턴 구현
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py               #     BaseRepository (CRUD 공통)
│   │   │   │   ├── component_repo.py     #     부품 조회/필터링
│   │   │   │   ├── price_repo.py         #     가격 조회/비교
│   │   │   │   ├── quote_repo.py         #     견적 저장/조회
│   │   │   │   └── game_repo.py          #     게임/소프트웨어 조회
│   │   │   ├── seeds/                    #   초기 데이터 시드
│   │   │   │   ├── compatibility_rules.json
│   │   │   │   ├── game_requirements.json
│   │   │   │   └── software_requirements.json
│   │   │   └── migrations/               #   Alembic 마이그레이션
│   │   │       ├── env.py
│   │   │       ├── script.py.mako
│   │   │       └── versions/
│   │   │
│   │   ├── cache/                        # ── 캐시 계층 ──
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py           #   Redis 연결 관리
│   │   │   ├── cache_keys.py             #   캐시 키 네이밍 규칙
│   │   │   └── cache_service.py          #   캐시 get/set/invalidate
│   │   │
│   │   ├── middleware/                   # ── 미들웨어 ──
│   │   │   ├── __init__.py
│   │   │   ├── logging_middleware.py     #   요청/응답 로깅
│   │   │   ├── error_handler.py          #   전역 에러 핸들링
│   │   │   ├── rate_limiter.py           #   요청 제한
│   │   │   └── cors.py                   #   CORS 설정
│   │   │
│   │   └── utils/                        # ── 유틸리티 ──
│   │       ├── __init__.py
│   │       ├── validators.py             #   데이터 유효성 검사
│   │       ├── formatters.py             #   가격/날짜 포매팅
│   │       └── helpers.py                #   범용 헬퍼 함수
│   │
│   ├── tests/                            # 백엔드 테스트
│   │   ├── conftest.py                   # pytest 공통 픽스처
│   │   ├── factories/                    # 테스트 데이터 팩토리
│   │   │   ├── component_factory.py
│   │   │   └── quote_factory.py
│   │   ├── unit/                         # 단위 테스트
│   │   │   ├── test_compatibility/
│   │   │   │   ├── test_socket_rules.py
│   │   │   │   ├── test_memory_rules.py
│   │   │   │   ├── test_physical_rules.py
│   │   │   │   └── test_power_rules.py
│   │   │   ├── test_quote_engine.py
│   │   │   ├── test_budget_validator.py
│   │   │   └── test_brand_service.py
│   │   ├── integration/                  # 통합 테스트
│   │   │   ├── test_quote_api.py
│   │   │   ├── test_component_api.py
│   │   │   └── test_compatibility_api.py
│   │   └── fixtures/                     # 테스트 데이터
│   │       ├── sample_components.json
│   │       └── sample_quotes.json
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt              # 개발용 의존성 (pytest, black 등)
│   ├── pyproject.toml
│   ├── .env.example
│   └── Dockerfile
│
├── ======================================
├── 📁 AI SERVICE (LLM 통합 독립 서비스)
├── ======================================
├── ai-service/
│   ├── app/
│   │   ├── main.py                       # FastAPI 앱 (AI 전용 마이크로서비스)
│   │   │
│   │   ├── providers/                    # ── LLM 프로바이더 ──
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py          #   추상 베이스 클래스
│   │   │   ├── claude_provider.py        #   Anthropic Claude API
│   │   │   ├── openai_provider.py        #   OpenAI GPT API
│   │   │   └── provider_factory.py       #   프로바이더 팩토리
│   │   │
│   │   ├── router/                       # ── LLM 스마트 라우팅 ──
│   │   │   ├── __init__.py
│   │   │   ├── model_router.py           #   역할별 모델 라우팅
│   │   │   ├── cost_tracker.py           #   일일/월간 비용 추적
│   │   │   └── fallback_handler.py       #   Fallback 전략 (Claude↔GPT)
│   │   │
│   │   ├── tasks/                        # ── AI 작업 유형별 모듈 ──
│   │   │   ├── __init__.py
│   │   │   ├── requirement_analyzer.py   #   자연어 → JSON 추출 (Sonnet)
│   │   │   ├── game_mapper.py            #   게임명 매핑 (Haiku)
│   │   │   ├── quote_optimizer.py        #   견적 최적화 추천 (Sonnet)
│   │   │   ├── explanation_generator.py  #   호환성 설명 생성 (Haiku)
│   │   │   ├── spec_extractor.py         #   크롤링 데이터 스펙 추출 (Haiku)
│   │   │   └── deep_analyzer.py          #   심층 비교 분석 (Opus, 요청 시)
│   │   │
│   │   ├── prompts/                      # ── 프롬프트 관리 ──
│   │   │   ├── __init__.py
│   │   │   ├── system_prompts.py         #   역할별 시스템 프롬프트
│   │   │   ├── templates/                #   Jinja2 프롬프트 템플릿
│   │   │   │   ├── requirement_analysis.j2
│   │   │   │   ├── game_mapping.j2
│   │   │   │   ├── quote_optimization.j2
│   │   │   │   └── compatibility_explain.j2
│   │   │   └── prompt_cache.py           #   프롬프트 결과 캐싱
│   │   │
│   │   ├── schemas/                      # ── AI 서비스 스키마 ──
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py               #   AnalyzedRequirements
│   │   │   ├── game_mapping.py           #   GameMappingResult
│   │   │   └── optimization.py           #   OptimizationSuggestion
│   │   │
│   │   └── config.py                     # AI 서비스 설정
│   │
│   ├── tests/
│   │   ├── test_requirement_analyzer.py
│   │   ├── test_game_mapper.py
│   │   ├── test_model_router.py
│   │   └── test_cost_tracker.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── ======================================
├── 📁 CRAWLER SERVICE (데이터 수집)
├── ======================================
├── crawler-service/
│   ├── app/
│   │   ├── main.py                       # Celery 앱 + Beat 스케줄러
│   │   │
│   │   ├── crawlers/                     # ── 사이트별 크롤러 ──
│   │   │   ├── __init__.py
│   │   │   ├── base_crawler.py           #   BaseCrawler 추상 클래스
│   │   │   ├── danawa/                   #   다나와 전용 ──────────
│   │   │   │   ├── __init__.py
│   │   │   │   ├── crawler.py            #     메인 크롤러 (Playwright)
│   │   │   │   ├── parser.py             #     HTML 파서 (BeautifulSoup)
│   │   │   │   ├── selectors.py          #     CSS 셀렉터 정의
│   │   │   │   └── urls.py               #     카테고리별 URL 매핑
│   │   │   ├── compuzone/                #   컴퓨존 전용 ──────────
│   │   │   │   ├── __init__.py
│   │   │   │   ├── crawler.py
│   │   │   │   ├── parser.py
│   │   │   │   └── selectors.py
│   │   │   ├── coupang/                  #   쿠팡 전용 ────────────
│   │   │   │   ├── __init__.py
│   │   │   │   ├── crawler.py            #     (Playwright - 동적 페이지)
│   │   │   │   ├── parser.py
│   │   │   │   └── selectors.py
│   │   │   └── pcpartpicker/             #   PCPartPicker 전용 ────
│   │   │       ├── __init__.py
│   │   │       ├── crawler.py            #     (BeautifulSoup)
│   │   │       ├── parser.py
│   │   │       └── selectors.py
│   │   │
│   │   ├── tasks/                        # ── Celery 태스크 ──
│   │   │   ├── __init__.py
│   │   │   ├── price_tasks.py            #   가격 업데이트 (6시간)
│   │   │   ├── discovery_tasks.py        #   신규 부품 감지 (24시간)
│   │   │   ├── inventory_tasks.py        #   재고 확인 (3시간)
│   │   │   ├── link_validation_tasks.py  #   링크 유효성 검증 (12시간)
│   │   │   └── cleanup_tasks.py          #   오래된 데이터 정리 (7일)
│   │   │
│   │   ├── pipeline/                     # ── 데이터 처리 파이프라인 ──
│   │   │   ├── __init__.py
│   │   │   ├── normalizer.py             #   가격/이름 정규화
│   │   │   ├── deduplicator.py           #   중복 상품 감지/병합
│   │   │   ├── anomaly_detector.py       #   이상 가격 감지
│   │   │   └── db_writer.py              #   DB 저장 + 이력 기록
│   │   │
│   │   ├── anti_block/                   # ── 차단 방지 ──
│   │   │   ├── __init__.py
│   │   │   ├── user_agents.py            #   User-Agent 로테이션
│   │   │   ├── proxy_pool.py             #   프록시 풀 관리
│   │   │   ├── rate_limiter.py           #   사이트별 요청 간격
│   │   │   └── fingerprint.py            #   브라우저 핑거프린트 관리
│   │   │
│   │   └── config.py                     # 크롤러 설정
│   │
│   ├── tests/
│   │   ├── test_danawa_parser.py
│   │   ├── test_normalizer.py
│   │   ├── test_anomaly_detector.py
│   │   └── fixtures/                     # 테스트용 HTML 샘플
│   │       ├── danawa_sample.html
│   │       ├── compuzone_sample.html
│   │       └── coupang_sample.html
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── ======================================
├── 📁 SHARED (공유 라이브러리)
├── ======================================
├── shared/
│   ├── __init__.py
│   ├── models/                           # 서비스 간 공유 모델
│   │   ├── __init__.py
│   │   ├── component_types.py            # 부품 카테고리 Enum
│   │   ├── brand_catalog.py              # 브랜드 분류 체계
│   │   └── socket_mapping.py             # 소켓-칩셋 매핑
│   ├── schemas/                          # 서비스 간 공유 스키마
│   │   ├── __init__.py
│   │   └── events.py                     # 이벤트 스키마 (서비스 간 통신)
│   ├── utils/                            # 공유 유틸리티
│   │   ├── __init__.py
│   │   ├── price_formatter.py            # 가격 포매팅
│   │   └── korean_utils.py               # 한국어 처리 유틸
│   └── constants.py                      # 전역 상수
│
├── ======================================
├── 📁 INFRASTRUCTURE (인프라/배포)
├── ======================================
├── infra/
│   ├── docker/
│   │   ├── docker-compose.yml            # 로컬 개발용
│   │   ├── docker-compose.prod.yml       # 프로덕션용
│   │   └── docker-compose.test.yml       # 테스트용
│   │
│   ├── aws/                              # AWS 배포 설정
│   │   ├── cloudformation/
│   │   │   ├── vpc.yaml                  # VPC + 서브넷
│   │   │   ├── ecs-cluster.yaml          # ECS 클러스터
│   │   │   ├── rds.yaml                  # RDS PostgreSQL
│   │   │   ├── elasticache.yaml          # ElastiCache Redis
│   │   │   ├── alb.yaml                  # Application Load Balancer
│   │   │   └── cloudfront.yaml           # CloudFront CDN
│   │   ├── terraform/                    # Terraform 대안 (선택)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── modules/
│   │   └── scripts/
│   │       ├── deploy.sh                 # 배포 스크립트
│   │       ├── rollback.sh               # 롤백 스크립트
│   │       └── seed-db.sh                # DB 시드 스크립트
│   │
│   ├── nginx/
│   │   ├── nginx.conf                    # Nginx 설정
│   │   └── ssl/                          # SSL 인증서 (Let's Encrypt)
│   │
│   ├── monitoring/
│   │   ├── prometheus.yml                # Prometheus 설정
│   │   ├── grafana/
│   │   │   └── dashboards/
│   │   │       ├── api-performance.json
│   │   │       ├── crawler-status.json
│   │   │       └── llm-cost.json
│   │   └── alertmanager.yml              # 알림 설정
│   │
│   └── ci-cd/
│       ├── .github/
│       │   └── workflows/
│       │       ├── ci.yml                # PR 검증 (lint, test)
│       │       ├── cd-staging.yml        # 스테이징 배포
│       │       └── cd-production.yml     # 프로덕션 배포
│       └── Makefile                      # 개발 편의 명령어
│
├── ======================================
├── 📁 DOCS (문서)
├── ======================================
├── docs/
│   ├── API_REFERENCE.md                  # API 전체 레퍼런스
│   ├── DATABASE_SCHEMA.md                # DB 스키마 상세
│   ├── DEPLOYMENT_GUIDE.md               # 배포 가이드
│   ├── DEVELOPMENT_SETUP.md              # 개발 환경 설정
│   ├── CODING_STANDARDS.md               # 코딩 표준 + 주석 가이드
│   ├── AWS_ARCHITECTURE.md               # AWS 아키텍처 상세
│   ├── COST_OPTIMIZATION.md              # 비용 최적화 가이드
│   └── TROUBLESHOOTING.md                # 트러블슈팅
│
├── .gitignore
├── .editorconfig                         # 에디터 설정 통일
├── README.md                             # 프로젝트 소개 + 빠른 시작
└── Makefile                              # 루트 Makefile (빌드/실행 명령)
```

---
