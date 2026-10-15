"""The demo site: three placeholder pages, standing in for the host application."""

import ast
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DEMO_SITE = Path(__file__).parent.parent / "demo" / "site" / "app.py"


def _load_demo_site() -> TestClient:
    """Load ``demo/site/app.py`` as the container runs it, by path: it is not an installed
    package."""
    spec = importlib.util.spec_from_file_location("demo_site_app", DEMO_SITE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return TestClient(module.app)


@pytest.mark.parametrize(
    ("path", "title"),
    [
        ("/", "Demo shop"),
        ("/intranet/hr", "Intranet - HR user"),
        ("/intranet/engineering", "Intranet - engineering user"),
    ],
)
def test_each_page_answers_with_its_own_title(path: str, title: str) -> None:
    response = _load_demo_site().get(path)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert f"<title>{title}</title>" in response.text
    assert f"<h1>{title}</h1>" in response.text


def test_every_page_links_to_the_others() -> None:
    client = _load_demo_site()

    for path in ("/", "/intranet/hr", "/intranet/engineering"):
        page = client.get(path).text
        assert 'href="/"' in page
        assert 'href="/intranet/hr"' in page
        assert 'href="/intranet/engineering"' in page


def test_an_unknown_page_is_a_404() -> None:
    assert _load_demo_site().get("/intranet/finance").status_code == 404


def test_the_demo_site_imports_nothing_from_the_gateway() -> None:
    """The host application and the gateway only ever talk over HTTP."""
    imported: set[str] = set()
    for node in ast.walk(ast.parse(DEMO_SITE.read_text())):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])

    assert imported
    assert not imported & {"ragbridge_chat", "ragbridge"}
