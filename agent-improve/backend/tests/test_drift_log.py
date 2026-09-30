"""Controls review, item 3 (founder, 2026-09-30): the drift hook's refusals are written to
`.claude/logs/drift.log`, and the session start counts them (it promised the log since commit 0.5.3;
nothing wrote it). The banned sample is built by concatenation: the drift hook scans this file too."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
_HOOKS = _REPO / ".claude" / "hooks"
_REGISTRY = _REPO / ".claude" / "config" / "deprecated_patterns.yaml"
SAGA_CLASS = "class Order" + "Saga:"


def test_a_drift_refusal_is_logged_and_the_session_start_counts_it(tmp_path) -> None:
    (tmp_path / ".claude" / "config").mkdir(parents=True)
    shutil.copy(_REGISTRY, tmp_path / ".claude" / "config" / "deprecated_patterns.yaml")
    envelope = {"tool_name": "Write", "tool_input": {
        "file_path": str(tmp_path / "agent-improve" / "backend" / "x.py"), "content": SAGA_CLASS + "\n    pass\n"}}
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(tmp_path)}
    r = subprocess.run([sys.executable, str(_HOOKS / "pre-tool-use-drift-check.py")], input=json.dumps(envelope),
                       capture_output=True, encoding="utf-8", env=env, timeout=60)
    assert r.returncode == 2, r.stderr
    rows = [json.loads(ln) for ln in (tmp_path / ".claude" / "logs" / "drift.log").read_text(encoding="utf-8").splitlines()]
    assert rows and rows[0]["pattern"] == "pattern-4-custom-saga" and rows[0]["file"].endswith("x.py")

    spec = importlib.util.spec_from_file_location("session_start", _HOOKS / "session-start-context.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    old = os.environ.get("CLAUDE_PROJECT_DIR")
    os.environ["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    try:
        assert mod.get_drift_warnings().splitlines()[0] == "drift refusals (last 7 days): pattern-4-custom-saga 1"
    finally:
        if old is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = old
