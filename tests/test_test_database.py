"""The guards that keep the suite away from a development database."""

import pytest

from tests.database import (
    assert_is_test_database,
    derive_test_database_url,
    safe_database_name,
)

URL = "postgresql+psycopg://user:secret@localhost:5433/ragbridge_chat"


def test_the_test_database_is_the_same_server_with_a_suffix() -> None:
    assert derive_test_database_url(URL) == URL + "_test"


def test_a_name_that_already_has_the_suffix_is_left_alone() -> None:
    assert derive_test_database_url(URL + "_test") == URL + "_test"


def test_a_database_without_the_suffix_is_refused() -> None:
    with pytest.raises(RuntimeError, match="_test"):
        assert_is_test_database(URL)

    assert_is_test_database(URL + "_test")


def test_an_unexpected_database_name_is_refused() -> None:
    with pytest.raises(RuntimeError):
        safe_database_name("postgresql+psycopg://u:p@localhost/bad-name;drop")
