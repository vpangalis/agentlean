"""The capture path accumulates — procedure step 6.33, G-78.

**A SINGLE-TURN TEST PASSES TODAY AND PROVES NOTHING**, which is why this file
exists and why its centrepiece drives five successive turns. Every capture
destroyed the ones before it, at two independent sites, and each site hid the
other:

  * `mappers_common.new_phase_state` seeded `artifacts` to `{}` on every
    invoke, so the field §6 calls *"the accumulation"* accumulated within one
    turn and was blanked at the start of the next;
  * `gateway/routes.ask` ASSIGNED `case.phases[phase].structured` from THIS
    turn's extraction.

**The second was invisible because of the first.** With `artifacts` blanked,
the turn's extraction was usually empty, so `if clean` skipped the write and
the prior value survived by accident. Fixing either half alone turns a silent
no-op into silent data loss — which is why both land in one commit and why the
reproduction below drives the two together.

The reproduction, as it ran against the tree before the fix:

    turn 1: captured=['problem_statement'] -> structured=['problem_statement']
    turn 2: captured=['goal_statement']    -> structured=['goal_statement']
    …
    LOST: business_case, goal_statement, problem_statement, project_scope

**What these tests drive is the code that ships.** The write half is
`routes.apply_capture`, called by `ask()` and called here — not a copy of its
logic. The seeding half is the real input mapper reading a real Store record
built by the real `_ensure_case_record`. The one thing not exercised is Azure,
and that is the `live-run` half of this step's Verify.

`InMemorySaver` is BANNED at every stage including tests (§1.7), so the
checkpointer is `test_turn_graph.RecordingSaver` — imported rather than copied,
because two hand-maintained copies of one fake is how the two drift apart.
"""
from __future__ import annotations

import asyncio
import operator
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from backend.core import graph as graph_mod
from backend.core.state import SUPERVISOR_STATE_FIELDS
from backend.core.substate import (
    CoachingResponse,
    PhaseState,
    field_log_key,
    is_empty_capture,
    merge_field_log,
    split_captures,
)
from backend.gateway.routes import _ensure_case_record, apply_capture
from backend.phases import nodes_common as _nc
from backend.phases.define.mappers import define_input_mapper
from backend.phases.mappers_common import (
    CASE_RECORD_CAPTURED,
    CASE_RECORD_FIELD_LOG,
    case_record_from_document,
)
from backend.storage.models import CaseDocument
from backend.tests.test_turn_graph import RecordingSaver

CASE_ID = "IMPR-TEST-633"


# ── the harness ───────────────────────────────────────────────────────────


class MemoryStore:
    """A Store that gives back what it is given.

    `test_turn_graph.FakeStore` returns `None` from `get` and raises on `put`,
    which is right for a step that writes nothing to the Store — and useless
    here, where the whole question is whether a value written on turn 1 is
    readable on turn 2. Only `get` and `put` are used: §0.24, the Store is
    reached through `BaseStore`'s two methods and nothing else.
    """

    def __init__(self) -> None:
        self.data: dict[tuple[tuple, str], Any] = {}

    def get(self, namespace, key):  # noqa: ANN001
        value = self.data.get((tuple(namespace), key))
        if value is None:
            return None
        return type("Item", (), {"value": value})()

    def put(self, namespace, key, value) -> None:  # noqa: ANN001
        self.data[(tuple(namespace), key)] = value


def _case() -> CaseDocument:
    return CaseDocument.new(
        case_id=CASE_ID, title="Invoice errors", belt_level="green",
        leader="Ana", department="Finance", target_date="2026-12-01", team=[],
    )


def _config() -> dict[str, Any]:
    return {
        "configurable": {
            "thread_id": CASE_ID, "entry": "ask", "current_user": "Tester",
            "case_metadata": {"title": "Invoice errors", "belt_level": "green",
                              "leader": "Ana", "department": "Finance"},
            "v1_phase_inputs": {},
        },
        "recursion_limit": graph_mod.RECURSION_LIMIT,
    }


def _seed_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "messages": [], "history": [], "case_id": CASE_ID, "phase_index": 0,
        "current_phase": "define", "gate_passed": {}, "final_output": None,
    }
    assert set(state) == set(SUPERVISOR_STATE_FIELDS)
    return state


