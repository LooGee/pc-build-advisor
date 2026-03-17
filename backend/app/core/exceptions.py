from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class IncompatibleBuildError(Exception):
    """호환되지 않는 PC 빌드 구성"""
    def __init__(self, issues: list):
        self.issues = issues
        super().__init__("Incompatible build configuration")


class LLMServiceError(Exception):
    """LLM 서비스 오류"""
    pass


class CrawlerError(Exception):
    """크롤러 오류"""
    pass
