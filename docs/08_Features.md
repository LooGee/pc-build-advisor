# PC Build Advisor - 주요 기능 설계

> 📁 **전체 문서 목차**: [INDEX.md](./INDEX.md)

## 16. 브랜드 선택 기능 설계

사용자가 각 부품(CPU, GPU, MB, RAM, 스토리지, PSU, 케이스, 쿨러)에 대해 선호 브랜드를 지정할 수 있어야 합니다.

### 16.1 브랜드 분류 체계

```python
BRAND_CATALOG = {
    "cpu": {
        "manufacturers": ["Intel", "AMD"],
        "series": {
            "Intel": ["Core i3", "Core i5", "Core i7", "Core i9", "Core Ultra 5", "Core Ultra 7", "Core Ultra 9"],
            "AMD": ["Ryzen 3", "Ryzen 5", "Ryzen 7", "Ryzen 9", "Ryzen Threadripper"]
        }
    },
    "gpu": {
        "chip_manufacturers": ["NVIDIA", "AMD", "Intel"],
        "board_partners": {
            "NVIDIA": ["ASUS", "MSI", "GIGABYTE", "EVGA", "ZOTAC", "Palit", "Gainward", "Inno3D", "PNY", "Colorful"],
            "AMD": ["ASUS", "MSI", "GIGABYTE", "SAPPHIRE", "PowerColor", "XFX", "ASRock"],
            "Intel": ["ASUS", "MSI", "ASRock"]
        }
    },
    "motherboard": {
        "manufacturers": ["ASUS", "MSI", "GIGABYTE", "ASRock", "BIOSTAR"],
        "tiers": {
            "ASUS": ["ROG Maximus", "ROG STRIX", "TUF GAMING", "ProArt", "PRIME"],
            "MSI": ["MEG", "MPG", "MAG", "PRO"],
            "GIGABYTE": ["AORUS MASTER", "AORUS ELITE", "GAMING", "UD"],
            "ASRock": ["Taichi", "Steel Legend", "Phantom Gaming", "Pro"]
        }
    },
    "ram": {
        "manufacturers": ["Samsung", "SK Hynix", "Micron", "G.Skill", "Corsair", "Kingston", "TeamGroup", "Patriot"]
    },
    "storage": {
        "manufacturers": ["Samsung", "SK Hynix", "Western Digital", "Crucial", "Kingston", "Seagate", "Sabrent"]
    },
    "psu": {
        "manufacturers": ["Seasonic", "Corsair", "EVGA", "be quiet!", "FSP", "Thermaltake", "Super Flower", "Antec", "Silverstone", "마이크로닉스", "시소닉"]
    },
    "case": {
        "manufacturers": ["NZXT", "Corsair", "Fractal Design", "be quiet!", "Lian Li", "Phanteks", "Cooler Master", "Thermaltake", "3RSYS", "ABKO", "앱코", "다크플래쉬"]
    },
    "cooler": {
        "manufacturers": ["Noctua", "be quiet!", "Corsair", "NZXT", "Cooler Master", "DeepCool", "Arctic", "Thermalright", "ID-COOLING", "EK"]
    }
}
```

### 16.2 브랜드 선호도 API 스키마

```json
{
    "user_input": "배그를 고사양으로 돌리고 싶어",
    "brand_preferences": {
        "cpu": {
            "manufacturer": "Intel",
            "series": "Core i7",
            "strict": false
        },
        "gpu": {
            "chip_manufacturer": "NVIDIA",
            "board_partner": "ASUS",
            "strict": false
        },
        "motherboard": {
            "manufacturer": "ASUS",
            "tier": "TUF GAMING",
            "strict": true
        },
        "ram": {
            "manufacturer": "G.Skill",
            "strict": false
        },
        "psu": null,
        "case": null,
        "cooler": null,
        "storage": null
    }
}
```

### 16.3 브랜드 필터 적용 로직

