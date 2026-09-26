#!/usr/bin/env python3
"""Pre-flight — seconds, before every commit attempt. Step 6.66 (founder ruling 2026-09-25).

The commit hook runs the full suite ONCE (CLAUDE.md §22 a) and the guard runs
mypy over the staged files. What refuses a commit is usually a KNOCK-ON effect
neither was pointed at: 6.61's first attempt was refused for a stale count in a
document, an old test that still asserted the old behaviour, and eleven type
errors in files the change reached through an import. This finds those first,
in seconds, by checking what the change REACHES — not only what it touches:

  drift   drift-check.py — every owned fact the documents restate, against its owner
  (built   verify_built.py retired with the procedure at 6.67)
  types   mypy over the changed Python AND its direct importers, judged against
          rule 3's baseline (the guard's own ratchet — importers' old debt passes)
  tests   the tests of the changed modules and of their importers, plus every
          test that names a changed non-Python file (a document, a hook)

All three run at once. Area runs are serial below SERIAL_MAX test files: the
6.65 timing log shows xdist start-up costs ~20 s (34-54 tests: 22-30 s under
`-n auto`, 1-47 tests: 4-12 s serial).

Usage (repo root):
    python .claude/hooks/preflight.py          # changed = staged + unstaged + untracked, vs HEAD
    python .claude/hooks/preflight.py --plan   # print what would run, run nothing

Exit 0 clear, 1 a check failed. It is an accelerator, not a gate: the commit
hook still runs the full suite and every guard rule.
"""
from __future__ import annotations

import ast
import concurrent.futures as cf
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
ROOT = HOOKS.parents[1]
PROJECT = ROOT / "agent-improve"
TESTS = PROJECT / "backend" / "tests"
#: Import-graph roots, relative to PROJECT — where a changed module's importers live.
GRAPH_DIRS = ("backend", "tools", "scripts")
#: At or below this many test files the area run is serial (no xdist start-up).
SERIAL_MAX = 12
#: Changing one of these changes every test's fixture — run the whole suite.
EVERYTHING = {"agent-improve/backend/tests/conftest.py"}
#: Test files that read a LIVE case over the network (~21 s per setup): the
#: commit hook's full run still runs them every commit; the pre-flight picks
#: them only when the file itself changed.
LIVE_READ = {"agent-improve/backend/tests/test_capability_rows.py"}

sys.path.insert(0, str(HOOKS))


def _venv() -> str:
    for rel in ("Scripts/python.exe", "bin/python"):
        p = PROJECT / ".venv" / rel
        if p.is_file():
            return str(p)
    raise SystemExit("preflight: the pinned venv agent-improve/.venv is missing")


def _git(*args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                         encoding="utf-8", errors="replace", timeout=30).stdout
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def changed_files() -> list[str]:
    """Staged, unstaged and untracked paths that exist — what the next commit could carry."""
    paths = set(_git("diff", "--name-only", "--diff-filter=ACMR", "HEAD"))
    paths |= set(_git("ls-files", "--others", "--exclude-standard"))
    return sorted(p for p in paths if (ROOT / p).is_file())


# ── the import graph ────────────────────────────────────────────────────────
def module_name(rel: str) -> str | None:
    """'agent-improve/backend/phases/moves.py' -> 'backend.phases.moves'."""
    if not rel.startswith("agent-improve/") or not rel.endswith(".py"):
        return None
    parts = rel[len("agent-improve/"):-3].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else None


def _imports(path: Path, mod: str) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    pkg = mod if path.name == "__init__.py" else mod.rpartition(".")[0]
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                anchor = pkg.split(".")
                anchor = anchor[: len(anchor) - (node.level - 1)] if node.level > 1 else anchor
                base = ".".join([*anchor, base] if base else anchor)
            out.add(base)
            out.update(f"{base}.{a.name}" for a in node.names)
    return out


def import_graph() -> dict[str, set[str]]:
    """module -> the project modules it imports (directly)."""
    files: dict[str, Path] = {}
    for d in GRAPH_DIRS:
        for p in (PROJECT / d).rglob("*.py"):
            if ".venv" in p.parts or "__pycache__" in p.parts:
                continue
            m = module_name(p.relative_to(ROOT).as_posix())
            if m:
                files[m] = p
    known = set(files)
    return {m: {i for i in _imports(p, m) if i in known} for m, p in files.items()}


def _token(rel: str) -> str:
    """How a test names a file: a module by its stem (tests load hooks by
    `"verify_built"` as often as by `"verify_built.py"`), anything else by name."""
    p = Path(rel)
    return p.stem if p.suffix == ".py" else p.name


def _readers() -> list[Path]:
    """The hooks and tools that parse documents — one level of indirection."""
    return sorted([*HOOKS.glob("*.py"), *(PROJECT / "tools").rglob("*.py")])


