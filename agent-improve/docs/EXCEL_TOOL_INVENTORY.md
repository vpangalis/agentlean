<!--
Document: agent-improve/docs/EXCEL_TOOL_INVENTORY.md
Created:  2026-08-25
Purpose:  Preserve the LSS tools-suite sheet inventory as the build-inventory
          for the §30 computation layer, after the workbook was removed from
          improve_knowledge_index.
Status:   Reference material. NOT binding, NOT a schema, NOT an amendment.
          The canonical computation-tool list is AGENTIC_ARCHITECTURE_REFERENCE.md §30.
-->

# LSS tools-suite inventory

## Why this file exists

`Lean-Six-Sigma Tools suite_20220912.xlsb` was removed from
`improve_knowledge_index` in the 2026-08-25 corpus rebuild. Its 21 sheets
carried only thin tool descriptions plus example data — redundant against the
eBook's far richer coverage of the same tools, and their example-number rows
acted as retrieval attractors.

**`EXCEL_SHEET_TOOL_MAP` was preserved rather than deleted with it.** The
sheet-to-phase mapping is a *spec* — the inventory of the tools the workbook
covered, and the closest thing to a source list for the §30 computation layer.
It is not corpus content, and it had no business living in an ingestion
script, which is why it moved here rather than staying there.

**This file is reference material, not a rule.** It does not amend §30, it does
not bind on any implementation, and the twenty computation tools in
`AGENTIC_ARCHITECTURE_REFERENCE.md` §30 remain canonical. What it does is stop
the inventory being lost, and record what fell out of comparing the two lists.

## The 21 sheets

Phase assignments are the workbook's own, as they were encoded in
`EXCEL_SHEET_TOOL_MAP`. The `Content` sheet was an index page and was never
ingested.

| # | Sheet | Workbook phase | Tool |
|---|---|---|---|
| 1 | `5W2H - Problem Statement` | define | 5W2H |
| 2 | `Data Collection plan` | measure | Data Collection Plan |
| 3 | `Histogram` | measure | Histogram |
| 4 | `Process capability index` | measure | Process Capability Cpk |
| 5 | `Normality Test` | measure | Normality Test |
| 6 | `MSA Long Method` | measure | MSA Measurement System Analysis |
| 7 | `Pareto` | analyse | Pareto Analysis |
| 8 | `Correlation and Regression` | analyse | Correlation and Regression |
| 9 | `Box Plot` | analyse | Box Plot |
| 10 | `5 Why drill down` | analyse | 5Why Drill Down |
| 11 | `Cause & Effect Matrix` | analyse | Cause and Effect Matrix |
| 12 | `Fishbone Diagram` | analyse | Fishbone Diagram |
| 13 | `Y2X Matrix` | analyse | Y2X Matrix |
| 14 | `Spider chart` | improve | Spider Chart |
| 15 | `Value analysis` | improve | Value Analysis |
| 16 | `Line Balancing` | improve | Line Balancing |
| 17 | `Impact & Effort Matrix` | improve | Impact and Effort Matrix |
| 18 | `Hoshin Kanri` | improve | Hoshin Kanri |
| 19 | `Control chart` | control | Control Chart |
| 20 | `I-MR Chart` | control | I-MR Chart |
| 21 | `DPO and Z calculator` | control | DPO and Z Calculator |

## How the inventory lines up against §30

**The two lists are not the same kind of thing, and reading them as rivals
would be a mistake.** §30's twenty are *computation* tools — pure functions
returning numbers. The workbook's twenty-one are *methodology* tools, and most
of them are templates, matrices or charts rather than calculations. The overlap
is where a sheet did arithmetic.

| Sheet | Nearest §30 tool |
|---|---|
| `Process capability index` | `calculate_cpk` |
| `MSA Long Method` | `calculate_grr` |
| `Correlation and Regression` | `pearson_correlation`, `linear_regression` |
| `Control chart` | `xbar_r_chart_limits` |
| `I-MR Chart` | `imr_chart_limits` |
| `DPO and Z calculator` | `calculate_dpmo`, `calculate_sigma_level` |

The remaining fifteen sheets have no computation-tool counterpart, and for most
of them that is correct by design rather than a gap:

- **Templates and framing tools** — `5W2H`, `Data Collection plan`,
  `Hoshin Kanri`, `Impact & Effort Matrix`, `Value analysis`. These are served
  by `propose_template` (§29), not by a calculation.
- **Diagrams** — `Histogram`, `Pareto`, `Box Plot`, `Fishbone Diagram`,
  `Spider chart`. Served by `propose_diagram`, which returns structured JSON
  the frontend renders (§29). A chart is not a computation tool.
- **Matrices that became schema fields** — `Cause & Effect Matrix` and
  `Y2X Matrix` are both captured as `xy_matrix_summary`, a Tier 1 Measure field
  (CLAUDE.md §9.7), with `vital_few_xs` carrying the output.
- **`5 Why drill down`** — a coaching sequence, held in the Analyse SKILL.md.
- **`Line Balancing`** — Lean rather than Six Sigma; no §30 tool, and none of
  the five phases binds one.

## Two observations, recorded rather than acted on

Both came out of the comparison above. **Neither is an amendment and neither
has been actioned** — they are noted here so that whoever builds
`knowledge/computation.py` meets them deliberately rather than rediscovering
them.

**1. `Normality Test` has no counterpart among the twenty.** It is the one
workbook sheet doing real statistics with no §30 tool behind it. It is also
load-bearing for the Measure phase as CLAUDE.md §10.8 describes it: capability
is assessed after stability, and a capability figure assumes a distribution
whose shape nobody has checked without one. Whether that warrants a
twenty-first tool is a §56 question, not a build decision — Measure already
sits at 15 tools against a ceiling of 16 (§30), so adding one there consumes
the last slot.

**2. The workbook files DPO/Z under `control`; §30 files the equivalent tools
under Measure.** `calculate_dpmo` and `calculate_sigma_level` are both Measure
tools in §30, and the workbook's sheet is tagged `control`. **§30 is right and
the workbook is the outlier** — sigma level and DPMO are baseline
characterisation, which is Measure's job; Control re-measures via
`post_improvement_cpk`. Recorded only so the discrepancy is not mistaken for a
missing Control tool later.

## Provenance

The map was `EXCEL_SHEET_TOOL_MAP` in `scripts/ingest_knowledge.py` until
2026-08-25. In that script it assigned an explicit `phase_relevance` to each
sheet at ingest time — deliberately bypassing the keyword classifier, because
a sheet's phase was known rather than inferred. That role ended with the
workbook's removal from the corpus; the inventory is all that survives, and it
survives as a spec.

The workbook itself remains at `data/knowledge/Lean-Six-Sigma Tools
suite_20220912.xlsb`. It is not deleted — it is simply not ingested, and
`SOURCE_ALLOWLIST` in the ingest script keeps it that way.
