from fastapi.testclient import TestClient

from apps.worker.src import database
from apps.worker.src.main import app


def test_health_endpoint_returns_alive() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"
    assert response.json()["service"] == "worker"


def test_ready_endpoint_returns_ready_when_database_is_reachable(monkeypatch) -> None:
    monkeypatch.setattr(database, "database_ready", lambda: True)
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
