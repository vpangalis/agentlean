# ADR-0077: Calculations are run by code, never by the coach; the coach explains them

Status: ACCEPTED (founder, 2026-10-11; drafted by Claude Code from the ruling)
Requirements: R4 (the thirteen elements; the benefits analysis carries the expected saving), R2 (the coach
teaches), §43.1 (the seven-step computation pattern); DEF-016, DEF-017
Depends on: ADR-0069 (tools per turn type), ADR-0071 (numbers read in code from the Belt's words),
ADR-0001 (the coaching move is decided in code)
Defects: G-151 (the coach can never run a calculation), G-100 (a percent read 100× too large)
Applies to: Define now; Measure, Analyse, Improve and Control as their calculations are built.

## Context

Each phase has computation tools (`knowledge/computation.py`, `COMPUTATION_TOOLS_BY_PHASE`) and §43.1
expects the coach to teach, run and interpret them. Since ADR-0069 a turn offers tools by its type —
teaching: lookups, `propose_template`, `load_skill`; upload: the evidence tools; answer: none — and no type
offers a computation tool. So the coach can never call one: on live run 132032 the benefits analysis was
confirmed with a figure the scripted Belt typed, and `computation_results` stayed empty (G-151). Separately,
`calculate_expected_savings` read "23%" as 23 and returned a saving 100× too large (G-100).

Three ways were put to the founder: a calculation turn type offering the tool to the coach; code runs the
calculation; move the features later.

## Decision

1. **Code runs every calculation; the coach is never offered a computation tool.** A calculation is
   deterministic arithmetic over values the Belt gave; running it is not a judgment.
2. **Inputs, in this order.** An input that is already a confirmed value in the case is read by code from
   state. An input not yet confirmed is extracted by the planner's one judgment call (structured output,
   `SufficiencyJudgment.calculation_inputs`), from the Belt's words — nothing is invented; an input not
   stated stays missing and nothing is calculated.
3. **When every input is present, code runs the tool** and records it in `computation_results` with its
   five keys (`tool`, `inputs`, `result`, `turn`, `phase`). The figure is never retyped by the coach.
4. **The read-back shows the figure with one line, written in code, on how it was calculated** — the
   multiplication with the Belt's own numbers. The value is stored, as always, only when the Belt confirms.
5. **The coach explains; it does not calculate.** The teaching turn of an element with a calculation
   teaches what the calculation is and why, before any figure appears (§43.1 step 1, DEF-016).
6. **One percent convention for rates** (G-100): a baseline or target rate given as "23%", "23" or "0.23"
   is the same rate, 0.23, in the expected-savings calculation.
7. The calculations of the other phases follow this ADR as they are built.

## Consequences

- `SufficiencyJudgment` gains `calculation_inputs` (a state schema change under ADR-0065: version raised,
  no-op migration). The judgment prompt asks for the inputs of the current element's calculation only.
- The computation tools stay registered (`COMPUTATION_TOOLS_BY_PHASE`) and are run by code; no turn type
  offers them, as ADR-0069 already has it.
- `computation_results` is filled by code; the gate document and the report read it as before.

## Rejected

- **A calculation turn type offering the tool to the coach.** A model choosing whether and how to call an
  arithmetic tool adds a failure mode (the call not made, wrong arguments) for no judgment gained.
- **Move DEF-016 and DEF-017 later.** The pilot would carry savings figures nothing computed.

## Verification

- Route test: at the benefits analysis, with the baseline and target confirmed, the Belt states the cost
  per defect and the yearly volume; the read-back carries the figure and its one-line calculation;
  `computation_results` holds one row with five keys; the confirmed report shows the saving.
- "23%", "23" and "0.23" give the same saving.
- Live: the run-through's benefits analysis carries a calculated saving.
