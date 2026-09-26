"""No MUST / NEVER / ALWAYS sentence weakens — rule 14 (step 6.68, founder ruling 2026-09-26).

`.claude/hooks/normative_check.py`, proven both ways: a dropped or softened
rule sentence is found, one kept in other words passes, a sentence the
retired list names passes; and the corpus today carries every normative
sentence of the pre-slimming corpus (the audit the ruling asked for).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_HOOKS = _REPO / ".claude" / "hooks"


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, _HOOKS / file)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nc = _load("normative_check_under_test", "normative_check.py")
OLD = {"r.md": "Never wrap a retrieval call in a bare except that returns an empty list.\n"}


def test_a_dropped_rule_sentence_is_found() -> None:
    got = nc.compare(OLD, {"r.md": "Retrieval errors are logged.\n"})
    assert [f["verdict"] for f in got] == ["dropped"]


def test_a_softened_rule_sentence_is_found() -> None:
    new = {"r.md": "Avoid wrapping a retrieval call in a bare except that returns an empty list.\n"}
    assert [f["verdict"] for f in nc.compare(OLD, new)] == ["weakened"]


def test_a_rule_kept_elsewhere_in_the_corpus_passes() -> None:
    new = {"other.md": "Never wrap any retrieval call in a bare except that returns an empty list.\n"}
    assert nc.compare(OLD, new) == []


def test_a_retired_sentence_passes() -> None:
    key = " ".join(nc.sentences(OLD["r.md"])[0].split())
    assert nc.compare(OLD, {"r.md": ""}, retired={key}) == []


def test_the_corpus_is_claude_md_the_rule_files_and_the_skills() -> None:
    assert nc.is_corpus("agent-improve/CLAUDE.md") and nc.is_corpus(".claude/rules/state.md")
    assert nc.is_corpus(".claude/skills/eight-d/SKILL.md")
    assert not nc.is_corpus("agent-improve/skills/dmaic-define-phase/SKILL.md")
    assert not nc.is_corpus("agent-improve/ARCHITECTURE.md")


@pytest.mark.skipif(not nc.corpus_at(nc.PRE_SLIM["claude"], ["agent-improve/CLAUDE.md"]),
                    reason="the pre-slimming commits are not in this clone")
def test_nothing_the_slimming_dropped_is_unaccounted_for() -> None:
    """The ruling's audit: every normative sentence before 69e9200 / e0e4d79 is
    in today's corpus, or classified in normative-retired.json."""
    assert nc.since_slim() == []
