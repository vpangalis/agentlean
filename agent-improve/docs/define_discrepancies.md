> **Step 6.66, Part 5d** — where the four sources (ARCHITECTURE.md, the procedure, the code, Anthropic/LangChain guidance) disagree on Define, each decided by the ladder: a) what IS (code and a test run at HEAD), b) what SHOULD BE (the latest founder ruling), c) HOW (official docs, checked against the installed version), d) the smaller reversible option, marked **FOR FOUNDER**. Written 2026-09-25 by reading at HEAD `189c672`: procedure line numbers below are from BEFORE that night's slimming — the text moved verbatim to `docs/_archive/REFACTORING_PROCEDURE_slimmed_2026-09-25.md`; find current lines through `docs/section-index.md`. Replace an entry when it is decided; do not append history.

# Where the four sources disagree, and how each disagreement is decided

**Line numbers.** `PROC` is `agent-improve/docs/REFACTORING_PROCEDURE.md` at HEAD (`189c672`, which
has the same procedure bytes as `5d29baa`). A peer session has since staged a slimmed copy.
`ARCH` is `agent-improve/ARCHITECTURE.md` v1.77. Code paths are relative to `agent-improve/`.

**The ladder, applied to each item in order:**
- **a) IS:** the code, plus a test run at HEAD.
- **b) SHOULD:** the latest founder ruling beats older text. That means CLAUDE.md, ARCH §56, and the 2026-09-25 rulings.
- **c) HOW:** the official Anthropic, LangChain and LangGraph docs, checked against the installed versions. These are langgraph 1.2.11, langchain 1.3.16, langchain-core 1.6.0 and langgraph-checkpoint 4.1.0. `interrupt(value)` and `Command(resume=…)` were confirmed importable from `langgraph.types`.
- **d) Still open:** take the smaller option that can be undone, and mark it **FOR FOUNDER**.

No founder ruling is invented here. Where a decision needs one, the item says so.

## Summary