def _reply(field: str, value: Any, **extra: Any) -> CoachingResponse:
    """One coaching turn's structured output, capturing one field."""
    return CoachingResponse(
        message=f"Noted — {field}.",
        fields_captured=[{"field_name": field, "value": value,
                          "source": "belt", **extra}],
    )


class Session:
    """One project, driven turn by turn through the path that ships.

    Each `turn()` is what `POST /ask` does, in its order: refresh the Store's
    `case` copy from the blob, invoke the graph, fold the turn's product back
    into the case document. Everything between those three is the code under
    test.
    """

    def __init__(self, monkeypatch, phase: str = "define") -> None:
        self.phase = phase
        self.store = MemoryStore()
        self.saver = RecordingSaver()
        self.case = _case()
        self.turns = 0
        monkeypatch.setattr(graph_mod, "get_checkpointer", lambda: self.saver)
        monkeypatch.setattr(graph_mod, "get_store", lambda: self.store)
        monkeypatch.setattr("backend.gateway.routes.get_store",
                            lambda: self.store)
        # **`backend.core.store` itself, and this one is not belt-and-braces.**
        # `routes._ensure_case_record` re-imports `get_store` INSIDE the
        # function, so it resolves from the source module at call time and the
        # two bindings above do not reach it. Without this the helper builds a
        # real `AzureBlobStore` and the suite spends its time in network
        # retries — measured at 59 minutes for this file, and SILENT, because
        # the helper swallows the failure by design (the Store is a copy; the
        # blob is the record). A test that quietly talks to Azure is the trap
        # `_RoutedRead` is autouse for, one layer down.
        monkeypatch.setattr("backend.core.store.get_store",
                            lambda: self.store)
        graph_mod.get_graph.cache_clear()
        graph_mod._subgraph.cache_clear()
        self.graph = graph_mod.get_graph(phase)

    def turn(self, stub_coach, reply: CoachingResponse,
             text: str | None = None) -> dict[str, Any]:
        """One coaching turn. Returns the transport payload the route reads."""
        self.turns += 1
        stub_coach.reply = reply
        _ensure_case_record(self.case)          # routes.ask, first statement
        message = HumanMessage(content=text or f"turn {self.turns}")
        state = ({**_seed_state(), "messages": [message]} if self.turns == 1
                 else {"messages": [message]})
        result = asyncio.run(self.graph.ainvoke(state, config=_config()))
        ai = [m for m in result["messages"] if isinstance(m, AIMessage)][-1]
        payload = dict(ai.additional_kwargs)
        apply_capture(self.case, self.phase, payload)   # routes.ask, the write
        return payload

    @property
    def structured(self) -> dict[str, Any]:
        return dict(self.case.phases[self.phase].structured or {})

    @property
    def field_log(self) -> list[dict[str, Any]]:
        return list(self.case.phases[self.phase].field_log or [])


#: Five fields, five turns — Define's opening sequence, in its coached order.
FIVE_TURNS = [
    ("problem_statement", "Invoices are wrong 12% of the time"),
    ("goal_statement",    "Cut invoice errors to 3% by December"),
    ("business_case",     "Rework costs GBP 180k a year"),
    ("project_scope",     "UK billing only, excludes credit notes"),
    ("team",              "Ana (lead), Ben (finance), Cara (IT)"),
]


# ══════════════════════════════════════════════════════════════════════════
# The step's own Done-when
# ══════════════════════════════════════════════════════════════════════════


def test_five_successive_turns_keep_all_five_fields(monkeypatch,
                                                    stub_planner,
                                                    stub_coach) -> None:
    """**The clause a single-turn test cannot reach.**

    A Belt fills Define's thirteen fields across many turns. Before this step
    the fifth turn's capture was the only one left standing, so the gate
    document could never accumulate, `gate_attempts` had nothing to count and
    §33's gate was unreachable — which is why 7.3 was blocked behind this.
    """
    session = Session(monkeypatch)
    for field, value in FIVE_TURNS:
        session.turn(stub_coach, _reply(field, value))

    assert session.structured == dict(FIVE_TURNS), (
        "a field captured on an earlier turn did not survive to the end"
    )


