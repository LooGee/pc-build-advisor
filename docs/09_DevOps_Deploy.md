# PC Build Advisor - 배포 및 인프라

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 23. AWS 배포 아키텍처

### 23.1 전체 AWS 아키텍처 다이어그램

```mermaid
graph TB
    subgraph Internet["인터넷"]
        USER["사용자 브라우저"]
    end

    subgraph AWS_Global["AWS Global"]
        R53["Route 53<br/>DNS"]
        CF["CloudFront<br/>CDN + SSL"]
    end

    subgraph VPC["VPC (10.0.0.0/16)"]
        subgraph Public_Subnet["Public Subnet"]
            ALB["Application<br/>Load Balancer"]
            NAT["NAT Gateway"]
        end

        subgraph Private_Subnet_App["Private Subnet - App"]
            ECS_FE["ECS Fargate<br/>Frontend<br/>(Next.js)"]
            ECS_BE["ECS Fargate<br/>Backend<br/>(FastAPI)"]
            ECS_AI["ECS Fargate<br/>AI Service<br/>(LLM Router)"]
            ECS_CR["ECS Fargate<br/>Crawler<br/>(Celery)"]
        end

        subgraph Private_Subnet_Data["Private Subnet - Data"]
            RDS["RDS PostgreSQL<br/>db.t4g.medium<br/>Multi-AZ"]
            EC["ElastiCache<br/>Redis<br/>cache.t4g.micro"]
        end
    end

    subgraph External["외부 서비스"]
        CLAUDE["Claude API"]
        GPT["OpenAI API"]
        SITES["크롤링 대상<br/>다나와/컴퓨존/쿠팡"]
    end

    subgraph Storage["스토리지"]
        S3["S3 Bucket<br/>정적 자산 + 로그"]
        ECR["ECR<br/>Docker 이미지"]
    end

    USER --> R53
    R53 --> CF
    CF -->|정적 자산| S3
    CF -->|동적 요청| ALB
    ALB --> ECS_FE
    ALB --> ECS_BE
    ECS_FE --> ECS_BE
    ECS_BE --> ECS_AI
    ECS_BE --> RDS
    ECS_BE --> EC
    ECS_AI --> CLAUDE
    ECS_AI --> GPT
    ECS_AI --> EC
    ECS_CR --> SITES
    ECS_CR --> RDS
    ECS_CR --> EC
    NAT --> ECS_CR
```

### 23.2 서비스별 AWS 구성

| 서비스 | AWS 리소스 | 인스턴스 | 비고 |
|--------|-----------|----------|------|
| **Frontend** | ECS Fargate | 0.25 vCPU, 0.5GB | Next.js SSR, 오토스케일 1~3 |
| **Backend** | ECS Fargate | 0.5 vCPU, 1GB | FastAPI, 오토스케일 1~4 |
| **AI Service** | ECS Fargate | 0.25 vCPU, 0.5GB | LLM 라우팅 (외부 API 호출만) |
| **Crawler** | ECS Fargate | 1 vCPU, 2GB | Playwright 헤드리스, 1개 상시 |
| **Database** | RDS PostgreSQL | db.t4g.medium | Multi-AZ, 50GB GP3 |
| **Cache** | ElastiCache Redis | cache.t4g.micro | 단일 노드 (시작) |
| **CDN** | CloudFront | - | 정적 자산 + Next.js ISR |
| **DNS** | Route 53 | - | 도메인 관리 |
| **Storage** | S3 | - | 정적 자산, 로그, 백업 |
| **Container** | ECR | - | Docker 이미지 레지스트리 |
| **CI/CD** | GitHub Actions | - | 빌드/테스트/배포 자동화 |

### 23.3 ECS Fargate 태스크 정의

```json
// backend-task-definition.json
{
    "family": "pc-build-backend",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::xxx:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::xxx:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "backend",
            "image": "{account_id}.dkr.ecr.ap-northeast-2.amazonaws.com/pc-build-backend:latest",
            "portMappings": [
                {"containerPort": 8000, "protocol": "tcp"}
            ],
            "environment": [
                {"name": "ENV", "value": "production"},
                {"name": "REDIS_HOST", "value": "pc-build-redis.xxx.cache.amazonaws.com"}
            ],
            "secrets": [
                {"name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:ap-northeast-2:xxx:parameter/pc-build/db-url"},
                {"name": "CLAUDE_API_KEY", "valueFrom": "arn:aws:ssm:ap-northeast-2:xxx:parameter/pc-build/claude-key"},
                {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:ssm:ap-northeast-2:xxx:parameter/pc-build/openai-key"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/pc-build-backend",
                    "awslogs-region": "ap-northeast-2",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3
            }
        }
    ]
}
```

### 23.4 Auto Scaling 정책

```python
# 서비스별 Auto Scaling 설정

SCALING_POLICIES = {
    "frontend": {
        "min_capacity": 1,
        "max_capacity": 3,
        "target_cpu_utilization": 70,      # CPU 70% 초과 시 스케일 아웃
        "scale_in_cooldown": 300,           # 5분 쿨다운
        "scale_out_cooldown": 60,           # 1분 쿨다운
    },
    "backend": {
        "min_capacity": 1,
        "max_capacity": 4,
        "target_cpu_utilization": 60,       # 견적 생성 시 CPU 부하 높음
        "target_request_count": 100,        # ALB 타겟당 100 req/min
        "scale_in_cooldown": 300,
        "scale_out_cooldown": 30,
    },
    "ai_service": {
        "min_capacity": 1,
        "max_capacity": 2,
        "target_cpu_utilization": 50,       # 외부 API 호출 대기가 주이므로 낮게
        "scale_in_cooldown": 600,
        "scale_out_cooldown": 120,
    },
    "crawler": {
        "min_capacity": 1,
        "max_capacity": 1,                  # 크롤러는 고정 1개 (rate limit 준수)
    },
}
```

### 23.5 CloudFront + S3 정적 자산 전략