```python
# backend/app/services/brand_filter.py

class BrandFilterService:
    """사용자 브랜드 선호도에 따른 부품 필터링"""

    async def filter_components_by_brand(
        self,
        category: str,
        brand_pref: dict | None,
        candidates: list,
        budget_range: tuple
    ) -> list:
        """
        브랜드 선호도에 따라 부품 후보를 필터링/정렬.
        strict=True이면 해당 브랜드만, False이면 해당 브랜드 우선 + 대안 포함.
        """
        if brand_pref is None:
            return candidates

        manufacturer = brand_pref.get("manufacturer")
        strict = brand_pref.get("strict", False)

        if strict:
            filtered = [c for c in candidates if c.brand == manufacturer]
            if not filtered:
                raise BrandNotAvailableError(
                    category=category,
                    brand=manufacturer,
                    message_ko=f"'{manufacturer}' 브랜드의 {CATEGORY_NAMES_KO[category]} 제품이 "
                               f"현재 재고에 없거나 예산 범위(₩{budget_range[0]:,}~₩{budget_range[1]:,}) 내에 "
                               f"해당 브랜드 제품이 없습니다."
                )
            return filtered
        else:
            preferred = [c for c in candidates if c.brand == manufacturer]
            others = [c for c in candidates if c.brand != manufacturer]
            return preferred + others

    async def validate_brand_combination(
        self,
        brand_preferences: dict
    ) -> list:
        """
        브랜드 조합의 논리적 타당성 검증.
        예: AMD CPU + Intel 메인보드는 불가능.
        """
        issues = []

        cpu_brand = brand_preferences.get("cpu", {}).get("manufacturer")
        mb_brand = brand_preferences.get("motherboard", {}).get("manufacturer")

        if cpu_brand == "AMD" and mb_brand:
            pass

        gpu_chip = brand_preferences.get("gpu", {}).get("chip_manufacturer")
        if gpu_chip == "AMD":
            issues.append({
                "type": "info",
                "message_ko": "AMD GPU를 선택하셨습니다. DLSS 대신 FSR을 지원하며, "
                              "CUDA 기반 작업(머신러닝, 영상편집 가속)에는 제한이 있을 수 있습니다."
            })

        return issues
```

### 16.4 프론트엔드 브랜드 선택 UI

```
┌─────────────────────────────────────────────────────┐
│  🏷️ 브랜드 선호도 (선택사항)                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  CPU: [Intel ▼] 시리즈: [Core i7 ▼] [⬜ 이 브랜드만] │
│  GPU 칩: [NVIDIA ▼] 제조사: [전체 ▼]  [⬜ 이 브랜드만] │
│  메인보드: [전체 ▼]   등급: [전체 ▼]  [⬜ 이 브랜드만] │
│  RAM: [전체 ▼]                       [⬜ 이 브랜드만] │
│  저장장치: [전체 ▼]                   [⬜ 이 브랜드만] │
│  파워: [전체 ▼]                      [⬜ 이 브랜드만] │
│  케이스: [전체 ▼]                    [⬜ 이 브랜드만] │
│  쿨러: [전체 ▼]                      [⬜ 이 브랜드만] │
│                                                     │
│  💡 브랜드를 지정하지 않으면 가성비 기준으로 자동 추천  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 18. 예산 및 이슈 알림 시스템

### 18.1 예산 검증 레이어

```python
# backend/app/services/budget_validator.py

from typing import List, Dict, Optional
from pydantic import BaseModel

class BudgetIssue(BaseModel):
    issue_type: str
    severity: str
    title_ko: str
    message_ko: str
    detail_ko: str
    suggestion_ko: str

class BudgetValidator:
    """예산 관련 이슈 검증 및 알림"""

    async def validate_budget(
        self,
        budget: dict,
        quote_components: list,
        requirements: dict
    ) -> List[BudgetIssue]:
        issues = []

        total_price = sum(c.price_krw for c in quote_components)
        max_budget = budget.get("max")
        min_budget = budget.get("min")

        if max_budget and total_price > max_budget:
            overflow = total_price - max_budget
            overflow_pct = (overflow / max_budget) * 100
            issues.append(BudgetIssue(
                issue_type="over_budget",
                severity="error" if overflow_pct > 20 else "warning",
                title_ko="예산 초과",
                message_ko=f"총 견적 금액 ₩{total_price:,}이(가) "
                           f"설정 예산 ₩{max_budget:,}을(를) "
                           f"₩{overflow:,} ({overflow_pct:.1f}%) 초과합니다.",
                detail_ko=self._get_price_breakdown(quote_components),
                suggestion_ko=self._get_cost_saving_suggestions(
                    quote_components, overflow, requirements
                )
            ))

        if max_budget and total_price < max_budget * 0.5:
            remaining = max_budget - total_price
            issues.append(BudgetIssue(
                issue_type="under_budget",
                severity="info",
                title_ko="예산 여유",
                message_ko=f"₩{remaining:,}의 예산이 남습니다. "
                           f"더 좋은 부품으로 업그레이드가 가능합니다.",
                detail_ko=f"현재 총 금액: ₩{total_price:,} / 예산: ₩{max_budget:,}",
                suggestion_ko=self._get_upgrade_suggestions(
                    quote_components, remaining, requirements
                )
            ))

        if max_budget and 0 < (max_budget - total_price) < max_budget * 0.05:
            issues.append(BudgetIssue(
                issue_type="tight_budget",
                severity="warning",
                title_ko="예산 근접",
                message_ko=f"총 견적이 ₩{total_price:,}으로 "
                           f"예산(₩{max_budget:,})에 매우 근접합니다. "
                           f"가격 변동 시 초과할 수 있습니다.",
                detail_ko="PC 부품 가격은 실시간으로 변동됩니다. "
                          "구매 시점에 따라 ₩10,000~₩50,000 변동 가능합니다.",
                suggestion_ko="가격 알림을 설정하거나, 약간의 여유 예산을 확보하세요."
            ))

        issues.extend(await self._check_budget_balance(quote_components, total_price, requirements))
        issues.extend(self._check_missing_essentials(quote_components))
        issues.extend(await self._check_requirements_feasibility(budget, requirements))

        return issues
