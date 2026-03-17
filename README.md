# 🖥️ PC Build Advisor

> AI가 자연어 요구사항을 분석해 최적의 PC 견적을 자동 추천하는 서비스

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai&logoColor=white)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 프로젝트 소개

**"배그 144fps 맞추고 싶은데 150만원 예산으로 PC 견적 뽑아줘"**

이런 자연어 한 문장이면 충분합니다.
PC Build Advisor는 GPT-4o-mini가 요구사항을 분석하고, 최소(Minimum) / 균형(Balanced) / 최고(Maximum) 3가지 견적을 자동으로 생성합니다.
다나와·쿠팡·컴퓨존 크롤러가 실시간 최저가를 자동으로 수집·갱신합니다.

---

## ✨ 주요 기능

- **🤖 AI 견적 생성** — 한국어 자연어 입력 → GPT-4o-mini 분석 → 3티어 견적 자동 출력
- **⚡ 호환성 자동 검사** — CPU 소켓·DDR 규격·GPU 길이·PSU 와트 등 18가지 규칙 검증
- **💰 실시간 최저가** — 다나와·쿠팡·컴퓨존 크롤러로 6시간마다 가격 자동 갱신
- **📊 가격 이력 추적** — 부품별 90일 가격 변동 그래프 제공
- **🎮 게임 FPS 예측** — 요청한 게임·해상도 기준 예상 FPS 표시
- **🔄 견적 커스터마이징** — 특정 부품 고정 후 나머지 재추천 기능

---

## 🏗️ 시스템 아키텍처

```
사용자 (브라우저)
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  Nginx (Reverse Proxy, port 80)                     │
└───────────┬─────────────────────────┬───────────────┘
            │                         │
            ▼                         ▼
┌───────────────────┐     ┌───────────────────────┐
│  Frontend         │     │  Backend API           │
│  Next.js 14       │────▶│  FastAPI (port 8000)   │
│  (port 3000)      │     └────────┬──────────────┘
└───────────────────┘              │
                                   ├──▶ AI Service
                                   │   FastAPI (port 8001)
                                   │   └─ OpenAI GPT-4o-mini
                                   │
                                   ├──▶ PostgreSQL 15
                                   │   (16개 테이블)
                                   │
                                   └──▶ Redis 7
                                        (캐시 + Celery 브로커)

크롤러 (Celery Beat)
├── 다나와  ─── 6시간마다 가격 갱신
├── 쿠팡    ─── (Playwright 동적 렌더링)
└── 컴퓨존  ─── 매일 신규 부품 탐지
```

---

## 🛠️ 기술 스택

| 영역 | 기술 |
|------|------|
| **프론트엔드** | Next.js 14, TypeScript, Tailwind CSS, Zustand, React Query, Recharts |
| **백엔드 API** | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| **AI 서비스** | OpenAI GPT-4o-mini (분석) / GPT-4o (재시도), Provider 패턴 |
| **크롤러** | Celery 5 + Beat, Playwright, httpx, BeautifulSoup4 |
| **데이터베이스** | PostgreSQL 15, Redis 7 |
| **인프라** | Docker Compose, Nginx, Prometheus, Grafana |
| **CI/CD** | GitHub Actions (린트 + 테스트), AWS ECS Fargate (프로덕션) |

---

## 🚀 빠른 시작

