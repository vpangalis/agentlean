"""Controls review proposal, accepted 2026-09-30: the fact-ownership guard logs each refusal to
`.claude/logs/fact-ownership.log`, as the drift hook writes drift.log, and the session start counts
them. Until now a review could not tell what this guard caught."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import sys
from pathlib import Path

_HOOKS = Path(__file__).resolve().parents[3] / ".claude" / "hooks"


def _load(name: str, file: str):
    sys.path.insert(0, str(_HOOKS))
    spec = importlib.util.spec_from_file_location(name, _HOOKS / file)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_refusal_is_logged_and_counted(tmp_path, monkeypatch) -> None:
    guard = _load("fact_ownership_guard", "fact-ownership-guard.py")
    guard._record(tmp_path, "agent-improve/docs/x.md", ["PhaseState", "langgraph"])
    row = json.loads((tmp_path / ".claude" / "logs" / "fact-ownership.log").read_text(encoding="utf-8"))
    assert row["file"] == "agent-improve/docs/x.md" and row["facts"] == ["PhaseState", "langgraph"]
    src = (_HOOKS / "fact-ownership-guard.py").read_text(encoding="utf-8")
    assert src.index("_record(root, target,") < src.index(".join(out))", src.index("_record(root, target,"))

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    start = _load("session_start_fo", "session-start-context.py")
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
    assert start._fact_ownership_refusals(since) == "fact-ownership refusals (last 7 days): 1"
    os.environ.pop("CLAUDE_PROJECT_DIR", None)
