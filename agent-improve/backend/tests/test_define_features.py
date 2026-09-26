"""Define's feature list — steps 6.66 and 6.67 (founder rulings 2026-09-25, 2026-09-26).

The list (`docs/define_features.json`) is what must be true; its status comes
ONLY from test results. Pinned here:
  - the shape: ids unique, depends_on resolve, every test exists, the five
    clauses, NO status field; code citations are path::symbol and resolve;
  - STATUS: derived from test-results.json and nothing else, both ways;
  - LANDING (the commit guard's rule 11): a commit naming DEF-xxx lands only
    when that feature's test and every depends_on feature's test pass — refused
    and allowed, through the guard itself;
  - THE RATCHET (rule 11b): a feature that has passed once must keep passing.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT = Path(__file__).resolve().parents[2]
_REPO = _PROJECT.parent
_TOOLS = _PROJECT / "tools" / "control_board"
sys.path.insert(0, str(_TOOLS))

import features as F  # noqa: E402

FIELDS = {"id", "description", "clause", "depends_on", "test", "sources", "lane", "provenance"}
CLAUSES = {"A Belt is coached through the twelve fields",
           "what they say is kept and every change is dated",
           "a complete case ASSEMBLES a gate document",
           "the Belt sees it, approves it",
           "the record is written once and correctly"}


@pytest.fixture(scope="module")
def feats() -> list[dict]:
    return F.load()


def test_every_feature_has_the_founders_fields_and_no_status(feats) -> None:
    for f in feats:
        assert set(f) == FIELDS, (f["id"], set(f) ^ FIELDS)
        assert f["lane"] in F.LANES, f["id"]
        assert f["test"].startswith("backend/tests/test_") and "::test_" in f["test"], f["id"]


def test_ids_are_unique_and_every_dependency_resolves(feats) -> None:
    ids = [f["id"] for f in feats]
    assert len(ids) == len(set(ids))
    for f in feats:
        assert set(f["depends_on"]) <= set(ids), (f["id"], set(f["depends_on"]) - set(ids))
        assert f["id"] not in f["depends_on"]


def test_the_clauses_are_the_five_of_define_complete(feats) -> None:
    assert {f["clause"] for f in feats} == CLAUSES


def test_every_features_test_exists(feats) -> None:
    """Part C: every named test node id exists (a stub that fails counts — it exists)."""
    import citations
    tracked = citations._tracked()
    bad = [(f["id"], f["test"]) for f in feats
           if citations.resolves("agent-improve/" + F.node_id(f["test"]), tracked)]
    assert not bad, bad


def test_every_code_citation_is_path_symbol_and_resolves_at_HEAD(feats) -> None:
    """Part C: no line numbers, no status words; every path and symbol exists."""
    import citations
    bad = [b for b in citations.check(feats) if not b[2].startswith("test ")]
    assert not bad, bad


# ── status ──────────────────────────────────────────────────────────────────

THREE = [{"id": "X-1", "test": "backend/tests/test_a.py::test_ok", "depends_on": [], "lane": "A"},
         {"id": "X-2", "test": "backend/tests/test_a.py::test_bad", "depends_on": ["X-1"], "lane": "A"},
         {"id": "X-3", "test": "backend/tests/test_a.py::test_unwritten", "depends_on": ["X-2"], "lane": "A"}]
RES = {"outcomes": {"backend/tests/test_a.py::test_ok": "passed",
                    "backend/tests/test_a.py::test_bad": "skipped"}}


def test_status_is_derived_from_the_recorded_outcome_only() -> None:
    assert F.status(THREE, RES) == {"X-1": "passing", "X-2": "failing", "X-3": "failing"}


def test_the_next_feature_waits_for_its_dependencies() -> None:
    feats = [{"id": "X-1", "depends_on": [], "lane": "A"}, {"id": "X-2", "depends_on": ["X-1"], "lane": "A"}]
    assert F._next(["X-1", "X-2"], feats, {"X-1": "failing", "X-2": "failing"}) == "X-1"
    assert F._next(["X-2"], feats, {"X-1": "passing", "X-2": "failing"}) == "X-2"


# ── landing and the ratchet, as functions ───────────────────────────────────


def test_dependency_blocking_is_strict_through_the_whole_chain() -> None:
    """Founder ruling 2026-09-26: a feature whose dependency passes but whose
    dependency's dependency fails is blocked — lane A fixes DEF-005 first."""
    st = {"X-1": "failing", "X-2": "passing", "X-3": "failing"}
    assert F.blockers("X-3", THREE, st) == ["X-1"]
    assert F._next(["X-1", "X-3"][::-1], THREE, st) == "X-1"
    ok = {"outcomes": {"backend/tests/test_a.py::test_bad": "passed",
                       "backend/tests/test_a.py::test_unwritten": "passed"}}
    assert any("depends on X-1" in w for w in F.landing_refusal("X-3", THREE, ok))


def test_the_core_is_a_second_number_that_leaves_out_the_quality_rows() -> None:
    """D2/D21, ruled 2026-09-26: all features is the headline; the five-clause
    core leaves out rows 22 and 26-32 — row 24 has an owner and counts."""
    def feat(fid, rows):
        return {"id": fid, "clause": "c", "lane": "A", "depends_on": [],
                "test": f"backend/tests/test_a.py::{fid}", "provenance": {"capability_rows": rows}}
    feats = [feat("a", ["24"]), feat("b", ["22"]), feat("c", ["30"]), feat("d", [])]
    s = F.summary(feats, {"outcomes": {"backend/tests/test_a.py::a": "passed"}})
    assert s["core"] == {"total": 2, "passing": 1} and s["total"] == 4
    assert "(core 1 of 2)" in F.headline(s)


