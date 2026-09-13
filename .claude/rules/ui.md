---
paths:
  - "agent-improve/ui/**"
  - "agent-improve/backend/gateway/**"
---
# §13 — UI and language rules

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 13. UI AND LANGUAGE RULES

- No methodology jargon in any team-facing string — plain language always
- Technical terms appear only as small secondary grey labels
- Every AI data request must include a concrete example with column names
- Every AI suggestion using cross-agent data must include a visible
  source citation
- Citation format: `agent_origin`, `index_name`, `document_id`,
  `relevance_summary`
- **Retrieval citations surface `source_file` and `page_number`**
  (§7.2) — "this came from page 47 of the BB eBook"
- **Spinner messages are contextual, never generic** — "Retrieving
  methodology…", "Validating your root cause…", not "Loading…"
- **The gate review screen shows extracted fields before approval**,
  editable, with an explicit approve action (§9.1 steps 4–7)

