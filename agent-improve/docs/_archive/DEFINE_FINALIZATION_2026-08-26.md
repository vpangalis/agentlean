> ## ⚠ SUPERSEDED on the baseline field name
>
> **This document states the rename as `baseline_metric` → `baseline`. The
> ratified direction is the reverse — `baseline` → `baseline_metric`** — per
> `CONTINUITY.md` v4.2 §5 and commit `c7663ca`.
>
> **Re-applying this document's rename instruction verbatim would re-introduce
> the `baseline` / `baseline_mean` collision** that reversal exists to resolve.
>
> **Kept as historical record only. Do not execute its rename instruction.**
> Everything else in this document — the 12 required fields, Option A, the
> measurement-thread rationale — stands and was applied at commit `885defc`.

# Define phase — FINALIZATION (all fields required, no tiers)

**Date: 2026-08-26. Supersedes the Tier 1/Tier 2 split for Define only.**
**Ratified rulings this closes:**
- **Option A for Define:** all Define fields are gate-required. No Tier 1 / Tier 2 distinction in Define. Missing any field → gate fails.
- Tier 1/Tier 2 **remains** for the other four phases, decided at each phase's review (Measure keeps an optional path for MSA per prior ruling).
- `baseline`, `target_metric`, `target_date` are **discrete required fields**, not folded into `goal_statement` — they are the machine-readable values Control compares against (the measurement thread). Removing them would break Control's target-vs-actual comparison.

**This is a consistency finalization: §39.1, §40/S-C27, §35, and every count mention are reconciled to one answer. It also resolves the live §39.1-vs-§40 contradiction (they disagreed on whether `team`/`baseline` are gate-required).**

---

## The authoritative Define field list — 12 REQUIRED fields, no tiers

| # | Field (`artifacts` key) | Type | Notes |
|---|---|---|---|
| 1 | `business_case` | str | Strategic rationale / quantified impact (COPQ). |
| 2 | `team` | list[dict] | `{name, role, function}` per member (§39.1.4). |
| 3 | `voc_summary` | str | Customers + their needs. |
| 4 | `problem_statement` | str | One SMART statement, composed from 5W2H coaching (§39.1.3). |
| 5 | `baseline` | str | **Discrete** current-state value — Control compares against it. |
| 6 | `project_scope` | dict | `{in_scope, out_scope}`. |
| 7 | `goal_statement` | str | SMART sentence (human-readable). |
| 8 | `target_metric` | str | **Discrete** target value — Control compares achieved-vs-target. Not redundant with `goal_statement` (that is prose; this is the comparable value). |
| 9 | `target_date` | str (ISO) | **Planned** completion date — a project-management parameter. May slip without affecting the improvement logic. Distinct from Control's actual close date. |
| 10 | `secondary_metrics` | str | What could get worse — side-effect watch. |
| 11 | `process_map_sipoc` | dict | Six keys: suppliers, inputs, process_steps, outputs, customers, process_kpis. Partial map (fewer than six) = failure. |
| 12 | `issues_and_barriers` | str | Belt-stated blockers. "none identified at this stage" is a valid conscious answer. |

**Gate rule (Option A):** `DEFINE_REQUIRED_FOR_GATE` = **all 12**. The gate blocks until every field is populated and passes the quality rubric. There is no `acknowledged_gaps` path for Define — no field is skippable.

