from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


class CompatibilityIssue(BaseModel):
    issue_id: str
    severity: IssueSeverity
    category_a: str
    category_b: str
    component_a_name: str
    component_b_name: str
    title_ko: str
    message_ko: str
    solution_ko: Optional[str] = None
    alternative_components: List[dict] = []
    icon: str = "🔴"


class CompatibilityResult(BaseModel):
    is_compatible: bool
    issues: List[CompatibilityIssue] = []
    warnings_count: int = 0
    errors_count: int = 0


class CompatibilityCheckRequest(BaseModel):
    component_ids: dict  # {cpu, gpu, motherboard, ram, psu, case, cooler, storages:[]}
