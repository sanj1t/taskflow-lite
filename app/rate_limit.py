import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limit: int = 30,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = self.requests[client_ip]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.limit:
            return JSONResponse(
                status_code=429,
                headers={
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                },
                content={
                    "error": "rate_limit_exceeded",
                    "detail": "Too many requests. Try again later.",
                },
            )

        window.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(
            self.limit - len(self.requests[client_ip])
        )
        return response
