---
paths:
  - "agent-improve/backend/phases/**"
  - "agent-improve/backend/middleware/**"
  - "agent-improve/skills/**"
---
# §21 — The coaching move

> Moved verbatim from `agent-improve/CLAUDE.md` v2.2.46 on 2026-09-26 (step 6.67): it binds the code that coaches, so it loads with that code. Never renumber.

## §21 — The coaching move is decided in code (founder 2026-09-25; ARCHITECTURE.md v1.75; binds all phases and agents)

- **Code decides this turn's move from the field's status — never a model.** Not
  yet taught → teach (explain, show, ask); answered, insufficient → challenge
  (say what is missing); answered, sufficient → read back (the Belt's own words,
  then *"is this right?"*); confirmed by the Belt → store and advance.
- **A model is used only to judge whether an answer is sufficient, and to write
  the coach's words.**
- **A value is stored only after the Belt confirms it, in the Belt's words.** A
  tidied version may be proposed in the read-back and is stored only if the Belt
  confirms it.
- **The coach's input is assembled by code each turn in labelled sections, one
  job each:** coaching rules (how to behave) · phase script (what to teach) ·
  state (facts) · this turn's move (authoritative) · last turn's quality
  feedback · the conversation.
- **Coaching rules and phase scripts contain no move-sequencing** — no *"then
  advance"*, no *"confirm and move on"*, no *"one move, then stop"*.
- **Feedback to the coach is never presented as a message from the Belt.**
- **Every step that touches coaching behaviour carries a repeated-run
  consistency test in its Done-when** — the same turn, run five times, makes the
  same move.

