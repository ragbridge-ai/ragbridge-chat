"""Keep the test suite away from the development database.

The suite creates and migrates a separate ``<name>_test`` database on the same server, and
the code that would empty tables refuses to touch any other. The same rule as the core's,
for the same reason: running ``pytest`` must never delete a developer's data.
"""

from sqlalchemy.engine import make_url

from ragbridge_chat.config import Settings

TEST_SUFFIX = "_test"


def derive_test_database_url(url: str) -> str:
    """The URL of the test database that goes with ``url``.

    Same server, user and password; the database name gains a ``_test`` suffix, unless it
    already has one.
    """
    parsed = make_url(url)
    name = parsed.database or ""
    if not name.endswith(TEST_SUFFIX):
        parsed = parsed.set(database=name + TEST_SUFFIX)
    return parsed.render_as_string(hide_password=False)


def assert_is_test_database(url: str) -> None:
    """Raise unless ``url`` names a test database."""
    name = make_url(url).database or ""
    if not name.endswith(TEST_SUFFIX):
        raise RuntimeError(
            f"Refusing to use database {name!r}: the test suite only runs against a "
            f"database whose name ends in {TEST_SUFFIX!r}."
        )


def safe_database_name(url: str) -> str:
    """The database name in ``url``, checked to be safe to put in ``CREATE DATABASE``."""
    name = make_url(url).database or ""
    if not name.replace("_", "").isalnum():
        raise RuntimeError(f"Unexpected characters in database name {name!r}.")
    return name


def point_environment_at_test_database() -> None:
    """Make ``DATABASE_URL`` the test database, for this process and its children.

    Must run before anything calls ``get_settings()``, which is cached.
    ``tests/__init__.py`` calls it, and Python imports a package before the modules inside
    it. ``.env`` is a developer's own setup, so it is switched off for the rest of the
    process once the one value the suite needs from it, the database URL, has been read.
    """
    import os

    os.environ["DATABASE_URL"] = derive_test_database_url(Settings().database_url)
    Settings.model_config["env_file"] = None