```

### 18.2 이슈 통합 응답

```json
{
    "quotes": [],
    "issues": {
        "budget_issues": [
            {
                "issue_type": "over_budget",
                "severity": "warning",
                "title_ko": "최대 견적이 예산을 약간 초과합니다",
                "message_ko": "Maximum 견적(₩1,580,000)이 예산(₩1,500,000)을 ₩80,000 초과합니다.",
                "suggestion_ko": "GPU를 RTX 4070에서 RTX 4060 Ti로 변경하면 예산 내 구성이 가능합니다."
            }
        ],
        "compatibility_issues": [],
        "availability_issues": [
            {
                "issue_type": "out_of_stock",
                "severity": "warning",
                "component": "Samsung 990 Pro 2TB",
                "message_ko": "현재 다나와, 컴퓨종에서 품절입니다. 쿠팡에서만 구매 가능합니다.",
                "alternatives": []
            }
        ],
        "general_notices": [
            {
                "type": "info",
                "message_ko": "Windows 11 라이선스 비용(약 ₩200,000)은 견적에 포함되지 않았습니다."
            }
        ]
    }
}
```

---

## 20. 구매 링크 안내 시스템

### 20.1 링크 제공 전략

```python
# backend/app/services/purchase_link_service.py

class PurchaseLinkService:
    """부품별 최적 구매 링크 제공"""

    SITE_INFO = {
        "danawa": {
            "name": "다나와",
            "logo": "/images/logos/danawa.png",
            "base_url": "https://www.danawa.com",
            "features": ["최저가 비교", "가격 추이"],
            "color": "#0066CC"
        },
        "compuzone": {
            "name": "컴퓨존",
            "logo": "/images/logos/compuzone.png",
            "base_url": "https://www.compuzone.co.kr",
            "features": ["PC 부품 전문", "기술 지원"],
            "color": "#FF6600"
        },
        "coupang": {
            "name": "쿠팡",
            "logo": "/images/logos/coupang.png",
            "base_url": "https://www.coupang.com",
            "features": ["로켓배송", "무료반품"],
            "color": "#E4002B"
        },
        "pcpartpicker": {
            "name": "PCPartPicker",
            "logo": "/images/logos/pcpartpicker.png",
            "base_url": "https://pcpartpicker.com",
            "features": ["해외 가격", "호환성 참고"],
            "color": "#FFCC00"
        }
    }

    async def generate_purchase_links(
        self,
        quote_components: list
    ) -> dict:
        """견적의 모든 부품에 대해 최적 구매 링크 생성"""

        result = {
            "components": [],
            "total_by_site": {},
            "optimal_strategy": {},
            "one_click_cart": {}
        }

        for comp in quote_components:
            prices = await self._get_all_prices(comp.id)
            cheapest = min(prices, key=lambda p: p.total_price_krw)

            comp_links = {
                "component_id": comp.id,
                "category": comp.category,
                "name": f"{comp.brand} {comp.model}",
                "recommended_purchase": {
                    "site": cheapest.source,
                    "site_name": self.SITE_INFO[cheapest.source]["name"],
                    "price_krw": cheapest.total_price_krw,
                    "url": cheapest.product_url,
                    "in_stock": cheapest.in_stock,
                    "shipping": "로켓배송" if cheapest.rocket_delivery else "일반배송",
                    "badge": "최저가" if cheapest == min(prices, key=lambda p: p.price_krw) else None
                },
                "all_sites": [
                    {
                        "site": p.source,
                        "site_name": self.SITE_INFO[p.source]["name"],
                        "site_logo": self.SITE_INFO[p.source]["logo"],
                        "site_color": self.SITE_INFO[p.source]["color"],
                        "price_krw": p.price_krw,
                        "shipping_cost_krw": p.shipping_cost_krw,
                        "total_price_krw": p.total_price_krw,
                        "url": p.product_url,
                        "in_stock": p.in_stock,
                        "is_cheapest": p == cheapest,
                        "features": self.SITE_INFO[p.source]["features"],
                        "last_checked": p.last_checked.isoformat()
                    }
                    for p in sorted(prices, key=lambda x: x.total_price_krw)
                ]
            }
            result["components"].append(comp_links)

        result["optimal_strategy"] = await self._calculate_optimal_strategy(result["components"])

        return result

    async def _calculate_optimal_strategy(self, components: list) -> dict:
        """
        전체 부품을 가장 저렴하게 구매할 수 있는 최적 조합.
        사이트별 배송비를 고려하여 한 사이트에서 몰아 사는 것이
        개별 최저가보다 나을 수 있음.
        """
        strategies = {
            "cheapest_per_item": {
                "description_ko": "부품별 최저가 사이트에서 개별 구매",
                "total_krw": 0,
                "items": [],
                "sites_count": 0,
                "pros": "총 가격 가장 저렴",
                "cons": "여러 사이트에서 주문, 배송 일정 다름"
            },
            "single_site_best": {
                "description_ko": "한 사이트에서 전부 구매 (배송비 절약)",
                "total_krw": 0,
                "site": "",
                "items": [],
                "pros": "배송 통합, AS 편리",
                "cons": "개별 최저가보다 약간 비쌀 수 있음"
            },
            "recommended": {
                "description_ko": "추천 전략 (가격 + 편의성 균형)",
                "total_krw": 0,
                "items": [],
                "reasoning_ko": ""
            }
        }

        return strategies
