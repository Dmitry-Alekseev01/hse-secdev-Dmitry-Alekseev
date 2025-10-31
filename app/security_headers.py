import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' "
            "'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' "
            "'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' "
            "data: https://fastapi.tiangolo.com; font-src 'self' https://cdn.jsdelivr.net;",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=()",
        }

        path = request.url.path
        if not path.startswith(("/docs", "/redoc", "/openapi.json")):
            for header, value in security_headers.items():
                response.headers[header] = value
        else:
            docs_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            }
            for header, value in docs_headers.items():
                response.headers[header] = value

        headers_to_remove = ["server", "x-powered-by"]
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]

        response.headers["X-Process-Time"] = str(process_time)

        return response