def test_the_input_mapper_seeds_artifacts_from_the_case_record(
        monkeypatch, stub_planner, stub_coach) -> None:
    """Half one of G-78, at the boundary that owns it.

    `artifacts` is documented as *"the accumulation"*; seeded to `{}` it could
    only ever hold one turn's worth, which is also why it and `draft` were
    always identical.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("problem_statement", "errors at 12%"))

    _ensure_case_record(session.case)
    child = define_input_mapper(
        _seed_state(),                       # type: ignore[arg-type]
        session.store,                               # type: ignore[arg-type]
    )
    assert child["artifacts"] == {"problem_statement": "errors at 12%"}
    assert child["draft"] == {}, (
        "`draft` is THIS turn's extraction (S-F04) and starts empty — the two "
        "were identical only because both were blanked"
    )


def test_a_fresh_phase_seeds_an_empty_accumulator(monkeypatch, stub_planner,
                                                  stub_coach) -> None:
    """`{}` is still the right answer on turn one, and now MEANS turn one.

    The difference this step makes is that an empty `artifacts` is a fact
    about the phase rather than a fact about the wiring — `uploads_for_phase`
    earns the same sentence at 6.11.
    """
    session = Session(monkeypatch)
    _ensure_case_record(session.case)
    child = define_input_mapper(
        _seed_state(),                       # type: ignore[arg-type]
        session.store,                               # type: ignore[arg-type]
    )
    assert child["artifacts"] == {}
    assert child["field_log"] == []


def test_the_write_merges_rather_than_replacing() -> None:
    """Half two of G-78, at the statement that carried it.

    Driven through `apply_capture` — the function `ask()` calls — rather than
    through a restatement of what it does.
    """
    case = _case()
    case.phases["define"].structured = {"problem_statement": "errors at 12%"}

    apply_capture(case, "define", {"v1_draft": {"goal_statement": "3% by Dec"}})

    assert case.phases["define"].structured == {
        "problem_statement": "errors at 12%",
        "goal_statement": "3% by Dec",
    }


def test_a_capture_with_an_empty_value_is_reported_not_dropped(
        caplog) -> None:
    """**The log counted KEYS and the filter dropped on VALUES.**

    *"captured 1 field(s) -> artifacts"* and *"nothing reached the gate
    document"* were both true of the same turn, which is exactly what the
    2026-09-15 live run produced. The value still does not reach the record —
    an empty capture is nothing to store — but it is now NAMED.
    """
    case = _case()
    case.phases["define"].structured = {"business_case": "GBP 180k"}

    with caplog.at_level("WARNING"):
        apply_capture(case, "define", {"v1_draft": {
            "goal_statement": "", "business_case": None,
            "team": "Ana, Ben, Cara",
        }})

    assert case.phases["define"].structured == {
        "business_case": "GBP 180k",        # NOT overwritten with nothing
        "team": "Ana, Ben, Cara",
    }
    reported = "\n".join(r.getMessage() for r in caplog.records)
    assert "business_case" in reported and "goal_statement" in reported


def test_an_empty_capture_does_not_destroy_the_value_in_artifacts(
        monkeypatch, stub_planner, stub_coach) -> None:
    """The same rule at the OTHER end, where it was a real data loss.

    `{**prior, **captured}` with a `None` in `captured` overwrote the value
    the gate document reads, while the case-blob write discarded the same
    entry — two records of one field disagreeing, silently, in the direction
    that loses data. A fix that repaired only the blob would have left this.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("business_case", "Rework costs GBP 180k"))
    session.turn(stub_coach, _reply("business_case", None))

    assert session.structured["business_case"] == "Rework costs GBP 180k"


