#!/usr/bin/env python3
"""Re-run every counted claim in ARCHITECTURE.md against the tree.

    python .claude/hooks/verify_built.py           # report
    python .claude/hooks/verify_built.py --quiet   # exit code only

WHY THIS FILE EXISTS, and it is one row's fault
-----------------------------------------------
`docs/ARCHITECTURE_STATUS.md` carried the row **"1 of 5 SKILL.md files
written"**. It was copied from `CONTINUITY.md` on the day that file was created
and was **wrong from its first commit** — all five existed. It sat wrong for
weeks, in the one document whose own header promised *"verified against the
tree, never from a document"*.

**A MARKER NOTHING RE-RUNS IS A CLAIM.** The `> **BUILT:**` lines in
ARCHITECTURE.md (§55.2) say what exists; this says whether that is still true.
The failure mode being guarded is not a wrong number — it is a number that
**ages without saying so**, because nothing ever asks it again.

WHAT IT DOES NOT DO
-------------------
**It checks counts, not correctness.** `20 computation tools exist` is
checkable here; `they compute the right thing` is `pytest`'s job, and
`the coach uses them well` is a live-run's. A check that claimed more than it
tests would be the same defect one level up.

**The `METRIC LITERACY` grep is a PROXY and is labelled as one** — it answers
"does this file carry the one §32 item Define was missing", not "does it carry
all seven". A file can satisfy an item without using the phrase. The full check
is reading the file against §32's list.

THE PINNED VENV IS MANDATORY
    Every Python probe runs `agent-improve/.venv`, never whatever is on PATH.
    WATCH 2: the repo root carries a second, older interpreter, and a probe
    against it answers for the wrong tree or not at all.

Python 3.11+, standard library only.
"""
from __future__ import annotations

import importlib
import importlib.metadata
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or "."
PROJECT = os.path.join(ROOT, "agent-improve")
VENV = os.path.join(PROJECT, ".venv", "Scripts", "python.exe")
if not os.path.exists(VENV):                       # POSIX layout
    VENV = os.path.join(PROJECT, ".venv", "bin", "python")
ARCH = os.path.join(PROJECT, "ARCHITECTURE.md")
PROCEDURE = os.path.join(PROJECT, "docs", "REFACTORING_PROCEDURE.md")


def _ver(step: str) -> tuple:
    """`6.9` sorts below `6.10`. String order would put it above."""
    return tuple(int(p) for p in step.split("."))


def count_lines(rel: str, pattern: str) -> str:
    """Lines in `rel` matching `pattern`. NO SHELL.

    The first cut of this file shelled out to `grep`. On Windows that runs
    through cmd.exe, which does not strip the single quotes a POSIX shell
    would — so two probes returned an EMPTY STRING and were reported as
    disagreements against a tree that was in fact correct. **A check whose
    failures are its own quoting teaches you to ignore it**, which is the
    failure mode this file exists to prevent, arriving through the back door.
    """
    rx = re.compile(pattern)
    text = Path(os.path.join(ROOT, rel)).read_text(encoding="utf-8", errors="replace")
    return str(sum(1 for ln in text.splitlines() if rx.search(ln)))


def count_glob(pattern: str) -> str:
    from glob import glob
    return str(len(glob(os.path.join(ROOT, pattern))))


def count_glob_containing(pattern: str, needle: str) -> str:
    from glob import glob
    n = 0
    for f in glob(os.path.join(ROOT, pattern)):
        if needle in Path(f).read_text(encoding="utf-8", errors="replace"):
            n += 1
    return str(n)


def count_tree_containing(rel_dir: str, needle: str, skip: str) -> str:
    n = 0
    for base, _, files in os.walk(os.path.join(ROOT, rel_dir)):
        if skip in base.replace("\\", "/"):
            continue
        for f in files:
            if f.endswith(".py") and needle in Path(base, f).read_text(
                    encoding="utf-8", errors="replace"):
                n += 1
    return str(n)


def route_set() -> str:
    """Every `@router.<verb>("<path>")` in `routes.py`, as `VERB /path`.

    **The SET, not the count** - added 2026-09-11. Section 49's marker
    miscounted which routes its own table names, while a count of eleven
    agreed with the tree on every run. A population check cannot see a route
    renamed, and cannot be asked which ones the spec covers; a sorted set can
    be diffed against the table by eye in one line.
    """
    rx = re.compile(r'^@router\.(get|post|delete|put|patch)\(\s*"([^"]+)"')
    text = Path(os.path.join(ROOT, "agent-improve/backend/gateway/routes.py")
                ).read_text(encoding="utf-8", errors="replace")
    found = set()
    for ln in text.splitlines():
        m = rx.match(ln)
        if m:
            found.add(f"{m.group(1).upper()} {m.group(2)}")
    return " | ".join(sorted(found))


def count_call_sites(rel_dir: str, func: str) -> str:
    """Real calls to `func` in `rel_dir`, parsed with `ast`. Tests excluded.

    **THE PARSE IS THE POINT, AND THE FIRST CUT PROVED IT.** This began as a
    line filter that stripped `#` comments, skipped docstring bodies and
    dropped any line carrying a backtick. It returned **3** where the true
    answer is **1**: two of its hits were the token inside a logging format
    string, and no amount of further line-level filtering reaches those
    without also hiding real code. `ast` distinguishes a call from a mention
    by construction, which no grep can.

    **Why a call-site check exists at all.** A `grep-absence` claim is
    self-falsifying the moment someone writes a guard naming the token it
    forbids - found twice on 2026-09-11: `set_entry_point` returns three
    hits, all comments reading *"never set_entry_point"*, and
    `COACH_RECURSION_LIMIT` returns one, the regression test asserting its
    absence. Steps 2.4 and 6.7 both HOLD; both Done-whens, read literally,
    now fail. The mechanism they describe is fine; the phrasing is not
    re-runnable, and this is what re-runnable looks like.
    """
    import ast

    n = 0
    for base, _, files in os.walk(os.path.join(ROOT, rel_dir)):
        norm = base.replace(chr(92), "/")
        if "/tests" in norm or "__pycache__" in norm:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            try:
                tree = ast.parse(Path(base, f).read_text(
                    encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                name = (fn.id if isinstance(fn, ast.Name) else
                        fn.attr if isinstance(fn, ast.Attribute) else None)
                if name == func:
                    n += 1
    return str(n)


def _is_pinned_interpreter() -> bool:
    """Are we ALREADY running under `agent-improve/.venv`?

    WATCH 2 is why `py()` shells out to a pinned interpreter at all: the repo
    root carries a second, older venv, and a probe against it answers for the
    wrong tree. **That rule is about WHICH interpreter answers, not about
    spawning a process** - so when this one is already the pinned one, the
    subprocess is a copy of ourselves and the guarantee is met without it.
    """
    try:
        return os.path.realpath(sys.executable) == os.path.realpath(VENV)
    except Exception:                               # noqa: BLE001
        return False


def py(code: str) -> str:
    """Run a probe against the pinned venv and return its last stdout line.

    **IN-PROCESS when we are already the pinned interpreter, subprocess
    otherwise.** Eleven probes, each importing langchain and langgraph in a
    cold interpreter, cost 49 seconds - acceptable for a hand-run advisory
    tool, not acceptable inside `pytest`, which rule 4 runs on every spine
    commit. A check people wait 49s for is a check someone eventually skips.

    The fast path `exec`s the same probe source with `cwd` set to PROJECT,
    because two probes open `ARCHITECTURE.md` by relative path. Failures are
    returned as text, exactly as the subprocess path returns stderr, so a
    broken probe reads as a disagreement rather than crashing the run.
    """
    if _is_pinned_interpreter():
        import contextlib
        import io as _io

        buf = _io.StringIO()
        cwd = os.getcwd()
        if PROJECT not in sys.path:
            sys.path.insert(0, PROJECT)
        try:
            os.chdir(PROJECT)
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "<verify_built probe>", "exec"),
                     {"__name__": "__probe__"})
        except BaseException as exc:                # noqa: BLE001
            return f"PROBE FAILED: {exc!r}"
        finally:
            os.chdir(cwd)
        lines = buf.getvalue().strip().splitlines()
        return lines[-1] if lines else ""

    out = subprocess.run([VENV, "-c", code], cwd=PROJECT, capture_output=True,
                         text=True, timeout=120)
    return (out.stdout.strip() or out.stderr.strip().splitlines()[-1:] or [""])[0] \
        if not out.stdout.strip() else out.stdout.strip()



