"""ARCHITECTURE.md's generated data models — founder, 2026-09-27 (Part G).

`tools/architecture/generate_models.py` writes the declarations and field tables
between the `data models` markers from the code, read with `ast` only. The
pre-commit hook regenerates the block; commit-msg rule 16 refuses a block that
differs from a fresh generation; rules 2b and 12 do not count it.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

_PROJECT = Path(__file__).resolve().parents[2]
_REPO = _PROJECT.parent
sys.path.insert(0, str(_PROJECT / "tools" / "architecture"))
sys.path.insert(0, str(_REPO / ".claude" / "hooks"))

import generate_models as gm  # noqa: E402

CLASSES = ("SupervisorState", "PhaseState", "SufficiencyJudgment", "CoachingPlan",
           "CoachingResponse", "DefineOutput", "MeasureOutput", "AnalyseOutput",
           "ImproveOutput", "ControlOutput")
DOC = ("# Title\n\nbefore\n\n"
       "<!-- BEGIN GENERATED: data models — never edit by hand. -->\n\nOLD BODY\n\n"
       "<!-- END GENERATED: data models -->\n\nafter\n")


def test_the_block_declares_every_class_and_every_table() -> None:
    body = gm.generate(_PROJECT)
    for name in CLASSES:
        assert f"class {name}(" in body, name
    assert body.startswith("### 4.2 Declarations"), "v2: the block is §4.2"
    for heading in ("#### Search indexes", "#### Store namespaces", "#### Blob layout"):
        assert heading in body
    assert "`content_digest`" in body and "`embedding`" in body and "`page_number`" in body
    assert gm.generate(_PROJECT) == body, "generation is deterministic"


def test_a_missing_class_fails_the_run_naming_it(tmp_path) -> None:
    shutil.copytree(_PROJECT / "backend", tmp_path / "backend",
                    ignore=shutil.ignore_patterns("tests", "__pycache__"))
    schema = tmp_path / "backend" / "phases" / "control" / "schema.py"
    schema.write_text(schema.read_text(encoding="utf-8").replace("class ControlOutput(",
                                                                  "class ControlRecord("),
                      encoding="utf-8")
    with pytest.raises(gm.GenerationError, match="ControlOutput"):
        gm.generate(tmp_path)


def test_a_changed_field_changes_the_block(tmp_path) -> None:
    shutil.copytree(_PROJECT / "backend", tmp_path / "backend",
                    ignore=shutil.ignore_patterns("tests", "__pycache__"))
    substate = tmp_path / "backend" / "core" / "substate.py"
    text = substate.read_text(encoding="utf-8")
    assert "    failed_criterion: Optional[str] = Field(" in text
    substate.write_text(text.replace("    failed_criterion: Optional[str] = Field(",
                                     "    failed_criterion: Optional[int] = Field(", 1),
                        encoding="utf-8")
    new = gm.generate(tmp_path)
    assert "failed_criterion: Optional[int]" in new and new != gm.generate(_PROJECT)


def test_only_the_text_between_the_markers_is_replaced() -> None:
    new = gm.replace_block(DOC, "NEW BODY\n")
    assert new.startswith("# Title\n\nbefore\n\n<!-- BEGIN GENERATED: data models — never edit by hand. -->")
    assert "OLD BODY" not in new and "NEW BODY" in new
    assert new.endswith("<!-- END GENERATED: data models -->\n\nafter\n")
    assert gm.is_current(new, "NEW BODY\n")
    assert not gm.is_current(new.replace("NEW BODY", "NEW BODY, hand-edited"), "NEW BODY\n")


def test_a_document_without_markers_is_left_alone() -> None:
    assert gm.replace_block("# no block\n", "x") == "# no block\n"
    assert gm.block_of("# no block\n") is None


def test_rule_12_does_not_measure_the_block_and_rule_2b_does_not_count_it() -> None:
    import size_budget
    assert size_budget.measure(DOC) == size_budget.measure(gm.replace_block(DOC, "x" * 5000))
    # 2b's comparison: the document with the block emptied.
    assert gm.replace_block(DOC, "") == gm.replace_block(gm.replace_block(DOC, "NEW"), "")
    assert gm.replace_block(DOC, "") != gm.replace_block(DOC.replace("after", "changed"), "")


def test_the_generator_never_imports_a_backend_module() -> None:
    src = (_PROJECT / "tools" / "architecture" / "generate_models.py").read_text(encoding="utf-8")
    assert "import backend" not in src and "from backend" not in src
    assert "importlib" not in src


def test_the_git_pipes_carry_bytes_so_nothing_is_staged_with_crlf() -> None:
    """The --stage bug of 2026-09-27: a text-mode stdin on Windows turned every
    newline into CRLF, so the index received a CRLF copy of the whole document.
    `hash-object --stdin` must hash exactly the LF text it is given."""
    import hashlib
    text = "line one\nline two\n"
    expected = hashlib.sha1(b"blob %d\x00" % len(text.encode()) + text.encode()).hexdigest()
    assert gm._git(["hash-object", "--stdin"], text).strip() == expected
    assert "\r" not in gm._git(["show", "HEAD:agent-improve/ARCHITECTURE.md"])[:5000]


def test_the_hooks_run_and_check_it() -> None:
    hook = (_REPO / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "generate_models.py --stage" in hook
    guard = (_REPO / ".claude" / "hooks" / "commit-msg-refactor-guard.py").read_text(encoding="utf-8")
    assert "check_generated_models(root, all_staged)" in guard
    assert "_status_changed_by_hand(root)" in guard


def test_the_declarations_live_in_their_own_file_linked_from_section_4_2() -> None:
    """Founder ruling 6, 2026-09-29: the generated block left ARCHITECTURE.md for
    docs/data-models.md, which §4.2 links; the file is current with the code."""
    arch = (_PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert gm.block_of(arch) is None, "ARCHITECTURE.md still carries the generated block"
    assert "[docs/data-models.md](docs/data-models.md)" in arch
    assert gm.DOC_REL == "agent-improve/docs/data-models.md"
    doc = (_PROJECT / "docs" / "data-models.md").read_text(encoding="utf-8")
    assert gm.is_current(doc, gm.generate(_PROJECT)), "docs/data-models.md differs from a fresh generation"
