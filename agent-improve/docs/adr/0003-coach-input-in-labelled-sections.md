# 0003. The coach's input is labelled sections, one job each

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §19.1 (v1.75), §22, §61 S-C11

## Context

The earlier prompt put facts at the top and mixed rules, script and state, so the model could not tell an instruction from a fact or feedback from the Belt.

## Decision

Code assembles the coach's input each turn in six labelled sections: coaching rules, phase script, state, this turn's move (authoritative), last turn's quality feedback, the conversation. Feedback is never presented as a message from the Belt.

## Consequences

Each section has one owner and can be tested on its own. It supersedes the facts-at-the-top order (0005).