```

### 20.2 프론트엔드 구매 링크 UI

```
┌─────────────────────────────────────────────────────────────┐
│ 🛒 구매 가이드                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📌 추천 구매 전략: 다나와 + 쿠팡 혼합 (총 ₩1,425,000)       │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ CPU: Intel Core i7-14700K                               │ │
│ │ ┌──────────────────────────────────────────────────┐    │ │
│ │ │ 🏷️ 다나와  ₩445,000  ✅ 최저가  [구매하기 →]      │    │ │
│ │ │ 🚀 쿠팡   ₩450,000  로켓배송  [구매하기 →]       │    │ │
│ │ │ 🖥️ 컴퓨존  ₩452,000  재고있음  [구매하기 →]      │    │ │
│ │ └──────────────────────────────────────────────────┘    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ GPU: NVIDIA RTX 4070 SUPER (ASUS TUF)                  │ │
│ │ ┌──────────────────────────────────────────────────┐    │ │
│ │ │ 🖥️ 컴퓨존  ₩598,000  ✅ 최저가  [구매하기 →]      │    │ │
│ │ │ 🏷️ 다나와  ₩605,000            [구매하기 →]       │    │ │
│ │ │ 🚀 쿠팡   ₩615,000  로켓배송  [구매하기 →]       │    │ │
│ │ └──────────────────────────────────────────────────┘    │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ... (나머지 부품들)                                         │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 💰 총 합계 비교                                         │ │
│ │                                                         │ │
│ │  부품별 최저가 구매: ₩1,420,000 (4개 사이트 주문)       │ │
│ │  다나와 한곳 구매:   ₩1,445,000 (배송비 통합)          │ │
│ │  쿠팡 한곳 구매:     ₩1,460,000 (로켓배송, 내일 도착)  │ │
│ │                                                         │ │
│ │  ⭐ 추천: 다나와 + 쿠팡 혼합 = ₩1,425,000              │ │
│ │     (GPU/PSU는 컴퓨존, 나머지는 쿠팡 로켓배송)         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ⚠️ 가격은 {last_updated} 기준이며 실시간 변동될 수 있습니다 │
│  [🔄 가격 새로고침]                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 20.3 링크 유효성 검증

```python
class LinkValidator:
    """구매 링크 유효성 주기적 검증"""

    async def validate_links(self, component_id: str) -> list:
        """모든 구매 링크의 유효성 검증"""
        prices = await self.db.get_prices(component_id)
        results = []

        for price in prices:
            try:
                status = await self._check_url(price.product_url)
                results.append({
                    "url": price.product_url,
                    "source": price.source,
                    "status": status,
                    "price_still_valid": await self._verify_price(price)
                })
            except Exception:
                results.append({
                    "url": price.product_url,
                    "source": price.source,
                    "status": "unreachable"
                })

        return results
```

---
