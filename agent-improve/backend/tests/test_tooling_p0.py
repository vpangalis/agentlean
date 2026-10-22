"""Package P0 — the commit hook and the tooling (founder ruling 2026-10-20: P0 runs before P1; requirement T97).

One test per P0 feature, each the proof of a tooling defect: G-177/G-230 (DEF-232), G-229 (DEF-233), G-231
(DEF-234), G-233 (DEF-235).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "agent-improve"
HOOKS = ROOT / ".claude" / "hooks"

#: A feature test's outcome is the measurement (as in test_define_e2e.py): failing, it reads xfail.
pytestmark = pytest.mark.xfail(strict=False, reason="a Define feature test — its outcome is the measurement")


def test_the_commit_hook_regenerates_the_generated_documents_before_it_runs_the_tests() -> None:
    """DEF-232 — G-177 / G-230: the pre-commit hook runs every generator the tests check (the data models, the code
    layout, the routes, the value keys, the middleware order) and stages their output BEFORE it runs the tests on
    the staged tree, so a commit that changes a generated source never fails its own first run."""
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    tests_at = hook.index('staged_tree.py $RUNFLAG')
    for generator in ("generate_models.py", "generate_layout generate_routes generate_value_keys "
                                            "generate_middleware_order"):
        assert generator in hook, generator
        assert hook.index(generator) < tests_at, f"{generator} runs after the tests"


def test_a_hook_whose_dependency_is_missing_refuses_with_the_reason(tmp_path) -> None:
    """DEF-233 — G-229: a Claude Code guard whose dependency (pyyaml) cannot be imported refuses the tool call —
    exit 2, the reason on stderr — instead of exiting 0 and letting every write through unchecked. Both guards.
    (One test, not parametrized: the feature names this node id, and rule 11 reads its outcome.)"""
    fake = tmp_path / "yaml"
    fake.mkdir()
    (fake / "__init__.py").write_text("raise ImportError('pyyaml is not installed (simulated)')\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(tmp_path), "PYTHONIOENCODING": "utf-8"}
    for hook in ("pre-tool-use-drift-check.py", "fact-ownership-guard.py"):
        r = subprocess.run([sys.executable, str(HOOKS / hook)], input='{"tool_name": "Write", "tool_input": {}}',
                           capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT, timeout=60)
        assert r.returncode == 2, (hook, r.returncode, r.stderr)
        assert "pyyaml" in r.stderr.lower(), (hook, r.stderr)


def test_the_test_summary_is_pytests_result_line_not_the_last_line() -> None:
    """DEF-234 — G-231: the summary the hook prints is pytest's result line, even when the interpreter's exit
    prints a logging error after it (aiohttp's unclosed connector ends in "Arguments: ()")."""
    sys.path.insert(0, str(HOOKS))
    import staged_tree
    out = ("....\n12 passed, 3 xfailed, 1 warning in 4.20s\n--- Logging error ---\nTraceback (most recent call "
           "last):\nValueError: I/O operation on closed file.\nCall stack:\nMessage: 'Unclosed connector'\nArguments: ()\n")
    assert staged_tree.result_line(out) == "12 passed, 3 xfailed, 1 warning in 4.20s"
    assert staged_tree.result_line("no result here\n") == "no result here"


def test_t67s_child_process_writes_utf8_whatever_the_shell() -> None:
    """DEF-235 — G-233: T67's test starts the app in a child process and reads its stderr as UTF-8; the child must
    write UTF-8 whatever the shell's encoding, so the test passes with PYTHONIOENCODING and PYTHONUTF8 unset."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONIOENCODING", "PYTHONUTF8")}
    t67 = "backend/tests/test_define_e2e.py::test_t67_start_up_exits_with_status_1_when_a_required_credential_is_missing"
    r = subprocess.run([sys.executable, "-m", "pytest", t67, "-q", "--no-header", "-p", "no:cacheprovider", "-n", "0",
                        "--runxfail"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**env, "AGENT_IMPROVE_NO_RECORD": "1"}, cwd=PROJECT, timeout=300)
    assert r.returncode == 0, r.stdout[-1500:]


# ── package P0b (founder ruling 2026-10-20; requirement T99) ─────────────────────────────────────────────────────


def test_the_fact_ownership_check_runs_at_the_commit_gate() -> None:
    """DEF-241 — G-59 (ruled 2026-09-14, §55.5): the ownership check moves to the commit gate, over the staged governed
    documents — the index holds the final content whatever wrote it (a Bash edit, a script, a peer). The commit guard
    exposes check_fact_ownership and its main runs it. (Contract level: P0b's build adds the refusal case.)"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("guard_p0b", HOOKS / "commit-msg-refactor-guard.py")
    assert spec and spec.loader
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    assert hasattr(guard, "check_fact_ownership"), "the commit guard has no fact-ownership check"
    assert "check_fact_ownership(" in (HOOKS / "commit-msg-refactor-guard.py").read_text(encoding="utf-8")


def test_search_index_schemas_have_a_registered_owner() -> None:
    """DEF-242 — G-60, closed by founder ruling 2026-10-20: the search-index-schema class is ruled OUT of mechanical
    ownership — the registry says so with the reason — and the generated data-models.md ties each index's fields to
    the code that owns them, which is where the facts are held."""
    import yaml
    reg = yaml.safe_load((ROOT / ".claude" / "config" / "fact_owners.yaml").read_text(encoding="utf-8"))
    out = {o.get("class"): o for o in reg.get("ruled_out") or []}
    assert "search-index-schemas" in out and "data-models.md" in out["search-index-schemas"]["reason"], out
    assert "search-index-schemas" not in {o.get("id") for o in reg.get("owners") or []}    # no guard row
    models = (PROJECT / "docs" / "data-models.md").read_text(encoding="utf-8")
    for owner in ("KNOWLEDGE_INDEX_FIELDS", "EVIDENCE_INDEX", "CASE_INDEX"):
        assert owner in models, owner


def test_the_server_log_is_quiet_and_the_favicon_is_served() -> None:
    """DEF-243 — G-228: the Azure SDK's request/response blocks are not logged at INFO, and /favicon.ico is served."""
    import logging
    from fastapi.testclient import TestClient
    from backend.app import app
    level = logging.getLogger("azure.core.pipeline.policies.http_logging_policy").getEffectiveLevel()
    assert level > logging.INFO, logging.getLevelName(level)
    assert TestClient(app).get("/favicon.ico").status_code == 200


def test_the_hooks_run_with_the_projects_python() -> None:
    """DEF-244 — the rest of G-229: every Python hook in .claude/settings.json runs with agent-improve/.venv's Python,
    the interpreter the project's requirements are installed in, not whatever "python" is on PATH."""
    import json
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"] for groups in (settings.get("hooks") or {}).values() for g in groups
                for h in g.get("hooks") or [] if ".py" in h.get("command", "")]
    assert commands, "no Python hook found"
    assert all(".venv" in c for c in commands), [c for c in commands if ".venv" not in c]


def test_the_session_start_reports_a_guard_that_cannot_run(tmp_path) -> None:
    """DEF-245 — the rest of G-229: with pyyaml unimportable, the session-start hook says a guard cannot run."""
    fake = tmp_path / "yaml"
    fake.mkdir()
    (fake / "__init__.py").write_text("raise ImportError('pyyaml is not installed (simulated)')\n", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(tmp_path), "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, str(HOOKS / "session-start-context.py")], input="{}", capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=env, cwd=ROOT, timeout=300)
    assert "cannot run" in (r.stdout + r.stderr).lower(), (r.stdout + r.stderr)[-1500:]


def test_the_tests_close_every_client_they_open() -> None:
    """DEF-246 — the rest of G-231: a serial run of the gate and state areas leaves no unclosed aiohttp client —
    no "Unclosed connector" at interpreter exit (the logging error that once replaced the hook's summary)."""
    r = subprocess.run([sys.executable, "-m", "pytest", "backend/tests/test_gate_acceptance.py",
                        "backend/tests/test_state.py", "-q", "--no-header", "-p", "no:cacheprovider", "-n", "0"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env={**os.environ, "AGENT_IMPROVE_NO_RECORD": "1"}, cwd=PROJECT, timeout=600)
    assert "Unclosed connector" not in r.stdout + r.stderr


# ── P0b, hook time (founder ruling 2026-10-20, item 2) ───────────────────────────────────────────────────────────


def _hook_module(file: str, name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, HOOKS / file)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(HOOKS))
    spec.loader.exec_module(mod)
    return mod


def test_the_full_suite_runs_once_per_package_before_its_push() -> None:
    """DEF-247 — (a): a push whose tip has no passing full run gets one — the pre-push hook runs the full suite on
    that source itself instead of refusing — so the full suite runs once per package, before its push, and the other
    commits take the fast run. A failing run still refuses the push. CLAUDE.md says push once per package."""
    pre_push = _hook_module("pre_push.py", "pre_push_p0b")
    sha = "a" * 40
    updates = [("refs/heads/main", sha, "refs/heads/main", "b" * 40)]
    ran: list[str] = []

    def passes(s: str) -> int:
        ran.append(s)
        return 0

    def fails(s: str) -> int:
        ran.append(s)
        return 1
    assert pre_push.ensure_full_runs(updates, lambda s: "SRC1", set(), passes) == []
    assert ran == [sha], ran                                               # run once, on the pushed tip
    ran.clear()
    left = pre_push.ensure_full_runs(updates, lambda s: "SRC1", set(), fails)
    assert left and "SRC1" in left[0], left                                # a failing run still refuses
    assert pre_push.ensure_full_runs(updates, lambda s: "SRC1", {"SRC1"}, lambda s: 1 / 0) == []   # already passed
    assert "Push once per package" in (PROJECT / "CLAUDE.md").read_text(encoding="utf-8")
    # The first live push (2026-10-20) failed: git's tree id came with its newline into source_id. A real tree id,
    # newline and all, is read as the same source.
    tree = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True, text=True, cwd=ROOT,
                          env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")}).stdout
    assert tree.endswith("\n") and pre_push.source_id(tree) == pre_push.source_id(tree.strip())


def test_a_passing_full_run_is_reused_when_the_source_is_unchanged(tmp_path, monkeypatch) -> None:
    """DEF-248 — (b): run_suite reuses the ledger's passing full run when the staged source is the same (a commit
    retried for its message alone), instead of running the suite again."""
    import json
    staged_tree = _hook_module("staged_tree.py", "staged_tree_p0b")
    import pre_push
    ledger = tmp_path / "full-runs.jsonl"
    ledger.write_text(json.dumps({"at": "x", "source": "SRC9", "tree": "t", "exit": 0, "summary": "1553 passed"}) + "\n",
                      encoding="utf-8")
    monkeypatch.setattr(pre_push, "LEDGER", ledger)
    monkeypatch.setattr(pre_push, "source_id", lambda rev, root=None: "SRC9")
    monkeypatch.setattr(staged_tree, "sync", lambda *a, **k: (_ for _ in ()).throw(AssertionError("the suite ran")))
    code, out = staged_tree.run_suite(tree="t")
    assert code == 0 and "reused" in out, out
    monkeypatch.setattr(pre_push, "source_id", lambda rev, root=None: "OTHER")
    with pytest.raises(AssertionError, match="the suite ran"):
        staged_tree.run_suite(tree="t")                                    # a changed source runs it


def test_the_commit_message_is_checked_at_preflight_before_any_test(tmp_path) -> None:
    """DEF-249 — (c): the pre-flight checks the commit message's rules (the subject format, the 8D of a fix) before
    it runs anything else — a message the guard would refuse is refused in a second, not after the suite."""
    hook = _hook_module("preflight-on-commit.py", "preflight_on_commit_p0b")
    bad = tmp_path / "msg.txt"
    bad.write_text("refactor(arch-v2): DEF-222, DEF-223 — two ids in the subject\n\nbody\n", encoding="utf-8")
    payload = {"tool_name": "Bash", "tool_input": {"command": f'git commit -F "{bad}"'}}
    code, msg = hook.decide(payload, lambda **k: (_ for _ in ()).throw(AssertionError("the pre-flight ran first")))
    assert code == 2 and "spine format" in msg, (code, msg)
    fix = tmp_path / "fix.txt"
    fix.write_text("fix(upload): G-236 — no 8D in this body\n\nCo-Authored-By: x\n", encoding="utf-8")
    code, msg = hook.decide({"tool_name": "Bash", "tool_input": {"command": f"git commit -F {fix}"}},
                            lambda **k: (_ for _ in ()).throw(AssertionError("the pre-flight ran first")))
    assert code == 2 and "8D" in msg, (code, msg)


def test_a_docs_only_commit_does_not_rebuild_the_board() -> None:
    """DEF-250 — (d): the pre-commit hook rebuilds the control board only when code is staged (the test run ran) or
    the waiting list the board reads changed — a docs-only commit skips it."""
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    block = hook[hook.index('t_log adr-index "$T0"'):hook.index('t_log control-board "$T0"')]
    guard = next(line for line in block.splitlines() if '"$CONTROL"' in line and line.lstrip().startswith("if"))
    assert '"$RAN"' in guard and "board_waiting" in guard, guard


def test_the_fast_run_runs_its_tests_in_parallel_and_the_serial_ones_alone(tmp_path, monkeypatch) -> None:
    """DEF-251 (founder ruling 2026-10-21, item 4): a commit's fast run is not one process for a few files — on
    2026-10-20/21 a 4-file fast run took 241 s while the whole suite's parallel pass took 167 s. Whatever the number
    of files, it runs the full run's two passes over them: everything but `serial` in parallel (worksteal), then
    the `serial` tests alone."""
    import subprocess
    staged_tree = _hook_module("staged_tree.py", "staged_tree_fast")
    files = ["backend/tests/test_a.py", "backend/tests/test_b.py", "backend/tests/test_c.py"]
    for f in files:
        (tmp_path / "agent-improve" / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "agent-improve" / f).write_text("", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(cmd, wt, root=None, timeout=900, **extra):
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="3 passed in 1.00s\n", stderr="")
    monkeypatch.setattr(staged_tree, "fast_tests", lambda root=None: files)
    monkeypatch.setattr(staged_tree, "sync", lambda *a, **k: tmp_path)
    monkeypatch.setattr(staged_tree, "run", fake_run)
    monkeypatch.setattr(staged_tree, "venv_python", lambda root=None: "python")
    code, out = staged_tree.run_fast(tmp_path)
    assert code == 0, out
    assert len(calls) == 2, calls
    par, ser = calls

    def opt(cmd: list[str], flag: str) -> str:
        return cmd[len(cmd) - 1 - cmd[::-1].index(flag) + 1]          # the last one: "-m pytest" comes first
    assert opt(par, "-n") == "auto" and opt(par, "--dist") == "worksteal", par
    assert opt(par, "-m") == "not serial and not wallclock", par
    assert opt(ser, "-n") == "0" and opt(ser, "-m") == "serial and not wallclock", ser
    assert all(f in par and f in ser for f in files), calls


def test_the_status_block_is_built_from_the_staged_tree(tmp_path, monkeypatch) -> None:
    """DEF-252 (founder ruling 2026-10-21, item 4): a docs-only commit was refused (rule 10) while code was
    uncommitted, because CONTINUITY.md's status block is generated from the WORKING tree — the feature list, the
    test record and the product hash on disk — while the board, not rebuilt for a docs-only commit (DEF-250),
    reflects the index. With --staged (as the commit hook calls it), the block is built from the staged tree: the
    worktree of the index the commit's tests run in (staged_tree.sync), never from the checkout."""
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert '"$CONTINUITY" --staged' in hook, "the commit hook does not ask for the staged status block"
    cont = _hook_module("pre-commit-continuity.py", "continuity_p0b")
    import staged_tree
    built: list[str] = []
    monkeypatch.setattr(staged_tree, "sync", lambda root=None, tree=None: tmp_path)
    def build_block(cwd, today=None) -> str:
        built.append(str(cwd))
        return ""
    monkeypatch.setattr(cont.cs, "build_block", build_block)
    monkeypatch.setattr(cont, "_git", lambda args, root: __import__("subprocess").CompletedProcess(
        args, 0, stdout=str(ROOT) if "rev-parse" in args else "", stderr=""))
    cont.main(["--staged"])
    assert built and built[0] == str(tmp_path), f"the block was built from {built}, not the staged tree"


def test_a_live_slice_replays_up_to_the_element_and_runs_only_it() -> None:
    """DEF-253 — T103 (founder ruling 2026-10-21, the lesson of 2026-10-20): a live slice tests one changed element
    live — the recorded answers of a run-through replayed up to that element (its earlier elements seeded as
    confirmed, no model call) and only that element's turns run live, with their calls, cost and checks recorded."""
    import sys
    sys.path.insert(0, str(PROJECT))
    from scripts import live_slice
    record: list[dict[str, Any]] = [
        {"kind": "turn", "n": 1, "belt": "Hi", "action": None, "move": "teach", "field": "business_case"},
        {"kind": "turn", "n": 2, "belt": "The case words", "action": None, "move": "read_back", "field": "business_case"},
        {"kind": "turn", "n": 3, "belt": "Confirm", "action": "confirm", "move": "store_and_advance", "field": "team"},
        {"kind": "turn", "n": 4, "belt": "The team words", "action": None, "move": "challenge", "field": "team"},
        {"kind": "turn", "n": 5, "belt": "The team, again", "action": None, "move": "read_back", "field": "team"},
        {"kind": "turn", "n": 6, "belt": "Confirm", "action": "confirm", "move": "store_and_advance", "field": "voc_summary"},
        {"kind": "turn", "n": 7, "belt": "The customers", "action": None, "move": "read_back", "field": "voc_summary"},
        {"kind": "final_case", "define_structured": {"business_case": "B", "team": [{"name": "Priya"}],
                                                     "voc_summary": "V", "critical_to_quality": ["c"]}},
        {"kind": "summary", "product_hash": "p0"}]
    plan = live_slice.plan_slice(record, "team")
    # replayed (seeded, no model call): every element before `team`, confirmed, with its own helper keys only
    assert plan["structured"] == {"business_case": "B"}, plan["structured"]
    assert plan["field_status"] == {"business_case": {"status": "confirmed"}, "team": {"status": "asked"}}
    # live: only team's turns — those sent while team was in focus, through its Confirm
    assert [(x["belt"], x["action"]) for x in plan["turns"]] == [
        ("The team words", None), ("The team, again", None), ("Confirm", "confirm")], plan["turns"]
    later = live_slice.plan_slice(record, "voc_summary")
    assert "critical_to_quality" not in later["structured"], "a helper key of the element itself was seeded"

    sent: list = []

    class Client:
        def post(self, url, json):
            sent.append((url, json.get("message"), json.get("action")))
            move = "store_and_advance" if json.get("action") == "confirm" else "read_back"

            class R:
                status_code = 200

                @staticmethod
                def json():
                    return {"move": move, "move_field": "voc_summary" if move == "store_and_advance" else "team"}
            return R()
    out = live_slice.replay(Client(), "IMPR-X", plan)
    assert [s[1] for s in sent] == ["The team words", "The team, again", "Confirm"], sent
    assert out["passed"] and out["turns"][-1]["move"] == "store_and_advance", out

    # 2026-10-22 (the goal's slice): a Confirm can store the element and move on with a read-back of the NEXT
    # element (A8, the target read from the goal) — that passes; a Confirm that stays on the element does not.
    def answering(move: str, field: str):
        class C:
            def post(self, url, json):
                class R:
                    status_code = 200

                    @staticmethod
                    def json():
                        return ({"move": move, "move_field": field} if json.get("action") == "confirm"
                                else {"move": "read_back", "move_field": "team"})
                return R()
        return C()
    assert live_slice.replay(answering("read_back", "voc_summary"), "IMPR-X", plan)["passed"]
    assert not live_slice.replay(answering("read_back", "team"), "IMPR-X", plan)["passed"]
