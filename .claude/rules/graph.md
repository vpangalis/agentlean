---
paths:
  - "agent-improve/backend/core/graph.py"
  - "agent-improve/backend/phases/**"
---
# §3 — Graph and node rules

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 3. GRAPH AND NODE RULES

### 3.1 — Graph structure

- One supervisor graph in `core/graph.py`
- One subgraph per phase in `phases/{phase}/graph.py`
- One escalation subgraph in `escalate.py`
- The supervisor compiles all subgraphs into a hierarchical compiled graph
- The compiled graph is the ONLY runtime path. `/ask`, `/ask/stream`,
  and `/gate/*` all invoke the same compiled graph object.
- **Entry is declared with `add_edge(START, ...)`.** The
  `set_entry_point` form is superseded.

The phase subgraph builder takes the phase as a parameter (it selects that
phase's computation-tool subset, §5.2) and compiles with **NO checkpointer,
NO store**.

### 3.2 — Node contract

Nodes are module-level async functions:

```python
async def phase_executor(state: PhaseState) -> dict:
    ...
    return {"draft": {...}, "step_log": [{...}]}
```

- File name and function name are aligned (one file per subgraph may
  contain multiple nodes)
- Nodes return `dict` slices only — never Pydantic, never full state
- Nodes are async (no sync nodes — §1.4)
- **Plans and drafts crossing nodes are structured**, never prose
  parsed downstream (§4.6)

### 3.3 — Per-phase subgraph nodes (the canonical structure)

Each phase subgraph contains exactly these nodes:

```
planner            — structured plan: focus_field, next_action,
                     retrieval_strategy, tools_needed
executor           — create_agent with the phase's tool subset
validation_stack   — the four layers (§9.2), shared cap of 3
gate_review        — interrupt() — presents validated fields, stops
gate_apply         — policy advisory, applies corrections, assembles
                     and writes the gate document (§9.6), routes on
```

**Five nodes. `policy_advisory` and `revise` are BANNED as node
names** — the policy advisory is logic inside `gate_apply`; revision is an
**edge** from the validation stack back to the planner.

**The subgraph is a cycle, not a pipeline.** After each executor step,
control returns to the planner.

**Leaf tools are NOT subgraph nodes** — they are passed to the executor via
`tools=` on `create_agent`.

**The validation stack and the policy advisory are NOT tools, and
adding either to a tool list is a violation.**

NEW node types may not be added to a subgraph without an amendment to
`../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56).

### 3.4 — Reflection is a node, not a private function

`_reflect()` inside orchestrate files (the v1 pattern) is BANNED.
Reflection is a graph node reached via a conditional edge.

For **invisible** retry use the retry middleware, not a reflection node:
`ModelRetryMiddleware` for model calls, `ToolRetryMiddleware` for tool calls
(§8.7).

### 3.5 — Escalation lives and runs

`escalate.py` defines the escalation subgraph. It is reachable via
conditional edge when the validation stack exhausts its shared cap of
3 attempts (§9.2), and via the `request_human_approval` tool.

`gate_attempts` lives in the checkpointed state (§10.1).

### 3.6 — Reliability primitives are native, not hand-written

**Custom Saga orchestrators and hand-written compensating-action
frameworks are BANNED.** LangGraph provides the mechanism.

**Per-node timeouts — required on every phase executor node:**
`builder.add_node(..., timeout=TimeoutPolicy(run_timeout=45),
error_handler=...)`. `NodeTimeoutError` triggers the fallback chain (§4.8).

**Node-level error handlers — required on every node with external
writes.** Every node that writes to Azure Blob, `improve_case_index`,
or `improve_evidence_index` gets an `error_handler=` that undoes the
external write and routes to a degraded response. The re-approval cascade
(§9.5) and time-travel debugging both depend on it.

**Graceful shutdown is REQUIRED; its named mechanism is UNCONFIRMED.** A
deployment rollout must not kill mid-coaching sessions — they save their
checkpoint and resume. If `request_drain()` does not exist, a real fallback
drain must be designed, never a replacement API name cited.
**No work may be scheduled against `RunControl.request_drain()` until it is
confirmed against a real release or the LangGraph source**
(`../AGENTIC_ARCHITECTURE_REFERENCE.md` §45).

**`DeltaChannel` is NOT used.** Beta API; deferred until sessions
exceed ~200 turns.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §44, §45.*

### 3.7 — Multi-hop is capped at five tool calls per Belt turn

**The cap is a count of `rag_lookup_*` calls, kept in the executor.**
`recursion_limit` is NOT the cap — it is a backstop (50) set on the parent
invoke. Never compute the hop cap from `recursion_limit`.

**`remaining_steps` is the graceful off-ramp, not the hop budget.** Read at
the top of the executor: when it runs low (`REMAINING_STEPS_FLOOR`) the
executor binds no tools and composes an answer from what it holds. Both
guards are required — hops and steps are different units.

**`GraphRecursionError` MUST still be caught in the coach node** and
turned into a partial answer for the Belt — belt-and-braces, not the
primary guard.

Hitting the cap is a **monitoring signal**, not just a limit.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §16, §26; S-F09 B1.*


## Never

*§14's bans that belong to this file — 8 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never mix static edges and `Command` routing from the same node
- Never use `set_entry_point` — use `add_edge(START, ...)`
- Never add a graph node type without an amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56)
- Never dispatch nodes manually in routes
- Never call `_reflect()` as a private function — reflection is a node
- Never fuse the planner and executor
- Never write a node with external writes and no `error_handler`
- Never hand-write a Saga orchestrator or compensating-action framework
