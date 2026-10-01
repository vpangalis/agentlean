# ADR-0074: An upload is judged against the current element when it is interpreted

Status: ACCEPTED (founder, 2026-10-01)
Requirements: W5 (uploads strengthen answers), DEF-108
Depends on: ADR-0067 (labelled data blocks; instructions in the system message), G-145 (every upload makes the
next turn an upload turn), G-146 (read status kept)

## Context

W5: "the coach reads it, checks it against the current element's acceptance criteria and asks for what is
missing, naming the file (and page, where it has pages); nothing from an upload is stored until the Belt confirms
it." Since G-145 every upload reaches the coach on the next turn. But on a read-back turn the coach model left the
file out on both live runs, whether the file instruction came first or last. Asking the coach model to do a
read-back AND a file check in one structured reply is unreliable, the same pattern as G-139: one call carrying two
duties.

Every upload already has one model call of its own: the interpretation call (system message = instructions, user
message = the labelled file text, per G-143's fix).

## Decision

1. The interpretation call also judges the file against the **current element's acceptance criteria** (the element
   the planner is working on when the file arrives). Its structured output gains one field, for example
   `element_check`: for each criterion of that element: `supported` / `contradicted` / `not_covered`, with the
   file's page or section where it has one, plus a short list of what is still missing.
2. On the upload turn, **code** builds the file part of the reply from `element_check`: it names the file, says
   which criteria the file supports and what is still missing, and asks for the missing part. The coach model
   writes the rest of its reply as usual; it is no longer responsible for the file part.
3. Nothing from the file is stored by this. Values the file suggests still go through the normal read-back and the
   Belt's Confirm (T6).
4. If the planner's current element changes before the upload turn runs, code re-runs the check against the new
   element (one call), or, if the turn's budget doesn't allow it, says that the file was checked against the earlier
   element and names it.
5. The check is recorded in `step_log` with the file, the element and the per-criterion result.
6. The interpretation call keeps ADR-0067's structure: instructions and criteria in the system message, file text
   only in the labelled data block.

## Consequences

- W5 is met deterministically: the file is always named, and the criteria check always appears.
- No extra model call per turn; T69 (4 coach calls) is unaffected. The interpretation call's output grows slightly.
- The interpretation schema changes. It is part of the upload record, not phase state; if it is persisted in a
  checkpoint or the Store, ADR-0065 versioning applies (version + migration; old records get `element_check = null`).
- DEF-108's test: after an upload, the reply contains the file name and the per-criterion result from
  `element_check`; the live run-through checks the same.

## Rejected

- **B. A separate judgment call on the upload turn.** Uses one of T69's 4 calls and squeezes the coach.
- **C. A new "upload" coaching move.** Changes the move set; more design for the same outcome.
- **D. Accept the code-written file line only.** Names the file but never checks it against the criteria, so W5
  would have to be weakened.
- **Leave it to the coach model's prompt.** Tried twice live (instruction first and last); unreliable.

## Verification

- Unit: the interpretation output carries `element_check` for the current element's criteria; the upload turn's
  reply includes the file name and the per-criterion result built in code.
- Unit: the element changes before the upload turn → re-check or explicit "checked against <element>".
- Live: one run-through with an upload; DEF-108 passes; M1 46/46; under USD 1.50.
