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


# ── The checks. (label, expected, probe, which BUILT marker it backs) ──────
#
# `expected` is written here rather than parsed out of the prose, deliberately:
# a check that reads its own expectation from the document it is checking
# cannot fail. That is the "check that cannot fail" this project keeps naming.
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

    # S-C05. Four of the ratified eight. Expected is the BUILT state, with
    # the gap named on the marker — §29.2's pattern. A check expecting
    # eight would fail every run until 10.2 and teach the reader to skip it.
    ("CoachingResponse fields (S-C05)",
     "citations, contradiction_flag, fields_captured, message",
     lambda: py("from backend.core.substate import CoachingResponse as C; "
                "print(', '.join(sorted(C.model_fields)))"),
     "S-C05 — 4 of the ratified 8; §50.1's explanation/example/prompt/"
     "progress are unbuilt (G-50). **Step 6.19 takes this to 8** — update the "
     "expectation in the same commit, or this check passes the day it lands"),

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

    ("hop caps (§26 / S-F09 B1)", "5 / 2 / 50",
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
]


def check_phase_scripts() -> tuple[str, str]:
    """Each phase's SKILL.md must contain its §39.x.10 script byte-for-byte."""
    code = (
        "import io, re\n"
        "arch = io.open('ARCHITECTURE.md', encoding='utf-8').read()\n"
        "SEC = {'define':'39.1.7','measure':'39.2.10','analyse':'39.3.10',\n"
        "       'improve':'39.4.10','control':'39.5.10'}\n"
        "n = 0\n"
        "for ph, sec in SEC.items():\n"
        "    i = arch.index(f'#### {sec}')\n"
        "    j = arch.index(chr(10) + '#### ', i + 1)\n"
        "    m = re.search(r'\\*\\*\\[OPENING', arch[i:j])\n"
        "    script = arch[i:j][m.start():].rstrip(chr(10))\n"
        "    skill = io.open(f'skills/dmaic-{ph}-phase/SKILL.md', encoding='utf-8').read()\n"
        "    n += 1 if script in skill else 0\n"
        "print(n)\n"
    )
    return "5", py(code)


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
    rows.append((ok, "phase scripts byte-matching §39.x.10", exp, got,
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