def test_the_turn_reports_captured_kept_and_empty_together(
        stub_planner, stub_coach) -> None:
    """The audit trail carries what reconciles the two, not just a count.

    `fields_captured` is what the coach NAMED; `fields_empty` is what did not
    reach `artifacts`; `fields_changed` is what the log recorded. A reader with
    only the first cannot tell a quiet turn from a broken one — which is the
    condition that produced *"captured 1 field(s)"* against an empty gate
    document on 2026-09-15.

    Driven against the executor node directly: `step_log` is `PhaseState`'s
    and does not travel to the route, so this is the layer that can see it.
    """
    stub_coach.reply = CoachingResponse(
        message="Noted.",
        fields_captured=[
            {"field_name": "team", "value": "Ana, Ben", "source": "belt"},
            {"field_name": "goal_statement", "value": "  ", "source": "belt"},
        ],
    )
    out = asyncio.run(_nc.executor("define", _phase_state(
        messages=[HumanMessage(content="hello")],
    )))

    assert out["artifacts"] == {"team": "Ana, Ben"}
    assert out["draft"] == {"team": "Ana, Ben", "goal_statement": "  "}, (
        "`draft` is the honest record of what the coach returned, empties "
        "included — the split is about what gets STORED"
    )
    step = out["step_log"][0]
    assert step["fields_captured"] == ["goal_statement", "team"]
    assert step["fields_empty"] == ["goal_statement"]
    assert step["fields_changed"] == ["team"]


# ══════════════════════════════════════════════════════════════════════════
# The ratified extension — the field change log
# ══════════════════════════════════════════════════════════════════════════


def test_the_first_capture_of_a_field_is_an_entry_with_no_prior_value(
        monkeypatch, stub_planner, stub_coach) -> None:
    """A field appearing for the first time IS a change, and says what it is."""
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("baseline_estimate", "12% of invoices"))

    assert len(session.field_log) == 1
    entry = session.field_log[0]
    assert entry["field"] == "baseline_estimate"
    assert entry["value"] == "12% of invoices"
    assert entry["prior_value"] is None
    assert entry["turn"] == 1
    assert entry["phase"] == "define"
    assert entry["timestamp"]
    assert entry["key"] == field_log_key("define", 1, "baseline_estimate")


def test_a_change_records_both_values_with_their_turns(
        monkeypatch, stub_planner, stub_coach) -> None:
    """**The extension's centrepiece.** One field, two turns, both values kept.

    This is the question neither existing field can answer: `artifacts` has
    overwritten the first value and `step_log` never held it.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("baseline_estimate", "about 12%"))
    session.turn(stub_coach, _reply("baseline_estimate", "12.4%, from the Q2 extract"))

    assert session.structured["baseline_estimate"] == "12.4%, from the Q2 extract"
    assert [e["value"] for e in session.field_log] == [
        "about 12%", "12.4%, from the Q2 extract",
    ]
    assert [e["prior_value"] for e in session.field_log] == [
        None, "about 12%",
    ]
    assert [e["turn"] for e in session.field_log] == [1, 2]
    assert all(e["timestamp"] for e in session.field_log)


def test_restating_the_same_value_is_not_a_change(
        monkeypatch, stub_planner, stub_coach) -> None:
    """A Belt repeating themselves is not a revision.

    Logging it would bury the revisions that matter under turns where nothing
    moved — and the gate document's provenance is the reader this exists for.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("business_case", "GBP 180k a year"))
    session.turn(stub_coach, _reply("business_case", "GBP 180k a year"))

    assert len(session.field_log) == 1


