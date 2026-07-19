"""API tests for the Task Tracker backend (Module 2, Part 2.4)."""


def move_to_status(client, task_id: int, *statuses: str) -> None:
    """Walk a task through a sequence of valid transitions."""
    for status in statuses:
        response = client.patch(f"/tasks/{task_id}", json={"status": status})
        assert response.status_code == 200


# --- Create ---------------------------------------------------------------


def test_create_task_returns_201_with_server_fields(client):
    response = client.post("/tasks", json={"title": "New task"})
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "New task"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["created_at"] and body["updated_at"]


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_extra_field_returns_422(client):
    response = client.post("/tasks", json={"title": "T", "owner": "someone"})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "T", "priority": "Urgent"})
    assert response.status_code == 422


def test_create_task_client_supplied_id_returns_422(client):
    response = client.post("/tasks", json={"title": "T", "id": 42})
    assert response.status_code == 422


# --- List and filter ------------------------------------------------------


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_contains_created_task(client, created_task):
    body = client.get("/tasks").json()
    assert [t["id"] for t in body] == [created_task["id"]]


def test_filter_by_status_returns_only_matches(client, created_task):
    move_to_status(client, created_task["id"], "InProgress")
    client.post("/tasks", json={"title": "Still todo"})
    body = client.get("/tasks", params={"status": "InProgress"}).json()
    assert len(body) == 1
    assert body[0]["id"] == created_task["id"]


def test_filter_by_priority_no_match_returns_200_empty_list(client, created_task):
    response = client.get("/tasks", params={"priority": "Low"})
    assert response.status_code == 200
    assert response.json() == []


def test_filter_with_invalid_status_value_returns_422(client):
    response = client.get("/tasks", params={"status": "Later"})
    assert response.status_code == 422


# --- Get by id ------------------------------------------------------------


def test_get_task_by_id_returns_200(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == created_task["title"]


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


# --- Patch ----------------------------------------------------------------


def test_patch_title_returns_200_and_updates_field(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": "Renamed"})
    assert response.status_code == 200
    assert response.json()["title"] == "Renamed"


def test_patch_missing_task_returns_404(client):
    response = client.patch("/tasks/999", json={"title": "Ghost"})
    assert response.status_code == 404


def test_patch_blank_title_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": "  "})
    assert response.status_code == 422


def test_patch_extra_field_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"created_at": "2026-01-01T00:00:00Z"})
    assert response.status_code == 422


# --- Status transitions ---------------------------------------------------


def test_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert response.status_code == 422


def test_transition_done_to_todo_returns_422(client, created_task):
    move_to_status(client, created_task["id"], "InProgress", "Done")
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_transition_done_to_inprogress_returns_200(client, created_task):
    move_to_status(client, created_task["id"], "InProgress", "Done")
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})
    assert response.status_code == 200


def test_transition_same_status_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_title_only_patch_skips_transition_validation(client, created_task):
    move_to_status(client, created_task["id"], "InProgress", "Done")
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": "Done but renamed"})
    assert response.status_code == 200


# --- PATCH edge cases (Module 3) -------------------------------------------


def test_patch_unsupported_status_value_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Archived"})
    assert response.status_code == 422


def test_patch_invalid_priority_value_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"priority": "Urgent"})
    assert response.status_code == 422


def test_patch_inprogress_back_to_todo_returns_422_with_message(client, created_task):
    move_to_status(client, created_task["id"], "InProgress")
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422
    assert "invalid status transition" in response.json()["detail"].lower()


def test_patch_null_title_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": None})
    assert response.status_code == 422


def test_patch_empty_body_returns_200_and_changes_nothing_but_updated_at(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == created_task["title"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["updated_at"] >= created_task["updated_at"]


# --- Delete ---------------------------------------------------------------


def test_delete_task_returns_204_with_empty_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_deleted_task_is_gone(client, created_task):
    assert client.delete(f"/tasks/{created_task['id']}").status_code == 204
    assert client.get(f"/tasks/{created_task['id']}").status_code == 404
    assert client.delete(f"/tasks/{created_task['id']}").status_code == 404
