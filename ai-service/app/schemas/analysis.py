from pydantic import BaseModel
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    user_input: str
    provider: str = "claude"


class BudgetSchema(BaseModel):
    min: Optional[int] = None
    max: int = 1500000
    currency: str = "KRW"


class PreferencesSchema(BaseModel):
    color: Optional[str] = None
    size: Optional[str] = None
    brands: List[str] = []
    features: List[str] = []
    monitor_resolution: Optional[str] = None
    target_fps: Optional[int] = None


class AnalyzedRequirements(BaseModel):
    primary_use: str = "gaming"
    specific_software_games: List[str] = []
    performance_tier: str = "mid"
    budget: BudgetSchema = BudgetSchema(max=1500000)
    preferences: PreferencesSchema = PreferencesSchema()
    priority: str = "balanced"
    additional_notes: Optional[str] = None
