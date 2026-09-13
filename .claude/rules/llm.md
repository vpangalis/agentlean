---
paths:
  - "agent-improve/backend/core/llm.py"
  - "agent-improve/backend/phases/**"
  - "agent-improve/backend/upload/**"
---
# §4 — LLM rules

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 4. LLM RULES

### 4.1 — Factory only

Never instantiate `AzureChatOpenAI` directly. Always use:

```python
from core.llm import get_llm
llm = get_llm("coach", max_tokens=1500)
```

### 4.2 — Roles

Defined in `core/llm.py`. Two deployment tiers, addressed by role:

| Role | Deployment | Purpose |
|---|---|---|
| `coach` | `operational-premium` (gpt-4o) | Coaching content, max_tokens=1500 |
| `planner` | `operational-premium` (gpt-4o) | Phase planner structured decisions |
| `synthesis` | `operational-premium` (gpt-4o) | Final multi-hop synthesis |
| `reasoning` | `operational-model` (gpt-4o-mini) | Default reasoning, intermediate hops |
| `extraction` | `operational-model` (gpt-4o-mini) | Field extraction |
| `coherence` | `operational-model` (gpt-4o-mini) | Layer 1 coherence check (§9.2) |
| `constraint` | `operational-model` (gpt-4o-mini) | Layer 3 constraint check (§9.2) |
| `grader` | `operational-model` (gpt-4o-mini) | Layer 4 rubric grading (§8.2) |
| `summarizer` | `operational-model` (gpt-4o-mini) | Context compression (§8.4) |
| `intent` | `operational-model` (gpt-4o-mini) | Short classification |
| `vision` | `operational-premium` (gpt-4o) | Multimodal upload analysis |

**Model tiering is a cost rule, not a style preference.** Intermediate
multi-hop retrieval runs on `operational-model`; only final synthesis
runs on `operational-premium`. gpt-4o-mini is roughly 15× cheaper.

New roles require an amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56).

### 4.3 — Never parse JSON from raw LLM text

Structured output is the only path from a model to a typed value. The
mechanism is §4.6; this rule is the prohibition.

### 4.4 — Agent construction — `create_agent`, with middleware

**Phase executors are built with `create_agent`.** Binding tools
directly onto a bare LLM inside a phase executor is a violation: it
bypasses the middleware stack (§8), which carries grading, skills,
compression, and state injection.

```python
executor = create_agent(
    model=get_llm("coach"),
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=CoachingResponse,       # §4.6, §10.7 — never a {Phase}Output
    middleware=[...],                       # §8.1 — all eight, in order
    system_prompt=PHASE_COACH_PROMPT[phase],
)
```

**The parameter is `system_prompt=`, not `prompt=`.** `create_react_agent`
took `prompt`; `create_agent` renamed it, and the LangGraph v1 migration
guide calls this out explicitly as a difference to watch when porting. The
verified signature also carries `state_schema`, `context_schema`,
`checkpointer`, `store`, `interrupt_before`, `interrupt_after`, `cache` and
`transformers` — none of which this project sets on the executor, since the
checkpointer and store attach to the parent graph only (§1.2).

