---
paths:
  - "agent-improve/docs/requirements/**"
  - "agent-improve/ARCHITECTURE.md"
  - "agent-improve/backend/**"
---
# When a change needs an ADR

Brief Part F1 (founder, 2026-09-27). The format, lifecycle and index: `agent-improve/docs/adr/README.md`.

An ADR is required before the change lands when it touches any of:

| Area | For example |
|---|---|
| A state field or a schema | `SupervisorState`, `PhaseState`, a phase record, `CoachingResponse` |
| The graph | a node, an edge, routing, an interrupt |
| Middleware | adding, removing, reordering, or changing a hook |
| Persistence | the checkpointer, the Store, Blob layout, a search index |
| An external service | a new Azure service, model deployment or endpoint |
| The security boundary or a banned pattern | input screening, tool trust, `deprecated_patterns.yaml` |
| A real choice between alternatives | two workable designs, one chosen |

- Claude Code never writes the decision itself: it reports the need to Desktop, which drafts the
  ADR; the founder rules; the new-requirement procedure places it.
- The requirement names it in `Design: ADR-nnnn`; a feature of that requirement lands only when the
  ADR is ACCEPTED (guard rule 19, from ADR 0057).
- An ACCEPTED ADR is never edited, only superseded (guard rule 21).