```python
# Next.js 정적 자산 배포 전략

# 1. 빌드 시 정적 페이지는 S3로 업로드
# 2. CloudFront가 S3 오리진으로 캐싱
# 3. 동적 페이지(SSR)는 ALB → ECS Frontend로 라우팅

CLOUDFRONT_BEHAVIORS = {
    "/_next/static/*": {
        "origin": "s3-static-assets",
        "cache_policy": "CachingOptimized",    # 365일 캐시
        "compress": True,
    },
    "/images/*": {
        "origin": "s3-static-assets",
        "cache_policy": "CachingOptimized",
        "compress": True,
    },
    "/api/*": {
        "origin": "alb-backend",
        "cache_policy": "CachingDisabled",     # API는 캐시하지 않음
    },
    "/*": {
        "origin": "alb-frontend",
        "cache_policy": "CachingOptimizedForUncompressedObjects",
        "ttl": 60,                             # 동적 페이지 1분 캐시
    },
}
```

### 23.6 CI/CD 파이프라인

```yaml
# .github/workflows/cd-production.yml

name: Production Deploy

on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - '*.md'

env:
  AWS_REGION: ap-northeast-2
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.ap-northeast-2.amazonaws.com

jobs:
  # 1단계: 테스트
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, ai-service, crawler-service, frontend]
    steps:
      - uses: actions/checkout@v4
      - name: Run tests for ${{ matrix.service }}
        run: |
          cd ${{ matrix.service }}
          # Python 서비스
          if [ -f requirements.txt ]; then
            pip install -r requirements.txt -r requirements-dev.txt
            pytest tests/ -v --cov --cov-report=xml
          fi
          # Frontend
          if [ -f package.json ]; then
            npm ci && npm run test && npm run build
          fi

  # 2단계: Docker 빌드 + ECR 푸시
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, ai-service, crawler-service, frontend]
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      - uses: aws-actions/amazon-ecr-login@v2
      - name: Build and push ${{ matrix.service }}
        run: |
          IMAGE_TAG="${{ github.sha }}"
          docker build -t $ECR_REGISTRY/pc-build-${{ matrix.service }}:$IMAGE_TAG \
                       -t $ECR_REGISTRY/pc-build-${{ matrix.service }}:latest \
                       ./${{ matrix.service }}
          docker push $ECR_REGISTRY/pc-build-${{ matrix.service }}:$IMAGE_TAG
          docker push $ECR_REGISTRY/pc-build-${{ matrix.service }}:latest

  # 3단계: ECS 배포 (Rolling Update)
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [backend, ai-service, crawler-service, frontend]
    steps:
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster pc-build-cluster \
            --service pc-build-${{ matrix.service }} \
            --force-new-deployment \
            --region ${{ env.AWS_REGION }}
```

### 23.7 보안 구성

```
┌─ AWS Secrets Manager / SSM Parameter Store ─┐
│                                              │
│  /pc-build/db-url          → RDS 접속 URL    │
│  /pc-build/claude-key      → Claude API Key  │
│  /pc-build/openai-key      → OpenAI API Key  │
│  /pc-build/redis-url       → Redis 접속 URL  │
│  /pc-build/jwt-secret      → JWT 시크릿      │
│                                              │
└──────────────────────────────────────────────┘

보안 그룹 규칙:
- ALB: 80, 443 (인터넷)
- Frontend ECS: 3000 (ALB만)
- Backend ECS: 8000 (ALB + Frontend)
- AI Service ECS: 8001 (Backend만)
- RDS: 5432 (Backend + Crawler만)
- Redis: 6379 (Backend + AI + Crawler만)
- Crawler: 아웃바운드만 (크롤링 대상 사이트)
```

---

## 24. 비용 최적화 전략

### 24.1 AWS 월간 비용 예측

```
┌──────────────────────────────────────────────────────────────┐
│  PC Build Advisor - AWS 월간 비용 예측 (2026년 3월 기준)     │
│  리전: ap-northeast-2 (서울)                                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ── 컴퓨팅 (ECS Fargate) ──                                 │
│  Frontend  (0.25vCPU, 0.5GB) × 1개 × 730h  =  $8.44/월     │
│  Backend   (0.5vCPU, 1GB)   × 1개 × 730h  =  $25.33/월     │
│  AI Service(0.25vCPU, 0.5GB) × 1개 × 730h  =  $8.44/월     │
│  Crawler   (1vCPU, 2GB)     × 1개 × 730h  =  $50.66/월     │
│  소계: $92.87/월                                             │
│                                                              │
│  ── 데이터베이스 (RDS) ──                                    │
│  PostgreSQL db.t4g.medium, 50GB GP3                          │
│  단일 AZ (비용 절감): $52.56/월                              │
│  → Multi-AZ는 트래픽 증가 후 전환                            │
│  소계: $52.56/월                                             │
│                                                              │
│  ── 캐시 (ElastiCache) ──                                   │
│  Redis cache.t4g.micro                                       │
│  소계: $11.52/월                                             │
│                                                              │
│  ── 네트워크/CDN ──                                          │
│  ALB: $22.63/월 (기본 + LCU)                                │
│  CloudFront: ~$5/월 (100GB 전송 기준)                        │
│  Route 53: $0.50/월                                          │
│  NAT Gateway: $35.04/월 + 데이터 전송                       │
│  소계: ~$65/월                                               │
│                                                              │
│  ── 스토리지 ──                                              │
│  S3: ~$2/월 (정적 자산 + 로그)                               │
│  ECR: ~$1/월 (Docker 이미지)                                 │
│  소계: ~$3/월                                                │
│                                                              │
│  ── 모니터링 ──                                              │
│  CloudWatch Logs: ~$5/월                                     │
│  소계: ~$5/월                                                │
│                                                              │
│  ── LLM API ──                                               │
│  역할별 분리 + 캐싱 적용 (일 1,000건 기준)                   │
│  소계: ~$810/월 (약 ₩1,093,500)                             │
│                                                              │
│  ════════════════════════════════════════════                │
│  총 AWS 인프라: ~$230/월 (약 ₩310,000)                      │
│  총 LLM API:   ~$810/월 (약 ₩1,093,500)                    │
│  ────────────────────────────────────────────                │
│  총 합계:      ~$1,040/월 (약 ₩1,404,000)                  │
│  ════════════════════════════════════════════                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 24.2 비용 절감 전략 상세

```python
# backend/app/core/cost_optimization.py

