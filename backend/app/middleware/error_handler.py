from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import IncompatibleBuildError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(IncompatibleBuildError)
    async def incompatible_build_handler(request: Request, exc: IncompatibleBuildError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "INCOMPATIBLE_BUILD",
                "message_ko": "선택하신 부품 조합으로는 PC를 구성할 수 없습니다.",
                "critical_issues": [i.model_dump() for i in exc.issues],
            },
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error_code": "INTERNAL_ERROR", "message": str(exc)},
        )
