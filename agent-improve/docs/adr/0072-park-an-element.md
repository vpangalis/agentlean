# ADR-0072: Parking an element is a coaching move decided in code

Status: ACCEPTED (founder, 2026-09-29)
Requirements: R14 (no dead end: after three attempts the coach offers to park the element and move on), W4 (choose what to work on next), DEF-075
Depends on: ADR-0065 (the new `field_status` value is a schema change)

## Context

R14: "If an element cannot be completed after three attempts, the coach offers to park it and move
on. A parked element stays open in the progress view and blocks approval only if it is required
(Tier 1). Every turn ends with an action the Belt can take." The coaching moves are decided in code
(teach, challenge, read back). "Park" doesn't exist yet, so a Belt who can't answer an element
today is stuck.

## Decision

1. `field_status` gains the value `parked`. This is a schema change under ADR-0065: the version goes
   up by one, and the migration is a no-op because no existing value changes.
2. **When:** after the third failed attempt on the same element (three challenges, or three refused
   Confirms), code sets the move to `offer_park`. The coach explains why the element matters and
   offers two buttons: **Park and move on**, or **Try again**.
3. **Park:** the element is marked `parked`, and the planner moves to the next available element (W4).
   Nothing is stored for the parked element.
4. **Coming back:** once all other available elements are confirmed, the planner returns to parked
   elements first. The Belt can also pick a parked element at any time from the progress view (W4, W9).
5. **At the gate:** every Define element is Tier 1, so a parked element blocks submission. The gate
   names it: "Parked: Primary metric and baseline. Complete it to submit." In other phases a parked
   Tier 2 element becomes an acknowledged gap (T66).
6. Every park and every return is recorded in `step_log` with the person and the time (R16, R19).

## Consequences

- The Belt is never stuck on one element (R14), and the journey carries on.
- The progress view shows parked elements as open, with their own marker.
- ARCHITECTURE.md §2.6 and §3 (coaching moves) are corrected in place; §4 regenerates.

## Rejected

- **Let the model decide when to offer parking.** Moves are decided in code, so it stays reproducible.
- **Auto-park without asking.** The Belt decides; the coach only offers.

## Verification

- End to end: three failed attempts lead to the offer, Park moves to the next element, and the gate
  names the parked element and refuses; completing it later allows submission.
- `step_log` holds both events.
