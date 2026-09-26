"""Define phase gate document.

ARCHITECTURE.md §39.1 · §40 · §63.1 (S-C27) · CLAUDE.md §10.7, §10.8, §2.

**This file is one third of an atomic unit** (§56.1). `schema.py` owns the field
names, types and shape; `validate.py` owns which of them block the gate; and
`skills/dmaic-define-phase/SKILL.md` coaches those exact names in the §39.1.2
order. **They are rebuilt together or not at all.** A mismatch does not fail
loudly — capture writes `artifacts["x"]`, `DefineOutput(**artifacts)` has no
`x`, and the gate raises on a Belt who has done nothing wrong, one phase later.

**Define has THIRTEEN elements, all gate-required, with no Tier 1 / Tier 2
split** — the founder's requirement R4 (`docs/requirements/define.md`,
2026-09-26) added the benefits analysis to the twelve of Option A (ratified
2026-08-26). Two consequences follow and both are load-bearing:
`DEFINE_REQUIRED_FOR_GATE` is the whole coached list plus the fields captured
inside a position, and **there is no `acknowledged_gaps` path out of Define**
because no field is skippable.

**Declaration order IS the coached order** (§39.1.2). With no tiers to group by,
the schema order and the `field_index` sequence are one list rather than two.

Classes live here by §2 — `phases/{phase}/schema.py` is one of the named files
where Pydantic models are permitted.
"""
from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, Field

# ── The 13 elements that BLOCK the gate — all of them ──────────────────
# R4 (founder, 2026-09-26): the twelve of Option A plus the benefits analysis.
# Every Define element is gate-required, so this list is also
# `DEFINE_FIELD_ORDER` below. Layer 2b checks presence deterministically — no
# LLM. `validate.py` imports this list; it is not duplicated there.
#
# Ordered as coached. A field's position here is its `field_index`.
DEFINE_REQUIRED_FIELDS: tuple[str, ...] = (
    "business_case",        # 1
    "team",                 # 2
    "voc_summary",          # 3  with the CTQs (critical_to_quality) inside
    "problem_statement",    # 4  composed from 5W2H (problem_5w2h inside)
    "baseline_estimate",    # 5  the ONE primary metric's value (registry inside)
    "project_scope",        # 6
    "goal_statement",       # 7  the objective statement
    "target_value",         # 8  discrete — Control compares achieved-vs-target
    "target_date",          # 9  the PLANNED completion date
    "benefits_analysis",    # 10 R4 — the savings calculation feeds it
    "secondary_metrics",    # 11 what could get worse
    "process_map_sipoc",    # 12 as-is
    "issues_and_barriers",  # 13 always last
)

# The order the coach walks and the planner indexes with `field_index`
# (§39.1.2 — this list closed G-38). It is the same list as
# DEFINE_REQUIRED_FIELDS: nothing is coached that does not block the gate, and
# nothing blocks the gate that is not coached.
#
# The four gate-metadata fields are assembled at `gate_apply`, never coached,
# so they are absent here by design.
DEFINE_FIELD_ORDER: tuple[str, ...] = DEFINE_REQUIRED_FIELDS

# Three gate-required fields are captured INSIDE a coached position rather than
# at their own, because the Belt answers both halves in one exchange:
#   metric_definitions   the METRIC REGISTRY (§63.8, S-C38), inside position 5 —
#                        "what are we measuring, in what units" and "what is it
#                        at today" are one exchange. The PRIMARY metric is the
#                        first entry (R7: exactly one primary).
#   critical_to_quality  the CTQs, inside position 3 — R4: "VOC includes the CTQs"
#   problem_5w2h         the seven 5W2H answers, inside position 4 — the problem
#                        statement is composed from them, and the Define report
#                        draws them as a diagram (R5)
DEFINE_REQUIRED_FOR_GATE_FIELDS: tuple[str, ...] = DEFINE_REQUIRED_FIELDS + (
    "metric_definitions", "critical_to_quality", "problem_5w2h",
)

# ── Step 6.57 — the Belt's position, COMPUTED ────────────────────────────
#
# **"Step n of 13" is this function's answer, never the model's count.** On
# 2026-09-24 every coached turn on 0E5 wrote a count off the gate list, the only
# count the coach was ever given. The walk has THIRTEEN positions (R4); the
# three fields captured inside a position (above) make positions 3, 4 and 5
# complete only when both halves are in.
#
# ONE function for every reader: the state-injection block delivers it, the
# executor records it, `field_index` is it minus one, and step 10.3's progress
# bar must call it rather than count again.
DEFINE_POSITIONS: int = len(DEFINE_FIELD_ORDER)

