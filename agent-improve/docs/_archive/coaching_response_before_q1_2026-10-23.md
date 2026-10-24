# CoachingResponse before Q1 — its docstring and field descriptions (archived 2026-10-23)

Founder ruling 2026-10-23 afternoon, item 2d-f (G-252): the class docstring was sent to the model as the schema's description (4,708 characters, 1,200 tokens — Claude outputs/PROMPT_ANATOMY.md) and the field descriptions carried section, ADR and step codes. The schema now says what the reply is; the build history below is kept here for the ADRs to cite. The shape rules of `fields_captured` moved to the turn's task section (`core/prompts.py::FIELD_SHAPES`).

The class as it stood at commit 1d41db0 (`backend/core/substate.py`):

```python
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
            "§50.1 — the position indicator, e.g. 'Define · Step 4 of 13'. "
            "Always visible. When PROJECT STATE gives the step (WHERE THE "
            "BELT IS), copy that text exactly — never count it yourself, and "
            "never from the gate list."
        ),
    )
    fields_captured: list[dict] = Field(
        default_factory=list,
        description=(
            "The value you READ BACK this turn, as "
            "[{field_name, value, source}] — filled ONLY when THIS TURN'S MOVE "
            "is READ BACK, and then exactly the value your message reads back "
            "to the Belt for confirmation. It is held as PENDING and stored "
            "only if the Belt confirms it; on every other move leave it "
            "empty. Name each field exactly as this phase's field list "
            "spells it. Never include a value the Belt did not state.\n"
            "\n"
            "SHAPE OF `value`. For almost every field it is a plain string — "
            "the Belt's own words, kept as they said them. TWELVE FIELDS ARE "
            "NOT: they are objects, and a sentence describing one is REFUSED "
            "and NOT STORED, which leaves the field uncaptured and the Belt "
            "answering it again. Emit real structure, never prose about "
            "structure:\n"
            "  team → LIST of {name, role, function}, one entry per person\n"
            "  critical_to_quality → LIST of {customer, need, requirement}, "
            "one entry per CTQ\n"
            "  problem_5w2h → {what, where, when, who, why, how, how_much, "
            "steps} — `steps`: LIST of the process step(s) where the problem "
            "shows, as the Belt names them\n"
            "  metric_definitions → LIST of {name, unit, meaning}, one entry "
            "per metric, the primary metric FIRST\n"
            "  project_scope → {in_scope, out_scope}\n"
            "  benefits_analysis → {cost_of_gap, impact_type, "
            "realisation_schedule, finance_contact}\n"
            "  process_map_sipoc → {suppliers, inputs, process_steps, "
            "outputs, customers, process_metrics, process_performance} — the "
            "six columns all filled; process_steps a LIST, one entry per step: "
            "{name, duration {avg, min, max}, runs_per_period, problems "
            "[{note, said_by}]}; process_performance {lead_time, "
            "runs_per_period}. Each figure is the Belt's words with its unit "
            "(\"about 2 days\", \"180 a week\") — code reads the number\n"
            "  detailed_process_map → {steps, cycle_times, resources, "
            "value_vs_waste, measurement_points, baseline_metrics}\n"
            "  control_plan → {documentation, monitoring, response, "
            "training, aligning_systems}\n"
            "  causal_hypothesis, solution_linked_to_root_cause, "
            "post_improvement_metrics → the Belt's content PLUS "
            "references_phase, references_field, references_metric_name, "
            "references_value\n"
            "Values INSIDE those objects are still strings.\n"
            "  baseline_estimate, target_value → NOT an object you build: "
            "the Belt's own words, as a string; the number, the unit and the "
            "direction are read from them in code (ADR-0071).\n"
            "\n"
            "`reason` (G-89, R16): when this read-back CHANGES a value the Belt "
            "confirmed earlier, add `reason` to the entry — why the Belt is "
            "changing it, in their words, from what they said; leave it out "
            "when they gave none or the value is new."
        ),
    )
    citations: list[dict] = Field(
        default_factory=list,
        description="Sources referenced this turn, from retrieval tool results.",
    )
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


```
