import logging

from fastapi import FastAPI

from app.config import settings
from app.errors import register_error_handlers
from app.middleware import RequestContextMiddleware
from app.rate_limit import RateLimitMiddleware
from app.routers import auth, comments, health, projects, tasks, users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    description="A lightweight team task-management REST API.",
    version="0.1.0",
)

app.add_middleware(RateLimitMiddleware, limit=60, window_seconds=60)
app.add_middleware(RequestContextMiddleware)

register_error_handlers(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "TaskFlow Lite API is running"}
