.PHONY: install test run db-up db-down migrate revision lint

install:
	./.venv/bin/python -m pip install --upgrade pip
	./.venv/bin/python -m pip install -r requirements.txt

test:
	./.venv/bin/python -m pytest -v

run:
	./.venv/bin/uvicorn app.main:app --reload

db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	./.venv/bin/alembic upgrade head

revision:
	./.venv/bin/alembic revision --autogenerate -m "$(m)"

lint:
	./.venv/bin/python -m ruff check .