COST_STRATEGIES = {
    # ── 전략 1: ECS Fargate Spot 활용 ──
    "fargate_spot": {
        "description": "Crawler 서비스는 Fargate Spot으로 실행 (최대 70% 할인)",
        "applicable_services": ["crawler-service"],
        "savings": "Crawler 비용 $50.66 → ~$15.20/월",
        "risk": "Spot 중단 시 크롤링 일시 중지 (자동 재시도로 대응)",
        "implementation": {
            "capacityProviderStrategy": [
                {"capacityProvider": "FARGATE_SPOT", "weight": 4},
                {"capacityProvider": "FARGATE", "weight": 1}
            ]
        }
    },

    # ── 전략 2: RDS Reserved Instance ──
    "rds_reserved": {
        "description": "1년 예약 인스턴스로 RDS 비용 37% 절감",
        "savings": "$52.56 → $33.11/월 (1년 약정)",
        "applicable_after": "서비스 안정화 후 (3개월 이후)"
    },

    # ── 전략 3: NAT Gateway 제거 ──
    "nat_optimization": {
        "description": "NAT Gateway($35/월)를 VPC Endpoint로 대체",
        "implementation": [
            "S3 Gateway Endpoint (무료)",
            "ECR Interface Endpoint ($7.20/월)",
            "CloudWatch Interface Endpoint ($7.20/월)",
            "Secrets Manager Interface Endpoint ($7.20/월)"
        ],
        "savings": "$35 → $21.60/월 (3개 엔드포인트)"
    },

    # ── 전략 4: CloudFront 캐시 최적화 ──
    "cloudfront_cache": {
        "description": "ISR + 정적 자산 캐싱으로 오리진 요청 80% 감소",
        "implementation": "Next.js revalidate + S3 정적 빌드",
        "savings": "ECS Frontend 트래픽 대폭 감소"
    },

    # ── 전략 5: LLM 비용 최적화 (기존 섹션 19 참고) ──
    "llm_optimization": {
        "description": "역할별 모델 분리 + 캐싱 + 일일 예산 제한",
        "savings": "월 59% 절감 (₩2,685,000 → ₩1,093,500)",
        "techniques": [
            "Haiku/Mini를 단순 작업에 사용",
            "Redis 프롬프트 캐싱 (히트율 50%+)",
            "일일 LLM 예산 $50 제한",
            "자주 묻는 요구사항 사전 캐싱"
        ]
    },

    # ── 전략 6: 시간대별 스케일링 ──
    "time_based_scaling": {
        "description": "한국 기준 새벽(02:00~07:00)에 최소 인스턴스로 축소",
        "implementation": {
            "peak_hours": {"backend": 2, "frontend": 2},   # 10:00~23:00
            "off_hours": {"backend": 1, "frontend": 1},    # 02:00~07:00
        },
        "savings": "컴퓨팅 비용 약 20% 추가 절감"
    },

    # ── 전략 7: Graviton 프로세서 활용 ──
    "graviton": {
        "description": "ARM 기반 Graviton3으로 ECS 실행 (20% 저렴, 40% 효율)",
        "requirement": "Docker 이미지 ARM64 빌드 필요",
        "savings": "ECS 비용 약 20% 절감"
    }
}

# ── 최적화 적용 후 비용 예측 ──
OPTIMIZED_MONTHLY_COST = {
    "ecs_fargate": 75,       # Spot + Graviton 적용
    "rds": 33,               # Reserved (1년 후)
    "elasticache": 11.52,
    "networking": 40,         # NAT → VPC Endpoint
    "storage": 3,
    "monitoring": 5,
    "llm_api": 810,          # 이미 최적화됨
    "total_usd": 977.52,
    "total_krw": 1320000,    # 약 ₩1,320,000/월
}
```

### 24.3 트래픽 증가 시 단계별 인프라 확장

```
┌─────────────────────────────────────────────────────────────────┐
│  단계별 확장 계획                                                │
├────────┬────────────┬──────────────────┬────────────────────────┤
│ 단계   │ 일일 사용자 │ 변경 사항         │ 예상 비용              │
├────────┼────────────┼──────────────────┼────────────────────────┤
│ Stage 1│ ~100명     │ 현재 구성 유지    │ ₩1,404,000/월          │
│ (출시) │            │                  │                        │
├────────┼────────────┼──────────────────┼────────────────────────┤
│ Stage 2│ ~1,000명   │ Backend 2→4개    │ ₩1,650,000/월          │
│ (성장) │            │ RDS Multi-AZ     │ (+₩246,000)            │
│        │            │ Redis 업그레이드  │                        │
├────────┼────────────┼──────────────────┼────────────────────────┤
│ Stage 3│ ~10,000명  │ ECS 서비스 확장   │ ₩3,500,000/월          │
│ (확장) │            │ RDS db.r7g.large │ (LLM 비용 증가 포함)    │
│        │            │ Redis 클러스터    │                        │
│        │            │ 크롤러 2개       │                        │
├────────┼────────────┼──────────────────┼────────────────────────┤
│ Stage 4│ ~100,000명 │ EKS 전환 고려     │ ₩12,000,000+/월        │
│ (대규모)│           │ Aurora Serverless │ (별도 아키텍처 리뷰)    │
│        │            │ DynamoDB 도입    │                        │
└────────┴────────────┴──────────────────┴────────────────────────┘
```

---

## 25. 개발자 편의 구조 (Developer Experience)

### 25.1 Makefile (루트)

```makefile
# ================================================================
# PC Build Advisor - 개발 편의 명령어
# 사용법: make <명령어>
# ================================================================

.PHONY: help setup dev test build deploy clean

# ── 도움말 ──
help: ## 사용 가능한 명령어 목록
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── 초기 설정 ──
setup: ## 전체 프로젝트 초기 설정 (의존성 설치 + DB 마이그레이션)
	@echo "🔧 Setting up PC Build Advisor..."
	cd frontend && npm install
	cd backend && pip install -r requirements.txt -r requirements-dev.txt
	cd ai-service && pip install -r requirements.txt
	cd crawler-service && pip install -r requirements.txt
	@echo "✅ Setup complete!"

# ── 로컬 개발 ──
dev: ## 전체 서비스 로컬 실행 (Docker Compose)
	docker compose -f infra/docker/docker-compose.yml up --build

dev-frontend: ## 프론트엔드만 실행
	cd frontend && npm run dev

dev-backend: ## 백엔드만 실행
	cd backend && uvicorn app.main:app --reload --port 8000

dev-ai: ## AI 서비스만 실행
	cd ai-service && uvicorn app.main:app --reload --port 8001

