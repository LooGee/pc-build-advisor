# PC Build Advisor — 설정 가이드

> 최종 업데이트: 2026-03-17

---

## 목차

1. [지금 당장 해야 할 작업 (필수)](#1-지금-당장-해야-할-작업-필수)
2. [최초 실행 순서](#2-최초-실행-순서)
3. [비용 발생 여부](#3-비용-발생-여부)
4. [크롤링 데이터 축적 구조](#4-크롤링-데이터-축적-구조)
5. [LLM 모델 구조](#5-llm-모델-구조)
6. [문제 해결 FAQ](#6-문제-해결-faq)

---

## 1. 지금 당장 해야 할 작업 (필수)

> **총 4개 파일 생성**이 필요합니다. 아래 내용을 그대로 복사 후 `sk-...` 부분만 교체하면 됩니다.

---

### ① `backend/.env` 생성

```env
# 데이터베이스 (docker-compose 기본값 그대로)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/pc_advisor

# Redis
REDIS_URL=redis://redis:6379/0

# 보안 키 (아무 문자열 32자 이상)
SECRET_KEY=change-me-to-any-random-string-32chars

# ★ OpenAI API 키 (유일하게 직접 입력해야 하는 값)
OPENAI_API_KEY=sk-...

# LLM 설정 (그대로 사용)
LLM_PROVIDER=openai
LLM_MODEL_ANALYSIS=gpt-4o-mini
LLM_MODEL_COMPLEX=gpt-4o

# 앱 설정
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
AI_SERVICE_URL=http://ai-service:8001
```

---

### ② `ai-service/.env` 생성

```env
# ★ OpenAI API 키 (위와 동일한 키)
OPENAI_API_KEY=sk-...

# LLM 설정 (그대로 사용)
LLM_PROVIDER=openai
LLM_MODEL_ANALYSIS=gpt-4o-mini
LLM_MODEL_COMPLEX=gpt-4o

# Redis (docker-compose 기본값 그대로)
REDIS_URL=redis://redis:6379/1
```

---

### ③ `crawler-service/.env` 생성

```env
# 데이터베이스 (docker-compose 기본값 그대로)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/pc_advisor

# Redis / Celery (docker-compose 기본값 그대로)
REDIS_URL=redis://redis:6379/2
CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3
```

> 이 파일은 API 키 없이 그대로 붙여넣기만 하면 됩니다.

---

### ④ `frontend/.env.local` 생성

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 정리 — 실제로 입력해야 하는 값

| 항목 | 파일 | 발급처 |
|------|------|--------|
| **`OPENAI_API_KEY=sk-...`** | `backend/.env`, `ai-service/.env` | https://platform.openai.com/api-keys |

> 나머지 값은 모두 기본값 그대로 복사하면 됩니다.

---

## 2. 최초 실행 순서

> **전제조건**: Docker Desktop이 실행 중이어야 합니다.

```bash
# ① 프로젝트 루트로 이동
cd C:\Users\gyoung\Claude\Pc_Build_Project

# ② 위 4개 .env 파일 생성 (최초 1회만)

# ③ 전체 서비스 빌드 및 시작
make dev
# 내부적으로: docker compose up --build -d
# 시작까지 2~5분 소요 (최초 빌드 시)

# ④ DB 마이그레이션 (최초 1회만)
make migrate
# 내부적으로: docker exec backend alembic upgrade head
# 16개 테이블 생성

# ⑤ 초기 부품 데이터 삽입 (최초 1회만)
docker exec -it pc-build-backend python -m app.db.seeds.run_seeds
# CPU 8 / GPU 8 / MB 6 / RAM 5 / SSD 5 / PSU 5 / Case 4 / Cooler 4
# 총 41개 부품 + 가격 데이터 삽입

# ⑥ 접속 확인
start http://localhost:3000      # 프론트엔드 (메인 화면)
start http://localhost:8000/docs # API 문서 (Swagger)
start http://localhost:5555      # Celery Flower (크롤러 모니터링)
```

---

### 이후 실행 (두 번째부터)

```bash
# 시작
make dev

# 중지
docker compose -f infra/docker/docker-compose.yml down
```

---

## 3. 비용 발생 여부

### OpenAI API — 사용할 때만 과금

채팅 입력 1회 → 견적 생성 시 API 호출 **1~2회** 발생합니다.

| 역할 | 모델 | 1회 예상 비용 |
|------|------|---------------|
| 요구사항 분석 (기본 경로) | **gpt-4o-mini** | ≈ ₩0.3원 |
| 분석 실패 시 재시도 | **gpt-4o** | ≈ ₩4원 |
| API 전체 실패 | 정규식 파서 (코드) | **₩0** |

| 시나리오 | 월 비용 |
|----------|---------|
| 월 1,000회 견적 (재시도 없음) | **약 ₩280** |
| 월 1,000회 견적 (재시도 포함) | 최대 **약 ₩4,000** |
| 개발/테스트 | 무료 크레딧으로 수천 회 가능 |

### 인프라 비용

| 환경 | 월 비용 |
|------|---------|
| 로컬 (Docker Desktop) | **₩0** |
| AWS 프로덕션 (ECS + RDS) | 약 ₩120,000 |

### 크롤링 비용

다나와·쿠팡·컴퓨존은 공개 웹사이트 스크래핑 → **₩0**

---

## 4. 크롤링 데이터 축적 구조

### 자동 실행 스케줄

| 작업 | 주기 | 설명 |
|------|------|------|
| 가격 업데이트 | **6시간마다** | 등록된 부품의 현재가 갱신 |
| 신규 부품 탐지 | **매일 새벽 2시** | 새 모델 자동 감지 후 DB 추가 |
| 링크 유효성 검사 | **12시간마다** | 품절 / 판매 종료 감지 |
| 가격 이력 정리 | **매주 일요일** | 90일 이상 오래된 이력 삭제 |

### 데이터 성장 추이

| 시점 | 부품 수 | 데이터 상태 |
|------|---------|-------------|
| 최초 실행 직후 | 41개 | 시드 데이터 (JSON) |
| 1일 후 | +10~50개 | 크롤러 자동 탐지 |
| 1주일 후 | 수십~수백개 | 가격 이력 누적 |
| 1개월 후 | 수백~수천개 | 충분한 가격 비교 데이터 |

### 크롤링 대상

| 사이트 | 방식 | 수집 항목 |
|--------|------|-----------|
| 다나와 | httpx (정적) | 가격, 스펙, 재고 |
| 쿠팡 | Playwright (동적) | 가격, 재고 |
| 컴퓨존 | httpx (정적) | 가격, 재고 |
| PCPartPicker | httpx (정적) | 글로벌 스펙 참조 |

> 크롤러는 `make dev` 실행 시 자동 시작됩니다.
> Flower UI → http://localhost:5555 에서 실시간 모니터링 가능

---

## 5. LLM 모델 구조

```
사용자 입력 (한국어 자연어)
         │
         ▼
┌─────────────────────────────────┐
│  AI Service (port 8001)         │
│                                 │
│  1차: gpt-4o-mini               │ ← 기본 경로 (비용 효율)
│       실패 시 ↓                 │
│  2차: gpt-4o                    │ ← 재시도 (최고 품질)
│       실패 시 ↓                 │
│  3차: 정규식 파서               │ ← API 없이도 기본 동작
└─────────────────────────────────┘
         │
         ▼
  견적 생성 엔진 (Backend)
  └─ 3가지 티어 견적 반환
     (Minimum / Balanced / Maximum)
```

### 모델 변경 방법 (필요 시)

`.env` 파일에서 언제든 변경 가능:

```env
# 품질 최우선 시
LLM_MODEL_ANALYSIS=gpt-4o

# 비용 최소화 (기본값, 권장)
LLM_MODEL_ANALYSIS=gpt-4o-mini
```

---

## 6. 문제 해결 FAQ

### Q. `make dev` 실행 후 backend 컨테이너가 계속 재시작됨
```bash
# 로그 확인
docker logs pc-build-backend

# 대부분 .env 파일이 없거나 OPENAI_API_KEY 미설정이 원인
```

### Q. 마이그레이션 실패 (`make migrate`)
```bash
# postgres 컨테이너가 healthy 상태인지 확인
docker ps

# backend 컨테이너 직접 접속 후 수동 실행
docker exec -it pc-build-backend alembic upgrade head
```

### Q. 시드 데이터 삽입 후 견적이 안 나옴
```bash
# DB에 데이터 있는지 확인
docker exec -it pc-build-postgres psql -U postgres -d pc_advisor -c "SELECT count(*) FROM components;"
```

### Q. OpenAI API 오류 (401 Unauthorized)
- `backend/.env`와 `ai-service/.env` 양쪽에 `OPENAI_API_KEY`가 있는지 확인
- https://platform.openai.com/api-keys 에서 키 유효성 확인

### Q. 크롤러가 동작하지 않는 것 같음
- http://localhost:5555 (Flower) 접속 → Tasks 탭에서 실행 이력 확인
- 크롤링은 6시간 간격이므로 첫 실행까지 대기 필요
- 즉시 실행: `docker exec -it pc-build-crawler celery -A app.main.celery_app call crawler.tasks.update_all_prices`

---

*파일 위치: `C:\Users\gyoung\Claude\Pc_Build_Project\SETUP_GUIDE.md`*