def test_a_feature_lands_only_when_it_and_its_dependencies_pass() -> None:
    assert F.landing_refusal("X-1", THREE, RES) == []
    assert F.landing_refusal("X-2", THREE, RES)            # its own test fails
    ok = {"outcomes": {**RES["outcomes"], "backend/tests/test_a.py::test_unwritten": "passed"}}
    assert any("depends on X-2" in w for w in F.landing_refusal("X-3", THREE, ok))
    assert F.landing_refusal("X-9", THREE, RES) == ["X-9 is not in docs/define_features.json"]


def test_the_ratchet_refuses_a_regression_and_never_forgets(tmp_path) -> None:
    path = tmp_path / "ratchet.json"
    assert F.update_ratchet(THREE, RES, path) == ["X-1"]
    worse = {"outcomes": {"backend/tests/test_a.py::test_ok": "skipped"}}
    assert F.update_ratchet(THREE, worse, path) == []       # never removes
    assert F.ratchet(path) == ["X-1"]
    refused, _ = F.ratchet_refusal(["X-1"], THREE, worse)
    assert refused and "X-1 passed before" in refused[0]
    assert F.ratchet_refusal(["X-1"], THREE, RES) == ([], [])


# ── landing and the ratchet, through the commit guard itself ───────────────


@pytest.fixture
def no_git_env(monkeypatch):
    """Inside a commit hook git exports GIT_INDEX_FILE; a throwaway repo's
    `git add` would write into the commit's index (found at 6.66)."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)


def _git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          encoding="utf-8", env=env).stdout.strip()


def _guard():
    spec = importlib.util.spec_from_file_location(
        "guard_rule11", _REPO / ".claude" / "hooks" / "commit-msg-refactor-guard.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _repo(tmp_path: Path, outcome: str, ratchet: list[str] | None = None) -> Path:
    """A repo whose one feature DEF-900's test is recorded `outcome`, with the
    full-run marker naming its index tree — what the pre-commit hook leaves."""
    repo = tmp_path / "r"
    tools = repo / "agent-improve" / "tools" / "control_board"
    docs = repo / "agent-improve" / "docs"
    tools.mkdir(parents=True)
    docs.mkdir(parents=True)
    shutil.copy(_TOOLS / "features.py", tools / "features.py")
    feat = {"id": "DEF-900", "description": "d", "clause": "c", "depends_on": [], "lane": "A",
            "test": "backend/tests/test_x.py::test_x", "sources": {}, "provenance": {}}
    (docs / "define_features.json").write_text(json.dumps({"features": [feat]}), encoding="utf-8")
    (docs / "test-results.json").write_text(json.dumps(
        {"outcomes": {"backend/tests/test_x.py::test_x": outcome}}), encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    if ratchet is not None:
        (docs / "features-ratchet.json").write_text(json.dumps({"passing": ratchet}), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")    # a fixture repo with no hooks of its own
    (repo / ".claude" / "logs").mkdir(parents=True)
    (repo / ".claude" / "logs" / "full-run.json").write_text(
        json.dumps({"tree": _git(repo, "write-tree"), "exit": 0}), encoding="utf-8")
    return repo


def test_the_guard_refuses_a_DEF_commit_whose_test_fails(tmp_path, no_git_env) -> None:
    repo = _repo(tmp_path, "skipped")
    with pytest.raises(SystemExit):
        _guard().check_landing(str(repo), "refactor(arch-v2): DEF-900 — the thing works")


def test_the_guard_allows_a_DEF_commit_whose_test_passes(tmp_path, no_git_env) -> None:
    repo = _repo(tmp_path, "passed")
    _guard().check_landing(str(repo), "refactor(arch-v2): DEF-900 — the thing works")


def test_the_guard_refuses_a_regression_of_a_ratcheted_feature(tmp_path, no_git_env) -> None:
    repo = _repo(tmp_path, "skipped", ratchet=["DEF-900"])
    with pytest.raises(SystemExit):
        _guard().check_ratchet(str(repo))


def _continuity_repo(tmp_path: Path, block: str) -> Path:
    repo = tmp_path / "c"
    (repo / "agent-improve" / "docs").mkdir(parents=True)
    (repo / "agent-improve" / "docs" / "CONTINUITY.md").write_text(f"# C\n\n{block}\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo


def test_rule_5_passes_a_current_block_that_did_not_change(tmp_path, no_git_env, monkeypatch) -> None:
    """Found by 6.67's Part E proof: the features-derived block is often
    unchanged between commits, and an unchanged file is never staged — rule 5
    refused a correct commit for it."""
    g = _guard()
    block = f"{g.cs.BEGIN}\n| **Headline** | 9 of 64 |\n{g.cs.END}"
    repo = _continuity_repo(tmp_path, block)
    monkeypatch.setattr(g.cs, "build_block", lambda root: block)
    g.check_continuity(str(repo), [])                       # not staged, current: passes


def test_rule_5_still_refuses_a_stale_block(tmp_path, no_git_env, monkeypatch) -> None:
    g = _guard()
    repo = _continuity_repo(tmp_path, f"{g.cs.BEGIN}\n| **Headline** | 8 of 64 |\n{g.cs.END}")
    monkeypatch.setattr(g.cs, "build_block", lambda root: f"{g.cs.BEGIN}\n| **Headline** | 9 of 64 |\n{g.cs.END}")
    with pytest.raises(SystemExit):
        g.check_continuity(str(repo), [])


def test_the_guard_passes_a_ratcheted_feature_that_still_passes(tmp_path, no_git_env) -> None:
    _guard().check_ratchet(str(_repo(tmp_path, "passed", ratchet=["DEF-900"])))
