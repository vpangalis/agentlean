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

import operator
from typing import Annotated, Any, Literal, NotRequired, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.managed import RemainingSteps
from pydantic import BaseModel, Field, model_validator


class CoachingPlan(BaseModel):
    """The planner's structured output — procedure step 6.1.

    Canonical definition: **§58.4 — S-C04**, which carries a *rebuild test*, so
    the four fields and their types below are transcribed from that entry rather
    than designed here. Architecture §17 (the planner/executor contract), §6.

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

    The `description=` on each field is not commentary — it is what the model
    reads when the planner calls it through structured output, the same way a
    tool's `args_schema` descriptions are its interface (§31).
    """

    focus_field: str = Field(
        description=(
            "The single field this turn coaches on, named exactly as it appears "
            "in the phase's coached field order. The coach may not choose a "
            "different one."
        ),
    )
    next_action: str = Field(
        description=(
            "What the coach should do with that field this turn — ask for it, "
            "challenge what the Belt gave, show a worked example, or run a "
            "computation. One turn's move, in a short phrase."
        ),
    )
    retrieval_strategy: Literal["single_hop", "multi_hop"] = Field(
        description=(
            "Which retrieval path the executor takes. 'single_hop' is one "
            "lookup; 'multi_hop' is a planned chain where each question depends "
            "on the previous answer. Not restricted to Analyse."
        ),
    )
    retrieval_hops: list[str] = Field(
        description=(
            "Hop question templates, in order, for a planned multi-hop turn. "
            "Empty for single-hop."
        ),
    )

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


class CoachingResponse(BaseModel):
    """The executor's per-turn structured output — procedure step 6.2.

    Canonical definition: **§58.5 — S-C05**, which carries a *rebuild test*, so
    the eight fields below are transcribed from that entry. Architecture §20,
    §18, §37.

    **The four presentational fields landed at step 6.19, closing G-50.** Until
    then this class carried four of the ratified eight, and the only field the
    UI received was `message` — the single free-text blob §50.1 exists to
    forbid, so that section's *"schema-backed, not prompt-hoped"* render
    contract was prompt-hoped. **The docstring above this one used to read
    "the four fields below are transcribed from that entry" against an entry
    defining eight** — a conformance claim made in the file that broke it.

    **`message` and the four presentational fields are not duplicates.**
    `message` is the TRANSCRIPT entry — appended to `messages`, and what
    `SummarizationMiddleware` later compresses (§19.3). The other four are the
    RENDER CONTRACT: the UI draws one block per field without parsing prose.
    Collapsing them back into one is what §50.1 prevents; dropping `message`
    would leave the conversation history nothing to append.

    **Produced by `response_format=` on `create_agent`, every coaching turn**
    (B1) — never by a second model call, and never substituted for a
    `{Phase}Output`, which is Pydantic-constructed once per phase at
    `gate_apply` (§20, §40).

    **This is the v2 field writer.** `fields_captured` is what the executor
    node writes into `artifacts` under the §39.x names, and its existence is
    what clears WATCH 7: until step 6.2 the v1 `orchestrate.py` +
    `EXTRACTION_{PHASE}` pair wrote v1 names into `draft` and `artifacts` stayed
    empty, so every phase's gate was inert by ruling (DECISIONS Part X, Route
    A). `record_field` is RETIRED and may not return (§29.3) — **a tool would
    make capture a decision the coach might skip; structured output makes it
    part of every response by construction.**

    **What this does NOT give you is truth** (§20). It guarantees shape. A
    schema-valid `baseline_estimate: "4.2"` the model invented is exactly as
    well-formed as one the Belt gave. Content-level defence is the
    anti-hallucination guards in the prompt (§22), validation Layer 2a (§34)
    and the policy advisory (§33) — not this class.

    **Adding a field here requires a §56 amendment**, the same as
    `SupervisorState` and `PhaseState`.

    **`fields_captured` CARRIES THE DECLARED SHAPE — §56 amendment, ratified
    2026-09-23.** Nine coached fields across the five phases are objects rather
    than strings (§7's enumerated exceptions, S-C32 and S-C33), and the
    description above names each with its keys.

    **WHY THE CONTRACT AND NOT THE COACHING SCRIPT.** The shape was first
    written into `skills/dmaic-define-phase/SKILL.md`, which is correct content
    in the right file and **did not reach the model**: SKILL.md loads at LEVEL
    2, on demand, through the `load_skill` tool the coach must choose to call
    (§19.2, S-C12). Measured on four live turns, 2026-09-23 — `load_skill` was
    called **zero** times and all four fields came back as prose.

    **A field's declared shape is part of its TYPE CONTRACT, not part of
    coaching.** A contract that lives only in a document can be broken by
    editing that document, with nothing failing until a Belt reaches a gate.
    This description is the structured-output contract the model receives on
    **every** turn, with nothing to fetch and nothing to choose.

    **It is a DESCRIPTION, not a type change.** The ratified eight fields stay
    eight and `value` stays `Any` — S-C05 B-whatever is untouched, and a
    per-phase response schema stays ruled out. What changed is what the model
    is told, on the one channel it cannot miss.

    **THE FOUR PRESENTATIONAL FIELDS DEFAULT TO `""` — §56 amendment, v1.64,
    founder ruling 2026-09-15.** They were REQUIRED `str` from 6.19 until then,
    which made a model omitting `progress` fail the WHOLE TURN's structured
    output. **That is a hard failure to the Belt, and §4.8 forbids exactly
    that**: the Belt asked a coaching question and would get an error because
    a position indicator was missing.

    **An empty field is a FINDING, not a silence.** `presentational_gaps()`
    names which of the four came back empty, and the executor logs it at
    WARNING. The block still renders, the turn still completes, and the gap is
    visible to whoever is watching rather than fatal to whoever is coaching.
    **Degraded, not broken** — the same shape as the routed read's refusal to
    dispatch (G-63).
    """

    message: str = Field(
        description=(
            "The coaching text the Belt reads. Plain language — no methodology "
            "jargon in team-facing strings (§13)."
        ),
    )
    explanation: str = Field(
        default="",
        description=(
            "§50.1 — plain-language 'what this deliverable is', 2-3 short "
            "lines. Its OWN block in the UI. Never methodology jargon (§13)."
        ),
    )
    example: str = Field(
        default="",
        description=(
            "§50.1 — the worked example, MARKED AS AN ILLUSTRATION so the Belt "
            "cannot mistake it for their own data. Its own visually distinct "
            "block. Never invent a value and present it as theirs."
        ),
    )
    prompt: str = Field(
        default="",
        description=(
            "§50.1 — the request to the Belt, the call to action. One ask, not "
            "three. This is the CTA block the UI draws last."
        ),
    )
    progress: str = Field(
        default="",
        description=(
            "§50.1 — the position indicator, e.g. 'Define · 4 of 12'. Always "
            "visible. Count the phase's COACHED positions, not the gate set."
        ),
    )
    fields_captured: list[dict] = Field(
        default_factory=list,
        description=(
            "Values the BELT supplied this turn, as "
            "[{field_name, value, source}]. Name each field exactly as this "
            "phase's field list spells it. Empty when the Belt supplied "
            "nothing new — which is the common case on a teaching turn. "
            "Never include a value the Belt did not state.\n"
            "\n"
            "SHAPE OF `value`. For almost every field it is a plain string — "
            "the Belt's own words, kept as they said them. NINE FIELDS ARE "
            "NOT: they are objects, and a sentence describing one is REFUSED "
            "and NOT STORED, which leaves the field uncaptured and the Belt "
            "answering it again. Emit real structure, never prose about "
            "structure:\n"
            "  team → LIST of {name, role, function}, one entry per person\n"
            "  metric_definitions → LIST of {name, unit, meaning}, one entry "
            "per metric\n"
            "  project_scope → {in_scope, out_scope}\n"
            "  process_map_sipoc → {suppliers, inputs, process_steps, "
            "outputs, customers, process_metrics} — all six\n"
            "  detailed_process_map → {steps, cycle_times, resources, "
            "value_vs_waste, measurement_points, baseline_metrics}\n"
            "  control_plan → {documentation, monitoring, response, "
            "training, aligning_systems}\n"
            "  causal_hypothesis, solution_linked_to_root_cause, "
            "post_improvement_metrics → the Belt's content PLUS "
            "references_phase, references_field, references_metric_name, "
            "references_value\n"
            "Values INSIDE those objects are still strings."
        ),
    )
    citations: list[dict] = Field(
        default_factory=list,
        description="Sources referenced this turn, from retrieval tool results.",
    )
    contradiction_flag: Optional[dict] = Field(
        default=None,
        description=(
            "Set ONLY where the Belt materially contradicts a value already "
            "gate-approved in an earlier phase, with the five keys "
            "prior_field, approved_value, approved_phase, proposed_value, "
            "belt_input. Leave null for prose rephrasing, and for any "
            "refinement of a current-phase value that has not been committed "
            "yet — that is ordinary coaching, not a contradiction."
        ),
    )


