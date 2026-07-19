from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_body_has_status_and_timestamp():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert "timestamp" in body
