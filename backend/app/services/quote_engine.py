import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.schemas.quote import (
    QuoteGenerateRequest, QuoteGenerateResponse, QuoteTierResult,
    QuoteComponentDetail, ComponentPriceInfo, PriceSourceInfo,
    AnalyzedRequirements, EstimatedPerformance, BudgetSchema, PreferencesSchema
)
from app.services.compatibility.checker import CompatibilityChecker
from app.db.repositories.component_repo import ComponentRepository
from app.db.repositories.price_repo import PriceRepository
from app.db.repositories.game_repo import GameRepository
from app.cache.cache_service import CacheService
from app.models.component import Component
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.motherboard import Motherboard
from app.models.ram import RAM
from app.models.storage import Storage
from app.models.psu import PSU
from app.models.case import Case
from app.models.cooler import Cooler
from app.models.price import Price
import logging

logger = logging.getLogger(__name__)

# Budget allocation per component category (gaming PC)
GAMING_BUDGET_ALLOCATION = {
    "gpu": 0.38,
    "cpu": 0.22,
    "motherboard": 0.12,
    "ram": 0.09,
    "storage": 0.07,
    "psu": 0.07,
    "case": 0.06,
    "cooler": 0.05,
}

WORKSTATION_BUDGET_ALLOCATION = {
    "cpu": 0.30,
    "ram": 0.18,
    "gpu": 0.25,
    "storage": 0.12,
    "motherboard": 0.07,
    "psu": 0.04,
    "case": 0.03,
    "cooler": 0.01,
}

TIER_BUDGET_RATIO = {
    "minimum": 0.70,
    "balanced": 0.85,
    "maximum": 1.00,
}

TIER_NAMES = {
    "minimum": ("최소 요구사항", "기본 요구사항을 충족하는 가성비 구성"),
    "balanced": ("균형 조화형", "뛰어난 성능과 가성비의 최적 조합"),
    "maximum": ("최고 성능형", "예산 내 최고 성능 구성"),
}

# Estimated FPS per GPU 3DMark TimeSpy score (rough approximation)
# score → (fps_1080p, fps_1440p)
GPU_FPS_MAP = [
    (25000, (200, 150)),
    (20000, (160, 120)),
    (17000, (144, 110)),
    (15000, (120, 90)),
    (12000, (100, 75)),
    (10000, (80, 60)),
    (8000,  (60, 45)),
    (6000,  (50, 35)),
    (4000,  (40, 28)),
]


def estimate_fps(gpu_benchmark: int) -> tuple[int, int]:
    for score, fps in GPU_FPS_MAP:
        if gpu_benchmark >= score:
            return fps
    return (30, 20)


