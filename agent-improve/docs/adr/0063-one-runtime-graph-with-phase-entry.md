# ADR-0063 — One compiled runtime graph that enters at the current phase

Status: PROPOSED (founder pre-ratified 2026-09-28: ACCEPTED when its Verification passes) · 2026-09-28 · Supersedes in part: ADR-0023 (no router at the parent) ·
Restores: ADR-0021 (one compiled graph) · Requirements: T23, C6, R6 · Defects: G-112

## Context (as built, from the code, reported 2026-09-28)
- Each route calls `get_graph(phase)` (`routes.py:705` ask, `:1541` submit_gate, `:1411` decide_gate).
- `get_graph` (`graph.py:449`, `@lru_cache`) builds a one-node graph per phase —
  `StateGraph(SupervisorState)` + `add_node(f"{phase}_phase", phase_node(phase))` — compiled once per
  phase per process with the checkpointer and store (`graph.py:504–510`).
- `phase_node` runs the input mapper and `compiled.ainvoke(child)` on the cached subgraph
  (`graph.py:196–225`). **No output mapper runs**, so nothing writes the approved record to the Store
  and nothing advances the phase in graph state (G-112). The route writes the case blob instead.
- `build_supervisor()` — the designed parent with static phase-to-phase edges — is compiled only by
  `tests/test_supervisor_graph.py`.

Why the design was bypassed: a static chain define → measure → … fits one long run, but every
Belt turn is a new invocation that must enter at the *current* phase. The per-phase graphs were the
workaround. Five graphs now share one `thread_id`, phase transitions live in route code, and the
mappers have no production caller.

## Options
| | A — keep per-phase graphs | B — one graph, deterministic entry (recommended) |
|---|---|---|
| Shape | five cached one-node graphs; output mapper added inside `phase_node` on approval | one compiled graph: `START → route_to_phase (code, reads current_phase) → {phase}_phase → END`; the wrapper node runs input mapper → subgraph → output mapper |
| Phase transition | route code picks the next graph | output mapper sets `current_phase`, `phase_index`, `gate_passed`; the next turn enters the new phase |
| Checkpoints | five graphs write one thread; resume must use the same graph | one graph, one thread, one history |
| Change size | small | medium: entry router, wrapper node, route calls one graph |
| Fit with ADRs | supersedes ADR-0021 | keeps ADR-0021; supersedes ADR-0023's "no router" for the entry only |

## Decision (proposed)
Option B.
1. `get_graph()` returns one graph compiled once per process with checkpointer and store.
2. `START` → `add_conditional_edges(START, route_to_phase)`: a pure function of
   `state["current_phase"]`, no model call. Phase-to-phase static edges are removed: a turn ends at
   `END` after its phase node.
3. Each `{phase}_phase` wrapper node: input mapper → `await subgraph.ainvoke(child)` (inherited
   config) → on approval, the output mapper writes the Store record and sets the three routing
   fields. The route no longer writes the approved record (DEF-060) and no longer writes the case
   blob mid-conversation (DEF-117).
4. `POST /gate/decision` resumes the same graph with `Command(resume=…)`.
5. `build_supervisor()` is removed or becomes the production builder; there is one builder.

## Verification (before the ADR is accepted)
A spike on a branch: one fresh case, Define approved, next `/ask` opens Measure through the same
compiled graph; the Store holds `artifacts/define`; checkpoint history shows one graph's nodes;
existing gate tests pass. Report the diff and the test run.

## Consequences
ARCHITECTURE.md §2.3, §2.4, §2.6 change with the code. DEF-060, DEF-062 and DEF-117 become one
package in lane B, tier 1.

## Rejected
Option A (keeps five graphs on one thread and transition logic in routes); an LLM router (the phase
is a fact, not a judgment).
