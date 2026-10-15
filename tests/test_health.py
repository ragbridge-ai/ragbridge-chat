"""Tests for the liveness endpoint."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ragbridge_chat.main import create_app


def test_health_reports_ok() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_app_builds_a_new_app_each_time() -> None:
    assert create_app() is not create_app()


def test_health_ready_returns_ok_when_database_is_reachable(
    app_with_database: FastAPI,
) -> None:
    response = TestClient(app_with_database).get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready_returns_503_when_database_is_unreachable(
    app_with_unreachable_database: FastAPI,
) -> None:
    response = TestClient(app_with_unreachable_database).get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}


def test_health_stays_ok_when_database_is_unreachable(
    app_with_unreachable_database: FastAPI,
) -> None:
    """Liveness must not depend on the database, or an orchestrator restarts a healthy
    process because its database is down."""
    response = TestClient(app_with_unreachable_database).get("/health")

    assert response.status_code == 200
