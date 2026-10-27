#!/usr/bin/env python3
"""B7 — the Define skill, generated from the code where it states what code owns — founder ruling 2026-10-27,
item 4: "code owns the criteria, their ids and the element order (one owner); the skill text and the welcome are
generated from it, not parsed."

Rewritten in `skills/dmaic-define-phase/SKILL.md`, from `backend/phases/define/criteria.py` (the owner) and the
schema's fields captured inside a position:

  * section 2's element table — each element's number, name and the fields captured at it;
  * each numbered head's number, `**[n · field · …]**` — the field's place in the owner's order; an unnumbered head
    that names `field n` (METRIC LITERACY) takes the number of the element block it stands before;
  * each element's acceptance criteria — the opening line, then one `- `id` — text` line per criterion;
  * the `[OPENING]` block — the welcome, the five phases, how Define is worked;
  * section F — how Define ends.

Everything else is the skill's own text and is left as it is. `coaching_script.md` is SKILL.md's section 3 (from the
`[OPENING]` block to the rule that closes the section), byte for byte: the whole file is generated.

The owner and the schema are read with `ast` — module-level literals, and names bound to them — and nothing is
imported, so the pre-commit hook runs this with the system Python. `test_generated_docs.py` fails when either file
differs from a fresh generation.

    generate_define_script.py --print | --write | --check | --stage
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import PROJECT, REPO, GenerationError, _git  # noqa: E402

OWNER = "backend/phases/define/criteria.py"
SCHEMA = "backend/phases/define/schema.py"
SKILL = "skills/dmaic-define-phase/SKILL.md"
MIRROR = "skills/dmaic-define-phase/coaching_script.md"
#: What the generation reads from the owner (and, for the fields captured inside a position, the schema).
NEEDED = ("ELEMENT_ORDER", "ELEMENT_NAMES", "CRITERIA", "CRITERIA_HEAD", "WELCOME", "PHASES",
          "HOW_DEFINE_IS_WORKED", "HOW_DEFINE_ENDS", "_CAPTURED_INSIDE")


# ── the owner, read with ast ────────────────────────────────────────────

def _value(node: ast.expr, env: dict[str, Any]) -> Any:
    """A literal, with a name read from `env` (a name bound to a literal earlier in the module, or the schema's)."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise GenerationError(f"{node.id} is not a literal")
        return env[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        return tuple(_value(e, env) for e in node.elts)
    if isinstance(node, ast.Dict) and all(k is not None for k in node.keys):
        return {_value(k, env): _value(v, env) for k, v in zip(node.keys, node.values) if k is not None}
    raise GenerationError(f"not a literal: {ast.unparse(node)[:60]}")


def _constants(path: Path, env: dict[str, Any]) -> dict[str, Any]:
    """`env` and the module-level names of `path` bound to a literal; any other binding is skipped."""
    out = dict(env)
    for node in ast.parse(path.read_text(encoding="utf-8"), filename=str(path)).body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name, value = node.target.id, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        else:
            continue
        try:
            out[name] = _value(value, out)
        except GenerationError:
            continue
    return out


def owner(project: Path) -> dict[str, Any]:
    """What the generation reads: the owner's constants, the schema's beside them."""
    env = _constants(project / OWNER, _constants(project / SCHEMA, {}))
    missing = [n for n in NEEDED if n not in env]
    if missing:
        raise GenerationError(f"{OWNER}: no literal {', '.join(missing)}")
    return env


# ── the parts of the skill code owns ────────────────────────────────────

_TABLE_HEAD = "| # | Element | Field(s) captured |\n|---|---|---|\n"
_TABLE_ROW = re.compile(r"\| \d+ \| [^|\n]+ \| [^|\n]+ \|\n")
_SECTION_F = "### F — The Define report\n\n"
_OPENING = re.compile(r"^\*\*\[OPENING[^\]]*\]\*\*[ \t]*\n((?:>.*\n)+)", re.M)
_HEAD = re.compile(r"^\*\*\[(?P<head>[^\]]+)\]\*\*[ \t]*$", re.M)
_FIELD_N = re.compile(r"\bfield (\d+)\b")
_CRITERIA_OPEN = re.compile(r"^> \*\*Acceptance criteria\*\*.*\n", re.M)


def _table(text: str, o: dict[str, Any]) -> str:
    """Section 2's element table: number, name, the fields captured — in the owner's order."""
    at = text.find(_TABLE_HEAD)
    if at < 0:
        raise GenerationError(f"{SKILL}: no element table ({_TABLE_HEAD.splitlines()[0]})")
    start = end = at + len(_TABLE_HEAD)
    while (row := _TABLE_ROW.match(text, end)) is not None:
        end = row.end()
    rows = []
    for n, field in enumerate(o["ELEMENT_ORDER"], start=1):
        fields = ", ".join(f"`{f}`" for f in (field, *o["_CAPTURED_INSIDE"].get(field, ())))
        rows.append(f"| {n} | {o['ELEMENT_NAMES'][field]} | {fields} |\n")
    return text[:start] + "".join(rows) + text[end:]


def _section_f(text: str, o: dict[str, Any]) -> str:
    """Section F's paragraph: how Define ends."""
    at = text.find(_SECTION_F)
    if at < 0:
        raise GenerationError(f"{SKILL}: no section {_SECTION_F.strip()!r}")
    start = at + len(_SECTION_F)
    return text[:start] + "\n".join(o["HOW_DEFINE_ENDS"]) + text[text.index("\n\n", start):]


def _opening(text: str, o: dict[str, Any]) -> str:
    """The [OPENING] block's lines: the welcome, the five phases, how Define is worked."""
    m = _OPENING.search(text)
    if m is None:
        raise GenerationError(f"{SKILL}: no [OPENING] block")
    lines = [o["WELCOME"], *(f"• **{name}** — {line}" for name, line in o["PHASES"]), o["HOW_DEFINE_IS_WORKED"]]
    return text[:m.start(1)] + "".join(f"> {line}\n" for line in lines) + text[m.end(1):]


def _numbered(head: str) -> Optional[str]:
    """The field of a numbered head (`n · field · …`), else None."""
    parts = [p.strip() for p in head.split("·")]
    return parts[1] if parts[0].isdigit() and len(parts) > 1 else None


def _element_fields(text: str, o: dict[str, Any]) -> list[str]:
    """The numbered blocks' fields, in the skill's order — each one of the owner's elements, every element once."""
    fields = [f for m in _HEAD.finditer(text) if (f := _numbered(m["head"]))]
    if sorted(fields) != sorted(o["ELEMENT_ORDER"]):
        raise GenerationError(f"{SKILL}: the numbered blocks {fields} are not the owner's elements, each once")
    return fields


def _heads(text: str, o: dict[str, Any]) -> str:
    """Each numbered head's number from the owner's order; `field n` in an unnumbered head from the element block it
    stands before."""
    order: tuple[str, ...] = o["ELEMENT_ORDER"]
    _element_fields(text, o)
    heads = list(_HEAD.finditer(text))
    out, last = [], 0
    for i, m in enumerate(heads):
        head, field = m["head"], _numbered(m["head"])
        if field:
            new = re.sub(r"^\d+", str(order.index(field) + 1), head, count=1)
        elif _FIELD_N.search(head):
            before = next((f for h in heads[i + 1:] if (f := _numbered(h["head"]))), None)
            if before is None:
                raise GenerationError(f"{SKILL}: [{head}] names a field and stands before no element's block")
            new = _FIELD_N.sub(f"field {order.index(before) + 1}", head, count=1)
        else:
            continue
        out += [text[last:m.start("head")], new]
        last = m.end("head")
    return "".join(out) + text[last:]


def _block_criteria(block: str, field: str, o: dict[str, Any]) -> str:
    """One element block with its criteria — the opening line and the `- `id`` lines after it — the owner's."""
    m = _CRITERIA_OPEN.search(block)
    items = o["CRITERIA"].get(field, ())
    if m is None or not items:
        raise GenerationError(f"{SKILL}: [{field}] — the block or the owner lists no acceptance criteria")
    end = m.end()
    while block.startswith("> - `", end):
        nl = block.find("\n", end)
        end = len(block) if nl < 0 else nl + 1
    lines = [f"> {o['CRITERIA_HEAD']}\n", *(f"> - `{cid}` — {text}\n" for cid, text in items)]
    return block[:m.start()] + "".join(lines) + block[end:]


def _criteria(text: str, o: dict[str, Any]) -> str:
    """Every element block's acceptance criteria from the owner."""
    _element_fields(text, o)
    heads = list(_HEAD.finditer(text))
    out, last = [], 0
    for i, m in enumerate(heads):
        field = _numbered(m["head"])
        if not field:
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out += [text[last:m.end()], _block_criteria(text[m.end():end], field, o)]
        last = end
    return "".join(out) + text[last:]


def mirror(skill: str) -> str:
    """`coaching_script.md`: SKILL.md's section 3, from the [OPENING] block to the rule that closes the section."""
    start = skill.find("\n**[OPENING")
    end = skill.find("\n---\n", start + 1) if start >= 0 else -1
    if end < 0:
        raise GenerationError(f"{SKILL}: no section 3 from [OPENING] to its closing rule")
    return skill[start + 1:end]


def generate(project: Path, skill: str) -> tuple[str, str]:
    """(SKILL.md, coaching_script.md) — `skill` with the parts code owns rewritten from `project`'s owner."""
    o = owner(project)
    for part in (_table, _section_f, _opening, _heads, _criteria):
        skill = part(skill, o)
    return skill, mirror(skill)


def stale(project: Path = PROJECT) -> list[str]:
    """The files that differ from a fresh generation ([] when both are current)."""
    skill = (project / SKILL).read_text(encoding="utf-8")
    fresh = dict(zip((SKILL, MIRROR), generate(project, skill)))
    return [rel for rel, text in fresh.items() if (project / rel).read_text(encoding="utf-8") != text]


# ── the command ─────────────────────────────────────────────────────────

def stage() -> str:
    """Pre-commit: from the STAGED owner and skill into the index copies of both files, and the working copies."""
    project_rel = PROJECT.name
    try:
        staged = _git(["show", f":{project_rel}/{SKILL}"])
    except GenerationError:
        return f"no staged {SKILL} — nothing to do"
    sys.path.insert(0, str(REPO / ".claude" / "hooks"))
    import staged_tree
    project = staged_tree.sync(REPO) / project_rel
    skill, script = generate(project, staged)
    work_skill, work_script = generate(project, (PROJECT / SKILL).read_text(encoding="utf-8"))
    done = []
    for rel, new, work in ((SKILL, skill, work_skill), (MIRROR, script, work_script)):
        path = f"{project_rel}/{rel}"
        if new == _git(["show", f":{path}"]):
            continue
        sha = _git(["hash-object", "-w", "--stdin"], input_=new).strip()
        mode = _git(["ls-files", "-s", path]).split()[0]
        _git(["update-index", "--cacheinfo", f"{mode},{sha},{path}"])
        (PROJECT / rel).write_text(work, encoding="utf-8", newline="")
        done.append(rel)
    return f"regenerated and staged: {', '.join(done)}" if done else "current"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="the Define skill's owned parts, generated from the code")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--print", action="store_true", help="print the generated SKILL.md")
    g.add_argument("--write", action="store_true", help=f"rewrite {SKILL} and {MIRROR}")
    g.add_argument("--check", action="store_true", help="exit 1 if either file is not current")
    g.add_argument("--stage", action="store_true", help="pre-commit: from the staged tree into the index")
    a = ap.parse_args(argv)
    try:
        if a.stage:
            print(f"  [define script] {stage()}", file=sys.stderr)
            return 0
        skill, script = generate(PROJECT, (PROJECT / SKILL).read_text(encoding="utf-8"))
        if a.print:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
            print(skill, end="")
            return 0
        if a.write:
            for rel, text in ((SKILL, skill), (MIRROR, script)):
                (PROJECT / rel).write_text(text, encoding="utf-8", newline="")
            return 0
        differ = stale()
        if not differ:
            print(f"{SKILL}, {MIRROR}: current")
            return 0
        print(f"{', '.join(differ)}: differs from a fresh generation — run with --write")
        return 1
    except GenerationError as exc:
        print(f"define script: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
