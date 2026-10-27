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

FIELDS = {"id", "description", "clause", "depends_on", "test", "sources", "lane", "provenance",
          "requirement", "belt_impact", "rework_risk", "effort", "priority_override",
          "phase", "stage", "layer"}
#: Carried by M2 features only: the founder's pilot cut (2026-09-30), true | false (rank.py --check).
#: `package` and `merged_into`: founder ruling 2026-10-20 (fixed packages; merged duplicates).
#: `structural`: founder ruling 2026-10-24 — see test_the_structural_features_are_exactly_the_six_ruled.
OPTIONAL = {"pilot", "run_criteria", "package", "merged_into", "track", "structural"}
#: Founder ruling 2026-10-24: features whose test checks content, the page's own script, the ingest or a live record
#: by nature, so the wiring check's "drives neither the graph nor the API" does not demote them. Exactly these six;
#: a further one needs the founder's ruling.
STRUCTURAL = {"DEF-024", "DEF-120", "DEF-136", "DEF-175", "DEF-205", "DEF-206"}
CLAUSES = {"A Belt is coached through the thirteen elements",
           "what they say is kept and every change is dated",
           "a complete case ASSEMBLES a gate document",
           "the Belt sees it, approves it",
           "the record is written once and correctly"}


@pytest.fixture(scope="module")
def feats() -> list[dict]:
    return F.load()


def test_every_feature_has_the_founders_fields_and_no_status(feats) -> None:
    for f in feats:
        assert FIELDS <= set(f) <= FIELDS | OPTIONAL, (f["id"], set(f) ^ FIELDS)
        assert f["lane"] in F.LANES, f["id"]
        assert f["test"].startswith("backend/tests/test_") and "::test_" in f["test"], f["id"]


def test_the_structural_features_are_exactly_the_six_ruled(feats) -> None:
    """Founder ruling 2026-10-24: `structural: true` is carried by exactly the six ruled features, and only as true;
    the board does not demote them for a test that drives neither the graph nor the API, and still demotes every
    other such feature."""
    marked = {f["id"] for f in feats if "structural" in f}
    assert marked == STRUCTURAL, f"structural is the founder's ruling, feature by feature: {sorted(marked ^ STRUCTURAL)}"
    assert all(f["structural"] is True for f in feats if "structural" in f)
    shallow = F.shallow(feats)
    assert not shallow & STRUCTURAL, sorted(shallow & STRUCTURAL)
    unmarked = [{k: v for k, v in f.items() if k != "structural"} for f in feats]
    assert STRUCTURAL <= F.shallow(unmarked), "without the mark the six are flagged — the exemption is the mark"


def test_every_feature_cites_a_citable_requirement_and_every_one_has_a_feature(feats) -> None:
    """Brief Part A (founder, 2026-09-27). A feature cites ONE id that is RATIFIED or
    ACCEPTED in docs/requirements/business.md, or ACCEPTED in platform.md — never a
    PROPOSED, DRAFT or RETIRED one. Every RATIFIED or ACCEPTED business id, and every
    ACCEPTED T id whose proof is `none`, has at least one feature."""
    reqs = F.requirements()
    ok = F.citable(reqs)
    cited = {f["requirement"] for f in feats}
    assert cited <= ok, sorted(cited - ok)
    business = {i for i in ok if not i.startswith("T")}
    unproven = {i for i in ok if i.startswith("T") and reqs[i]["proof_none"]}
    assert business | unproven <= cited, sorted((business | unproven) - cited)


def test_every_requirement_carries_moscow_and_design_and_the_checker_refuses_one_without() -> None:
    """Brief Part F2 (founder, 2026-09-27): every entry of business.md and platform.md has
    `MoSCoW:` (`?` allowed until ratified) and `Design: ADR-nnnn | none` on its heading line."""
    assert F.field_problems(F.requirements()) == []
    texts = {n: (F.REQUIREMENTS / n).read_text(encoding="utf-8") for n in ("business.md", "platform.md")}
    texts["business.md"] = texts["business.md"].replace(
        "**R1 Team copilot** · RATIFIED 2026-09-26 · MoSCoW: Must · Design: ADR-0001",
        "**R1 Team copilot** · RATIFIED 2026-09-26 · Design: ADR-0001")
    texts["platform.md"] = texts["platform.md"].replace("| Must | ADR-0015 | `test_state.py", "| Must | | `test_state.py", 1)
    assert F.field_problems(F.requirements(texts=texts)) == [
        "R1 (business.md) has no MoSCoW: field", "T1 (platform.md) has no Design: field"]


