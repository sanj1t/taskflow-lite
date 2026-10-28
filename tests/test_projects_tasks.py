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


def test_create_and_list_projects(client: TestClient):
    headers = register_and_login(client, "project-user@example.com")

    created = client.post(
        "/projects",
        json={"name": "Backend Migration", "description": "Migrate services"},
        headers=headers,
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    listed = client.get("/projects", headers=headers)
    assert listed.status_code == 200
    assert any(project["id"] == project_id for project in listed.json())


def test_create_task_and_filter_by_status(client: TestClient):
    headers = register_and_login(client, "task-user@example.com")

    project = client.post(
        "/projects",
        json={"name": "Task Project"},
        headers=headers,
    ).json()

    task_response = client.post(
        f"/projects/{project['id']}/tasks",
        json={"title": "Implement auth", "priority": "high"},
        headers=headers,
    )
    assert task_response.status_code == 201

    todo_tasks = client.get(
        f"/projects/{project['id']}/tasks?status=todo",
        headers=headers,
    )
    assert todo_tasks.status_code == 200
    assert len(todo_tasks.json()) == 1

    done_tasks = client.get(
        f"/projects/{project['id']}/tasks?status=done",
        headers=headers,
    )
    assert done_tasks.status_code == 200
    assert len(done_tasks.json()) == 0


def test_update_task_status(client: TestClient):
    headers = register_and_login(client, "update-user@example.com")

    project = client.post(
        "/projects",
        json={"name": "Update Project"},
        headers=headers,
    ).json()

    task = client.post(
        f"/projects/{project['id']}/tasks",
        json={"title": "Write tests"},
        headers=headers,
    ).json()

    updated = client.patch(
        f"/tasks/{task['id']}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_progress"


def test_cannot_access_another_users_project(client: TestClient):
    owner_headers = register_and_login(client, "owner-user@example.com")
    other_headers = register_and_login(client, "other-user@example.com")

    project = client.post(
        "/projects",
        json={"name": "Private Project"},
        headers=owner_headers,
    ).json()

    response = client.get(
        f"/projects/{project['id']}",
        headers=other_headers,
    )
    assert response.status_code == 404
