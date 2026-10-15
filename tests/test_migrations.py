"""Alembic runs against an empty database."""

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy import text
from sqlalchemy.engine import make_url

from ragbridge_chat.config import Settings
from tests.database import derive_test_database_url, safe_database_name

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def scratch_database_url() -> Iterator[str]:
    """An empty, throwaway database, so migrations can be run on a database nothing else uses.

    Its name ends in ``_test``, like the suite's own database, and it is dropped afterwards.
    """
    url = derive_test_database_url(Settings().database_url)
    scratch = make_url(url).set(database=f"{make_url(url).database}_migration")
    admin = create_sync_engine(scratch.set(database="postgres"), isolation_level="AUTOCOMMIT")
    name = safe_database_name(scratch.render_as_string(hide_password=False))
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    yield scratch.render_as_string(hide_password=False)
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
    admin.dispose()


def test_alembic_upgrades_an_empty_database_to_head(scratch_database_url: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=PROJECT_ROOT,
        env={**os.environ, "DATABASE_URL": scratch_database_url},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