dev-crawler: ## 크롤러 워커 실행
	cd crawler-service && celery -A app.main worker --loglevel=info

# ── 테스트 ──
test: ## 전체 테스트 실행
	cd backend && pytest tests/ -v --cov
	cd ai-service && pytest tests/ -v
	cd crawler-service && pytest tests/ -v
	cd frontend && npm run test

test-backend: ## 백엔드 테스트만
	cd backend && pytest tests/ -v --cov --cov-report=html

test-frontend: ## 프론트엔드 테스트만
	cd frontend && npm run test

test-e2e: ## E2E 테스트
	cd frontend && npx playwright test

# ── 코드 품질 ──
lint: ## 전체 린트 검사
	cd backend && ruff check . && mypy app/
	cd ai-service && ruff check . && mypy app/
	cd frontend && npm run lint

format: ## 전체 코드 포매팅
	cd backend && ruff format . && isort .
	cd ai-service && ruff format . && isort .
	cd frontend && npm run format

# ── 데이터베이스 ──
db-migrate: ## DB 마이그레이션 생성
	cd backend && alembic revision --autogenerate -m "$(msg)"

db-upgrade: ## DB 마이그레이션 적용
	cd backend && alembic upgrade head

db-seed: ## 초기 데이터 시드 (호환성 규칙, 게임 요구사항)
	cd backend && python -m app.db.seeds.run_seeds

# ── 빌드 & 배포 ──
build: ## 전체 Docker 이미지 빌드
	docker compose -f infra/docker/docker-compose.yml build

deploy-staging: ## 스테이징 배포
	./infra/aws/scripts/deploy.sh staging

deploy-prod: ## 프로덕션 배포
	./infra/aws/scripts/deploy.sh production

# ── 정리 ──
clean: ## Docker 볼륨/캐시 정리
	docker compose -f infra/docker/docker-compose.yml down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	cd frontend && rm -rf .next node_modules
```

### 25.2 파트별 독립 실행 가이드

```
각 서비스는 독립적으로 개발/테스트/배포 가능해야 합니다.

┌─────────────────────────────────────────────────────────────┐
│  서비스 독립 실행 매트릭스                                    │
├──────────────┬──────────┬──────────┬────────────────────────┤
│ 서비스       │ 포트     │ 의존성    │ 독립 실행 명령          │
├──────────────┼──────────┼──────────┼────────────────────────┤
│ frontend     │ 3000     │ backend  │ npm run dev             │
│ backend      │ 8000     │ DB,Redis │ uvicorn app.main:app    │
│ ai-service   │ 8001     │ Redis    │ uvicorn app.main:app    │
│ crawler      │ -        │ DB,Redis │ celery -A app.main ...  │
├──────────────┼──────────┼──────────┼────────────────────────┤
│ DB (로컬)    │ 5432     │ -        │ docker run postgres     │
│ Redis (로컬) │ 6379     │ -        │ docker run redis        │
└──────────────┴──────────┴──────────┴────────────────────────┘

개발 시 모든 서비스를 띄울 필요 없이, 필요한 서비스만 실행:
  • 프론트엔드 개발자: make dev-frontend  (backend는 스테이징 API 연결)
  • 백엔드 개발자:     make dev-backend   (DB+Redis만 Docker로)
  • AI 개발자:         make dev-ai        (Redis만 Docker로)
  • 크롤러 개발자:     make dev-crawler   (DB+Redis만 Docker로)
```

### 25.3 .env.example (각 서비스별)

```bash
# backend/.env.example
# ====================================
# PC Build Advisor - Backend 환경변수
# 이 파일을 .env로 복사하여 실제 값을 입력하세요
# ====================================

# ── 서버 설정 ──
ENV=development                         # development | staging | production
PORT=8000
DEBUG=true
LOG_LEVEL=DEBUG                         # DEBUG | INFO | WARNING | ERROR

# ── 데이터베이스 ──
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/pcbuild
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# ── Redis ──
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL_PRICES=21600            # 가격 캐시 TTL (6시간, 초)
REDIS_CACHE_TTL_COMPONENTS=86400        # 부품 캐시 TTL (24시간)

# ── AI Service 연결 ──
AI_SERVICE_URL=http://localhost:8001
AI_SERVICE_TIMEOUT=30                   # 타임아웃 (초)

# ── API 보안 ──
JWT_SECRET=your-jwt-secret-here
API_RATE_LIMIT=100                      # 분당 요청 제한
CORS_ORIGINS=http://localhost:3000      # 허용 오리진

# ── 외부 API (AI Service에서 관리하지만 직접 호출 시) ──
# CLAUDE_API_KEY=sk-ant-xxx
# OPENAI_API_KEY=sk-xxx
```

### 25.4 파트별 README 구조

```
각 서비스 폴더에 독립적인 README.md 포함:

frontend/README.md:
  - 개발 환경 설정
  - 사용된 라이브러리 + 버전
  - 컴포넌트 구조 설명
  - 빌드/배포 방법

backend/README.md:
  - 개발 환경 설정
  - API 엔드포인트 빠른 참조
  - DB 마이그레이션 방법
  - 테스트 실행 방법

ai-service/README.md:
  - 지원 LLM 모델 목록
  - 프롬프트 수정 가이드
  - 비용 추적 방법

crawler-service/README.md:
  - 새 사이트 크롤러 추가 방법
  - 셀렉터 업데이트 가이드
  - 크롤링 스케줄 변경 방법
```

---

## 26. 초절약 플랜 (Budget-First Architecture)

> **기존 계획: ₩1,404,000/월 → 초절약 플랜: ₩170,000~250,000/월 (85% 절감)**
>
> 이 섹션은 **돈을 최대한 안 쓰면서** 동일한 기능을 구현하는 현실적인 대안 아키텍처입니다.
> 사용자 수가 늘어나면 단계적으로 기존 AWS 아키텍처(섹션 23~24)로 마이그레이션합니다.

### 26.1 비용이 비싼 진짜 이유

```
현재 설계의 비용 구조 (₩1,404,000/월):

  LLM API (Claude Sonnet + Haiku)     ₩1,093,500  ██████████████████████████░░░░  78%
  ECS Fargate (4개 서비스 24h)          ₩92,870    ███░░░░░░░░░░░░░░░░░░░░░░░░░░   7%
  RDS PostgreSQL                       ₩52,560    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░   4%
  NAT Gateway                          ₩35,040    █░░░░░░░░░░░░░░░░░░░░░░░░░░░░   3%
  ALB + CloudFront                     ₩65,000    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░   5%
  ElastiCache Redis                    ₩11,520    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   1%
  기타 (S3, CloudWatch, ECR)           ₩53,510    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░   4%

