#!/usr/bin/env python3
"""The data models, generated from the code — founder, 2026-09-27 (Part G); since founder ruling 6
of 2026-09-29 in their own file, `docs/data-models.md`, linked from ARCHITECTURE.md §4.2.

Rewrites ONLY the text between

    <!-- BEGIN GENERATED: data models ... -->      (the marker comment itself is kept)
    <!-- END GENERATED: data models -->

with the declarations and field tables of:

  * ten classes, found by name anywhere under `backend/` (tests excluded) —
    SupervisorState, PhaseState, SufficiencyJudgment, CoachingPlan,
    CoachingResponse and the five {Phase}Output. A missing class fails the run
    naming it; a name declared twice fails it too;
  * the search indexes — the knowledge index from its owner,
    `knowledge/retriever.py::KNOWLEDGE_INDEX_FIELDS`; the evidence and case
    indexes from `storage/layout.py`;
  * the Store namespaces and the Blob layout, from `storage/layout.py`.

**It reads source with `ast` (and `tokenize` for trailing comments) — it never
imports a backend module and never reads live Azure.** Writer/reader tables are
hand-written in ARCHITECTURE.md §3.2; nothing here produces them.

    generate_models.py --print                  # the block body, to stdout
    generate_models.py --write docs/data-models.md  # rewrite the block in place
    generate_models.py --check docs/data-models.md  # exit 1 if the block differs
    generate_models.py --stage                  # pre-commit: from the STAGED tree,
                                                # into the INDEX (and the working copy)
    --project DIR   read the source from DIR (default: this checkout's agent-improve/)

A document with no markers is left alone: --check passes, --write/--stage do
nothing. Python 3.11+, stdlib only.
"""
from __future__ import annotations

import argparse
import ast
import io
import subprocess
import sys
import tokenize
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parent
DOC_REL = "agent-improve/docs/data-models.md"
BEGIN = "<!-- BEGIN GENERATED: data models"
END = "<!-- END GENERATED: data models -->"

GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("4.1", ("SupervisorState",)),
    ("4.2", ("PhaseState",)),
    ("4.3", ("SufficiencyJudgment", "CoachingPlan", "CoachingResponse")),
    ("4.4", ("DefineOutput", "MeasureOutput", "AnalyseOutput", "ImproveOutput", "ControlOutput")),
)
#: v2 (ARCHITECTURE.md 2.0): the block is §4.2 "Declarations", one #### per group;
#: the hand-written §4.1 sits above it, outside the markers.
TITLES = {"4.3": "Planner and coach schemas", "4.4": "Phase records"}
_TYPE = {"SearchFieldDataType.String": "Edm.String", "SearchFieldDataType.Int32": "Edm.Int32",
         "SearchFieldDataType.Collection(SearchFieldDataType.Single)": "Collection(Edm.Single)"}
_KIND = {"SimpleField": "simple", "SearchableField": "searchable"}


class GenerationError(RuntimeError):
    pass


# ── reading the source ──────────────────────────────────────────────────────

def _parse(path: Path) -> tuple[ast.Module, list[str]]:
    text = path.read_text(encoding="utf-8")
    return ast.parse(text, filename=str(path)), text.splitlines()


def find_classes(project: Path, names: tuple[str, ...]) -> dict[str, tuple[str, ast.ClassDef, list[str]]]:
    backend = project / "backend"
    found: dict[str, list[tuple[str, ast.ClassDef, list[str]]]] = {n: [] for n in names}
    for path in sorted(backend.rglob("*.py")):
        rel = path.relative_to(backend).as_posix()
        if rel.startswith("tests/"):
            continue
        tree, lines = _parse(path)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name in found:
                found[node.name].append((rel, node, lines))
    missing = [n for n, hits in found.items() if not hits]
    if missing:
        raise GenerationError(f"class not found under backend/: {', '.join(missing)}")
    twice = {n: [h[0] for h in hits] for n, hits in found.items() if len(hits) > 1}
    if twice:
        raise GenerationError(f"class declared more than once: {twice}")
    return {n: hits[0] for n, hits in found.items()}


def _trailing_comment(lines: list[str], node: ast.AST) -> str:
    """The `# ...` comments on the lines a field declaration spans, joined."""
    src = "\n".join(lines[node.lineno - 1: node.end_lineno]) + "\n"  # type: ignore[attr-defined]
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError):
        return ""
    return " ".join(t.string.lstrip("#").strip() for t in toks if t.type == tokenize.COMMENT)


def _default(value: ast.expr | None) -> str | None:
    """The field's default as it reads in a declaration; None when required."""
    if value is None:
        return None
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "Field":
        if value.args and not (isinstance(value.args[0], ast.Constant) and value.args[0].value is Ellipsis):
            return ast.unparse(value.args[0])
        for kw in value.keywords:
            if kw.arg == "default":
                return ast.unparse(kw.value)
            if kw.arg == "default_factory":
                f = ast.unparse(kw.value)
                return {"list": "[]", "dict": "{}", "set": "set()", "str": "''"}.get(f, f"{f}()")
        return None
    return ast.unparse(value)


