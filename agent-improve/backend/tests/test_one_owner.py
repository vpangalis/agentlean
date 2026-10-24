"""One owner per rule (G-266; audit H4, H5, H6; founder ruling 2026-10-24, B2): a rule the product applies in
several places is written once, and every caller reads that one — a fix to one copy can no longer leave another
behind. Read with `ast` and the module text; nothing is imported."""
from __future__ import annotations

import ast
import re
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]


def _modules() -> list[tuple[str, str]]:
    return [(p.relative_to(BACKEND).as_posix(), p.read_text(encoding="utf-8"))
            for p in sorted(BACKEND.rglob("*.py")) if not p.relative_to(BACKEND).as_posix().startswith("tests/")]


def _defining(names: set[str]) -> list[tuple[str, str]]:
    """(module, name) for every function or module-level name in `names` the backend defines."""
    out = []
    for rel, text in _modules():
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
                out.append((rel, node.name))
            elif isinstance(node, ast.Assign):
                out += [(rel, t.id) for t in node.targets if isinstance(t, ast.Name) and t.id in names]
    return sorted(out)


def test_the_empty_value_rule_has_one_owner() -> None:
    """H4: the gate's "present" and the capture's "empty" are one function."""
    assert _defining({"_is_empty", "is_empty_capture"}) == [("core/substate.py", "is_empty_capture")]


def test_the_methodology_phase_filter_has_one_owner() -> None:
    """H5: the filter a methodology search sends and the one a failed search logs are one function, with one
    cross-phase value."""
    assert _defining({"_phase_filter", "phase_filter", "CROSS_PHASE_RELEVANCE"}) == [
        ("knowledge/retriever.py", "CROSS_PHASE_RELEVANCE"), ("knowledge/retriever.py", "phase_filter")]


def test_the_clock_has_one_owner() -> None:
    """H6: every stamp the product writes reads core/clock.py's utc_now — in any spelling of the call."""
    clock = re.compile(r"\bdatetime\.now\(|\butcnow\(")
    assert [rel for rel, text in _modules() if clock.search(text)] == ["core/clock.py"]


def test_temperatures_have_one_owner() -> None:
    """Audit A8 (founder ruling 2026-10-24, B5): every temperature a call uses is core/llm.py's ROLE_TEMPERATURES —
    no backend call to get_llm passes its own."""
    passing = []
    for rel, text in _modules():
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", "")) == "get_llm" \
                    and any(k.arg == "temperature" for k in node.keywords):
                passing.append(f"{rel}:{node.lineno}")
    assert passing == [], passing


def test_model_clients_are_built_in_one_place() -> None:
    """B5: the chat models and the embeddings are constructed in core/llm.py only."""
    built = sorted({rel for rel, text in _modules() for node in ast.walk(ast.parse(text))
                    if isinstance(node, ast.Call)
                    and getattr(node.func, "id", "") in ("AzureChatOpenAI", "AzureOpenAIEmbeddings")})
    assert built == ["core/llm.py"], built


def test_the_escalation_decision_has_one_owner() -> None:
    """B5 (one GATE_MAX_ATTEMPTS): a failed gate's count meets GATE_MAX_ATTEMPTS in gate_registry.gate_escalates
    only — the validation stack's layers 2b and 2d both read it."""
    comparing = [rel for rel, text in _modules() if re.search(r"[<>]=?\s*settings\.GATE_MAX_ATTEMPTS", text)]
    assert comparing == ["phases/gate_registry.py"], comparing
