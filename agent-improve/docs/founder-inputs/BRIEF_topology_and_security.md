# Brief for Claude Code — restore the concept: one supervisor graph, the security node, and the documents corrected in place

From Desktop, founder-ratified 2026-09-28. One long run by founder decision (the 60-minute box does
not apply to this brief; the three-commits limit does not apply; one commit per part below).
Inputs in `docs/founder-inputs/`: `RULINGS_2026-09-28.md`, `adr/ADR-0063-…`, `adr/ADR-0064-…`,
`adr/ADR-0065-…`. 0 live model calls. Every requirement change carries
`Ruling: 2026-09-28 founder — topology, security node and state versioning per BRIEF_topology_and_security.md`.

## The concept this restores (the founder's picture)

```
Main graph — Supervisor (orchestrator, not an agent, no LLM)
  input_guard  → phase router ("traffic light": reads current_phase / gate_passed)
        ↓ routes to one phase
Subgraph — one DMAIC phase (phase subagent), PhaseState
  planner (LLM call, not an agent) → executor = THE agent (create_agent + tools + middleware)
  → validation_stack → gate_review (HITL interrupt) → gate_apply
  wrapper node: input mapper → subgraph → output mapper (on approval: Store record, next phase)
```

**Documents are corrected in place.** ARCHITECTURE.md's existing sections are rewritten to
describe the new build; nothing is appended as an extra section, no "correction" notes, no
history. The drift story lives in the defect (Part B) and ADR-0063's context only.

---

## Part A — Rulings and records

1. Apply `RULINGS_2026-09-28.md` as ratified (MoSCoW, feature-input corrections, ADR statuses,
   G-115 in the other four skills, one passing count) — skip whatever is already applied.
2. Place ADR-0063, ADR-0064, ADR-0065. Statuses: **0063 ACCEPTED on condition** — the founder
   pre-ratifies it provided Part C's verification passes; if it fails, set it back to PROPOSED
   and stop before Part D. **0064 ACCEPTED. 0065 PROPOSED.** Set ADR-0023 to SUPERSEDED by 0063
   (status line only).
3. platform.md — add, with `Design:` and `MoSCoW:`:
   - **T88** (Must, ADR-0065): every checkpoint and Store record carries a state schema version;
     every state change ships a tested migration; a newer version refuses to load readably.
   - **T89** (Must, ADR-0063): production and tests compile the same graph builder; there is one
     builder.
   - **T90** (Must, ADR-0063): each turn enters the graph at the case's current phase through a
     deterministic router (no model call); approval of a phase's gate writes its record to the Store
     and advances the phase inside the graph.
   Amend **T3** if its wording conflicts ("no phase node writes case_id or current_phase" — the
   output mapper in the wrapper node is the single writer; confirm the test still expresses that).
4. Features: create the features for T88, T89, T90 (T88 held by ADR-0065). Make DEF-060, DEF-062,
   DEF-117 and the T89/T90 features one lane-B package; mark T71's feature (input guard) and
   DEF-144/T72 upload screening as lane B, next package.

## Part B — The defect

Register **G-116**: "Production runs one small graph per phase (`get_graph(phase)`); the designed
supervisor graph (`build_supervisor()`) is compiled only by tests; no output mapper runs." Evidence:
the call path you reported on 2026-09-28. Link it to the T90 feature. Work it as an 8D in the defect
entry's notes: occurrence (static-chain rule could not start a turn at the current phase),
escape (tests exercised the unused builder; no production-caller check; the document described
intent). D7 is ADR-0063's one-builder rule (T89) plus the F6 wiring check turned into a refusal for
graph builders and mappers.

## Part C — ADR-0063 verification (branch first)

On a branch: build the single graph as ADR-0063 decides and run its verification — one fresh case,
Define approved, the next `/ask` enters Measure through the same compiled graph; the Store holds
`artifacts/define`; checkpoint history shows one graph; existing gate and turn tests pass. Report
the result. If it passes, continue to Part D on that branch and merge at the end; if not, stop and
report.

## Part D — Implement the topology (lane B package)

1. One builder, `core/graph.py`, compiled once per process with checkpointer and store:
   `START → route_to_phase` (conditional entry, a pure function of `current_phase`) →
   `{phase}_phase` wrapper nodes → `END`. Remove the per-phase `get_graph(phase)` graphs and make
   `build_supervisor()` that one builder (or delete it) — T89.
2. Wrapper node: input mapper → `await subgraph.ainvoke(child)` with the inherited config → on
   approval the output mapper writes the Store record and sets `current_phase`, `phase_index`,
   `gate_passed`. The route stops writing the approved record (DEF-060) and stops writing the case
   blob mid-conversation (DEF-117); the case blob is written once at approval.
3. `/ask`, `POST /gate` and `POST /gate/decision` invoke the one graph; resume with
   `Command(resume=…)` on the same graph.
4. Existing development checkpoints written by the old per-phase graphs: report which cases would
   not load. Do not delete anything; Desktop decides.
5. Land DEF-060, DEF-062, DEF-117 and the T89/T90 features with their end-to-end tests through the
   API; the wiring check must show no mapper without a production caller.

## Part E — The security node (ADR-0057, accepted, fail closed)

1. `core/guard.py::input_guard` as a node in the main graph between `START` and `route_to_phase`;
   fixed rules first, then Prompt Shields through `core/content_safety.py` (endpoint and key from
   config, private endpoint). Block → a plain refusal with guidance, nothing written except the
   `step_log` verdict. Prompt Shields unreachable → fail closed for that turn with a readable message.
   Resume turns (`/gate/decision`) carry no Belt text and skip it.
2. Upload screening (T72): Prompt Shields document check in the upload pipeline before
   interpretation.
3. Tests use a fake Content Safety client (no live calls). If no Content Safety resource exists yet,
   say so; the live check is a later run.
4. Land T71's and T72's features.

## Part F — ARCHITECTURE.md corrected in place

Rewrite, do not append:
- §1 key-decisions table: ADR-0063 (one graph, phase router) replaces the ADR-0023 row; add ADR-0057.
- §2.1 context: Content Safety inside the intranet.
- §2.3 the graph: redraw as the concept above — main graph (input_guard, phase router), wrapper
  nodes, the five-node subgraph with the executor marked as the only agent; remove the per-phase
  graph description.
- §2.4 one coaching turn and §2.6 human in the loop: the route invokes the one graph; approval runs
  the output mapper.
- §2.5 persistence: case blob written once at approval.
- §3.1 code layout, §3.2 node table (add `input_guard`, `route_to_phase`, wrapper node), §3.9 API.
- §4.2 regenerates by itself.
Rule 17 must pass on every code commit.

## Part G — Close the loop

1. The board: G-116 and the lane-B package visible; "Waiting for you" updated.
2. `docs/architecture-v2-gaps.md`: remove anything this brief resolved.
3. Record the run in `prompts.jsonl`.

## Report

| Part | Commit(s) | Evidence |
|---|---|---|
| A | … | rulings applied; ADR statuses; T88–T90 added; features and package |
| B | … | G-116 with its 8D |
| C | … | verification result (pass / fail) with the test run |
| D | … | the new call path; DEF-060, DEF-062, DEF-117, T89, T90 passing through the API; wiring check clean for mappers |
| E | … | guard node and upload screening, tests with the fake client; Content Safety resource status |
| F | … | ARCHITECTURE.md sections rewritten (list them) |
| G | … | board and gaps file |

Stop and ask only if Part C fails or a founder decision is missing. Timing line at the end.
