import logging
import re
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class RFC7807Error(Exception):
    def __init__(
        self,
        status: int,
        title: str,
        detail: str,
        type_: str = "about:blank",
        instance: str | None = None,
    ):
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type_
        self.instance = instance


def sanitize_error_detail(detail: str) -> str:
    """Удаляем чувствительные данные из ошибок"""
    if not isinstance(detail, str):
        return str(detail)

    sensitive_patterns = [
        (r"password[^=]*=[^,]*", "password=***"),
        (r'("password"\s*:\s*)"[^"]*"', r'\1"***"'),
        (r"(?i)token[^=]*=[^,]*", "token=***"),
        (r"(?i)secret[^=]*=[^,]*", "secret=***"),
        (r"(?i)key[^=]*=[^,]*", "key=***"),
    ]

    sanitized_detail = detail
    for pattern, replacement in sensitive_patterns:
        sanitized_detail = re.sub(pattern, replacement, sanitized_detail)

    return sanitized_detail


async def rfc7807_exception_handler(request: Request, exc: RFC7807Error):
    correlation_id = str(uuid.uuid4())

    safe_detail = sanitize_error_detail(exc.detail)

    logger.error(
        f"Error {exc.status}: {exc.title}",
        extra={
            "correlation_id": correlation_id,
            "status": exc.status,
            "type": exc.type,
            "instance": exc.instance,
            "path": request.url.path,
            "method": request.method,
        },
    )

    if not request.app.debug:
        detail = "An error occurred"
    else:
        detail = safe_detail

    return JSONResponse(
        status_code=exc.status,
        content={
            "type": exc.type,
            "title": exc.title,
            "status": exc.status,
            "detail": detail,
            "instance": exc.instance or str(request.url),
            "correlation_id": correlation_id,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return await rfc7807_exception_handler(
        request,
        RFC7807Error(
            status=exc.status_code,
            title="HTTP Error",
            detail=exc.detail,
            instance=str(request.url),
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return await rfc7807_exception_handler(
        request,
        RFC7807Error(
            status=422,
            title="Validation Error",
            detail="Invalid request parameters",
            type_="https://example.com/errors/validation",
            instance=str(request.url),
        ),
    )


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(RFC7807Error, rfc7807_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