#: Fields captured INSIDE a coached position rather than at their own.
_CAPTURED_INSIDE: dict[str, tuple[str, ...]] = {
    "voc_summary": ("critical_to_quality",),
    "problem_statement": ("problem_5w2h",),
    "baseline_estimate": ("metric_definitions",),
}


def _is_captured(artifacts: Mapping[str, Any], field: str) -> bool:
    """`artifacts` carries `str` or structure (§7); blank is not an answer."""
    return bool(str(artifacts.get(field) or "").strip())


def define_position(artifacts: Mapping[str, Any]) -> int:
    """The Define position being coached, 1..13: the first not yet complete.

    Once every position is complete it rests on 12 rather than running off
    the end — there is no thirteenth step to point at.
    """
    for position, field in enumerate(DEFINE_FIELD_ORDER, start=1):
        if not all(_is_captured(artifacts, f)
                   for f in (field, *_CAPTURED_INSIDE.get(field, ()))):
            return position
    return DEFINE_POSITIONS


def define_progress(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    """The position, its field, and the label the Belt is shown."""
    position = define_position(artifacts)
    return {"position": position, "of": DEFINE_POSITIONS,
            "field": DEFINE_FIELD_ORDER[position - 1],
            "label": f"Define · Step {position} of {DEFINE_POSITIONS}"}


# Keys on each `metric_definitions` entry (§63.8). `name` is the traceability
# key — written identically in every phase, and the thing the grader matches on.
METRIC_DEFINITION_KEYS: tuple[str, ...] = ("name", "unit", "meaning")

# Keys on each `phase_metrics` entry (§63.9). `name` MUST equal a registry
# `name`; the remaining keys are whatever state the phase produced.
PHASE_METRIC_REQUIRED_KEYS: tuple[str, ...] = ("name",)

# The six SIPOC keys. Fewer than six filled is the partial-map failure the
# field exists to catch (§41): a Belt who maps steps 3-5 of a seven-step
# process produces a project that cannot show improvement, because the
# baseline never covered the whole thing.
SIPOC_KEYS: tuple[str, ...] = (
    "suppliers", "inputs", "process_steps", "outputs", "customers",
    "process_metrics",
)

# Both scope halves are required. What the project is deliberately NOT doing
# is what protects it from ballooning (§39.1.2 B4).
PROJECT_SCOPE_KEYS: tuple[str, ...] = ("in_scope", "out_scope")

# Each team entry carries all three (§39.1.4).
TEAM_MEMBER_KEYS: tuple[str, ...] = ("name", "role", "function")

# R4 — each CTQ turns a customer need into a measurable requirement (p. 31, 82).
CTQ_KEYS: tuple[str, ...] = ("customer", "need", "requirement")

# R5 — the 5W2H answers the problem statement is composed from, drawn as a
# diagram in the Define report. Each in the Belt's words.
FIVE_W_TWO_H_KEYS: tuple[str, ...] = (
    "what", "where", "when", "who", "why", "how", "how_much",
)

# R4 — the benefits analysis: the cost of the gap (COPQ), sustainable or
# one-off, when the money lands, and who in finance validates it (p. 60-63).
BENEFITS_ANALYSIS_KEYS: tuple[str, ...] = (
    "cost_of_gap", "impact_type", "realisation_schedule", "finance_contact",
)


class DefineOutput(BaseModel):
    """Gate document for the Define phase — 21 fields.

    **13 coached elements, all gate-required · three fields captured inside a
    position (`metric_definitions`, `critical_to_quality`, `problem_5w2h`), also
    gate-required · `phase_metrics` · 4 gate metadata.** Sixteen block the gate;
    thirteen are coached. No tier split — see the module docstring. The count
    is `DefineOutput.model_fields`'s; this docstring does not own it.

    Assembled ONCE, at `gate_apply`, by Pydantic construction over values
    already captured — **there is no LLM call in this path** (§20, §33). Every
    one of the 12 is read `artifacts["field"]` so a missing one raises: Layer 2b
    should have blocked the gate, and reaching assembly without the field is a
    bug that must surface loudly. **Define never uses the Tier 2
    `.get(..., "")` pattern** — it has no Tier 2 fields (§40.1, S-F28).

    **The measurement thread — do not "simplify" these away.** `baseline_estimate`,
    `target_value` and `target_date` are discrete fields on purpose, not
    redundant restatements of `goal_statement`. That field is the
    human-readable SMART sentence; these three are the machine-readable values
    **Control extracts to compute target-vs-actual**. Folded into prose, they
    would leave Control with nothing to compare. This mirrors the three-phase
    KPI thread `process_map_sipoc["process_metrics"]` ->
    `detailed_process_map["baseline_metrics"]` -> `post_improvement_metrics` (§39).
    """

    # ── The 13 gate-required elements, in coached order (R4) ──────────
    business_case: str = Field(
        ...,
        description=(
            "Strategic rationale — why the project is worth investing in, with "
            "the quantified impact (COPQ) where the Belt has it."
        ),
    )
    team: list[dict] = Field(
        ...,
        description=(
            "Project team. Each entry {name, role, function}. Roles per "
            "§39.1.4: Project Leader, Sponsor/Champion, Process Owner, Team "
            "Members. Coached early because the people must exist before the "
            "work."
        ),
    )
    voc_summary: str = Field(
        ...,
        description=(
            "Voice of the Customer — who the process serves and what they "
            "need, including what they complain about most. Its CTQs are "
            "`critical_to_quality`, captured in the same exchange."
        ),
    )
    problem_statement: str = Field(
        ...,
        description=(
            "ONE SMART statement, composed by the coach from the Belt's own "
            "5W2H answers and confirmed by the Belt before storage (§39.1.3). "
            "The 5W2H are coaching prompts, never stored fields."
        ),
    )
    baseline_estimate: str = Field(
        ...,
        description=(
            "DISCRETE current-state value — Control compares against it. "
            "Rough as the Belt states it here; the rigorous baseline is "
            "Measure's job. This one anchors the goal."
        ),
    )
    project_scope: dict = Field(
        ...,
        description=(
            "{in_scope, out_scope} — both explicit. Stating what is out is "
            "what protects the project from ballooning."
        ),
    )
    goal_statement: str = Field(
        ...,
        description=(
            "The SMART sentence — human-readable prose mirroring the problem. "
            "The comparable values live in `baseline_estimate` and "
            "`target_value`, not in here."
        ),
    )
    target_value: str = Field(
        ...,
        description=(
            "DISCRETE target value, in the same metric and units as "
            "`baseline_estimate`. Control compares the achieved value against "
            "it. NOT redundant with `goal_statement`: that is prose, this is the "
            "comparable value (§39.1.2, the measurement thread)."
        ),
    )
    target_date: str = Field(
        ...,
        description=(
            "The PLANNED completion date, ISO format — a project-management "
            "parameter that may slip without invalidating the improvement. "
            "The single date field: `estimated_completion_date` is retired as "
            "a duplicate (F-11). Control's paired actual close date is not yet "
            "specified (F-12)."
        ),
    )
    benefits_analysis: dict = Field(
        ...,
        description=(
            "R4 — {cost_of_gap, impact_type, realisation_schedule, "
            "finance_contact}: what the gap costs (COPQ), sustainable or "
            "one-off, when the money lands, and who in finance validates it. "
            "The expected-savings calculation is proposed as `cost_of_gap`; "
            "the Belt confirms it in their own words."
        ),
    )
    secondary_metrics: str = Field(
        ...,
        description=(
            "What could get worse — the side-effect watch. On all five schemas "
            "alongside `issues_and_barriers` (§40); gate-required in Define."
        ),
    )
    process_map_sipoc: dict = Field(
        ...,
        description=(
            "SIPOC with six keys: suppliers, inputs, process_steps, outputs, "
            "customers, process_metrics. `process_metrics` carries WHAT is measured "
            "— the first link of the three-phase measurement thread (§39)."
        ),
    )
    issues_and_barriers: str = Field(
        ...,
        description=(
            "Belt-stated blockers. Gate-required in every phase (§40). 'none "
            "identified at this stage' is a valid conscious answer; silence "
            "is not."
        ),
    )

    # ── Captured inside positions 3 and 4 (R4, R5) ────────────────────
    critical_to_quality: list[dict] = Field(
        ...,
        description=(
            "The CTQs — one entry per requirement, {customer, need, "
            "requirement}, where `requirement` is the measurable form of the "
            "need. Captured inside position 3 with `voc_summary`."
        ),
    )
    problem_5w2h: dict = Field(
        ...,
        description=(
            "{what, where, when, who, why, how, how_much} — the Belt's own "
            "answers the problem statement is composed from, drawn as the "
            "5W2H diagram in the Define report. Captured inside position 4."
        ),
    )

    # ── The metric registry — Define owns it (§63.8, S-C38) ──────────
    metric_definitions: list[dict] = Field(
        ...,
        description=(
            "THE PROJECT'S METRIC REGISTRY. One entry per metric the project "
            "tracks: {name, unit, meaning}. `name` is the stable traceability "
            "key — written identically in every phase, and what the grader "
            "matches on to follow a metric across the five gate documents. "
            "The FIRST entry is the ONE primary metric (R7). Gate-required, "
            "captured inside position 5's conversation."
        ),
    )

    # ── phase_metrics — on all five schemas (§40, §63.9, S-C39) ───────
    phase_metrics: list[dict] = Field(
        default_factory=list,
        description=(
            "What THIS phase produced for each registry metric it engaged. "
            "One entry per metric, `name` equal to a registry `name`. Define "
            "records the stated starting point and target: "
            "{name, unit, baseline_estimate, target_value, source: 'stated'}. "
            "A phase touching no metric writes 'none this phase' — never a "
            "silent gap (§40)."
        ),
    )

    # ── Gate metadata — same four on all five schemas (§40) ───────────
    computation_results: list[dict] = Field(default_factory=list)
    acknowledged_gaps: list[str] = Field(
        default_factory=list,
        description=(
            "Kept for cross-schema uniformity (§40) and ALWAYS EMPTY for "
            "Define: under Option A no field is skippable, so nothing can be "
            "acknowledged as skipped."
        ),
    )
    citations: list[dict] = Field(default_factory=list)
    uploads: list[dict] = Field(default_factory=list)


from backend.phases.gate_assembly import (  # noqa: E402
    build_gate_document,
    tier_1,
)


#: What Define states about a metric, as against what Measure measures (§63.9).
#: Written into every entry rather than inferred, because a later phase reading
#: the trail has to know which kind of number it is looking at.
DEFINE_METRIC_SOURCE = "stated"

#: What a registry metric this phase did not address writes into its scalars.
#: **Founder ruling 2026-09-23**, matching Analyse (§39.3.3) and Improve
#: (§39.4.3), which both write it into the content key of an entry they carry
#: but did not act on. **Two conventions for one fact would be read by one
#: grader**, so Define does not invent a third — an empty string would have
#: been that third, and §63.9's *"never a silent absence"* is the rule both
#: existing phases already follow.
#:
#: **Distinct from `"none this phase"`** (§63.9 B2), which replaces the WHOLE
#: list when a phase engaged no metric at all. This marks ONE entry inside a
#: list the phase does carry, which is why the keyed trail stays unbroken.
NOT_ADDRESSED = "not addressed this phase"


def define_phase_metrics(artifacts: dict) -> list[dict]:
    """Define's `phase_metrics`, DERIVED from what the Belt already stated.

    **§39.1.9 — one entry per registry metric, assembled deterministically
    immediately before the `{Phase}Output` is constructed, with no model call.**
    Five keys: `name` and `unit` verbatim from `metric_definitions` (§63.8 B2 —
    the registry name is a matching KEY, not prose), `baseline_estimate` and
    `target_value` from the captured fields of the same names, and
    `source: "stated"`, because Define states rather than measures.

    **THE SINGLE-AUTHORITY INVARIANT NOW HOLDS BY CONSTRUCTION, AND THAT IS THE
    POINT RATHER THAN A SIDE EFFECT.** S-F28 B2 exists because two stores of one
    number drift invisibly. Deriving the entry from the scalars removes the
    second author instead of detecting it: there is no value here that anything
    else authored. **For Define the invariant becomes a tautology** — it still
    guards Measure and Control, whose entries are captured rather than derived,
    and a Define-specific drift test would now be testing something that cannot
    happen. Said out loud so nobody writes that test and reads its green as
    evidence.

    **The FIRST emitted entry is the primary**, because `core.metrics.primary_entry`
    defines the primary as the first entry carrying a name, and it is the only
    one the invariant mirrors. Define captures ONE `baseline_estimate` and ONE
    `target_value` (§39.1.2), so only the first entry can carry them; any further
    registry metric gets its `name` and `unit` with both scalars set to
    **`"not addressed this phase"`** — the marker Analyse (§39.3.3) and Improve
    (§39.4.3) already write into an entry they carry but did not act on.
    **Founder ruling 2026-09-23**: an empty string would have been a third
    convention for one fact, and one grader reads all three phases.

    **`"none this phase"` is NOT written here and the branch is deliberately
    absent.** §63.9 B2 offers it to a phase that engaged no metric; Define's
    `baseline_estimate` and `target_value` are both gate-required (§39.1.2,
    Option A), so a Define gate that reaches assembly has always engaged one. A
    branch that cannot fire is the unfireable-check class this project keeps
    paying for — so if the registry is empty, this returns `[]` and S-F28 B3
    raises with the message it already has: *the value cannot be traced to a
    registry metric*. That is the correct outcome, not a gap.

    Scalars are coerced with `str` per §63.9 B5 — the dict is §7's exception,
    its values are not.
    """
    registry = artifacts.get("metric_definitions") or []
    if not isinstance(registry, list):
        return []

    entries: list[dict] = []
    for metric in registry:
        if not isinstance(metric, dict):
            continue
        name = str(metric.get("name") or "").strip()
        if not name:
            continue                    # §63.8 B1 — an unnamed metric is not a key
        primary = not entries
        entries.append({
            "name": name,
            "unit": str(metric.get("unit") or ""),
            "baseline_estimate": (
                str(artifacts.get("baseline_estimate") or "") if primary
                else NOT_ADDRESSED),
            "target_value": (
                str(artifacts.get("target_value") or "") if primary
                else NOT_ADDRESSED),
            "source": DEFINE_METRIC_SOURCE,
        })
    return entries


def assemble_define_gate_document(
    artifacts: dict,
    citations: list[dict],
    uploads: list[dict],
    acknowledged_gaps: list[str] | None = None,
) -> DefineOutput:
    """Construct Define's gate document from captured values (S-F28).

    **Define is the one phase with no Tier 2** (Option A, §39.1.2), so every
    content field is a direct `artifacts[...]` access and the
    `.get(..., "")` pattern never appears here. Sixteen direct accesses: the
    thirteen coached elements plus the three fields captured inside a
    position, which are gate-required and therefore read the same way.

    `phase_metrics` is the ONE `.get()` in this assembly and it is **not** a
    Tier 2 access — it defaults to `[]` because a phase may legitimately engage
    no metric, in which case §63.9 B2 requires `"none this phase"` to be
    written into it rather than the field being absent.

    `acknowledged_gaps` is **always empty for Define**: nothing is skippable,
    so nothing can be acknowledged as skipped. It stays on the schema for
    cross-schema uniformity (§40).
    """
    # §39.1.9 — derived HERE, immediately before construction, and folded into
    # the artifacts the invariants run against. `build_gate_document` calls
    # `assert_single_authority(phase, artifacts)` (S-F28 B1), so an entry that
    # existed only in `values` would be invisible to the check it exists to
    # satisfy.
    phase_metrics = define_phase_metrics(artifacts)
    artifacts = {**artifacts, "phase_metrics": phase_metrics}

    values = {
        # The 13 gate-required elements, in coached order (R4)
        "business_case": tier_1(artifacts, "business_case"),
        "team": tier_1(artifacts, "team"),
        "voc_summary": tier_1(artifacts, "voc_summary"),
        "problem_statement": tier_1(artifacts, "problem_statement"),
        "baseline_estimate": tier_1(artifacts, "baseline_estimate"),
        "project_scope": tier_1(artifacts, "project_scope"),
        "goal_statement": tier_1(artifacts, "goal_statement"),
        "target_value": tier_1(artifacts, "target_value"),
        "target_date": tier_1(artifacts, "target_date"),
        "benefits_analysis": tier_1(artifacts, "benefits_analysis"),
        "secondary_metrics": tier_1(artifacts, "secondary_metrics"),
        "process_map_sipoc": tier_1(artifacts, "process_map_sipoc"),
        "issues_and_barriers": tier_1(artifacts, "issues_and_barriers"),
        # Captured inside positions 3, 4 and 5 — gate-required
        "critical_to_quality": tier_1(artifacts, "critical_to_quality"),
        "problem_5w2h": tier_1(artifacts, "problem_5w2h"),
        "metric_definitions": tier_1(artifacts, "metric_definitions"),
        # On all five schemas (§63.9). DERIVED, never read back out of
        # `artifacts`: §39.1.9 makes this assembly the single author, so a
        # `phase_metrics` that arrived some other way is overridden rather
        # than trusted.
        "phase_metrics": phase_metrics,
        # Gate metadata (§40)
        "computation_results": artifacts.get("computation_results", []),
        "acknowledged_gaps": list(acknowledged_gaps or []),
        "citations": citations,
        "uploads": uploads,
    }
    return build_gate_document(DefineOutput, "define", artifacts, values)