def test_every_feature_carries_the_rank_inputs_and_no_priority(feats) -> None:
    """Brief Part F3 (ADR-0058): belt_impact, rework_risk, effort, priority_override on every
    feature; the typed `priority` of Part A is gone — the order is computed, never stored."""
    import rank
    assert rank.problems(feats) == []
    assert not any("priority" in f or "rank" in f for f in feats)


def _rf(fid, req, impact="degraded", rework="low", effort="M", deps=(), lane="A", override=None):
    return {"id": fid, "requirement": req, "belt_impact": impact, "rework_risk": rework,
            "effort": effort, "depends_on": list(deps), "lane": lane, "priority_override": override,
            "test": f"backend/tests/test_x.py::test_{fid}"}


def _reqs(**moscow):
    return {k: {"status": "ACCEPTED", "moscow": v, "design": "none"} for k, v in moscow.items()}


def test_the_rank_tiers_scores_and_never_places_a_feature_above_its_dependency() -> None:
    """ADR-0058's rule, on a fixture: tier 1 = Belt-blocking and Must; else MoSCoW tiers;
    score = (impact + rework + unblocks) ÷ effort; a dependency takes its dependent's tier
    and ranks above it; an override wins; `?` ranks as Must, marked provisional;
    Won't-now is not ranked."""
    import rank
    fs = [_rf("A", "R1", impact="dead_end", effort="L"),          # tier 1, score 3/3 = 1
          _rf("B", "R2", impact="degraded", effort="S"),          # tier 3 (Should), score 1
          _rf("C", "R3", impact="wrong_data", deps=["D"]),        # tier 1 (? = Must), 1.5
          _rf("D", "R2", impact="none", effort="S"),              # raised to tier 1 by C
          _rf("E", "R4"),                                         # Won't-now: not ranked
          _rf("F", "R2", override={"rank_tier": 1, "reason": "founder: demo on Monday"})]
    r = rank.rank(fs, {"outcomes": {}}, _reqs(R1="Must", R2="Should", R3="?", R4="Won't-now"))
    order = [x["id"] for x in r]
    assert "E" not in order
    assert order.index("D") < order.index("C")
    assert {x["id"]: x["tier"] for x in r} == {"A": 1, "C": 1, "D": 1, "F": 1, "B": 3}
    why = {x["id"]: x["reason"] for x in r}
    assert "raised to tier 1: C depends on it" in why["D"]
    assert "provisional" in why["C"] and "founder override to tier 1: founder: demo on Monday" in why["F"]
    assert {x["id"]: x["score"] for x in r}["D"] == 1.0          # (0 + 0 + 1 unblocked) ÷ 1
    assert rank.next_per_lane(r)["A"] == order[0]


def test_each_lane_takes_its_top_ranked_failing_feature(feats) -> None:
    import rank
    r = rank.rank(feats, {"outcomes": {}})
    nxt = F.summary(feats, {"outcomes": {}})["lanes"]
    for lane in F.LANES:
        mine = [x["id"] for x in r if x["lane"] == lane and not x["held"]]   # never a held one
        assert nxt[lane]["next"] == (mine[0] if mine else None), lane


def by_id(feats: list[dict]) -> dict[str, dict]:
    return {f["id"]: f for f in feats}


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
    import rank
    feats = [_rf("X-2", "R1", impact="dead_end", deps=["X-1"]), _rf("X-1", "R1", impact="none")]
    top = rank.next_per_lane(rank.rank(feats, {"outcomes": {}}, _reqs(R1="Must")))["A"]
    assert top == "X-1"                                  # the dependency first, whatever its score
    passed = {"outcomes": {"backend/tests/test_x.py::test_X-1": "passed"}}
    assert rank.next_per_lane(rank.rank(feats, passed, _reqs(R1="Must")))["A"] == "X-2"


# ── landing and the ratchet, as functions ───────────────────────────────────


def test_dependency_blocking_is_strict_through_the_whole_chain() -> None:
    """Founder ruling 2026-09-26: a feature whose dependency passes but whose
    dependency's dependency fails is blocked — lane A fixes DEF-005 first."""
    st = {"X-1": "failing", "X-2": "passing", "X-3": "failing"}
    assert F.blockers("X-3", THREE, st) == ["X-1"]
    import rank
    ranked = rank.rank(THREE, {"outcomes": {"backend/tests/test_a.py::test_bad": "passed"}}, {})
    assert rank.next_per_lane(ranked)["A"] == "X-1"
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


