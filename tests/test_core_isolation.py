"""The gateway reaches the core over HTTP only, and never imports its code.

That is what lets the two be deployed and released separately (decision 15,
docs/plans/chat-roadmap.md in the core repository). The core's package is named
``ragbridge``; this one is ``ragbridge_chat``, so the check is on the first part
of each imported module's dotted name, not on a prefix of the text.
"""

import ast
from pathlib import Path

SOURCE = Path(__file__).parent.parent / "src"
CORE_PACKAGE = "ragbridge"


def _imported_top_level_names(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_no_module_imports_the_core() -> None:
    modules = sorted(SOURCE.rglob("*.py"))
    assert modules  # the scan must have found the gateway's own code

    offenders = [
        str(path.relative_to(SOURCE))
        for path in modules
        if CORE_PACKAGE in _imported_top_level_names(path)
    ]

    assert offenders == []
