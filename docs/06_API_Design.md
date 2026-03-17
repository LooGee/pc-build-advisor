# PC Build Advisor - API 엔드포인트 설계

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 9. API 엔드포인트 설계 (상세)

### 9.1 주요 엔드포인트

#### POST /api/v1/quotes/generate
**요청 (Request)**
```json
{
  "user_input": "배틀그라운드를 고사양으로 돌리고 싶은데 예산은 150만원",
  "user_session_id": "session_abc123xyz",
  "llm_provider": "claude" | "gpt4"
}
```

**응답 (Response)**
```json
{
  "id": "quote_12345",
  "user_input": "배틀그라운드를 고사양으로 돌리고 싶은데 예산은 150만원",
  "analyzed_requirements": {
    "primary_use": "gaming",
    "specific_software_games": ["PlayerUnknown's Battlegrounds"],
    "performance_tier": "max",
    "budget": {
      "min": null,
      "max": 1500000,
      "currency": "KRW"
    },
    "preferences": {
      "color": null,
      "size": null,
      "brands": [],
      "features": [],
      "monitor_resolution": "1080p",
      "target_fps": 144
    },
    "priority": "performance"
  },
  "quotes": [
    {
      "tier": "minimum",
      "tier_name": "최소 요구사항",
      "tier_description": "배그 고설정 1080p 144fps 최소 충족",
      "total_price_krw": 1450000,
      "components_price_krw": 1420000,
      "shipping_cost_krw": 30000,
      "components": [
        {
          "category": "cpu",
          "id": "cpu_xyz",
          "brand": "Intel",
          "model": "Core i7-14700K",
          "image_url": "https://...",
          "specifications": {
            "cores": 20,
            "threads": 28,
            "base_clock_ghz": 3.4,
            "boost_clock_ghz": 6.0,
            "tdp_w": 125,
            "socket": "LGA1700"
          },
          "price_info": {
            "price_krw": 450000,
            "sources": [
              {
                "source": "danawa",
                "price_krw": 445000,
                "url": "https://danawa.com/...",
                "in_stock": true
              },
              {
                "source": "coupang",
                "price_krw": 450000,
                "url": "https://coupang.com/...",
                "in_stock": true,
                "shipping": "rocket"
              }
            ]
          },
          "compatibility_status": "ok",
          "compatibility_notes": ""
        },
        {
          "category": "gpu",
          "id": "gpu_abc",
          "brand": "NVIDIA",
          "model": "GeForce RTX 4070 SUPER",
          "image_url": "https://...",
          "specifications": {
            "vram_size_gb": 12,
            "vram_type": "GDDR6X",
            "base_clock_mhz": 2475,
            "boost_clock_mhz": 2610,
            "tdp_w": 220,
            "length_mm": 286,
            "ray_tracing_supported": true,
            "dlss_supported": true,
            "dlss_version": "3.5"
          },
          "price_info": {
            "price_krw": 600000,
            "sources": [
              {
                "source": "compuzone",
                "price_krw": 598000,
                "url": "https://compuzone.com/..."
              }
            ]
          },
          "compatibility_status": "ok"
        }
        // ... 나머지 부품 (MB, RAM, SSD, PSU, Case, Cooler)
      ],
      "compatibility": {
        "is_compatible": true,
        "issues": []
      },
      "estimated_performance": {
        "cpu_benchmark_score": 55000,
        "gpu_benchmark_score": 15000,
        "estimated_gaming_fps_1080p": 110,
        "estimated_gaming_fps_1440p": 75,
        "estimated_power_consumption_w": 550
      }
    },
    {
      "tier": "balanced",
      "tier_name": "균형 조화형",
      "tier_description": "뛰어난 성능과 가성비의 조화",
      "total_price_krw": 1480000,
      // ... (similar structure)
    },
    {
      "tier": "maximum",
      "tier_name": "최고 성능형",
      "tier_description": "배그 최고설정 4K 144fps",
      "total_price_krw": 1499000,
      // ... (similar structure)
    }
  ],
  "created_at": "2026-03-17T12:34:56Z",
  "expires_at": "2026-03-20T12:34:56Z"
}
```

#### GET /api/v1/quotes/{id}
**응답**: 저장된 견적 조회 (위와 동일한 구조)

