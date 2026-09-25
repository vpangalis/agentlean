---
paths:
  - "agent-improve/backend/core/llm.py"
  - "agent-improve/backend/phases/**"
  - "agent-improve/backend/upload/**"
---
# §4 — LLM rules

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 4. LLM RULES

### 4.1 — Factory only

Never instantiate `AzureChatOpenAI` directly. Always use:

```python
from core.llm import get_llm
llm = get_llm("coach", max_tokens=1500)
```

### 4.2 — Roles

**Roles, their deployment tier and their default temperature are owned by
`core/llm.py`** (`ROLE_DEPLOYMENTS`, `ROLE_TEMPERATURES`) — read them there.

**Model tiering is a cost rule, not a style preference.** Intermediate
multi-hop retrieval runs on `operational-model`; only final synthesis
runs on `operational-premium`.

New roles require an amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56).

### 4.3 — Never parse JSON from raw LLM text

Structured output is the only path from a model to a typed value. The
mechanism is §4.6; this rule is the prohibition.

### 4.4 — Agent construction — `create_agent`, with middleware

**Phase executors are built with `create_agent`** (in `nodes_common.py`) with
`response_format=CoachingResponse`, the full middleware stack (§8.1) and
`system_prompt=` — **not `prompt=`**. Binding tools directly onto a bare LLM
bypasses the middleware stack (§8) and is a violation. Checkpointer and store
are never set on the executor (§1.2).

**`create_react_agent` is superseded** by `create_agent` from
`langchain.agents`. Nothing may import it, and nothing may import from
the `langgraph.prebuilt` namespace.

**deepagents is NOT a dependency.** `create_deep_agent`,
`RubricMiddleware`, and `SkillsMiddleware` from that package are all
BANNED while it remains pre-1.0. Revisit at deepagents 1.0; migrate all
three custom middlewares together or not at all.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §18, §19.*

### 4.5 — Content blocks, both directions

Read `response.content_blocks`. String-indexing or substring-parsing the
raw content field is a violation.

**Content blocks apply in both directions. Never build message content by
interpolating or concatenating an existing message's `.content` —
construct with `content_blocks=`. Plain-string construction of a new
message is fine. A string-content message passes either
implementation, so any test covering message construction must use
list content.**

```python
existing = request.system_message
blocks = list(existing.content_blocks) if existing is not None else []
request.override(system_message=SystemMessage(
    content_blocks=[{"type": "text", "text": block}, *blocks],
))
```

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §21.*

### 4.6 — Structured output — scoped by call type

**The choice is determined by what is being called:**
- **An agent built with `create_agent`** → `response_format=Schema`. The phase
  executor is the only one, and its schema is **`CoachingResponse`, never a
  phase Output schema** (§10.7). Prefer `ProviderStrategy` over `ToolStrategy`.
- **A plain model call inside a tool, middleware or validator** (planner,
  validation layers, policy advisory, `DMAICGraderMiddleware`, `rag_lookup_*`
  query variants) → `with_structured_output`.
- **Gate document assembly and `gate_review`** → **no LLM call**
  (`DefineOutput(**artifacts)`; `interrupt()`).

**The structured response and the coaching text coexist** — the terminal
response arrives in `result["structured_response"]`; tools and coaching prose
in `messages` are unaffected.

**Structured output guarantees shape, not truth.** Content-level defence is
§6.4, §9.2, and §9.4.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §20, §21.*

### 4.7 — Temperature discipline

Per-role defaults are owned by `ROLE_TEMPERATURES` in `core/llm.py`. Coach
0.5–0.7; grader, coherence and constraint 0.1; extraction and field
validators 0.0–0.2.

**The grader's temperature is a hard requirement, not a tuning knob.**

### 4.8 — Fallback chain and circuit breakers

**Four levels, always terminating in success:**

```
Level 0: TimeoutPolicy(run_timeout=45)         — fires first (§3.6)
Level 1: gpt-4o    (operational-premium)       exponential backoff
Level 2: gpt-4o-mini (operational-model)       exponential backoff
Level 3: Azure Cache for Redis, session-scoped jittered backoff
Level 4: Degraded mode — never a hard failure to the Belt
```

**Backoff rule:** exponential for managed services (Azure OpenAI);
jittered for shared resources (the cache).

**Circuit breakers — three-state, two instances:** LLM (on OPEN: fall to
Level 2, then degraded) and Search (on OPEN: coaching **continues** without
RAG grounding). 3 failures in 30s trips open; 60s reset; one probe in
HALF-OPEN. **Two-state (CLOSED/OPEN) breakers are not permitted.**

**Degraded mode uses actual state, never a generic error** — name the phase
and how many fields are captured, say progress is saved.

**HTTP 400 (token limit exceeded) is NOT a fallback case.** Do not retry the
same request against a smaller model. Fix the context (§8.4).

**Every attempt is logged to `step_log` as a dict** (§10.3).

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §44, §46.*


## Never

*§14's bans that belong to this file — 6 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never instantiate `AzureChatOpenAI` directly — use `get_llm()`
- Never bind tools directly onto a bare LLM in a phase executor — use
  `create_agent` (§4.4)
- Never use `create_react_agent`, or import from `langgraph.prebuilt`
- Never parse JSON from raw LLM text
- Never string-index the raw content field — read `content_blocks` (§4.5)
- Never build message content by interpolating or concatenating an
  existing message's `.content` — construct with `content_blocks=`.
  Plain-string construction of a NEW message is fine, and a test covering
  message construction MUST use a list-content fixture (§4.5)
