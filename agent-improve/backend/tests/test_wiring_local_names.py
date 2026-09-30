"""Controls review, item 5 (founder, 2026-09-30): a shared test helper must not count as a direct
node call — a name the test binds itself is a local, not the node of that name."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]


def test_item_5_a_local_named_like_a_node_is_not_a_direct_node_call(tmp_path) -> None:
    """The e2e tests keep the real factory as `planner = nodes_common.get_llm` and call it in a stub;
    the wiring check counted that as calling the planner node directly (seven findings)."""
    sys.path.insert(0, str(_REPO / "agent-improve" / "tools" / "architecture"))
    import wiring
    t = tmp_path / "test_x.py"
    t.write_text(
        "from backend.phases.nodes_common import planner\n"
        "def test_local(monkeypatch):\n"
        "    planner = object\n"
        "    stub = lambda role: planner(role)\n"
        "    return stub\n"
        "def test_imported():\n"
        "    planner({})\n", encoding="utf-8")
    got_local = wiring._test_calls(t, "test_local")
    got_imported = wiring._test_calls(t, "test_imported")
    assert got_local is not None and got_imported is not None
    assert "planner" not in got_local[0] and "planner" in got_imported[0]