def test_the_belts_stated_reason_is_carried_where_it_is_given(
        monkeypatch, stub_planner, stub_coach) -> None:
    """`reason` where given, `None` where not — and today it is given nowhere.

    Nothing asks the coach for one: `CoachingResponse.fields_captured` permits
    the key because its entries are free-form dicts, and its field description
    names `field_name`, `value` and `source` only. So this is proven on a
    capture that carries one and recorded as an EMPTY COLUMN in live use until
    a §56 amendment to S-C05 asks for it. A column that exists and is empty
    says "nobody was asked"; a column that does not exist says nothing.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("baseline_estimate", "about 12%"))
    session.turn(stub_coach, _reply(
        "baseline_estimate", "12.4%",
        reason="the Q2 extract contradicted my estimate",
    ))

    assert session.field_log[0]["reason"] is None
    assert session.field_log[1]["reason"] == (
        "the Q2 extract contradicted my estimate"
    )


def test_the_channel_is_append_only_by_declaration(monkeypatch, stub_planner,
                                                   stub_coach) -> None:
    """**THE MUTATION PROOF — remove the reducer and this goes red.**

    The executor returns THIS TURN's entries. With `merge_field_log` on the
    channel they fold onto the history; with the `Annotated` stripped to a
    bare `list[dict[str, Any]]` LangGraph replaces the channel and the two
    seeded entries vanish — silently, which is the whole argument for putting
    "append, never replace" in the declaration rather than in every writer.

    Run against the compiled SUBGRAPH rather than through the mapper, so what
    is proven is the channel and not the seeding.
    """
    subgraph = graph_mod._subgraph("define")
    seeded = [
        {"key": field_log_key("define", 1, "problem_statement"),
         "field": "problem_statement", "phase": "define", "turn": 1,
         "value": "errors at 12%", "prior_value": None,
         "timestamp": "2026-09-20T09:00:00+00:00", "reason": None},
        {"key": field_log_key("define", 2, "goal_statement"),
         "field": "goal_statement", "phase": "define", "turn": 2,
         "value": "3% by December", "prior_value": None,
         "timestamp": "2026-09-20T09:05:00+00:00", "reason": None},
    ]
    stub_coach.reply = _reply("business_case", "GBP 180k a year")

    result = asyncio.run(subgraph.ainvoke(_phase_state(
        messages=[HumanMessage(content="one"), AIMessage(content="ok"),
                  HumanMessage(content="two"), AIMessage(content="ok"),
                  HumanMessage(content="three")],
        artifacts={"problem_statement": "errors at 12%",
                   "goal_statement": "3% by December"},
        field_log=seeded,
    )))

    assert [e["field"] for e in result["field_log"]] == [
        "problem_statement", "goal_statement", "business_case",
    ], "the turn's own entry REPLACED the history — the reducer is not doing it"


def test_a_rerun_of_the_same_turn_replaces_its_own_entry(
        monkeypatch, stub_planner, stub_coach) -> None:
    """**§11's idempotence, enforced rather than merely recorded.**

    A turn that is retried, resumed from a checkpoint, or replayed after a
    client disconnect re-executes the same logical step. `operator.add` would
    log the change twice and the log would inflate on every retry until it
    stopped being evidence. The key is `{phase}:{turn}:{field}` and the turn
    number is counted in the conversation, so a replay computes the same key.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("business_case", "GBP 180k a year"))

    # The same turn again — same conversation, same ordinal, same key.
    session.turns -= 1
    payload = session.turn(stub_coach, _reply("business_case", "GBP 180k a year"),
                           text="turn 1")
    del payload

    assert len(session.field_log) == 1, session.field_log
    assert session.field_log[0]["turn"] == 1


def test_the_turn_number_is_not_turn_count(monkeypatch, stub_planner,
                                           stub_coach) -> None:
    """The trap this key had to avoid, pinned so it cannot come back.

    `turn_count` is seeded to `0` by the input mapper on every invoke and read
    by `core/graph.py` as the ENTRY MODE, so it is `0` on every coaching turn
    — which is why every `step_log` key of every turn reads `{phase}:0:{node}`.
    A change log keyed on it would have each turn overwrite the one before:
    the defect this step exists to end, reproduced inside the fix. G-39 leaves
    that contract unstated and this routes around it rather than closing it.
    """
    session = Session(monkeypatch)
    payload_one = session.turn(stub_coach, _reply("problem_statement", "12%"))
    payload_two = session.turn(stub_coach, _reply("goal_statement", "3%"))

    assert payload_one["turn_count"] == payload_two["turn_count"] == 1, (
        "if `turn_count` ever starts accumulating, re-read this key's choice"
    )
    assert [e["turn"] for e in session.field_log] == [1, 2]


def test_the_log_crosses_the_turn_boundary_through_the_case_record(
        monkeypatch, stub_planner, stub_coach) -> None:
    """The reducer cannot carry it across turns, and is not asked to.

    The subgraph gets a fresh `checkpoint_ns` per parent turn, so nothing in
    the child state survives a turn on its own — the same reason `gate_attempts`
    cannot accumulate. The seed is what crosses; the reducer is what stops a
    node destroying it once it has.
    """
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("problem_statement", "errors at 12%"))

    record = case_record_from_document(session.case)
    assert record[CASE_RECORD_CAPTURED]["define"] == {
        "problem_statement": "errors at 12%"}
    assert [e["field"] for e in record[CASE_RECORD_FIELD_LOG]["define"]] == [
        "problem_statement"]

    _ensure_case_record(session.case)
    child = define_input_mapper(
        _seed_state(),                       # type: ignore[arg-type]
        session.store,                               # type: ignore[arg-type]
    )
    assert [e["field"] for e in child["field_log"]] == ["problem_statement"]


