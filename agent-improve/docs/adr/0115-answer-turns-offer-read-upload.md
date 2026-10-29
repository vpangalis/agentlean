# ADR-0115: Answer turns offer read_upload, and no other tool

Status: ACCEPTED (founder, 2026-10-29, decision 5 on the wave-2 report: "ADR-0069 amendment: offer read_upload on answer turns; no other lookups now"; written by Claude Code from that ruling)
Requirements: W5 "Uploads strengthen answers", T69 (at most 4 model calls per turn), R13 (45 s)
Refines: ADR-0069 (answer turns bind no tools). ADR-0069 stays in force for every other tool; this ADR adds one tool to its answer row.
Depends on: ADR-0106 (`read_upload`, the coach reads a document the Belt uploaded), ADR-0114 (the element card: a teaching turn makes no coach call)

## Context

- Since R-C (ADR-0114, wave 2), a teaching turn in Define is the element card, written in code with no coach call. ADR-0069 binds no tools on an answer turn, so Define offers `read_upload` only on an upload turn (wave-2 report, decision 5).
- An upload turn is made only by a new upload, or by an unread one the Belt refers to. When the Belt answers with "as in the file I sent" about a file already read, the coach can quote only what is in the conversation.
- ADR-0069 rejected "a structured reply after one tool call" because it meant five calls. With the coherence judge retired (ADR-0083), an answer turn's calls are the planner's judgment, the coach and the grader: the coach's share is 2 (`TURN_MODEL_CALLS - 1 - AFTER_AGENT_CALLS`). One `read_upload` call and the structured reply fit in T69's 4.

## Decision (the founder's ruling)

1. **An answer turn offers `read_upload`, and no other tool.** No lookups, no templates, no `load_skill`, no computation tool.
2. The turn tools middleware still offers no tool on the coach's last allowed call (G-131), so the second call is always the structured reply.
3. Teaching and upload turns are unchanged.

## Consequences

- The coach can quote a file the Belt names in an answer, from the case's own blob (ADR-0106: only files of the current case).
- An answer turn that reads a file makes one more model call, within T69. An answer turn that does not read one is unchanged.
- ARCHITECTURE.md §3.6's tools-per-turn-type table changes in place.

## Rejected

- **Offer the methodology lookups on answer turns too.** Not now (the ruling).
- **Offer `read_upload` only when the case has an upload.** The tool refuses a file outside the case, so offering it with nothing to read costs only its schema. The live slice measures whether the coach calls it with nothing to read.

## Verification

- DEF-292's test: an answer turn offers exactly `read_upload` on the coach's first call and nothing on its last.
- The executor's answer-turn test: no lookup is offered.
- A live slice on the founder's answers: no answer turn calls a tool it does not need, and every turn stays under 45 s.