#: The five keys `contradiction_flag` carries when it is set (S-C05, §37).
#: `ContradictionDetectionMiddleware` (S-C10, step 6.5) reads them to build its
#: interrupt payload, so a flag missing one is a flag it cannot present.
CONTRADICTION_FLAG_KEYS: tuple[str, ...] = (
    "prior_field", "approved_value", "approved_phase", "proposed_value",
    "belt_input",
)



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


class PhaseState(TypedDict):
    """Twenty-two author-populated fields — two identity, three plumbing,
    seventeen content — plus one engine-managed value: twenty-three declared.

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
    step_log:           Annotated[list[dict[str, Any]], operator.add]

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

    # The Belt's corrections at gate step 5. NOT the same thing as
    # `validator_feedback` and must never be merged with it: two actors, two
    # moments (§33). Conflating them has the coach read the Belt's own
    # corrections as validation failures.
    belt_edits:         dict[str, Any]
    turn_count:         int
    final:              dict[str, Any]

    # The shared retry counter for the four-layer validation stack (§34).
    # PER PHASE and IN THE CHECKPOINT — never in route scope. v1 held the
    # equivalent counter in route scope, so every request rebuilt it at 0,
    # the cap never fired, and the loop reported attempt 1 indefinitely.
    # This placement is the fix for that specific defect (§6).
    gate_attempts:      int

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
    "field_log",
    "belt_edits", "turn_count", "final", "gate_attempts",
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
    "CoachingPlan",
    "CoachingResponse",
    "CONTRADICTION_FLAG_KEYS",
    "FIELD_LOG_ENTRY_KEYS",
    "field_log_key",
    "is_empty_capture",
    "merge_field_log",
    "split_captures",
    "PhaseState",
    "PHASE_STATE_IDENTITY_FIELDS",
    "PHASE_STATE_PLUMBING_FIELDS",
    "PHASE_STATE_CONTENT_FIELDS",
    "PHASE_STATE_ENGINE_MANAGED_FIELDS",
    "PHASE_STATE_AUTHOR_POPULATED_FIELDS",
    "PHASE_STATE_READ_ONLY_FIELDS",
]
