"""Founder 2026-09-30 (ARCHITECTURE.md headroom, A1 and A3): the code layout and the API routes are
generated from the code into docs/code-layout.md and docs/api-routes.md, as §4.2's declarations are
into docs/data-models.md. The pre-commit hook regenerates both; this checks each file equals a fresh
generation, and that ARCHITECTURE.md links them."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT / "tools" / "architecture"
sys.path.insert(0, str(TOOLS))

import generate_layout  # noqa: E402
import generate_routes  # noqa: E402


@pytest.mark.parametrize("gen", [generate_layout, generate_routes], ids=["code layout", "api routes"])
def test_the_generated_document_is_current(gen) -> None:
    doc = gen.DOC
    text = (PROJECT.parent / doc.doc_rel).read_text(encoding="utf-8")
    assert doc.span(text) is not None, f"{doc.doc_rel} has no generated block"
    assert doc.is_current(text, PROJECT), f"{doc.doc_rel} differs from a fresh generation — run {gen.__name__}.py --write"


def test_architecture_links_both() -> None:
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "(docs/code-layout.md)" in arch and "(docs/api-routes.md)" in arch


def test_every_route_is_listed() -> None:
    body = generate_routes.generate(PROJECT)
    for path in ("/ask", "/upload", "/gate", "/gate/decision", "/cases", "/health"):
        assert f"| `{path}` |" in body, path
