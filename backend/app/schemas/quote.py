from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class BudgetSchema(BaseModel):
    min: Optional[int] = None
    max: int
    currency: str = "KRW"


class PreferencesSchema(BaseModel):
    color: Optional[str] = None
    size: Optional[str] = None
    brands: List[str] = []
    features: List[str] = []
    monitor_resolution: Optional[str] = None
    target_fps: Optional[int] = None


class AnalyzedRequirements(BaseModel):
    primary_use: str
    specific_software_games: List[str] = []
    performance_tier: str  # min | mid | max
    budget: BudgetSchema
    preferences: PreferencesSchema
    priority: str = "balanced"
    additional_notes: Optional[str] = None


class PriceSourceInfo(BaseModel):
    source: str
    price_krw: int
    url: Optional[str] = None
    in_stock: bool = True
    shipping: Optional[str] = None


class ComponentPriceInfo(BaseModel):
    price_krw: int
    sources: List[PriceSourceInfo] = []


class QuoteComponentDetail(BaseModel):
    category: str
    id: str
    brand: str
    model: str
    image_url: Optional[str] = None
    specifications: Dict[str, Any] = {}
    price_info: ComponentPriceInfo
    compatibility_status: str = "ok"
    compatibility_notes: str = ""


class EstimatedPerformance(BaseModel):
    cpu_benchmark_score: Optional[int] = None
    gpu_benchmark_score: Optional[int] = None
    estimated_gaming_fps_1080p: Optional[int] = None
    estimated_gaming_fps_1440p: Optional[int] = None
    estimated_power_consumption_w: Optional[int] = None


class QuoteTierResult(BaseModel):
    tier: str
    tier_name: str
    tier_description: str
    total_price_krw: int
    components_price_krw: int
    shipping_cost_krw: int = 0
    components: List[QuoteComponentDetail] = []
    compatibility: Dict[str, Any] = {}
    estimated_performance: Optional[EstimatedPerformance] = None


class QuoteGenerateRequest(BaseModel):
    user_input: str
    user_session_id: Optional[str] = None
    llm_provider: Optional[str] = "claude"


class QuoteGenerateResponse(BaseModel):
    id: str
    user_input: str
    analyzed_requirements: AnalyzedRequirements
    quotes: List[QuoteTierResult]
    created_at: datetime
    expires_at: Optional[datetime] = None


class QuoteCustomizeRequest(BaseModel):
    tier: str
    component_changes: List[Dict[str, str]]
