"""Shared test fixtures — added at procedure step 6.1.

**One fixture, and it exists because step 6.1 gave the planner a real model
call.** Before 6.1 the planner built a stub dict and every test could call it
directly; now `phases/nodes_common._plan_turn` invokes the `planner`-role model
through structured output, so any test that reaches the planner would reach
Azure. Two test modules need the same stub — `test_phase_subgraphs.py` calls the
node directly, `test_turn_graph.py` drives it through the compiled graph — and a
second copy of it is a second thing to keep true.

**It stubs `get_llm`, not `_plan_turn`.** Patching the helper would skip the
code under test: the prompt build, the `with_structured_output(CoachingPlan)`
wiring and the role choice would all go unexercised while the tests still
looked green. Patching the factory leaves all three live and replaces only the
network call — and it lets the fixture ASSERT the role and the schema, which is
how §17's "planner role, temp 0.1" and S-C04 B1's "never JSON from raw text"
become checkable rather than conventions.
"""
from __future__ import annotations

from typing import Any

import pytest

from langchain_core.language_models.fake_chat_models import (
    GenericFakeChatModel,
)
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError

from backend.core.llm import role_temperature
from backend.core.substate import CoachingPlan, CoachingResponse, SufficiencyJudgment

#: A plan for tests that hand the executor a plan directly. Since 6.61 a plan
#: is BUILT BY CODE (`phases/moves.decide`) — the planner model returns only a
#: judgment — so this is what `_plan_turn` builds on an opening Define turn.
DEFAULT_PLAN = CoachingPlan(
    focus_field="business_case",
    status="untaught",
    move="teach",
    retrieval_strategy="single_hop",
    retrieval_hops=[],
)

#: What the fake planner MODEL returns unless a test sets
#: `stub_planner.judgment` — step 6.61: the model's one judgment.
DEFAULT_JUDGMENT = SufficiencyJudgment(verdict="sufficient", reason="it names the cost and the pain")


class _FakePlannerModel:
    """Stands in for `get_llm("planner")` and its structured-output wrapper.

    Records what it was asked so the tests can assert on it rather than on the
    fact that nothing raised.
    """

    def __init__(self) -> None:
        self.judgment: SufficiencyJudgment = DEFAULT_JUDGMENT
        self.prompts: list[str] = []
        self.schemas: list[Any] = []
        self.roles: list[str] = []
        self.temperatures: list[float | None] = []

    # `get_llm(role, temperature=None, ...)` — recorded, then returns self
    # for the `planner` role and a real fake chat model for every other.
    def __call__(self, role: str, temperature: float | None = None,
                 **kwargs: Any) -> Any:
        self.roles.append(role)
        self.temperatures.append(temperature)
        if role != "planner":
            # **Step 6.3 made this necessary and it is not a workaround.**
            # `SummarizationMiddleware` (position 3) is LangChain core used as
            # shipped, and it calls `.with_retry()` and reads `._llm_type` on
            # the model it is given. Handing it this recorder would mean
            # growing a hand-rolled impersonation of `BaseChatModel` — so
            # non-planner roles get LangChain's OWN fake, which has the whole
            # surface, needs no network and needs no Azure credentials.
            return GenericFakeChatModel(messages=iter([]))
        return self

    def with_structured_output(self, schema: Any, **kwargs: Any) -> "_FakePlannerModel":
        self.schemas.append(schema)
        return self



    async def ainvoke(self, prompt: Any, *args: Any, **kwargs: Any) -> SufficiencyJudgment:
        self.prompts.append(str(prompt))
        return self.judgment

    # ── what the tests read ───────────────────────────────────────────────

    @property
    def calls(self) -> int:
        """How many times the planner actually invoked the model."""
        return len(self.prompts)

    @property
    def effective_temperature(self) -> float:
        """The temperature the call resolves to.

        `_plan_turn` passes none, so the role default applies — which is the
        point: §17 and §4.7 put the planner at 0.1, and `get_llm` documents an
        explicit temperature as a deliberate override.
        """
        assert self.temperatures and self.temperatures[-1] is None, (
            "the planner passed an explicit temperature — §17's 0.1 is the "
            "role default, not an override the call site should restate"
        )
        return role_temperature(self.roles[-1])


