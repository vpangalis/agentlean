"""The parent graph — what procedure step 4.2 established.

Step 4.2's *Done when* is an `azure-query` against the real container: after one
`/ask` turn `checkpoints/{case_id}/latest.json` exists, a second turn adds a
`history/{checkpoint_id}.json` entry, and a client killed mid-turn leaves no new
checkpoint. **That verification needs Azure and is run by hand** — these tests
pin the structural facts underneath it, on an in-process fake saver, so a later
step cannot quietly undo them.

What is pinned here, and why each would be silent if it broke:

  * **`thread_id` reaches the saver as `case_id`** — the whole of §16, and the
    single reason zero checkpoints had ever been written before this step;
  * **checkpointer AND store on the parent, neither on the subgraph** (§16,
    S-F02 B1) — passing only the checkpointer is named in §1.1 as the most
    common architecture mistake, and it fails by losing cross-phase data much
    later, in another phase;
  * **`messages` does not duplicate across turns** — `operator.add` means a
    state update is appended, so a route that re-sends the conversation grows it
    geometrically while every individual turn still looks correct;
  * **one invoke is one coaching turn** — the executor runs once, which is the
    boundary the whole step exists to create;
  * **`gate_apply` applies nothing** — no gate document, no phase advance, until
    the `interrupt()` lands at stage 7.

`InMemorySaver` is BANNED at every stage (§1.7), including tests, so the fake
below is a minimal `BaseCheckpointSaver` that records the `thread_id` and blob
paths `AzureBlobCheckpointSaver` would have written. That is what these tests
are asserting about anyway — the real saver's Azure behaviour is
`test_checkpointer.py`'s subject.
"""
from __future__ import annotations

import asyncio
from typing import Any, Iterator, Optional, Sequence
from urllib.parse import quote

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)

from backend.core import graph as graph_mod
from backend.core.substate import CoachingResponse
from backend.tests.conftest import DEFAULT_REPLY
from backend.core.state import SUPERVISOR_STATE_FIELDS
from backend.phases.mappers_common import PHASE_ORDER


# ── a saver that records what the Azure one would have written ────────────

class RecordingSaver(BaseCheckpointSaver):
    """Records `thread_id` and the two blob paths per `put`, and replays state.

    Mirrors `AzureBlobCheckpointSaver`'s layout, **including the
    `checkpoint_ns` segment step 4.2 added** — the parent keeps
    `checkpoints/{thread_id}/…` and a subgraph goes under
    `checkpoints/{thread_id}/ns/{ns}/…`. Keying this fake on `thread_id`
    alone reproduces the defect exactly: parent and subgraph share one
    `latest.json`, the subgraph loads the parent's `messages` on top of its
    own, and the conversation doubles every turn with no error raised.
    """

    def __init__(self) -> None:
        super().__init__()
        self.writes: list[dict[str, Any]] = []
        self._store: dict[
            tuple[str, str],
            list[tuple[Checkpoint, CheckpointMetadata, Optional[str]]],
        ] = {}

    @staticmethod
    def _key(config: RunnableConfig) -> tuple[str, str]:
        conf = config["configurable"]  # type: ignore[typeddict-item]
        return conf["thread_id"], conf.get("checkpoint_ns") or ""

    @staticmethod
    def _prefix(thread_id: str, ns: str) -> str:
        return (f"checkpoints/{thread_id}" if not ns
                else f"checkpoints/{thread_id}/ns/{quote(ns, safe='')}")

    def put(self, config: RunnableConfig, checkpoint: Checkpoint,
            metadata: CheckpointMetadata, new_versions: dict) -> RunnableConfig:
        thread_id, ns = self._key(config)
        prefix = self._prefix(thread_id, ns)
        self.writes.append({
            "thread_id": thread_id,
            "checkpoint_ns": ns,
            "latest": f"{prefix}/latest.json",
            "history": f"{prefix}/history/{checkpoint['id']}.json",
            "checkpoint_id": checkpoint["id"],
        })
        parent = config.get("configurable", {}).get("checkpoint_id")
        self._store.setdefault((thread_id, ns), []).append(
            (checkpoint, metadata, parent)
        )
        return RunnableConfig(
            configurable={"thread_id": thread_id, "checkpoint_ns": ns,
                          "checkpoint_id": checkpoint["id"]}
        )

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id, ns = self._key(config)
        saved = self._store.get((thread_id, ns))
        if not saved:
            return None
        checkpoint, metadata, parent = saved[-1]
        conf = {"thread_id": thread_id, "checkpoint_ns": ns,
                "checkpoint_id": checkpoint["id"]}
        return CheckpointTuple(
            config=RunnableConfig(configurable=conf),
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=(
                RunnableConfig(configurable={**conf, "checkpoint_id": parent})
                if parent else None
            ),
        )

    def list(self, config, *, filter=None, before=None, limit=None) -> Iterator[CheckpointTuple]:
        return iter([])

    def put_writes(self, config: RunnableConfig,
                   writes: Sequence[tuple[str, Any]],
                   task_id: str, task_path: str = "") -> None:
        return None

    async def aput(self, config, checkpoint, metadata, new_versions):
        return self.put(config, checkpoint, metadata, new_versions)

    async def aget_tuple(self, config):
        return self.get_tuple(config)

    async def alist(self, config, *, filter=None, before=None, limit=None):
        for t in self.list(config, filter=filter, before=before, limit=limit):
            yield t

    async def aput_writes(self, config, writes, task_id, task_path=""):
        return None