문제 1: LLM API가 전체의 78% → Claude Sonnet이 너무 비쌈
문제 2: ECS Fargate가 24시간 돌아감 → 사용자 0명이어도 돈 나감
문제 3: RDS + NAT + ALB → 트래픽 없어도 고정비 ₩150,000+
```

### 26.2 초절약 아키텍처

```mermaid
graph TB
    subgraph Free_Tier["무료/초저가 인프라"]
        VERCEL["Vercel<br/>Next.js Frontend<br/>$20/월 (Pro)"]
        LAMBDA["AWS Lambda<br/>Backend API<br/>100만건 무료"]
        LAMBDA_AI["AWS Lambda<br/>AI Service<br/>100만건 무료"]
        LAMBDA_CR["Lambda + EventBridge<br/>Crawler<br/>스케줄 실행"]
    end

    subgraph Cheap_Data["초저가 데이터"]
        SUPA["Supabase<br/>PostgreSQL<br/>$25/월 (Pro)"]
        UPSTASH["Upstash Redis<br/>Serverless<br/>$0~10/월"]
    end

    subgraph LLM["초저가 LLM"]
        DS["DeepSeek V3.2<br/>$0.28/M input<br/>단순 작업 전담"]
        HAIKU["Claude Haiku 4.5<br/>$1/M input<br/>핵심 분석만"]
    end

    VERCEL --> LAMBDA
    LAMBDA --> LAMBDA_AI
    LAMBDA --> SUPA
    LAMBDA --> UPSTASH
    LAMBDA_AI --> DS
    LAMBDA_AI --> HAIKU
    LAMBDA_CR --> SUPA
```

### 26.3 LLM 비용 90% 절감: DeepSeek V3.2 도입

```python
# ai-service/app/router/budget_model_router.py
"""
초절약 LLM 라우팅 전략.

핵심 원칙: 비싼 모델은 '꼭 필요한 곳'에만. 나머지는 전부 DeepSeek.
DeepSeek V3.2: 입력 $0.28/M, 출력 $0.42/M (캐시 히트 $0.028/M)
Claude Haiku 4.5: 입력 $1/M, 출력 $5/M
Claude Sonnet 4: 입력 $3/M, 출력 $15/M (거의 안 씀)
"""

from enum import Enum

class LLMTask(str, Enum):
    REQUIREMENT_ANALYSIS = "requirement_analysis"   # 자연어 → JSON 추출
    GAME_MAPPING = "game_mapping"                   # "배그" → "PUBG"
    QUOTE_OPTIMIZATION = "quote_optimization"       # 견적 최적화 추천
    COMPATIBILITY_EXPLANATION = "compatibility_explanation"  # 호환성 설명
    USER_FOLLOWUP = "user_followup"                 # 후속 질문 응답
    SPEC_EXTRACTION = "spec_extraction"             # 크롤링 스펙 추출
    DEEP_ANALYSIS = "deep_analysis"                 # 심층 비교 (드물게 사용)


# ================================================================
# 초절약 모델 라우팅 (기존 대비 90% 비용 절감)
# ================================================================
BUDGET_MODEL_ROUTING = {
    # ── DeepSeek 전담 (전체 요청의 70%) ──
    # 이 작업들은 DeepSeek V3.2로 충분히 처리 가능
    LLMTask.GAME_MAPPING: {
        "provider": "deepseek",
        "model": "deepseek-chat",           # V3.2
        "cost_input_per_1m": 0.28,          # $0.28 (캐시 미스)
        "cost_output_per_1m": 0.42,
        "max_tokens": 512,
        "temperature": 0.0,
        "reason": "단순 키워드 매핑, 고급 모델 불필요"
    },
    LLMTask.COMPATIBILITY_EXPLANATION: {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "cost_input_per_1m": 0.28,
        "cost_output_per_1m": 0.42,
        "max_tokens": 512,
        "temperature": 0.1,
        "reason": "템플릿 기반 메시지 생성, 한국어도 우수"
    },
    LLMTask.SPEC_EXTRACTION: {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "cost_input_per_1m": 0.28,
        "cost_output_per_1m": 0.42,
        "max_tokens": 1024,
        "temperature": 0.0,
        "reason": "정형화된 HTML에서 스펙 파싱, 정확도 충분"
    },

    # ── Claude Haiku 전담 (전체 요청의 25%) ──
    # 한국어 자연어 이해가 중요한 작업
    LLMTask.REQUIREMENT_ANALYSIS: {
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "cost_input_per_1m": 1.0,           # $1.00
        "cost_output_per_1m": 5.0,
        "max_tokens": 1024,
        "temperature": 0.2,
        "reason": "한국어 자연어 분석 핵심, Haiku면 충분"
    },
    LLMTask.USER_FOLLOWUP: {
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
        "cost_input_per_1m": 1.0,
        "cost_output_per_1m": 5.0,
        "max_tokens": 1024,
        "temperature": 0.5,
        "reason": "대화 맥락 유지, 자연스러운 한국어 응답"
    },

    # ── DeepSeek + Haiku 혼합 (5%) ──
    LLMTask.QUOTE_OPTIMIZATION: {
        "provider": "deepseek",             # 1차: DeepSeek
        "model": "deepseek-chat",
        "cost_input_per_1m": 0.28,
        "cost_output_per_1m": 0.42,
        "max_tokens": 2048,
        "temperature": 0.3,
        "fallback": {                       # 결과 불만족 시: Haiku
            "provider": "anthropic",
            "model": "claude-haiku-4-5-20251001"
        },
        "reason": "대부분 DeepSeek으로 처리, 복잡한 경우만 Haiku"
    },

    # ── Claude Sonnet (거의 안 씀, <1%) ──
    LLMTask.DEEP_ANALYSIS: {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "cost_input_per_1m": 3.0,
        "cost_output_per_1m": 15.0,
        "max_tokens": 4096,
        "temperature": 0.4,
        "reason": "사용자가 명시적으로 '상세 분석' 요청 시에만"
    },
}
```

### 26.4 LLM 비용 시뮬레이션 (일 1,000건 기준)

```
┌──────────────────────────────────────────────────────────────────┐
│  일 1,000건 견적 요청 시 LLM 비용 비교                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ── 기존 (Claude Sonnet + Haiku) ──                              │
│  요구사항 분석 (Sonnet): 1000 × (0.5K×$3 + 1K×$15) = $16.50    │
│  게임 매핑 (Haiku):     1000 × (0.3K×$1 + 0.5K×$5) = $2.80     │
│  견적 최적화 (Sonnet):  1000 × (1K×$3 + 2K×$15)   = $33.00     │
│  호환성 설명 (Haiku):   1000 × (0.3K×$1 + 0.5K×$5) = $2.80     │
│  일 합계: $55.10 → 월: $1,653 (약 ₩2,232,000)                   │
│  + 캐시 50%: 월 $826 (약 ₩1,115,000)                            │
│                                                                  │
│  ── 초절약 (DeepSeek V3.2 + Haiku) ──                            │
│  요구사항 분석 (Haiku):  1000 × (0.5K×$1 + 1K×$5) = $5.50       │
│  게임 매핑 (DeepSeek):   1000 × (0.3K×$0.28 + 0.5K×$0.42)      │
│                          = $0.29                                 │
│  견적 최적화 (DeepSeek): 1000 × (1K×$0.28 + 2K×$0.42) = $1.12  │
│  호환성 설명 (DeepSeek): 1000 × (0.3K×$0.28 + 0.5K×$0.42)      │
│                          = $0.29                                 │
│  후속 질문 (Haiku, 30%): 300 × (0.5K×$1 + 1K×$5) = $1.65       │
│  일 합계: $8.85 → 월: $265.50 (약 ₩358,000)                     │
│  + 캐시 50%: 월 $133 (약 ₩180,000)                              │
│                                                                  │
│  ── 절감 효과 ──                                                 │
│  기존:     ₩1,115,000/월                                         │
│  초절약:   ₩180,000/월                                           │
│  절감:     ₩935,000/월 (84% 절감)                                │
│                                                                  │
│  + DeepSeek 캐시 히트 활용 시 ($0.028/M, 90% 할인):              │
│    반복 요청 캐시 히트 70% 달성 시: 월 ₩120,000까지 가능         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 26.5 인프라 Serverless 전환

