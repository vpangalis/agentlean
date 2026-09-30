"""Controls review, item 6 (founder, 2026-09-30): where the fix is only "regenerate the board", the
pre-commit hook regenerates and re-stages it instead of leaving rule 10 to refuse the commit."""
from __future__ import annotations

from pathlib import Path

_HOOK = Path(__file__).resolve().parents[3] / ".githooks" / "pre-commit"


def test_the_hook_checks_its_board_and_regenerates_once_when_it_disagrees() -> None:
    text = _HOOK.read_text(encoding="utf-8")
    at = text.index("agent-improve/tools/control_board/check_board.py")
    after = text[at:at + 700]
    assert "if ! " in text[at - 40:at + 10], "the check's failure is what triggers the rebuild"
    assert '"$CONTINUITY"' in after and '"$CONTROL" agent-improve/docs/control-board.html --staged' in after
    assert "git add agent-improve/docs/control-board.html" in after