# ── F-15's check: every state field needs a writer AND a reader. ───────────
#
# **Seven instances before anything checked for it.** The Store's `case`
# namespace (closed 6.8), `PhaseState.uploads` (6.11), §6's "evidence context"
# reader (6.12), `get_evidence_vectorstore()` (called by nothing),
# `computation_results`, `phase_metrics` and `final_output`. §55.1's
# bidirectional rule governs references between DOCUMENTS; nothing applied it
# between a declaration and its reader, so each was found by hand, while
# building something adjacent, months apart.
#
# **Exemptions are DECLARED with a reason, never baselined.** Three fields are
# genuinely one-sided by specification, and a check that quietly tolerated
# them would tolerate the next one too.
PAIRING_EXEMPT = {
    "history": "§5 / §6 — diagnostic only; *no control logic reads it*, by spec",
    "remaining_steps": "§6 — engine-managed: LangGraph writes it, the executor "
                       "reads it. A writer here would be the WATCH-26 bug",
    "phase_index": "§5 — its readers are the UI progress display, which is "
                   "`ui/index.html`; no Python reader is expected",
}

#: Keys §7 and §39.x.7 name on `artifacts` that are not coached fields, so
#: nothing writes them by capture. This is where F-15 keeps recurring.
PAIRING_ARTIFACT_KEYS = ("computation_results", "phase_metrics", "acknowledged_gaps")

_STATE_ANNOTATIONS = {"PhaseState", "SupervisorState"}


def _state_write_dicts(tree: "object") -> set:
    """ids of dict literals that are a STATE WRITE, by the three real idioms.

    **Not "any dict literal anywhere", and not "only `return {...}`".** The
    first cut counted every key in every dict and reported
    `computation_results` as written five times - those five are the
    gate-document assemblers CONSTRUCTING a document from
    `artifacts.get("computation_results", [])`, which is a READ. A heuristic
    that calls a read a write cannot find a missing write.

    The second cut counted only `return {...}` and swung the other way,
    calling `final` and `validator_feedback` unwritten when both are written
    through the other two idioms. **A check that cries wolf is worse than no
    check.** All three idioms the codebase actually uses:

        return {...}                a node's state update
        Command(update={...})       §17's routing update
        state: PhaseState = {...}   the input mappers' construction
    """
    import ast

    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            out.add(id(node.value))
        elif isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "update" and isinstance(kw.value, ast.Dict):
                    out.add(id(kw.value))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Dict):
            ann = node.annotation
            name = ann.id if isinstance(ann, ast.Name) else getattr(ann, "attr", "")
            if name in _STATE_ANNOTATIONS:
                out.add(id(node.value))
    return out


