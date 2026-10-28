import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("taskflow")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            process_time = time.perf_counter() - started_at
            logger.exception(
                "Unhandled error request_id=%s method=%s path=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                process_time * 1000,
            )
            return JSONResponse(
                status_code=500,
                headers={"X-Request-ID": request_id},
                content={
                    "error": "internal_server_error",
                    "detail": "An unexpected error occurred.",
                    "request_id": request_id,
                },
            )

        process_time = time.perf_counter() - started_at
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time * 1000:.2f}"

        if not request.url.path.startswith("/health"):
            logger.info(
                "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                process_time * 1000,
            )

        return response
