"""`PhaseState` — the Level 2 per-phase subgraph state.

Canonical definition: reference **§58.2 — S-C02**. Architecture rationale: §6.
Procedure step 3.1. S-C02 carries a *rebuild test*: this file's `PhaseState`
must be reconstructable from that entry alone, so the field list, the order
and the reducers below are transcribed from it rather than designed here.

Private to one phase subgraph and checkpointed through the parent's saver
under an auto-managed `checkpoint_ns` (§16). It holds the phase's working
data — the plan in flight, what has been captured, the audit trail, the retry
budget — and it is where every value that must survive context compression
lives (§19.3).

**Explicit `TypedDict`, never `MessagesState` inheritance** (§6). The
dominant content here is structured fields, not conversation;
`MessagesState` is appropriate only where the content genuinely is
conversational exchange, which in this architecture is the deferred debate
subgraph and nothing else.

**Nothing is wired into a graph in this step** (procedure 3.1) — this module
declares the schema and no more. The v1 `ImproveGraphState` in `state.py`
remains the live schema until step 11.1.
"""
from __future__ import annotations

import contextvars
import operator
from typing import Annotated, Any, Literal, NotRequired, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.managed import RemainingSteps
from pydantic import BaseModel, ConfigDict, Field, create_model, field_validator, model_validator


class SufficiencyJudgment(BaseModel):
    """THE PLANNER MODEL'S ONE JUDGMENT — step 6.61 (§17 v1.75, S-C04 v1.77).

    Founder ruling 2026-09-25: *"An LLM is used only to judge whether an answer
    is sufficient, and to write the coach's words."* This is the whole of what
    the planner's model returns. Everything else in `CoachingPlan` — the field,
    its status, the move — is code's (`phases/moves.py`).

    **Three verdicts, and the third is not a fourth judgment.** The question is
    one: does the Belt's latest message make a sufficient answer to this field?
    `not_an_answer` is its honest third value — the message asks a question or
    talks about something else, so there is no answer to call sufficient or
    not ("where do we stand?").

    The `description=` on each field is what the model reads (§31).
    """

    verdict: Literal["sufficient", "insufficient", "not_an_answer"] = Field(
        description=(
            "'sufficient' — the answer so far, with the Belt's latest message, "
            "gives everything the field needs. 'insufficient' — it answers the "
            "field but something the field needs is missing or vague. "
            "'not_an_answer' — the latest message does not answer or correct this "
            "field at all: it asks a question, asks where things stand, or is "
            "about something else."
        ),
    )
    reason: str = Field(
        description=(
            "One sentence. For 'insufficient', name exactly what is missing. For "
            "'sufficient', what makes it complete. For 'not_an_answer', what the "
            "message is instead."
        ),
    )
    failed_criterion: Optional[str] = Field(
        default=None,
        description=(
            "R3 — for 'insufficient', the id of the FIRST acceptance criterion "
            "the answer does not meet, exactly as listed (e.g. 'no-cause-no-fix'). "
            "Empty for 'sufficient' and 'not_an_answer'."
        ),
    )
    calculation_inputs: Optional[dict[str, str]] = Field(
        default=None,
        description=(
            "ADR-0077 — ONLY when the prompt lists CALCULATION INPUTS: each listed input the Belt "
            "has stated, keyed by its name, as the Belt's own words with the number (for example "
            "{\"unit_cost\": \"£9\", \"annual_volume\": \"42,000 invoices\"}). Leave out any input "
            "the Belt did not state — never estimate one. Empty otherwise."
        ),
    )
    criterion_spans: Optional[dict[str, str]] = Field(
        default=None,
        description=(
            "ADR-0093 — for 'sufficient': for each acceptance criterion, keyed by its id exactly as "
            "listed, the passage of the Belt's answer that meets it, copied character for character. "
            "Leave out a criterion no passage meets. Empty otherwise."
        ),
    )