@pytest.fixture
def stub_planner(monkeypatch) -> _FakePlannerModel:
    """Replace the planner's model so no Azure call is made (step 6.1)."""
    fake = _FakePlannerModel()
    monkeypatch.setattr("backend.phases.nodes_common.get_llm", fake)
    return fake


# ── the executor's agent — step 6.2 ───────────────────────────────────────

DEFAULT_REPLY = CoachingResponse(explanation="", example="", prompt="", progress="", 
    message="Let's start with the business case. Here is what a good one "
            "looks like, then you build yours.",
    fields_captured=[],
    citations=[],
)


class _FakeAgent:
    """One `create_agent(...)` result, and the turns invoked through it."""

    def __init__(self, recorder: "_CreateAgentRecorder") -> None:
        self._rec = recorder

    async def ainvoke(self, payload: dict, *args: Any, **kwargs: Any) -> dict:
        self._rec.invocations.append(payload)
        self._rec.invoke_configs.append(dict(kwargs.get("config") or {}))
        if self._rec.raise_recursion:
            # §3.7's cap, as the real agent raises it. The executor must turn
            # this into a partial answer rather than letting it reach the Belt.
            raise GraphRecursionError("recursion limit reached")
        reply = self._rec.reply
        return {
            # The agent echoes what it was given and appends its own turn —
            # the shape the executor's tail-slice depends on.
            "messages": [*payload.get("messages", []),
                         *self._rec.tool_messages,
                         AIMessage(content=reply.message)],
            "structured_response": reply,
        }


class _CreateAgentRecorder:
    """Stands in for `create_agent`, recording HOW it was called.

    **The kwargs are the point, not just the stub.** CLAUDE.md §0.10 records
    that `prompt=` vs `system_prompt=` sat wrong in the canonical block for
    months, and §18 forbids binding tools onto a bare model. Recording the call
    lets a test assert both against the real construction site rather than
    against a comment.
    """

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.invocations: list[dict[str, Any]] = []
        self.invoke_configs: list[dict[str, Any]] = []
        self.reply: CoachingResponse = DEFAULT_REPLY
        self.tool_messages: list[Any] = []
        #: Make the next `ainvoke` raise §3.7's cap, as the real agent does.
        self.raise_recursion = False

    def __call__(self, **kwargs: Any) -> _FakeAgent:
        self.calls.append(kwargs)
        return _FakeAgent(self)

    @property
    def system_prompt(self) -> str:
        """The composed prompt from the most recent construction."""
        return str(self.calls[-1]["system_prompt"])

    @property
    def tool_names(self) -> list[str]:
        return [t.name for t in self.calls[-1]["tools"]]

    @property
    def middleware(self) -> list[Any]:
        """The stack the executor mounted, in declaration order (§19)."""
        return list(self.calls[-1].get("middleware") or [])

    def middleware_named(self, name: str) -> Any:
        """One mounted middleware, by class name."""
        for m in self.middleware:
            if type(m).__name__ == name:
                return m
        raise AssertionError(
            f"{name} is not mounted; stack is "
            f"{[type(m).__name__ for m in self.middleware]}"
        )

    @property
    def injected_block(self) -> str:
        """What `BeforeModelStateInjection` would put at the top of the prompt.

        Runs the real `before_agent`, so this is the block the coach actually
        sees rather than a restatement of it. Needed because this fixture
        replaces `create_agent`, so the mounted middleware is captured but
        never executed by the agent loop.
        """
        mw = self.middleware_named("BeforeModelStateInjection")
        mw.before_agent(None, None)
        return mw._block


# ── the node-dispatched read — step 6.21, option C ────────────────────────

DEFAULT_SERIES = (
    "complaints.csv · column 'complaints': n=5, mean=3.4000, sigma=1.5166, "
    "min=2, max=6."
)

