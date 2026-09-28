# ADR-0064 — The as-is process carries its performance, and the problem points at its steps

Status: ACCEPTED (founder, 2026-09-28) · Requirements: R17, R18, C6

## Context
R17 asks Define to capture, per process step, duration (average, minimum, maximum, unit),
frequency and the team's problem notes with who said them, plus end-to-end lead time and runs per
period. R18 asks the problem statement to name the step(s) where the problem shows and the coach
to check the link both ways. Today `process_map_sipoc.process_steps` holds step names only and
`problem_statement` is one string. Measure and Improve need these values in structure (C6).

## Decision
1. `DefineOutput.process_map_sipoc` keeps its six keys; `process_steps` becomes a list of step
   dicts, and a new key `process_performance` holds the whole-process values:
   ```
   process_steps: [{ "name": str, "duration_avg": str, "duration_min": str, "duration_max": str,
                     "duration_unit": str, "frequency": str, "frequency_period": str,
                     "problems": [{ "note": str, "said_by": str }], "estimate": "yes"|"no" }]
   process_performance: { "lead_time": str, "lead_time_unit": str, "runs_per_period": str,
                          "period": str }
   ```
   All values strings (ADR-0016). `estimate` marks values Measure must replace with data.
2. `DefineOutput` gains `problem_steps: list[str]` — step names from `process_steps`.
   `problem_statement` stays the Belt's sentence.
3. R18's check is deterministic first: every name in `problem_steps` exists in `process_steps`,
   and every step with problem notes is either named in `problem_steps` or explicitly accepted by
   the Belt as secondary. The coach raises a mismatch before either element is confirmed; the
   Define SKILL.md tells the coach to ask for times, frequency and problems per step.
4. Measure's input mapper reads these from the Store to seed `detailed_process_map` and marks
   estimates to verify; Improve compares its to-be steps by `name`.
5. The Define report's section 6 shows the SIPOC table and flow with step times, frequency and the
   problem steps highlighted (R5).

## Consequences
A schema change: `phases/define/schema.py`, gate assembly, the report, the skill and their tests;
§4.2 regenerates. Rework risk high — it goes before the report layout (C1/C2/R5).

## Rejected
Performance as free text (Measure cannot read it); a separate element (R4 fixes thirteen).