```python
# ================================================================
# 기존 → 초절약 인프라 매핑
# ================================================================
INFRA_MIGRATION = {
    # ── Frontend ──
    "frontend": {
        "before": "ECS Fargate (0.25vCPU, 0.5GB, 24h) → $8.44/월",
        "after": "Vercel Pro → $20/월",
        "why": "Next.js 배포에 특화, CDN/SSL/CI-CD 자동, 빌드 최적화 포함. "
               "ECS보다 비싸 보이지만 ALB($22) + CloudFront($5) + ECR($1)이 불필요해짐. "
               "실질 절감: $36.44 → $20 = $16.44 절감",
        "free_option": "Vercel Hobby (무료, 비상업용 MVP 테스트)"
    },

    # ── Backend API ──
    "backend": {
        "before": "ECS Fargate (0.5vCPU, 1GB, 24h) → $25.33/월",
        "after": "AWS Lambda + API Gateway → 사용량 기반",
        "why": "요청이 없으면 비용 0원. Lambda 월 100만건 무료. "
               "API Gateway HTTP API는 100만건당 $1. "
               "일 1,000건이면 월 3만건 → 사실상 무료",
        "monthly_cost": "₩0~5,000 (Lambda 무료 티어 내)",
        "cold_start": "Python Lambda 콜드스타트 ~800ms. "
                      "Provisioned Concurrency 1개 설정 시 $5/월로 해결",
        "implementation": {
            "framework": "Mangum (FastAPI → Lambda 어댑터)",
            "deploy": "AWS SAM 또는 Serverless Framework",
            "example": "handler = Mangum(app)  # FastAPI 앱 그대로 사용"
        }
    },

    # ── AI Service ──
    "ai_service": {
        "before": "ECS Fargate (0.25vCPU, 0.5GB, 24h) → $8.44/월",
        "after": "AWS Lambda → 사용량 기반",
        "why": "LLM API 호출만 하는 서비스. 대부분의 시간은 외부 API 응답 대기. "
               "Lambda가 완벽한 유스케이스",
        "monthly_cost": "₩0~3,000",
        "timeout": "Lambda 타임아웃 30초 설정 (LLM 응답 대기)"
    },

    # ── Crawler ──
    "crawler": {
        "before": "ECS Fargate (1vCPU, 2GB, 24h) → $50.66/월 ← 가장 비쌈",
        "after": "Lambda + EventBridge 스케줄",
        "why": "크롤러는 6시간마다 실행, 실행 시간 약 30분. "
               "하루 2시간만 쓰는데 24시간 Fargate? 돈 낭비. "
               "Lambda 최대 15분 제한 → 사이트별 별도 Lambda로 분할",
        "monthly_cost": "₩3,000~8,000",
        "schedule": {
            "price_update": "EventBridge: rate(6 hours) → 4개 Lambda (사이트별)",
            "new_components": "EventBridge: rate(24 hours) → 1개 Lambda",
            "link_validation": "EventBridge: rate(12 hours) → 1개 Lambda"
        },
        "playwright_issue": "Lambda에서 Playwright 실행은 Layer 크기 이슈. "
                           "대안 1: Lambda Container Image (최대 10GB). "
                           "대안 2: 다나와/쿠팡은 AWS Fargate Spot으로 분리 "
                           "($15/월, 실행 시간만 과금)"
    },

    # ── Database ──
    "database": {
        "before": "RDS PostgreSQL db.t4g.medium → $52.56/월",
        "after": "Supabase Pro → $25/월",
        "why": "Supabase = Managed PostgreSQL + REST API + Auth + Realtime. "
               "8GB RAM, 100GB DB, 250GB 대역폭, 7일 백업 포함. "
               "RDS 대비 50% 저렴하고 관리 부담 제로",
        "free_option": "Supabase Free (500MB DB, 영구 무료, 개발/MVP용)",
        "migration": "PostgreSQL이므로 스키마 그대로 사용. pg_dump → pg_restore"
    },

    # ── Cache ──
    "cache": {
        "before": "ElastiCache Redis cache.t4g.micro → $11.52/월",
        "after": "Upstash Redis Serverless → $0~10/월",
        "why": "Upstash = Serverless Redis. 무료 티어: 월 50만 커맨드, 256MB. "
               "사용량 초과 시 $0.20/10만 커맨드. "
               "일 1,000건 견적이면 무료 티어로 충분",
        "free_option": "Upstash Free (50만 커맨드/월, 256MB)",
        "pricing": "$0.20/100K 커맨드 + $0.25/GB 스토리지"
    },

    # ── 제거되는 서비스 ──
    "removed": {
        "NAT_Gateway": "제거 ($35/월 절감). Lambda는 VPC 밖에서 실행 가능",
        "ALB": "제거 ($22/월 절감). API Gateway가 대체",
        "CloudFront": "제거 ($5/월 절감). Vercel Edge Network가 대체",
        "ECR": "최소화. Lambda Container Image는 ECR 사용하지만 크기 작음",
        "ELK_Stack": "제거. CloudWatch Logs로 대체 (Lambda 자동 연동)"
    }
}
```

