from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": "securepassword123",
        },
    )
    response = client.post(
        "/auth/login",
        data={"username": email, "password": "securepassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_task(client: TestClient, headers: dict[str, str]) -> dict:
    project = client.post(
        "/projects",
        json={"name": "Activity Project"},
        headers=headers,
    ).json()

    return client.post(
        f"/projects/{project['id']}/tasks",
        json={"title": "Implement comments"},
        headers=headers,
    ).json()


def test_add_and_list_comments(client: TestClient):
    headers = register_and_login(client, "comment-user@example.com")
    task = create_task(client, headers)

    created = client.post(
        f"/tasks/{task['id']}/comments",
        json={"body": "This needs API tests."},
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["body"] == "This needs API tests."

    comments = client.get(
        f"/tasks/{task['id']}/comments",
        headers=headers,
    )
    assert comments.status_code == 200
    assert len(comments.json()) == 1


def test_activity_records_task_creation_and_comment(client: TestClient):
    headers = register_and_login(client, "activity-user@example.com")
    task = create_task(client, headers)

    client.post(
        f"/tasks/{task['id']}/comments",
        json={"body": "First comment"},
        headers=headers,
    )

    activity = client.get(
        f"/tasks/{task['id']}/activity",
        headers=headers,
    )
    assert activity.status_code == 200

    event_types = [event["event_type"] for event in activity.json()]
    assert "task_created" in event_types
    assert "comment_added" in event_types


def test_activity_records_status_change(client: TestClient):
    headers = register_and_login(client, "status-user@example.com")
    task = create_task(client, headers)

    updated = client.patch(
        f"/tasks/{task['id']}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert updated.status_code == 200

    activity = client.get(
        f"/tasks/{task['id']}/activity",
        headers=headers,
    )
    event_types = [event["event_type"] for event in activity.json()]
    assert "task_status_changed" in event_types


def test_cannot_comment_on_another_users_task(client: TestClient):
    owner_headers = register_and_login(client, "comment-owner@example.com")
    other_headers = register_and_login(client, "comment-other@example.com")

    task = create_task(client, owner_headers)

    response = client.post(
        f"/tasks/{task['id']}/comments",
        json={"body": "Unauthorized comment"},
        headers=other_headers,
    )
    assert response.status_code == 404
