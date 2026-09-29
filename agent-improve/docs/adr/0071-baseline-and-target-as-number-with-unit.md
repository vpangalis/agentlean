# ADR-0071: Baseline and target are stored as a number with a unit

Status: ACCEPTED (founder, 2026-09-29)
Requirements: R7 amendment ("baseline and target are stored as a number with a unit, and an unparseable value is asked again"), C6 (carried forward in structure), T54 (one computing authority), DEF-076
Depends on: ADR-0065 (state schema versioning), accepted in the same ruling

## Context

The Define schema declares `baseline_metric` and `target_metric` as text. Measure has to verify the
baseline, and Control has to verify the target (C6), so both need a number they can compute with.
G-120's fix already parses a Belt's answer ("under 5%", "unter 5 %") into a number, a unit and a
direction in code, but the result is thrown away and the text is stored. G-132, where the chart read
"30 days" instead of 23%, shows what goes wrong when later steps re-read free text.

## Decision

1. Both fields become one structured type, `MetricValue`:

   | Part | Meaning |
   |---|---|
   | `value` | number |
   | `unit` | normalised unit (%, days, count, EUR…); the list is owned by the parser |
   | `direction` | target only: at most / at least / exactly (`<=`, `>=`, `=`) |
   | `is_estimate` | true when the Belt gives an estimate (R17: Define values may be estimates) |
   | `raw` | the Belt's own words, kept for the read-back and the audit trail (R16) |

2. The G-120 parser is the only way text becomes a `MetricValue`. Nothing else parses these fields.
3. The target must use the baseline's unit. If it doesn't, the coach asks again, naming both units,
   decided in code.
4. The read-back and the visual (ADR-0070) are built from the `MetricValue`, never from the raw text.
5. This is the first state schema change under ADR-0065. The schema version goes up by one, with the
   migration `migrate_vN_to_vN+1`. Existing text is parsed; a value that won't parse keeps `raw`, gets
   `value = None` and is marked for re-confirmation, so the coach asks for it again on the next visit.
   Nothing is deleted.

## Consequences

- Measure and Control read a number, not prose, as C6 requires.
- The baseline-to-target chart can no longer pick up the wrong number (the G-132 class).
- The 10 development cases migrate. Any value that can't be parsed shows up as a re-confirmation.
- ARCHITECTURE.md §4 (generated data models) changes automatically; the §3 description changes in place.

## Rejected

- **Keep text and parse it wherever it's needed.** Several parsers would drift apart, which is what G-132 showed.
- **A bare float.** It loses the unit and the direction, and "under 5%" is not the same as "5%".

## Verification

- The migration test uses fixtures of old checkpoints: parseable, unparseable, and estimate.
- End to end: "under 5% of supplier invoices" and "unter 5 %" are both stored as `{5, %, <=}`, and a
  target in a different unit from the baseline is asked again.
- In the live run-through, Measure's first turn reads the numeric baseline.
