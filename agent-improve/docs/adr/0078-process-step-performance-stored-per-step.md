# ADR-0078: The as-is process stores its performance per step, and the problem is located in it

Status: ACCEPTED (founder, 2026-10-12; drafted by Claude Code from the ruling)
Requirements: R17 (the as-is process with its performance; open decision 6 closed as written), R18 (the problem is
located in the process), C6 (carried forward in structure); DEF-084, DEF-085
Depends on: ADR-0071 (MetricValue, the one parser), ADR-0065 (state schema versioning), ADR-0066 (the phase
record), ADR-0001 (the coaching move is decided in code)

## Context

Element 12, the high-level process (`process_map_sipoc`), stores six SIPOC columns; `process_steps` is the
Belt's text ("Receive → Approve → Pay"). R17 adds how the process performs today — per step: average, minimum
and maximum duration with a unit, how often it runs per period, the problems the team sees there and who said
so; for the whole process: end-to-end lead time and runs per period. Values may be estimates in Define. R18
links the problem statement to the steps where the problem shows, checked both ways before either element is
confirmed. Measure (C6) needs these as numbers, per step, to replace with measured data.

## Decision

1. **Each process step is an entry with a stable id**, inside `process_map_sipoc["process_steps"]`:

   | Key | Meaning |
   |---|---|
   | `id` | `S1`, `S2`, … — given in code; a step keeps its id when the SIPOC is changed (matched by name), a new step takes the next free number |
   | `name` | the step in the Belt's words |
   | `duration` | `{avg, min, max}`, each a MetricValue (ADR-0071) with a time unit and `is_estimate` |
   | `runs_per_period` | a MetricValue whose unit is the period ("per day", "per week", "per month") |
   | `problems` | `[{note, said_by}]` — the team's own words and who said them |

2. **The whole process** is one more key, `process_map_sipoc["process_performance"]`:
   `{lead_time, runs_per_period}`, both MetricValues. It is not a step and does not repeat one.
3. **Numbers are read in code.** The coach proposes each figure as the Belt's words; the read-back's store is
   built by code, every duration and frequency through the one parser (`parse.metric_value`, ADR-0071 point
   2). A figure with no number stays as words (`value` None) and is asked again; nothing is guessed.
   `is_estimate` is set from the Belt's words as ADR-0071 defines it; Measure replaces estimates.
4. **The problem names its steps.** The problem statement's 5W2H carries `steps`: the step(s) where the problem
   shows, in the Belt's words. The Define skill instructs the coach to ask for them actively (R18).
5. **The link is checked in code at read-back, both directions.** When the SIPOC is read back after the problem
   statement was confirmed, or the problem statement after the SIPOC (a change): (a) a step the problem names
   that matches no step, or a matching step with no problem notes; (b) a step with problem notes that the
   problem statement does not name. A mismatch turns the read-back into a challenge naming it, once; when the
   Belt answers again with the same mismatch, the read-back goes ahead and names what the Belt kept. Names are
   matched in code (case and punctuation ignored; one contains the other, or they share a word of five or more
   letters).
6. **Schema change under ADR-0065.** The state schema version is raised and a migration turns a stored
   SIPOC's text `process_steps` into step entries (split on arrows, commas, semicolons and new lines; ids in
   order; no performance) wherever state carries a Define SIPOC (`artifacts`, `final`, `draft`, the Store's
   case record and Define document). A phase record inside a message is not migrated (as under ADR-0071); the
   readers accept the old text form and read it as step entries the same way.

## Consequences

- `parse` gains the step reader and the period reader; `moves.pending_store` builds the SIPOC through them.
- The SIPOC's six columns and `missing_columns` are unchanged: `process_steps` is filled when it holds a step.
- The SIPOC diagram draws step names; the Define report and screen read the entries.
- The run-through's scripted Belt gives per-step performance, problems and the whole-process figures.

## Rejected

- **A separate `step_performance` key beside the SIPOC.** No concrete technical reason requires it: the step
  entry with an id carries its performance where it is read, and a parallel list keyed by name could drift
  from the steps it describes (founder, 2026-10-12).
- **Durations as text.** Measure could not compare them with measured data (C6, as ADR-0071).
- **The R18 check as a judgment criterion.** A model would decide a deterministic comparison of two lists.

## Verification

- Route test: the Belt gives the SIPOC with per-step performance and problems; the confirmed value holds step
  entries with ids, MetricValues (estimates marked) and `process_performance`; a changed SIPOC keeps ids.
- Route test: a problem naming a step without problem notes, and a step with problems the statement ignores,
  each turn the read-back into a challenge naming the step; answered again, the read-back goes ahead.
- Migration test: a version-7 SIPOC with text steps loads as step entries.

## Notes

Note (founder, 2026-10-22): point 5's matching, for a "from → to" location (DEF-211, finding 61): code finds the start step and the end step, takes every step between, and reads them back in code ("The problem occurs in steps 1–5: is that right?") for one Confirm, with Change as usual; an end step not found makes the coach ask which step it starts or ends at. No ticking and no new screen interaction. The flow's located and flagged marks follow from it.