#: The columns of the file on the G-63 trace (`01a09ff4`), verbatim. `date` is
#: first and is NOT the answer — which is why the header read resolves the
#: first NUMERIC column rather than the first one.
FILE_COLUMNS = ["date", "complaints", "reason"]


class _RoutedRead:
    """Stands in for `load_evidence_series` where the NODE dispatches it.

    Step 6.21 has `executor()` call the tool itself when the planner routes to
    an unread upload, so a `PhaseState` carrying one now performs a real Azure
    blob read unless something replaces it. **That is why this fixture is
    autouse**: the trap is not in the tests that exist, it is in the next test
    someone writes with an upload in its state, which would reach the network
    and fail somewhere unrelated to what it was testing.
    """

    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.content: str = DEFAULT_SERIES
        self.artifact: dict = {"ok": True, "column": "complaints", "n": "5"}
        #: Set to an exception to exercise the fail-soft path.
        self.raises: Exception | None = None

        # ── the header read — G-63 ────────────────────────────────────
        #
        # **Stubbed here for the same reason the tool is, and it is the same
        # trap through a second door.** Since G-63, a routed read whose ask
        # declares no column resolves one from the file's own header, which
        # is another real Azure blob read. Define populates no ask shapes
        # (ruling AR-R2), so in Define this is the NORMAL path — every test
        # with an upload and no declared column would reach the network.
        #
        # `FILE_COLUMNS` is the G-63 trace's own file, so a test asserting
        # "a column the file has" is asserting against the real thing.
        self.file_columns: list[str] = list(FILE_COLUMNS)
        #: What the header read resolves. `None` exercises the refusal branch
        #: — a file with no numeric column is not dispatched at all.
        self.numeric_column: str | None = "complaints"
        self.header_reads: list[str] = []

    async def first_numeric_column(self, blob_path: str) -> str | None:
        self.header_reads.append(blob_path)
        return self.numeric_column

    async def ainvoke(self, call: dict, *args: Any, **kwargs: Any) -> Any:
        self.calls.append(call)
        if self.raises is not None:
            raise self.raises
        return ToolMessage(
            content=self.content, tool_call_id=str(call.get("id")),
            name=str(call.get("name")), artifact=self.artifact,
        )

    @property
    def blob_paths(self) -> list[str]:
        return [str((c.get("args") or {}).get("blob_path")) for c in self.calls]


@pytest.fixture(autouse=True)
def routed_read(monkeypatch) -> _RoutedRead:
    """Replace the tool the node dispatches (step 6.21). Autouse — see above."""
    fake = _RoutedRead()
    monkeypatch.setattr(
        "backend.phases.nodes_common.load_evidence_series", fake)
    monkeypatch.setattr(
        "backend.phases.nodes_common.first_numeric_column",
        fake.first_numeric_column)
    return fake


@pytest.fixture
def stub_coach(monkeypatch) -> _CreateAgentRecorder:
    """Replace `create_agent` so the executor makes no Azure call (step 6.2).

    Stubs the CONSTRUCTOR rather than the model, for the same reason
    `stub_planner` stubs `get_llm` rather than `_plan_turn`: everything the
    executor node actually does — composing the prompt, reading
    `structured_response`, writing `fields_captured` into `artifacts`, merging
    citations, attaching the diagram payload — stays live, and only the model
    and its tool loop are replaced.
    """
    rec = _CreateAgentRecorder()
    monkeypatch.setattr("backend.phases.nodes_common.create_agent", rec)
    return rec


# ── step 6.54 — the per-index search clients are process-wide ─────────────
def store_plan(values: Any) -> CoachingPlan:
    """A STORE-AND-ADVANCE plan whose `store` is `values` — step 6.61.

    Since 6.61 nothing a reply returns is stored: `artifacts` receives only
    what the Belt CONFIRMED, carried on the plan (§20 v1.75). The tests of the
    capture MECHANICS downstream of that decision — the merge, the field log,
    the type and worked-example guards — take their values from here. `values`
    is a dict, or a `CoachingResponse` whose `fields_captured` stands for what
    the Belt confirmed (entries with no `field_name` are dropped, as a
    malformed capture always was)."""
    if isinstance(values, CoachingResponse):
        values = {str(e.get("field_name")).strip(): e.get("value")
                  for e in (values.fields_captured or [])
                  if isinstance(e, dict) and str(e.get("field_name") or "").strip()}
    values = dict(values)
    return CoachingPlan(focus_field=None, status="confirmed", move="store_and_advance",
                        store=values, stored_field=next(iter(values), None))