def test_a_regressed_run_through_feature_is_exempt_only_with_a_registered_defect(monkeypatch) -> None:
    """Founder ruling 5, 2026-09-28: a fresh run-through record that shows a regression is
    committed; the regressed feature is exempt from the ratchet when a registered defect names
    it, and refused when none does."""
    rt = [{"id": "R-1", "test": F.RUNTHROUGH_TESTS + "test_run_x", "depends_on": []}]
    monkeypatch.setattr(F, "runthrough_fresh", lambda: True)
    failing = {"outcomes": {F.RUNTHROUGH_TESTS + "test_run_x": "failed"}}
    refused, exempt = F.ratchet_refusal(["R-1"], rt, failing, defects=set())
    assert refused and not exempt
    assert F.ratchet_refusal(["R-1"], rt, failing, defects={"R-1"}) == ([], ["R-1"])


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


# Rule 5 (CONTINUITY's block current) retired with its two tests: founder ruling 2026-10-27, item 6.
# The pre-commit hook still regenerates the block (pre-commit-continuity.py).


def test_the_guard_passes_a_ratcheted_feature_that_still_passes(tmp_path, no_git_env) -> None:
    _guard().check_ratchet(str(_repo(tmp_path, "passed", ratchet=["DEF-900"])))


def test_the_next_package_is_the_fixed_one_holding_the_lanes_top_feature() -> None:
    """Founder ruling 2026-10-20: packages are fixed in the feature list; rank chooses the package — the one holding
    the lane's top-ranked failing feature that carries one. The package is all its features, whatever their lane,
    in rank order, passing ones after; points count the failing ones; over 5 it may take two prompts."""
    import rank
    fs = [{**_rf("A1", "R1", impact="dead_end", effort="L"), "package": "P2"},
          {**_rf("A2", "R1", effort="L"), "package": "P2"},
          {**_rf("B1", "R1", effort="S", lane="B"), "package": "P2"},
          {**_rf("A3", "R1", effort="S"), "package": "P1"},
          {**_rf("A4", "R1", impact="dead_end", effort="S")},                  # top of lane A, no package
          {**_rf("A5", "R1", effort="S"), "package": "P2"}]
    passed = {"outcomes": {"backend/tests/test_x.py::test_A5": "passed"}}
    ranked = rank.rank(fs, passed, _reqs(R1="Must"))
    assert [r["id"] for r in ranked if r["lane"] == "A"][:2] == ["A4", "A1"]
    got = rank.packages(fs, ranked)
    assert got["A"] == {"package": "P2", "features": ["A1", "B1", "A2", "A5"], "points": 7, "over": True}
    assert got["B"]["package"] == "P2"                       # B1's own lane chooses the same package
    assert got["C"] == {"package": None, "features": [], "points": 0, "over": False}
    # Founder ruling 2026-10-20 (P4 before P5): a package whose feature depends on a failing feature of another
    # package waits for it — the lane takes that package first.
    fs += [{**_rf("I1", "R1", impact="dead_end", effort="S", lane="integrator", deps=["C1"]), "package": "P5"},
           {**_rf("C1", "R1", effort="S", lane="C"), "package": "P4"}]
    got = rank.packages(fs, rank.rank(fs, passed, _reqs(R1="Must")), passed)
    assert got["integrator"]["package"] == "P4" and got["integrator"]["features"] == ["C1"], got["integrator"]