*This example previously showed `response_format=ProviderStrategy(PhaseOutput)`
and "all four" middlewares. Both contradicted rules elsewhere in this file —
§4.6 and §10.7 mandate `CoachingResponse` on the executor, and §8.1 declares
eight middlewares. Corrected 2026-08-21. `prompt=` → `system_prompt=`
corrected in the same pass (`docs/_archive/BIBLE_VERIFICATION_LOG.md` C-2).* (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

**`create_react_agent` is superseded** by `create_agent` from
`langchain.agents`. Nothing may import it, and nothing may import from
the `langgraph.prebuilt` namespace.

**deepagents is NOT a dependency.** `create_deep_agent`,
`RubricMiddleware`, and `SkillsMiddleware` from that package are all
BANNED while it remains pre-1.0. Our equivalents are custom middleware
on `create_agent` (§8.2, §8.3). Revisit at deepagents 1.0; migrate all
three custom middlewares together or not at all.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §18, §19.*

### 4.5 — Content blocks, both directions

Model responses carry typed content blocks. Read
`response.content_blocks`. String-indexing or substring-parsing the
raw content field is a violation — it breaks the moment a provider
returns a multi-part response.

**Content blocks apply in both directions. §21 governs messages we
write as well as responses we read. Never build message content by
interpolating or concatenating an existing message's `.content` —
construct with `content_blocks=`. Plain-string construction of a new
message is fine. A string-content message passes either
implementation, so any test covering message construction must use
list content.**

`SystemMessage.content` is `str | list[dict]`. Over a multi-part
message an f-string renders the literal
`[{'type': 'text', 'text': …}]` into the prompt — structure
destroyed, **no error raised**, and the model silently reads a Python
repr.

```python
existing = request.system_message
blocks = list(existing.content_blocks) if existing is not None else []
request.override(system_message=SystemMessage(
    content_blocks=[{"type": "text", "text": block}, *blocks],
))
```

**The write side reached a commit at step 6.3** — both custom
middlewares concatenated onto `.content`, and it survived writing,
review, 716 green tests and a live trace. The rule had been filed
under *reading*, because step 2.6's twenty sites were all
`response.content`. **The list-content fixture is the load-bearing
half of this rule:** a string-content message passes the correct and
the broken implementation identically, so a test built on one proves
nothing. Full record: `docs/_archive/DECISIONS.md` Part AH2.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §21.*

### 4.6 — Structured output — scoped by call type

**This rule replaces v2.1 §4.3, which mandated one mechanism
everywhere. There are two mechanisms, and the choice is determined by
what is being called — not by preference.**

| The call is… | Use | Example |
|---|---|---|
| An agent built with `create_agent` | `response_format=Schema` (ProviderStrategy auto-selected) | Phase executor → `CoachingResponse` |
| A plain model invocation inside a tool, middleware, or validator | The builder-style structured-output call on the model | Query variants, grader verdict, constraint verdict |
| Assembling a gate document from already-captured fields | **No LLM call** — Pydantic construction | `DefineOutput(**artifacts)` at `gate_apply` |

**Why the first two exist separately:** `response_format=` attaches to
an agent's model-tools loop. A tool generating query variants, a
middleware grading a transcript, and a validator returning
per-constraint verdicts are not agents — there is no loop to attach to.

Prefer `ProviderStrategy` over `ToolStrategy` where the provider
supports native JSON mode. LangChain 1.2 can infer the choice from the
model profile.

**Complete mapping — every structured output in the system:**

| Component | Built with | Schema | Mechanism |
|---|---|---|---|
| Phase planner | Plain LLM call | `CoachingPlan` | `with_structured_output` |
| **Phase executor (coach)** | **`create_agent` + tools** | **`CoachingResponse`** | **`response_format=`** |
| Validation Layer 2a (coherence) | Plain LLM call | `CoherenceResult` | `with_structured_output` |
| Validation Layer 2c (constraints) | Plain LLM call | `ConstraintCheckResult` | `with_structured_output` |
| Validation Layer 2d (gate grader) | Plain LLM call | `GraderVerdict` | `with_structured_output` |
| `gate_review` | **No LLM** | Interrupt payload | `interrupt()` |
| `gate_apply` — policy advisory | Plain LLM call | `PolicyAdvisoryResult` | `with_structured_output` |
| `DMAICGraderMiddleware` | Plain LLM call in middleware | `CoachingGraderVerdict` | `with_structured_output` |
| Inside `rag_lookup_*` | Plain LLM call | `QueryVariants` | `with_structured_output` |
| Gate document assembly | **No LLM** | `DefineOutput` … `ControlOutput` | `Schema(**artifacts)` |

**The executor's `response_format` is `CoachingResponse`, never a phase
Output schema.** The executor runs once per coaching turn; the gate
document is assembled once per phase. Asking the coach to emit a
complete `DefineOutput` every turn requests fields it has not yet
coached. See §10.7.

**The structured response and the coaching text coexist.** The agent
still calls tools normally through the ReAct loop and still writes
coaching prose into `messages`; only the terminal response is
additionally structured, and it arrives in `result["structured_response"]`.
Reading one does not cost you the other.

**What structured output does NOT give you:** truth. It guarantees
shape. A schema-valid `baseline_estimate: 4.2` invented by the model is
exactly as well-formed as a correct one. Content-level defence is
§6.4, §9.2 Layer 1, and §9.4 — not this rule.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §20, §21.*

### 4.7 — Temperature discipline

| Component | Temperature | Why |
|---|---|---|
| Coach responses | 0.5–0.7 | Natural variation improves the Belt's experience |
| Grader (§8.2) | 0.1 | Same gate document must get the same verdict across runs |
| Coherence check (Layer 1) | 0.1 | Consistent verdicts |
| Constraint check (Layer 3) | 0.1 | Consistent verdicts |
| Extraction, field validators | 0.0–0.2 | Same rationale |

**The grader's temperature is a hard requirement, not a tuning knob.**
A grader that returns different verdicts across runs makes the
regression thresholds in §12 meaningless.

### 4.8 — Fallback chain and circuit breakers

**Four levels, always terminating in success:**

```
Level 0: TimeoutPolicy(run_timeout=45)         — fires first (§3.6)
Level 1: gpt-4o    (operational-premium)       exponential backoff
Level 2: gpt-4o-mini (operational-model)       exponential backoff
Level 3: Azure Cache for Redis, session-scoped jittered backoff
Level 4: Degraded mode — never a hard failure to the Belt
```

**Backoff rule:** exponential for managed services (Azure OpenAI, which
rate-limits predictably); jittered for shared resources (the cache,
which several subagents may hit simultaneously).

**Circuit breakers — three-state, two instances:**

| Breaker | Wraps | On OPEN |
|---|---|---|
| LLM | Azure OpenAI calls | Coaching turn cannot happen — fall to Level 2, then degraded |
| Search | Azure AI Search calls | Coaching **continues** without RAG grounding — quality degradation, not availability failure |

Threshold 3 failures in 30s trips open; 60s reset timeout; one probe
request in HALF-OPEN before resuming. **Two-state (CLOSED/OPEN)
breakers are not permitted** — this is a long-running service and must
recover without a restart.

**Degraded mode uses actual state, never a generic error:**

```python
def degraded_mode_response(state: PhaseState) -> str:
    return (
        f"I'm experiencing a temporary connection issue. "
        f"Based on what we've captured so far in the {phase} phase "
        f"({n_captured} of {n_total} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

**HTTP 400 (token limit exceeded) is NOT a fallback case.** It is a
context-management failure — do not retry the same request against a
smaller model. Fix the context (§8.4).

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
