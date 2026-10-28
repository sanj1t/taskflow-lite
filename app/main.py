from fastapi import FastAPI

from app.config import settings
from app.routers import auth, health, users, projects, tasks, comments

app = FastAPI(
    title=settings.app_name,
    description="A lightweight team task-management REST API.",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "TaskFlow Lite API is running"}