@pytest.fixture
def confirming_planner(monkeypatch, stub_coach):
    """Every turn confirms what the stub coach's reply carries — the capture
    mechanics through the real graph, with the move logic (tested on its own
    in `test_moves.py`) held at store-and-advance."""
    async def _plan(phase: str, state: Any, config: Any = None) -> CoachingPlan:
        return store_plan(stub_coach.reply)
    monkeypatch.setattr("backend.phases.nodes_common._plan_turn", _plan)
    return stub_coach


@pytest.fixture(autouse=True)
def _fresh_search_clients():
    """Empty `retriever`'s per-index `SearchClient` registry around each test.

    Since 6.54 a search reuses one client per index for the whole process, so
    a test that patches `retriever.SearchClient` would otherwise be handed a
    client an EARLIER test built. Clearing the registry is test isolation for a
    module-level cache — the same thing `cache_clear()` is for `lru_cache` — not
    a change to what the code under test does.
    """
    from backend.knowledge import retriever
    retriever._SEARCH_CLIENTS.clear()
    yield
    retriever._SEARCH_CLIENTS.clear()


# ── gap G-95 — the test suite never sends a trace ─────────────────────────
#
# `init_tracing()` sets LANGCHAIN_TRACING_V2=true for the WHOLE process, so the
# first test that started the app (6.49's row checks, 6.54's warm-up test)
# switched tracing on for every test after it — 827 test graph runs went to
# LangSmith on 2026-09-24, on top of ~4,070 standalone spans, and the monthly
# unique-traces quota ran out (429 on every trace since, real turns included).
#
# Two layers. The switch: tracing off for the session — both environment
# names, the SDK's cached reads cleared, `langsmith.run_trees.configure(
# enabled=False)`, and `init_tracing` made a no-op in the two modules that
# hold it. The GUARD: every run the LangSmith client is asked to create or
# send is COUNTED and NOT sent, and `pytest_sessionfinish` fails the session
# if the count is not zero — so a regression fails the suite instead of
# spending quota.

TRACE_CALLS: list[str] = []
_CLIENT_SENDS = ("create_run", "update_run", "batch_ingest_runs", "multipart_ingest")


@pytest.fixture(scope="session", autouse=True)
def _count_tracing_calls():
    """The GUARD: every run the LangSmith client is asked to create or send is
    counted and NOT sent. Separate from the switch below on purpose — remove
    the switch and this still sees, and fails the session."""
    from langsmith import Client
    mp = pytest.MonkeyPatch()
    for method in _CLIENT_SENDS:
        if hasattr(Client, method):
            mp.setattr(Client, method,
                       lambda self, *a, _m=method, **k: TRACE_CALLS.append(_m))
    yield
    mp.undo()


@pytest.fixture(scope="session", autouse=True)
def _no_tracing(_count_tracing_calls):
    """The SWITCH: tracing off for the session, and `init_tracing` unable to
    turn it back on."""
    import langsmith.utils as ls_utils
    from langsmith.run_trees import configure

    import backend.app as app_mod
    import backend.core.tracing as tracing_mod

    mp = pytest.MonkeyPatch()
    for name in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING_V2",
                 "LANGSMITH_TRACING", "LANGCHAIN_TRACING"):
        mp.setenv(name, "false")
    getattr(ls_utils.get_env_var, "cache_clear")()   # lru_cached in the SDK
    mp.setattr(tracing_mod, "init_tracing", lambda: None)
    mp.setattr(app_mod, "init_tracing", lambda: None)
    configure(enabled=False)
    yield
    mp.undo()


