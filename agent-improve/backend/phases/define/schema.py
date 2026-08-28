"""Define phase gate document.

ARCHITECTURE.md §39.1 · §40 · §63.1 (S-C27) · CLAUDE.md §10.7, §10.8, §2.

**This file is one third of an atomic unit** (§56.1). `schema.py` owns the field
names, types and shape; `validate.py` owns which of them block the gate; and
`skills/dmaic-define-phase/SKILL.md` coaches those exact names in the §39.1.2
order. **They are rebuilt together or not at all.** A mismatch does not fail
loudly — capture writes `artifacts["x"]`, `DefineOutput(**artifacts)` has no
`x`, and the gate raises on a Belt who has done nothing wrong, one phase later.

**Define uses Option A — all 12 fields are gate-required, with no Tier 1 /
Tier 2 split** (ratified 2026-08-26; §39.1.2). This supersedes the 8/3 split of
2026-08-25 **for Define only** — the other four phases keep their tiers, each
settled at its own phase review. Two consequences follow and both are load-
bearing: `DEFINE_REQUIRED_FOR_GATE` is the whole coached list, and **there is no
`acknowledged_gaps` path out of Define** because no field is skippable.

**Declaration order IS the coached order** (§39.1.2). With no tiers to group by,
the schema order and the `field_index` sequence are one list rather than two.

Classes live here by §2 — `phases/{phase}/schema.py` is one of the named files
where Pydantic models are permitted.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# ── The 12 fields that BLOCK the gate — all of them ────────────────────
# §35, §39.1.2. Option A: every Define field is gate-required, so this list is
# also `DEFINE_FIELD_ORDER` below. Layer 2b checks presence deterministically —
# no LLM. `validate.py` imports this list; it is not duplicated there.
#
# Ordered as coached. A field's position here is its `field_index`.
DEFINE_REQUIRED_FIELDS: tuple[str, ...] = (
    "business_case",        # 1
    "team",                 # 2
    "voc_summary",          # 3
    "problem_statement",    # 4  composed from 5W2H (§39.1.3)
    "baseline_estimate",      # 5  discrete — Control compares against it
    "project_scope",        # 6
    "goal_statement",       # 7  the human-readable SMART sentence
    "target_value",        # 8  discrete — Control compares achieved-vs-target
    "target_date",          # 9  the PLANNED completion date
    "secondary_metrics",    # 10 what could get worse
    "process_map_sipoc",    # 11
    "issues_and_barriers",  # 12 always last
)

# The order the coach walks and the planner indexes with `field_index`
# (§39.1.2 — this list closed G-38). Under Option A it is the same list as
# DEFINE_REQUIRED_FIELDS: nothing is coached that does not block the gate, and
# nothing blocks the gate that is not coached. `secondary_metrics` is coached
# at position 10 rather than assembled silently — the earlier build left it out
# of the walk while §40 still required it on all five schemas.
#
# The four gate-metadata fields are assembled at `gate_apply`, never coached,
# so they are absent here by design.
DEFINE_FIELD_ORDER: tuple[str, ...] = DEFINE_REQUIRED_FIELDS

# `metric_definitions` is the project's METRIC REGISTRY (§63.8, S-C38) — the
# canonical set of metrics the whole project is traced by. It is gate-required
# but it is NOT a thirteenth coached position: the Belt names their metrics
# inside position 5's conversation (`baseline_estimate`), because "what are we
# measuring, in what units" and "what is it at today" are one exchange, not two.
#
# **The 12-position coached walk of the Option A finalization is unchanged.**
# `field_index` still indexes DEFINE_FIELD_ORDER above; only the gate list grows.
DEFINE_REQUIRED_FOR_GATE_FIELDS: tuple[str, ...] = DEFINE_REQUIRED_FIELDS + (
    "metric_definitions",
)

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


class DefineOutput(BaseModel):
    """Gate document for the Define phase — 18 fields.

    **12 content fields, all gate-required (Option A) · `metric_definitions`,
    the registry, also gate-required · `phase_metrics` · 4 gate metadata**
    (§40, §63.1). Thirteen block the gate; twelve are coached. No tier split —
    see the module docstring.

    *(This read "16 fields" until 2026-08-28 — the count from before the metric
    registry landed at ARCHITECTURE.md v1.15, which added `metric_definitions`
    and `phase_metrics`. §40 and §63.1 have said 18 since. Corrected against
    `DefineOutput.model_fields`, which is 18.)*

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

    # ── The 12 gate-required fields, in coached order (§39.1.2) ───────
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
            "need, including what they complain about most."
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

    # ── The metric registry — Define owns it (§63.8, S-C38) ──────────
    metric_definitions: list[dict] = Field(
        ...,
        description=(
            "THE PROJECT'S METRIC REGISTRY. One entry per metric the project "
            "tracks: {name, unit, meaning}. `name` is the stable traceability "
            "key — written identically in every phase, and what the grader "
            "matches on to follow a metric across the five gate documents. "
            "Gate-required, but captured inside position 5's conversation "
            "rather than at a thirteenth coached position (§39.1.2)."
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