class FakeStore:
    """Enough `BaseStore` surface for `define_input_mapper`'s single `get`."""

    def get(self, namespace, key):
        return None

    def put(self, namespace, key, value):  # pragma: no cover — 4.2 writes none
        raise AssertionError("step 4.2 writes nothing to the Store")


CASE_ID = "IMPR-TEST-4T2"


def _seed_state(**overrides: Any) -> dict[str, Any]:
    """A complete `SupervisorState`, so a §56 field addition breaks this first."""
    state: dict[str, Any] = {
        "messages": [],
        "history": [],
        "case_id": CASE_ID,
        "phase_index": 0,
        "current_phase": "define",
        "gate_passed": {},
        "final_output": None,
    }
    assert set(state) == set(SUPERVISOR_STATE_FIELDS)
    state.update(overrides)
    return state


def _config(entry: str = "ask", **configurable: Any) -> dict[str, Any]:
    return {
        "configurable": {
            "thread_id": CASE_ID,
            "entry": entry,
            "current_user": "Tester",
            "case_metadata": {"title": "T", "belt_level": "green",
                              "leader": "L", "department": "D"},
            "v1_phase_inputs": {},
            **configurable,
        },
        "recursion_limit": graph_mod.RECURSION_LIMIT,
    }


@pytest.fixture
def wired(monkeypatch, stub_planner):
    """The parent graph, compiled against the recording saver and a fake store.

    `get_graph` and `_define_subgraph` are `lru_cache`d for the process, so both
    caches are cleared around the test — otherwise the first test to run would
    pin a graph the rest inherit.

    **`stub_planner` is a dependency rather than something each test requests**
    (step 6.1): every invoke here runs the planner node, which now makes a real
    `planner`-role model call. Hanging it on the fixture that compiles the graph
    keeps "this graph does not reach Azure" one statement instead of one per
    test. `conftest.py` says why it stubs `get_llm` and not `_plan_turn`.
    """
    saver = RecordingSaver()
    store = FakeStore()
    monkeypatch.setattr(graph_mod, "get_checkpointer", lambda: saver)
    monkeypatch.setattr(graph_mod, "get_store", lambda: store)
    graph_mod.get_graph.cache_clear()
    graph_mod._subgraph.cache_clear()
    try:
        yield graph_mod.get_graph("define"), saver
    finally:
        graph_mod.get_graph.cache_clear()
        graph_mod._subgraph.cache_clear()


# ── §16: where persistence attaches ───────────────────────────────────────

def test_parent_carries_both_checkpointer_and_store(wired) -> None:
    """§1.1 — "passing only a checkpointer is the most common mistake"."""
    graph, saver = wired
    assert graph.checkpointer is saver
    assert graph.store is not None


def test_subgraph_carries_neither(wired) -> None:
    """S-F02 B1 — the subgraph reaches the parent's through `checkpoint_ns`."""
    subgraph = graph_mod._subgraph("define")
    assert subgraph.checkpointer is None
    assert subgraph.store is None


def test_the_runtime_is_one_phase_node_per_phase(wired) -> None:
    """One invoke is one Belt turn, and the node name carries the phase.

    4.2's parent was a single node hardwired to Define, because Define was the
    only built subgraph. Since **4.4 all five are built**, so the runtime is one
    trivial graph per phase — not one graph with five nodes and a branch from
    `START`, which would be a Level 1 conditional edge and the shape §15 and
    S-F01 forbid. The `{phase}_phase` name is load-bearing: S-F10 derives the
    subgraph's `checkpoint_ns` from it, so a shared name would put every phase's
    state in one namespace.
    """
    graph, _ = wired
    names = {n for n in graph.get_graph().nodes
             if n not in ("__start__", "__end__")}
    assert names == {"define_phase"}
    assert graph_mod.WIRED_PHASES == PHASE_ORDER, "step 4.4 closed WATCH 17"
    for phase in PHASE_ORDER:
        other = {n for n in graph_mod.get_graph(phase).get_graph().nodes
                 if n not in ("__start__", "__end__")}
        assert other == {f"{phase}_phase"}, phase