def test_the_define_count_leaves_out_other_phases_and_merged_features() -> None:
    """Founder ruling 2026-10-20: only phase-Define features that were not merged into another count toward
    Define; a merged feature is not ranked (its first carries it); `package` is P<n> and `merged_into` names a
    feature. On the real list: DEF-227 and DEF-228 (phase analyse) and the four merged features are left out."""
    import rank
    fs = [{**_rf(i, "R1"), "clause": "c", "sources": {}, "provenance": {"capability_rows": []}}
          for i in ("A1", "A2", "A3")]
    fs[1]["phase"], fs[2]["merged_into"] = "analyse", "A1"
    assert [f["id"] for f in fs if F.counted(f)] == ["A1"]
    s = F.summary(fs, {"outcomes": {}})
    assert s["total"] == 1 and s["lanes"]["A"]["total"] == 1
    # A later phase (A2, analyse) is not ranked while Define runs; a merged feature (A3) never is (2026-10-20).
    assert [r["id"] for r in rank.rank(fs, {"outcomes": {}}, _reqs(R1="Must"))] == ["A1"]
    bad = rank.problems([{**f, "belt_impact": "none", "rework_risk": "low", "effort": "S", "phase": "define",
                          "stage": "coached", "layer": "api"} for f in
                         ({**fs[0], "package": "pilot"}, {**fs[2], "merged_into": "X-9"})])
    assert any("package 'pilot' is not P<n>" in b for b in bad) and any("merged_into 'X-9'" in b for b in bad)
    real = F.load()
    reqs = F.requirements()
    out = {f["id"] for f in real if not F.counted(f, reqs)}
    # The ones the rulings named are out; and every feature out is out for one of the three reasons, no other.
    assert {"DEF-089", "DEF-090", "DEF-092", "DEF-106", "DEF-140", "DEF-227", "DEF-228"} <= out, out
    for f in real:
        if f["id"] in out:
            assert (f.get("phase", "define") != "define" or f.get("merged_into")
                    or (reqs.get(f["requirement"]) or {}).get("moscow") == "Won't-now"
                    or f.get("track") in ("platform", "post_define")), f["id"]   # rulings 2026-10-21, 2026-10-22
    # Founder ruling 2026-10-20: Won't-now is out of the count too (DEF-140 cites T68, Won't-now).
    assert not F.counted({**fs[0], "requirement": "T68"}, {"T68": {"moscow": "Won't-now"}})
    assert F.counted(fs[0], {"R1": {"moscow": "Must"}})
    assert {f["merged_into"] for f in real if f.get("merged_into")} == {"DEF-200", "DEF-213", "DEF-204", "DEF-214"}


def test_a_wallclock_test_is_read_from_the_run_through_stage(monkeypatch) -> None:
    """Founder ruling 4, 2026-09-28 (G-127): the commit hook no longer runs the wall-clock tests;
    their outcome comes from the run-through stage's record while it is fresh, and the ratchet
    exempts them while it is not."""
    t = sorted(F.WALLCLOCK_TESTS)[0]
    feats = [{"id": "W-1", "test": t, "depends_on": []}]
    monkeypatch.setattr(F, "wallclock_outcomes", lambda: ({t: "passed"}, True))
    assert F.status(feats, {"outcomes": {}}) == {"W-1": "passing"}
    monkeypatch.setattr(F, "wallclock_outcomes", lambda: ({t: "passed"}, False))
    assert F.status(feats, {"outcomes": {}}) == {"W-1": "failing"}
    assert F.ratchet_refusal(["W-1"], feats, {"outcomes": {}}, defects=set()) == ([], ["W-1"])


def test_a_run_criterion_is_a_live_run_check_and_holds_back_its_feature(feats, monkeypatch) -> None:
    """Desktop review of DEF-014, 2026-10-12: a feature whose requirement sets a run-level criterion
    its own test does not check names that check in `run_criteria` — tests on the live run's record —
    and passes only when its test and every run criterion pass."""
    for f in feats:
        for t in f.get("run_criteria") or []:
            assert t.startswith("backend/tests/test_define_runthrough.py::test_run_"), (f["id"], t)
            assert t != f["test"], f["id"]
    feature = {"id": "DEF-X", "test": "backend/tests/test_a.py::test_own",
               "run_criteria": ["backend/tests/test_define_runthrough.py::test_run_floor"]}
    passed = {"backend/tests/test_a.py::test_own": "passed"}
    assert F.status([feature], {"outcomes": passed}) == {"DEF-X": "failing"}
    assert F.awaiting_run_criterion([feature], {"outcomes": passed}) == {"DEF-X"}
    both = {**passed, "backend/tests/test_define_runthrough.py::test_run_floor": "passed"}
    assert F.status([feature], {"outcomes": both}) == {"DEF-X": "passing"}
    assert F.awaiting_run_criterion([feature], {"outcomes": both}) == set()
    # Rule 11b holds it like a run-through feature: refused, unless a registered defect names it.
    monkeypatch.setattr(F, "runthrough_fresh", lambda: True)
    refused, _ = F.ratchet_refusal(["DEF-X"], [feature], {"outcomes": passed}, defects=set())
    assert refused and "DEF-X" in refused[0]
    assert F.ratchet_refusal(["DEF-X"], [feature], {"outcomes": passed}, defects={"DEF-X"})[1] == ["DEF-X"]


def test_a_platform_track_feature_is_neither_counted_nor_ranked() -> None:
    """Founder ruling 2026-10-21, item 6: P25, P27, P28 (DEF-173 excepted), P30, P31, P32 and P34 move to the platform
    track — required before the first customer, not before Measure. A feature with `track: "platform"` does not count
    toward Define (R12 amended: "every Define feature passes, platform-track features excepted") and is not ranked
    while Define runs; P29 and DEF-173 stay on the Define track."""
    import rank
    fs = [{**_rf(i, "R1"), "clause": "c", "sources": {}, "provenance": {"capability_rows": []}} for i in ("A1", "A2")]
    fs[1]["track"] = "platform"
    assert [f["id"] for f in fs if F.counted(f, {"R1": {"moscow": "Must"}})] == ["A1"]
    assert [r["id"] for r in rank.rank(fs, {"outcomes": {}}, _reqs(R1="Must"))] == ["A1"]
    assert any("track 'x'" in p for p in rank.problems([{**fs[0], "track": "x", "belt_impact": "none",
                                                          "rework_risk": "low", "effort": "S", "phase": "define",
                                                          "stage": "coached", "layer": "api"}]))
    real = F.load()
    moved = {"P25", "P27", "P28", "P30", "P31", "P32", "P34"}
    for f in real:
        if f.get("package") in moved and f["id"] != "DEF-173":
            assert f.get("track") == "platform", f["id"]
        elif f.get("package") == "P29" or f["id"] == "DEF-173":
            assert f.get("track", "define") == "define", f["id"]


def test_a_post_define_feature_is_neither_counted_nor_ranked() -> None:
    """Founder ruling 2026-10-22 afternoon, item 5: DEF-107 moves to the post-Define list — it needs W4's open
    decision 1 and an ADR. A feature with `track: "post_define"` leaves the Define count and the queue, as the
    platform track does; docs/post_define.md lists it with what it waits for."""
    from pathlib import Path

    import rank
    fs = [{**_rf(i, "R1"), "clause": "c", "sources": {}, "provenance": {"capability_rows": []}} for i in ("A1", "A2")]
    fs[1]["track"] = "post_define"
    assert [f["id"] for f in fs if F.counted(f, {"R1": {"moscow": "Must"}})] == ["A1"]
    assert [r["id"] for r in rank.rank(fs, {"outcomes": {}}, _reqs(R1="Must"))] == ["A1"]
    assert "post_define" in rank.TRACKS
    real = {f["id"]: f for f in F.load()}
    assert real["DEF-107"].get("track") == "post_define"
    listed = (Path(__file__).resolve().parents[2] / "docs" / "post_define.md").read_text(encoding="utf-8")
    assert "DEF-107" in listed and "Team overview" in listed


def test_g247_a_feature_test_that_has_passed_carries_no_xfail() -> None:
    """G-247 — audit wave 1 item 5 (founder ruling 2026-10-20, "drop xfail once passed"): a Define feature test
    is measured (non-strict xfail) only until its feature enters the ratchet; from then on a regression fails
    the run. The run-through module stays measured: its record is a live run, and a stale or registered
    regression there is exempt by ruling (2026-09-26; ruling 5, 2026-09-28)."""
    feats: list[dict] = [{"id": "DEF-900", "test": "backend/tests/test_define_e2e.py::test_done"},
             {"id": "DEF-901", "test": "backend/tests/test_define_e2e.py::test_open",
              "run_criteria": ["backend/tests/test_define_runthrough.py::test_run_open"]}]
    measured = F.measured_tests(feats, ["DEF-900"])
    assert "backend/tests/test_define_e2e.py::test_done" not in measured
    assert {"backend/tests/test_define_e2e.py::test_open",
            "backend/tests/test_define_runthrough.py::test_run_open"} <= measured
    # The deterministic feature modules carry no blanket xfail: the marker is attached per test at collection.
    for name in F.STRICT_FEATURE_MODULES:
        assert "pytestmark = pytest.mark.xfail" not in (_PROJECT / name).read_text(encoding="utf-8"), name
    # On the tree: every ratcheted feature whose test lives in a strict module is collected without xfail.
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-n", "0", "-p", "no:cacheprovider",
                          *F.STRICT_FEATURE_MODULES, "--co", "-m", "xfail"],
                         cwd=_PROJECT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    collected_xfail = {l.strip() for l in out.stdout.splitlines() if "::" in l}
    assert out.returncode == 0 and collected_xfail, out.stdout[-2000:] + out.stderr[-2000:]
    done = {F.node_id(f["test"]) for f in F.load() if f["id"] in set(F.ratchet())}
    assert not (collected_xfail & done), sorted(collected_xfail & done)
