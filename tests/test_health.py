"""Tests for the liveness endpoint."""

from fastapi.testclient import TestClient

from ragbridge_chat.main import create_app


def test_health_reports_ok() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_app_builds_a_new_app_each_time() -> None:
    assert create_app() is not create_app()
