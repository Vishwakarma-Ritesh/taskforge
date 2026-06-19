from datetime import UTC, datetime

from fastapi.testclient import TestClient

from apps.backend.src import database
from apps.backend.src.main import app


def test_health_endpoint_returns_alive() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"
    assert response.json()["service"] == "backend"


def test_ready_endpoint_returns_ready_when_database_is_reachable(monkeypatch) -> None:
    monkeypatch.setattr(database, "database_ready", lambda: True)
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_tasks_endpoint_returns_tasks(monkeypatch) -> None:
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    monkeypatch.setattr(
        database,
        "list_tasks",
        lambda: [
            {
                "id": 1,
                "title": "ship-demo",
                "description": "test task",
                "processed": False,
                "created_at": created_at,
                "processed_at": None,
            }
        ],
    )
    client = TestClient(app)

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "ship-demo"


def test_items_endpoint_aliases_tasks(monkeypatch) -> None:
    created_at = datetime(2026, 1, 1, tzinfo=UTC)
    monkeypatch.setattr(
        database,
        "list_tasks",
        lambda: [
            {
                "id": 2,
                "title": "item-alias",
                "description": "test alias",
                "processed": False,
                "created_at": created_at,
                "processed_at": None,
            }
        ],
    )
    client = TestClient(app)

    response = client.get("/items")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "item-alias"
