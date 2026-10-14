# ADR-0086: The target value and date are read from the confirmed goal, for one Confirm

Status: ACCEPTED (founder, 2026-10-13, A8; drafted by Claude Code from the ruling)
Requirements: R4 (the thirteen elements); DEF-171
Depends on: step 6.61 (the move decided in code; a read-back's value is pending until confirmed), ADR-0071
(the baseline and the target are MetricValues parsed in code), G-120 (a target judged in code), ADR-0070
(the target's chart on its read-back)

## Context

The goal (element 7) usually states the target already: "Reduce the late payment rate from 23% to under 5%
by 31 March 2027." Elements 8 (target value) and 9 (target date) then teach and ask again for what the
Belt has just confirmed — two more teach turns, two more answers, two more Confirms. A8, among the founder's
actions on the labelled turns, was ruled on 2026-10-13: the goal confirmed → the target value and date
parsed in code → one Confirm stores both; a missing part is taught; Change falls back to teaching.

## Decision

1. When the goal's Confirm advances to the target value (or the target date), the planner parses the
   confirmed goal in code (`define/parse.py::goal_targets`, `moves.from_goal`): the target value is the
   goal's last figure read as a limit after any baseline figure, accepted only as G-120 accepts a typed
   target — in the baseline's unit and different from the baseline; the target date is the date phrase as
   the goal writes it (ISO, "31 March 2027", "March 31, 2027", "March 2027").
2. What it finds is a pending read-back of that position, as if the Belt had answered with the goal's
   words: the goal's store turn ends with it, written in code (`nodes_common._goal_target_reply`, no model
   call, no sample), shown as a read-back of the target value with its chart not yet confirmed.
3. One Confirm stores both the target value and the target date and moves past the date; a goal with a
   value and no date reads back the value alone and the date is taught next; a goal with no value that
   counts is taught as before.
4. Change on this read-back teaches the target as usual; a typed answer is judged as one.

## Consequences

- A Define walk is two Belt turns and two model calls shorter when the goal states its target.
- The store turn of the goal makes no coach call (the reply is written in code).
- No state field changes: the read-back is a pending record of the existing `field_status`.

## Rejected

- **The coach writes the read-back**: the values would be the model's reading of the goal; the parser
  already decides the target in code (G-120, ADR-0071).
- **Folding the target into the goal element**: changes the thirteen elements (R4) and the gate document.

## Notes

Note (founder, 2026-10-14): relative targets are never read as the target value — "from 23% by 30%", "halve
the rate", "reduce by 5 points": a figure counts only when a target word introduces it ("to", "down to", a
limit such as "under" or "at most", "target of"); otherwise the target value is taught. Dates are parsed:
"31.03.2027" (and 31/03/2027) is read as written; a quarter ("Q1 2027") is read as its last day and shown with
the quarter it came from ("31 March 2027 (end of Q1 2027)") in the read-back the Belt confirms; a year alone
("by end of 2027") is no date, and the target date is taught.
