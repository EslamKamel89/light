from typing import Any, cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict[str, Any]


class APIException(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_type: str = "api_error",
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.error_type = error_type


async def api_exception_handler(request: Request, exc: Exception):
    exc = cast(APIException, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {"type": exc.error_type, "message": exc.message},
        },
    )


async def validation_exception_handler(request: Request, exc: Exception):
    exc = cast(RequestValidationError, exc)
    errors = []
    for error in exc.errors():
        field = ".".join(str(item) for item in error["loc"])
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "type": "validation_error",
                "message": "Validation failed",
                "details": errors,
            },
        },
    )