**Coaching order** (the planner's `field_index` sequence) = the order above: business_case → team → voc_summary → problem_statement → baseline → project_scope → goal_statement → target_metric → target_date → secondary_metrics → process_map_sipoc → issues_and_barriers.

> **The measurement thread (do NOT "simplify" these away):** `baseline`, `target_metric`, and Measure's/Control's paired fields are discrete on purpose. Define sets `baseline` (start) and `target_metric` (goal value); Control captures the achieved value and computes target-vs-actual. If these lived only inside `goal_statement` prose, Control could not extract and compare them. This mirrors the existing three-phase KPI thread (`process_map_sipoc["process_kpis"]` → `detailed_process_map["baseline_kpis"]` → `post_improvement_metric`, EARS B7).

---

## Edits required across the document (reconcile to the above)

### E1 — §40 / S-C27 `DefineOutput` (line ~7367–7404) — the schema itself

Rewrite the class and its header. Header: **"12 fields, all gate-required, plus 4 gate-metadata."** (No Tier 1/Tier 2 split.)

```python
class DefineOutput(BaseModel):
    """Gate document for the Define phase. All 12 fields gate-required (Option A)."""
    business_case:        str
    team:                 str      # rendered from list[dict] {name, role, function}
    voc_summary:          str
    problem_statement:    str
    baseline:             str      # discrete current-state value (Control compares)
    project_scope:        str      # in/out
    goal_statement:       str      # SMART sentence
    target_metric:        str      # discrete target value (Control compares)
    target_date:          str      # planned completion (PM parameter)
    secondary_metrics:    str
    process_map_sipoc:    dict     # 6 sub-fields
    issues_and_barriers:  str
    # Gate metadata (unchanged)
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []   # stays in schema; unused by Define
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

- **Rename `baseline_metric` → `baseline`.** Update every reference (lines 1777, 7306, and any other).
- **Delete the "Tier 1 / Tier 2" comment banners** inside the class — all fields are required.
- **EARS B1** (line 7402): change "block on all six Tier 1 fields" → **"block on all 12 required fields."**

### E2 — §35 table (line 3181) — the per-phase Tier list

The Define row currently lists 6 fields under "Tier 1." Replace with: **Define — all 12 fields required (no tier split; Option A).** List all 12. Remove the Define "Tier 1 = 6" count. Note in the table that Define is the one phase with no Tier 2 (the other four retain tiers).

### E3 — §39.1 (the Define amendment) — update the tier language

§39.1.2's table currently marks fields Tier 1/Tier 2 (8/2 or 8/3 depending on version). Replace the Tier column with **"required"** for all 12. Add the ruling note: "Define uses Option A — all fields gate-required, no tiers. Ratified 2026-08-26." Add `target_metric` and `target_date` to the list if the current §39.1.2 dropped them, with the measurement-thread rationale.

### E4 — All stale count mentions → "12 required fields"

| Line | Current | Change to |
|---|---|---|
| 3445 | "6 Tier 1 fields" | "12 required fields (no tiers)" |
| 4493 | "of Define's six Tier 1 fields, exactly one name matches v1" | "of Define's 12 required fields, [N] names match v1" (Claude Code sets N from the actual v1→v2 diff) |
| 7146 | "Define 6, Measure 7, …" | "Define 12 (all required), Measure 7, …" |
| 7372 | "15 fields — 6 Tier 1, 5 Tier 2, 4 gate" | "16 fields — 12 required, 4 gate metadata" |

### E5 — Gate-assembly sample (line ~7297) — `DefineOutput(...)` construction

Currently mixes Tier-1 direct assignment and Tier-2 `.get()`. Change so **all 12 fields are direct `artifacts["field"]` assignments** (none via `.get()` default) — under Option A every field is required, so none defaults to empty. `baseline_metric` → `baseline`; add `target_metric`, `target_date`, `secondary_metrics`, `team`, `business_case` as direct assignments.

### E6 — Forward note for Control (log, do not build)

Add to §66.7 (findings) or the Control stub: **Control needs `actual_close_date`** — the real project end date, paired with Define's planned `target_date` (target-vs-actual, same pattern as target_metric-vs-achieved). To be formalized at Control's phase review.

---

## Code alignment (Claude Code verifies against the actual files)

The document edits above make ARCHITECTURE.md internally consistent. Claude Code must then confirm the **code matches**:

- `phases/define/schema.py` — `DefineOutput` must be the 12-required-field version above (no tiers). If it was built to the old 6/5 split, rebuild it.
- `phases/define/validate.py` — `DEFINE_REQUIRED_FOR_GATE` = all 12 field names. If it lists 6 or 8, correct to 12.
- `skills/dmaic-define-phase/SKILL.md` — coaching order = the 12-field order; confirm `target_metric`, `target_date`, `secondary_metrics` each have a coaching block (add if the earlier skill omitted them).
- Confirm the three files share the 12-field vocabulary exactly (atomic-unit rule, §56).

---

## WATCH-register touch (already tracked, restated)

- **WATCH 7** unchanged: `orchestrate.py` still writes v1 names; Define gate non-functional until Step 4.1. This finalization is spec+schema alignment, NOT the orchestrator migration — that stays at 4.1.
- **WATCH 8** (CLAUDE.md stale figures): now includes "Define 6 Tier 1" → must become "Define 12 required." Still a §0.x rule-file amendment, still deferred to the WATCH-8 commit — do NOT edit CLAUDE.md in this pass (§56).

---

## INTENT HAND-OFF FOR CLAUDE CODE

> Read `agent-improve/docs/DEFINE_FINALIZATION_2026-08-26.md`. Apply edits E1–E6 to ARCHITECTURE.md so Define reads as **12 required fields, no Tier 1/Tier 2 split** everywhere (§40/S-C27, §35, §39.1, all count mentions, the gate-assembly sample). Rename `baseline_metric` → `baseline` throughout. Keep `baseline`, `target_metric`, `target_date` as discrete required fields (measurement-thread rationale). Then align the code: `phases/define/schema.py` (`DefineOutput` = the 12-field version, no tiers), `phases/define/validate.py` (`DEFINE_REQUIRED_FOR_GATE` = all 12), and `skills/dmaic-define-phase/SKILL.md` (12-field coaching order; add coaching blocks for any of the 12 the skill currently omits). Verify the three files share the 12-field vocabulary exactly. Do NOT touch `orchestrate.py` (WATCH 7, Step 4.1) or CLAUDE.md (WATCH 8, §56). Log the Control `actual_close_date` forward note (E6). Stage by name. Co-Authored-By: Claude <noreply@anthropic.com>.