| # | Disagreement | Decided by | Decision |
|---|---|---|---|
| D1 | The contradiction stop: restore the middleware `interrupt()` (7.3 clause 1), or move the stop into a node (6.44) | d | **FOR FOUNDER.** Smaller option: the node (6.44). The LangGraph docs support it |
| D2 | What "Define works end to end" means: the five clauses (quality does not gate), or 7.9 (every one of the 35 rows green) | d | **FOR FOUNDER.** Measure both. Report the five-clause subset as the headline distance |
| D3 | Rows 26–32 need a person watching a traced turn; 6.66 wants pass/fail only from automated tests, with tracing off | d | **FOR FOUNDER.** Tests prove the structural half from the audit record. The rows stay founder-marked |
| D4 | The approval gate: §33 has three routes plus an interrupt; the tree has one `POST /gate` that writes at once, and the UI's "approve" button calls it | a/b | IS is the direct write. SHOULD is §33 plus 7.3/7.7. Features encode §33 |
| D5 | ARCH §33 says position 6 pauses today; the code has 0 `interrupt()` call sites | a | Code wins. The ARCH note is stale |
| D6 | An interrupt inside a subgraph that is called from a wrapper node: on resume, what re-runs? | c | The docs say a node re-runs from the start. 7.3 must prove this with a fake-model test on 1.2.11 |
| D7 | 6.45 (planner decides on field completeness, row 4) against 6.61 (code picks the first unconfirmed field) | b, then d | 6.61 is later and delivers row 4's behaviour. **FOR FOUNDER:** re-scope 6.45 to gate routing |
| D8 | 7.9's precondition says "Order 1–19"; 7.9 now sits at Order 21 and 7.8 at 20 | d | **FOR FOUNDER.** Reword it as "every Order position before 7.9" |
| D9 | 10.4 is Order 11, but its precondition is 8.1, which is in no Order and not started | d | **FOR FOUNDER.** Narrow the precondition, or add 8.1 to the Order |
| D10 | 7.8's card says "off the Define critical path"; Order 20 and the Define path table include it | b | Order (2026-09-25) wins. The card text is stale |
| D11 | Appendix I says "Order is DERIVED from story rank"; the 2026-09-25 ruling says "Priority = Appendix F Order column" | b | The later ruling wins. Appendix I lines 8377–8417 are stale |
| D12 | Row 2 is 🟢 in the register and CONTINUITY says 15 proven; the generated board says 14, because row 2's check is skipped in CI | a/b | The derived count (14) is right. The hand-written line is stale |
| D13 | Steps counted DONE while rows they own have no check (10.0 → row 15; 6.46 → rows 26–32) | a | This follows `progress.py` (done = wired or proven). Rows stay red. Features give the missing checks |
| D14 | Appendix F shows ☐ for 6.42 and 6.48 (and 6.20); their rows are proven and the code is landed | a | The code and tests win. This is G-86 (the State column is hand-kept) |
| D15 | 6.20 was #2 on the 2026-09-23 critical path; it is absent from the 2026-09-25 Order; row 10 is still red | b, then d | The Order wins on priority. **FOR FOUNDER:** where 6.20's last clause (row 10) lands |
| D16 | WATCH 7 and code docstrings say "the Define gate is inert / artifacts stays empty"; the gate has passed on real case 1FF | a | The code wins. The comments are stale; record only, since no `backend/` edits are allowed tonight |
| D17 | ARCH §39.1.2 says "16 fields in total"; the schema and §40/§63.1 say 18 | a | 18 (`DefineOutput.model_fields`) |
| D18 | Open gaps whose Step cell disagrees with where they are actually owned or closed (G-78, G-89, G-23, G-40) | a/b | Update the gap rows. The features cover them either way |
| D19 | `build_board.read_gaps` docstring against its behaviour, and the guard's register against the brief's wording | a | Code behaviour is recorded. Use a new `progress.gaps()` reader |
| D20 | The Anthropic article (agent flips a `passes` field; browser testing) against the founder ruling (no status field, status from `test-results.json`) and this environment (no Playwright) | b, then d | The founder ruling wins. Lane C uses headless node checks for now. **FOR FOUNDER:** browser automation later |
| D21 | Row 24 has no owning step, but 7.9 needs every row green | d | **FOR FOUNDER** (part of D2) |
| D22 | The gate write is the route's (`POST /gate`); §33.2 puts it in `gate_apply`, with the output mapper | a/b | IS is the route. SHOULD is §33.2 at 7.3 (clause 3: one writer or an ETag) |
| D23 | The memory note says the UI's v1 names go at 10.2; G-107 (2026-09-25) gives them to 10.3 | b | 10.3 |
| D24 | The recorded test run is volatile: a concurrent session's source change turns every status amber | a | The coverage test must not read status (see coverage_map.md) |

---

## Details

### D1 — The contradiction stop: middleware `interrupt()` or a node?

- **PROC:4079 (7.3 clause 1, ruled 2026-09-11):** the guard on middleware position 6 is removed and
  its `interrupt()` restored, "with a resume route PROVING it".
- **PROC:5512 (6.44 Done-when, a later ruling that carries the §37 correction, ARCH v1.69):** "the stop
  lives in a node that writes nothing; a resumed turn is proven to write once."
- **PROC:4129:** "CLAUSE 1 AND STEP 6.44 DISAGREE — RECORDED 2026-09-23, NOT RESOLVED … this is a
  founder's call."
- **Code:** `backend/middleware/contradiction.py:116–165`. The `interrupt(self._payload(flag))` line is
  commented out. `verify_built.py` reports "interrupt() call sites (§33) 0 0".
- **Docs:** `interrupt()` pauses a graph node that has a checkpointer and a thread id. Resuming
  re-runs that node from its start, so side effects before the interrupt must be idempotent
  (https://docs.langchain.com/oss/python/langgraph/interrupts). G-15 (PROC Appendix G) records that
  an exception raised from `after_agent` is not resumable.
- **Decision:**
  - a) Nothing pauses today.
  - b) 6.44's placement is the later ruling, but PROC explicitly leaves the conflict to the founder.
  - c) The docs favour a node.
  - d) **FOR FOUNDER.** The smaller option that can be undone: build the stop as a node (6.44), and
    make 7.3 clause 1's three checks assert that the *node's* interrupt resumes, rather than
    restoring the middleware line.
  - Feature DEF-040 is written to that shape, and its test name does not assume where the stop lives.

