from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    items: List[T]


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
