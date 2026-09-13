---
paths:
  - "agent-improve/backend/core/prompts.py"
  - "agent-improve/skills/**"
---
# §6 and §15 — Prompts, and prompt size

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 6. PROMPTS

### 6.1 — Constants in `core/prompts.py`

All prompts live as constants in `core/prompts.py`. Prompt strings are
never inline in node files.

### 6.2 — Prompt naming

- `{PHASE}_COACH_PROMPT` — phase executor system prompt
- `{PHASE}_PLANNER_PROMPT` — phase planner prompt
- `{PHASE}_RUBRIC` — grader rubric constant (§8.2)
- `{PHASE}_CONSTRAINTS` — constraint set (§9.2)

The v1 `ORCHESTRATOR_{PHASE}_CONTEXT` and `EXTRACTION_{PHASE}`
patterns are deleted. Extraction is a tool call.

**`KNOWLEDGE_INJECTION_TEMPLATE` is deleted.** RAG results arrive as
tool results, not as a prepended system message (§7.1).

### 6.3 — The memory hierarchy paragraph is mandatory

Every coach system prompt carries an explicit source hierarchy. This
is the ratified mechanism for memory prioritisation — **prompt-level
priority, not per-chunk metadata scoring**:

```
MEMORY HIERARCHY — when sources disagree, weight them in this order:
  1. LSS Black Belt methodology (rag_lookup_methodology) — authoritative
  2. This project's confirmed captured fields — the Belt's own approved facts
  3. Past case history (rag_lookup_case_history) — patterns, not prescriptions
  4. Recent conversation — context, not evidence
Never present case history as methodology. Never let a recent remark
override a gate-approved value without flagging it.
```

### 6.4 — Anti-hallucination guards are mandatory

Every coach and extraction prompt carries explicit anti-hallucination
guards. **The LLM must never invent field values from coaching
templates.** A template showing `baseline_mean: 4.2` as an example is
not data.

Structured output does not satisfy this rule (§4.6). Content-level
defence requires all three of:
1. Explicit prompt guards
2. Cross-checking extracted values against the raw conversation
3. The policy advisory reviewing extracted values before Belt approval

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §22.*

## 15. PROMPT SIZE MANAGEMENT

When a UI change touches more than 3 functions or adds more than ~150
lines of new code, split into multiple focused prompts. Never include
more than 2 full function replacements per prompt for `index.html`.


## Never

*§14's bans that belong to this file — 5 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never put prompts inline in node files
- Never omit the memory hierarchy paragraph from a coach prompt
- Never omit anti-hallucination guards from a coach or extraction prompt
- Never duplicate `CitationRecord`
- Never use methodology jargon in team-facing strings
