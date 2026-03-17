# PC Build Advisor - 설계 문서 목차

> **PC 견적 자동 추천 시스템** 아키텍처 설계 문서 v4
>
> 원본 문서(5,251줄)를 개발 편의를 위해 카테고리별로 분리했습니다.

---

## 문서 구조

| # | 파일 | 내용 | 원본 섹션 |
|---|------|------|-----------|
| 00 | [00_Overview.md](./00_Overview.md) | 프로젝트 개요, 기술 스택, 시스템 아키텍처 | §1~3 |
| 01 | [01_Project_Structure.md](./01_Project_Structure.md) | 프로젝트 디렉토리 구조 (6개 파트) | §4 |
| 02 | [02_Database.md](./02_Database.md) | DB 스키마 16개 테이블 (SQL DDL) | §5 |
| 03 | [03_Compatibility_Engine.md](./03_Compatibility_Engine.md) | 호환성 체크 엔진 18개 규칙 + 오류 메시지 카탈로그 | §6, §17 |
| 04 | [04_AI_LLM.md](./04_AI_LLM.md) | LLM 요구사항 분석 + 모델 역할별 분리 전략 | §7, §19 |
| 05 | [05_Crawler.md](./05_Crawler.md) | 크롤링 시스템 (다나와/컴퓨존/쿠팡/PCPartPicker) | §8 |
| 06 | [06_API_Design.md](./06_API_Design.md) | API 엔드포인트 설계 (Request/Response 스키마) | §9 |
| 07 | [07_Frontend.md](./07_Frontend.md) | 프론트엔드 UI/UX 설계 (와이어프레임) | §10 |
| 08 | [08_Features.md](./08_Features.md) | 브랜드 선택, 예산 알림, 구매 링크 안내 | §16, §18, §20 |
| 09 | [09_DevOps_Deploy.md](./09_DevOps_Deploy.md) | AWS 배포, 비용 최적화, DX, 초절약 플랜 | §23~26 |
| 10 | [10_Quality_Security.md](./10_Quality_Security.md) | 로드맵, 도전과제, 성능, 보안, 점검, 주석 표준, 결론 | §11~15, §21~22, 결론 |

---

## 개발 파트별 참조 가이드

### Frontend 개발자
→ [01_Project_Structure.md](./01_Project_Structure.md) (frontend/ 구조)
→ [07_Frontend.md](./07_Frontend.md) (UI/UX 와이어프레임)
→ [06_API_Design.md](./06_API_Design.md) (API 스키마)
→ [08_Features.md](./08_Features.md) (브랜드 선택 UI, 구매 링크 UI)

### Backend 개발자
→ [01_Project_Structure.md](./01_Project_Structure.md) (backend/ 구조)
→ [02_Database.md](./02_Database.md) (DB 스키마)
→ [03_Compatibility_Engine.md](./03_Compatibility_Engine.md) (호환성 엔진)
→ [06_API_Design.md](./06_API_Design.md) (API 엔드포인트)
→ [08_Features.md](./08_Features.md) (예산 검증, 구매 링크 서비스)

### AI/LLM 개발자
→ [01_Project_Structure.md](./01_Project_Structure.md) (ai-service/ 구조)
→ [04_AI_LLM.md](./04_AI_LLM.md) (LLM 분석 + 모델 라우팅)
→ [09_DevOps_Deploy.md](./09_DevOps_Deploy.md) §26 (DeepSeek 초절약 플랜)

### Crawler 개발자
→ [01_Project_Structure.md](./01_Project_Structure.md) (crawler-service/ 구조)
→ [05_Crawler.md](./05_Crawler.md) (크롤링 시스템)

### DevOps / 인프라
→ [09_DevOps_Deploy.md](./09_DevOps_Deploy.md) (AWS, CI/CD, 비용)
→ [10_Quality_Security.md](./10_Quality_Security.md) (모니터링, 보안)

---

## 비용 요약

| 플랜 | 월 비용 | 비고 |
|------|---------|------|
| 기존 (v3) | ₩1,404,000 | ECS Fargate + Claude Sonnet |
| 최적화 (v3) | ₩1,320,000 | Spot + Reserved + VPC Endpoint |
| **초절약 (v4)** | **₩264,000** | **Serverless + DeepSeek V3.2 (82% 절감)** |
| 개발 단계 | ₩20,000 | 무료 티어 최대 활용 |

> 상세: [09_DevOps_Deploy.md](./09_DevOps_Deploy.md) §24, §26 참고
