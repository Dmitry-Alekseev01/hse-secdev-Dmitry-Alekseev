import logging
import uuid
from typing import Optional

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
        instance: Optional[str] = None,
    ):
        self.status = status
        self.title = title
        self.detail = detail
        self.type = type_
        self.instance = instance


async def rfc7807_exception_handler(request: Request, exc: RFC7807Error):
    correlation_id = str(uuid.uuid4())

    # Логируем с correlation_id для трассировки
    logger.error(
        f"Error {exc.status}: {exc.title}",
        extra={
            "correlation_id": correlation_id,
            "status": exc.status,
            "type": exc.type,
            "instance": exc.instance,
        },
    )

    # В продакшене маскируем детали
    if not request.app.debug:
        detail = "An error occurred"
    else:
        detail = exc.detail

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