### D2 — What "Define works end to end" means

- **PROC:369–386:** the five clauses. "What is QUALITY, and therefore follows rather than gates":
  grading (Layer 2d, row 22), the polished gate screen (10.2), reading uploads (6.43), and the
  planner's real predicate (6.45).
- **PROC:4267 (7.9 Done-when, ruled 2026-09-25):** "every Define capability row in Appendix H is
  green on one fresh case that carries an upload". That includes row 22 (blocked on the rubric
  text), row 24 (no owning step), row 9 (6.43) and rows 26–32 (live-turn, founder-marked).
- **Code:** `tools/control_board/progress.py:582`. `forecast_define` is 7.9's end date, which is why
  the forecast is "conditional on G-23, G-40".
- **Decision:**
  - b) 7.9's card is the later ruling, but it cannot be satisfied while row 24 has no owner.
  - d) **FOR FOUNDER.** The smaller option that can be undone: the feature list tags each feature
    with its clause. The morning measure reports two numbers:
    1. The five-clause core: every feature whose clause is C1–C5 *and* whose covered rows exclude
       22, 24 and 26–32.
    2. All 64 features.
  - Nothing is removed from 7.9.

### D3 — Rows the founder must watch, against a pass/fail that comes only from tests

- **PROC:8158–8185 (Appendix H exception, 2026-09-23):** rows 26–32 "cannot go green in CI and cannot
  go green without a person". The record carries the LangSmith trace id.
- **PROC 6.66 Done-when:** the run-through runs with tracing off. The harness pass/fail comes only
  from tests. `docs/harness-progress.md` Part 7 says the same.
- **Decision:** d) **FOR FOUNDER.** The smaller option that can be undone:
  - DEF-005, 011, 016, 018 and 019 test the *structural* half of their row from the run-through's
    audit record. For example: an `example` block is present before the `prompt` on a teach move,
    and no captured value equals a script example. No reply contains `http`.
  - A passing feature does **not** turn the row green. The row stays founder-marked, on a traced run
    (6.56, which is held).

### D4 — The approval gate

- **ARCH §33:**
  - The Frontend sequence (ARCH:3944): `POST /gate/submit`, then an interrupt, then
    `/gate/approve` or `/gate/reject`.
  - §33.2: `gate_apply` writes the document to the store and to `final`.
  - §33.3: the checkpoint commits only after approval.
- **Code:**
  - `backend/gateway/routes.py:1389` `submit_gate` runs the graph and, if 2b passes, calls
    `blob.write_phase_gate` (`:1482`) and advances the phase. There is no pause.
  - `backend/phases/nodes_common.py:2139` `gate_review` and `:2164` `gate_apply` are pass-throughs.
  - `ui/index.html:3307` `gate-approve-btn` calls `submitGateReview()` (`:6190`), which calls
    `POST /gate`.
  - G-47 (PROC:7887) records the route mismatch.
- **Decision:** a) Today, "approve" means "submit, and write immediately". b) §33 is ratified and 7.3
  and 7.7 build it. Features DEF-047 to DEF-051 and DEF-060 encode §33. HOW:
  https://docs.langchain.com/oss/python/langgraph/interrupts (approve/reject by routing on the
  resume value with `Command(goto=…)`). `HumanInTheLoopMiddleware` is tool-call-only
  (https://docs.langchain.com/oss/python/langchain/human-in-the-loop), which agrees with §19.9's ban
  on it for gates.

### D5 — ARCH §33 says one thing pauses today

- **ARCH:3876:** "CORRECTED 2026-09-11 … one thing does [pause]: `ContradictionDetectionMiddleware`
  calls `langgraph.types.interrupt`".
- **Code:** `backend/middleware/contradiction.py:72–78` says "Since 2026-09-11 the `interrupt()` call
  is GUARDED". `verify_built.py` reports 0 call sites.
- **Decision:** a) Nothing pauses. The ARCH note predates the same-day guard ruling. Record it for
  the next ARCH amendment.