# ── the step's Done-when, at the layer a unit test can reach ──────────────

def test_one_turn_writes_a_checkpoint_under_the_case_id(wired, stub_coach) -> None:
    """`thread_id` IS `case_id` (§16) — never per phase, never concatenated."""
    graph, saver = wired
    asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="hello")]
    ), config=_config()))

    assert saver.writes, "no checkpoint written — the saver is still inert"
    assert {w["thread_id"] for w in saver.writes} == {CASE_ID}

    parent = [w for w in saver.writes if w["checkpoint_ns"] == ""]
    assert parent, "the parent graph wrote no checkpoint"
    assert all(w["latest"] == f"checkpoints/{CASE_ID}/latest.json"
               for w in parent), "step 4.2's azure-query reads this exact path"
    assert all(w["history"].startswith(f"checkpoints/{CASE_ID}/history/")
               for w in parent)

    # §16 — the subgraph's writes go through the parent's saver, distinguished
    # by the auto-managed namespace. Sharing `latest.json` with the parent is
    # the defect 4.2 found: the subgraph reads the parent's state back.
    child = [w for w in saver.writes if w["checkpoint_ns"]]
    assert child, "the subgraph wrote nothing through the parent's saver"
    assert all(w["checkpoint_ns"].startswith("define_phase:") for w in child)
    assert all(w["latest"].startswith(f"checkpoints/{CASE_ID}/ns/")
               for w in child)
    assert not ({w["latest"] for w in parent} & {w["latest"] for w in child})


def test_a_second_turn_adds_a_distinct_history_entry(wired, stub_coach) -> None:
    """The second half of the *Done when*: history accumulates, latest is one path."""
    graph, saver = wired
    asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="one")]
    ), config=_config()))
    parent_writes = lambda: [w for w in saver.writes if w["checkpoint_ns"] == ""]
    first = {w["checkpoint_id"] for w in parent_writes()}

    asyncio.run(graph.ainvoke(
        {"messages": [HumanMessage(content="two")]}, config=_config()
    ))
    second = {w["checkpoint_id"] for w in parent_writes()} - first

    assert second, "the second turn wrote no new checkpoint"
    assert len({w["latest"] for w in parent_writes()}) == 1, (
        "latest.json is one path per thread; history is what accumulates"
    )


# ── one invoke is one Belt turn ───────────────────────────────────────────

def test_the_executor_runs_exactly_once_per_invoke(wired, stub_coach) -> None:
    """The 4.1 predicate looped here until `GraphRecursionError`."""
    graph, _ = wired
    asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="hello")]
    ), config=_config()))
    assert len(stub_coach.invocations) == 1


def test_the_conversation_is_not_duplicated_across_turns(wired, stub_coach) -> None:
    """`messages` reduces with `operator.add` — the trap this step had to avoid.

    Two turns, one human message each: four messages, not seven and not ten.
    """
    graph, _ = wired
    asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="one")]
    ), config=_config()))
    result = asyncio.run(graph.ainvoke(
        {"messages": [HumanMessage(content="two")]}, config=_config()
    ))

    texts = [m.content for m in result["messages"]]
    assert texts == ["one", DEFAULT_REPLY.message,
                     "two", DEFAULT_REPLY.message], texts


def test_the_coach_sees_the_prior_conversation_on_turn_two(wired, stub_coach) -> None:
    """The checkpoint is what carries it — the case blob is not read again."""
    graph, _ = wired
    asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="one")]
    ), config=_config()))
    asyncio.run(graph.ainvoke(
        {"messages": [HumanMessage(content="two")]}, config=_config()
    ))
    second_turn = stub_coach.invocations[1]["messages"]
    assert [m.content for m in second_turn] == [
        "one", DEFAULT_REPLY.message, "two",
    ]


# ── what the route reads back ─────────────────────────────────────────────

def test_the_turn_product_rides_on_the_reply_message(wired, stub_coach) -> None:
    """`SupervisorState` is seven fields (§5), so this is the channel out.

    **Step 6.2 changed WHAT rides out.** The v1 orchestrator returned
    `sipoc_diagram` and `section_completed` on every turn; the v2 coach emits a
    `CoachingResponse` and calls `propose_diagram` when a picture helps. So the
    draft is what the coach captured, and the diagram is present only on a turn
    that drew one.
    """
    stub_coach.reply = CoachingResponse(
        message="Noted.",
        fields_captured=[{"field_name": "business_case", "value": "b",
                          "source": "belt"}],
    )
    graph, _ = wired
    result = asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="hello")]
    ), config=_config()))

    reply = [m for m in result["messages"] if isinstance(m, AIMessage)][-1]
    extra = reply.additional_kwargs
    assert extra["v1_draft"] == {"business_case": "b"}
    assert extra["gate_verdict"] == {}, "a coaching turn validates nothing"