#### POST /api/v1/quotes/{id}/customize
**요청**
```json
{
  "tier": "minimum",
  "component_changes": [
    {
      "category": "gpu",
      "old_id": "gpu_abc",
      "new_id": "gpu_def"
    }
  ]
}
```

**응답**
```json
{
  "id": "quote_12345_v2",
  "parent_quote_id": "quote_12345",
  "tier": "minimum",
  "total_price_krw": 1520000,
  "components": [
    // 업데이트된 부품 목록
  ],
  "compatibility": {
    "is_compatible": true,
    "issues": []
  }
}
```

#### GET /api/v1/components
**요청 파라미터**
```
?category=gpu&brand=NVIDIA&min_vram=8&max_price=800000&page=1&limit=20
```

**응답**
```json
{
  "total": 256,
  "page": 1,
  "limit": 20,
  "items": [
    {
      "id": "gpu_xyz",
      "brand": "NVIDIA",
      "model": "GeForce RTX 4070 SUPER",
      "category": "gpu",
      "specifications": { /* ... */ },
      "prices": [
        {
          "source": "danawa",
          "price_krw": 600000,
          "in_stock": true
        }
      ],
      "average_price_krw": 605000,
      "min_price_krw": 598000,
      "max_price_krw": 615000
    }
  ]
}
```

#### GET /api/v1/components/{id}
**응답**: 부품 상세 정보 (모든 스펙 + 가격 비교)

#### GET /api/v1/components/{id}/prices
**응답**
```json
{
  "component_id": "gpu_xyz",
  "brand": "NVIDIA",
  "model": "RTX 4070 SUPER",
  "prices": [
    {
      "source": "danawa",
      "price_krw": 600000,
      "shipping_cost_krw": 0,
      "total_price_krw": 600000,
      "in_stock": true,
      "url": "https://danawa.com/...",
      "updated_at": "2026-03-17T12:00:00Z"
    },
    {
      "source": "compuzone",
      "price_krw": 598000,
      "shipping_cost_krw": 5000,
      "total_price_krw": 603000,
      "in_stock": true,
      "url": "https://compuzone.com/...",
      "updated_at": "2026-03-17T11:30:00Z"
    },
    {
      "source": "coupang",
      "price_krw": 615000,
      "shipping_cost_krw": 0,
      "total_price_krw": 615000,
      "in_stock": true,
      "shipping": "rocket",
      "url": "https://coupang.com/...",
      "updated_at": "2026-03-17T12:15:00Z"
    }
  ],
  "average_price_krw": 605000,
  "cheapest": {
    "source": "compuzone",
    "total_price_krw": 603000,
    "url": "https://compuzone.com/..."
  }
}
```

#### POST /api/v1/compatibility/check
**요청**
```json
{
  "component_ids": {
    "cpu": "cpu_xyz",
    "motherboard": "mb_123",
    "ram": "ram_456",
    "gpu": "gpu_789",
    "psu": "psu_000",
    "case": "case_111",
    "cooler": "cooler_222",
    "storages": ["ssd_333", "hdd_444"]
  }
}
```

**응답**
```json
{
  "is_compatible": true,
  "issues": [
    {
      "id": "compat_04",
      "type": "memory_speed",
      "severity": "warning",
      "component_a": "ram",
      "component_b": "cpu",
      "message_ko": "RAM이 CPU 지원 속도보다 빠릅니다. CPU 최대 속도(5600MHz)로 다운클록됩니다.",
      "recommendation_ko": "6000MHz RAM 대신 5600MHz RAM 선택을 추천합니다."
    }
  ],
  "warnings_count": 1,
  "errors_count": 0
}
```

#### GET /api/v1/games
**응답**
```json
{
  "games": [
    {
      "id": "game_pubg",
      "name": "PlayerUnknown's Battlegrounds",
      "aliases": ["PUBG", "배그", "배틀그라운드"],
      "genre": "Battle Royale",
      "min_requirements": {
        "cpu_benchmark": 8000,
        "gpu_benchmark": 8000,
        "ram_gb": 16
      },
      "recommended_requirements": {
        "cpu_benchmark": 12000,
        "gpu_benchmark": 11000,
        "ram_gb": 16
      }
    }
  ]
}
```

---
