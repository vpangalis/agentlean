---
paths:
  - "agent-improve/backend/core/graph.py"
  - "agent-improve/backend/phases/**"
---
# §3 — Graph and node rules

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

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

The phase subgraph builder takes the phase as a parameter, because it
must select that phase's computation-tool subset (§5.2):

```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
    return builder.compile()          # NO checkpointer, NO store
```

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
names.** Both appeared in earlier revisions:

| Retired | Ratified | Why |
|---|---|---|
| `policy_advisory` | `validation_stack` | The four-layer stack was missing from the node list entirely. The policy advisory is logic inside `gate_apply`, not a node |
| `revise` | `gate_apply` | Revision is an **edge** — the validation stack routes back to the planner with `validator_feedback`. `gate_apply` does advisory + approval + store write |

**The subgraph is a cycle, not a pipeline.** The planner fires many
times per phase, not once: after each executor step, control returns
to the planner to decide whether to continue on the current field,
advance to the next, or trigger the gate.

**Leaf tools are NOT subgraph nodes.** The universal eight (§5.1) and
the phase's computation tools are passed to the executor via `tools=`
on `create_agent`. From the subgraph's perspective the executor is one
node.

**The validation stack and the policy advisory are NOT tools, and
adding either to a tool list is a violation.**

| Component | What it is |
|---|---|
| Validation stack | A **node**, reached by an edge after the executor finishes. As a tool, the coach would decide whether to be validated — backwards |
| Policy advisory | **Logic inside `gate_apply`**. It runs after the Belt edits, when the coach is no longer in the loop |

NEW node types may not be added to a subgraph without an amendment to
`../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56).

### 3.4 — Reflection is a node, not a private function

`_reflect()` inside orchestrate files (the v1 pattern) is BANNED.

Reflection is a graph node reached via a conditional edge. The edge
decides whether reflection is needed based on response length, risk
keywords (numbers, commitments, dates), and phase-specific rules.

For **invisible** retry — mechanical, not a coaching event — use the
retry middleware rather than a reflection node: `ModelRetryMiddleware`
for model-call failures, `ToolRetryMiddleware` for tool-call failures
(§8.7). Neither is named `RetryMiddleware`; that class does not exist.

### 3.5 — Escalation lives and runs

`escalate.py` defines the escalation subgraph. It is reachable via
conditional edge when the validation stack exhausts its shared cap of
3 attempts (§9.2), and via the `request_human_approval` tool.

`gate_attempts` is persisted in the checkpointed state, never in route
scope.

### 3.6 — Reliability primitives are native, not hand-written

**Custom Saga orchestrators and hand-written compensating-action
frameworks are BANNED.** LangGraph 1.2 provides the mechanism.

**Per-node timeouts — required on every phase executor node:**

```python
builder.add_node(
    "phase_executor",
    phase_executor_fn,
    timeout=TimeoutPolicy(run_timeout=45),
    error_handler=phase_error_recovery,
)
```

`run_timeout=45` is the wall-clock limit. `NodeTimeoutError` triggers
the fallback chain (§4.8) before the Belt notices the delay.

**Node-level error handlers — required on every node with external
writes.** Every node that writes to Azure Blob, `improve_case_index`,
or `improve_evidence_index` gets an `error_handler=` that undoes the
external write and routes to a degraded response:

```python
def phase_error_recovery(error: NodeError, state: PhaseState) -> Command:
    delete_or_flag_stale_in_case_index(state["case_id"], state["phase"])
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response",
    )
```

**Two dependencies on this rule, both correctness-critical:**
- **Gate reopening** (§9.5) — when the re-approval cascade fires, the
  affected phase's handler must run, or state and index disagree
  silently.
- **Time-travel debugging** — resuming from an earlier checkpoint
  rolls back state, **not** external writes. Time travel is only
  correct for nodes that have a handler.

**Graceful shutdown is REQUIRED; its named mechanism is UNCONFIRMED.** A
deployment rollout must not kill mid-coaching sessions — they save their
checkpoint and resume. **But `RunControl.request_drain()` may not exist:**
it was not found in LangGraph releases 1.2.5–1.2.11 or in the reference
during the 2026-08-21 verification pass.

**No work may be scheduled against `request_drain()` until it is confirmed
against a real release or the LangGraph source.** If it does not exist, a
real fallback drain must be designed rather than a replacement API name
cited. Full statement and what counts as confirmation:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §45.

**`DeltaChannel` is NOT used.** Beta API; deferred until sessions
exceed ~200 turns.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §44, §45.*

### 3.7 — Multi-hop is capped at five tool calls per Belt turn

**The cap is a count of `rag_lookup_*` calls, kept in the executor.**
`recursion_limit` is NOT the cap. It is a backstop against a genuine
infinite loop, set high (50) on the parent invoke and inherited by
everything below it:

```python
await graph.ainvoke(
    state,
    config={"recursion_limit": RECURSION_LIMIT,        # 50 — backstop
            "configurable": {"thread_id": case_id}},
)
```

**`remaining_steps` is the graceful off-ramp, not the hop budget.**
It is a `RemainingSteps` managed value declared on `PhaseState`
(§10.1) and read at the top of the executor. When it runs low the
executor stops calling tools and composes an answer from what it
already holds — the Belt gets a coached turn, not a cap message:

```python
if (state.get("remaining_steps") or 0) <= REMAINING_STEPS_FLOOR:
    ...                     # compose from what is in hand; bind no tools
```

**Hops and steps are different units and neither substitutes for the
other.** `remaining_steps` counts graph-node transitions out of
`recursion_limit`; the whole coach loop runs inside ONE node, so it
moves by 1 per executor turn no matter how many hops that turn made.
A hop count is therefore kept separately, in the executor. Both
guards are required: the hop count enforces five, `remaining_steps`
catches the case where the graph itself is running out of room.

**`GraphRecursionError` MUST still be caught in the coach node** and
turned into a partial answer for the Belt. It is now **belt-and-braces
against a bug, not the primary guard** — a Belt mid-session never sees
a stack trace because the coach explored too broadly.

Hitting the cap is a **monitoring signal**, not just a limit — it
means either the system prompt encourages too-broad exploration, or
the question warrants `operational-premium` for that turn.

**This rule is why the build was wrong from step 6.2 to 6.6.** It
previously carried `recursion_limit = 2 * max_hops + 1 = 11` as the
hop cap — which `../AGENTIC_ARCHITECTURE_REFERENCE.md` §16 explicitly
rejects, and which is also arithmetically short: measured on both
LangGraph 1.1.10 and 1.2.11, a coach making its five permitted hops at
`recursion_limit=11` raises `GraphRecursionError` **before** it can
compose the answer, so a well-behaved five-hop turn could only ever
end in the cap message. That is WATCH 26's see-saw. Whatever this
rule says is what gets built, so it says the mechanism now.

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