class QuoteEngine:
    def __init__(self, db: AsyncSession, cache: CacheService, ai_client):
        self.db = db
        self.cache = cache
        self.ai_client = ai_client
        self.component_repo = ComponentRepository(db)
        self.price_repo = PriceRepository(db)
        self.game_repo = GameRepository(db)
        self.compat_checker = CompatibilityChecker(db)

    async def generate(self, request: QuoteGenerateRequest) -> QuoteGenerateResponse:
        # Step 1: Analyze requirements via AI service
        requirements = await self._analyze_requirements(request.user_input, request.llm_provider)

        # Step 2: Generate 3 tiers
        quotes = []
        for tier in ["minimum", "balanced", "maximum"]:
            quote = await self._build_tier_quote(tier, requirements)
            if quote:
                quotes.append(quote)

        quote_id = str(uuid.uuid4())
        return QuoteGenerateResponse(
            id=quote_id,
            user_input=request.user_input,
            analyzed_requirements=requirements,
            quotes=quotes,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=3),
        )

    async def _analyze_requirements(self, user_input: str, provider: str = "claude") -> AnalyzedRequirements:
        cached = await self.cache.get_llm_analysis(user_input)
        if cached:
            return AnalyzedRequirements(**cached)

        if self.ai_client:
            try:
                response = await self.ai_client.post(
                    "/analyze",
                    json={"user_input": user_input, "provider": provider}
                )
                if response.status_code == 200:
                    data = response.json()
                    reqs = AnalyzedRequirements(**data)
                    await self.cache.set_llm_analysis(user_input, data)
                    return reqs
            except Exception as e:
                logger.warning(f"AI service unavailable: {e}")

        return self._parse_requirements_fallback(user_input)

    def _parse_requirements_fallback(self, user_input: str) -> AnalyzedRequirements:
        budget_max = 1500000
        for token in user_input.split():
            if "만원" in token:
                try:
                    amount = int(token.replace("만원", "").replace(",", "")) * 10000
                    budget_max = amount
                except ValueError:
                    pass

        tier = "mid"
        if any(kw in user_input for kw in ["고사양", "최고", "최상", "울트라"]):
            tier = "max"
        elif any(kw in user_input for kw in ["저사양", "저예산", "싸게", "가성비"]):
            tier = "min"

        return AnalyzedRequirements(
            primary_use="gaming",
            specific_software_games=[],
            performance_tier=tier,
            budget=BudgetSchema(max=budget_max),
            preferences=PreferencesSchema(),
            priority="balanced",
        )

    async def _build_tier_quote(self, tier: str, requirements: AnalyzedRequirements) -> Optional[QuoteTierResult]:
        budget = requirements.budget.max
        tier_budget = int(budget * TIER_BUDGET_RATIO[tier])
        name, desc = TIER_NAMES[tier]

        # Choose allocation based on primary use
        allocation = (
            WORKSTATION_BUDGET_ALLOCATION
            if requirements.primary_use in ("workstation", "3d_rendering", "video_editing")
            else GAMING_BUDGET_ALLOCATION
        )

        component_budgets = {cat: int(tier_budget * ratio) for cat, ratio in allocation.items()}

        # Sequential selection with compatibility constraints
        selected_components: Dict[str, Any] = {}
        selected_models: Dict[str, Any] = {}

        # 1. Select CPU
        cpu_comp, cpu_model = await self._select_component_with_model(
            "cpu", component_budgets["cpu"],
            order_by_benchmark=True,
            preferred_brands=requirements.preferences.brands,
        )
        if cpu_comp:
            selected_components["cpu"] = cpu_comp
            selected_models["cpu"] = cpu_model

        # 2. Select Motherboard (must match CPU socket + DDR type)
        cpu_socket = cpu_model.socket if cpu_model else None
        cpu_ddr = cpu_model.supported_memory_type if cpu_model else None
        mb_comp, mb_model = await self._select_motherboard(
            component_budgets["motherboard"], cpu_socket, cpu_ddr,
            preferred_brands=requirements.preferences.brands,
        )
        if mb_comp:
            selected_components["motherboard"] = mb_comp
            selected_models["motherboard"] = mb_model

        # 3. Select RAM (must match MB DDR type)
        ddr_type = mb_model.memory_type if mb_model else (cpu_ddr or "DDR5")
        ram_comp, ram_model = await self._select_component_with_model(
            "ram", component_budgets["ram"],
            extra_filters={"type": ddr_type},
        )
        if ram_comp:
            selected_components["ram"] = ram_comp
            selected_models["ram"] = ram_model

        # 4. Select GPU
        gpu_comp, gpu_model = await self._select_component_with_model(
            "gpu", component_budgets["gpu"],
            order_by_benchmark=True,
            preferred_brands=requirements.preferences.brands,
        )
        if gpu_comp:
            selected_components["gpu"] = gpu_comp
            selected_models["gpu"] = gpu_model

        # 5. Select PSU (wattage = CPU TDP + GPU TDP + 100W overhead * 1.2)
        cpu_tdp = cpu_model.tdp_w if cpu_model else 125
        gpu_tdp = gpu_model.tdp_w if gpu_model else 220
        required_wattage = int((cpu_tdp + gpu_tdp + 100) * 1.2)
        psu_comp, psu_model = await self._select_psu(
            component_budgets["psu"], required_wattage,
        )
        if psu_comp:
            selected_components["psu"] = psu_comp
            selected_models["psu"] = psu_model

        # 6. Select Case (must fit MB form factor and GPU length)
        mb_form = mb_model.form_factor if mb_model else "ATX"
        gpu_length = gpu_model.length_mm if gpu_model else 300
        case_comp, case_model = await self._select_case(
            component_budgets["case"], mb_form, gpu_length,
        )
        if case_comp:
            selected_components["case"] = case_comp
            selected_models["case"] = case_model

        # 7. Select Cooler (must support CPU socket)
        cooler_comp, cooler_model = await self._select_cooler(
            component_budgets["cooler"], cpu_socket, cpu_tdp,
        )
        if cooler_comp:
            selected_components["cooler"] = cooler_comp
            selected_models["cooler"] = cooler_model

        # 8. Select Storage
        storage_comp, storage_model = await self._select_component_with_model(
            "storage", component_budgets["storage"],
            order_by_benchmark=False,
        )
        if storage_comp:
            selected_components["storage"] = storage_comp
            selected_models["storage"] = storage_model

        # Build component detail list with prices
        component_details = []
        total_price = 0

        for category, comp in selected_components.items():
            price_info = await self._get_price_info(comp.id)
            unit_price = price_info["price_krw"] if price_info else 0
            total_price += unit_price

            # Get specs from model
            model_obj = selected_models.get(category)
            specs = self._extract_specs(category, comp, model_obj)

            component_details.append(QuoteComponentDetail(
                category=category,
                id=str(comp.id),
                brand=comp.brand,
                model=comp.model,
                image_url=comp.image_url,
                specifications=specs,
                price_info=ComponentPriceInfo(
                    price_krw=unit_price,
                    sources=[
                        PriceSourceInfo(
                            source=s["source"],
                            price_krw=s["price_krw"],
                            url=s.get("url"),
                            in_stock=s.get("in_stock", True),
                        )
                        for s in price_info.get("sources", [])
                    ] if price_info else [],
                ),
                compatibility_status="ok",
                compatibility_notes="",
            ))

        # Run compatibility check
        compat_result = await self._check_compatibility(selected_components)

        # Estimate performance
        gpu_benchmark = gpu_model.tdmark_timespy_score if gpu_model and gpu_model.tdmark_timespy_score else 10000
        cpu_benchmark = cpu_model.cinebench_r23_multi_core if cpu_model and cpu_model.cinebench_r23_multi_core else 20000
        fps_1080p, fps_1440p = estimate_fps(gpu_benchmark)
        total_power = int((cpu_tdp + gpu_tdp) * 0.85)  # ~85% load

        return QuoteTierResult(
            tier=tier,
            tier_name=name,
            tier_description=desc,
            total_price_krw=total_price,
            components_price_krw=total_price,
            shipping_cost_krw=0,
            components=component_details,
            compatibility=compat_result,
            estimated_performance=EstimatedPerformance(
                cpu_benchmark_score=cpu_benchmark,
                gpu_benchmark_score=gpu_benchmark,
                estimated_gaming_fps_1080p=fps_1080p,
                estimated_gaming_fps_1440p=fps_1440p,
                estimated_power_consumption_w=total_power,
            ),
        )

    async def _select_component_with_model(
        self,
        category: str,
        budget: int,
        order_by_benchmark: bool = False,
        extra_filters: dict = None,
        preferred_brands: list = None,
    ):
        """Select best component within budget. Returns (Component, ModelObj) tuple."""
        MODEL_MAP = {
            "cpu": CPU, "gpu": GPU, "ram": RAM,
            "storage": Storage, "psu": PSU, "case": Case, "cooler": Cooler,
        }
        model_class = MODEL_MAP.get(category)
        if not model_class:
            return None, None

        # Subquery: min price per component
        min_price_sq = (
            select(Price.component_id, func.min(Price.price_krw).label("min_price"))
            .where(and_(Price.in_stock == True, Price.price_krw <= budget))
            .group_by(Price.component_id)
            .subquery()
        )

        query = (
            select(Component, model_class, min_price_sq.c.min_price)
            .join(model_class, Component.id == model_class.id)
            .join(min_price_sq, Component.id == min_price_sq.c.component_id)
            .where(and_(
                Component.category == category,
                Component.is_active == True,
            ))
        )

        if extra_filters:
            for field, value in extra_filters.items():
                query = query.where(getattr(model_class, field) == value)

        if preferred_brands:
            query = query.where(Component.brand.in_(preferred_brands))

        if order_by_benchmark:
            benchmark_col = self._get_benchmark_col(category, model_class)
            if benchmark_col is not None:
                query = query.order_by(benchmark_col.desc().nullslast())
            else:
                query = query.order_by(min_price_sq.c.min_price.desc())
        else:
            query = query.order_by(min_price_sq.c.min_price.desc())

        query = query.limit(1)
        result = await self.db.execute(query)
        row = result.first()

        if not row:
            # Retry without brand preference
            if preferred_brands:
                return await self._select_component_with_model(
                    category, budget, order_by_benchmark, extra_filters, preferred_brands=None
                )
            return None, None

        return row[0], row[1]

    def _get_benchmark_col(self, category: str, model_class):
        if category == "cpu":
            return model_class.cinebench_r23_multi_core
        elif category == "gpu":
            return model_class.tdmark_timespy_score
        elif category == "cooler":
            return model_class.tdp_rating_w
        return None

    async def _select_motherboard(self, budget: int, cpu_socket: str, ddr_type: str, preferred_brands: list = None):
        min_price_sq = (
            select(Price.component_id, func.min(Price.price_krw).label("min_price"))
            .where(and_(Price.in_stock == True, Price.price_krw <= budget))
            .group_by(Price.component_id)
            .subquery()
        )

        query = (
            select(Component, Motherboard, min_price_sq.c.min_price)
            .join(Motherboard, Component.id == Motherboard.id)
            .join(min_price_sq, Component.id == min_price_sq.c.component_id)
            .where(and_(
                Component.category == "motherboard",
                Component.is_active == True,
            ))
            .order_by(min_price_sq.c.min_price.desc())
            .limit(1)
        )

        if cpu_socket:
            query = query.where(Motherboard.socket == cpu_socket)
        if ddr_type:
            query = query.where(Motherboard.memory_type == ddr_type)
        if preferred_brands:
            query = query.where(Component.brand.in_(preferred_brands))

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            if preferred_brands:
                return await self._select_motherboard(budget, cpu_socket, ddr_type)
            # Relax DDR constraint
            if ddr_type:
                return await self._select_motherboard(budget, cpu_socket, None)
            return None, None

        return row[0], row[1]

    async def _select_psu(self, budget: int, required_wattage: int):
        min_price_sq = (
            select(Price.component_id, func.min(Price.price_krw).label("min_price"))
            .where(and_(Price.in_stock == True, Price.price_krw <= budget))
            .group_by(Price.component_id)
            .subquery()
        )

        query = (
            select(Component, PSU, min_price_sq.c.min_price)
            .join(PSU, Component.id == PSU.id)
            .join(min_price_sq, Component.id == min_price_sq.c.component_id)
            .where(and_(
                Component.category == "psu",
                Component.is_active == True,
                PSU.wattage >= required_wattage,
            ))
            .order_by(PSU.wattage.asc())  # Cheapest sufficient wattage
            .limit(1)
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            # Relax wattage if nothing found, just pick best within budget
            return await self._select_component_with_model("psu", budget)

        return row[0], row[1]

    async def _select_case(self, budget: int, mb_form_factor: str, gpu_length_mm: int):
        min_price_sq = (
            select(Price.component_id, func.min(Price.price_krw).label("min_price"))
            .where(and_(Price.in_stock == True, Price.price_krw <= budget))
            .group_by(Price.component_id)
            .subquery()
        )

        query = (
            select(Component, Case, min_price_sq.c.min_price)
            .join(Case, Component.id == Case.id)
            .join(min_price_sq, Component.id == min_price_sq.c.component_id)
            .where(and_(
                Component.category == "case",
                Component.is_active == True,
            ))
            .order_by(min_price_sq.c.min_price.desc())
            .limit(1)
        )

        if mb_form_factor:
            query = query.where(Case.supported_form_factors.contains([mb_form_factor]))
        if gpu_length_mm:
            query = query.where(Case.max_gpu_length_mm >= gpu_length_mm)

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            return await self._select_component_with_model("case", budget)

        return row[0], row[1]

    async def _select_cooler(self, budget: int, cpu_socket: str, cpu_tdp: int):
        min_price_sq = (
            select(Price.component_id, func.min(Price.price_krw).label("min_price"))
            .where(and_(Price.in_stock == True, Price.price_krw <= budget))
            .group_by(Price.component_id)
            .subquery()
        )

        query = (
            select(Component, Cooler, min_price_sq.c.min_price)
            .join(Cooler, Component.id == Cooler.id)
            .join(min_price_sq, Component.id == min_price_sq.c.component_id)
            .where(and_(
                Component.category == "cooler",
                Component.is_active == True,
                Cooler.tdp_rating_w >= cpu_tdp,
            ))
            .order_by(Cooler.tdp_rating_w.asc())
            .limit(1)
        )

        if cpu_socket:
            query = query.where(Cooler.supported_sockets.contains([cpu_socket]))

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            return await self._select_component_with_model("cooler", budget)

        return row[0], row[1]

    async def _get_price_info(self, component_id) -> Optional[dict]:
        result = await self.db.execute(
            select(Price).where(
                and_(Price.component_id == component_id, Price.in_stock == True)
            ).order_by(Price.price_krw.asc())
        )
        prices = result.scalars().all()
        if not prices:
            return None

        cheapest = prices[0]
        return {
            "price_krw": cheapest.price_krw,
            "sources": [
                {
                    "source": p.source,
                    "price_krw": p.price_krw,
                    "url": p.product_url,
                    "in_stock": p.in_stock,
                }
                for p in prices
            ],
        }

    def _extract_specs(self, category: str, comp: Component, model_obj) -> dict:
        if not model_obj:
            return {}
        specs = {}
        try:
            if category == "cpu":
                specs = {
                    "socket": model_obj.socket,
                    "cores": model_obj.cores,
                    "threads": model_obj.threads,
                    "base_clock_ghz": float(model_obj.base_clock_ghz),
                    "boost_clock_ghz": float(model_obj.boost_clock_ghz),
                    "tdp_w": model_obj.tdp_w,
                }
            elif category == "gpu":
                specs = {
                    "vram_size_gb": model_obj.vram_size_gb,
                    "vram_type": model_obj.vram_type,
                    "tdp_w": model_obj.tdp_w,
                    "length_mm": model_obj.length_mm,
                    "dlss_supported": model_obj.dlss_supported,
                    "ray_tracing_supported": model_obj.ray_tracing_supported,
                }
            elif category == "motherboard":
                specs = {
                    "socket": model_obj.socket,
                    "chipset": model_obj.chipset,
                    "form_factor": model_obj.form_factor,
                    "memory_type": model_obj.memory_type,
                    "memory_slots": model_obj.memory_slots,
                    "m2_slots": model_obj.m2_slots,
                }
            elif category == "ram":
                specs = {
                    "type": model_obj.type,
                    "speed_mhz": model_obj.speed_mhz,
                    "total_capacity_gb": model_obj.total_capacity_gb,
                    "cas_latency": model_obj.cas_latency,
                }
            elif category == "storage":
                specs = {
                    "type": model_obj.type,
                    "capacity_gb": model_obj.capacity_gb,
                    "interface": model_obj.interface,
                    "read_speed_mbs": model_obj.read_speed_mbs,
                }
            elif category == "psu":
                specs = {
                    "wattage": model_obj.wattage,
                    "efficiency_rating": model_obj.efficiency_rating,
                    "modular_type": model_obj.modular_type,
                }
            elif category == "case":
                specs = {
                    "form_factor_case": model_obj.form_factor_case,
                    "max_gpu_length_mm": model_obj.max_gpu_length_mm,
                    "max_cpu_cooler_height_mm": model_obj.max_cpu_cooler_height_mm,
                }
            elif category == "cooler":
                specs = {
                    "type": model_obj.type,
                    "tdp_rating_w": model_obj.tdp_rating_w,
                    "height_mm": model_obj.height_mm,
                }
        except Exception as e:
            logger.debug(f"Error extracting specs for {category}: {e}")
        return specs

    async def _check_compatibility(self, selected: dict) -> dict:
        try:
            is_compat, issues = await self.compat_checker.check_build_compatibility(
                cpu_id=str(selected["cpu"].id) if "cpu" in selected else None,
                motherboard_id=str(selected["motherboard"].id) if "motherboard" in selected else None,
                ram_id=str(selected["ram"].id) if "ram" in selected else None,
                gpu_id=str(selected["gpu"].id) if "gpu" in selected else None,
                psu_id=str(selected["psu"].id) if "psu" in selected else None,
                case_id=str(selected["case"].id) if "case" in selected else None,
                cooler_id=str(selected["cooler"].id) if "cooler" in selected else None,
                storages=[str(selected["storage"].id)] if "storage" in selected else [],
            )
            return {
                "is_compatible": is_compat,
                "issues": [i.model_dump() for i in issues],
            }
        except Exception as e:
            logger.warning(f"Compatibility check failed: {e}")
            return {"is_compatible": True, "issues": []}

    async def customize(self, quote_id: uuid.UUID, request):
        return {"message": "Customize endpoint - implementation pending"}