class CoachingPlan(BaseModel):
    """The plan for one turn — procedure step 6.1, reshaped at step 6.61.

    Canonical definition: **§58.4 — S-C04**, as amended at v1.77. Architecture
    §17 (the planner/executor contract), §6.

    **6.61 — BUILT BY CODE, not returned by a model.** Until 6.61 this was the
    planner model's structured output and `next_action` was its free-text
    choice of move. The ruling (v1.75) took the move away from every model:
    `phases/moves.decide` derives `focus_field`, `status` and `move` from the
    field's status, and the model contributes `judgment` alone
    (`SufficiencyJudgment`) — and only when the Belt has answered.
    `next_action` is RETIRED; `move` replaces it.

    **A Pydantic model rather than a dict, specifically so `retrieval_strategy`
    can carry a `Literal`** (S-C04): that field selects the executor's entire
    retrieval path, and a typo would fall through silently to single-hop.

    **One plan, never a queue.** B3 — a new plan overwrites the previous one
    entirely. The plan is transient; its consequences are durable (captured
    values in `artifacts`, sources in `citations`, the rationale in `step_log`,
    the exchange in the LangSmith trace), so nothing is lost when it is
    overwritten.

    **Read by attribute, never by subscript** (S-C02 B7):
    `plan.retrieval_hops`, not `plan["retrieval_hops"]`.

    **No model reads these descriptions any more** — since 6.61 no model
    returns this class. The descriptions the planner model reads are
    `SufficiencyJudgment`'s.
    """

    focus_field: Optional[str] = Field(
        description=(
            "The field this turn's reply works on — for a store-and-advance, "
            "the NEXT field, which the same reply teaches. `None` once every "
            "position is confirmed."
        ),
    )
    status: Literal["not taught", "asked", "answered", "confirmed", "parked"] = Field(
        description=("The current field's STORED status at the start of the turn "
                     "(R5: PhaseState.field_status), before this turn's change."),
    )
    move: Literal["teach", "challenge", "read_back", "store_and_advance", "respond", "offer_park"] = Field(
        description="THIS TURN'S MOVE, decided in code from the status (moves.decide).",
    )
    judgment: Optional[SufficiencyJudgment] = Field(
        default=None,
        description="The planner model's one judgment; `None` when none was needed.",
    )
    answer: str = Field(
        default="",
        description="The Belt's own words for the field so far, across messages.",
    )
    messages: int = Field(
        default=0, description="How many Belt messages `answer` spans.",
    )
    pending: Optional[dict] = Field(
        default=None,
        description=(
            "The read-back awaiting the Belt's confirmation — `field`, `fields`, "
            "`belt_words`, `messages`, and after the read-back `store`: what a "
            "confirmation stores. NOTHING in it is stored until confirmed."
        ),
    )
    store: dict[str, Any] = Field(
        default_factory=dict,
        description="What the Belt confirmed THIS turn — the only values written to `artifacts`.",
    )
    stored_field: Optional[str] = Field(
        default=None, description="The position the Belt confirmed this turn.",
    )
    confirmed: Optional[dict[str, Any]] = Field(
        default=None,
        description=("R16 (DEF-021, DEF-082; schema version 5): on a confirming turn, the read-back "
                     "the Belt confirmed — its words, the reason for a change and each value's source — "
                     "for the change log. Never shown to the coach."),
    )
    statuses: dict[str, str] = Field(
        default_factory=dict,
        description="Every position's status AFTER this turn's change — what section 3 shows.",
    )
    field_status: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description=("The after-change `PhaseState.field_status` the executor stores at "
                     "turn end (R5: only code changes a status, at turn end)."),
    )
    reason: str = Field(
        default="",
        description="What the move answers — the judgment's reason, or a click's (Change).",
    )
    retrieval_strategy: Literal["single_hop", "multi_hop"] = Field(
        default="single_hop",
        description=(
            "Which retrieval path the executor takes. Since 6.61 the phase's "
            "default (§28), set in code — no model chooses it."
        ),
    )
    retrieval_hops: list[str] = Field(
        default_factory=list,
        description=(
            "Hop question templates, in order, for a planned multi-hop turn. "
            "Empty since 6.61: no model writes them."
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def _read_pre_r5_status(cls, data: Any) -> Any:
        """A plan checkpointed before ruling R5 carries "untaught" — read it as
        "not taught", or every old checkpoint fails to load (found by row 3's
        check reading IMPR-2026-7F1)."""
        if isinstance(data, dict) and data.get("status") == "untaught":
            return {**data, "status": "not taught"}
        return data

    @model_validator(mode="after")
    def _single_hop_carries_no_hops(self) -> CoachingPlan:
        """**B2** — `single_hop` leaves `retrieval_hops` empty.

        Normalises rather than raises. This runs on model output, and a plan
        rejected for a stray hop list would fail the turn over something the
        strategy field has already decided; the planner node logs when it fired,
        so a model that keeps doing it stays visible.
        """
        if self.retrieval_strategy == "single_hop" and self.retrieval_hops:
            object.__setattr__(self, "retrieval_hops", [])
        return self


#: G-139 (ADR-0075, founder 2026-10-01) — this turn's normalizations of `fields_captured`, one
#: shape name each ("empty_object", "single_entry"). The executor sets a fresh list per turn and
#: copies it into the turn's step_log entry; the validator only appends (a ContextVar holding a
#: list, so a parse in a copied context still reaches the turn's list).
FIELDS_CAPTURED_NORMALIZED: contextvars.ContextVar[list[str] | None] = contextvars.ContextVar(
    "fields_captured_normalized", default=None)


#: The five keys `contradiction_flag` carries when it is set (S-C05, §37).
#: `ContradictionDetectionMiddleware` (S-C10, step 6.5) reads them to build its
#: interrupt payload, so a flag missing one is a flag it cannot present.
CONTRADICTION_FLAG_KEYS: tuple[str, ...] = (
    "prior_field", "approved_value", "approved_phase", "proposed_value",
    "belt_input",
)

#: G-252 (founder ruling 2026-10-23, item 2f): what each key of a contradiction flag holds, in plain words.
_FLAG_MEANING: dict[str, str] = {
    "prior_field": "The field whose approved value is contradicted.",
    "approved_value": "The value approved in the earlier phase.",
    "approved_phase": "The phase that approved it.",
    "proposed_value": "The value the Belt now gives.",
    "belt_input": "The Belt's words that contradict it.",
}

#: Gate fields no reply captures: code writes them.
NOT_CAPTURED: tuple[str, ...] = ("computation_results", "acknowledged_gaps", "citations", "uploads")


class CapturedValue(BaseModel):
    """One value read back to the Belt for confirmation."""

    field_name: str = Field(description="The field, exactly as the phase's field list names it.")
    value: Any = Field(description="The Belt's words as a string, or the structure the field's shape gives.")
    source: str = Field(default="belt", description="Where the value came from: belt, or the uploaded file's name.")
    reason: str = Field(default="", description="Why the Belt is changing a value confirmed earlier, in their "
                                                "words; empty for a new value.")


class Citation(BaseModel):
    """A source this reply relies on."""

    # A citation the coach writes in its own shape (G-176) keeps its keys: the record is mapped in code
    # (core/citations.as_records), and one odd citation never refuses the whole reply.
    model_config = ConfigDict(extra="allow")

    source: str = Field(default="", description="The document, file or index the cited text came from.")
    relevance_summary: str = Field(default="", description="What it says that this reply relies on.")
    role: str = Field(default="", description="The uploaded file's role, as the list of files names it.")


# Built from the keys, so CONTRADICTION_FLAG_KEYS stays the one definition (G-252, item 2f).
ContradictionFlag = create_model(  # type: ignore[call-overload]
    "ContradictionFlag",
    __doc__="A material contradiction of a value approved in an earlier phase.",
    **{k: (str, Field(description=_FLAG_MEANING[k])) for k in CONTRADICTION_FLAG_KEYS},
)


class CoachingResponse(BaseModel):
    """The coach's reply to the Belt: the message, its teaching blocks, and any value read back for confirmation."""

    message: str = Field(description="The coaching text the Belt reads, in plain language.")
    explanation: str = Field(default="", description="What the element is and why it matters, in two or three "
                                                     "plain lines.")
    example: str = Field(default="", description="A worked example, marked as an illustration, never the Belt's "
                                                 "own data.")
    prompt: str = Field(default="", description="The one thing asked of the Belt.")
    progress: str = Field(default="", description="Where the Belt is, copied exactly from the project state.")
    fields_captured: list[CapturedValue] = Field(
        default_factory=list,
        description="The values this reply reads back for confirmation; empty unless this turn's move is a "
                    "read-back.")
    citations: list[Citation] = Field(default_factory=list, description="The sources this reply relies on.")
    contradiction_flag: Optional[ContradictionFlag] = Field(  # type: ignore[valid-type]
        default=None,
        description="Set only when the Belt materially contradicts a value approved in an earlier phase.")

    @field_validator("fields_captured", mode="before")
    @classmethod
    def _one_list(cls, value: Any) -> Any:
        """G-139 (ADR-0075): gpt-4o, through ToolStrategy, returns this list field in two other
        shapes — an empty object `{}` (a challenge, live 083638 turn 10 and 104934 turn 8) and ONE
        entry object (a read-back, 104934 turn 33). Refused, either ended an answer turn in a reply
        written in code. Read as `[]` and as a one-item list; anything else is left to fail."""
        shape = ("empty_object" if isinstance(value, dict) and not value
                 else "single_entry" if isinstance(value, dict) and "field_name" in value else None)
        if shape is None:
            return value
        seen = FIELDS_CAPTURED_NORMALIZED.get()
        if seen is not None:
            seen.append(shape)
        return [] if shape == "empty_object" else [value]


_RESPONSE_MODELS: dict[str, type[CoachingResponse]] = {}


def capturable_fields(phase: str) -> tuple[str, ...]:
    """The fields a reply may read back in `phase`: its gate model's fields, less those code writes."""
    from backend.phases.gate_registry import GATE_SPECS
    return tuple(f for f in GATE_SPECS[phase].model.model_fields if f not in NOT_CAPTURED)


def coaching_response_model(phase: str) -> type[CoachingResponse]:
    """G-252 (founder ruling 2026-10-23, item 2e): the phase's CoachingResponse — `field_name` limited to the phase's
    own field list. A subclass named CoachingResponse, so the tool the coach calls keeps its name."""
    if phase not in _RESPONSE_MODELS:
        names = capturable_fields(phase)
        entry = create_model("CapturedValue", __base__=CapturedValue, __doc__=CapturedValue.__doc__,
                             field_name=(Literal[names], Field(description=CapturedValue.model_fields[  # type: ignore[valid-type]
                                 "field_name"].description)))
        _RESPONSE_MODELS[phase] = create_model(
            "CoachingResponse", __base__=CoachingResponse, __doc__=CoachingResponse.__doc__,
            fields_captured=(list[entry], Field(  # type: ignore[valid-type]
                default_factory=list, description=CoachingResponse.model_fields["fields_captured"].description)))
    return _RESPONSE_MODELS[phase]


#: The four §50.1 fields whose absence is a FINDING rather than a failure.
#: §56 amendment v1.64. `message` is NOT among them — a turn with no coaching
#: text has nothing to say to the Belt and is a real failure, not a gap.
PRESENTATIONAL_FIELDS = ("explanation", "example", "prompt", "progress")


def presentational_gaps(response: CoachingResponse) -> list[str]:
    """Which of §50.1's four blocks came back empty this turn.

    **Empty is a finding, and this is what makes it one.** Before v1.64 the
    four were required, so an omission failed the turn's structured output —
    against §4.8's *never a hard failure to the Belt*. Making them optional
    without this would have traded a loud failure for a silent one, which is
    the worse of the two: the UI would draw four blocks, one of them blank,
    and nothing anywhere would have noticed.

    Whitespace counts as empty. A `progress` of `" "` renders as a layout
    break exactly as `""` does, and §58.5 B6 already says an absence must be
    stated plainly rather than folded away.
    """
    return [f for f in PRESENTATIONAL_FIELDS
            if not str(getattr(response, f, "") or "").strip()]


# ── the capture path — what an empty value means, and who may say so ──────
#
# **The log counted KEYS and the filter dropped on VALUES, and both were
# right about different things.** `nodes_common.executor` logged
# *"captured 1 field(s) -> artifacts"* while `gateway/routes.py` discarded
# every entry whose value was `None`, `[]` or `{}` — so *"captured a field"*
# and *"nothing reached the gate document"* were both true of the same turn
# (step 6.33, G-78). A capture is now split ONCE, here, and the two ends of
# the path read the same answer.


def is_empty_capture(value: Any) -> bool:
    """Whether a captured value carries nothing the Belt could point at.

    `None`, an empty list, an empty dict, and a string that is blank or
    **whitespace**. Whitespace counts on two existing arguments rather than a
    new one: `presentational_gaps` above already treats `" "` as absent
    because it renders as a layout break, and `nodes_common._advance_field_index`
    already reads `str(artifacts.get(field) or "").strip()` when it looks for
    the next uncaptured field. A value the field walk does not count as
    captured must not be one the write counts either.

    **`0` and `False` are values, not absences.** The membership tests are
    typed rather than written `value == []`, which is what keeps `0` out of
    the empty bucket — §7's law makes every captured field a string, so this
    is defence against a model returning a bare numeric, not a supported shape.
    """
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, dict, tuple, set)):
        return not value
    return False


