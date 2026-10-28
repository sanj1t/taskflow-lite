from fastapi.testclient import TestClient


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "TaskFlow Lite API is running"}


def test_liveness(client: TestClient):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