# ── step 6.65 — pytest-xdist: the recorder and the guard, on the controller ──
#
# Under `-n`, each WORKER runs its own session: it sees its own tests' reports
# and its own LangSmith calls. The controller sees every report (xdist relays
# them) but none of the workers' calls. So a worker writes nothing and hands
# its trace-guard count up through `workeroutput`; the controller folds it in
# before its own `sessionfinish` decides, exactly as a serial run does.

_SESSION_START: list[float] = []


def _is_worker(config) -> bool:
    return hasattr(config, "workerinput")


def pytest_sessionstart(session):
    import time as _time
    _SESSION_START.append(_time.monotonic())


def pytest_testnodedown(node, error):
    """Controller only (an xdist hook): a worker's trace-guard count."""
    TRACE_CALLS.extend((getattr(node, "workeroutput", None) or {}).get("trace_calls") or [])


def pytest_sessionfinish(session, exitstatus):
    if _is_worker(session.config):
        session.config.workeroutput["trace_calls"] = list(TRACE_CALLS)
        return
    # Step 6.63 — record the run for the control board. Not when the trace
    # guard fired: a run that broke the quota rule is not evidence of anything.
    if _OUTCOMES and not TRACE_CALLS:
        _record_results()
    _record_slow()
    _time_the_run(session)
    if TRACE_CALLS:
        print(f"\n\nG-95 GUARD: the suite asked LangSmith to create/send "
              f"{len(TRACE_CALLS)} run(s) ({sorted(set(TRACE_CALLS))}). Tests must "
              f"never trace — every trace counts against the monthly quota.")
        session.exitstatus = 1


# ── step 6.63 — the recorded run the control board reads ─────────────────────
#
# A board status is green only when the test it names PASSED ON THE CURRENT
# SOURCE. So every run records each outcome, bound to a hash of the source
# (`tools/control_board/progress.py::source_hash`). Outcomes from a run on the
# same source are merged — a `-k` run adds to the record rather than erasing
# it; a run on changed source starts a new record and keeps the previous one
# as `older`. The board shows an outcome found only in `older` as AMBER: it
# exists, and it is older than the code.

_OUTCOMES: dict[str, str] = {}


_DURATIONS: dict[str, float] = {}
#: A test at or above this many seconds is SLOW: the pre-flight skips it (the
#: commit hook's full run never does). Step 6.67, the addendum's speed item 2.
SLOW_SECONDS = 1.0


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        _OUTCOMES[report.nodeid.replace("\\", "/")] = report.outcome
    if report.when in ("setup", "call"):
        key = report.nodeid.replace("\\", "/")
        _DURATIONS[key] = _DURATIONS.get(key, 0.0) + float(report.duration or 0.0)


def _record_slow() -> None:
    """Step 6.67 — `.claude/logs/slow-tests.json` (local, untracked): every test
    this run measured at SLOW_SECONDS or more; a test measured faster leaves it.
    A measurement for the pre-flight, never evidence of anything."""
    import json as _json
    from pathlib import Path as _Path
    import os as _os
    logs = _os.environ.get("AGENTLEAN_LOGS")  # 6.68: a run in the staged worktree
    path = (_Path(logs) if logs else _Path(__file__).resolve().parents[3] / ".claude" / "logs") / "slow-tests.json"
    try:
        slow = _json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        for nodeid, seconds in _DURATIONS.items():
            if seconds >= SLOW_SECONDS:
                slow[nodeid] = round(seconds, 1)
            else:
                slow.pop(nodeid, None)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_json.dumps(dict(sorted(slow.items())), indent=1) + "\n", encoding="utf-8")
    except (OSError, ValueError):
        pass


def _time_the_run(session) -> None:
    """Step 6.65 — the test recorder times itself (rule g)."""
    import sys as _sys
    import time as _time
    from collections import Counter
    from pathlib import Path as _Path
    if not _SESSION_START:
        return
    hooks = _Path(__file__).resolve().parents[3] / ".claude" / "hooks"
    _sys.path.insert(0, str(hooks))
    try:
        import timing  # type: ignore[import-not-found]
    except ImportError:
        return
    finally:
        _sys.path.pop(0)
    workers = getattr(session.config.option, "numprocesses", None) or 0
    timing.append({"kind": "tests", "seconds": round(_time.monotonic() - _SESSION_START[0], 1),
                   "workers": workers, "tests": len(_OUTCOMES),
                   "outcomes": dict(Counter(_OUTCOMES.values()))})


