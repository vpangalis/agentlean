# Response to Task 1 Audit Report (2026-08-19)

Paste this into the Claude Code session as the reply to its audit. It answers
every open question — proceed to apply changes once you've done the two
operational items below.

## Do these two things first, before anything else

1. **Commit now.** `start.ps1` runs `git reset --hard origin/main`. This
   entire audit and every decision below is one accidental run away from
   being destroyed. Commit before Task 2 starts.
2. **Revoke the GitHub PAT in `HANDOVER_AGENT_IMPROVE.md` line 364 now.**
   Untracked but on disk in a synced folder is still exposed. Not a
   documentation question — do it immediately, independent of everything else.

`_Artifacts/audit-2026-07-03.md` — no action needed, leave as historical record.

## B1 — resolved: SupervisorState wins, store-mediated only

CLAUDE.md §10.1, §10.2, and §1.2 are correct. REVIEW_DECISIONS.md line 2479
is the stale artifact — CLAUDE.md wins over a review-log line when they
disagree.

- Sweep `DMAICState` → `SupervisorState` across all 15 sites.
- Remove `define_output`/`measure_output` (and any equivalent per-phase
  output fields) from every occurrence.
- Replace the shared-key-name crossing example at §44 lines 9364–9388 with:

```python
# Parent — SupervisorState (§17), NOT DMAICState
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]
    case_id:         str
    phase_index:     int
    current_phase:   str
    gate_passed:     dict[str, bool]
    final_output:    Optional[dict]
    # NO define_output, NO measure_output — cross-phase artifacts never live here

class DefineState(TypedDict):
    messages: list
    understand_result: str       # PRIVATE — never crosses
    search_result: str           # PRIVATE — never crosses
    ctq_candidates: list         # PRIVATE — never crosses
    draft: DefineOutput          # written during the phase, not shared with parent

define_subgraph = build_define_subgraph(llm)
main_graph.add_node("define", define_subgraph)
main_graph.add_edge("define", "measure")             # static edge — fixed sequence

def define_output_mapper(state: DefineState, config) -> dict:
    case_id = config["configurable"]["thread_id"]
    store.put(("projects", case_id, "artifacts"), "define", state["draft"].model_dump())
    return {}

def measure_input_mapper(state, config) -> dict:
    case_id = config["configurable"]["thread_id"]
    define_artifacts = store.get(("projects", case_id, "artifacts"), "define").value
    return {"phase_context": build_context_from(define_artifacts)}
```

- Add the Store as a **third** mechanism in §44's mechanical explanation,
  alongside Mechanism 1 (shared keys, in-graph only) and Mechanism 2
  (transformers, in-graph only) — it's currently missing entirely, which is
  how this drift happened.

## C6 — resolved: Observer Agent keeps item 14, geographic redundancy becomes item 15

Observer Agent is the longer-standing, more thoroughly specified entry
(clear promotion trigger already defined). Renumber the newer addition
(2026-08-19), not the established one.

## C1, C2, C4, C5 — resolved

- **C1 (§71-D):** Finding body wins — **three LLM calls** (planner, synthesis,
  coach). Fix the Actions Summary table to say 3, not 2.
- **C2 (field count):** **17 total — 3 plumbing + 14 content.** Confirmed,
  proceed with your own proposed standardization.
- **C4 (§34-D):** **DEFERRED** wins — matches Category A's own A7. Fix the
  "OPEN" table entry.
- **C5 (`completeness_score`):** **No stored field — lines 8720/8827/8838 are
  correct.** Line 923's comment is stale, same root cause as A15. Fix both
  together.
- **A10's `retries=3` vs `retries=2`:** standardize on **`retries=2`**
  (majority of sites) unless Task 3B finds a documented reason for 3.

## C3 — resolved and verified against current LangChain docs

**CLAUDE.md §7.4 and REFACTORING §35 are correct. DECISIONS E1 is wrong.**
Verified directly against the official LangChain v1 migration guide: retrievers
including `EnsembleRetriever` moved out of the main `langchain` package into
`langchain_classic` as of the 1.0 migration. `langchain.retrievers.ensemble`
is non-functional in current `langchain`. E1's "confirmed v0.3" predates the
migration. Fix E1 to match CLAUDE.md §7.4.

## B2 — new decision, wasn't previously logged: improve_evidence_index schema

```
improve_evidence_index (7 fields, was 5)
  id, content, content_vector, metadata, case_id   [existing]
  phase           Edm.String   — NEW, auto-set from state["current_phase"] at upload
  uploaded_at     Edm.String   — NEW, ISO 8601, server-side, never Belt-entered
```

`rag_lookup_evidence` gains an optional `phase` filter (default unfiltered,
so cross-phase retrieval still works when needed). Resolves E1's own flagged
gap (no sortable `uploaded_at`) plus a previously-unaddressed problem: two
similar documents uploaded at different phases were indistinguishable.
Requires a reindex — batch with the already-planned `content_vector`
standardization (E2/A16).

`PhaseState.uploads` internal shape, also previously unspecified:
```python
uploads: list[dict]
# {"evidence_index_id": str, "filename": str, "phase": str,
#  "uploaded_at": str, "summary": str}
```

## B3 — new decision, wasn't previously logged: disconnect policy for the thread_id/graph.ainvoke wiring step

"Step 6" refers to the work described as the carry-forward blocker
(`routes.py:238` dispatches manually, checkpoints won't write until
`thread_id` is wired through `graph.ainvoke()`). Map this to whichever step
in your actual table that work belongs to (likely 3.3+, or a step that needs
adding) — reconcile the name, don't create a parallel "Step 6."

Source: Ranjan Kumar, "FastAPI + LangGraph: What a Client Disconnect Commits"
(measured 2026-08-04). Finding: the FastAPI handler's control-flow shape, not
the checkpointer, decides what survives a client disconnect once checkpoints
are live. Disconnect policy for Agent Improve: **ABANDON, not COMPLETE** — a
silently-completed gate approval the Belt never saw is unacceptable.

Required additions to that step's scope:
1. Deliberate handler shape (inline `await` streaming, or explicit `ABANDON`
   policy with `t.cancel()` in `gen()`'s `finally` — never a bare
   `asyncio.create_task` with no disconnect handling).
2. Deterministic `step_log` keys (`f"{phase}:{turn_count}:{step_name}"`, not
   raw timestamps).
3. An Azure Blob lease as the per-thread concurrency guard (Postgres
   advisory locks not available pre-migration).
4. A reconciliation sweep for abandoned threads that excludes
   `interrupt()`-paused threads.
5. Confirm `thread_id`/`case_id` is derived from the authenticated session,
   never client-supplied.

`gate_apply_node`'s store write is already safe (idempotent by key) — no
change needed there.

## B4 — low priority, apply whenever convenient

- §52: `BaseStore.search()` does support `filter=` — remove "metadata
  filters" from the list of things it lacks. It genuinely lacks hybrid
  BM25+vector scoring and multi-query+RRF — that part stays correct.
- §44/§45: the March 2026 Anthropic harness-design post is a specific
  research write-up on long-running coding harnesses, not general Anthropic
  architecture guidance superseding "Building Effective Agents" — soften
  the framing, keep the comparison.

## Green light

**Category A's 16 change sets are approved as originally listed.** Apply
everything above, then proceed to Task 2.