### 26.6 초절약 월간 비용 상세

```
┌──────────────────────────────────────────────────────────────────┐
│  초절약 플랜 - 월간 비용 (일 1,000건 견적 기준)                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ── 인프라 ──                                                    │
│  Vercel Pro (Frontend)               $20.00    ₩27,000          │
│  Supabase Pro (PostgreSQL)           $25.00    ₩34,000          │
│  Upstash Redis (캐시)                 $5.00    ₩7,000           │
│  AWS Lambda (Backend + AI)            $2.00    ₩3,000           │
│  AWS Lambda (Crawler)                 $5.00    ₩7,000           │
│  API Gateway                          $1.00    ₩1,400           │
│  EventBridge (스케줄러)               $0.00    ₩0 (무료)        │
│  CloudWatch Logs                      $3.00    ₩4,000           │
│  S3 (백업/로그)                       $1.00    ₩1,400           │
│  ──────────────────────────────────────────────────────────────────│
│  인프라 소계:                        $62.00    ₩84,000          │
│                                                                  │
│  ── LLM API ──                                                   │
│  DeepSeek V3.2 (70% 요청)           $48.00    ₩65,000          │
│  Claude Haiku 4.5 (25% 요청)        $82.00    ₩111,000         │
│  Claude Sonnet 4 (<1% 요청)          $3.00    ₩4,000           │
│  ──────────────────────────────────────────────────────────────────│
│  LLM 소계:                         $133.00    ₩180,000         │
│                                                                  │
│  ══════════════════════════════════════════════════════════════════│
│  총 합계:                          $195.00    ₩264,000/월      │
│  ══════════════════════════════════════════════════════════════════│
│                                                                  │
│  기존 대비: ₩1,404,000 → ₩264,000 (81% 절감, 월 ₩1,140,000 절약)│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 26.7 개발 단계 (거의 무료)

```
┌──────────────────────────────────────────────────────────────────┐
│  개발/MVP 단계 - 무료 티어 최대 활용                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Vercel Hobby (Frontend)              $0      무료 (비상업용)    │
│  Supabase Free (PostgreSQL)           $0      500MB, 영구 무료   │
│  Upstash Free (Redis)                 $0      50만 커맨드/월     │
│  AWS Lambda Free Tier                 $0      100만 건/월        │
│  API Gateway Free Tier                $0      100만 건/12개월    │
│  DeepSeek API (테스트 최소 사용)     ~$5      ₩7,000            │
│  Claude API (테스트 최소 사용)       ~$10     ₩14,000           │
│  ──────────────────────────────────────────────────────────────────│
│  개발 단계 합계:                    ~$15/월   ₩20,000/월        │
│                                                                  │
│  → 개발 6개월간 총 비용: 약 ₩120,000 (기존 대비 ₩8,304,000 절약) │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 26.8 단계별 비용 확장 로드맵

```
┌──────────┬──────────┬────────────────────────────┬──────────────┐
│ 단계     │ 사용자   │ 인프라 구성                 │ 월 비용      │
├──────────┼──────────┼────────────────────────────┼──────────────┤
│ Stage 0  │ 0명      │ 전부 무료 티어              │ ₩20,000     │
│ 개발     │ (개발)   │ Vercel Hobby + Supabase    │              │
│          │          │ Free + Upstash Free        │              │
├──────────┼──────────┼────────────────────────────┼──────────────┤
│ Stage 1  │ ~100명   │ Vercel Pro + Supabase Pro  │ ₩264,000    │
│ 출시     │ /일      │ + Lambda + DeepSeek/Haiku  │              │
├──────────┼──────────┼────────────────────────────┼──────────────┤
│ Stage 2  │ ~1,000명 │ + Lambda Provisioned       │ ₩450,000    │
│ 성장     │ /일      │ + Supabase Team ($599)     │              │
│          │          │ + Upstash Pro              │              │
├──────────┼──────────┼────────────────────────────┼──────────────┤
│ Stage 3  │ ~5,000명 │ Lambda → ECS Fargate 전환  │ ₩1,200,000  │
│ 확장     │ /일      │ + RDS PostgreSQL           │              │
│          │          │ + ElastiCache              │              │
│          │          │ (섹션 23 아키텍처로 전환)   │              │
├──────────┼──────────┼────────────────────────────┼──────────────┤
│ Stage 4  │ ~10,000+ │ 섹션 23~24 풀 아키텍처     │ ₩2,500,000+ │
│ 대규모   │ /일      │ ECS + RDS Multi-AZ + CDN   │              │
└──────────┴──────────┴────────────────────────────┴──────────────┘
```

### 26.9 초절약 아키텍처 디렉토리 변경점