def split_captures(values: Any) -> tuple[dict[str, Any], list[str]]:
    """One turn's captures, split into what carries a value and what does not.

    Returns `(kept, empty)` — `empty` being the FIELD NAMES whose capture
    arrived with nothing in it. **The names, not a count**, because the point
    is that the turn can now say WHICH field the Belt appeared to give and the
    record does not hold: a count reconciles the two logs and still leaves a
    reader guessing.

    **Underscore-prefixed keys are skipped and are not reported as empty.**
    `_gate_passed` and `_missing_fields` are the v1 seam's own internals
    (`nodes_common.to_v1_state`), not captures, and naming them as dropped
    fields would report a defect on every turn.
    """
    kept: dict[str, Any] = {}
    empty: list[str] = []
    for name, value in dict(values or {}).items():
        if str(name).startswith("_"):
            continue
        if is_empty_capture(value):
            empty.append(str(name))
        else:
            kept[str(name)] = value
    return kept, sorted(empty)


# ── the field change log — §56 amendment, ratified 2026-09-21 ─────────────


#: The keys one `field_log` entry carries. Named here because the WRITER
#: (`nodes_common.executor`) and the READER (`gateway/routes.py`, and a
#: reviewer at a gate) are in different files and neither owns the shape.
FIELD_LOG_ENTRY_KEYS: tuple[str, ...] = (
    "key", "field", "phase", "turn", "value", "prior_value",
    "timestamp", "reason",
    # R16 (DEF-082, schema version 5): who confirmed it, and where the value came from.
    "by", "source",
)


