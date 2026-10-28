# ADR-0096: The benefits analysis stores hard benefits, the expected saving apart from the cost of the gap, and soft benefits each with its indicator

Status: ACCEPTED (founder, 2026-10-28, at the start of wave 1 — founder test 2026-10-27; drafted by Claude Code 2026-10-16 from the founder's ruling of 2026-10-15 on the benefits analysis)
Requirements: R4 and R7 (amendment PROPOSED), C6, C1; findings 10, 57, 72; G-226; founder test 2026-10-27 findings 48, 51, 52 (G-320, G-323, G-324)
Depends on: ADR-0077 (calculations run by code), ADR-0065 (T88)

## Decision

1. **`benefits_analysis` keeps** `cost_of_gap`, `impact_type`, `realisation_schedule` and `finance_contact`
   (the hard benefits), and gains:
   - `expected_saving`: what reaching the target removes. It is apart from the cost of the gap, which is
     what the problem costs today at the baseline.
   - `soft_benefits`: a list of `{benefit, indicator}`. Each is never converted into money and never added to
     the hard figure. "None identified" is a conscious answer.
2. **The code calculation proposes both figures, labelled**: the cost of the gap and the expected saving,
   with € and thousands separators, and the formula and input elements named.
   - The Define skill's TOOL step is corrected: it called the saving "the cost of the gap".
3. **A new rubric criterion** (R7): soft benefits stated, each with an indicator, or consciously none (manual
   p. 60–63).
4. **Define report section B** shows the hard and soft benefits separately.
5. **The skill text and the overview** use the founder-approved wording (findings file, item 7).
6. **Schema bump with a migration**: `soft_benefits` is absent → "not stated", and the Belt is asked when the
   element is next opened.

## Rejected

- **Soft benefits as free text inside the business case**: Control cannot read them (C6).
