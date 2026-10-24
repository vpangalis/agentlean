"""B4 (founder ruling 2026-10-24): the substance ratchet — broad excepts (ruff BLE001) and over-complex functions
(ruff C901) may fall, never rise. Commit-msg rule 25 applies `.claude/hooks/ruff_ratchet.py`; its refusal is pure
and tested here, and the count reads through `# noqa` markers."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_HOOKS = Path(__file__).resolve().parents[3] / ".claude" / "hooks"


def _ratchet():
    assert (_HOOKS / "ruff_ratchet.py").is_file(), f"{_HOOKS / 'ruff_ratchet.py'} is missing"
    spec = importlib.util.spec_from_file_location("ruff_ratchet", _HOOKS / "ruff_ratchet.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ruff_ratchet"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_a_new_broad_except_or_complex_function_is_refused() -> None:
    rr = _ratchet()
    rec = {"BLE001": 42, "C901": 7}
    assert rr.refusal(dict(rec), dict(rec), dict(rec)) == []
    assert any("BLE001" in w for w in rr.refusal({"BLE001": 43, "C901": 7}, rec, rec))
    assert any("C901" in w for w in rr.refusal({"BLE001": 42, "C901": 8}, rec, rec))


def test_a_raised_record_and_an_unfollowed_fall_are_refused() -> None:
    rr = _ratchet()
    assert any("RAISED" in w for w in rr.refusal({"BLE001": 43, "C901": 7}, {"BLE001": 43, "C901": 7},
                                                  {"BLE001": 42, "C901": 7}))
    assert any("did not follow" in w for w in rr.refusal({"BLE001": 40, "C901": 7}, {"BLE001": 42, "C901": 7},
                                                         {"BLE001": 42, "C901": 7}))


def test_the_count_reads_through_noqa(tmp_path) -> None:
    """A `# noqa: BLE001` hides a broad except from a reader, never from the count."""
    rr = _ratchet()
    backend = tmp_path / "agent-improve" / "backend"
    backend.mkdir(parents=True)
    (backend / "m.py").write_text("def f():\n    try:\n        return 1\n    except Exception:  # noqa: BLE001\n"
                                  "        return 0\n", encoding="utf-8")
    got = rr.measure(tmp_path, rr.venv_python(), 15)
    assert got == {"BLE001": 1, "C901": 0}, got
