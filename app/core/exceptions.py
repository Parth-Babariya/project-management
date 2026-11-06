import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

logger = logging.getLogger("app")


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


class PayloadTooLargeError(AppException):
    status_code = 413


class UnsupportedMediaTypeError(AppException):
    status_code = 415