### 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치 및 실행
- [OpenAI API 키](https://platform.openai.com/api-keys) 발급

### 1. 클론

```bash
git clone https://github.com/LooGee/pc-build-advisor.git
cd pc-build-advisor
```

### 2. 환경 변수 파일 생성

**`backend/.env`**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/pc_advisor
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me-to-any-random-string-32chars
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL_ANALYSIS=gpt-4o-mini
LLM_MODEL_COMPLEX=gpt-4o
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
AI_SERVICE_URL=http://ai-service:8001
```

**`ai-service/.env`**
```env
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL_ANALYSIS=gpt-4o-mini
LLM_MODEL_COMPLEX=gpt-4o
REDIS_URL=redis://redis:6379/1
```

**`crawler-service/.env`**
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/pc_advisor
REDIS_URL=redis://redis:6379/2
CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3
```

**`frontend/.env.local`**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 서비스 시작

```bash
make dev         # 전체 서비스 빌드 및 시작 (2~5분 소요)
```

### 4. DB 초기화 (최초 1회)

```bash
make migrate     # 테이블 생성
docker exec -it pc-build-backend python -m app.db.seeds.run_seeds  # 초기 부품 데이터 삽입
```

### 5. 접속

| URL | 설명 |
|-----|------|
| http://localhost:3000 | 메인 서비스 |
| http://localhost:8000/docs | API 문서 (Swagger) |
| http://localhost:5555 | 크롤러 모니터링 (Flower) |

---

## 💬 사용 예시

채팅창에 아래와 같이 입력하면 견적이 생성됩니다:

```
배그 144fps 맞추고 싶어. 예산은 150만원이야.
```
```
영상편집용 PC 200만원 예산, 조용한 케이스 선호
```
```
사이버펑크 2077 1440p 울트라 옵션으로 즐길 수 있는 PC
```

---

## 📁 프로젝트 구조

```
pc-build-advisor/
│
├── backend/               # FastAPI 메인 서버
│   ├── app/
│   │   ├── api/v1/        # REST API 엔드포인트
│   │   ├── models/        # SQLAlchemy ORM (16개 테이블)
│   │   ├── services/      # 견적 엔진, 호환성 검사
│   │   ├── db/
│   │   │   ├── migrations/ # Alembic 마이그레이션
│   │   │   └── seeds/      # 초기 부품 데이터 (41개)
│   │   └── cache/          # Redis 캐시
│   └── requirements.txt
│
├── ai-service/            # LLM 분석 서비스 (port 8001)
│   └── app/
│       ├── providers/     # OpenAI / Claude Provider 패턴
│       └── tasks/         # 요구사항 분석, 게임명 매핑
│
├── crawler-service/       # 가격 크롤러 (Celery)
│   └── app/
│       ├── crawlers/      # 다나와, 쿠팡, 컴퓨존, PCPartPicker
│       └── pipeline/      # DB 저장 파이프라인
│
├── frontend/              # Next.js 프론트엔드 (port 3000)
│   └── app/
│       ├── page.tsx       # 채팅 입력 메인 화면
│       └── quotes/[id]/   # 견적 상세 화면
│
├── infra/
│   ├── docker/            # docker-compose.yml (개발/프로덕션)
│   ├── nginx/             # 리버스 프록시 설정
│   ├── monitoring/        # Prometheus + Grafana
│   └── aws/terraform/     # ECS Fargate + RDS 프로덕션 인프라
│
├── shared/                # 공유 유틸리티 (소켓 매핑, 예산 파싱)
├── Makefile               # 개발 명령어 모음
└── SETUP_GUIDE.md         # 상세 설정 가이드
```

---

## 💸 비용 안내

| 항목 | 비용 |
|------|------|
| OpenAI API (gpt-4o-mini, 월 1,000회 견적) | **약 ₩280/월** |
| 크롤링 (다나와·쿠팡·컴퓨존) | **₩0** (공개 데이터) |
| 인프라 (로컬 Docker) | **₩0** |
| 인프라 (AWS ECS + RDS, 선택) | 약 ₩120,000/월 |

---

## 🕷️ 크롤링 정책 및 면책 조항

이 프로젝트의 크롤러는 **개인 학습 및 포트폴리오 목적**으로 제작되었습니다.

- 공개된 가격 정보(비로그인 접근 가능한 데이터)만 수집합니다.
- 요청 간격을 **최소 6시간** 이상으로 유지하여 서버 부하를 최소화합니다.
- 상업적 대규모 크롤링 목적으로 사용하지 마세요.
- 각 사이트의 이용약관 및 robots.txt를 준수하는 것은 사용자의 책임입니다.

---

## 📖 상세 가이드

자세한 설정 방법, 비용 분석, 문제 해결 FAQ는 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** 를 참고하세요.

---

## 📄 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.
