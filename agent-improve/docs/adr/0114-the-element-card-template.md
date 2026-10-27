# ADR-0114: One element card for every element of every phase, assembled in code from the skill and the phase state

Status: ACCEPTED (founder, 2026-10-27, ruling R-C and the register-report ruling 5; drafted by Claude Code from the ruling and the approved mockup "progress-led, business" v2, Desktop chat 2026-10-27)
Requirements: W3 "Coaching page welcome" (amended 2026-10-27, R-A and R-C), C3 "Every request is explained, with a sample", R2 "Teach before asking"; founder test 2026-10-27 findings 9, 11, 12, 17, 18, 27, 31, 44, 45 (G-282, G-284, G-285, G-290, G-291, G-300, G-304, G-317, G-318); founder principle 15 Oct #83 ("the model writes language and judgment; code renders structure")
Depends on: ADR-0093 (element templates and the Gate view — the card's example table uses the element's Gate columns), ADR-0001 (teach before asking), ADR-0111 (what the model reads)
Changes: how a teaching move reaches the Belt (today the coach model writes `explanation`, `example` and `prompt`, and code fills an empty one from the script — G-138)

## Context

- Founder test 2026-10-27: the element card repeats the welcome (11); the example carries three labels (12, 18); a Confirm is announced three times — green strip, "Stored: …", "Now that your … is confirmed…" (17); the confirmation and the next element run together and the eye goes to the strip and the yellow example, not the question (27); "Where do we stand?" repeats the question and the example (31); a confirm prompt appears as "Your turn" (44); a Confirm that stores two elements names one (45); the welcome ends at "First: Business case" with nothing to do (9).
- Every one of these is STRUCTURE the coach model is asked to write, or code adds around what it wrote. The structure differs turn to turn because a model writes it.

## Decision (the founder's ruling R-C, in order)

1. **One template, every element, every phase.** The card has six parts, top to bottom:
   1. **Step trail** — "✓ n-1 · previous › [n] current › n+1 · next", and "k of N confirmed" on the right. From code (the element order, the phase state).
   2. **Saved note** — one line naming every element the last Confirm stored, with a short summary and "view in the Gate" linking to its section ("Target and target date saved: …"). From code. It replaces the green strip, "Stored: <element>." and "Now let's move on…".
   3. **Title and one-line purpose** — from the skill's element block.
   4. **YOUR TURN** — the strongest block (accent border and fill, the larger type): the element's question and a short hint on how much to write and, where the element accepts one, that a file can be uploaded. From the skill. Never a confirm prompt — that belongs to the read-back card.
   5. **"What a good answer looks like · example, not your data"** — a small table in the element's own columns, the same columns as its read-back and its Gate view (ADR-0093). One label only. From the skill's structured example.
   6. **Quiet help links** — "Why this matters", one element-specific question ("What makes a good CTQ?"; for the benefits "How do I calculate the cost of the gap?"), "Where do we stand?".
2. **Assembled in code, no model call.** A function builds the card from the skill's element block and the phase state; the page renders it. R-A: the welcome flows straight into the first element's card.
3. **The skill carries what the card needs, per element**: purpose (one line), question, hint, the structured example (rows in the element's Gate columns), and the element-specific help question. The skill's element blocks gain these as labelled parts, read by code the way `teaching_blocks` reads them today.
4. **A teaching turn makes NO coach model call** (founder, 2026-10-27, ruling 5): the card is the whole of the
   teaching. This removes a model call of 13–20 s from every teaching turn (measured on the founder's test).
5. **Later, in the same style**: the read-back card, the computation-result card (Measure and Analyse) and the completion card — each its own decision when it is built.

## Consequences

- Findings 11, 12, 17, 18, 27, 31, 44 and 45 are closed by one template rather than eight fixes; the card cannot drift between turns.
- The skill files of all five phases need the per-element parts of decision 3 before their elements can use the card; Define first.
- A teaching turn has no coach reply to grade: the card is given (ADR-0111 D3's rule for given parts).
- Size: L — the card builder, the page's renderer, Define's skill blocks, the welcome's hand-over, the tests.

## Rejected

- **Fixing the eight findings one by one** in the coach's prompt — each fix is a request to a model to lay out structure, which is what produced them.
- **A card per phase** — the founder ruled one template for all five.

## Verification

- A test per part: the card of every Define element carries the six parts in order, from the skill and the state, with no model call; the saved note names both elements when one Confirm stores two (finding 45); the example has one label (12); no confirm prompt in YOUR TURN (44); the welcome is followed by element 1's card (9).
- A run-through: every teaching turn's card recorded and checked against the template.