def _record_results(outcomes_run: dict[str, str] | None = None) -> None:
    """`outcomes_run` defaults to this session's outcomes. A test passes its
    own (step 6.65): patching `_OUTCOMES` instead swallowed that test's own
    report in a serial run — the report landed in the patched dict."""
    run = _OUTCOMES if outcomes_run is None else outcomes_run
    import datetime as _dt
    import json as _json
    import sys as _sys
    from pathlib import Path as _Path

    project = _Path(__file__).resolve().parents[2]
    _sys.path.insert(0, str(project / "tools" / "control_board"))
    try:
        from features import RESULTS, SOURCE_GLOBS, source_hash  # type: ignore[import-not-found]  # 6.67: moved from progress.py
    finally:
        _sys.path.pop(0)
    current = source_hash(project)
    prior = _json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.is_file() else {}
    if prior.get("source_hash") == current:
        outcomes, older = dict(prior.get("outcomes") or {}), prior.get("older") or {}
    else:
        # A run on changed source: the previous record becomes OLDER — kept, so
        # a test this run did not include reads amber ("passed on older code"),
        # never as if it had not been run at all.
        outcomes = {}
        older_out = dict((prior.get("older") or {}).get("outcomes") or {})
        older_out.update(prior.get("outcomes") or {})
        older = {"source_hash": prior.get("source_hash"),
                 "recorded_at": prior.get("recorded_at"),
                 "outcomes": dict(sorted(older_out.items()))} if older_out else {}
    outcomes.update(run)
    # 6.65 — which source the last FULL run was on. The pre-commit hook runs
    # the whole suite with AGENT_IMPROVE_FULL_RUN=1 and the commit-msg guard's
    # rule 4 reads this instead of running the suite a second time. A targeted
    # run on the same source keeps it; a run on changed source clears it.
    import os as _os
    full_hash = (current if _os.environ.get("AGENT_IMPROVE_FULL_RUN") == "1"
                 else prior.get("full_run_hash") if prior.get("source_hash") == current else None)
    # 6.64 — NOT REWRITTEN WHEN NOTHING CHANGED. A run on the same source with
    # the same outcomes used to rewrite the file for its timestamp alone, so
    # every test run dirtied the tree. The record's truth is the source hash
    # and the outcomes; when both are unchanged, the file already says it.
    # A record from before 6.64 carries no commit and is written once more.
    if (prior.get("source_hash") == current and "commit" in prior
            and full_hash == prior.get("full_run_hash")
            and dict(sorted(outcomes.items())) == dict(sorted((prior.get("outcomes") or {}).items()))):
        return
    # The commit the results were run against — HEAD, and whether the product
    # source differed from it at the time. The AMBER is still the source
    # hash's to give (`progress.verdict`); the commit is what lets a reader
    # `git diff` from the run to now.
    root = project.parent
    head = _git(root, "rev-parse", "--short", "HEAD")
    clean = _git(root, "status", "--porcelain", "--", *(
        f"agent-improve/{g.split('/')[0]}" for g in SOURCE_GLOBS)) == ""
    RESULTS.write_text(_json.dumps({
        "source_hash": current,
        "commit": head,
        "commit_matches_source": clean,
        "full_run_hash": full_hash,
        "recorded_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "outcomes": dict(sorted(outcomes.items())),
        "older": older,
    }, indent=1) + "\n", encoding="utf-8")


def _git(root, *args: str) -> str | None:
    """One git read for the recorder; `None` when git cannot answer."""
    import subprocess as _sp
    try:
        return _sp.run(["git", *args], cwd=root, capture_output=True, encoding="utf-8",
                       check=True).stdout.strip()
    except (OSError, _sp.CalledProcessError):
        return None