def render_class(name: str, rel: str, node: ast.ClassDef, lines: list[str]) -> str:
    bases = ", ".join(ast.unparse(b) for b in node.bases)
    fields = [s for s in node.body if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)]
    width = max((len(f.target.id) for f in fields), default=0) + 1  # type: ignore[union-attr]
    out = [f"class {name}({bases}):"]
    for f in fields:
        head = f"    {(f.target.id + ':').ljust(width + 1)}{ast.unparse(f.annotation)}"  # type: ignore[union-attr]
        d = _default(f.value)
        if d is not None:
            head += f" = {d}"
        c = _trailing_comment(lines, f)
        out.append(head + (f"  # {c}" if c else ""))
    if not fields:
        out.append("    ...")
    return "\n".join(out)


def _module_constant(tree: ast.Module, name: str) -> ast.expr:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == name and node.value is not None:
            return node.value
    raise GenerationError(f"constant {name} not found")


def _spec_from_calls(value: ast.expr) -> list[dict]:
    """`KNOWLEDGE_INDEX_FIELDS = [SimpleField(...), ...]` read as layout-style specs."""
    if not isinstance(value, ast.List):
        raise GenerationError("KNOWLEDGE_INDEX_FIELDS is not a list literal")
    spec = []
    for call in value.elts:
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)):
            raise GenerationError(f"unreadable index field: {ast.unparse(call)}")
        kw = {k.arg: k.value for k in call.keywords}
        f: dict = {"name": ast.literal_eval(kw["name"]),
                   "type": _TYPE.get(ast.unparse(kw["type"]), ast.unparse(kw["type"]))}
        if "vector_search_dimensions" in kw:
            f.update(kind="vector", dimensions=ast.literal_eval(kw["vector_search_dimensions"]),
                     profile=ast.literal_eval(kw["vector_search_profile_name"]))
        else:
            f["kind"] = _KIND.get(call.func.id, call.func.id)
        for flag in ("key", "filterable", "sortable", "facetable"):
            if flag in kw and ast.literal_eval(kw[flag]) is True:
                f[flag] = True
        spec.append(f)
    return spec


def render_index(spec: list[dict]) -> str:
    rows = ["| Field | Type | Attributes |", "|---|---|---|"]
    for f in spec:
        attrs = [a for a in ("key", "filterable", "sortable", "facetable") if f.get(a)]
        if f["kind"] == "searchable":
            attrs.insert(0, "searchable")
        if f["kind"] == "vector":
            attrs = [f"vector, {f['dimensions']} dimensions, profile `{f['profile']}`"]
        rows.append(f"| `{f['name']}` | `{f['type']}` | {', '.join(attrs) or '—'} |")
    return "\n".join(rows)


def _setting_default(config: ast.Module, setting: str) -> str:
    """`Settings.<setting>`'s default in core/config.py, resolving a module constant."""
    for node in ast.walk(config):
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            for s in node.body:
                if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name) and s.target.id == setting:
                    call = s.value
                    arg = None
                    if isinstance(call, ast.Call):
                        arg = call.args[0] if call.args else next(
                            (k.value for k in call.keywords if k.arg == "default"), None)
                    if isinstance(arg, ast.Name):
                        arg = _module_constant(config, arg.id)
                    if isinstance(arg, ast.Constant):
                        return str(arg.value)
    raise GenerationError(f"no default for setting {setting} in core/config.py")


# ── the block ───────────────────────────────────────────────────────────────