def field_log_key(phase: str, turn: int, field: str) -> str:
    """The deterministic identity of one field change — §11.

    ``f"{phase}:{turn}:{field}"`` — §11's key shape with the FIELD in the slot
    `step_log` gives the node, and the whole of the idempotence guarantee:
    *"a turn that is retried, resumed from a checkpoint, or replayed after a
    client disconnect re-executes the same logical step … a deterministic key
    makes the write idempotent, so the replay overwrites its own earlier entry
    instead of duplicating it."*

    **It is not `nodes_common.step_key`, and that is the import direction
    rather than an oversight.** `nodes_common` imports this module; importing
    it back would be a cycle. `test_capture_accumulates.py` asserts the two
    produce the same string for the same three arguments, so the shape cannot
    drift apart in two files.
    """
    return f"{phase}:{turn}:{field}"


def _entry_identity(entry: dict[str, Any]) -> str:
    """One entry's key, rebuilt from its own fields if it carries none."""
    key = str(entry.get("key") or "").strip()
    if key:
        return key
    return field_log_key(
        str(entry.get("phase") or ""),
        int(entry.get("turn") or 0),
        str(entry.get("field") or ""),
    )


def merge_field_log(
    left: list[dict[str, Any]] | None,
    right: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """The `field_log` reducer — **append-only BY DECLARATION**, keyed per §11.

    **This is why `field_log` carries a reducer and `artifacts` does not.**
    `artifacts` merges in its writer (S-C02), which is safe because the
    executor is its only writer and merges every time. A change log has to
    survive a writer that forgets: a node returning `{"field_log": [one new
    entry]}` into a channel with no reducer REPLACES the history with that one
    entry, and the replacement is silent. Declaring the reducer moves
    "append, never replace" from something every writer must remember into
    something the channel does — which is the same move `messages` and
    `step_log` already make with `operator.add`.

    **It is not `operator.add`, and the difference is §11's idempotence.**
    `operator.add` cannot honour a deterministic key: a resumed or replayed
    turn appends its entries a second time, and the log inflates on every
    retry until it stops being evidence of what happened. This upserts on
    `key` — `{phase}:{turn}:{field}` — so **a re-run of the same turn replaces
    its own entry** and a run of the NEXT turn adds one. §11 requires that of
    `step_log` too and `operator.add` does not deliver it there; it is
    delivered here.

    **Order is first-appearance order**, which is chronological: assigning to
    an existing `dict` key keeps the key's original position, so a replaced
    entry stays where it was rather than jumping to the end.

    Used by the channel AND by the case-record write in `gateway/routes.py`,
    deliberately: a log that merges one way in the checkpoint and another way
    in the blob can disagree with itself, and the disagreement would look
    exactly like a missing change.
    """
    merged: dict[str, dict[str, Any]] = {
        _entry_identity(e): dict(e) for e in (left or [])
    }
    for entry in (right or []):
        merged[_entry_identity(entry)] = dict(entry)
    return list(merged.values())



def merge_step_log(
    left: list[dict[str, Any]] | None,
    right: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """The `step_log` reducer — ADR-0107: an upsert on `key`, like `merge_field_log`.

    A node re-run (a retry, a resume after an interrupt, a restart) writes its entry again under the same
    deterministic key (`nodes_common.step_key`), and the later entry replaces the earlier in its first
    position. Entries repeated BY DESIGN carry their repeat in the key — the grader's iteration, and the pass
    after a gate rejection (`:r1`, `:r2` …, ADR-0107's note) — so they are never collapsed.

    **Every entry must carry a key**: a keyless one is refused (ValueError), because an entry without its
    identity can be neither replaced on a replay nor told apart from another. An old checkpoint is unaffected:
    LangGraph restores a stored channel value as it is, and this runs only on new writes."""
    merged: dict[str, dict[str, Any]] = {}
    for entry in [*(left or []), *(right or [])]:
        key = str((entry or {}).get("key") or "").strip()
        if not key:
            raise ValueError(f"a step_log entry carries no key (ADR-0107): {entry!r}")
        merged[key] = dict(entry)
    return list(merged.values())

def value_history(field_log: list[dict[str, Any]] | None,
                  phase: str | None = None) -> dict[str, dict[str, Any]]:
    """R6 (docs/requirements/business.md) — per field, the FIRST confirmed value
    with its date and the CURRENT value with its date, read from `field_log`.

    `field_log` already holds this; nothing new is stored. Since 6.61 an entry
    is written only when the Belt CONFIRMS a value (the executor builds the log
    from what the plan stores), each with its ISO `timestamp` and the value it
    replaced, and the log crosses turns through the case record. So the first
    entry for a field is its first confirmed value and the last is its current
    one. Entries are ordered by timestamp (the reducer keeps first-appearance
    order, which is the same; the sort makes it independent of that).

        {field: {"first":   {"value", "at", "turn"},
                 "current": {"value", "at", "turn"},
                 "changes": <entries for the field>}}
    """
    rows = [e for e in (field_log or [])
            if isinstance(e, dict) and e.get("field")
            and (phase is None or e.get("phase") == phase)]
    rows.sort(key=lambda e: (str(e.get("timestamp") or ""), int(e.get("turn") or 0)))
    out: dict[str, dict[str, Any]] = {}
    for e in rows:
        stamp = {"value": e.get("value"), "at": e.get("timestamp"), "turn": e.get("turn")}
        entry = out.setdefault(str(e["field"]), {"first": stamp, "changes": 0})
        entry["current"] = stamp
        entry["changes"] += 1
    return out


class PhaseState(TypedDict):
    """Twenty-three author-populated fields — two identity, three plumbing,
    eighteen content — plus one engine-managed value: twenty-four declared.
    (`field_status` joined at step 6.61, §56 amendment v1.77.)

    **Any new field requires a §56 amendment**, whatever category it is
    placed in. `test_state.py` asserts the count and the names.

    **This caption was stale by two fields before `field_log` was added, and
    the field list beneath it was right the whole time.** It read *"Twenty …
    fifteen content … twenty-one declared"* while the class carried sixteen
    content fields: `asks` landed at step 6.12 and the caption was never
    updated with it, exactly as `.claude/rules/state.md`'s own caption was
    left behind by `rejection_feedback` at 2.2.23 and says so. Corrected here
    rather than separately — the count was being edited anyway, and a figure
    sync gets said out loud rather than slipped in.
    """

    # ── identity, copied down by the input mapper (2) ────────────────
    #
    # THE COPY-DOWN INVARIANT (S-C02). Both are copied down from the parent
    # `SupervisorState` by the input mapper at phase entry, from no other
    # source — not config, not a build-time constant. They are READ-ONLY
    # inside the subgraph: no node may return either key in its state-update
    # dict (B9). `SupervisorState.current_phase` stays authoritative and
    # keeps its single writer, the output mapper (§5).
    #
    # This is a boundary-time copy, not a second writer: parent and child are
    # two fields on two schemas, and the child's is derived from the parent's
    # exactly once, at entry.
    case_id:            str
    current_phase:      str

    # ── conversation plumbing (3) ────────────────────────────────────
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str

    # ── content fields (15) ──────────────────────────────────────────
    #
    # `coaching_plan` is ONE typed plan, not a queue — overwritten every time
    # the planner fires (B2). **It is now the `CoachingPlan` model above**:
    # step 6.1 landed the real planner, so the `dict[str, Any]` §6 sanctioned
    # as the interim annotation ("typed is preferred") is retired here. Read it
    # by attribute — `coaching_plan.retrieval_hops`, never `["retrieval_hops"]`
    # (B7). `None` until the phase's first planner turn produces one.
    coaching_plan:      Optional[CoachingPlan]
    field_index:        int

    # `draft`, `belt_edits` and `final` are dicts and NEVER str (B6). A
    # string-typed handoff forces the next node to parse prose out of the
    # last one's output — the anti-pattern this architecture exists to remove.
    draft:              dict[str, Any]

    # Everything captured so far, keyed by field name. Every value is a `str`
    # (§7's field typing law), except the three cross-phase reference dicts
    # (S-C32) and the three structured dicts (S-C33). Also holds
    # `computation_results` — §7 forbids a top-level field for those.
    artifacts:          dict[str, Any]

    # The audit trail: HOW each thing was captured, as against WHAT, which is
    # `artifacts`. The two must stay separate. Dicts only — tuples are
    # banned (§10.3).
    # ADR-0107 — an upsert on the entry's key: a replayed step leaves one entry.
    step_log:           Annotated[list[dict[str, Any]], merge_step_log]

    # WHEN each captured value changed, and what it was before — §56
    # amendment, ratified 2026-09-21, built at step 6.33. One entry per
    # change, keyed `{phase}:{turn}:{field}` per §11, including the first
    # capture of a field, which carries no `prior_value`.
    #
    # **A THIRD thing, and it is neither of the other two.** `artifacts` is
    # WHAT is captured and holds only the current value; `step_log` is HOW a
    # TURN went, one entry per node. Neither can answer *"what did
    # `baseline_estimate` say before the Belt changed it on turn 9, and
    # why"* — `artifacts` has overwritten it and `step_log` never held it.
    # For a quality system that is not bookkeeping: a gate document the Belt
    # must be able to stand behind has to be able to show the value's
    # history, not only its last state.
    #
    # **The one channel here whose reducer is not `operator.add`**, because
    # §11's deterministic key has to mean something: `merge_field_log` upserts
    # on the key, so a replayed turn overwrites its own entry instead of
    # logging the same change twice.
    field_log:          Annotated[list[dict[str, Any]], merge_field_log]

    # WHERE EACH FIELD STANDS — step 6.61, founder ruling R5 2026-09-25, §56
    # amendment v1.77. Per coached position: `status` — one of the four,
    # "not taught" -> "asked" -> "answered" -> "confirmed" — plus the Belt's
    # words so far (`answer`, `messages`) and, while a read-back awaits the
    # Belt, `pending` (the value in the Belt's words, and what a yes stores).
    # **Stored, never derived from a reply.** Only code changes it, and only
    # at turn end (the executor writes the plan's after-change map). Seeded by
    # the input mapper from the case record, exactly as `artifacts` is, so it
    # crosses the turn boundary — the subgraph's own state does not.
    field_status:       dict[str, dict[str, Any]]

    # The Belt's corrections at gate step 5. NOT the same thing as
    # `validator_feedback` and must never be merged with it: two actors, two
    # moments (§33). Conflating them has the coach read the Belt's own
    # corrections as validation failures.
    belt_edits:         dict[str, Any]
    turn_count:         int
    final:              dict[str, Any]

    # The shared retry counter for the three-layer validation stack (§34; 2a retired, ADR-0083).
    # PER PHASE and IN THE CHECKPOINT — never in route scope. v1 held the
    # equivalent counter in route scope, so every request rebuilt it at 0,
    # the cap never fired, and the loop reported attempt 1 indefinitely.
    # This placement is the fix for that specific defect (§6).
    gate_attempts:      int

    # G-192 (ADR-0076): what the last FAILED gate submission submitted — `submission_fingerprint`
    # in `phases/nodes_common.py`. The same submission again is not counted against the cap of 3;
    # "" when none failed since the last pass.
    gate_fingerprint:   str

    # Accumulated per-attempt validation failures. Accumulation is the entire
    # point: the shared cap of 3 is defensible only because each attempt is
    # better informed than the last, and this field carries the memory.
    validator_feedback: list[dict]

    # The Belt's stated reasons for REJECTING at gate step 7. A THIRD actor at
    # a THIRD moment, and it must stay separate from the other two:
    # `validator_feedback` is what the validation layers said about the AI's
    # output at step 2, `belt_edits` is what the Belt corrected at step 5, and
    # this is why the Belt refused at step 7. Merging any two has the coach
    # read one actor's intent as another's. The reason is MANDATORY — a
    # rejection with no reason gives the coach nothing to change, so the next
    # turn reproduces the one just refused.
    rejection_feedback: list[dict]
    citations:          list[dict]

    # An EMPTY list is meaningful, not merely empty: because
    # `improve_evidence_index` is the only channel through which external
    # data enters (§29.1), an empty `uploads` means the phase reached its
    # conclusions from the Belt's typed statements alone, and a reviewer
    # should be able to see that.
    uploads:            list[dict]

    # The coach's recorded requests for data — §56 amendment, ratified
    # 2026-09-09 (DECISIONS Part AR2), built at step 6.12. Entry shape:
    # `ask_id`, `role` (§23.2.1's vocabulary), `expected_shape`, `phase`,
    # `asked_at`, `status`.
    #
    # **A SYSTEM record, not a captured value**, which is why it is here and
    # not in `artifacts`: `artifacts` holds what the BELT produced, gate
    # assembly walks it, and a structured `asks` list would need a fifth
    # exception to §7's string law. The case blob was rejected too — §10 says
    # it is written "never mid-conversation" and an ask is born in a coaching
    # turn (Part AR2).
    #
    # **An ask is the logical identity of a document; files are its versions**
    # (ruling AP2.2). The binding is recorded when the coach asks, never
    # reconstructed from a filename afterwards.
    asks:               list[dict]

    # Both carry the planned multi-hop chain (§26) and are `[]` / `None` on
    # every single-hop turn in every phase (B5). They are state rather than
    # node locals because LangSmith traces node inputs and outputs, not
    # interpreter locals: held in a local dict they would be invisible in the
    # trace AND lost on checkpoint restore.
    hop_results:        list[str]
    synthesis_output:   Optional[dict]

    # ── engine-managed (1) — DECLARED, never populated by the mapper ──
    #
    # **`remaining_steps` HAS NOTHING TO DO WITH `step_log`.** They are
    # declared on the same object and share a word, and the word means
    # opposite things in each: `remaining_steps` is LangGraph's own
    # execution counter — `recursion_limit` minus graph-node transitions,
    # engine-owned, meaningless outside a run — while `step_log` is this
    # project's coaching audit trail, hand-written by every node and read by
    # the UI and LangSmith (§10.3). Nothing derives one from the other, and a
    # DMAIC "step" is not a graph step. Said here because the collision is in
    # the schema, where the two are three fields apart.
    #
    # A second unit collision worth naming: `remaining_steps` counts STEPS,
    # and §3.7's cap counts HOPS. The coach's whole tool loop runs inside one
    # node, so this counter moves by 1 per executor turn however many hops
    # that turn made — measured. It is the graceful off-ramp (§26, S-F09 B1),
    # never the hop cap; `phases/nodes_common.py` holds both guards and says
    # which is which.
    #
    # DECLARING IT IS WHAT ACTIVATES IT. `RemainingSteps` resolves to
    # `Annotated[int, RemainingStepsManager]`, and the manager returns
    # `scratchpad.stop - scratchpad.step`. Undeclared, §26's guard
    # `state.get("remaining_steps", 10) <= 2` returned 10 FOREVER and the
    # five-hop cap (§3.7) could never fire — a cap that cannot fire is not a
    # loose cap, it is a check recorded as evidence while proving nothing.
    #
    # S-C02 B1: this is the one declared field the input mapper SHALL NOT
    # populate. LangGraph's execution loop supplies it.
    # `NotRequired` is S-C02's own words — "engine-managed, `NotRequired`
    # in intent". Declaring it literally makes the type express the rule:
    # mypy stops demanding the key from a mapper that is FORBIDDEN to
    # supply it, and LangGraph still registers the managed value.
    # Verified against the pinned LangGraph: with `NotRequired`, the
    # builder still reports {'remaining_steps': RemainingStepsManager}
    # while `__required_keys__` drops it.
    remaining_steps:    NotRequired[RemainingSteps]


# The field census, kept next to the schema so the count in §6 and the count
# in the code cannot drift apart silently. Asserted in `test_state.py`.
PHASE_STATE_IDENTITY_FIELDS = ("case_id", "current_phase")
PHASE_STATE_PLUMBING_FIELDS = ("messages", "history", "phase_context")
PHASE_STATE_CONTENT_FIELDS = (
    "coaching_plan", "field_index", "draft", "artifacts", "step_log",
    "field_log", "field_status",
    "belt_edits", "turn_count", "final", "gate_attempts", "gate_fingerprint",
    "validator_feedback", "rejection_feedback", "citations", "uploads",
    "asks", "hop_results", "synthesis_output",
)

# Declared so LangGraph populates it; the input mapper must NOT (S-C02 B1).
PHASE_STATE_ENGINE_MANAGED_FIELDS = ("remaining_steps",)

# What an input mapper writes: everything except the engine-managed value.
PHASE_STATE_AUTHOR_POPULATED_FIELDS = (
    PHASE_STATE_IDENTITY_FIELDS
    + PHASE_STATE_PLUMBING_FIELDS
    + PHASE_STATE_CONTENT_FIELDS
)

# Read-only inside the subgraph — see the copy-down invariant above. §55.1
# rule 5's check is a grep of every node's return dict for these two keys;
# any hit is a violation.
PHASE_STATE_READ_ONLY_FIELDS = PHASE_STATE_IDENTITY_FIELDS


__all__ = [
    "CapturedValue",
    "Citation",
    "ContradictionFlag",
    "capturable_fields",
    "coaching_response_model",
    "CoachingPlan",
    "SufficiencyJudgment",
    "CoachingResponse",
    "CONTRADICTION_FLAG_KEYS",
    "FIELD_LOG_ENTRY_KEYS",
    "field_log_key",
    "is_empty_capture",
    "merge_field_log",
    "merge_step_log",
    "value_history",
    "split_captures",
    "PhaseState",
    "PHASE_STATE_IDENTITY_FIELDS",
    "PHASE_STATE_PLUMBING_FIELDS",
    "PHASE_STATE_CONTENT_FIELDS",
    "PHASE_STATE_ENGINE_MANAGED_FIELDS",
    "PHASE_STATE_AUTHOR_POPULATED_FIELDS",
    "PHASE_STATE_READ_ONLY_FIELDS",
]
