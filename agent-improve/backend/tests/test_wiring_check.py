"""The wiring check, tools/architecture/wiring.py — brief Part F6 (founder, 2026-09-27).

It reads ARCHITECTURE.md §3's names, finds the production callers by `ast`, and flags a
feature test that calls a node or mapper directly. It warns; these tests pin that it sees.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT / "tools" / "architecture"))

import wiring  # noqa: E402


def test_it_reads_what_section_3_names() -> None:
    n = wiring.named()
    assert {"planner", "executor", "validation_stack", "gate_review", "gate_apply"} <= set(n["node"])
    assert "ContradictionDetectionMiddleware" in n["middleware"] and len(n["middleware"]) == 8
    assert "define_output_mapper" in n["mapper"] and "POST /gate/decision" in n["route"]


def test_it_finds_a_component_with_no_production_caller_and_passes_a_wired_one() -> None:
    """G-112, the case that motivated it: the output mappers had no production caller."""
    ix = wiring._Index()
    got = {f["name"] for f in wiring.check_callers(ix, {"node": ["planner"], "middleware": [],
                                                        "mapper": ["define_output_mapper"], "tool": [],
                                                        "route": ["POST /ask"]})}
    reach = ix.reach(wiring._roots(ix))
    wired = any(k in reach for k in ix.defs if k[1] == "define_output_mapper")
    assert ("define_output_mapper" in got) == (not wired)
    assert "planner" not in got and "POST /ask" not in got


def test_a_feature_test_calling_a_mapper_directly_is_seen(tmp_path) -> None:
    t = tmp_path / "test_x.py"
    t.write_text("def helper(s):\n    return define_input_mapper(s, None)\n\n"
                 "def test_direct():\n    helper(1)\n\n"
                 "def test_api(client):\n    client.post('/ask', json={})\n", encoding="utf-8")
    direct = wiring._test_calls(t, "test_direct")
    assert direct is not None and "define_input_mapper" in direct[0] and not direct[1]
    api = wiring._test_calls(t, "test_api")
    assert api is not None and api[0] & wiring.DRIVES