def test_config_frames_the_coach(wired, stub_coach) -> None:
    """`case_metadata` frames the coaching prompt.

    It rides on `config["configurable"]` because `PhaseState` may not grow a
    field (§56). If LangGraph stops injecting `config` — which it does silently
    when the annotation is not exactly `RunnableConfig` or
    `Optional[RunnableConfig]` — the coach loses its framing with no error.

    **`belt_level` is the one that matters most**: §35's grader suppresses
    Black-Belt-only methodology for a Green Belt, and a coach that does not know
    which it is talking to cannot honour that.
    """
    graph, _ = wired
    asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="hello")]
    ), config=_config()))
    # **Step 6.3 moved this.** The framing was composed into the system prompt
    # by hand at 6.2; it now arrives through `BeforeModelStateInjection`
    # (§19.1), which is the whole point of position 1 — so the assertion moves
    # to the injected block rather than being deleted.
    block = stub_coach.injected_block
    assert "Department: D" in block
    assert "Belt level: green" in block
    assert "Project: T" in block


# ── §47 requirement 2, end to end ─────────────────────────────────────────

def test_history_carries_the_deterministic_step_keys(wired, stub_coach) -> None:
    """The parent reuses the subgraph's `step_log` keys rather than minting new."""
    graph, _ = wired
    result = asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="hello")]
    ), config=_config()))
    assert all(h.startswith("define:") for h in result["history"]), result["history"]
    assert "define:0:planner" in result["history"]
    assert "define:1:validation_stack" in result["history"]


# ── the gate path ─────────────────────────────────────────────────────────

def test_the_gate_entry_skips_the_coach(wired, stub_coach, monkeypatch) -> None:
    """A gate submission validates; it does not spend a coaching turn."""
    graph, _ = wired

    async def fake_validate(state):
        return {"gate_attempts": 2, "escalated": False,
                "phase_inputs": {"define": {"_gate_passed": False,
                                            "_missing_fields": ["team"]}}}

    monkeypatch.setattr(
        "backend.phases.define.nodes.validate_define", fake_validate
    )
    result = asyncio.run(graph.ainvoke(
        _seed_state(messages=[HumanMessage(content="hi")]),
        config=_config(entry="gate"),
    ))

    assert stub_coach.invocations == [], "the executor ran on a gate submission"
    reply = [m for m in result["messages"] if isinstance(m, AIMessage)][-1]
    verdict = reply.additional_kwargs["gate_verdict"]
    assert verdict["passed"] is False
    assert verdict["missing"] == ["team"]
    # NOT a route-scope literal (§1.7) — the counter came off `PhaseState`.
    assert verdict["gate_attempts"] == 2


def test_a_coaching_turn_never_runs_the_validator(wired, stub_coach, monkeypatch) -> None:
    """§34's cap of 3 must not be burned by a Belt who is still typing."""
    graph, _ = wired
    called: list[int] = []

    async def fake_validate(state):
        called.append(1)
        return {"gate_attempts": 1, "phase_inputs": {"define": {}}}

    monkeypatch.setattr(
        "backend.phases.define.nodes.validate_define", fake_validate
    )
    asyncio.run(graph.ainvoke(
        _seed_state(messages=[HumanMessage(content="hi")]), config=_config()
    ))
    assert called == []


# ── what 4.2 must NOT do ──────────────────────────────────────────────────

def test_reaching_end_does_not_apply_the_gate(wired, stub_coach) -> None:
    """No `interrupt()` yet, so END means "the graph ran", not "the Belt approved".

    `FakeStore.put` raises, so a gate document written here fails loudly. The
    phase must also not advance: `current_phase` has one writer, the output
    mapper, and it does not fire until stage 7.
    """
    graph, _ = wired
    result = asyncio.run(graph.ainvoke(_seed_state(
        messages=[HumanMessage(content="hello")]
    ), config=_config()))
    assert result["current_phase"] == "define"
    assert result["phase_index"] == 0
    assert result["gate_passed"] == {}
    assert result["final_output"] is None


def test_a_case_in_a_non_phase_is_refused_rather_than_dispatched(wired) -> None:
    """All five DMAIC phases are wired since 4.4; `"complete"` is not one.

    A finished project is the ordinary way to reach this — `IMPR-2026-E9D`
    carries `current_phase="complete"` — and it must be refused rather than
    coached as whichever phase the graph happens to hold.
    """
    graph, _ = wired
    with pytest.raises(graph_mod.PhaseNotWired, match="complete"):
        asyncio.run(graph.ainvoke(
            _seed_state(current_phase="complete", phase_index=4),
            config=_config(),
        ))
