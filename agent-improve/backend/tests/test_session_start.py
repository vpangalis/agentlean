"""The SessionStart hook prints its sections — step 6.67.

The hook is FAIL-SOFT by contract: any error is logged to stderr and it exits 0
with nothing on stdout, so a session simply starts without its context. That
is exactly how 6.67's Part A shipped it broken (a rewrite dropped three helper
functions; every session since started blind) and nothing noticed. So this
calls `main()` directly — where an exception is NOT swallowed — and checks the
sections are there. The PyPI lookup is stubbed: no network in the suite.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_HOOK = Path(__file__).resolve().parents[3] / ".claude" / "hooks" / "session-start-context.py"


def test_the_session_start_hook_prints_every_section(monkeypatch, capsys) -> None:
    spec = importlib.util.spec_from_file_location("session_start", _HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "get_latest_version", lambda pkg: None)
    assert mod.main() == 0
    out = capsys.readouterr().out
    for section in ("GIT STATE", "PROGRESS", "DEFINE FEATURES", "DEPENDENCY VERSIONS"):
        assert f"── {section}" in out, section
    assert "Define features pass" in out
