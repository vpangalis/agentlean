"""Define's feature list — step 6.66 (founder ruling 2026-09-25).

The list (`docs/define_features.json`) is the plan; its status comes ONLY from
test results. Pinned here:
  - the shape: the founder's fields, NO status field, lanes, ids, dependencies;
  - COVERAGE: every Define step (open or not, so the test never depends on a
    run), every capability row and every open Define gap maps to a feature —
    with a mutation proof that dropping one mapping turns the test red;
  - STATUS: derived from test-results.json and nothing else, both ways.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2] / "tools" / "control_board"
sys.path.insert(0, str(_TOOLS))

import features as F  # noqa: E402
import progress as P  # noqa: E402

FIELDS = {"id", "description", "clause", "depends_on", "test", "sources", "lane", "covers"}
SOURCES = {"architecture", "procedure", "code", "guidance"}


@pytest.fixture(scope="module")
def feats() -> list[dict]:
    return F.load()


@pytest.fixture(scope="module")
def text() -> str:
    return P._read(P.PROCEDURE)


def _covered(feats: list[dict], kind: str) -> set[str]:
    return {x for f in feats for x in f["covers"][kind]}


def _uncovered(feats: list[dict], text: str) -> dict[str, list[str]]:
    return {
        "steps": sorted(F.define_steps(text) - _covered(feats, "steps")),
        "capability_rows": sorted(F.capability_rows(text) - _covered(feats, "capability_rows")),
        "gaps": sorted(F.define_gaps(text) - _covered(feats, "gaps")),
    }


def test_every_feature_has_the_founders_fields_and_no_status(feats) -> None:
    for f in feats:
        assert set(f) == FIELDS, (f["id"], set(f) ^ FIELDS)
        assert "status" not in f and "passes" not in f
        assert set(f["sources"]) == SOURCES, f["id"]
        assert f["lane"] in F.LANES, f["id"]
        assert f["test"].startswith("backend/tests/test_") and "::test_" in f["test"], f["id"]


def test_ids_are_unique_and_every_dependency_resolves(feats) -> None:
    ids = [f["id"] for f in feats]
    assert len(ids) == len(set(ids))
    for f in feats:
        assert set(f["depends_on"]) <= set(ids), (f["id"], set(f["depends_on"]) - set(ids))
        assert f["id"] not in f["depends_on"]


def test_every_define_step_row_and_open_gap_maps_to_a_feature(feats, text) -> None:
    """Founder ruling 2026-09-25, Part 5c."""
    assert F.define_steps(text) and F.capability_rows(text), "the readers found nothing — a heading moved"
    assert _uncovered(feats, text) == {"steps": [], "capability_rows": [], "gaps": []}


def test_dropping_one_mapping_turns_the_coverage_red(feats, text) -> None:
    """The mutation proof: a coverage test that cannot fail proves nothing."""
    step = sorted(F.define_steps(text))[0]
    mutant = copy.deepcopy(feats)
    for f in mutant:
        f["covers"]["steps"] = [s for s in f["covers"]["steps"] if s != step]
    assert _uncovered(mutant, text)["steps"] == [step]


def test_status_is_derived_from_the_recorded_outcome_only() -> None:
    feats = [{"id": "X-1", "test": "backend/tests/test_a.py::test_ok", "depends_on": [], "lane": "A"},
             {"id": "X-2", "test": "backend/tests/test_a.py::test_bad", "depends_on": [], "lane": "A"},
             {"id": "X-3", "test": "backend/tests/test_a.py::test_unwritten", "depends_on": [], "lane": "A"}]
    res = {"outcomes": {"backend/tests/test_a.py::test_ok": "passed",
                        "backend/tests/test_a.py::test_bad": "failed"}}
    assert F.status(feats, res) == {"X-1": "passing", "X-2": "failing", "X-3": "failing"}


def test_the_next_feature_waits_for_its_dependencies() -> None:
    feats = [{"id": "X-1", "depends_on": [], "lane": "A"},
             {"id": "X-2", "depends_on": ["X-1"], "lane": "A"}]
    assert F._next(["X-1", "X-2"], feats, {"X-1": "failing", "X-2": "failing"}) == "X-1"
    assert F._next(["X-2"], feats, {"X-1": "passing", "X-2": "failing"}) == "X-2"