```
기존 구조 대비 변경되는 부분만 표시:

backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 (변경 없음)
│   │   └── lambda_handler.py    # [추가] Lambda 진입점
│   │       """
│   │       from mangum import Mangum
│   │       from app.main import app
│   │
│   │       # FastAPI → Lambda 어댑터
│   │       # 기존 FastAPI 코드를 한 줄도 안 바꾸고 Lambda에서 실행
│   │       handler = Mangum(app, lifespan="off")
│   │       """
│   └── template.yaml            # [추가] AWS SAM 배포 템플릿

ai-service/
│   ├── app/
│   │   ├── providers/
│   │   │   ├── deepseek_provider.py  # [추가] DeepSeek V3.2 클라이언트
│   │   │   │   """
│   │   │   │   DeepSeek은 OpenAI 호환 API를 제공하므로
│   │   │   │   openai 패키지의 base_url만 변경하면 됨:
│   │   │   │
│   │   │   │   from openai import AsyncOpenAI
│   │   │   │   client = AsyncOpenAI(
│   │   │   │       api_key=DEEPSEEK_API_KEY,
│   │   │   │       base_url="https://api.deepseek.com"
│   │   │   │   )
│   │   │   │   """
│   │   │   ├── claude_provider.py    # (기존 유지)
│   │   │   └── openai_provider.py    # (기존 유지, fallback용)
│   │   └── router/
│   │       └── budget_model_router.py # [추가] 초절약 라우팅 전략
│   └── lambda_handler.py             # [추가] Lambda 진입점

crawler-service/
│   ├── lambdas/                      # [추가] 사이트별 Lambda 함수
│   │   ├── danawa_crawler/
│   │   │   ├── handler.py            # Lambda 핸들러
│   │   │   └── Dockerfile            # Container Image (Playwright 포함)
│   │   ├── compuzone_crawler/
│   │   │   └── handler.py
│   │   ├── coupang_crawler/
│   │   │   ├── handler.py
│   │   │   └── Dockerfile
│   │   └── pcpartpicker_crawler/
│   │       └── handler.py
│   └── template.yaml                # AWS SAM (EventBridge 스케줄 포함)

infra/
│   ├── aws/
│   │   ├── sam/                     # [추가] AWS SAM 템플릿
│   │   │   ├── template.yaml        # 전체 Lambda + API Gateway 정의
│   │   │   └── samconfig.toml       # SAM 배포 설정
│   │   └── cloudformation/          # (Stage 3 이후 사용)
```

### 26.10 DeepSeek 사용 시 유의사항

```python
# ai-service/app/providers/deepseek_provider.py

"""
DeepSeek V3.2 사용 시 유의사항:

1. 데이터 프라이버시:
   - DeepSeek는 중국 기업 (항저우 소재)
   - 이 프로젝트에서 DeepSeek에 전송되는 데이터:
     * 게임 이름 매핑 ("배그" → "PUBG") → 민감하지 않음
     * HTML 파싱 결과 (부품 스펙) → 공개 정보
     * 호환성 설명 생성 → 기술적 설명
   - 사용자 개인정보는 절대 DeepSeek에 전송하지 않음
   - 예산, IP 주소 등 개인 식별 정보는 Claude에서만 처리

2. API 안정성:
   - DeepSeek API는 간헐적 다운타임 발생 가능
   - 반드시 Claude Haiku fallback 설정 필수
   - timeout 10초, retry 2회 설정

3. 캐시 히트 활용:
   - 동일 프롬프트 prefix는 $0.028/M (90% 할인)
   - 시스템 프롬프트를 고정하면 캐시 히트율 높아짐
   - off-peak 시간대 (01:30~09:30 KST) 추가 50% 할인

4. 품질:
   - 한국어 이해: Claude 대비 약 85~90% 수준
   - JSON 구조화 출력: Claude와 동등
   - 게임명/부품명 매핑: 충분히 정확
   - 복잡한 추론이 필요한 작업은 Claude가 우수
"""

class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek V3.2 API 클라이언트.
    OpenAI 호환 API이므로 openai 패키지를 그대로 사용합니다.
    """

    def __init__(self, api_key: str, redis_client=None):
        # DeepSeek은 OpenAI SDK와 호환
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.redis = redis_client

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 1024,
        temperature: float = 0.2
    ) -> str:
        """
        DeepSeek V3.2로 텍스트 생성.

        Args:
            system_prompt: 시스템 프롬프트 (캐시 히트 최적화를 위해 고정 권장)
            user_message: 사용자 메시지
            max_tokens: 최대 출력 토큰
            temperature: 생성 온도 (0.0=결정적, 1.0=창의적)

        Returns:
            생성된 텍스트

        Note:
            - 시스템 프롬프트가 동일하면 캐시 히트 → 90% 할인
            - timeout 10초 초과 시 Claude Haiku로 fallback
        """
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"}  # JSON 모드
                ),
                timeout=10.0  # 10초 타임아웃
            )
            return response.choices[0].message.content

        except (asyncio.TimeoutError, Exception) as e:
            # DeepSeek 실패 시 Claude Haiku fallback
            logger.warning(f"DeepSeek 실패, Claude Haiku로 전환: {e}")
            return await self._fallback_to_haiku(system_prompt, user_message)
```

### 26.11 비용 비교 총괄표

```
┌──────────────────────────────────────────────────────────────────┐
│  비용 비교 총괄 (일 1,000건 견적 기준)                            │
├──────────────┬──────────────┬──────────────┬─────────────────────┤
│ 항목         │ 기존 (v3)    │ 최적화 (v3)  │ 초절약 (v4)         │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ Frontend     │ ₩49,000      │ ₩49,000      │ ₩27,000 (Vercel)   │
│ Backend      │ ₩34,000      │ ₩27,000      │ ₩3,000 (Lambda)    │
│ AI Service   │ ₩11,000      │ ₩11,000      │ ₩3,000 (Lambda)    │
│ Crawler      │ ₩68,000      │ ₩20,000      │ ₩7,000 (Lambda)    │
│ Database     │ ₩71,000      │ ₩45,000      │ ₩34,000 (Supabase) │
│ Cache        │ ₩16,000      │ ₩16,000      │ ₩7,000 (Upstash)   │
│ 네트워크     │ ₩88,000      │ ₩54,000      │ ₩3,000 (불필요)    │
│ 모니터링     │ ₩7,000       │ ₩7,000       │ ₩0 (CloudWatch)    │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ 인프라 소계  │ ₩344,000     │ ₩229,000     │ ₩84,000            │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ LLM API      │ ₩1,115,000   │ ₩1,093,500   │ ₩180,000           │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ 총 합계      │ ₩1,459,000   │ ₩1,322,500   │ ₩264,000           │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ 절감율       │ -            │ 9%           │ 82%                 │
└──────────────┴──────────────┴──────────────┴─────────────────────┘
```

---