### D6 — Resuming an interrupt in the Define subgraph

- **Design:** the Define subgraph runs inside a uniquely named wrapper node, and the mapper runs
  inside it (G-42, resolved). `backend/gateway/routes.py:762` notes that "the input mapper rebuilds
  the child state on every invoke".
- **Docs:**
  - A resumed **node** re-executes from its beginning
    (https://docs.langchain.com/oss/python/langgraph/interrupts).
  - The parent must have a checkpointer for subgraph interrupts to work
    (https://docs.langchain.com/oss/python/langgraph/use-subgraphs). The fetched page also says
    "only the interrupted node re-executes — not the entire parent node" for the subgraph-as-node
    case.
- **Decision:** c) The docs do not settle the wrapper-node case for 1.2.11. 7.3 must first write a
  fake-model test: interrupt at `gate_review`, then resume with `Command(resume=…)` through the real
  wrapper. It must assert that the mapper's re-run does not reset `artifacts`, `field_status` or
  `gate_attempts`. That test is DEF-047 and DEF-048's precondition. Not FOR FOUNDER; it is a
  question of how.

### D7 — 6.45 (field completeness) against 6.61 (the move decided in code)

- **PROC:5521–5548 (6.45, 2026-09-23):** "the real S-F13 DP1 predicate replaces the turn-count
  placeholder" (`nodes_common.py:326`). Row 4: "field two is asked only once field one is complete".
- **Code at HEAD:**
  - `backend/phases/moves.py:206` `current()` returns the first position not confirmed. That is
    row 4's behaviour, landed at 6.61 (2026-09-25).
  - The routing placeholder is still there: `backend/phases/nodes_common.py:328–333` routes on
    `turn_count`, and `:392` logs "G-01 — DP1 is founder-owned … terminating placeholder".
- **Decision:**
  - b) 6.61 is later and already decides the field.
  - d) **FOR FOUNDER:** re-scope 6.45 to the *gate-routing* half of DP1 (when a turn routes to the
    validation stack), or retire it. The smaller option that can be undone: keep the card, and let
    DEF-011's route-level test write row 4's check against `moves.current`.

### D8 — 7.9's precondition range

- **PROC:4261:** "every Define-path step before it (Appendix F's `Order` 1–19)".
- **Code:** `tools/control_board/progress.py:200–215` (`_ORDER_RANGE`) expands "1–19" to Order
  positions 1–19. That is now 6.63 to 7.5, which leaves out **7.8 (Order 20)**. The range was
  written before 6.63–6.65 were inserted at positions 1–3.
- **Decision:** d) **FOR FOUNDER** (the card is ruled text). Smaller option: reword it as "every
  Order position before 7.9", which is stable under insertion.

### D9 — 10.4's precondition is outside the Order

- **PROC:6691:** 10.4's precondition is **8.1** ("Not started"). 8.1 is not in the Order.
- **Code:** `progress.schedule` ignores dependencies with no end date (`progress.py:570`), so the
  plan shows 10.4 as schedulable.
- **Decision:** d) **FOR FOUNDER:** narrow 10.4's precondition (DEF-055 needs only a readable error
  on screen), or add 8.1 to the Order.

### D10 — 7.8 "off the critical path" against Order 20

- **PROC:4225:** 7.8's card says "*(empty — this step is off the Define critical path)*".
- **PROC:7766:** the estimate table lists 7.8 at WP4. Order 20.
- **Decision:** b) The Order is the 2026-09-25 ruling. The card line is stale.

### D11 — Appendix I on Order

- **PROC:8377:** "Appendix F's `Order` column is DERIVED from story rank."
- **PROC:8419–8425**, `tools/control_board/stories.py:5–7` and PROC:7737: "Priority = Appendix F
  Order column" (founder 2026-09-25).
- **Decision:** b) The later ruling wins.

### D12 — Row 2: 14 or 15 proven?

