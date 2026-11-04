from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    status_code: int = 400

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BadRequestError(AppException):
    status_code = 400


class UnauthorizedError(AppException):
    status_code = 401


class ForbiddenError(AppException):
    status_code = 403


class NotFoundError(AppException):
    status_code = 404


class ConflictError(AppException):
    status_code = 409


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )