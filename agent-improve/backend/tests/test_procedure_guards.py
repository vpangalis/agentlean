"""The procedure's guards — commit-msg rules 18-21 (brief Part F4, founder 2026-09-27).

Each rule refused and passed, through the guard itself, on a throwaway repo that
carries the real requirement files, feature list and tools:

  18  requirements are well formed and covered
  19  the design gate — a feature lands only when its ADR (0057+) is ACCEPTED
  20  founder ownership — business.md / platform.md change only with `Ruling:`
  21  ADR immutability — an ACCEPTED record changes only to SUPERSEDED; links may move
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

_PROJECT = Path(__file__).resolve().parents[2]
_REPO = _PROJECT.parent
_ADR = "agent-improve/docs/adr/0058-refactoring-order-is-computed.md"
_NEW_ADR = "agent-improve/docs/adr/0099-a-proposed-decision.md"


@pytest.fixture
def no_git_env(monkeypatch):
    """Inside a commit hook git exports GIT_INDEX_FILE (found at 6.66)."""
    for k in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(k)


def _git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          encoding="utf-8", env=env).stdout.strip()


def _guard():
    spec = importlib.util.spec_from_file_location(
        "guard_procedure", _REPO / ".claude" / "hooks" / "commit-msg-refactor-guard.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(repo: Path, rel: str, text: str) -> None:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path, no_git_env) -> Path:
    r = tmp_path / "r"
    for rel in ("agent-improve/docs/requirements/business.md", "agent-improve/docs/requirements/platform.md",
                "agent-improve/docs/define_features.json", _ADR,
                "agent-improve/tools/control_board/features.py", "agent-improve/tools/control_board/adrs.py",
                "agent-improve/tools/control_board/rank.py"):
        (r / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(_REPO / rel, r / rel)
    _write(r, _NEW_ADR, "# ADR-0099 — A proposed decision\n\nStatus: PROPOSED (founder) · 2026-09-27\n\n"
                        "## Context\nSee [the file](../requirements/business.md).\n")
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@t")
    _git(r, "config", "user.name", "t")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "seed")
    return r


def _stage(repo: Path, rel: str, text: str) -> list[str]:
    _write(repo, rel, text)
    _git(repo, "add", rel)
    return _git(repo, "diff", "--cached", "--name-only").splitlines()


def _read(repo: Path, rel: str) -> str:
    return (repo / rel).read_text(encoding="utf-8")


# ── rule 20 — founder ownership ─────────────────────────────────────────────


def test_rule_20_refuses_a_requirement_change_without_a_ruling_and_passes_with_one(repo) -> None:
    rel = "agent-improve/docs/requirements/platform.md"
    staged = _stage(repo, rel, _read(repo, rel).replace("at most 4 model calls", "at most 5 model calls"))
    g = _guard()
    with pytest.raises(SystemExit):
        g.check_founder_ownership(str(repo), "docs(requirements): T69 says five\n", staged)
    g.check_founder_ownership(str(repo), "docs(requirements): T69 says five\n\n"
                              "Ruling: 2026-09-27 founder raised T69 to five calls\n", staged)


# ── rule 21 — ADR immutability ──────────────────────────────────────────────


def test_rule_21_refuses_an_edit_to_an_accepted_adr(repo) -> None:
    staged = _stage(repo, _ADR, _read(repo, _ADR).replace("on every commit", "on each commit"))
    with pytest.raises(SystemExit):
        _guard().check_adr_immutability(str(repo), staged)


def test_rule_21_passes_superseding_an_accepted_adr_and_a_link_only_change(repo) -> None:
    g = _guard()
    staged = _stage(repo, _ADR, _read(repo, _ADR).replace(
        "Status: ACCEPTED (founder, 2026-09-27)", "Status: SUPERSEDED by 0099"))
    g.check_adr_immutability(str(repo), staged)
    _git(repo, "reset", "-q", "--hard")
    staged = _stage(repo, _NEW_ADR, _read(repo, _NEW_ADR).replace("../requirements/business.md",
                                                                    "../requirements/platform.md"))
    g.check_adr_immutability(str(repo), staged)


def test_rule_21_refuses_deleting_a_record(repo) -> None:
    _git(repo, "rm", "-q", _NEW_ADR)
    staged = _git(repo, "diff", "--cached", "--name-only").splitlines()
    with pytest.raises(SystemExit):
        _guard().check_adr_immutability(str(repo), staged)


# ── rule 18 — requirements well formed and covered ──────────────────────────


def test_rule_18_refuses_an_accepted_requirement_left_without_a_feature(repo) -> None:
    rel = "agent-improve/docs/define_features.json"
    data = json.loads(_read(repo, rel))
    data["features"] = [f for f in data["features"] if f["requirement"] != "W6"]
    staged = _stage(repo, rel, json.dumps(data, indent=1, ensure_ascii=False))
    with pytest.raises(SystemExit):
        _guard().check_requirements(str(repo), staged)


def test_rule_18_refuses_a_requirement_without_its_fields_and_passes_the_real_files(repo) -> None:
    g = _guard()
    rel = "agent-improve/docs/requirements/business.md"
    staged = _stage(repo, rel, _read(repo, rel))
    g.check_requirements(str(repo), staged + [rel])            # the real files pass
    staged = _stage(repo, rel, _read(repo, rel).replace(" · MoSCoW: ? · Design: ADR-0001", "", 1))
    with pytest.raises(SystemExit):
        g.check_requirements(str(repo), staged)


# ── rule 19 — the design gate ───────────────────────────────────────────────


def _cite(repo: Path, design: str) -> None:
    """R1's Design becomes `design`, staged."""
    rel = "agent-improve/docs/requirements/business.md"
    _stage(repo, rel, _read(repo, rel).replace("**R1 Team copilot** · RATIFIED 2026-09-26 · MoSCoW: ? · Design: ADR-0001",
                                               f"**R1 Team copilot** · RATIFIED 2026-09-26 · MoSCoW: ? · Design: {design}"))


def test_rule_19_refuses_landing_a_feature_whose_adr_is_proposed(repo) -> None:
    _cite(repo, "ADR-0099")                                      # DEF-001 cites R1
    with pytest.raises(SystemExit):
        _guard().check_design_gate(str(repo), "refactor(arch-v2): DEF-001 — a case opens")


def test_rule_19_passes_an_accepted_adr_and_an_ungated_one(repo) -> None:
    g = _guard()
    _stage(repo, _NEW_ADR, _read(repo, _NEW_ADR).replace("PROPOSED (founder)", "ACCEPTED (founder)"))
    _cite(repo, "ADR-0099")
    g.check_design_gate(str(repo), "refactor(arch-v2): DEF-001 — a case opens")
    _cite(repo, "ADR-0001")                                      # before 0057: not gated
    g.check_design_gate(str(repo), "refactor(arch-v2): DEF-001 — a case opens")