def generate(project: Path = PROJECT) -> str:
    names = tuple(n for _, group in GROUPS for n in group)
    classes = find_classes(project, names)
    parts: list[str] = []
    for num, group in GROUPS:
        paths = sorted({classes[n][0] for n in group})
        title = TITLES.get(num) or f"`{group[0]}`"
        where = ", ".join(f"`{p}`" for p in paths) if len(paths) <= 2 else "`phases/{phase}/schema.py`"
        body = "\n\n".join(render_class(n, *classes[n]) for n in group)
        parts.append(f"#### {title} — {where}\n\n```python\n{body}\n```")

    config, _ = _parse(project / "backend" / "core" / "config.py")
    retriever, _ = _parse(project / "backend" / "knowledge" / "retriever.py")
    layout_tree, _ = _parse(project / "backend" / "storage" / "layout.py")

    def lit(name: str):  # noqa: ANN202
        return ast.literal_eval(_module_constant(layout_tree, name))

    knowledge = _spec_from_calls(_module_constant(retriever, "KNOWLEDGE_INDEX_FIELDS"))
    idx = [
        ("AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX", "`knowledge/retriever.py::KNOWLEDGE_INDEX_FIELDS`", knowledge),
        ("AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX", "`storage/layout.py::EVIDENCE_INDEX`", list(lit("EVIDENCE_INDEX"))),
        ("AZURE_SEARCH_IMPROVE_CASE_INDEX", "`storage/layout.py::CASE_INDEX`", list(lit("CASE_INDEX"))),
    ]
    sec = ["#### Search indexes — Azure AI Search"]
    for setting, owner, spec in idx:
        sec.append(f"**`{_setting_default(config, setting)}`** — the default of `settings.{setting}`; "
                   f"fields owned by {owner}\n\n{render_index(spec)}")
    parts.append("\n\n".join(sec))

    ns = ["| Namespace | Key | Holds |", "|---|---|---|"]
    ns += [f"| `{a}` | `{b}` | {c} |" for a, b, c in lit("STORE_NAMESPACES")]
    parts.append("#### Store namespaces — `storage/layout.py::STORE_NAMESPACES`\n\n" + "\n".join(ns))

    container = _setting_default(config, "AZURE_BLOB_CONTAINER_IMPROVE")
    bl = ["| Path | Owner | Holds |", "|---|---|---|"]
    bl += [f"| `{p}` | `{o}` | {h} |" for p, o, h in lit("BLOB_PATHS")]
    parts.append(f"#### Blob layout — container `{container}` (the default of "
                 "`settings.AZURE_BLOB_CONTAINER_IMPROVE`); `storage/layout.py::BLOB_PATHS`\n\n"
                 + "\n".join(bl))
    state, _ = _parse(project / "backend" / "core" / "state.py")
    version = (f"**State schema version {ast.literal_eval(_module_constant(state, 'STATE_SCHEMA_VERSION'))}** "
               "(`core/state.py::STATE_SCHEMA_VERSION`, ADR-0065): written into every checkpoint's metadata, "
               "every Store record and every case blob; an older one is migrated on load by "
               "`core/migrations.py`, a newer one is refused.")
    return "### 4.2 Declarations\n\n" + version + "\n\n" + "\n\n".join(parts) + "\n"


def _span(doc: str) -> tuple[int, int] | None:
    """(start, end) of the replaceable text: after the BEGIN comment, up to END."""
    b = doc.find(BEGIN)
    if b < 0:
        return None
    start = doc.index("-->", b) + len("-->")
    end = doc.find(END, start)
    if end < 0:
        raise GenerationError("BEGIN GENERATED: data models has no END marker")
    return start, end


def replace_block(doc: str, body: str) -> str:
    span = _span(doc)
    if span is None:
        return doc
    return doc[:span[0]] + "\n\n" + body + "\n" + doc[span[1]:]


def block_of(doc: str) -> str | None:
    span = _span(doc)
    return None if span is None else doc[span[0]:span[1]]


def is_current(doc: str, body: str) -> bool:
    return doc == replace_block(doc, body)


# ── git: the staged tree and the index ─────────────────────────────────────

def _git(args: list[str], input_: str | None = None) -> str:
    """Bytes on the pipes, decoded here: a text-mode stdin on Windows turns every
    newline into CRLF, which would stage a CRLF copy of the whole document."""
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                       input=None if input_ is None else input_.encode("utf-8"))
    if r.returncode != 0:
        raise GenerationError(f"git {' '.join(args)}: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")


def staged_project() -> Path:
    sys.path.insert(0, str(REPO / ".claude" / "hooks"))
    import staged_tree
    return staged_tree.sync(REPO) / "agent-improve"


def stage() -> str:
    """Pre-commit: regenerate from the STAGED source into the INDEX copy of the
    document, and the same block into the working copy (its other edits kept)."""
    try:
        staged_doc = _git(["show", f":{DOC_REL}"])
    except GenerationError:
        return "no staged docs/data-models.md — nothing to do"
    if _span(staged_doc) is None:
        return "no generated block in docs/data-models.md — nothing to do"
    body = generate(staged_project())
    new = replace_block(staged_doc, body)
    if new == staged_doc:
        return "data models block current"
    sha = _git(["hash-object", "-w", "--stdin"], input_=new).strip()
    mode = _git(["ls-files", "-s", DOC_REL]).split()[0]
    _git(["update-index", "--cacheinfo", f"{mode},{sha},{DOC_REL}"])
    work = REPO / DOC_REL
    work.write_text(replace_block(work.read_text(encoding="utf-8"), body), encoding="utf-8", newline="")
    return "data models block regenerated and staged"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--print", action="store_true")
    g.add_argument("--write", metavar="DOC")
    g.add_argument("--check", metavar="DOC")
    g.add_argument("--stage", action="store_true")
    ap.add_argument("--project", type=Path, default=PROJECT)
    a = ap.parse_args(argv)
    try:
        if a.stage:
            print(f"  [data models] {stage()}", file=sys.stderr)
            return 0
        body = generate(a.project)
        if a.print:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
            print(body, end="")
            return 0
        path = Path(a.write or a.check)
        doc = path.read_text(encoding="utf-8")
        if a.write:
            path.write_text(replace_block(doc, body), encoding="utf-8", newline="")
            return 0
        if _span(doc) is None:
            print(f"{path}: no generated block — nothing to check")
            return 0
        if is_current(doc, body):
            print(f"{path}: the data models block is current")
            return 0
        print(f"{path}: the data models block differs from a fresh generation")
        return 1
    except GenerationError as exc:
        print(f"generate_models: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
