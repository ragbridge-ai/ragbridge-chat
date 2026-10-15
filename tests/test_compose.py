"""What the demo stack's compose file must keep promising."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

COMPOSE = Path(__file__).parent.parent / "docker-compose.yml"


def _services() -> dict[str, dict[str, Any]]:
    services: dict[str, dict[str, Any]] = yaml.safe_load(COMPOSE.read_text())["services"]
    return services


def test_the_stack_has_the_planned_services() -> None:
    assert set(_services()) == {
        "core-postgres",
        "core-redis",
        "core",
        "gateway-postgres",
        "gateway",
        "demo-site",
    }


def test_no_database_or_cache_is_published_to_the_host() -> None:
    """So the demo can run next to the core's own stack, and nothing is exposed that need
    not be."""
    services = _services()

    for name in ("core-postgres", "core-redis", "gateway-postgres"):
        assert "ports" not in services[name], name


def test_the_core_is_built_from_a_release_tag_unless_overridden() -> None:
    context = _services()["core"]["build"]["context"]

    assert context.startswith("https://github.com/ragbridge-ai/ragbridge.git#")
    assert context.endswith("${CORE_REF:-v1.4.0}")


def test_the_gateway_and_the_demo_site_use_one_image() -> None:
    services = _services()

    assert services["demo-site"]["image"] == services["gateway"]["image"]
    assert "build" not in services["demo-site"]
    assert services["demo-site"]["pull_policy"] == "never"


def test_the_gateway_waits_for_its_own_database_not_the_cores() -> None:
    depends_on = _services()["gateway"]["depends_on"]

    assert set(depends_on) == {"gateway-postgres"}
    assert depends_on["gateway-postgres"]["condition"] == "service_healthy"
