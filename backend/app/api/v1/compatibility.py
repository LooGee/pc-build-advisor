from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.compatibility import CompatibilityCheckRequest, CompatibilityResult
from app.services.compatibility.checker import CompatibilityChecker

router = APIRouter()


@router.post("/check", response_model=CompatibilityResult)
async def check_compatibility(
    request: CompatibilityCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    checker = CompatibilityChecker(db)
    ids = request.component_ids
    is_compat, issues = await checker.check_build_compatibility(
        cpu_id=ids.get("cpu"),
        motherboard_id=ids.get("motherboard"),
        ram_id=ids.get("ram"),
        gpu_id=ids.get("gpu"),
        psu_id=ids.get("psu"),
        case_id=ids.get("case"),
        cooler_id=ids.get("cooler"),
        storages=ids.get("storages", []),
    )
    return CompatibilityResult(
        is_compatible=is_compat,
        issues=issues,
        warnings_count=sum(1 for i in issues if i.severity == "warning"),
        errors_count=sum(1 for i in issues if i.severity == "error"),
    )