- **PROC:8258** (register 🟢) and **CONTINUITY.md:64** say "15 of 35 … Green: 1, 2, …".
- **Code:** `test-results.json` records `test_row_2_a_turn_returns_a_coached_reply` as **skipped**. It
  is opt-in: `CAPABILITY_LIVE_TURN=1`, at `backend/tests/test_capability_rows.py:503`. So
  `progress.py` counts row 2 red, and the generated headline (CONTINUITY.md:10) says **14 of 35**.
- **Decision:** a/b) Derived is right (6.63, 2026-09-25). DEF-002 gives row 2 a CI-runnable e2e test
  through the route, with fakes.

### D13 — Steps counted done while rows they own have no check

- **Code:** `progress.py:481`. `done = wired or proven or tooling`. `proven` needs every owned row
  proven, but `wired` alone is enough.
- 10.0 is wired (`test_wired_10_0…`). Row 15, which it owns, reads "*pending — 10.0 writes it*"
  (Appendix H).
- 6.46 is wired. Rows 26–32, which it owns, are red.
- **Decision:** a) This is consistent with the 6.63 ruling ("DONE only when WIRED or PROVEN"). The rows
  stay red. DEF-052 is the check row 15 is owed.

### D14 — Appendix F ☐ against landed code

- **PROC:7467, :7474** show 6.42 and 6.48 as ☐ with anchor "—". **PROC:7465** shows 6.20 ☐.
- **Code:**
  - `routes.py:1482` uses `assemble_gate_document` (6.42).
  - `backend/tests/test_declared_types.py` passes (6.48).
  - `backend/phases/define/schema.py:339` has `define_phase_metrics` (6.20's scorecard half).
  - Rows 18, 19, 20 and 21 were green at `5d29baa`.
- **Decision:** a) Landed. This is the G-86 class: Appendix F's State is hand-kept. Coverage keys on
  steps, not on F State.

### D15 — Where 6.20 stands

- **PROC:400:** 6.20 is #2 on the 2026-09-23 critical path.
- The 2026-09-25 Order (PROC Appendix F) does not contain 6.20.
- 6.20's Done-when needs `computation_results` (row 10), `field_index`, and a browser view of a
  computed figure.
- **Code:**
  - `nodes_common.py:1378` (`_computation_results`) and `:1444` (`_advance_field_index`) exist.
  - Row 10's check is skipped: no calculation turn exists.
- **Decision:**
  - b) The Order wins on priority.
  - d) **FOR FOUNDER:** whether row 10 is proven by 6.56/6.58's calculation turn, which is what DEF-016
    and DEF-017 assume, or 6.20 re-enters the Order.

### D16 — "The Define gate is inert"

- **PROC:460 (WATCH 7):** the gate is "non-functional"; this was superseded by Route A.
- **Docstrings:** `backend/phases/define/nodes.py:36–43` ("`artifacts` stays empty … The Define gate
  is inert") and `backend/gateway/routes.py:1418` ("The Define gate remains inert (WATCH 7)").
- **Code and tests:** `test_wired_6_33_a_capture_reaches_the_artifacts` passes. Case `IMPR-2026-1FF`
  passed the gate, per the Appendix H note on rows 20–21. Rows 19–21 were proven.
- **Decision:** a) The code wins. The comments are stale. Record only; tonight's ruling allows no
  `backend/` edits outside tests.

### D17 — The field count

- **ARCH:4581:** "16 fields in total: 12 required, 4 gate metadata".
- **Code:** `backend/phases/define/schema.py:146` `DefineOutput`. "18 fields … §40 and §63.1 have
  said 18 since". The live `/gate/review` returns an eighteen-key document (PROC Appendix H note).
- **Decision:** a) 18. The ARCH line is stale (pre-v1.15).

### D18 — Gap rows that disagree with their owners

- **G-78** (PROC:7916) is open and **unscheduled**: "every coached field capture destroys the ones
  before it". 6.33 fixed accumulation, and `test_wired_6_33…` and row 5 prove it.
  - Decision: a) the code says fixed at 6.33. **The row was NOT closed** — closing a register row is not done here; recommended, FOR FOUNDER. DEF-037 keeps it covered.