def test_an_empty_capture_produces_no_entry(monkeypatch, stub_planner,
                                            stub_coach) -> None:
    """It changed nothing, so it is not a change — but it is still reported."""
    session = Session(monkeypatch)
    session.turn(stub_coach, _reply("business_case", ""))
    assert session.field_log == []


# ══════════════════════════════════════════════════════════════════════════
# The reducer and the split, as units
# ══════════════════════════════════════════════════════════════════════════


def test_merge_field_log_upserts_on_the_key() -> None:
    left = [{"key": "define:1:a", "field": "a", "value": "one"}]
    right = [{"key": "define:1:a", "field": "a", "value": "corrected"},
             {"key": "define:2:b", "field": "b", "value": "two"}]
    merged = merge_field_log(left, right)
    assert [e["key"] for e in merged] == ["define:1:a", "define:2:b"]
    assert merged[0]["value"] == "corrected", (
        "a replaced entry must keep its position — order is chronological"
    )


def test_merge_field_log_rebuilds_a_missing_key_rather_than_colliding() -> None:
    """An entry with no `key` is identified from its own fields, not dropped."""
    merged = merge_field_log(
        [{"field": "a", "phase": "define", "turn": 1, "value": "one"}],
        [{"field": "b", "phase": "define", "turn": 1, "value": "two"}],
    )
    assert [e["field"] for e in merged] == ["a", "b"]


def test_merge_field_log_is_not_operator_add() -> None:
    """Stated as a unit, because `operator.add` is what a future edit reaches
    for and the difference only shows on a replay."""
    entry = {"key": "define:1:a", "field": "a", "value": "one"}
    assert merge_field_log([entry], [entry]) == [entry]
    assert operator.add([entry], [entry]) == [entry, entry]


def test_field_log_key_matches_the_step_log_key_shape() -> None:
    """Two builders, one shape (§11) — pinned because they live in two modules.

    `nodes_common` imports `substate`, so `substate` cannot import the key
    builder back without a cycle. The duplication is the import direction, and
    this is what stops it becoming a divergence.
    """
    assert field_log_key("define", 3, "team") == _nc.step_key(
        "define", 3, "team")


@pytest.mark.parametrize("value", [None, "", "   ", [], {}])
def test_these_values_are_empty_captures(value: Any) -> None:
    assert is_empty_capture(value) is True


@pytest.mark.parametrize("value", ["12%", 0, False, ["a"], {"k": "v"}])
def test_these_values_are_not_empty_captures(value: Any) -> None:
    """**`0` and `False` are values, not absences.**

    §7 makes every captured field a string, so this is defence against a model
    returning a bare numeric rather than a supported shape — and it is the
    trap `v != []` would have walked into.
    """
    assert is_empty_capture(value) is False


def test_split_captures_skips_the_v1_seam_internals() -> None:
    """`_gate_passed` and `_missing_fields` are not captures and must not be
    reported as dropped ones — that would report a defect every turn."""
    kept, empty = split_captures({
        "team": "Ana, Ben", "business_case": None,
        "_gate_passed": False, "_missing_fields": ["team"],
    })
    assert kept == {"team": "Ana, Ben"}
    assert empty == ["business_case"]


def _phase_state(**overrides: Any) -> PhaseState:
    """A complete `PhaseState` — a §56 field addition breaks this first."""
    base: PhaseState = {
        "case_id": CASE_ID, "current_phase": "define",
        "messages": [], "history": [], "phase_context": "",
        "coaching_plan": None, "field_index": 0, "draft": {}, "artifacts": {},
        "step_log": [], "field_log": [], "belt_edits": {}, "turn_count": 0,
        "final": {}, "gate_attempts": 0, "validator_feedback": [],
        "rejection_feedback": [], "citations": [], "uploads": [], "asks": [],
        "hop_results": [], "synthesis_output": None,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
    return base