def plan(changed: list[str], graph: dict[str, set[str]] | None = None) -> dict:
    """What the change reaches: modules to type-check, test files to run."""
    graph = import_graph() if graph is None else graph
    mods = {m for m in (module_name(c) for c in changed) if m and m in graph}
    # Graph modules are reached through imports; everything else by name.
    named = {_token(c) for c in changed if module_name(c) not in graph}
    # 6.67 (the addendum's speed item 2): changed files and their importers
    # ONLY — the importers are type-checked; the tests run are those of the
    # changed modules themselves. The one-level "a hook reads this document"
    # reach retired with verify_built.py; the hook's full run covers the rest.
    importers = {m for m, deps in graph.items() if deps & mods}
    scope = mods | importers
    tests: set[str] = set()
    everything = any(c in EVERYTHING for c in changed)
    for p in sorted(TESTS.glob("test_*.py")):
        rel = p.relative_to(ROOT).as_posix()
        if rel in LIVE_READ and rel not in changed:
            continue
        m = module_name(rel)
        if rel in changed or (m and graph.get(m, set()) & mods):
            tests.add(rel)
            continue
        if named:
            text = p.read_text(encoding="utf-8", errors="replace")
            if any(n in text for n in named):
                tests.add(rel)
    type_files = sorted(
        c for c in changed if c.endswith(".py") and c.startswith("agent-improve/")
        and not c.startswith("agent-improve/docs/")      # archived code is not live (6.67)
    )
    type_files += sorted(
        {f"agent-improve/{m.replace('.', '/')}.py" for m in importers} - set(type_files)
    )
    type_files = [f for f in type_files if (ROOT / f).is_file()]
    return {"changed": changed, "modules": sorted(mods), "importers": sorted(importers),
            "types": type_files, "tests": "ALL" if everything else sorted(tests)}


# ── the four checks ─────────────────────────────────────────────────────────
def _run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    env.pop("AGENT_IMPROVE_FULL_RUN", None)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding="utf-8",
                       errors="replace", timeout=900, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def check_drift(py: str, _p: dict) -> tuple[bool, str]:
    code, out = _run([py, str(HOOKS / "drift-check.py")], ROOT)
    return code == 0, out.strip().splitlines()[-1] if code == 0 and out.strip() else out.strip()


def _guard():
    spec = importlib.util.spec_from_file_location("guard", HOOKS / "commit-msg-refactor-guard.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_types(py: str, p: dict) -> tuple[bool, str]:
    files = p["types"]
    if not files:
        return True, "no Python reached"
    g = _guard()
    found = g.run_mypy(str(ROOT), py, files)
    base = g.load_baseline(str(ROOT))
    new = [f"{k.replace(chr(9), '  ')} (x{n - base.get(k, 0)})"
           for k, n in sorted(found.items()) if n > base.get(k, 0)]
    if new:
        return False, "NEW type errors (not in rule 3's baseline):\n  " + "\n  ".join(new[:25])
    return True, f"{len(files)} file(s) ({len(p['importers'])} importer(s)), no new errors"


def slow_tests() -> list[str]:
    """Tests the last runs measured at >= 1 s (`.claude/logs/slow-tests.json`,
    written by the test recorder). The pre-flight leaves them to the commit
    hook's full run, which never skips anything (6.67, speed item 2)."""
    import json
    path = ROOT / ".claude" / "logs" / "slow-tests.json"
    try:
        return sorted(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return []


def check_tests(py: str, p: dict) -> tuple[bool, str]:
    tests = p["tests"]
    if tests == "ALL":
        args, n = ["backend/tests", "-n", "auto"], "the whole suite"
    elif not tests:
        return True, "no test reached"
    else:
        rel = [t[len("agent-improve/"):] for t in tests]
        args = rel + (["-n", "auto"] if len(rel) > SERIAL_MAX else ["-n", "0"])
        skip = [s for s in slow_tests() if s.split("::")[0] in rel and s not in rel]
        args += [a for s in skip for a in ("--deselect", s)]
        n = f"{len(rel)} test file(s), {len(skip)} slow test(s) left to the hook"
    code, out = _run([py, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", *args], PROJECT)
    lines = out.strip().splitlines()
    summary = lines[-1] if lines else "(no output)"
    if code in (0, 5):          # 5 = nothing collected
        return True, f"{n}: {summary}"
    failed = [l for l in lines if l.startswith(("FAILED", "ERROR"))][:20]
    return False, f"{n}: {summary}\n  " + "\n  ".join(failed)


CHECKS = {"drift": check_drift, "types": check_types, "tests": check_tests}


def run(changed: list[str] | None = None, echo=print) -> int:
    t0 = time.time()
    changed = changed_files() if changed is None else changed
    p = plan(changed)
    py = _venv()
    echo(f"[preflight] {len(changed)} changed file(s) -> {len(p['types'])} to type-check, "
         f"{'ALL' if p['tests'] == 'ALL' else len(p['tests'])} test file(s)")
    results: dict[str, tuple[bool, str, float]] = {}

    def timed(name):
        s = time.time()
        try:
            ok, msg = CHECKS[name](py, p)
        except SystemExit as exc:           # the guard's fail() exits
            ok, msg = False, f"{exc}"
        except Exception as exc:            # noqa: BLE001 — a broken check is a failed check
            ok, msg = False, f"the check crashed: {exc!r}"
        return name, ok, msg, round(time.time() - s, 1)

    with cf.ThreadPoolExecutor(max_workers=len(CHECKS)) as ex:
        for name, ok, msg, sec in ex.map(timed, CHECKS):
            results[name] = (ok, msg, sec)
    for name, (ok, msg, sec) in results.items():
        echo(f"  {'ok' if ok else '!!'} {name:<6} {sec:>5.1f}s  {msg}")
    total = round(time.time() - t0, 1)
    bad = [n for n, r in results.items() if not r[0]]
    echo(f"[preflight] {'CLEAR' if not bad else 'FAILED: ' + ', '.join(bad)} in {total}s")
    try:
        import timing
        timing.append({"kind": "preflight", "seconds": total, "ok": not bad,
                       "checks": {n: r[2] for n, r in results.items()},
                       "changed": len(changed),
                       "test_files": "ALL" if p["tests"] == "ALL" else len(p["tests"])})
    except Exception:                       # noqa: BLE001 — timing never fails a run
        pass
    return 1 if bad else 0


if __name__ == "__main__":
    if "--plan" in sys.argv:
        import json
        print(json.dumps(plan(changed_files()), indent=1))
        sys.exit(0)
    sys.exit(run())
