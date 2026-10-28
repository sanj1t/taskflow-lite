# TaskFlow Lite

A lightweight team task-management REST API built with FastAPI, PostgreSQL,
SQLAlchemy 2, JWT authentication, Docker, Alembic, and Pytest.

## Features

- User registration and JWT authentication
- Protected current-user endpoint
- Project ownership and authorization
- Task CRUD with status and priority
- Task filtering and pagination
- Comments
- Activity events for task creation, updates, assignment, and comments
- Request IDs, structured logging, and consistent error responses
- Dockerized local development
- GitHub Actions CI with PostgreSQL
- OpenAPI documentation

## Tech stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- Pydantic v2
- JWT
- Docker Compose
- Pytest
- GitHub Actions

## API documentation

Local Swagger UI:

http://127.0.0.1:8000/docs

## Local setup

```bash
cp .env.example .env
docker compose up -d db
./.venv/bin/alembic upgrade head
./.venv/bin/uvicorn app.main:app --reload
```

## Run tests

```bash
./.venv/bin/python -m pytest -v
```

## Example flow

1. `POST /auth/register`
2. `POST /auth/login`
3. Create a project with `POST /projects`
4. Create a task with `POST /projects/{project_id}/tasks`
5. Update task status with `PATCH /tasks/{task_id}`
6. Add a comment with `POST /tasks/{task_id}/comments`
7. View the audit trail with `GET /tasks/{task_id}/activity`

## Architecture

```text
Client
  |
  v
FastAPI routers
  |
  v
Service/helper layer
  |
  v
SQLAlchemy repositories / ORM models
  |
  v
PostgreSQL
```

The service is intentionally a modular monolith. Routers, schemas, models, and helpers are separated so individual domains can be extracted into services later.

## Design decisions

- Used PostgreSQL for relational integrity, constraints, indexes, and scalable querying.
- Used JWT access tokens for stateless authentication.
- Used Alembic for versioned schema migrations.
- Used activity events to provide an audit trail without coupling event storage to task fields.
- Used request IDs to correlate logs and client-reported failures.
- Used an in-memory rate limiter for the single-process demo; a multi-worker deployment should use Redis.

## Future improvements

- Refresh-token rotation
- Redis-backed rate limiting
- Background notification worker
- OpenTelemetry tracing
- Load testing and query optimization
- Deployment to Render, Railway, or AWS