def unpaired_state_fields() -> str:
    """`name:W` / `name:R` for every field missing a writer / a reader.

    `W` means nothing writes it; `R` means nothing reads it. Declared-and-
    entirely-unused reads `WR`.
    """
    import ast

    writes: dict[str, set] = {}
    reads: dict[str, set] = {}
    for base, _, files in os.walk(os.path.join(PROJECT, "backend")):
        norm = base.replace("\\", "/")
        if "/tests" in norm or "__pycache__" in norm:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            try:
                tree = ast.parse(Path(base, f).read_text(
                    encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            state_dicts = _state_write_dicts(tree)
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict) and id(node) in state_dicts:
                    for k in node.keys:
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            writes.setdefault(k.value, set()).add(f)
                elif isinstance(node, ast.Subscript):
                    sl = node.slice
                    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                        (writes if isinstance(node.ctx, ast.Store) else reads
                         ).setdefault(sl.value, set()).add(f)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("get", "setdefault", "pop") and node.args:
                        a0 = node.args[0]
                        if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                            reads.setdefault(a0.value, set()).add(f)
                            if node.func.attr == "setdefault":
                                writes.setdefault(a0.value, set()).add(f)

    names = py("from backend.core.state import SupervisorState as S; "
               "from backend.core.substate import PhaseState as P; "
               "print(','.join(dict.fromkeys(list(S.__annotations__) + "
               "list(P.__annotations__))))")
    fields = [n for n in names.split(",") if n] + list(PAIRING_ARTIFACT_KEYS)

    out = []
    for name in fields:
        if name in PAIRING_EXEMPT:
            continue
        flag = ("W" if name not in writes else "") + ("R" if name not in reads else "")
        if flag:
            out.append(f"{name}:{flag}")
    return " ".join(sorted(out))



# ── Titles: the board renders names, so the names have to be the source's. ─
#
# **The board types no title anywhere** — section names come from
# ARCHITECTURE.md's headings, step names from Appendix D. That makes the board
# safe and moves the risk one level back: **the two sources can disagree with
# each other**, and then the board faithfully renders a wrong name.
#
# Found on the first run, 2026-09-11: **seven steps**. One was semantic — 6.9's
# row said *"SKILL.md conformance to §32's seven"* while its section said *"The
# four missing SKILL.md files"*, two descriptions of different work. Four were
# body headings carrying `· **BLOCKED**` / `**GATED**` / `**DONE**` /
# `**EXTERNAL**`, **a second hand-maintained source for the one fact Appendix
# D's Status column exists to own.**
PROCEDURE_DOC = os.path.join(PROJECT, "docs", "REFACTORING_PROCEDURE.md")

#: Words carried by both forms of a title without being part of its name.
_TITLE_STOP = {"the", "a", "an", "and", "of", "to", "with", "its",
               "·", "—", "in", "for", "on"}
#: Status belongs in Appendix D's cell, never in a heading.
_TITLE_STATUS = {"blocked", "gated", "external", "done"}


def _title_tokens(text: str) -> set:
    text = re.sub(r"\*\*|`", "", text).lower()
    return {w for w in re.split(r"[^\w§'\-\{\}./]+", text)
            if w and w not in _TITLE_STOP}


def step_title_mismatches() -> str:
    """Appendix D's row title vs the step's own `## Step X.Y — ...` heading.

    **Not byte-equality, deliberately.** A row is a SHORT FORM — *"Middleware
    1–3"* against *"Middleware positions 1–3"* — and demanding equality would
    force 58 edits that make the index worse. The rule is that a short form may
    DROP words and may not INVENT them: every significant word in the row must
    appear in the heading. That passes abbreviation and fails drift.

    Also fails a status token in a heading, which is a second source for
    Appendix D's Status cell.
    """
    text = Path(PROCEDURE_DOC).read_text(encoding="utf-8")
    i = text.index("## Appendix D")
    j = text.index("## Appendix E", i)
    rows = {m.group(1): m.group(2).strip() for m in re.finditer(
        r"^\| \d+ \| \*\*Commit (\d+\.\d+)\*\* \| (.*?) \| ?\w* ?\| \w+ \| \w+ \|",
        text[i:j], re.M)}
    heads = {m.group(1): m.group(2).strip() for m in re.finditer(
        r"^## Step (\d+\.\d+) — (.+?)\s*$", text, re.M)}

    bad = []
    for step in sorted(set(rows) | set(heads),
                       key=lambda x: tuple(int(n) for n in x.split("."))):
        if step not in heads:
            bad.append(f"{step}:no-section")
            continue
        if step not in rows:
            bad.append(f"{step}:no-row")
            continue
        invented = _title_tokens(rows[step]) - _title_tokens(heads[step])
        if invented:
            bad.append(f"{step}:row-invents({','.join(sorted(invented))})")
        status = _title_tokens(heads[step]) & _TITLE_STATUS
        if status:
            bad.append(f"{step}:status-in-heading({','.join(sorted(status))})")
    return " ".join(bad)


def section_title_sources() -> str:
    """How many rendered names the board TYPES rather than reads. Must be 0.

    `build_board.py` must derive every section name from ARCHITECTURE.md's
    headings and every step name from Appendix D. A literal title in the
    generator is a third copy, and the one that cannot be corrected by editing
    a document.
    """
    src = Path(os.path.join(ROOT, ".claude", "hooks", "build_board.py")
               ).read_text(encoding="utf-8")
    # **The RENDERED form, not "any string with a § in it".** The first cut
    # matched `"§55.3 found but no rows matched the row format"` - an error
    # message - and reported a typed title that did not exist. A check whose
    # failures are its own regex teaches you to ignore it, which is the one
    # thing this file exists to prevent.
    #
    # The board renders `§N — Title`; a typed name would have to look like
    # that, or map a section to prose in a literal.
    # **STRING LITERALS ONLY, via `ast`** - the third cut of this probe. A
    # regex over raw source counted the example inside a COMMENT that
    # explains the rule ("§49 — API surface"), and reported a typed title
    # that does not exist. Comments are not rendered; `ast` never sees them.
    import ast

    rx = re.compile(r"^§\d+(?:\.\d+)*\s+—\s+[A-Za-z].{3,}")
    n = 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if rx.match(node.value.strip()):
                n += 1
    return str(n)


# ── The checks. (label, expected, probe, which BUILT marker it backs) ──────
#
# `expected` is written here rather than parsed out of the prose, deliberately:
# a check that reads its own expectation from the document it is checking
# cannot fail. That is the "check that cannot fail" this project keeps naming.

# ═══ THE ANCHOR EVALUATOR — Appendix F’s Evidence column (step 6.31) ═══
#
# Never a line number. A line number is invalidated by an edit to any line
# ABOVE it, and it fails by pointing at the WRONG line rather than at
# nothing — which is the silent half of every anchoring scheme this
# repository has already rejected.



PASS, FAIL, DEPENDENCY, EXTERNAL, MALFORMED = (
    "PASS", "FAIL", "DEPENDENCY", "EXTERNAL", "MALFORMED")

_SET_RE = re.compile(r"^(?P<body>[^{=]+?)\s*\{(?P<items>[^}]*)\}$")
_VAL_RE = re.compile(r"^(?P<body>[^{=]+?)\s*=(?P<val>.+)$")


def _members(obj) -> set[str] | None:
    """The comparable member set of a symbol, or None if it has none.

    A dict gives its KEYS; a list of tool objects gives their `.name`; a
    pydantic model gives its field names; any other iterable gives `str()` of
    its elements. **Deliberately not `dir()`** — a set anchor is about the
    thing's declared contents, never about its Python attributes.
    """
    if isinstance(obj, dict):
        return {str(k) for k in obj}
    flds = getattr(obj, "model_fields", None)
    if isinstance(flds, dict):
        return {str(k) for k in flds}
    if isinstance(obj, (list, tuple, set, frozenset)):
        return {str(getattr(x, "name", x)) for x in obj}
    return None


_MODULE_RE = re.compile(r"^[A-Za-z_][\w]*(\.[A-Za-z_][\w]*)*$")


class MalformedAnchor(ValueError):
    """A module path that could never import, whatever the tree looked like.

    **This exists because of a FALSE PASS it caught on its first run.** Step
    6.31's own row carried `absent: .claude.hooks.verify_built::read_matrix`.
    `.claude.hooks.verify_built` is not a legal module name — it starts with a
    dot — so the import could never succeed, so the `absent:` was **trivially
    true and would have stayed true forever**, including after the symbol was
    built. The row would have reported PASS while claiming the opposite of the
    tree.

    **An anchor that cannot fail is the failure mode this whole appendix
    exists to end**, and an `absent:` anchor is where it hides: a positive
    anchor that cannot resolve fails loudly, while a negative one goes quiet.
    So a malformed module path is MALFORMED, never PASS.
    """


def _resolve(body: str):
    """`mod::Symbol` or `mod::Symbol.attr` -> (found, value)."""
    if "::" not in body:
        return None, None
    mod, _, path = body.partition("::")
    if not _MODULE_RE.match(mod.strip()):
        raise MalformedAnchor(
            f"{mod.strip()!r} is not a legal module name, so this anchor can "
            f"never resolve — which would make an `absent:` cell permanently "
            f"and silently true")
    try:
        obj = importlib.import_module(mod.strip())
    except Exception:                                    # noqa: BLE001
        return False, None
    for part in path.strip().split("."):
        # A dict is traversed by KEY first. `SHAPES_BY_PHASE.define` means the
        # "define" entry, not an attribute called `define` — and a mapping
        # almost never has the latter, so attribute-first would report every
        # dict anchor as unresolved.
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        elif hasattr(obj, part):
            obj = getattr(obj, part)
        else:
            return False, None
    return True, obj


def evaluate_anchor(cell: str, root: str) -> tuple[str, str]:
    """(verdict, detail) for one Evidence cell."""
    try:
        return _evaluate_anchor(cell, root)
    except MalformedAnchor as exc:
        return MALFORMED, str(exc)


def _evaluate_anchor(cell: str, root: str) -> tuple[str, str]:
    cell = (cell or "").strip().strip("`")
    if not cell:
        return MALFORMED, "empty Evidence cell — nothing proves this row"

    if cell.startswith("azure:"):
        return EXTERNAL, cell[6:].strip()

    negated = cell.startswith("absent:")
    if negated:
        cell = cell[7:].strip()
    installed = cell.startswith("installed:")
    if installed:
        cell = cell[10:].strip()

    # ---- `repo:` — a path, resolved from the REPOSITORY ROOT --------------
    #
    # Explicit, because the two roots in this tree are a real trap: `.claude/`
    # sits ABOVE `agent-improve/`, so a bare relative path is ambiguous and
    # gets resolved silently against whichever root the caller passed. It cost
    # five false FAILs on this evaluator's first run.
    if cell.startswith("repo:"):
        rel = cell[5:].strip().rstrip("/")
        hit = os.path.exists(os.path.join(root, rel))

        # ── G-72: an `absent:` path whose PARENT does not exist ───────
        #
        # **The second instance of the unfailable-`absent:` class in one day,
        # which is why this fixes the CLASS and not the row.** Step 10.2
        # carried `absent: repo:agent-improve/frontend/gate_document.js` and
        # there is no `agent-improve/frontend/` — the UI is
        # `agent-improve/ui/`. The cell passed, and **would have kept passing
        # after 10.2 shipped**, because 10.2 ships into `ui/`.
        #
        # `MalformedAnchor` already catches the MODULE form of this. It
        # validates a module name and cannot reach a path — which is exactly
        # how the same defect survived in a different spelling.
        #
        # **The rule: to declare a FILE absent, the directory it belongs in
        # must exist.** If the whole directory is missing, declare the
        # DIRECTORY absent (`absent: repo:backend/evals`) or use the module
        # form (`absent: backend.evals`). Both start failing the moment the
        # thing is created; a file inside a directory that will never be
        # created starts failing never.
        #
        # **Scoped to `absent:` deliberately.** A POSITIVE path anchor whose
        # parent is missing already FAILs, and a loud failure needs no guard.
        if negated and not hit:
            parent = os.path.dirname(rel)
            if parent and not os.path.isdir(os.path.join(root, parent)):
                raise MalformedAnchor(
                    f"{rel!r} claims a file is absent, but its directory "
                    f"{parent!r} does not exist — so this can never start "
                    f"failing, whatever is built. Declare the DIRECTORY "
                    f"absent instead (`absent: repo:{parent}`), or use the "
                    f"module form")

        ok = (not hit) if negated else hit
        return (PASS if ok else FAIL,
                f"path {'present' if hit else 'absent'}: {rel}")

    # ---- `installed: <dist> =<version>` — a DISTRIBUTION, not a module ----
    if installed and "::" not in cell:
        m = _VAL_RE.match(cell)
        dist = (m.group("body") if m else cell).strip()
        try:
            got = importlib.metadata.version(dist)
        except Exception:                                # noqa: BLE001
            return DEPENDENCY, f"{dist} is not installed"
        if not m:
            return PASS, f"{dist} {got}"
        want = m.group("val").strip()
        return ((PASS, f"{dist} {got}") if got == want
                else (DEPENDENCY, f"{dist} is {got}, the matrix says {want}"))

    # ---- a bare dotted MODULE — `backend.evals` ---------------------------
    #
    # A whole package is the honest anchor for a step that creates one, and
    # `absent: backend.evals` is the cleanest statement that 7.0 is not built.
    if "::" not in cell:
        if "/" in cell or "\\" in cell:
            return MALFORMED, ("a path anchor needs the `repo:` prefix so the "
                               "root it resolves against is not a guess")
        if not re.fullmatch(r"[A-Za-z_][\w.]*", cell):
            return MALFORMED, f"not an anchor: {cell}"
        try:
            importlib.import_module(cell)
            found = True
        except Exception:                                # noqa: BLE001
            found = False
        ok = (not found) if negated else found
        if ok:
            return PASS, ("module absent, as claimed" if negated
                          else "module imports")
        if installed:
            return DEPENDENCY, f"module not in the installed library: {cell}"
        return FAIL, (f"{cell} imports, but the row claims it is absent"
                      if negated else f"{cell} does not import")

    # ---- set form: mod::Symbol {a,b} --------------------------------------
    m = _SET_RE.match(cell)
    if m:
        found, obj = _resolve(m.group("body"))
        if not found:
            ok = negated
            v = DEPENDENCY if (installed and not ok) else (PASS if ok else FAIL)
            return v, f"unresolved: {m.group('body').strip()}"
        want = {s.strip() for s in m.group("items").split(",") if s.strip()}
        got = _members(obj)
        if got is None:
            return MALFORMED, f"{m.group('body').strip()} has no member set"
        ok = (got != want) if negated else (got == want)
        if ok:
            return PASS, f"set of {len(got)}"
        return FAIL, (f"set differs — missing {sorted(want - got) or '[]'}, "
                      f"unexpected {sorted(got - want) or '[]'}")

    # ---- value form: mod::Symbol =v ---------------------------------------
    m = _VAL_RE.match(cell)
    if m:
        found, obj = _resolve(m.group("body"))
        if not found:
            ok = negated
            v = DEPENDENCY if (installed and not ok) else (PASS if ok else FAIL)
            return v, f"unresolved: {m.group('body').strip()}"
        want = m.group("val").strip()
        got = str(obj)
        ok = (got != want) if negated else (got == want)
        return (PASS if ok else FAIL), f"value {got!r} vs {want!r}"

    # ---- bare resolve: mod::Symbol ----------------------------------------
    found, _ = _resolve(cell)
    ok = (not found) if negated else found
    if ok:
        return PASS, "resolves" if not negated else "absent, as claimed"
    if installed:
        return DEPENDENCY, f"not in the installed library: {cell}"
    return FAIL, ("resolves, but the row claims it is absent" if negated
                  else f"does not resolve: {cell}")


# ═══════════════════════════════════════════════════════════════════════════
# THE MATRIX REFEREE — Appendix F (step 6.31)
# ═══════════════════════════════════════════════════════════════════════════
#
# The 24 checks above are HAND-WRITTEN: someone chose a claim and typed an
# expected value beside it. That is why there were only 24 of them against 69
# markers — every one costs an author. Appendix F inverts it: the DOCUMENT
# carries the claim and the anchor, and this reads them all.
#
# **FAIL-CLOSED, and that is a change of character for this script.** It was
# advisory — `build_board.py` calls it and renders the board either way. As
# the referee for the one document that now owns build status, an internal
# error must BLOCK. `CONTINUITY.md` §7: a check that cannot fail is worse than
# no check, because it is recorded as evidence.

#: The exact shape `matrix_covers_appendix_d` returns when the two agree.
#: The commit guard matches on this rather than re-deriving set equality —
#: two implementations of one invariant is the drift this file exists to catch.
MATRIX_CLEAN_RE = re.compile(r"^\d+ steps, both directions$")

#: **The row key is the FACT, not the step** (founder ruling 2026-09-18).
#: `Step` is an ATTRIBUTE: a step row names the step that delivers it, a marker
#: row names the step that closes it, and a fact nothing schedules carries `—`.
#: So the step cell is `[^|]*` where it used to be `\*\*\d+\.\d+\*\*` — a
#: pattern that REQUIRED a step would drop every unscheduled fact from the parse
#: silently, which is the failure mode this register exists to end.
MATRIX_ROW_RE = re.compile(
    r"^\|\s*L(?P<layer>\d+)\s*\|"          # Layer — also the board's block
    r"(?P<order>[^|]*)\|"                  # Order — sparse, hand-set
    r"(?P<zone>[^|]*)\|"                   # Zone — Container derives from it
    r"(?P<step>[^|]*)\|"                   # Step — an attribute, may be `—`
    r"(?P<item>[^|]*)\|"                   # Fact — what the § specifies
    r"(?P<state>[^|]*)\|"                  # State
    r"(?P<evidence>[^|]*)\|"               # Symbol — the anchor, may be `—`
    r"(?P<ref>[^|]*)\|\s*$", re.M)

#: Every step number a row's `Step` cell names. A cell may name more than one
#: (a marker closing 7.3 and 7.6), or none.
_STEP_IN_CELL = re.compile(r"(?<!\d)(\d+\.\d+)(?!\d)")

#: A cell carrying no anchor and no step. Not a blank: blank is a malformed
#: cell and stays an error.
NOT_SET = "—"

#: The four verdicts that are NOT a disagreement between matrix and tree.
#: `EXTERNAL` is owed, never passed; `DEPENDENCY` has a different owner.
_NOT_A_MARKER_FAILURE = ("PASS", "EXTERNAL")


def read_matrix(text: str | None = None) -> list[dict]:
    """Appendix F's rows. Raises if the appendix is missing — fail-CLOSED.

    `text` is injected by the COMMIT GUARD, which must read the **index** and
    not the disk: §0.32 clause 1, the same reason rule 8 resolves its registers
    from `git show :<path>`. A matrix check that read the working tree would
    pass a commit whose STAGED matrix is broken, and fail one whose staged
    matrix is fine while the tree is mid-edit. Default `None` keeps every
    existing caller — `CHECKS` included — reading the tree, which is correct
    for a hand-run tool.
    """
    if text is None:
        text = Path(PROCEDURE).read_text(encoding="utf-8")
    start = text.find("## Appendix F — The build matrix")
    if start < 0:
        raise RuntimeError(
            "Appendix F is missing from REFACTORING_PROCEDURE.md. It is the "
            "leading document for build status (step 6.31); without it this "
            "script cannot referee anything, and reporting success would be "
            "the failure mode §55.2 exists to name.")
    end = text.find("\n## Appendix ", start + 10)
    body = text[start:end if end > 0 else len(text)]
    return [m.groupdict() for m in MATRIX_ROW_RE.finditer(body)]


def appendix_d_steps(text: str | None = None) -> set:
    """The steps Appendix D declares. Read, never typed."""
    if text is None:
        text = Path(PROCEDURE).read_text(encoding="utf-8")
    return set(re.findall(r"^\|\s*\d+\s*\|\s*\*\*Commit (\d+\.\d+)\*\*\s*\|",
                          text, re.M))


#: Things an open gap legitimately attaches to that are NOT architectural
#: facts and never will be: appendices, other gaps, and FILES that carry no §
#: of their own. **Enumerated with a reason, never baselined** - `ui/index.html`
#: is here because G-71 IS the gap that it has no owner, and a check demanding
#: a fact row for it would force inventing the very thing G-71 says is absent.
ATTACH_NOT_A_FACT = {
    "Appendix D", "Appendix F", "F-15", "G-63", "build_board.py",
    "deprecated_patterns.yaml", "gateway/routes.py", "storage/blob.py",
    "ui/index.html", "verify_built.py",
}

_GAP_OPEN = re.compile(r"^\|\s*(?P<struck>~~)?\*\*(?P<gap>G-\d+)\*\*")
_SID = re.compile(r"(?<![\w-])S-[CF]\d+(?![\w-])")


def _register_facts(text: str) -> tuple:
    """`(§ keys, S-id keys)` the fact table defines."""
    secs, sids = set(), set()
    for r in read_matrix(text):
        ref = r["ref"].strip()
        if re.fullmatch(r"§[\d.]+", ref):
            secs.add(ref)
        sids |= set(_SID.findall(r["item"]))
    return secs, sids


def gap_refs_resolve(text: str | None = None) -> str:
    """ASSERTION 5, the half that is checkable at 6.39.

    **Every `S-id` an OPEN gap attaches to must have a row in the register.**
    Before this step 26 gaps referenced an `S-id` whose section carried no
    marker, so not one of them could name a fact that exists; the 96 spec-entry
    rows are what make the question answerable.

    **THE `§` HALF WAITS FOR 6.40 AND THE CONDITION IS STATED RATHER THAN
    ASSUMED.** 19 distinct sections an open gap names carry neither a fact row
    nor a `NOT-MARKABLE` declaration - §19, §20.5.1, §55.1, §56, §6, §4.6 among
    them. Most are governance rules that are probably NOT-MARKABLE, and
    **creating a fact row for each would pre-empt exactly the judgement 6.40
    exists to make** - then delete it again. So this ranges over `S-id`s now
    and gains its `§` half when every section declares one or the other.

    Closed gaps are out of scope: §66.6's rows use the `Attaches to` column for
    a resolution note rather than a reference list, and a resolved gap owes no
    live fact.
    """
    if text is None:
        text = Path(PROCEDURE).read_text(encoding="utf-8")
    i = text.find("## Appendix G")
    if i < 0:
        raise RuntimeError(
            "Appendix G is missing from REFACTORING_PROCEDURE.md. It is the "
            "gap register since step 6.37; reporting success without it is the "
            "failure mode §55.2 exists to name.")
    _, sids = _register_facts(text)
    sub, bad = "", []
    for ln in text[i:].splitlines():
        h = re.match(r"^### (66\.\d+)", ln)
        if h:
            sub = h.group(1)
        m = _GAP_OPEN.match(ln)
        if not m or m.group("struck") or sub == "66.6":
            continue
        cells = ln.split("|")
        if len(cells) < 4:
            continue
        # **From the RIGHT.** Two rows carry a `|` inside their gap text, so a
        # left-indexed parse reads the wrong cell for G-59 and G-64.
        for tok in re.split(r"[,·]", cells[-3]):
            tok = tok.strip().strip("`").strip()
            if _SID.fullmatch(tok) and tok not in sids:
                bad.append(f"{m.group('gap')} -> {tok}")
    return "; ".join(sorted(set(bad)))


#: The 11 sections that carry neither a register row nor a `NOT-MARKABLE`
#: note and whose classification is a FOUNDER judgement, not a rule. Declared
#: with their reason for being open, never baselined, and ratcheted at 11 so
#: the list can only shrink.
#:
#: **Each is a top-level section or a close relative of one**, which is why no
#: category rule reached them: §1 and §4 are orientation, §19 and §39 are
#: parents whose children carry the facts, §50, §58, §63 and §69 are section
#: heads whose sub-sections own the rows, §19.9 and §66 are deliberate
#: absences, and §69.1 states conventions binding on twenty entries.
PENDING_CLASSIFICATION = {
    "§1", "§4", "§19", "§19.9", "§39", "§50",
    "§58", "§63", "§66", "§69", "§69.1",
}

_HEADING = re.compile(r"^#{2,4}\s+(\d+(?:\.\d+)*)\.?\s+(.*)$")
_NOT_MARKABLE = "> **NOT-MARKABLE:"


def _sections_and_declarations(arch_text: str) -> tuple:
    """`(ordered sections, those declaring themselves NOT-MARKABLE)`."""
    order, declared, cur = [], set(), None
    for line in arch_text.splitlines():
        h = _HEADING.match(line)
        if h:
            cur = "§" + h.group(1)
            order.append(cur)
        if line.startswith(_NOT_MARKABLE) and cur:
            declared.add(cur)
    return list(dict.fromkeys(order)), declared


def _ancestors(section: str) -> list:
    parts = section[1:].split(".")
    return ["§" + ".".join(parts[:k]) for k in range(len(parts) - 1, 0, -1)]


def every_section_declares_itself(text: str | None = None,
                                  arch_text: str | None = None) -> str:
    """ASSERTION 7 — every numbered section owns a row or declares it cannot.

    **§66's header always claimed this correspondence "is checkable" and in
    this direction it was not**, because the population it ranges over was
    never defined: nothing distinguished the 198 sections carrying no
    annotation from the 17 that carried one, since the 17 were simply the ones
    somebody had annotated.

    A section is accounted for when any of these holds:

      * it owns a register row, keyed on its §;
      * it declares `> **NOT-MARKABLE:` with a reason;
      * **an ANCESTOR owns a row** — §16's own convention, *"One marker per
        item, never one per section that mentions it"*, so a sub-section of a
        marked item is marked at its canonical home;
      * it is in `PENDING_CLASSIFICATION`, which is 11 founder judgements.

    **The ancestor clause is what makes this a check rather than a backlog.**
    Without it the population is 112 and the check reports 112 violations on
    its first run, which is the failure `section_title_sources` records
    happening twice to the typed-title probe.
    """
    if text is None:
        text = Path(PROCEDURE).read_text(encoding="utf-8")
    if arch_text is None:
        arch_text = Path(ARCH).read_text(encoding="utf-8")
    rows, _ = _register_facts(text)
    order, declared = _sections_and_declarations(arch_text)
    if not order:
        raise RuntimeError(
            "no numbered sections parsed from ARCHITECTURE.md — the heading "
            "shape changed and this check would otherwise report success "
            "over an empty population, which is the failure §55.2 names.")
    undeclared = [
        s for s in order
        if s not in rows
        and s not in declared
        and s not in PENDING_CLASSIFICATION
        and not any(a in rows for a in _ancestors(s))
    ]
    return ", ".join(undeclared)


def sections_awaiting_a_ruling(text: str | None = None,
                               arch_text: str | None = None) -> str:
    """How many sections are parked in `PENDING_CLASSIFICATION` and still real.

    Pinned so the list can only shrink. **A section that gains a row or a
    declaration must leave the set**, or the exemption outlives its reason —
    which is the shape §55.2 keeps finding.
    """
    if text is None:
        text = Path(PROCEDURE).read_text(encoding="utf-8")
    if arch_text is None:
        arch_text = Path(ARCH).read_text(encoding="utf-8")
    rows, _ = _register_facts(text)
    _, declared = _sections_and_declarations(arch_text)
    still_open = [s for s in PENDING_CLASSIFICATION
                  if s not in rows and s not in declared]
    return str(len(still_open))


def _unanchored(text: str | None = None) -> list:
    """Register rows carrying `—` where a symbol anchor belongs."""
    return [r for r in read_matrix(text)
            if r["evidence"].strip().strip("`") == NOT_SET]


def facts_anchorable_not_anchored(text: str | None = None) -> str:
    """G-87: the half of the old bound that is a BACKLOG.

    A fact whose State is ✅ or ⚠️ asserts that something exists in the tree.
    **Something that exists can be pointed at**, so every row here is work
    nobody has done — not a limitation of the register.

    **This is the number 6.41 exists to bring down**, and it is the only one of
    the three whose rise is unambiguously bad: a new built fact arriving
    without an anchor is exactly the drift `matrix_anchors` cannot see, because
    it evaluates anchors that exist and says nothing about a row that has none.
    """
    return str(sum(1 for r in _unanchored(text)
                   if r["state"].strip() in ("✅", "⚠️")))


def facts_with_nothing_to_anchor(text: str | None = None) -> str:
    """G-87: the half that is a SPECIFICATION, not a backlog.

    A fact whose State is ☐ asserts that something does NOT exist. There is
    nothing in the tree to point at, so the em dash is the honest cell and
    anchoring it would mean inventing a symbol.

    **A rise here is normal and means the spec grew.** Conflating it with the
    backlog above is what made the single number unreadable — the register
    could gain ratified-but-unbuilt design and look like it was rotting.

    The `absent:` form is the exception and is preferred where the claim is
    that something is GONE rather than not yet arrived: §10 says the class is
    gone, so `absent: backend.storage.blob::ImproveBlobClient` proves it.
    """
    return str(sum(1 for r in _unanchored(text)
                   if r["state"].strip() == "☐"))


def facts_unassessed(text: str | None = None) -> str:
    """G-87: the half that is neither, and was hiding inside the other two.

    A fact whose State is itself `—` has never been assessed against the tree.
    **96 spec entries arrived this way at 6.39** and were counted as unanchored
    alongside built facts, which is how 70 became 166 in one step and read as a
    collapse rather than as a population change.

    Whether these are anchorable is unknown by definition — that is what
    unassessed means — so they belong in neither of the other two.
    """
    return str(sum(1 for r in _unanchored(text)
                   if r["state"].strip() in ("", NOT_SET)))


def matrix_covers_appendix_d(text: str | None = None) -> str:
    """EVERY STEP HAS AT LEAST ONE ROW, and every row's step is a real one.

    **Restated from set equality by founder ruling 2026-09-18**, because the
    row key became the FACT. Set equality was correct while the table held one
    row per step; it is wrong now that a step may own several rows and a fact
    may own none. What survives is the part that catches a drop: a step with no
    row is invisible, and a row naming a step that does not exist is a typo
    that would otherwise schedule nothing.

    The original reasoning, still binding on the direction it covers:

    **The ruling said "GROUP BY Step must return exactly 69. Assert it."** A
    literal 69 would have failed on the very commit that introduced it: step
    6.31 adds its own Appendix D row and makes the total 70.

    **Set equality is stronger than the count anyway** — a count of 69 passes
    when one step is dropped and another added, which is precisely the edit a
    renumber makes. It is also this document's own rule, twice stated: *"the
    total is the row count"*, and *"edit the band here, not in the generator"*.
    """
    want = appendix_d_steps(text)
    got = set()
    for r in read_matrix(text):
        got.update(_STEP_IN_CELL.findall(r["step"]))
    if want == got:
        return f"{len(want)} steps, both directions"
    missing = sorted(want - got, key=_ver)
    extra = sorted(got - want, key=_ver)
    parts = []
    if missing:
        parts.append(f"in Appendix D, NOT in the matrix: {', '.join(missing)}")
    if extra:
        parts.append(f"in the matrix, NOT in Appendix D: {', '.join(extra)}")
    return " · ".join(parts)


def matrix_anchors() -> str:
    """Every Evidence cell, evaluated against the tree.

    Returns the empty string when every row is `PASS`, `EXTERNAL` or
    `DEPENDENCY` — the expected value in CHECKS is `""`, so the check reads the
    same way as `step titles` and `unpaired state fields` already do.

    **`DEPENDENCY` is reported and does not fail**, because a library that
    moved under us is not a stale marker and has a different owner. It is
    printed on its own line so it cannot be mistaken for a pass.
    """
    rows = read_matrix()
    findings, deps = [], []
    for r in rows:
        cell = r["evidence"].strip().strip("`")
        # `—` is a fact with NO symbol anchor yet. It asserts nothing, so it
        # cannot be evaluated - but it is not silently tolerated either:
        # `facts_without_a_symbol` pins the count, so the backlog can shrink and
        # cannot grow. **A blank cell stays MALFORMED**, because "nobody filled
        # this in" and "this is knowingly unanchored" are different claims.
        if cell == NOT_SET:
            continue
        verdict, detail = evaluate_anchor(cell, ROOT)
        if verdict in _NOT_A_MARKER_FAILURE:
            continue
        if verdict == "DEPENDENCY":
            deps.append(f"{r['step'].strip()} {detail}")
            continue
        findings.append(f"{r['step'].strip()} [{verdict}] {detail}")
    out = "; ".join(findings)
    if deps:
        out += ("  —— DEPENDENCY (different owner, not a marker "
                "failure): " + "; ".join(deps))
    return out


CHECKS = [
    ("API routes in routes.py", "11",
     lambda: count_lines("agent-improve/backend/gateway/routes.py",
                         r"^@router\.(get|post|delete|put)"),
     "§49 — 11 of 12"),

    ("phase subgraph nodes", "5",
     lambda: count_lines("agent-improve/backend/phases/subgraph_common.py",
                         r"builder\.add_node"),
     "§13 — 5 nodes"),

    ("middleware mounted", "8",
     lambda: count_lines("agent-improve/backend/phases/nodes_common.py",
                         r"Middleware\(|^ {12}coherence,"),
     "§19 — eight positions"),

    ("universal tools BUILT", "6",
     lambda: py("from backend.knowledge.tools import UNIVERSAL_TOOLS as U; print(len(U))"),
     "§29.2 — 6 of the ratified 8; check_gate_status (7.1) and "
     "request_human_approval (7.5) are unbuilt"),

    ("distinct computation tools", "20",
     lambda: py("from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE as C; "
                "print(len({t.name for p in C for t in C[p]}))"),
     "§30 — the twenty"),

    ("per-phase computation split", "1/8/5/1/5",
     lambda: py("from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE as C\n"
                "from backend.phases.mappers_common import PHASE_ORDER as P\n"
                'print("/".join(str(len(C[p])) for p in P))'),
     "§30 — the per-phase partition"),

    ("SKILL.md files that exist", "5",
     lambda: count_glob("agent-improve/skills/*/SKILL.md"),
     "§32 — five of five"),

    ("SKILL.md carrying METRIC LITERACY (proxy)", "5",
     lambda: count_glob_containing("agent-improve/skills/*/SKILL.md",
                                   "METRIC LITERACY"),
     "§32 — the one item Define lacked until 6.9. A PROXY, not a proof"),

    ("upload formats with a real parser", "['document', 'pdf', 'spreadsheet', 'text']",
     lambda: py("from backend.upload.parsers import PARSERS; print(sorted(PARSERS))"),
     "§29.1 — membership in PARSERS is what 'supported' now means"),

    ("@traceable in the backend", "0",
     lambda: count_tree_containing("agent-improve/backend", "@traceable",
                                  "/tests"),
     "§51 — zero, and that is the ☐ marker"),

    # ── Added 2026-09-11 by the three-way alignment audit. ────────────────
    # Ten checks for markers that had none. The audit found FOUR markers
    # stale or self-contradictory in a document whose eleven checks all
    # passed — so the eleven were not wrong, they were not enough. What
    # they had in common: every one counted a POPULATION (routes, tools,
    # files) and none pinned a VALUE or a SET. A count cannot see a route
    # renamed, a constant retuned, or a field dropped.

    # §49. The SET, not the count. The marker this backs contradicted
    # itself — "names 8 of the 11 — six … in no ratified table", 8 + 6 = 14
    # — and a count of 11 agreed with the tree throughout.
    ("API route set (§49)",
     "DELETE /files/{case_id}/{file_id} | GET /cases/{case_id} | "
     "GET /gate/review/{case_id}/{phase} | GET /health | GET /registry | "
     "POST /ask | POST /cases | POST /context | POST /gate | "
     "POST /summarise | POST /upload",
     lambda: route_set(),
     "§49 — 4 named by the table, 7 in no ratified table (G-47)"),

    # S-C05. **All eight, since step 6.19 closed G-50** (2026-09-14). This
    # expectation read four until that step, with the gap named on the marker
    # — §29.2's pattern — because a check expecting eight would have failed
    # every run and taught the reader to skip it. The step's own comment here
    # said to update it in the same commit, and this is that update.
    ("CoachingResponse fields (S-C05)",
     "citations, contradiction_flag, example, explanation, fields_captured, "
     "message, progress, prompt",
     lambda: py("from backend.core.substate import CoachingResponse as C; "
                "print(', '.join(sorted(C.model_fields)))"),
     "S-C05 — all 8 ratified fields, since step 6.19 closed G-50"),

    ("state field counts (S-C01 / S-C02)", "7 / 22",
     lambda: py("from backend.core.state import SupervisorState as S; "
                "from backend.core.substate import PhaseState as P; "
                "print(f'{len(S.__annotations__)} / {len(P.__annotations__)}')"),
     "S-C01 — seven · S-C02 — twenty-two. Step 3.1's Done-when said "
     "7 and 19; four ratified amendments have moved it since"),

    ("storage models (S-C09)", "11",
     lambda: py("import backend.storage.models as M; "
                "from pydantic import BaseModel; "
                "print(sum(1 for n in dir(M) if isinstance(getattr(M, n), type) "
                "and issubclass(getattr(M, n), BaseModel) and getattr(M, n) "
                "is not BaseModel))"),
     "S-C09 — eleven defined, six named by the entry (G-51)"),

    # §19.3 / §19.4 / §19.5 / §26 / §44 — the tuned values. Five markers
    # state these numbers and nothing re-read them.
    ("summarization trigger / keep (§19.3)",
     "('tokens', 100000) / ('messages', 20)",
     lambda: py("import backend.phases.nodes_common as N; "
                "print(f'{N.SUMMARIZATION_TRIGGER} / {N.SUMMARIZATION_KEEP}')"),
     "§19.3 — trigger 100k, keep 20"),

    ("retry caps (§19.4 / §19.5)", "2 / continue",
     lambda: py("import backend.phases.nodes_common as N; "
                "print(f'{N.RETRY_MAX} / {N.TOOL_RETRY_ON_FAILURE}')"),
     "§19.4 — max_retries=2 · §19.5 — on_failure='continue'"),

    ("hop caps (§26 / S-F09 B1)", "3 / 2 / 50",
     lambda: py("import backend.phases.nodes_common as N; "
                "from backend.core.graph import RECURSION_LIMIT; "
                "print(f'{N.COACH_HOP_BUDGET} / {N.REMAINING_STEPS_FLOOR} / "
                "{RECURSION_LIMIT}')"),
     "§26 — the caps ARE built (6.7): budget 5, floor 2, backstop 50. "
     "It is `analyse_executor_node` that is not"),

    ("executor run timeout (§44)", "45",
     lambda: py("from backend.phases.subgraph_common import "
                "EXECUTOR_RUN_TIMEOUT as T; print(T)"),
     "§44 — Step 0 only; TimeoutPolicy(run_timeout=45)"),

    # §33. The ☐ marker's own load-bearing fact. This flips the day 7.3
    # lands, which is the point — four other markers name the interrupt's
    # absence as their reason (WATCH 13, 18, 23).
    # ZERO, and the journey of this number in one day is the whole argument
    # for the check. It went 0 (assumed) -> 1 (measured: §19.6's contradiction
    # interrupt, which disproved §33's "nothing pauses for a human") -> 0
    # again (founder ruling: position 6 GUARDED until 7.3, because a fired
    # interrupt parks the CASE permanently with no route able to resume it).
    #
    # **The two zeros mean opposite things.** The first was nobody having
    # looked. This one is a deliberate, tested, reversible suspension with a
    # commented restore line. STEP 7.3 TAKES THIS TO 2 - `gate_review`'s
    # interrupt plus position 6's, restored in the same commit.
    ("interrupt() call sites (§33)", "0",
     lambda: count_call_sites("agent-improve/backend", "interrupt"),
     "§33 — position 6 GUARDED until 7.3 (founder ruling 2026-09-11); "
     "`gate_review` still pass-through. Both land at 7.3"),

    # §30. The figure NONE of the four captions was measuring.
    ("LIVE per-phase tool bind (§30)", "7/14/11/7/11",
     lambda: py("from backend.phases.nodes_common import _executor_tools as E, "
                "COACH_HOP_BUDGET as B; "
                "from backend.phases.mappers_common import PHASE_ORDER as P; "
                "print('/'.join(str(len(E(p, B, None))) for p in P))"),
     "§30 — ratified 9/16/13/9/13; two universal tools unbuilt (7.1, 7.5). "
     "Four captions carried four different figures for this on 2026-09-11"),

    # F-15, checked at last. Every name here is accounted for by a step or is
    # registered as unowned; the VALUE of the check is that a NEW name cannot
    # join the list quietly, which is how all seven previous instances began.
    ("state fields with no writer (W) or no reader (R)",
     "acknowledged_gaps:WR belt_edits:R computation_results:W field_index:R "
     "final_output:R hop_results:R phase_metrics:W rejection_feedback:R "
     "synthesis_output:R",
     unpaired_state_fields,
     "F-15 · §6 / §7 — computation_results and phase_metrics are step 6.20; "
     "field_index 6.20; hop_results / synthesis_output 6.10; belt_edits, "
     "rejection_feedback and acknowledged_gaps need the gate (7.3, 7.4); "
     "**final_output has NO OWNING STEP**. Exemptions are declared in "
     "PAIRING_EXEMPT with reasons"),

    # The board renders NAMES. These two keep the names honest: the first that
    # the two sources agree with each other, the second that the generator
    # reads them rather than carrying its own copy.
    ("step titles — Appendix D row vs its own section heading", "",
     step_title_mismatches,
     "Appendix D · a row may DROP words (it is a short form) and may not "
     "INVENT them, and a heading may not carry a status token — that is "
     "Appendix D's Status cell's job. Seven steps failed on 2026-09-11"),

    ("section names TYPED into build_board.py", "0",
     section_title_sources,
     "§55.2 — every rendered name is read from a heading or from Appendix D. "
     "A literal in the generator is a third copy, and the only one an editor "
     "cannot correct by editing a document"),

    # ── Step 6.31: the matrix is the leading document, and these two are what
    #    make that true rather than asserted. ───────────────────────────────
    # ── Step 6.40: assertion 7 — the section-to-row direction. ──────
    ("every section owns a row or declares it cannot", "",
     every_section_declares_itself,
     "§66 · step 6.40 — assertion 7. A section is accounted for by a row, a "
     "NOT-MARKABLE note, an ANCESTOR owning a row (§16's one-marker-per-item "
     "convention), or membership of the 11 founder judgements"),

    ("sections awaiting a founder ruling", "11",
     sections_awaiting_a_ruling,
     "§66 · step 6.40 — pinned so the list can only shrink. A section that "
     "gains a row or a declaration must LEAVE the set, or the exemption "
     "outlives its reason"),

    # ── Step 6.39: assertion 5, the S-id half. ───────────────────────────
    ("every S-id an open gap names has a fact row", "",
     gap_refs_resolve,
     "Appendix G · step 6.39 — assertion 5. The § half turns on at 6.40, when "
     "every section declares a row or declares itself NOT-MARKABLE; 19 "
     "sections an open gap names have neither today, and inventing rows for "
     "them would pre-empt that judgement"),

    # ── Step 6.41: G-87 — one bound became three, each meaning something
    #    different. The old single number could not tell a backlog from a
    #    specification, so every rise looked the same and none could fall.
    ("facts built but not anchored — the BACKLOG", "50",
     facts_anchorable_not_anchored,
     "Appendix F · step 6.41 — G-87. ✅ or ⚠️ means something EXISTS in the "
     "tree, and what exists can be pointed at, so every row here is work "
     "nobody has done. **A rise is unambiguously bad** and needs a reason in "
     "the commit body; `matrix_anchors` cannot see it, because it evaluates "
     "anchors that exist and says nothing about a row that has none"),

    ("facts with nothing to anchor to — ratified, unbuilt", "16",
     facts_with_nothing_to_anchor,
     "Appendix F · step 6.41 — G-87. ☐ means something does NOT exist, so the "
     "em dash is the honest cell. **A rise here is normal** and means the "
     "spec grew; conflating it with the backlog is what made one number "
     "unreadable"),

    ("facts never assessed against the tree", "96",
     facts_unassessed,
     "Appendix F · step 6.41 — G-87. State is itself an em dash. The 96 spec "
     "entries arrived this way at 6.39 and were counted beside built facts, which is how 70 became 166 in one step and read as a collapse"),


    ("Appendix F covers Appendix D — set equality, both directions",
     f"{len(appendix_d_steps())} steps, both directions",
     matrix_covers_appendix_d,
     "Appendix F · step 6.31 — one row per step. NOT a count: a count passes "
     "when one step is dropped and another added. The expectation is DERIVED "
     "from Appendix D, so adding a step cannot make this stale"),

    ("Appendix F anchors — every Evidence cell against the tree", "",
     matrix_anchors,
     "Appendix F · step 6.31 — PASS or EXTERNAL passes; DEPENDENCY is "
     "reported with a different owner; FAIL means the matrix and the tree "
     "disagree and MALFORMED means the cell is not an anchor. An `absent:` "
     "cell that starts resolving is the step that built the thing failing to "
     "remove its own cell"),
]


def check_phase_scripts() -> tuple[str, str]:
    """Each phase's SKILL.md must contain its coaching script byte-for-byte.

    **FILE TO FILE since 2026-09-13 (brief step 8).** The script used to live in
    ARCHITECTURE.md §39.x.7/.10, so this check had to find a heading inside a
    965 KB document, locate the `**[OPENING` marker within it, and slice —
    three steps that could each break on an edit touching neither artifact.
    Both sides are now files in the same directory, so the check is a
    containment test a person can reproduce with `diff`.

    **Containment rather than equality, deliberately.** SKILL.md wraps the
    script in §32's frontmatter and structure and the middleware loads it
    whole; the script file is the atomic unit §56.1 names. Equality would
    force SKILL.md to be nothing but the script.
    """
    n = 0
    for ph in ("define", "measure", "analyse", "improve", "control"):
        d = Path(PROJECT) / "skills" / f"dmaic-{ph}-phase"
        try:
            script = (d / "coaching_script.md").read_text(
                encoding="utf-8").rstrip("\n")
            skill = (d / "SKILL.md").read_text(encoding="utf-8")
        except OSError:
            continue
        n += 1 if script and script in skill else 0
    return "5", str(n)

def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    rows, bad = [], 0

    for label, expected, probe, backs in CHECKS:
        try:
            got = probe()
        except Exception as exc:                    # noqa: BLE001
            got = f"PROBE FAILED: {exc!r}"
        ok = got == expected
        bad += 0 if ok else 1
        rows.append((ok, label, expected, got, backs))

    exp, got = check_phase_scripts()
    ok = got == exp
    bad += 0 if ok else 1
    rows.append((ok, "phase scripts byte-matching their SKILL.md", exp, got,
                 "§56.1 — the atomic unit"))

    if not quiet:
        w = max(len(r[1]) for r in rows)
        print(f"{'':2} {'check'.ljust(w)}  {'expected':<12} {'tree'}")
        print("-" * (w + 34))
        for ok, label, expected, got, backs in rows:
            print(f"{'ok' if ok else '!!':2} {label.ljust(w)}  "
                  f"{expected:<12} {got}")
            if not ok:
                print(f"{'':2} {''.ljust(w)}  -> backs: {backs}")
        print()
        if bad:
            print(f"{bad} marker(s) DISAGREE with the tree. "
                  "Either the tree moved and the BUILT line in ARCHITECTURE.md "
                  "is now a claim, or this check is stale — resolve which, "
                  "never just re-baseline.")
        else:
            print(f"{len(rows)} checks, zero disagreements.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
