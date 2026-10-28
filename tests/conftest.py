from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def clean_database() -> Generator[None, None, None]:
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
        )

    yield


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