- **G-89** (PROC:7932): Step reads "the procedure amendment". 6.44's Done-when (PROC:5516) says
  "closing G-89".
  - Decision: b) 6.44 owns it.
- **G-23 and G-40** (PROC:7979, :7999): Step reads "unscheduled". The milestone table (PROC:7774–7775)
  says G-23 blocks 7.1 and G-40 blocks 7.2.
  - Decision: b) The milestones are the 2026-09-25 statement. The gap Step cells are stale.

### D19 — The gap readers

- **`.claude/hooks/build_board.py:601–611`:** the docstring says "Today only ARCHITECTURE.md carries
  §66 … TEMPORARY — collapses … at step 6.38", and that `refs` is "the sections the gap affects".
  - Behaviour: it reads the procedure's Appendix G first. `refs` is the last cell, which is now the
    **Step** column, with `**` left in (`read_gaps()['G-102']['refs'] == {'**6.59**'}`).
- **The brief** says the guard resolves gaps against ARCH §66. The guard actually reads Appendix G:
  `.claude/hooks/commit-msg-refactor-guard.py:677–689`, "ONE source since 6.38". ARCH §66 (ARCH:12053)
  is a NOT-MARKABLE pointer.
- **Decision:** a) Code behaviour is recorded. The coverage test should use a dedicated reader
  (coverage_map.md).

### D20 — The Anthropic harness pattern against the founder ruling and the environment

- **Article** (https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):
  - A JSON feature list with `category`, `description`, `steps` and `passes`.
  - Agents may edit only `passes`: "It is unacceptable to remove or edit tests".
  - End-to-end verification "as a human user would", with browser automation.
- **PROC 6.66 Done-when:** status comes from `test-results.json`. The brief says no status field.
- **Environment:** `playwright` and `selenium` are not installed (checked). The memory notes say to
  verify UI logic headlessly with node (v24.14.0 is present).
- **Decision:**
  - b) The founder ruling is stricter than the article and consistent with its intent. Keep no
    status field.
  - d) **FOR FOUNDER:** Lane C tests (DEF-052 to DEF-059) are route plus headless-node checks of
    `ui/index.html`'s functions for now. Real browser automation would be a new dependency, which
    needs the upgrade skill and a ruling.

### D21 — Row 24 has no owner

- **PROC:8242:** "Row 24 has NO owning step … waits on the graph owning its own boundary (stage 7)".
- **PROC:4267:** 7.9 needs every row green.
- **Decision:** d) **FOR FOUNDER** (with D2). DEF-062 is mapped and has no step.

### D22 — Who writes the gate document

- **ARCH §33.2 (≈3955–3983):** `gate_apply` writes the store and `final`. The output mapper publishes.
- **Code:**
  - `routes.py:1482` writes the record from the route.
  - `nodes_common.py:2164` `gate_apply` "applies nothing".
  - PROC:4102 (7.3 clause 3): "one writer, or the write carries its ETag".
- **Decision:** a) IS is the route. b) SHOULD is §33.2 at 7.3. DEF-060 encodes "written once, and
  store, `final` and case record agree".

### D23 — Who fixes the UI's v1 field names

- **Memory** (agent-improve-progress, 2026-09-10): "v1 names in UI go at 10.2 (UI) and 11.1".
- **PROC:7950 (G-107, founder 2026-09-25):** "10.3, reading the move from 6.61's field status".
  `ui/index.html:700–736` still uses the v1 keys.
- **Decision:** b) 10.3 (DEF-053).

### D24 — Volatile status

- **Observed:** `progress.progress()` read 11 steps done and 14 rows proven at 5d29baa. Later in the
  same session, a peer session's uncommitted Part 2–4 edits changed `source_hash`, and it read 0
  done and 0 proven. `test-results.json` was re-recorded at `a96decf51f98af6b` by that session.
- **Decision:** a) This is G-109's class. The coverage test must not filter by status.
  "Status only from tests" still holds for the board.
