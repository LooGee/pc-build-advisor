from fastapi import APIRouter
from app.tasks.requirement_analyzer import analyze_requirements
from app.schemas.analysis import AnalyzeRequest, AnalyzedRequirements

router = APIRouter()


@router.post("/analyze", response_model=AnalyzedRequirements)
async def analyze(request: AnalyzeRequest):
    return await analyze_requirements(request.user_input, request.provider)


@router.get("/health")
async def health():
    return {"status": "ok"}
