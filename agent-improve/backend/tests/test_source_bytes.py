"""No control character in the product's source (G-347, founder ruling 2026-10-29, item 5).

A shell heredoc turns a written `\\b` into a backspace byte (chr 8). It is invisible in an editor and in a diff,
and a regex carrying it silently matches nothing: ui/index.html's captured-fields label regex held one from
fcd915a (2026-05-26) until G-347, and the same thing was caught in report.py on 2026-10-29 before its commit.
Read as text; nothing is imported."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_SOURCES = (("backend", "*.py"), ("ui", "*.html"), ("ui", "*.js"), ("scripts", "*.py"), ("skills", "*.md"),
            ("config", "*.yaml"), ("config", "*.json"), ("tools", "*.py"))
_ALLOWED = {"\t", "\n", "\r"}


def test_g347_no_control_character_in_the_product_source() -> None:
    """Every source file is free of control characters other than tab and line ends."""
    found = []
    for folder, pattern in _SOURCES:
        for path in sorted((ROOT / folder).rglob(pattern)):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                bad = sorted({f"chr({ord(c)})" for c in line if ord(c) < 32 and c not in _ALLOWED})
                if bad:
                    found.append(f"{path.relative_to(ROOT).as_posix()}:{number} {', '.join(bad)}")
    assert not found, found


def test_g347_the_captured_fields_label_regex_is_a_word_boundary() -> None:
    """The line that held the backspace now title-cases each word of a field key, as fcd915a meant."""
    page = (ROOT / "ui" / "index.html").read_text(encoding="utf-8")
    assert "label:k.replace(/_/g,' ').replace(/\\b\\w/g,c=>c.toUpperCase())" in page
