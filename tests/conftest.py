"""Shared fixtures for tests that need a database-backed app."""

import asyncio
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from ragbridge_chat.config import Settings
from ragbridge_chat.db.session import create_engine, create_session_factory
from ragbridge_chat.main import create_app
from tests.database import assert_is_test_database, safe_database_name

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def _test_database() -> None:
    """Create the test database if it is missing, and migrate it to head.

    ``tests/__init__.py`` has already pointed ``DATABASE_URL`` at ``<name>_test``.
    Migrations run in a subprocess, as they do in CI and in Docker: Alembic's ``env.py``
    reconfigures logging, which would disable this process's loggers.
    """
    url = Settings().database_url
    assert_is_test_database(url)
    name = safe_database_name(url)

    async def create_if_missing() -> None:
        # CREATE DATABASE cannot run inside a transaction, hence AUTOCOMMIT, and it is run
        # from the server's maintenance database.
        admin_url = make_url(url).set(database="postgres")
        engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
        async with engine.connect() as connection:
            exists = await connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": name}
            )
            if not exists:
                await connection.execute(text(f'CREATE DATABASE "{name}"'))
        await engine.dispose()

    asyncio.run(create_if_missing())
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env=os.environ,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def app_with_database() -> Iterator[FastAPI]:
    """A FastAPI app wired to the real test database.

    Its engine is disposed after the test, so a test run does not leave pooled connections
    open until garbage collection.
    """
    app = create_app()
    engine = create_engine(Settings())
    app.state.session_factory = create_session_factory(engine)
    yield app
    asyncio.run(engine.dispose())


@pytest.fixture
def app_with_unreachable_database() -> Iterator[FastAPI]:
    """A FastAPI app wired to a database that refuses connections.

    Points at a closed local port: connecting to a port nothing listens on fails at once
    with "connection refused", so there is no network timeout to wait out.
    """
    app = create_app()
    unreachable = Settings(
        database_url="postgresql+psycopg://ragbridge_chat:ragbridge_chat@localhost:1/ragbridge_chat"
    )
    engine = create_engine(unreachable)
    app.state.session_factory = create_session_factory(engine)
    yield app
    asyncio.run(engine.dispose())
