# Instruction: update CONTINUITY.md to current state (end of 2026-08-24 session)

Update agent-improve/docs/CONTINUITY.md so a NEW chat can resume the spec-gap
resolution work exactly where this session ends. This is a state refresh, not a
restructure — keep the existing structure, update the facts, add the new
in-progress detail below. Process governance (version-log bump), not a §56
amendment.

## What the new chat must know — fold all of this into CONTINUITY.md

### Where the work stands
- The SDD spec-layer conversion is DONE. AGENTIC_ARCHITECTURE_REFERENCE.md
  (root, platform reference) and agent-improve/ARCHITECTURE.md (Improve's copy)
  carry the spec layer: 73 spec entries in the three-layer template (SIPOC +
  EARS table + selective AI-ACT flag), the Compliance & Risk Part (EU AI Act
  posture + DORA register), governance rules §55.1, and the Standing Reasoning
  Protocol §6.1.
- Governing docs: SPEC_LAYER_GUIDE.md (the spec-of-the-spec), SPEC_SAMPLES.md
  (the two approved calibration samples — SupervisorState = class template,
  phase_executor = function template). Both in agent-improve/docs/.
- The two reference files remain byte-identical except the 93-line divergence
  (copy's provenance header + six root-only Scope: annotations). Any spec change
  goes into BOTH and is diff-checked after.

### The current activity: resolving SPEC-GAPs via the Standing Reasoning Protocol
- 43 gaps identified. Work them in severity order: Category B latent bugs first
  (the "reader with no declared writer" pattern, same signature as
  route_after_phase), then C/D.
- Each gap is resolved through the 4-step protocol (CONTINUITY §6.1 / guide
  §6.1): (1) DETAIL, (2) HOLISTIC trace through SIPOC links, (3) TRUSTED-SOURCE
  check against current LangGraph/LangChain/LangSmith (+ EU AI Act/DORA for
  compliance), (4) USE-CASE forward-note. Resolving a gap may surface new gaps.
- Reasoning happens in the Claude.ai chat (Opus); Claude Code applies. The chat
  has no repo write access — it reads the live reference from OneDrive.

### Gaps resolved so far (mark status in the §66 register)
- G-41: closed (samples supplied).
- G-03 + G-42 + gate_apply's case_id half: RESOLVED via ruling A2, committed.
  PhaseState 17 -> 19 fields: added case_id and current_phase, BOTH written only
  by the input mapper at phase entry (copy-down from parent SupervisorState),
  read-only within the subgraph (invariant enforced by grep check + B4/B6
  no-return-upward). §56 trigger reworded to fire on ANY PhaseState field
  addition regardless of category (closed an enforcement hole). CLAUDE.md
  (v2.2.21) and procedure steps 3.1/3.3 updated in the same amendment.
  Use-case tags: UC-PHASE-ENTRY (input_mapper), UC-PHASE-EXIT (output_mapper).
- G-43: RESOLVED as FALSE ALARM / already-known-pending (this was the last
  action of the session — CONFIRM it committed). Findings: no standalone
  subgraph invocation exists anywhere (every .invoke is either the single
  parent graph.ainvoke with thread_id in config, or an LLM call); checkpointer
  placement is correct per LangGraph docs (parent has it, subgraphs inherit via
  checkpoint_ns); the "dropped companion clause" was correctly omitted (applies
  only to independently-persisted subgraphs, which Agent Improve does not do) --
  so NOT a genuine partial-quotation instance, recorded as a true negative that
  fired-and-cleared. What remains folds entirely into the already-known,
  already-scheduled "thread_id through graph.ainvoke" wiring step (§16/§47) --
  the WIRED-INERT checkpointer. No new work. Memory architecture confirmed
  SOUND: checkpointer stores full conversation+PhaseState in Azure Blob under
  thread_id=case_id and reloads on return; SummarizationMiddleware (keep=20)
  only trims what the LLM sees per turn, not what is stored. A Belt's 100-message
  session survives close/reopen once thread_id wiring lands.

### NEXT GAP: G-04 — the live one
- Location: analyse_executor_node, reference §26 (~line 2515):
  `if state.get("remaining_steps", 10) <= 2:` — reads remaining_steps, which
  has NO declared writer on PhaseState. So it defaults to 10 forever and the
  5-hop cap NEVER fires. This is a genuine latent bug (unlike G-43), the sharpest
  of the remaining Category B set.
- Likely needs a RemainingSteps declaration on PhaseState (probably another §56
  field-addition amendment — note PhaseState is now at 19 after G-03).
- Work it through the full 4-step protocol. Check the LangGraph RemainingSteps /
  recursion_limit semantics against current docs (the code comment claims
  RemainingSteps does not decrement between hops inside one node — verify that
  against current LangGraph before designing the fix).

### Memory-architecture note to carry forward (established this session)
Two separate LangGraph memories: (1) short-term = checkpointer = the
conversation + PhaseState, thread-scoped by thread_id=case_id, stored in Azure
Blob; (2) long-term = Store = cross-project knowledge, namespaced. Trimming/
summarization (last-20) is a THIRD thing — it shapes what the LLM SEES per turn,
not what is STORED. Storage keeps everything.

### Working discipline reminders (already in CONTINUITY, keep prominent)
- raw grep -rn for any "zero references" claim (gitignore-filtered tools have a
  blind spot).
- A check that cannot fail is worse than no check.
- Provenance-pattern watch: "a rule adopted as a partial quotation" has recurred
  (R1, R2); G-43 looked like a fourth instance but was a true negative — the
  check fired and correctly cleared.
- Reference files edited in BOTH directions; diff-check the changed sections
  after every change.

## Do this
Fold the above into CONTINUITY.md at the right places (version log bump per its
§7; update the gap-status section; set NEXT = G-04 with its specifics). Confirm
the G-43 resolution actually committed before writing it as done — if it did
not, note it as "resolution ruled, commit pending." Commit the CONTINUITY
update. Report the commit hash and confirm G-04 is clearly marked as the next
gap for the new chat.
