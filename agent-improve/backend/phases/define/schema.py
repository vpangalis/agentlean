"""Define phase gate document.

ARCHITECTURE.md §39.1 · §40 · §63.1 (S-C27) · CLAUDE.md §10.7, §10.8, §2.

**This file is one third of an atomic unit** (§56.1). `schema.py` owns the field
names, types and shape; `validate.py` owns which of them are Tier 1; and
`skills/dmaic-define-phase/SKILL.md` coaches those exact names in the §39.1.2
order. **They are rebuilt together or not at all.** A mismatch does not fail
loudly — capture writes `artifacts["x"]`, `DefineOutput(**artifacts)` has no
`x`, and the gate raises on a Belt who has done nothing wrong, one phase later.

**The coached order is §39.1.2, not the declaration order below.** Fields are
declared grouped by tier because that is how they are read; the planner walks
`field_index` over §39.1.2's sequence, which starts at `business_case` and ends
at `issues_and_barriers`.

Classes live here by §2 — `phases/{phase}/schema.py` is one of the named files
where Pydantic models are permitted.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# ── Tier 1: the eight fields that BLOCK the gate ───────────────────────
# §35, §39.1.2. Layer 2b checks presence deterministically — no LLM.
# `validate.py` imports this list; it is not duplicated there.
DEFINE_TIER_1_FIELDS: tuple[str, ...] = (
    "team",
    "voc_summary",
    "problem_statement",
    "baseline",
    "project_scope",
    "goal_statement",
    "process_map_sipoc",
    "issues_and_barriers",
)

# ── Tier 2: recommended; a gap is recorded, never blocking (§35) ───────
DEFINE_TIER_2_FIELDS: tuple[str, ...] = (
    "business_case",
    "target_date",
    "secondary_metrics",
)

# The order the coach walks and the planner indexes with `field_index`
# (§39.1.2 — this list closed G-38). `secondary_metrics` is NOT here: it is a
# schema field required on all five phases (§40), not part of Define's coached
# sequence. Gate-metadata fields are assembled, never coached, so they are
# likewise absent.
DEFINE_FIELD_ORDER: tuple[str, ...] = (
    "business_case",        # 1  Tier 2
    "team",                 # 2  Tier 1
    "voc_summary",          # 3  Tier 1
    "problem_statement",    # 4  Tier 1 — composed from 5W2H (§39.1.3)
    "baseline",             # 5  Tier 1
    "project_scope",        # 6  Tier 1
    "goal_statement",       # 7  Tier 1
    "target_date",          # 8  Tier 2
    "process_map_sipoc",    # 9  Tier 1
    "issues_and_barriers",  # 10 Tier 1 — always last
)

# The six SIPOC keys. Fewer than six filled is the partial-map failure the
# field exists to catch (§41): a Belt who maps steps 3-5 of a seven-step
# process produces a project that cannot show improvement, because the
# baseline never covered the whole thing.
SIPOC_KEYS: tuple[str, ...] = (
    "suppliers", "inputs", "process_steps", "outputs", "customers",
    "process_kpis",
)

# Both scope halves are required. What the project is deliberately NOT doing
# is what protects it from ballooning (§39.1.2 B4).
PROJECT_SCOPE_KEYS: tuple[str, ...] = ("in_scope", "out_scope")

# Each team entry carries all three (§39.1.4).
TEAM_MEMBER_KEYS: tuple[str, ...] = ("name", "role", "function")


class DefineOutput(BaseModel):
    """Gate document for the Define phase — 15 fields.

    8 Tier 1 · 3 Tier 2 · 4 gate metadata (§40, §63.1).

    Assembled ONCE, at `gate_apply`, by Pydantic construction over values
    already captured — **there is no LLM call in this path** (§20, §33).
    Tier 1 fields are read `artifacts["field"]` so a missing one raises: Layer
    2b should have blocked the gate, and reaching assembly without the field is
    a bug that must surface loudly. Tier 2 uses `.get(..., "")`, where an empty
    value records that the Belt consciously proceeded without it (§40.1).
    """

    # ── Tier 1 — gate-required (§39.1.2) ──────────────────────────────
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
    baseline: str = Field(
        ...,
        description=(
            "Rough current level of the problem, as the Belt states it. The "
            "rigorous baseline is Measure's job; this one anchors the goal."
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
            "SMART goal mirroring the problem — same metric, a target value "
            "and a date."
        ),
    )
    process_map_sipoc: dict = Field(
        ...,
        description=(
            "SIPOC with six keys: suppliers, inputs, process_steps, outputs, "
            "customers, process_kpis. `process_kpis` carries WHAT is measured "
            "— the first link of the three-phase measurement thread (§39)."
        ),
    )
    issues_and_barriers: str = Field(
        ...,
        description=(
            "Belt-stated blockers. Tier 1 in every phase (§40). 'none "
            "identified at this stage' is a valid conscious answer; silence "
            "is not."
        ),
    )

    # ── Tier 2 — rubric-recommended (§35) ─────────────────────────────
    business_case: str = Field(
        default="",
        description="Strategic rationale — why the project is worth investing in.",
    )
    target_date: str = Field(
        default="",
        description=(
            "Project completion target, ISO format. The single date field — "
            "`estimated_completion_date` is retired as a duplicate (F-11)."
        ),
    )
    secondary_metrics: str = Field(
        default="",
        description=(
            "What could get worse. On all five schemas alongside "
            "`issues_and_barriers` (§40)."
        ),
    )

    # ── Gate metadata — same four on all five schemas (§40) ───────────
    computation_results: list[dict] = Field(default_factory=list)
    acknowledged_gaps: list[str] = Field(default_factory=list)
    citations: list[dict] = Field(default_factory=list)
    uploads: list[dict] = Field(default_factory=list)
