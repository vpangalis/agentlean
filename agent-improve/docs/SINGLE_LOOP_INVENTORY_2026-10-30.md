# Single-loop inventory (read-only, 30–31 Oct 2026)

**Measured against:** `docs/founder-inputs/ADR_DRAFT_single_agent_loop_2026-10-30.md` (D1–D8) and
`TEST_STRATEGY_single_loop_2026-10-30.md` (T1 code · T2 replay · T3+T4 live golden cases · nightly journey).

**State:** the code at the Define baseline (tag `define-baseline-2026-10-30`, ff508e7). Nothing was changed.

**Method:**
- Three read-only code searches (skills and hooks; Azure AI Search; Define's searches, middleware and carry-over).
- My checks of the points that decide something (cited).
- Two live reads: the search service's index statistics, and the worktrees on disk.

## Findings that matter for the ADR

| # | Finding | Evidence | Bears on |
|---|---|---|---|
| 1 | **Define makes no knowledge search in practice.** Answer turns offer only `read_upload`. The three lookups are offered on teaching turns only, and a teaching turn is the card, written in code with no coach call. A Belt's methodology question gets no lookup. | `backend/middleware/turn_tools.py:24-29`; `nodes_common.py:1778-1790` | D4: the "search knowledge" tool and when the coach may call it |
| 2 | **Three of the 12 middleware layers make their own model call:** the summariser (on its trigger), the fallback (on failure) and the grader (every reply, log-only). Outside the stack there are the planner's judgment, query variants, the SIPOC reading, upload interpretation and vision, and the gate judge. | §d | D5, D6: the grader's call goes; its code checks seed reflection layer 1 |
| 3 | **What the ADR removes is mostly not middleware.** Validation is a graph node, not middleware. The contradiction layer makes no model call (it logs the coach's flag). The input guard is a graph node, not middleware. | `nodes_common.py:4271-4357`; `middleware/contradiction.py:73-94`; `core/guard.py:185-217` | D5: the keep/remove list should name graph nodes, not layers |
| 4 | **The pure parts carry over:** the card, Gate A–G, report, parse, calculations, upload parsing, the SIPOC core and the drawing functions. Their ties are data shapes plus three executor hand-offs: the SIPOC context variables, the chat-edit reply, and upload routing. | §e | Staging step 3 (wrap as tools) |
| 5 | **The run-through is wired into the gates:** guard rules 11 and 11b, the `docs(runthrough)` exemption, the staged-tree fast set, the CONTINUITY ratchet, the board's journey and the coach-input ratchet. | §a | Test strategy: nightly journey + T2/T3 replace it as acceptance |
| 6 | **Azure AI Search has one service and nine indexes.** Two retired Improve indexes still exist (`improve_knowledge_index`, `_v2`). The case index is empty and has no writer. | §b | D4 Look-up tools; cleanup is the founder's call |
| 7 | **The 11 agent worktrees hold 676 MB in OneDrive:** 6 are safe to remove, 5 hold files never committed. Two snapshot folders hold copies of `agent-improve/.env`. | §f | Housekeeping (list only) |

## a. Skills and hooks against the ADR and the test strategy

**Count:** 83 items. 49 still valid, 24 must change, 10 obsolete (9 guard rules already retired, plus one generated mirror).

### a1. Development skills (`.claude/skills/<name>/SKILL.md`)

| Name | What it does | Verdict | Why (one line) | Point |
|---|---|---|---|---|
| add-computation-tool | Adds a per-phase computation tool, its binding, the 7-step teaching block and rubric criterion | must change | One tool per calculation and a 16-tool cap vs one `calculate` over a formula library, 10 offered, teaching in the element block | D4, D4a, D3 |
| amend-rules | How a rule is amended | must change | Names `SupervisorState` / `PhaseState` / `CoachingResponse` amendments; those classes go | D8 |
| change-gate-schema | Fan-out for a new field on a phase output or `PhaseState` | must change | Its fan-out (state.py, substate.py, field order, validate.py, gate_assembly, grader) becomes case-state section, element order, save element, block, gate rubric | D8, D2, D4, D7 |
| eight-d | Work a defect as an 8D | still valid | Process, no design | — |
| new-requirement | Requirement → ADR → features → rank | still valid | Design-neutral; a feature could name its test level | T1–T4 |
| reconcile-docs | Drift and marker checks, each finding an 8D | still valid | The checks it calls change (a6), not the procedure | — |
| refactor-step-review | Review a step against the architecture and the rejected designs | still valid | Its refusals match the ADR; it should add: planner rules as a skill, subagents, a model tool selector, layer 2 before evidence | D1, D2, D5, D6 |
| upgrade-langchain-stack | Re-resolve and upgrade the LangChain pins | must change | The langgraph floor's reason is the nested-subgraph checkpoint fix, which the single loop drops | D1, D8 |
| verify-current-version | Check a pattern against live docs | must change | Maps sources to "our Planner/Executor/Grader"; calls "Building effective agents" not current while the ADR cites it; lacks the ADR's sources | D1 |

### a2. Runtime coaching skills (`agent-improve/skills/`)

| Name | What it holds | Verdict | Why (one line) | Point |
|---|---|---|---|---|
| dmaic-define-phase/SKILL.md | Element blocks `[1 · business_case]`…`[13]`, opening, calculate tool block, gate readiness | must change | The block shape already fits D3, but: capture through `fields_captured`, not save element; the mismatch flag; the allowed-tools list is not the D4 pool; tool teaching sits in a separate block | D3, D4, D5, D6 |
| dmaic-define-phase/coaching_script.md | Generated mirror of SKILL.md §3 | obsolete | One source per element block; only tests read the mirror | D3 |
| dmaic-define-phase/sipoc_example.json | The SIPOC worked example | still valid | Reference material, input to the drawing library | D3, D4a |
| dmaic-measure / analyse / improve / control | Phase skills written for the node design (§39, grader, one tool per calculation) | must change (deferred) | Staging step 6 re-checks them before Measure | D4, D6, staging 6 |
| extraction/*_extraction.md (5) | Raw eBook extractions | still valid | Source for element blocks and look-ups | D3 |

### a3. Hook registrations (`.claude/settings.json`, `.claude/settings.local.json`)

| Name | What it does | Verdict | Why (one line) | Point |
|---|---|---|---|---|
| SessionStart → session-start-context.py | Git state, board headline, versions, drift refusals, next failing feature per lane | still valid | No old-design content | — |
| PreToolUse Bash\|PowerShell → preflight-on-commit.py | Pre-flight before `git commit` | still valid | A trigger only (a6 for its logic) | — |
| PreToolUse Write\|Edit → pre-tool-use-drift-check.py | Blocks deprecated patterns | must change | Several patterns guard the node design (a6) | D1, D8 |
| PreToolUse Write\|Edit → fact-ownership-guard.py | Denies restated owned facts | must change | Its owner registry names state.py / substate.py | D8 |
| InstructionsLoaded → instructions-loaded-log.py | Logs which rule files load | still valid | — | — |
| Stop → drift-check.py --quiet | Owned-fact drift check | must change | Same registry | D8, D5 |
| Stop / Notification (local) → ntfy | Phone notifications | still valid | No design content | — |
| permissions.ask (not a hook) | Live scripts that prompt first | must change | Names planner_repeatability and validation_repeat (both go) and define_runthrough (becomes nightly); no golden-case runner yet | D1, T3 |

### a4. Git hooks (`.githooks`, `core.hooksPath` absolute)

| Name | What it does | Verdict | Why (one line) | Point |
|---|---|---|---|---|
| core.hooksPath | Points git at the tracked hooks | still valid | An absolute path: fragile on another clone | — |
| commit-msg | Runs the guard (a5) | still valid | — | — |
| pre-commit → generate_models / layout / routes / value_keys | Regenerate the generated docs | still valid | Follow the code | D8 |
| pre-commit → generate_middleware_order.py | Middleware order from `_build_executor` | must change | The builder goes; middleware moves onto the one coach | D1, D5 |
| pre-commit → generate_define_script.py | Criteria, order and welcome from `criteria.py` | still valid | Already "order in code"; could emit the element blocks | D2, D3 |
| pre-commit → staged_tree.py --fast/--suite | One test run on the staged tree | must change | Its fast set includes the run-through record tests; needs T1 mapped + smoke and T2 replay under 5 min | T1, T2 |
| pre-commit → mypy_ratchet / ruff_ratchet | Counts may only fall | still valid | Design-neutral | — |
| pre-commit → pre-commit-continuity + continuity_status | Status block and the feature ratchet | must change | Prints "re-run define_runthrough"; exemptions keyed to the run-through | nightly + segments |
| pre-commit → section_index, rank --check, adrs --write | Index, rank inputs, ADR index | still valid | — | — |
| pre-commit → wiring.py | Every component has a production caller | must change | Roots are `core.graph` and `_build_executor` | D1 |
| pre-commit → build_control_board + check_board | The board, checked against the tree | must change | The journey panel reads `define_runthrough_*.json` | T2, T3 |
| pre-merge-commit | pre-commit on merges | still valid | — | — |
| pre-push → pre_push.py | A push needs a passing full suite | still valid | "Full suite once per wave" fits | T1, T2 |
| prepare-commit-msg → timing_trailer | Timing trailer | still valid | Could add per-level wall times | Reporting |
| size_budget, normative_check, check_links, verify_rule_citations, annotation_only, doc_names, verify_rule_triggers, prompt_record | The logic behind rules 12, 13, 14, 17, 24 and manual checks | still valid | Design-neutral (rule 14 will need founder entries when skill sentences are dropped) | — |

### a5. Commit guard rules (`.claude/hooks/commit-msg-refactor-guard.py`)

| Rule | What it does | Verdict | Why (one line) | Point |
|---|---|---|---|---|
| 1, 2, 2b, 5, 8, 9, 15, 16, 23 | Retired (27 or 30 Sep / 27 Oct) | obsolete | Already retired | — |
| 3, 3b | mypy on changed files; whole-tree count may only fall | still valid | — | — |
| 4 | Suite green for this tree | still valid | What runs is staged_tree's choice (a4) | T1, T2 |
| 6 | A fix answers the six 8D labels | still valid | — | — |
| 6, `docs(runthrough):` exemption | Run-through record commits skip the 8D | must change | Records become nightly; T2's recorded answers need their own commit type | T2 |
| 7 | No scratch in the tree | still valid | — | — |
| 10 | Staged board agrees with the tree | still valid | The board's inputs change | — |
| 11 | A DEF lands when its test and its dependencies pass | must change | Run-through features land only on a fresh live record; the strategy lands on T2/T3 | T2, T3 |
| 11b | A passing feature keeps passing | must change | Exemptions keyed to run-through freshness; ratchet the golden cases instead | T2, T3 |
| merge check | 10/11/11b on merges | still valid | Inherits rule 11's change | — |
| 12, 13, 14, 18, 20, 22, 24, 25 | Size, links, normative, requirements, founder files, deprecated patterns, document names, ruff | still valid | Design-neutral; 14 and 24 will slow the migration on purpose | — |
| 17 | A §3 file change updates ARCHITECTURE.md or says `Design: unchanged` | still valid | Deleting nodes forces the §3 update | D1 |
| 19 | A DEF waits while its ADR is not ACCEPTED | still valid | This ADR is PROPOSED | — |
| 21 | An ACCEPTED ADR only changes to SUPERSEDED | still valid | The Pattern B, planner and grader ADRs will be superseded | D1, D6 |

### a6. Drift, ownership, pre-flight and logging scripts

| Name | What it does | Verdict | Why (one line) | Point |
|---|---|---|---|---|
| drift-check.py + `.claude/config/fact_owners.yaml` | Owned facts re-derived; documents must agree | must change | Owners: `SupervisorState`, `PhaseState`/`CoachingResponse`, the gate validator, middleware order from `nodes_common.py` | D8, D5, D7 |
| pre-tool-use-drift-check.py + `deprecated_patterns.yaml` | Blocks deprecated patterns | must change | Patterns about phase executors, subgraphs compiling with no checkpointer, dict routing | D1, D8 |
| fact-ownership-guard.py + `_fact_owners.py` | Denies restated owned facts | must change | `cites_owner()` hard-codes state.py and substate.py | D8 |
| preflight.py | Drift, types, tests of changed modules | must change | Nothing triggers T2 replay on coach, middleware, tool or state changes | T1, T2 |
| session-start-context.py, instructions-loaded-log.py | Context and rule-load log | still valid | — | — |
| coach-input-ratchet.json + test_run_records.py | Input-token ceilings per coach call type | must change | Measured from run-through records; the strategy measures it at the live level | T3, T4 |

## b. Azure AI Search: who uses it, which indexes exist

**Service:** one, `valuesims-search-service`. Statistics read live on 31 Oct (read-only `get_index_statistics`). Agent Resolve has no `.env` in the repo; its indexes are on the same service.

| Index | Docs | Storage (vector) | Owner | Written by | Queried by | Note |
|---|---|---|---|---|---|---|
| improve_knowledge_index_v3 | 1,184 | 45.7 MB (13.9) | Improve, methodology | `scripts/ingest_knowledge.py` (confirms before writing) | `rag_lookup_methodology` → `retriever.search_knowledge` | The live one (`core/config.py`) |
| improve_knowledge_index_v2 | 1,184 | 45.7 MB (13.9) | Improve | — | — | Keyword interim, "delete when v3 confirmed" (CONTINUITY) |
| improve_knowledge_index | 1,369 | 53.0 MB (16.1) | Improve | — | — | Retired (contaminated corpus); its name is a banned pattern |
| improve_evidence_index | 139 | 5.7 MB (1.6) | Improve, uploads | `routes._index_upload` on POST /upload; `backfill_evidence_index.py` | `rag_lookup_evidence` (filter case_id + kind) | Test cases' uploads only (D8) |
| improve_case_index | 0 | 0 | Improve, past cases | **no writer** (T98 / DEF-236 not written) | `rag_lookup_case_history` | Vector field `embedding`, the others `content_vector` |
| case_index_v3 | 43 | 1.9 MB (0.7) | Resolve, cases | Resolve's case manager and seed scripts | Resolve; Improve's `search_resolve_cases` (unbound) | — |
| knowledge_index_v2 | 113 | 4.7 MB (1.3) | Resolve, knowledge | Resolve `POST /entry/knowledge` | Resolve; `search_resolve_knowledge` (unbound) | — |
| knowledge_index_v1 | 177 | 14.2 MB (2.2) | Resolve (older) | — | not referenced by Improve's config | Probably superseded by v2 (unverified) |
| evidence_index_v1 | 7 | 0.5 MB (0.0) | Resolve, evidence | Resolve entry handler | Resolve; `search_resolve_evidence` (unbound) | — |

**Other users of the service:**
- **Agent Flow:** none. `search_flow_vsm` is a stub returning "not yet available" (`knowledge/tools.py:446-451`).
- **The four cross-agent tools** (`search_resolve_*`, `search_flow_vsm`) are present and unbound, by rule.

**Unverified, worth checking before D4's search tools:**
- **Field names:** Improve's `search_resolve_*` pass no field names. The installed LangChain `AzureSearch` takes field names only from `AZURESEARCH_FIELDS_*` environment variables, so vector queries probably go to `content_vector` on Resolve indexes whose vector field is `embedding`.
- **A missing index name is created:** LangChain creates an index whose name does not exist.
- **Key variables differ:** Improve uses `AZURE_SEARCH_API_KEY`, Resolve `AZURE_SEARCH_ADMIN_KEY`, on the same endpoint variable.

## c. Which knowledge searches Define makes

| Tool | Index | How it searches | Offered on | Called in Define? |
|---|---|---|---|---|
| `rag_lookup_methodology` | improve_knowledge_index_v3 | Query + 3–5 variants (a model call each), RRF k=60, top 10, filter `phase_relevance` | Teaching turns only | **Effectively never**: a teaching turn is the card with no coach call (finding 1) |
| `rag_lookup_case_history` | improve_case_index (empty) | Variants + RRF, completed cases, own case dropped | Teaching only | Never |
| `rag_lookup_evidence` | improve_evidence_index | Variants + RRF, filter case_id + kind | Teaching, upload | On upload turns, by the coach's choice |
| `read_upload` | One blob file of the case (no index) | Up to 12,000 characters; pictures from the kept text or a vision read | Teaching, upload, answer | Yes; the only tool an answer turn offers (ADR-0115) |
| `read_sipoc` | No index; one extraction call | Merges with the SIPOC read so far | Answer and upload turns at element 12 | Yes, at element 12 |
| `load_evidence_series` | Re-parses the uploaded file | — | Upload | Mostly called by code itself on upload turns (`_dispatch_routed_read`) |
| `propose_diagram`, `calculate_expected_savings` | — | — | No turn type | Never offered; savings are computed in code, though SKILL.md still names the tool |
| `search_resolve_*`, `search_flow_vsm` | Resolve / none | — | Unbound | Never |

- **Searches the code makes itself:** none. The planner's retrieval strategy is a constant `single_hop` that is only logged.
- **Tool count:** at most 4 tools + the structured reply on one Define call (an upload turn at element 12). 10 tools are registered.

## d. The 12 middleware layers (`_build_executor`, `nodes_common.py:1104-1211`) and their model calls

| # | Layer | Own model call? | ADR D5 |
|---|---|---|---|
| 1 | BeforeModelStateInjection (`middleware/state_injection.py:233`) | No | Keep (dynamic part already last) |
| 2 | DMAICSkillsMiddleware (`middleware/skills.py:533`), the element block, `load_skill` | No | Keep as element-block injection; `load_skill` does not fit D3 |
| 3 | SummarizationMiddleware (100k-token trigger) | **Yes**, `summarizer`, only on the trigger | Keep |
| 4 | TurnTools (`middleware/turn_tools.py:49`) | No | Keep (tools per phase and state, in code) |
| 5 | ModelCallLimitMiddleware (coach_limit = 4 − judgment − 1) | No | Keep |
| 6 | ModelFallbackMiddleware | **Yes, on failure only** (the fallback deployment) | Keep |
| 7 | ModelRetryMiddleware (2) | Re-sends the same call | Keep |
| 8 | KeptFromFallback (`middleware/fallback.py:49`) | No | Goes with retry and fallback |
| 9 | ToolRetryMiddleware (2, continue) | No | Keep |
| 10 | PIIMiddleware (tool results, regex) | No | Keep, tuned |
| 11 | DMAICGraderMiddleware (`middleware/grader.py:273`) | **Yes**, `grader`, once per reply (log-only) | Not on the keep list: D6 replaces G1–G6; its code checks are layer-1 candidates |
| 12 | ContradictionDetectionMiddleware (`middleware/contradiction.py:64`) | **No**: logs the coach's own flag | "Remove" — there is no separate model layer to remove |

**Model calls outside the stack, per Define turn (budget 4):**

| Call | Role | When |
|---|---|---|
| The planner's judgment (`nodes_common._judge`) | planner | The Belt answered and code did not decide; it also extracts the calculation inputs |
| The coach | coach | Only when code does not write the reply |
| Query variants (`knowledge/fusion.py`) | query_variants | Once per lookup, at most 3 |
| SIPOC reading (`knowledge/sipoc.py`) | extraction / vision | The coach calls `read_sipoc`, or an upload at element 12 |
| Upload interpretation (`upload/agent.py`) | extraction / vision | POST /upload |
| Prompt Shields (`core/guard.py`) | Content Safety | Every message and upload |
| Gate judge (layer 2d, `validation/rubric.py`) | gate_judge | Once per submission, after layer 2b |

## e. What carries over unchanged

| Part | Files | Tie to the old design | Verdict |
|---|---|---|---|
| Element card | `phases/define/templates.py` `teaching_card`, `card_text` | None by import; its only caller is the executor | Carries over |
| Read-back card | `templates.card`, `rows`, `verbatim_spans` | Data: "in your answer" quotes come from the planner's judgment | Carries over; the quote source moves to save element / reflection |
| Gate A–G, report | `templates.gate_view`, `gate_card`; `phases/define/report.py`; `visuals.report_visuals` | None (case-record data) | Carries over |
| SIPOC tool | `knowledge/sipoc.py` (read, draft, gaps); wrapper in `knowledge/tools.py` | `coach_reading` uses the executor's context variables | Core carries over; the hand-off becomes the tool's artifact |
| Change by chat | `define/parse.py` `chat_edits`, `change_asked`, `apply_team_edits`, `apply_text_edits`; `moves.chat_edit` | parse: none; `chat_edit` is called inside `moves.decide` (planner) and its reply is executor code | parse carries over; the routing becomes the save element tool's |
| Value parsers | `define/parse.py` (metric_value, calendar_date, team_rows, process_steps, …) | None | Carries over (T1) |
| Calculations | `phases/calculations.py` | Inputs come from the planner's judgment | The formula library (D4a); inputs from the calculate tool |
| Uploads | `upload/parsers.py`, `classifier.py`, `agent.py` | Routing an upload into a turn is executor code | Carries over; routing changes |
| UI drawing | `ui/index.html` card, read-back, strip, benefit bars, SIPOC, 5W2H | The response contract (`teaching_card`, `move_field`) | Carries over; `move_field` changes meaning |
| Tests, pure functions (~12 files) | test_templates, test_moves, test_uploads, test_computation, test_fusion, test_retriever, … | None | Carry over as T1 |
| Tests through the graph | test_define_e2e (268), test_wiring, test_gate_acceptance, … | The stubbed planner, step_log keys | HTTP assertions carry over; plumbing changes |
| Tests of executor and middleware units | test_executor, test_middleware, test_hop_cap, test_turn_budget, … | Build CoachingPlan / PhaseState | Must change |
| Run records, live slice | `docs/runthrough/` (~295 files); `scripts/live_slice.py` | Seeding through `moves.positions` and the phase record in the checkpoint | Records are history (the baseline); the slice's seeding changes; golden cases replace both |

## f. `.claude/worktrees` — list only, nothing removed

**Count:** 13 folders, **676 MB**, all inside OneDrive and git-ignored.

**How "safe" was decided:**
- **Agent worktrees (11):** each sits on a commit main contains. "Safe" means every uncommitted file's exact content already exists in git. Checked with `git hash-object` against the object store.
- **Snapshot folders (2):** plain copies of a tree, with no git of their own.

| Folder | Size | Head | Uncommitted files | Never committed | Safe to remove? |
|---|---|---|---|---|---|
| agent-a2ad8c841551dd596 | 35 MB | 5b0caf4 (24 Oct) | 7 | 0 | **yes** |
| agent-a342c02d0b91c9d2c | 35 MB | 77697e1 (24 Oct) | 15 | 0 | **yes** |
| agent-a4c0b5fe347ac3bdc | 35 MB | 5b0caf4 (24 Oct) | 1 | 0 | **yes** |
| agent-a5632035aa45a4037 | 49 MB | 8f6b187 (26 Oct) | 14 | 0 | **yes** |
| agent-aab5ac3554cb57ebe | 35 MB | 77697e1 (24 Oct) | 17 | 0 | **yes** |
| agent-abb5d793031b57fd8 | 35 MB | 77697e1 (24 Oct) | 16 | 0 | **yes** |
| agent-a035bfce5b87faa3e | 35 MB | 5b0caf4 (24 Oct) | 6 | 2 (define/schema.py, validation/rubric.py) | look first |
| agent-a098c705f80799ad5 | 107 MB | 7eee98a (24 Oct) | 1 | 1 (nodes_common.py) | look first |
| agent-a10c6fd06807e445a | 101 MB | 8f6b187 (26 Oct) | 6 | 2 (test_define_runthrough.py, test_run_records.py) | look first |
| agent-a6f2d112ea307b1e1 | 105 MB | cd1be49 (27 Oct) | 14 | 1 (docs/code-layout.md) | look first |
| agent-a8f94c8b9af93785a | 35 MB | 77697e1 (24 Oct) | 20 | 1 (gateway/schemas.py) | look first |
| e19-at-5b0caf4 | 37 MB | snapshot of 5b0caf4 | 1,071 files (979 at the commit) | holds a copy of `agent-improve/.env` | yes, once you agree; the copy of the secrets should go |
| gate-at-define-v1 | 37 MB | snapshot of tag define-v1 | 1,028 files (991 at the tag) | holds a copy of `agent-improve/.env` | yes, once you agree; as above |

**Also found:**
- **Stale worktree entries:** `.git/worktrees` holds metadata for worktrees that no longer exist (AgentLean-test, e19-at-5b0caf4, agentlean-walk-4eb1c3e from yesterday's script test). `git worktree prune` would clear them.
- **Walk and run-through worktrees in Temp, outside OneDrive:**
  - agentlean-walk-ff508e7 serves :8020 now; keep it.
  - agentlean-walk 19e6625, 58e6447, 753ae19, 9826a3f and b2d304c are locked and old.
  - agentlean-dev-288 is the run-through side worktree.
  - agentlean-staged/* are the pre-push trees.
