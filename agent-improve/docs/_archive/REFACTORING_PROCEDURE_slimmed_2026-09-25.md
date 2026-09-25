# REFACTORING_PROCEDURE.md — text moved out on 2026-09-25

Text moved out of `agent-improve/docs/REFACTORING_PROCEDURE.md` by step 6.66,
founder ruling 2026-09-25 (documents hold only current binding text). Every
passage is VERBATIM, grouped under the heading of the section it came from, in
the procedure's original order; line numbers refer to the procedure at commit
`5d29baa`. Nothing here is binding: the procedure, `ARCHITECTURE.md` and
`CLAUDE.md` are. For a landed step the procedure keeps the heading, the header
table and the Done-when; everything else of the card is here.

---

## ⚑ STATUS BANNER — 2026-08-27 · the phase specs are now RATIFIED INPUTS

*Original lines 11–96.*

*Added, not rewritten. **No step is renumbered and no step's prose is
altered.** This document was written 2026-08-22, before the five phase reviews
ran; several steps below therefore reason about phase content as an open
question. It is no longer open.*

**What became ratified between 2026-08-22 and 2026-08-27:**

| Input | Where | State |
|---|---|---|
| The five per-phase specs | `ARCHITECTURE.md` **§39.1–§39.5** | ✅ ratified — ordered field list (`field_index`), tier split, bound tools, methodology guards, routing/gate conditions, cross-phase reads/writes, embedded coaching script |
| The five gate-document schemas | **§63.1–§63.5** | ✅ ratified — Define 18 / Measure 15 / Analyse 14 / Improve 14 / Control 17 |
| The 20 computation tools | **§69** (S-F37–S-F56) | ✅ **specified** — name, inputs, output shape, preconditions, phase binding. **Code is still this document's step 5.3** |
| The five Layer-2d rubrics | DEFINE / MEASURE / ANALYSE / IMPROVE / CONTROL | ✅ ratified — each phase's methodology guards as Tier-1 checks |
| The metric registry | `metric_definitions` + `phase_metrics`, **§63.8 / §63.9** | ✅ ratified — single-authority invariant live in `core/metrics.py`, unit-tested across all five phases |

**What this changes for the steps below — build against these, not around
them:**

- **Step 3.4** (`{Phase}Output` schemas + validators + UI) — the four
  outstanding phases now have a ratified field list, type and tier for every
  field. Its Stage-2 prompt no longer has to be "written after reading the
  audit" for *what the fields are*; §63.2–§63.5 answer that. The audit is still
  owed for the **UI** half, which is untouched for all five phases.
- **Step 4.1** (Define subgraph) and **4.4** (the other four) — the gate
  conditions, routing and per-phase state parameters the nodes wire up are
  specified in each §39.x.
- **Step 5.3** (the 20 tools) — §69 is the build spec. Names, signatures and
  preconditions are settled; this step writes the functions to them.
- **Steps 7.1–7.4** (validation and gates) — the five rubrics are the Layer-2d
  content.

**Gap status at this banner** (`ARCHITECTURE.md` §66 — 46 identified, 12 closed
or resolved, 34 open):

- **CLOSED, so no step below is waiting on them:** F-12, F-13, F-14 (findings,
  closed at the Analyse / Improve / Control reviews) and **G-25** (the
  computation layer, resolved at spec level by §69). *Checked: no step in this
  document names any of them in a Precondition — a `grep` for `G-25`, `G-27`,
  `G-28`, `G-36`, `F-12`, `F-13`, `F-14` returns zero hits here. Nothing to
  un-block.*
- **STILL OPEN, and both are build gaps carried by steps below:** **G-27**
  boundary mappers = **step 3.3**; **G-28** gate assembly for the four phases
  beyond Define (only Define's was written) = **step 3.4** and **7.1**.

### The resume point is step 2.4 — CONFIRMED

**One spine step of 38 is done** (2.3, the dependency upgrade), plus **9.0**
out-of-band. **The next step is 2.4** — `set_entry_point` →
`add_edge(START, …)`, one line and an import, `grep-absence` verify. Appendix D
agrees. The horizontal order then runs 2.5 → 3.3 → 3.4.

> **⚠ WATCH 7 is NOT a viable "small first step" — reassessed 2026-08-27.**
> It has been carried (in §0.2's gate table and in step 3.4's consequence note)
> as a contained migration of `phases/define/orchestrate.py` to the v2 field
> names. Reading the code says it is not contained: the v1 names are emitted by
> **`EXTRACTION_DEFINE` in `core/prompts.py`**, not by `orchestrate.py`, which
> merges them unfiltered; **four readers beyond the three cross-phase briefs**
> stand on them (`ui/index.html` 78 sites, `phases/measure/{orchestrate,
> validate}.py`'s metric seeding, `gateway/routes.py:433`, `upload/agent.py:89`);
> **three of the moves are not renames** (`primary_metric` + unit → the
> `metric_definitions` registry is scalar → registry; the **5W2H fields have no
> v2 home at all**, §39.1.3; `sipoc` gains a sixth key the generator never
> produces); and **Appendix B marks all five `orchestrate.py` DELETE, not
> REWRITE**. Step 3.4's own ruling would additionally force the `ui/index.html`
> rename into the same commit, under a `manual-UI` verify.
>
> **Consequence:** the Define gate stays inert until the v2 capture path exists
> — executor node → `CoachingResponse.fields_captured` → `artifacts` — which is
> the 4.1 / 6.1 / 6.2 run, not a step before it.
>
> **⚑ RULED 2026-08-28 — ROUTE A.** `orchestrate.py` and `EXTRACTION_DEFINE`'s
> Define block are **not migrated**. They carry the v1 names unchanged and are
> **deleted at step 11.1**, per Appendix B. **WATCH 7 clears at step 6.2.** The
> Define gate is accepted as inert until then. Routes B and C rejected.
> **Do not "fix" the v1 Define names anywhere in the tree — they are the
> ruled-correct state.** Evidence in **`docs/_archive/WATCH7_AUDIT_2026-08-27.md`**, (archived to docs/_archive/; canonical: DECISIONS.md Part X)
> ruling at **`docs/_archive/DECISIONS.md` Part X**. **§0.2's WATCH 7 row and step 3.4's
> consequence note are left as written**, per the annotate-don't-rewrite rule;
> read them against this banner.
>
> **One inconsistency this surfaced, annotated not fixed:** §0.2 says WATCH 7
> clears when *"4.1 lands (… executor stops delegating to v1
> `orchestrate_define`)"*, but **step 4.1's own prompt has the executor
> delegating to `orchestrate_define`**. As written, WATCH 7 does not clear at
> 4.1 — it clears at **6.2**, when the executor gains its own capture path via
> `response_format=CoachingResponse`.

---

## About this document

*Original lines 107–115.*

> **Corrected 2026-09-10.** These three lines named
> `../../AGENTIC_ARCHITECTURE_REFERENCE.md` as the target, which the founder
> ruling of **2026-08-27** superseded: `agent-improve/ARCHITECTURE.md` is the
> authoritative build target for every step. The correction was carried as an
> open item in `BUILD_TRACKER.md` — *"Procedure framing … Annotate"* — from
> 2026-08-27 until that file was deleted, and is applied here rather than moved
> to another list. **The root reference still binds at the platform level** and
> is what a back-port owes once Improve settles (§0.12); it is simply not what
> a step here is built against.

---

## The three-document division

*Original lines 130–133.*

`../ARCHITECTURE.md` is **no longer the v2.2.16 design document** — since
2026-08-22 that path holds a copy of the root reference, Improve's own
architecture doc. **The old §15 migration sequence is replaced by this
document** and is available only at commit `8533879`.

---

## Verification owed, and by which steps

*Original lines 202–203.*

| ~~6.21~~ | `live-run` | **DISCHARGED 2026-09-15**, rid `20167cc9-ea86-4501-a827-0e19ebb2420a`. See the closure in 6.21's own section |
| ~~6.33~~ | `live-run` | **DISCHARGED 2026-09-21**, rid `5415c73d-6b80-426a-b5f4-7daabef1ec4b` and the turn after it. **The row is written in the SAME COMMIT as the code**, which is what this table asks for and what 6.21's absence for eleven days cost. See the closure in 6.33's own section — including what the run does NOT prove |


*(continued — original lines 212–220)*

>
> **6.21 WAS THE CASE THIS TABLE EXISTS FOR, AND IT WAS MISSING FROM IT.** The
> four rows above were added when their steps landed; 6.21's was not, for
> eleven days. **A step whose `Verify` names `live-run` is exactly the step
> most likely to land on its code half alone**, because the code half is the
> half a session can finish unaided — so the row recording the debt is owed
> at the SAME COMMIT as the code, never later. **G-63's fix (2026-09-15) did
> not close 6.21 and said so in its own body**; the evidence is still the
> founder's live turn.


*(continued — original lines 222–228)*

**All five run through the same path.** The
executor loops on `rag_lookup_evidence` instead of calling the
`load_evidence_series` its own planner named, so no Define turn on
`IMPR-2026-ED8` completes (`ARCHITECTURE.md`'s gap register, and 6.13's
section). The first three were recorded as owed on the assumption that running
them was merely pending. **It is not pending; it is blocked**, and until
2026-09-10 none of the three said so.

---

## 3 — Test first, and the whole set

*Original lines 309–315.*

> **THE WORKED EXAMPLE IS THIS PROJECT'S OWN, AND IT IS EIGHT DAYS OLD.** Step
> 6.33 landed on 2026-09-22 and built the field change log. **One file over,
> `storage/blob.py::write_phase_gate` replaces the whole `PhaseRecord`** — so
> the first gate write erases the log 6.33 had just built, along with the
> Belt's uploads. **Every test 6.33 wrote still passes.** A step that proves
> only its own clauses cannot see what it broke, and the register is what makes
> the second half of that sentence checkable.

---

## 5 — Admission: a finding becomes a step only if it blocks a step in flight

*Original lines 340–343.*

**This clause exists because the alternative was measured.** The register
carries 77 gap rows and 91 steps against a Define slice that cannot complete,
and a founder reading the board cannot tell which four of those hundred and
sixty-eight items are in the way.

---

## 6 — A mutation proof neuters the PRODUCER, never the stored value

*Original lines 352–360.*

> **WORKED EXAMPLE, 2026-09-23, from step 6.20's own proofs.** The first
> mutation replaced `values["phase_metrics"]` — one of the derivation's two
> consumers. The other consumer folds the same derived entry into `artifacts`,
> so the assertion read the injected value straight back and **the mutation
> came back GREEN against a proof that was supposed to go red.** The corrected
> mutation neutered `define_phase_metrics` itself: eleven of sixteen tests
> failed, which is what the proof was claiming all along. **A check only ever
> seen passing is not known to fail**, and this is that rule catching a check
> rather than a piece of code.

---

## ⚑ THE DEFINE CRITICAL PATH — sequenced 2026-09-23

*Original lines 417–432.*

> **⛑ TWO IDENTIFIERS IN THE 2026-09-23 RULING COULD NOT BE RECORDED AS
> WRITTEN, AND THE SUBSTITUTION IS FLAGGED RATHER THAN ASSUMED.** The ruling
> names **`CO-1`** and splits 7.3 into **`7.3a` / `7.3b`**. **Appendix D's step
> number is parsed as `\d+\.\d+` by FIVE regexes across FOUR hooks** —
> `session-start-context.py`, `continuity_status.py`, `build_board.py` and
> `verify_built.py` twice. A row reading `**Commit CO-1**` or `**Commit 7.3a**`
> matches none of them: it does not render late, **it disappears**, which is the
> failure Appendix D's own header warns about — and `matrix_covers_appendix_d`
> would then report set inequality against Appendix F.
>
> So `CO-1` is registered as step **6.48** carrying `CO-1` as its ratified
> label, 7.3a keeps the number **7.3** (narrowed in place, so nothing is
> renumbered), and 7.3b is registered as step **7.8**. **The numbers are the
> only thing substituted; every precondition, scope and reason is as ruled.**
> Changing the five regexes instead would be a code change, which the
> amendment that carries this excludes.

---

## 0.2 Standing gates

*Original lines 456–456.*

| ~~**LangGraph < 1.2.6**~~ | ~~4.1, 4.2, 4.3, 4.4, 8.2~~ | **CLEARED 2026-08-21** — step 2.3 landed `langgraph` 1.2.11 |


*(continued — original lines 460–460)*

| **WATCH 7 — Define gate non-functional** | Define phase end-to-end runs | Step **4.1** lands (Define subgraph; executor stops delegating to v1 `orchestrate_define`, which still writes v1 names). Accepted interim, not a bug — a consequence of running 3.4's Define portion (commit `4701a09`) ahead of 4.1. `validate.py` reads v2 names; `orchestrate.py` writes v1 names; gate reads all Tier-1 fields missing. **Do not add a v1→v2 shim** (CLAUDE.md §17) — the migration happens naturally when 4.1 replaces the orchestrator's role. Cross-phase Define briefs in analyse/improve/control stay on v1 names until then, deliberately. **⚑ RULED 2026-08-28 — ROUTE A. This row is superseded on two points and left as written per annotate-don't-rewrite.** (a) It **clears at step 6.2**, not 4.1 — step 4.1's own prompt has the executor still delegating to `orchestrate_define`, so 4.1 cannot clear it. 6.2 gives the executor its own capture path via `response_format=CoachingResponse`. (b) `orchestrate.py` is **never migrated**; it and `EXTRACTION_DEFINE`'s Define block carry the v1 names unchanged and are **deleted at 11.1** (Appendix B). The Define gate is accepted as inert until 6.2 — nothing else is blocked. See `CONTINUITY.md` §6 and `docs/_archive/DECISIONS.md` Part X. |

---

## 0.3 What "current codebase" means

*Original lines 475–484.*

> **As of 2026-08-26:** Step 2.3 done. **Out-of-band:** Step **9.0** (index
> rebuild, `871637f`) done; Step **3.4 partially done for Define**
> (`4701a09`) with four phases + UI outstanding. **Next spine step: 2.4** —
> the procedure's horizontal order resumes here. **Do not jump ahead to more
> phase work** until the 2.4–3.3 foundation is complete; then 3.4 finishes all
> five phases together.
>
> **Direction confirmed: HORIZONTAL.** Today's Define work is absorbed, not
> extended. The two out-of-band commits are recorded so the spine reads
> truthfully — they do not re-order it.

---

## ... mutate, run, then:

*Original lines 538–545.*

**Twice now, and both times it produced a false result.** ARCHITECTURE.md
v1.49(D): disabling only `after_agent` left `aafter_agent` overriding, the
middleware still fired, and the new test passed — a mutation that did nothing,
read as proof. v1.58: a `git checkout --` restore reverted the uncommitted fix
instead of the mutation, and the next mutation reported a different test
failing that would have been recorded as a pass of a check never exercised.
**A mutation that does not do what you think produces a result that means
nothing**, and it looks identical to one that does.

---

## Step 2.3 — Dependency upgrade

*Original lines 548–588.*



**The floor is a rule; the target is a measurement.** The floor is
**≥1.2.6** — LangGraph 1.2.6 (2026-06-18) carries *"nested subgraph inherits
parent `checkpoint_ns` (regression in 1.2.3)"*, which §16 depends on.

**Resolve the exact target by running `/verify-current-version` as this step's
first action.** As of 2026-08-21 that resolved to `langgraph` 1.2.11,
`langchain` 1.3.16, `langchain-classic` 1.0.8. **If the skill resolves
different values, the skill wins** — Reference §53's table is a snapshot and says
so.

**The `langchain-core` jump is the risk.** The resolved `langchain` requires
`langchain-core>=1.6.0`; installed is 1.3.3. Three minors. Expect this to be
where surprises land, not in `langgraph`.

**Change:** upgrade, let pip resolve adjacent packages, then repin all of them.
Sweep for imports from `langgraph.prebuilt` (CLAUDE.md §4.4) and fix any found.


**Rollback:** `pip install -r requirements.txt` from the previous commit.

**Prompt:**
> Read CLAUDE.md §16.1 and §16.3. Run the `/verify-current-version` skill to
> resolve the current stable `langgraph`, `langchain`, `langchain-core` and
> `langchain-classic` versions — do not trust any version written in a
> document. Upgrade `agent-improve/requirements.txt` to the resolved targets,
> install into `agent-improve/.venv`, let pip resolve adjacent packages, then
> repin every resolved version explicitly. Report the resolved `langchain-core`
> version and any breaking change encountered on that upgrade. Then grep the
> whole `backend/` tree for imports from `langgraph.prebuilt` and report them —
> do not fix them in this step unless they break the import.


---

## Step 2.4 — `set_entry_point` → `add_edge(START, …)`

*Original lines 592–615.*



**Change:** replace the single `builder.set_entry_point("orchestrate_define")`
with `builder.add_edge(START, "orchestrate_define")`, importing `START` from
`langgraph.graph`.


**Rollback:** trivial, single line.

**Prompt:**
> CLAUDE.md §3.1: entry is declared with `add_edge(START, ...)`;
> `set_entry_point` is superseded and on the no-go list. In
> `agent-improve/backend/core/graph.py`, replace the `set_entry_point` call
> with `add_edge(START, ...)` and add the `START` import. Change nothing else.
> Confirm `grep -rn "set_entry_point" agent-improve/backend/` returns nothing.


---

## Step 2.5 — Async conversion

*Original lines 619–651.*



**Why this precedes everything architectural:** per-node timeouts (§45) are
unavailable on sync nodes — a hard LangGraph constraint, not a preference. Every
reliability step in Stage 8 depends on this being done first.

**Change:** convert all 11 phase nodes and `escalate` to `async def`; convert
every handler in `gateway/routes.py` to `async def`; `await` all LLM calls
(`llm.ainvoke`) and Azure SDK calls where an `aio` variant exists.

**Do not** change dispatch logic here — routes still dispatch manually until
4.2. This step converts signatures and call sites only.


**Rollback:** revert the commit; no state written.

**Prompt:**
> CLAUDE.md §1.4 (async by default) and §3.2 (nodes are async). Convert to
> `async def`: all five `orchestrate_{phase}` functions, all five
> `validate_{phase}` functions, `escalate`, and every route handler in
> `agent-improve/backend/gateway/routes.py`. Convert LLM calls to
> `await llm.ainvoke(...)` and Azure SDK calls to their `aio` variants where
> one exists. **Do not change how routes dispatch nodes** — that is a later
> step. Report any call site where no async variant exists.


---

## Step 2.6 — `response.content` → `content_blocks` · 20 sites

*Original lines 655–700.*



**This is its own step because the scope is ten times what the current-state
register records.** The reference's Appendix E names two sites
([`routes.py:67`](../backend/gateway/routes.py#L67),
[`upload/agent.py:107`](../backend/upload/agent.py#L107)). There are **20**:

| File | Count |
|---|---|
| `phases/define/orchestrate.py` | 5 |
| `phases/analyse/orchestrate.py` | 3 |
| `phases/control/orchestrate.py` | 3 |
| `phases/improve/orchestrate.py` | 3 |
| `phases/measure/orchestrate.py` | 3 |
| `escalate.py` | 1 |
| `gateway/routes.py` | 1 |
| `upload/agent.py` | 1 |

**This is also the pattern the drift hook blocks** (`pattern-3-response-content-parsing`,
citing CLAUDE.md §4.5), so leaving 18 of them in place means the hook fires
against the codebase's own existing state.

**Change:** read `response.content_blocks` and extract text from the typed
blocks, per §21 — which states why the raw `content` field must not be
index­ed or substring-parsed.


**Prompt:**
> CLAUDE.md §4.5: read `response.content_blocks`; string-indexing or
> substring-parsing the raw content field is a violation. There are 20 sites in
> `agent-improve/backend/` — find them with
> `grep -rn "\.content\.strip()" agent-improve/backend/`. Convert every one to
> read `content_blocks` and extract the text block. Where a site parses JSON out
> of the text afterwards, leave that parsing alone for now (§4.3 is a later
> step) — this step changes only how the text is obtained. Confirm zero
> remaining hits, then run one `/ask` turn to confirm coaching text still
> returns.


---

## Step 2.7 — LLM factory: class → functions, 6 roles → 11

*Original lines 704–748.*



**Two violations in one file.** `LLMProvider` at
[llm.py:29](../backend/core/llm.py#L29) is a class in a file where §54 permits
none — the LLM factory is named explicitly as module-level-functions-only. And
`_ROLE_MAP` carries **6 roles** (`intent`, `reasoning`, `operational`,
`premium`, `extraction`, `coach`) over three deployment settings, where §21
specifies **11 roles** over two tiers.

**The 11 roles (§21):** `coach`, `planner`, `synthesis` → `operational-premium`;
`reasoning`, `extraction`, `coherence`, `constraint`, `grader`, `summarizer`,
`intent` → `operational-model`; `vision` → `operational-premium`.

> **`max_retries=3` on the `AzureChatOpenAI` constructor stays in this step.**
> It is hand-rolled retry that `ModelRetryMiddleware` replaces, but removing it
> before the middleware exists leaves a window with no retry at all. **It is
> removed in step 6.4**, which is where the replacement lands.

**Change:** replace the class with module-level functions preserving the
`lru_cache`; expand `_ROLE_MAP` to all 11 roles; add the §21 temperature
defaults per role (grader/coherence/constraint at 0.1, extraction 0.0–0.2,
coach 0.5–0.7).


**Prompt:**
> CLAUDE.md §4.1, §4.2, §4.7 and §2 (where classes are allowed — `core/llm.py`
> is module-level functions only). Rewrite
> `agent-improve/backend/core/llm.py`: remove the `LLMProvider` class, keep the
> `lru_cache`, and expose module-level `get_llm(role, temperature, max_tokens)`.
> Expand the role map from the current 6 roles to the 11 in CLAUDE.md §4.2, each
> mapped to `operational-premium` or `operational-model` as that table says.
> Apply the §4.7 temperature defaults per role. **Leave `max_retries=3` on the
> constructor** — it is removed in step 6.4 when `ModelRetryMiddleware` lands;
> add a comment saying so. Write `backend/tests/test_llm.py` asserting every one
> of the 11 roles resolves and that the grader role defaults to temperature 0.1.
> Update every `get_llm` call site that used a retired role name.


---

## Step 3.1 — `SupervisorState` and `PhaseState`

*Original lines 756–783.*



**Change:** `core/state.py` holds `SupervisorState` — exactly seven fields
(§5). `core/substate.py` holds `PhaseState` — §6 / S-C02 is authoritative for the
field census, its categories and the copy-down rule. The v1 `ImproveGraphState` is deleted in step 11.1, not
here; both coexist until the last v1 consumer is gone.

**`gate_attempts` must be on `PhaseState`** — holding it in route scope is what
produced the v1 "attempts always reset to 0" bug (§6).


**Prompt:**
> CLAUDE.md §10.1 gives both schemas in full. Create
> `agent-improve/backend/core/substate.py` with `PhaseState` (19 fields) and
> rewrite `agent-improve/backend/core/state.py` to add `SupervisorState`
> (7 fields) **alongside** the existing v1 `ImproveGraphState`, which stays
> until step 11.1. Use explicit `TypedDict`, not `MessagesState` inheritance
> (§10.1). Do not wire either into the graph in this step. Add a test asserting
> the exact field counts and names.


---

## Step 3.2 — `AzureBlobStore`

*Original lines 787–811.*



**Change:** `AzureBlobStore(BaseStore)` at `core/store.py`, namespace
`("projects", case_id, <kind>)`, blob prefix
`store/projects/{case_id}/{kind}/{key}.json` (§9).


**Prompt:**
> CLAUDE.md §10.2 and §2 (`core/store.py` is one of the files where a class is
> permitted). Implement `AzureBlobStore(BaseStore)` in
> `agent-improve/backend/core/store.py` using the namespace convention and blob
> prefix in §10.2. Follow the same async and ETag patterns as the existing
> `core/checkpointer.py`. Write a headless script under `scripts/` that puts a
> dict under `("projects", "IMPR-2026-E9D", "artifacts")` key `"define"`, gets
> it back, and asserts equality. Report the blob path actually written.


---

## Step 3.3 — Boundary mappers

*Original lines 815–839.*



**An input mapper's only dependency is `BaseStore`** (§9). Reading context off
parent state, or handing a mapper a blob client, is a violation: the first
creates a parent field to keep in sync, the second puts untracked I/O in a
translation function.


**Prompt:**
> CLAUDE.md §10.2 (boundary mappers). Create `mappers.py` in each of the five
> `agent-improve/backend/phases/{phase}/` directories, each with an input mapper
> and an output mapper as §10.2 specifies. **The only dependency is
> `BaseStore`** — no blob client, no parent state reads. Define's input mapper
> reads the case record; the other four read the prior phase's artifacts. Write
> unit tests with a fake store for Define and Measure.


---

## Step 3.4 — `{Phase}PhaseInput` → `{Phase}Output` schemas, with validators and UI

*Original lines 843–952.*


> ⚠ **PARTIALLY EXECUTED AHEAD OF SEQUENCE — Define only (commits `4701a09`
> then `885defc`, 2026-08-26).** Read before running this step.
>
> The Define portion of this step's schema+validator work was done early, via
> the ratified Define amendment (`docs/_archive/DEFINE_AMENDMENT_2026-08-25.md` → (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1)
> `ARCHITECTURE.md` §39.1), then **finalized at Option A**
> (`docs/_archive/DEFINE_FINALIZATION_2026-08-26.md` → §39.1.2, §40, §63.1). **Build to (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)
> the finalization, not the amendment** — the amendment's 8 Tier 1 / 3 Tier 2
> split is superseded for Define.
>
> **Already done for Define:**
> - `phases/define/schema.py` — `DefineOutput` (**16 fields: 12 required, 4
>   gate metadata — no tiers, Option A**) rebuilt; granular 5W2H
>   `DefinePhaseInput` retired.
> - `phases/define/validate.py` — `DEFINE_REQUIRED_FOR_GATE` = the **12
>   required fields** (no tiers, Option A — see §39.1 /
>   `DEFINE_FINALIZATION_2026-08-26.md`). (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)
> - `skills/dmaic-define-phase/SKILL.md` — written, generated verbatim from
>   §39.1.7.
> - `CoachingResponse` (S-C05) — gained 4 presentational fields
>   (`explanation`, `example`, `prompt`, `progress`), shared across all five
>   phases.
>
> **STILL OUTSTANDING for this step (do NOT skip):**
> - The **other four phases'** schema+validator rebuilds — Measure, Analyse,
>   Improve, Control. This step's "all five in one step, deliberately" rule
>   (§14 cross-phase) is **not yet satisfied** — only Define is done. The four
>   must be completed together.
> - The **`ui/index.html` field-rename** coupling — NOT done for any phase. The
>   UI still references v1 field names.
> - **Count correction:** this step's prose below says "Define's six Tier 1
>   fields" and "exactly one name survives from v1 (`goal_statement`)." Both
>   are superseded — Define is **12 required fields with no Tier 1 / Tier 2
>   split** (Option A, ratified 2026-08-26), and **two** v1 names survive:
>   `goal_statement` and `target_date`. **§39.1 and
>   `DEFINE_FINALIZATION_2026-08-26.md` are authoritative; this step's inline (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)
>   counts are pre-amendment** and are left unrewritten deliberately, per the
>   annotate-don't-rewrite rule.
> - **One more inline claim to read past for Define:** the "two fields on all
>   five schemas" paragraph below tiers `secondary_metrics` as Tier 2. True for
>   the other four phases; in Define it is **gate-required** like every other
>   field, and it is coached at position 10 (§39.1.2).
>
> **Consequence — WATCH 7 (§0.2):** doing Define's schema early, without its
> subgraph (Step 4.1), left `phases/define/orchestrate.py` still writing v1
> field names while the validator reads v2 names — so **the Define gate cannot
> currently pass.** Expected given out-of-sequence execution; resolves at Step
> 4.1 per the procedure's own order.



**Rewritten in place, per §53.1** — `{Phase}PhaseInput` becomes
`{Phase}Output` in the same file. There is no production consumer to protect.

**All five phases in one step, deliberately.** Two fields are on all five
schemas — `issues_and_barriers` (Tier 1) and `secondary_metrics` (Tier 2) — and
CLAUDE.md §14 forbids adding a field to one phase's schema without checking the
other four. Splitting this by phase would violate that rule four times.

**The models are near-disjoint.** Of Define's six Tier 1 fields, **exactly one
name survives from v1**: `goal_statement`. Everything else is new.

**Three conversions bind:**

| Conversion | Detail |
|---|---|
| `team_members` | `list[TeamMember]` → **string** (§7 — every captured field is a string). The `TeamMember` model is deleted |
| `process_map_sipoc` | **Introduce as a new Tier 1 dict field, promoted from prompt-embedded content, including `process_metrics`.** It is *not* an edit to an existing schema field — there is no `sipoc` field in `DefinePhaseInput` today. SIPOC exists only as `ImproveGraphState.sipoc_diagram` and a five-column JSON key in `core/prompts.py`. The promotion adds `process_metrics` as the sixth key |
| Numeric fields | Any typed numeric becomes `str` (§7). Computation tools parse at the point of use |

**Coupled in the same commit, per ruling:** the five `validate_{phase}.py`
files that instantiate these models, and the `ui/index.html` field names that
render them. Leaving the UI reading fields that no longer exist — even briefly
— produces a workspace that renders blank panels with no error.


**Rollback:** revert the commit. No stored gate documents exist yet to migrate.

**Prompt (Stage 1 — audit, read-only):**
> Read CLAUDE.md §10.6 (field typing law), §10.7 (the five `{Phase}Output`
> schemas and their field counts), §10.8 (structured dict fields) and §9.7 (the
> Tier 1/Tier 2 split). Then read all five
> `agent-improve/backend/phases/{phase}/schema.py`, all five `validate.py`, and
> every place `agent-improve/ui/index.html` references a phase field name.
> **Report only — change nothing.** Produce: (a) a per-phase table of v1 field →
> v2 field → Tier, marking every v1 field with no v2 home and every v2 field
> with no v1 source; (b) the exact list of `ui/index.html` line numbers that
> reference a v1 field name; (c) every place `TeamMember` is constructed or
> read; (d) where `sipoc` content currently lives in `core/prompts.py` and
> `core/state.py`.

**Prompt (Stage 2 — implement, written after reading the audit):**
> *Written once the Stage 1 audit is in hand. It must cover: rewrite all five
> schema files in place to the §10.7 definitions; `team_members` to a string and
> delete the `TeamMember` model; introduce `process_map_sipoc` as a new Tier 1
> dict with all six keys including `process_metrics`; every field `str` except the
> three cross-phase reference dicts and the three structured dicts; update all
> five validators; update every `ui/index.html` field reference found in the
> audit.*


---

## Step 3.5 — `storage/blob.py`: `ImproveBlobClient` class → functions, sync → aio

*Original lines 974–1054.*



**Added 2026-08-31, after step 3.2 made the gap visible.** This step did not
exist. The procedure named `storage/blob.py` exactly once — in Appendix B's
disposition table as *keep, minor edits* — and no step's **Touches** row
claimed it, while **S-C08's own header read `Procedure: [tbd]`**. Two pieces
of owed work therefore had no home, and neither is optional:

| Owed | Why it binds |
|---|---|
| **Class → module-level functions** | §54 and CLAUDE.md §2 both list `storage/blob.py` explicitly among the files that hold *module-level functions ONLY*. `ImproveBlobClient` is a class where none is permitted — the same violation step 2.7 cleared in `core/llm.py` |
| **Sync → aio** | §1.4 and §49 require the `aio` variants where they exist. Every method is synchronous, and since **2.5** made the route handlers `async def` this I/O runs **on the event loop** instead of in FastAPI's threadpool — a concurrency regression 2.5 recorded and deferred rather than one this step invents |

**Nothing else covers it.** 11.1 deletes v1, and Appendix B marks this file
*keep*; 3.3 touches `phases/{phase}/mappers.py`; 8.5 is the shutdown gate, not
a rewrite. §10's concern 2 stays a distinct concern with a distinct owner —
**this step rewrites `ImproveBlobClient`, it does not fold it into
`AzureBlobStore`.** Merging the two would delete S-C08's subject and collapse
the separation §10 spends a section establishing.

**Change:** replace the class with module-level functions preserving the
module-level singleton behaviour; convert the Blob calls to
`azure.storage.blob.aio`; `await` them at every call site in
`gateway/routes.py`. The paths this file owns are unchanged —
`cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}` — and it
still writes on case create, on gate pass and on file upload, **never
mid-conversation** (§10).

> ### ⚠ THIS STEP CARRIES A DESIGN DECISION — rule it when the step is built
>
> **The aio session lifecycle for `load_case` / `save_case`.** An
> `azure.storage.blob.aio` client owns an aiohttp session bound to the running
> loop, so it needs a deterministic close. Step 3.2 solved this **per
> operation** — a fresh client per call under `async with` — because Store
> writes happen a handful of times per phase.
>
> **That reasoning does not transfer here.** `load_case` and `save_case` run on
> **every request**, so per-operation client construction is the wrong trade at
> this frequency. The two candidates:
>
> | Option | For | Against |
> |---|---|---|
> | **Cached client + `aclose()` on the shutdown hook** | One client, one session, no per-request construction. The right shape for a hot path | The hook is step **8.5**, which is **GATED** on `RunControl.request_drain()` being confirmed to exist (§0.2). Building 3.5 against it couples a Stage 3 step to a gate that may never clear |
> | **Accept 3.2's per-operation pattern** | Ships now, no dependency on 8.5, one pattern across both Blob owners | Pays a client construction per request. **Unmeasured** — the cost is asserted, not known |
>
> **The decision needs a measurement, not an opinion.** Time both shapes
> against the real container on the `/ask` path before choosing; if the
> per-operation overhead is small against the Azure round-trip it already
> pays, the second option wins on its lack of a gated dependency. **Record the
> figure in the commit body either way** — a performance decision with no
> number in the record is one the next reader has to make again.
>
> A third shape exists and is **not** a candidate: closing over the loop
> lifetime with no shutdown hook at all. That is the leak the per-operation
> pattern was chosen to avoid.


**Rollback:** revert the commit. The blob layout is untouched, so no written
state needs undoing.

**Prompt:**
> CLAUDE.md §2 and reference §54: `storage/blob.py` is module-level functions
> only. §1.4 and §49: Azure SDK calls use the `aio` variants. Rewrite
> `agent-improve/backend/storage/blob.py` — remove the `ImproveBlobClient`
> class, keep the same public names as module-level functions, and convert the
> Blob calls to `azure.storage.blob.aio`. Await them at every `blob_client.*`
> call site in `gateway/routes.py`. **Do not fold this into `AzureBlobStore`**
> — §10 keeps the two concerns separate. **Rule the session-lifecycle question
> first and report the measurement**, per the boxed note in this step.


---

## Step 4.1 — The Define phase subgraph

*Original lines 1057–1096.*



**Five nodes: `planner`, `executor`, `validation_stack`, `gate_review`,
`gate_apply`** (§13). `policy_advisory` and `revise` are BANNED as node names.

**The subgraph compiles with NO checkpointer and NO store** (§16) — both attach
to the parent graph only.

At this step the five nodes are **structurally correct and behaviourally
minimal**: the planner returns a stub `CoachingPlan`, the executor still calls
the v1 orchestrate logic. Stages 5–7 fill them. This keeps the step small
enough to verify.


> *Corrected 2026-09-02: this read `build_phase_subgraph("define", llm).compile()`.
> The builder already returns a compiled graph — S-F02's own definition ends
> `return builder.compile()` — so the trailing call raises `AttributeError`
> (`CompiledStateGraph` has no `.compile`). Found while building 4.1.*

**Prompt:**
> CLAUDE.md §3.1 and §3.3. Create `agent-improve/backend/phases/define/graph.py`
> with `build_phase_subgraph(phase, llm)` and
> `agent-improve/backend/phases/define/nodes.py` with the five module-level
> async node functions named in §3.3 — `planner`, `executor`,
> `validation_stack`, `gate_review`, `gate_apply`. Wire the edges as §3.3
> describes, including the cycle back to the planner. **Compile with no
> checkpointer and no store** (§1.2). For now: the planner returns a stub plan,
> the executor delegates to the existing `orchestrate_define`, and
> `validation_stack`/`gate_review`/`gate_apply` are pass-throughs that log. Do
> not route any traffic to this yet. Add a test asserting the compiled graph has
> exactly those five nodes.


---

## Step 4.2 — `thread_id` through `graph.ainvoke`, and the disconnect policy

*Original lines 1100–1234.*



**This is the step that makes the checkpointer real.** It is currently
**wired but inert** — `core/graph.py:147` compiles with a checkpointer, but
`thread_id` and `ainvoke` appear nowhere in the codebase and the compiled graph
is discarded at [routes.py:238](../backend/gateway/routes.py#L238). **Zero
checkpoints have ever been written** (Reference §53.1, Appendix E).

**The five Handler-Shaped Durability requirements of §47 land here, not
separately** — §47 says so explicitly. Once checkpoints write, the FastAPI
handler's control-flow shape, not the checkpointer, decides what survives a
client disconnect.

> *Amended 2026-09-02, twice — on building the step, then again on verifying
> it. **Requirement 1 was reported as landed and was not**: the inline `await`
> it shipped with does not abandon on disconnect, and only the live
> `azure-query` found that. It is now a disconnect race and is genuinely met;
> the full account, including the second wrong implementation, is `DECISIONS.md`
> **Z8**, and `backend/tests/test_abandon.py` pins the mechanism. **Three of
> the five landed, two did not, and the split is a ruling rather than a
> shortfall.*** Requirement 4
> (the reconciliation sweep) **cannot be written before `interrupt()` exists** —
> its whole content is which threads to EXCLUDE, and there are no paused threads
> to exclude until stage 7. Requirement 5 (`thread_id` from the authenticated
> session) **has no auth layer to derive from**; §17 places multi-user identity
> after the refactor. Requirement 3 landed as the **optimistic ETag guard**
> already in `AzureBlobCheckpointSaver` rather than the specified Blob lease —
> the guarantee is *two tabs waste a turn, they do not corrupt one* — with the
> lease and an unguarded history-blob orphan deferred to the PostgreSQL
> migration, which §47 itself names as the point advisory locks become
> available. **WATCHes 13, 14 and 15 in `CONTINUITY.md` §6; the reasoning is
> `DECISIONS.md` Part Z.** Requirement 5 in particular is a **tenancy** gap and
> must not be read as closed because `thread_id` is now correctly wired.*

**The five requirements are §47's "Five requirements", and are not restated
here.** Read them there. **Ratified policy is ABANDON, not COMPLETE** (§47).

**Change:** routes stop dispatching nodes manually and call
`await graph.ainvoke(state, config={"configurable": {"thread_id": case_id}, "recursion_limit": 50})`.
`get_graph()` is used, not discarded.


> *Two corrections, both made while running the verification on 2026-09-02.*
>
> **The case is not `IMPR-2026-E9D`.** That case is **complete** — all five
> gates passed in June 2026 under v1 — so its `current_phase` is `"complete"`,
> which is not a phase and has no subgraph. It cannot exercise the Define path
> and never could have. The verification ran against **`IMPR-2026-0CB`**
> (`phase=define`, `status=active`), the only case in the registry that is in
> a coachable phase. Any future step naming E9D for a live-run check needs the
> same substitution.
>
> **"leaves no new checkpoint" was too strong**, and is corrected above.
> LangGraph writes an entry checkpoint when `ainvoke` begins — before any node
> runs — so a turn abandoned after that point legitimately leaves those blobs.
> Measured: 2 blobs, both timestamped *before* the disconnect, and **nothing
> after it**. The guarantee ABANDON gives is that no node runs and no
> checkpoint is written once the Belt is gone, which is what §47 is protecting.
> `DECISIONS.md` Z8.

**Rollback:** revert. Delete the `checkpoints/IMPR-2026-E9D/` prefix so a
retry starts clean.

**Prompt (Stage 1 — audit, read-only):**
> Read CLAUDE.md §1.1 (one runtime), §1.2 (`thread_id`), §1.4, and
> `../../AGENTIC_ARCHITECTURE_REFERENCE.md` §47 in full. Then read
> `agent-improve/backend/gateway/routes.py` and `core/graph.py`. **Report only.**
> Produce: (a) every place `routes.py` dispatches a node directly, with line
> numbers; (b) what state `routes.py` builds by hand that `SupervisorState`
> should carry; (c) the current shape of the `/ask` handler and whether it
> streams; (d) for each of the five §47 requirements, what the code does today
> and what it would need to do; (e) whether `core/checkpointer.py`'s existing
> `ConcurrentTurnError` already covers requirement 3 or whether a Blob lease is
> still needed.

**Prompt (Stage 2 — implement):**
> CLAUDE.md §1.1, §1.2, §1.7 and reference §16, §47, §49. Rewrite `/ask` and
> `submit_gate` in `agent-improve/backend/gateway/routes.py` to call the
> compiled graph — `await graph.ainvoke(state, config={"configurable":
> {"thread_id": case_id}, "recursion_limit": 50})` — and delete both hand-built
> dispatch tables (`node_map`, `validate_map`) with their function-level
> `orchestrate_*` / `validate_*` imports. Build `SupervisorState` through the
> input mapper at the boundary, not the eleven-field `ImproveGraphState`
> literal; `current_phase` gets its single writer. Do not recreate the
> hardcoded `gate_attempts=0`. Implement §47 requirements 1–3 with the handler
> shape chosen and commented as such; **requirements 4 and 5 are OUT** — 4 needs
> `interrupt()` (stage 7) and 5 needs an auth layer (§17, post-refactor) — carry
> both as WATCHes and say so rather than reporting 5/5.

> ### ⚠ WHAT 4.2 ACTUALLY RULED — read before starting 4.3
>
> Full record: `DECISIONS.md` **Part Z** (Z1–Z7). Four consequences bind on the
> next steps:
>
> 1. **The parent is one node — `START → define_phase → END` over
>    `SupervisorState`, compiled with checkpointer AND store.** That is the
>    smallest parent §16 permits, built only so the checkpointer has something
>    to attach to. **4.3 grows it; it does not start from scratch.** The v1
>    chained graph and `escalate` as a node are deleted — 4.3 re-adds escalation
>    as the conditional branch.
> 2. **`define_output_mapper` is NOT called, and `gate_apply` writes nothing.**
>    Reaching `END` means "the graph ran", not "the Belt approved", until the
>    `interrupt()` lands at `gate_review`. Both reverse together at **stage 7**
>    and neither may be enabled alone — doing so commits a gate approval the
>    Belt never saw (§47, §33).
> 3. **`core/checkpointer.py` was edited although it is not in `Touches`.**
>    `checkpoint_ns` was absent from the blob layout, so parent and subgraph
>    shared one `latest.json` and the conversation doubled every turn with no
>    error. The parent's paths are unchanged; subgraphs go under
>    `checkpoints/{thread_id}/ns/{ns}/…`. **Part Z3.**
> 4. **Only Define runs through the graph.** The other four raise
>    `PhaseNotWired` → HTTP 501 until **4.4** (WATCH 17). Not a live regression —
>    no case can reach Measure while the Define gate is inert (WATCH 7).
>
> **Verification status.** `pytest` is green (362, including the new
> `backend/tests/test_turn_graph.py`) and `mypy` adds no new errors. **The
> step's own `azure-query` — `checkpoints/IMPR-2026-E9D/latest.json` after one
> `/ask` turn, a `history/` entry after a second, and no checkpoint after a
> mid-turn kill — needs the live container and is run by hand.** The unit tests
> pin the structure beneath it (`thread_id` = `case_id`, both persistence
> primitives on the parent and neither on the subgraph, no message duplication,
> one executor call per invoke, `gate_apply` applying nothing); they do not
> substitute for it.


---

## Step 4.3 — The supervisor graph

*Original lines 1238–1303.*



**Static edges only.** `define → measure → analyse → improve → control → END`.
No routing LLM, no `Command` at this level — Level 1 has nothing to reason
about (§12, §15). **Never mix static edges and `Command` from the same node**;
both paths execute, silently.

**Escalation is a NODE here and an EDGE one level down.** The supervisor gets an
`escalate` node whose only edge is to `END` (§38 — it defers to the Belt and
never returns to the supervisor). **There is no conditional edge at Level 1.**

> ### ⚠ THIS STEP'S PROMPT USED TO SAY THE OPPOSITE — corrected 2026-09-02
>
> It read *"route to escalation on the conditional edge §3.5 describes"*, and
> **read literally that rebuilds `route_after_phase`** — the function §15,
> CLAUDE.md §0.14 and `DECISIONS.md` §R2 all record as deleted, with S-F01's
> invariants saying it *"MUST NOT be reinstated"*.
>
> §3.5 names the **trigger** — the validation stack exhausting its shared cap
> of 3 — and does not say where the edge lives. §15 and §38 both do, and they
> agree: *"a conditional edge **from inside the phase** to the escalation
> subgraph, which defers to the Belt and never returns to the supervisor."* The
> hop is `Command(graph=Command.PARENT, goto="escalate")` (§0.17 — the only use
> of `Command.PARENT` in this architecture), **verified at 4.3 to work through
> S-F10's node-function execution site.**
>
> **Why the literal reading is not a small mistake:** the deleted router
> branched on `state["gate_attempts"]`, which `SupervisorState` does not carry,
> so it raised `KeyError` on the gate-failure path — the one path such a branch
> would exist to serve. §15 forbids adding that counter to `SupervisorState`,
> which makes a Level 1 escalation branch unbuildable rather than merely
> unwanted. Full ruling: `DECISIONS.md` **Part AA**.


> **The supervisor built here is the TARGET, not the runtime**, and that is
> deliberate — 4.1's precedent. §15's static chain is safe because *"reaching
> `END` means the gate passed"*, and **that is false until `gate_review` raises
> `interrupt()` at stage 7**: today the subgraph runs straight through to `END`,
> so one `/ask` turn on the chained graph would run Define, then Measure, then
> Analyse. `get_graph()` therefore still returns the one-turn parent from 4.2
> until the interrupt lands, `build_supervisor()` is the ratified topology, both
> live in `core/graph.py`, and `test_get_graph_is_still_the_one_turn_parent`
> fails if the swap happens early. Part AA3.

**Prompt:**
> CLAUDE.md §1.2, §3.1, §3.3 and reference §15, §38, S-F01. Rewrite
> `agent-improve/backend/core/graph.py` as the supervisor: compile the five
> phase subgraphs as nodes, connect them with static edges in DMAIC order,
> `add_edge(START, "define")`, and add an `escalate` node with a single static
> edge to `END`. **No conditional edge and no router at Level 1** — the
> conditional escalation edge lives inside the phase subgraph and hops up with
> `Command(graph=Command.PARENT)`. **Checkpointer and store attach here and only
> here.** Phase sequencing is the static chain, not a gate-check function —
> reaching `END` already means the gate passed. Add tests asserting the
> topology, that subgraphs compile with neither checkpointer nor store, and that
> no Level 1 branch or `gate_attempts` read has crept back.


---

## Step 4.4 — The remaining four phase subgraphs

*Original lines 1307–1317.*



Same five-node structure, built from the parameterised builder. **No subgraph
imports another subgraph's nodes** (§12).


---

## Step 5.1 — Retrieval failure semantics

*Original lines 1328–1344.*



**Partly done already** — Appendix E records that `knowledge/retriever.py`
already carries the correct `phase_relevance` filter and `fields=` declaration.
This step completes the failure semantics: `[]` only when the search ran and
matched nothing; `KnowledgeSearchError` when it failed.

**Never wrap a retrieval call in a bare `except Exception` that returns `[]`** —
that is what hid the `phase` filter bug, by reporting a broken index as a silent
corpus (§27).


---

## Step 5.2 — Three `rag_lookup_*` tools with multi-query + RRF

*Original lines 1351–1382.*



**§24's three retired names — `search_improve_knowledge`,
`search_improve_cases`, `search_improve_evidence` — are quoted because they ARE
the `grep-absence` target**, and §24 records that verification depends on
literal strings — corrected in CLAUDE.md
§5.1 and the reference's Appendix D.1 on 2026-08-21. **`grep-absence` must target those
three strings.**

**Only the tool layer is retired.** `knowledge/retriever.py`'s
`search_knowledge` / `search_cases` / `search_evidence` functions keep their
names — §27 depends on them. **Do not grep-absence `search_evidence`**; it is
supposed to survive.

**The four cross-agent tools stay, unbound** — `search_resolve_cases`,
`search_resolve_knowledge`, `search_resolve_evidence`, `search_flow_vsm`.
Ratified as a distinct third category in **Reference §29.4** (2026-08-21,
`docs/_archive/DECISIONS.md` §Q1). **Do not delete them and do not bind them to the
executor in this step.** Binding one is an amendment, and §29.4 names three
rules that bind first — §27 compliance among them.

**Blocked partially by 9.1:** until the reindex lands,
`rag_lookup_evidence` takes **no** `order_by` and no `phase` filter, and
`rag_lookup_case_history` must use `embedding`, not `content_vector` (§23).
**Write against the live schema** (CLAUDE.md §7.2, §7.3).


---

## Step 5.3 — The 20 computation tools

*Original lines 1390–1400.*



**All 20 are pure functions** — no LLM call, deterministic, unit-tested (§30).
**Each is a separate named tool**; parameterised grouping is BANNED.


---

## Step 5.4 — Per-phase tool binding

*Original lines 1407–1431.*




> **⛑ Done-when corrected 2026-09-11 — it carried the superseded figure.**
> It read `8 / 15 / 12 / 8 / 12`, which was right until `load_evidence_series`
> made the universal set eight on 2026-09-09 (Part AR1) and every phase gained
> one. §30's table moved; this clause did not, so **the step's acceptance
> criterion and the section it verifies disagreed for two days** while the test
> — which had been updated — passed against neither number written down.
>
> **The live bind is 7 / 14 / 11 / 7 / 11 and that is not a defect of this
> step.** Two of the ratified eight universal tools are unbuilt by the spec's
> own assignment: `check_gate_status` (7.1) and `request_human_approval` (7.5).
> The ratified figure is what this step is checked against; the live figure is
> what `verify_built.py` pins, so the gap is measured rather than assumed. See
> §30's BUILT marker.


---

## Step 6.1 — Planner / Executor split

*Original lines 1439–1449.*



**Never fuse them** (§17). The planner produces a typed `CoachingPlan` via
structured output and never dispatches to tools; the executor consumes it and
never decides strategy.


---

## Step 6.2 — `create_agent` executor with `CoachingResponse`

*Original lines 1456–1491.*



**Two parameter names this project got wrong once already** — verify both
against the reference before writing, per CLAUDE.md §16.3:

```python
executor = create_agent(
    model=get_llm("coach"),
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=CoachingResponse,        # never a {Phase}Output
    middleware=[...],                        # added in 6.3–6.5
    system_prompt=PHASE_COACH_PROMPT[phase], # system_prompt, NOT prompt
)
```


> **⚑ THIS STEP CLEARS WATCH 7 (ruled 2026-08-28, Route A).** It is where the
> **v2 Define writer comes into existence**: `fields_captured` on the
> `CoachingResponse` lands in `artifacts` under the §39.1.2 names, which is what
> `phases/define/validate.py` has been reading since the rename. Until this
> step, the Define gate is **accepted as inert** and `orchestrate.py` +
> `EXTRACTION_DEFINE` keep writing the v1 names unchanged — deliberately, and
> **not** to be "fixed" in the meantime.
>
> §0.2's gate row says WATCH 7 clears at 4.1. It does not: step 4.1's own prompt
> has the executor delegating to the v1 `orchestrate_define`. Add to this step's
> Done-when: **the Define gate opens on a case coached through the v2 path**,
> and the v1 writer is then dead code awaiting deletion at 11.1.


---

## Step 6.3 — Middleware positions 1–3

*Original lines 1495–1505.*



**`BeforeModelStateInjection` MUST be first, on `before_agent`** — not
`before_model`, which re-injects the same project facts on every model call
within a turn (§19.1).


---

## Step 6.4 — Retry middleware, positions 4–5 · and the factory hardcoded-retry removal

*Original lines 1509–1550.*



> **Touches corrected at 6.4.** The row said `phases/{phase}/graph.py`, stale
> since the **4.4 consolidation**: the middleware stack is assembled once in
> `nodes_common._build_executor`, and the five `phases/{phase}/graph.py`
> re-export the parameterised builder without carrying a stack of their own.
> Positions 1–3 landed there at 6.3 and 4–5 here.

```python
ModelRetryMiddleware(max_retries=2),                        # wrap_model_call
ToolRetryMiddleware(max_retries=2, on_failure="continue"),  # wrap_tool_call
```

> **`max_retries`, not `retries`.** `retries=` does not exist and raises at
> construction. This exact keyword sat in the canonical stack undetected from
> adoption until 2026-08-21 (`BIBLE_VERIFICATION_LOG.md` C-1). (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

**This step also removes the hardcoded retry from the `AzureChatOpenAI`
constructor in `core/llm.py`**, deferred from step 2.7. **Ruled at 6.4: it is
replaced by an explicit `max_retries=0`, not simply deleted** — deleting it
inherits the SDK's `DEFAULT_MAX_RETRIES = 2` and silently restores the
stacking. Two layers multiply rather than add (DECISIONS Part AI).

> **⚑ THIS MAKES A BOUNDED REQUEST TIMEOUT LOAD-BEARING AT STEP 8.2** (§44,
> §45). The SDK's own retry had been quietly covering for the absence of one;
> with retry pinned off, a hung request has nothing underneath it but §44's
> `TimeoutPolicy`. Both projects that fixed this stacking pair `max_retries=0`
> with an explicit timeout for exactly that reason. **8.2 owns it** — this note
> exists so that step knows it inherited a dependency rather than a
> preference. Carried as WATCH 28.

**Sequenced here deliberately, not standalone:** the hand-rolled retry is only
safe to remove once the middleware that replaces it exists, and removing it
earlier would leave a window with no retry at all. CLAUDE.md §8.7 bans
hand-written retry plumbing — that ban only becomes satisfiable at this step.


---

## Step 6.5 — Middleware positions 6–8

*Original lines 1559–1592.*



**All three fire `after_agent` in declaration order.** If `CoherenceMiddleware`
exhausts its retries, `DMAICGraderMiddleware` is skipped for that turn (§19).

**Three independent retry caps, and they must not be merged** — model retry 2,
coherence 2, validation stack 3 (§19).

> ### ⚠ `ContradictionDetectionMiddleware` is a flag-reader — build it that way
>
> **Redesigned 2026-08-22 (`DECISIONS.md` §R1).** Its entire body is:
>
> ```python
> def after_agent(self, state, runtime):
>     flag = state["structured_response"].contradiction_flag
>     if flag:
>         raise HITLInterrupt(**flag)
> ```
>
> **Do NOT build the mechanical comparison** — no `store.get`, no
> `current_phase` read, no field-name matching. That version is deleted from
> the architecture because it could not work: it read a Store key
> `gate_apply` does not write until phase end, and matched names where 38 of
> 41 content fields are unique to one phase.
>
> **This step depends on `contradiction_flag` existing on `CoachingResponse`**
> — added in step 6.2's schema. If it is absent, 6.2 is incomplete; fix that
> rather than reintroducing comparison logic here.


---

## Step 6.6 — Prompts

*Original lines 1596–1633.*



The v1 `ORCHESTRATOR_{PHASE}_CONTEXT`, `EXTRACTION_{PHASE}` and
`KNOWLEDGE_INJECTION_TEMPLATE` patterns are deleted. **Every coach prompt
carries the memory hierarchy paragraph and the anti-hallucination guards** —
both mandatory (§22).

**The contradiction-check instruction lands here or in the SKILL.md files it
depends on** (§32, §37, `DECISIONS.md` §R1): every turn, compare the Belt's
input against prior committed values already in context and set
`contradiction_flag` on a **material** numeric or categorical contradiction of
a committed value — never prose rephrasing, never refinement of a
not-yet-committed current-phase value. **Step 6.5's middleware does nothing
without it** — the flag is the only thing it reads.


> **⚑ Done-when corrected at 6.6 — "in live v2 code", not repo-wide.**
> `KNOWLEDGE_INJECTION_TEMPLATE` is gone. **The other two families cannot reach
> zero here**, because their only consumers are the five `orchestrate.py`, and
> **step 11.1 owns deleting those** — it says so by name, including
> `EXTRACTION_DEFINE`'s block. Removing the constants at 6.6 would mean editing
> code 11.1 removes wholesale, and would break those imports; mypy analyses them
> (40 baselined entries), so guard rule 3 would fail for nothing.
>
> **This follows Route A**: the v1 vocabulary is carried unmigrated and dies
> with its writers at 11.1. `core/prompts.py` is rewritten — the v2 constants
> are the live ones — and the retired families leave when their consumers do.


---

## Step 6.7 — The hop cap, as §26 specifies it (WATCH 26)

*Original lines 1637–1693.*



**Not in the original spine. Added 2026-09-07 because WATCH 26 did not close
at 6.6 and the cause was a governance rule, not a build step.** CLAUDE.md
§3.7 carried `recursion_limit = 2 * max_hops + 1 = 11` as the hop cap, which
ARCHITECTURE §16 rejects outright and §26 replaced with `RemainingSteps` in
August 2026. The build followed §3.7 — correctly; it is the constitution — so
the fix is a governance commit (2.2.32) and then this step.

**Two properties MUST be measured before anything is built on them**, and both
were: does `remaining_steps` survive the subgraph boundary (it does, both ways
a subgraph can be entered), and are hops and steps the same unit (they are
not — the counter moves by 1 per executor turn however many hops that turn
made). **Both guards are therefore required and neither substitutes for the
other.** `DECISIONS.md` Part AL carries the numbers.

- `COACH_RECURSION_BACKSTOP = 50` replaces `COACH_RECURSION_LIMIT = 11` —
  §16's infinite-loop backstop, passed explicitly.
- `COACH_HOP_BUDGET = 5` — §3.7's cap, counted in per-turn copies of the three
  `rag_lookup_*` tools. **Past the budget the tool answers rather than
  searching**, so the coach composes from what it has.
- `REMAINING_STEPS_FLOOR = 2` — §26 / S-F09 B1's off-ramp, read at the top of
  the executor. Below it, the coach is built with no retrieval tools bound.
- The `GraphRecursionError` catch stays, now belt-and-braces against a bug.


> **⚑ The live half is owed, not done.** The 429 blocker on
> `operational-premium` is CLEARED (quota raised 50K → 200K TPM, 2026-09-14),
> so what remains is running the turns. The unit suite pins both guards
> deterministically, so what is owed is end-to-end confirmation of the
> mechanism, not the mechanism.
>
> ### ⚑ WHAT THIS CLAUSE ASKS FOR IS **COACH RATHER THAN CAP** — read it twice
>
> **It does NOT ask for the hop cap to ENGAGE.** The clause is *"the Define and
> Measure opening turns that see-sawed both **coach rather than cap**"* — the
> see-saw was the PRE-6.7 behaviour, and the evidence wanted is that those two
> turns now produce coaching instead of exhausting retrieval. **A run
> engineered to spend six lookups and trip `_HOP_BUDGET_SPENT` would
> demonstrate the opposite of what this asks** and would not discharge it.
>
> **The Define half is arguably already met** by the 2026-09-15 turn (rid
> `20167cc9`): it coached, returned the file's real statistics, and spent
> **0 of 5 hops** — coaching without approaching the cap. **The MEASURE half
> is not**, because no Measure turn has been run. Recorded 2026-09-15 rather
> than claimed, because *"arguably"* is not a verdict and the founder owns it.


---

## Step 6.8 — `phase_context` is read (WATCH 19)

*Original lines 1697–1735.*



**Not in the original spine. Added 2026-09-07 by the pre-Stage-7 coverage
audit, and it is the most urgent of the eight.** `phase_context` is declared on
`PhaseState`, written by all five input mappers, and **read by nothing.** §6's
field table names its consumers as *"planner; state injection (§19.1)"* and
neither touches it.

**Two halves, and only together do they fix anything:**

1. **The Store's `case` namespace has no writer** (WATCH 19). §9 and S-F10
   describe `("projects", case_id, "case") / "record"` as a session-start copy
   of the case record; `read_case_record` reads it and **nothing writes it**,
   so every read returns `{}`. The write belongs at case creation
   (`POST /cases`) and, for cases predating it, lazily on first read.
2. **`BeforeModelStateInjection` must inject `phase_context`.** 6.3 shipped the
   middleware without it, which is why half 1 stayed invisible.

**Fix half 2 alone and the coach gets an empty string with no error.** Fix half
1 alone and a correct value is composed and discarded. That pairing is why this
is one step.

> **⚠ THIS INVALIDATES EVERY LIVE MEASUREMENT TAKEN SINCE 6.3.** Every
> trace-check, live-run and coaching-quality observation from 6.3 onward was
> taken on a coach whose phase framing was mapper-fallback prose — *"this
> project — the department. Belt belt, led by the project leader…"* — rather
> than the case record or the prior gate document. **WATCH 26's see-saw
> included.** Nothing in those observations is safe to reuse as a baseline; the
> §26 arithmetic that explains the see-saw is unaffected because it was measured
> against the library rather than against the coach, but every judgement about
> what the coach *does* is provisional until this step lands and the runs are
> repeated. `DECISIONS.md` Part AM.


---

## Step 6.9 — The four missing SKILL.md files, and §32 conformance

*Original lines 1743–1760.*



**Not in the original spine — it was a parallel workstream with no scheduled
slot, which is how four of five went unwritten through all of Stage 6.** Only
Define's exists. `DMAICSkillsMiddleware` (§19.2) loads them, so four phases are
running progressive disclosure against nothing.

**Each must carry the contradiction-check instruction** (§37, `DECISIONS.md`
§R1) — step 6.5's middleware reads `contradiction_flag` and nothing else sets
it — **and the `CoachingResponse`-population instruction** (WATCH 9), without
which `explanation`/`example`/`prompt`/`progress` stay empty for that phase.


---

## Step 6.11 — The upload path (G-36)

*Original lines 1815–1877.*



**Not in the original spine. Added 2026-09-08 as the twelfth unstepped
section, and the largest.** §29.1 calls `improve_evidence_index` *"the only
channel through which external, real-world data enters AgentLean"*, and for the
formats a Belt actually uploads it does nothing: `classify_content_type` buckets
CSV and XLSX as `other`, PDF and DOCX get no extractor despite `is_supported()`
returning True for them, and `_index_upload` returns early on empty text — so a
spreadsheet is stored to Blob, never parsed, never indexed, and never
retrievable.

**`PhaseState.uploads` has no writer.** The route persists an `UploadRecord` to
the case blob instead. Gate assembly reads `PhaseState.uploads`, so **every gate
document currently asserts what §6 says an empty list means** — *"the phase
reached its conclusions from typed statements alone"* — including for phases
where the Belt uploaded. That is why this step must land before Stage 7
completes.

**Four founder rulings bind here** (`DECISIONS.md` Part AP):

- **Deterministic parse first.** Columns, row count, types and ranges come from
  the file. **Only meaning costs a model call, once, at ingest** — never spend a
  premium model to be told a spreadsheet has fourteen columns.
- **Evidence and artefact are different kinds.** Evidence describes the world
  and goes to the index. An artefact is what the team designed — a to-be
  process, a control-plan draft — and belongs to the gate document as captured
  content. **Why the split binds is ruling AP2.3, in §23.2.1.**
- **A file that cannot be extracted is refused or reported, never silently
  accepted.**
- **Interpretation stores to `computation_results` and cites its source
  upload** — §50's traceability binds on computed figures, not only quotations.


> **The last two are ratifications, not new scope** (`DECISIONS.md` Part AP5,
> 2026-09-08). The `/upload` route and the `UploadRecord` model already exist in
> the tree and neither was named in the ratified spec — **the same class of
> drift this step exists to close, so it closes in the same commit** rather
> than in a second reconciliation pass. `ask_id` and `version` are reserved
> here rather than added at 6.12 because an upload written between the two
> steps would otherwise carry no version identity and nothing to reconstruct
> one from — AP2 ruling 2 having forbidden inference from filenames.

> **G-36 closes here, or is re-scoped here.** S-F35 says the entire external
> data channel *"is currently specified as one cell in a field table"*. The
> rulings above are the founder input that gap asked for; this step is where
> they become a specification and then code.


---

## Step 6.12 — Ask-binding: an upload answers a request

*Original lines 1881–1980.*



> **This section was updated on 2026-09-10 and its Done-when grew.** As
> originally written it predated the evidence-channel amendment
> (`DECISIONS.md` Part AQ) and listed five clauses, so **the step could have
> been marked done while owing four more.** The founder rulings behind the
> additions are Part AR and Part AS.

**Not in the original spine.** Founder ruling: **an upload is bound to the
coach's request that prompted it, not to its filename.**

- **The ask carries an `expected_shape`.** Its keys and where they come from
  are §6 / S-C02's `asks` entry. The arriving
  file is validated against it.
- **A mismatch is a coaching question, not an error.** *"This has a `date` and
  an `amount` but no reason code — is the reason somewhere else, or not
  collected?"* is the coaching move; a validation failure is not.
- **The ask is the logical identity; files are its versions.** A second upload
  against the same ask is a revision. **No naming convention, no inference from
  filenames** — the binding is recorded when the coach asks, not reconstructed
  afterwards.

**This is what makes feeding uploaded data to a computation tool safe.** Without
it the only route from a file to `calculate_grr` is the coach transcribing
numbers out of retrieved chunks — which is the anti-pattern §22 exists to
prevent, performed on the platform's own evidence.

> ### ⛑ CORRECTED 2026-09-15 — THE LIVE-RUN CLAUSE WAS WRONG, NOT UNMET
>
> **This step's verification is RE-HOMED TO MEASURE.** Founder ruling. The
> five clauses below are unchanged; what changes is the phase they are
> verified in, and the reason is structural rather than practical.
>
> **THE TEST APPLIED: could any run have satisfied it? No.**
> `SHAPES_BY_PHASE` declares **0** ask shapes for Define and **4** for Measure
> — ruling AR-R2, and a deliberate one. So *"a coach request for data is
> recorded with its expected shape"* has nothing to record in Define, and
> *"an upload resolves to that ask"* has no ask to resolve to. **No Define
> turn could ever have satisfied clauses 1 and 2**, however many were run.
>
> **A Done-when requiring something structurally impossible in the phase under
> work is a defect in the CLAUSE, not a debt against the WORK.** It was
> carried as owed verification from 6.12's landing until today, and it was
> never owed — it was unsatisfiable. It also propagated: **6.21's Done-when
> required this step's live half *"in the same pass"***, so a false debt was
> inherited by a second step and would have been inherited by any step that
> named it next.
>
> **NOT QUIETLY DELETED.** The clause stands, re-homed, because the thing it
> asks for is real and is worth verifying — in the phase where ask shapes
> exist. **Verify becomes `live-run` (Measure).**


**Done when — the amendment's seven** (Part AQ, ruled into this step 2026-09-10):

1. `role`, `shape_match` and `content_digest` are on `UploadRecord` and in §6's
   uploads entry, with S-C09 and S-C02 updated. **Without all three, 6.13's
   backfill has nothing to read** — it reads the case blob.
2. Supersession resolves on `(case_id, role)` by comparing `content_digest`:
   the same digest is not a new version; a different one supersedes.
3. `consumed_at` is written when a load or a citation references the document.
4. **The upload manifest is injected every turn** by
   `BeforeModelStateInjection` — one line per uploads entry, inventory and not
   content.
5. The planner routes on an unconsumed upload bound to an open ask.
6. `load_evidence_series` per **S-F57**.
7. Citations carry `blob_path` and `content_digest`, **enriched in code and
   matched on `role`** — never on filename, which ruling AP2.2 forbids.

> **⚠ CLAUSE 7 IS HALF-SATISFIABLE HERE, AND THE SEAM IS PART OF THE
> ACCEPTANCE CRITERIA.** A citation the coach made against an upload it saw in
> the manifest **can** be anchored now, because `PhaseState.uploads` carries
> both fields. **One sourced from `rag_lookup_evidence` cannot** — the
> structured record carrying them is §24's, and that is **step 6.13**. Those
> citations pass through unanchored rather than being given a guessed anchor.
> **This step is done with half of clause 7 outstanding, by ruling**, and 6.13
> closes it.

**Measure's SKILL.md carries the three shapes; the other four phases do not.**
Ruling AR-R2 scoped the content pass to one phase and gave the rest their own
Appendix D row — **four-fifths of a content pass silently owed is the failure
this project keeps paying for**, so it is scheduled rather than assumed.

> **A vocabulary gap is recorded here and deliberately not fixed.** §23.2.1 has
> no `role` for a measurement-system study, and GR&R is not a capability study,
> so shape 3 uses `other evidence` — the catch-all that row exists for.
> **Extending a controlled vocabulary once with complete information beats
> extending it four times**, so it is batched with the four-phase pass.


---

## Step 6.13 — The evidence index migration

*Original lines 1984–2123.*



**Not in the original spine. Added 2026-09-09** with the evidence-channel schema
amendment (`DECISIONS.md` Part AQ). It applies the seven ratified-not-yet-applied
fields of §23.2 — `phase` and `uploaded_at` from the original ratification, plus
`role`, `kind`, `description`, `content_digest` and `shape_match`.

**No drop-and-rebuild is required, and that is what makes this a step rather
than a reindex.** All seven are *additive*; Azure assigns `null` to existing
documents. Only changing an EXISTING field forces a rebuild (Part AQ3, verified
against Microsoft Learn). 9.1's framing assumed the opposite and is narrowed
accordingly.

### Four sub-steps, and the order is load-bearing

| # | Sub-step | What it does |
|---|---|---|
| 1 | **Schema add** | The seven fields on the live index. Existing documents take `null` |
| 2 | **Write path** | `_index_upload` writes all seven, with `fields=EVIDENCE_INDEX_FIELDS` on the vectorstore |
| 3 | **Backfill** | Re-index every existing upload **from the case blobs**, which already hold `kind`, `summary`, `evidence_index_id` and the bytes a digest is computed from — **and, for a live document no blob record names, from the index's own `metadata`** (ruling 2 below) |
| 4 | **Retrieval filters** | `search_evidence` defaults to `kind eq 'evidence'`; `rag_lookup_evidence` returns §24's structured record |

**Why the order cannot change:**

- **Filters before the write path exposes artefacts with nothing hiding them.**
  A default `kind eq 'evidence'` filter against documents where `kind` is `null`
  matches nothing — or, if the filter is written to tolerate nulls, matches
  everything including the artefacts ruling 3's revision depends on separating.
  The filter is only safe once every document carries a `kind`.
- **Backfill before the schema has nothing to write into.** The fields must
  exist before a document can carry a value for them.
- **The write path before the backfill** means new uploads and backfilled ones
  land in the same shape, and the backfill is a one-pass job rather than a job
  that has to be repeated for anything uploaded while it ran.

> **§23.4 binds on sub-step 2 and is the most likely way this step fails
> silently.** A metadata key becomes a filterable field only if the key is named
> **and** the vectorstore declares it in `fields=`. Miss either and the value is
> written into the `metadata` JSON blob where `$filter` cannot reach it, **with
> no error raised** — which is exactly how `phase_relevance` went unpopulated.
> **`fields=EVIDENCE_INDEX_FIELDS` is not optional**, and each of the seven is
> two changes rather than one.

> **`mergeOrUpload` may OMIT `content_vector` on this index, and should.**
> Measured 2026-09-09: `improve_evidence_index.content_vector` is `stored: true`
> and `retrievable: false`, so a partial update that omits the vector keeps it
> — and **carrying it would mean re-embedding every document the backfill
> touches**, since a non-retrievable field cannot be read back. **The backfill is
> therefore a merge, not a re-ingest**, which is what makes sub-step 3 cheap.
> §23.2 carries the conditional and its tripwire: **if `stored` is ever declared
> `false` here, this sub-step must be rewritten before that change lands.**

**Placed AFTER 6.12, and it is not a precondition of it.** 6.12's ask-binding
works on `PhaseState` and the case blob alone and does not read the index.
**Anything uploaded between the two steps is picked up by sub-step 3**, because
the case blob holds everything the index needs — which is the property that lets
these two be sequenced rather than merged.

### Three rulings taken at the implementation audit, 2026-09-10

**The Done-when below was unsatisfiable as originally written**, and the audit
that found it measured the live index and the stored blob JSON rather than the
loaded models. All three are governance events under §23.5 and landed in their
own doc-only commit **before** the code commit, on the ordering this step already
uses for its own seven fields.

**1 — Pre-6.12 uploads take `role = "unclassified (pre-ask-binding)"`.** New
§23.2.1 row. the three fields are **absent keys** in the
stored JSON on every pre-6.12 record; what a loaded `UploadRecord` shows for them
is a Pydantic default. The full reasoning, including why the sentinel is not
`other evidence`, is at §23.2.1.

**2 — The backfill's source widens to include the index's own `metadata`.**
`IMPR-2026-E9D` holds one live document (`test_sipoc.png`, 2026-05-27) and **no
upload record at all** — the case blob loads, carries all five phase records, and
its `uploads` list is empty. A backfill sourced only from case blobs never visits
that document, so it would keep `role = null` whatever sentinel were ratified:
**the sentinel fixes a value problem and this is a missing-record problem.** Its
`metadata` blob carries `filename`, `upload_phase` and `timestamp`, and its bytes
survive at `uploads/IMPR-2026-E9D/test_sipoc.png`, so a real digest is computable
without a case record. Following Part AQ4 finding 2 again — hiding a legacy
document is the worse failure.

**3 — A superseded document whose bytes are gone is DELETED, not backfilled.**
`IMPR-2026-ED8` uploaded the same three files twice (08:09/08:10, then 10:23).
The index kept both batches; blob storage kept one blob per filename, because
`storage/blob.py` writes with `overwrite=True`. **The earlier bytes no longer
exist**, so a digest for the 08:09 documents could only be computed from the
10:23 bytes — writing the newer version's digest onto the older chunk, which is
the exact version-identity claim `content_digest` exists to make, made falsely.
§23.2's ratified rule already answers it: *supersession deletes; it does not
flag*, and the index holds only current versions. These three predate 6.12's
supersession path and survive only for that reason. **The case-blob record's
`evidence_index_id` is nulled in the same pass**, or the blob points at a
document that no longer exists.

> ### ⛔ `azure-query` PASSED. `live-run` was ATTEMPTED AND FAILED — and the cause is not this step.
>
> **The status is `done — live half BLOCKED, not owed`, and the last three words
> are the point.** 6.7, 6.9 and 6.12 each landed `done — live half owed`, meaning
> the live-run had not been run. **This one was run.** It failed, the cause was
> isolated to code this step did not touch, and "owed" would file a diagnosed
> blocker under the same word as three un-attempted checks — which is how a
> known defect becomes indistinguishable from a to-do.
>
> **What passed, 2026-09-10.** Sub-steps 1–4 are built and applied. `azure-query`
> confirms all seven fields present and filterable, all four surviving documents
> carrying `role` / `kind` / `content_digest`, `kind eq 'evidence'` returning 4
> and `kind eq 'artefact'` returning 0. 813 tests green, 17 of them new. The
> three superseded documents are deleted and the case blob no longer names them.
>
> **What blocked the live-run, and it is NOT this step's defect.** A Belt asking
> what the to-be process is never reaches an answer: `POST /ask` on
> `IMPR-2026-ED8` returns *"Node 'executor' exceeded its run timeout of 45.000s"*.
> The log shows the planner routing correctly — *"routing to an UNREAD upload …
> call `load_evidence_series` on `uploads/IMPR-2026-ED8/complaints.csv`"* — and
> the executor then calling `rag_lookup_evidence` roughly six times (nineteen
> underlying searches, three per multi-query call) **without ever calling
> `load_evidence_series`**, until the node timeout fires.
>
> **Reproduced on HEAD to prove ownership.** The four changed source files were
> reverted to `1714d75`, the server restarted, and the identical request produced
> the identical failure at the identical elapsed time. **The loop predates 6.13
> and belongs to the executor, not to the evidence index.** The `BlobNotFound`
> entries in the log are first-turn checkpoint misses and are not related.
>
> **What this owes, and it is NOT 6.13's debt:** a diagnosis of why the executor
> ignores a planner instruction naming a specific tool and a specific blob path,
> which is §26 / S-F04 territory and a step of its own. **It also silently
> invalidates the live half of 6.7, 6.9 and 6.12** — three steps carrying `live
> half owed` against a path that cannot currently complete a Define turn on
> `IMPR-2026-ED8`. 6.13's live-run re-runs once that clears, and so should
> theirs.


---

## Step 6.14 — The SKILL.md shape pass: Define, Analyse, Improve, Control

*Original lines 2147–2170.*

> ### ⛔ BLOCKED IN APPENDIX D, 2026-09-11 — the prose said so; the status cell did not
>
> **The note below has said this step is incomplete by design since it was
> written. Appendix D's status cell was EMPTY**, so every tool that reads the
> board called 6.14 the next schedulable step and `CURRENT BUILD STATUS`
> printed it as `Next` — **a pointer at work that cannot start, waiting on
> input deliberately deferred.** The cell is the only part of the row a tool
> reads; a paragraph above it is not a status.
>
> **This is the failure mode Appendix D's own header warns about, inverted.**
> That header explains why the column carries only what git cannot say —
> `BLOCKED`, `GATED`, `EXTERNAL` — and 9.0 carries `EXTERNAL` for exactly this
> reason. **The rule was applied to a step that had landed out-of-band and not
> to one that cannot start**, though the consequence is identical: the pointer
> rests forever on a row nothing can advance.
>
> **The block is an INPUT, not a defect** — unlike 6.10 (G-05/G-35) or the four
> steps behind G-49, no code change unblocks it and nothing is wrong with the
> tree. It clears when the three lists below arrive.
>
> **The cursor moves past this row**, to the lowest unblocked step above it —
> 6.16 when this was written, and **6.17 after 6.16 landed and the count-check
> was renumbered above it** (see that step's note). Either way the spine keeps
> moving while the content is owed.

---

## Step 6.17 — The count-check: a written count against the list it describes

*Original lines 2256–2286.*

> ### ⛑ MOVED OUT OF BAND A ON 2026-09-11 — it is housekeeping, not loop work
>
> **Founder ruling.** This sat at Seq 320, first in THE LOOP, and therefore
> rendered as `BUILDING NOW` — so the first thing on the board was a
> consistency check rather than the first thing that serves the goal.
>
> **The count-check is worth doing and it does not move the product.** It
> stops a written count disagreeing with the list it describes, which is a
> governance property; band A is the one Belt turn running end to end. Moved
> to **Seq 565**, with the rest of the cross-cutting work, and the cursor
> moved to **6.18** — the executor actually completing a turn.

> ### ⛑ RENUMBERED 6.15 → 6.17 on 2026-09-11, and the reason is this table's own rule
>
> **6.16 landed first, which put this step BELOW the last completed one — and
> Appendix D's header says what that means: *"a step inserted below that line is
> never proposed as next and never will be. It does not appear late, it
> disappears."*** The session banner proved it within a minute of the commit:
> `last completed 6.16 | next 7.0`, stepping straight over an unbuilt,
> fully-specified step.
>
> **The ordering was the founder's and correct on its merits** — 6.16 was built
> from data 4a had just corrected, which is the whole point of generating a
> board rather than drawing one. The renumber is the cost of that ordering, paid
> openly. **Numbering here is a schedule, not a taxonomy**, which is why
> remedial storage work sits at 8.7 rather than at 3.6, and why the eight steps
> added 2026-09-07 were all numbered above 6.7.
>
> **The content is unchanged.** Searching this document for `6.15` finds this
> note and the historical change-log entries that named it; those are left as
> written, because they were true when written.

---

## Step 6.25 — Scratch leaves the tree

*Original lines 2608–2644.*



### The condition this ends

**Two working folders sat untracked INSIDE the tree** — `_Artifacts/` at the
root and `agent-improve/_Claude_chat_Prompts/` — and a tracked document cited a
file in each. **A citation from a tracked document to an untracked file
resolves for whoever has the folder on disk and for nobody else**, which is
§55.1's bidirectional rule failing in the direction nothing checks.

**The ignore rule that was supposed to cover one of them matched nothing.**
`.gitignore` carried `ARTIFACTS/` while the directory is `_Artifacts/`. **An
ignore rule that matches nothing fails the same silent way a rule file's
`paths:` glob does**: no error, no warning, and the thing it was written to
handle simply is not handled. `agent-improve/.gitignore` did carry `_Artifacts/`
— scoped to a directory where no such folder exists.

### What to do

**Sort by CONTENT, not by folder.** The folder is not the unit; what a document
cites is.

| | Goes | Because |
|---|---|---|
| Cited by a tracked document | `docs/_archive/`, **tracked** | §0.32 clause 2: if a scratch artifact matters it becomes a tracked file |
| Cited by nothing | **outside the tree**, kept | Clause 2 says outside, not deleted |

**Redact on the way in, because this repository is public.** A file that was
safe as working material is not automatically safe as a published one, and the
check is what the tracked tree does NOT already contain.


---

## Step 6.26 — The guard's tree rules get a test suite (G-57)

*Original lines 2654–2691.*



### The gap this closes

**Rules 7 and 8 of the commit-msg guard are proven by hand and re-run by
nothing.** Ten cases were demonstrated when the rules landed — a staged
`scratch/` path and a staged `.bak` blocked by name, an undeclared new path
blocked, an unresolvable step and an unresolvable gap blocked, a registered gap
on disk but not in the index blocked, the same gap staged in the commit
allowed. **None of it runs again.**

**An index check fails the way a message check fails: silently, by letting
commits through.** That is the argument `test_commit_guard_8d.py` already makes
for rule 6, and it transfers without a word changed. A pattern list that stops
matching reports nothing. A register regex that stops resolving after Appendix
D or §66 is reformatted reports nothing — and **rule 8 is the fourth hook
parsing Appendix D's table and the second parsing §66's**, both of which carry
format warnings in their own headers for exactly this reason.

### What to build

A test file beside the existing guard tests, loading the hook by path the same
way. **It pins what the rules RANGE OVER, not only what they match**: that a
modified path is invisible to both (the ratchet), that a rename into a scratch
name is caught, that the registers are read from the index rather than the
disk, and that a declared number must resolve.

**What it deliberately does not pin** is whether a file genuinely belongs to
the step it declares. Rule 8 checks that a number is declared and exists; that
limit is in its docstring and belongs in the test file too, so a green suite is
not read as evidence the numbers are honest.


---

## Step 6.27 — The watched-path contract has one owner (G-58)

*Original lines 2700–2747.*



### The defect this closes

**One fact, two owners.** §55.2 tabulates the paths that oblige an
`ARCHITECTURE.md` re-check; `commit-msg-refactor-guard.py` hardcodes the same
list as `STATUS_WATCHED`. CLAUDE.md's *Facts have one owner* rule says a value
is stated in exactly one place and cited everywhere else, and this is two
copies of a set.

**It has already drifted, twice, in opposite directions.** The board was added
to both on 2026-09-11 and removed from only the guard on 2026-09-14 — so
between `258d0dd` and this step, the document said thirteen paths and the gate
enforced twelve. The first drift cost `ef59aa8`; the second was created by the
commit that fixed the first, which is the shape this rule exists to stop.

### What to build

**A test asserting the two are equal**, not a second source that reads the
first. Parsing a prose section at hook runtime would put a document on the
critical path of every commit and fail closed on a reformat — §55.2's table is
authored for a human reader and is not a data file. **The equality assertion
gets the ownership benefit without the coupling**: one of the two may move,
and the suite says so before the gate and the document can disagree in
production.

The parse is deliberately narrow and anchored to the fenced block in §55.2, so
a path mentioned in that section's prose is not mistaken for a table row.



---

## The worked case

*Original lines 2883–2891.*

> **The example first offered for this step was wrong and is recorded as such.**
> It was *“the executor times out at 45s while nothing in the repository
> enforces any timeout”*. **The timeout is enforced**:
> `backend/phases/subgraph_common.py:73` sets `EXECUTOR_RUN_TIMEOUT = 45`, line
> 129 attaches `timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT)`, and
> `verify_built.py` re-runs it. What **step 8.2** owns and has not built is the
> bounded **request** timeout at the HTTP layer — a different timeout at a
> different layer. **A step whose purpose is to gate unresolvable citations must
> not open with one.**

---

## Step 6.31 — The build matrix: one row per step, anchored to a symbol

*Original lines 2909–3156.*



**Build status is stated in two places and re-run in one.** `ARCHITECTURE.md`
carries 69 `> **BUILT:**` markers, each mixing *what the thing is for* with
*whether it exists today*; `verify_built.py` re-runs **24** hand-written checks
against the tree. **The two populations are not the same population**, and
nothing makes them converge — 45 markers are backed by no check at all, and a
marker nothing re-runs is, in §55.2's own words, a claim.

**§58.5 is what this step is for.** Its marker reads, in one unbroken block:

> ✅ **all 8 fields exist** — step 6.19 (**G-50 CLOSED**) … **§50.1's four
> presentational fields … are NOT BUILT** (**G-50**)

**Both sentences are in the same marker and they contradict each other.** 6.19
landed and edited the first line; the paragraph beneath it still describes the
world before. That is not an editing slip — it is the predictable outcome of
storing a *status* inside a *design rationale*, where the reader's eye goes to
the prose and the status rides along unmaintained.

### The ruling this step carries

> ### ✅ RULED 2026-09-15 — STATUS LEAVES `ARCHITECTURE.md`; RATIONALE STAYS
>
> **`REFACTORING_PROCEDURE.md` is the single leading document for build
> status.** No new file: this document already owns the route, and a third
> document would be a third place for the same fact to go stale.
>
> **Design rationale STAYS in `ARCHITECTURE.md`.** *Why* `CoachingResponse`
> splits `message` from the four presentational fields is architecture and
> belongs nowhere else. *Whether the class has eight fields today* is build
> status and belongs here, next to the step that put them there.
>
> **`CONTINUITY.md` CITES, IT DOES NOT MOVE.** It is the first-read document
> and it stays terse. Its hand-written vertical becomes a generated projection
> of Appendix F's `Order` column into the region the pre-commit hook already
> rewrites.

### Appendix F — the shape, and why each column is there

**Seven columns, organised BY LAYER.** One row per step, so the matrix and the
plan cannot describe different populations.

| Column | Owns | Why it is not somewhere else |
|---|---|---|
| **Layer** | which part of the system the step changes | the organising axis — the thing a reader scans for |
| **Order** | the near-term execution sequence | **the only hand-set column.** Sparse: a number means *"in the run of work being done now"* |
| **Step** | the identifier | **`GROUP BY Step` is the completeness assertion** |
| **Item** | what the step delivers | joined from Appendix D's title; never retyped |
| **State** | ✅ / ⚠️ / ☐ / ⛔ | §55.2's vocabulary, unchanged, moved |
| **Evidence** | the anchor that proves the State | **the column that makes this a matrix and not a caption** |
| **§** | the ratified section that owns the rationale | joined from Appendix A — *cite, do not move* |

> **`Order` IS NOT Appendix D's `Seq`, and conflating them would lose the
> thing the founder actually asked for.** `Seq` is the global schedule and the
> board already renders it as four bands. `Order` is the **short vertical a
> founder works to** — what `CONTINUITY.md`'s hand-written *"NEXT WORK"* list
> has been since 2026-09-14. It is sparse, it is hand-set, and it is the one
> column nothing derives.

### The anchor grammar — never a line number

**A line number is not an anchor.** It is invalidated by an edit to any line
above it, which is to say by almost every commit, and it fails silently by
pointing at the wrong line rather than at nothing.

| Form | Means | Passes when |
|---|---|---|
| `mod::Symbol` | the symbol resolves | import succeeds and the attribute exists |
| `mod::Symbol {a,b}` | set equality over its members | dict keys, model fields, or `.name` of its elements, exactly |
| `mod::Symbol =v` | scalar equality | `str(value) == v` |
| `absent: <anchor>` | the anchor does **not** hold | **this is what proves a `☐ not built` row** |
| `installed: <anchor>` | resolved against the **installed library** | a failure prints as a **DEPENDENCY finding**, never a marker one |
| `repo:<path>` | a path, from the **repository root** | the path exists |
| `azure:<resource>` | an Azure-side fact | **EXTERNAL — owed, never passed** from this machine |

> **`repo:` is explicit because the ambiguity is a real trap, and it cost five
> false failures on the evaluator's first run.** `.claude/` sits ABOVE
> `agent-improve/`, so a bare relative path resolves against whichever root the
> caller happened to pass, and reports a present file as absent.
>
> **A BEHAVIOUR IS ANCHORED ON THE TEST THAT OBSERVES IT, and that needs no
> new form.** Steps 2.6, 6.22, 6.26 and 6.27 deliver a behaviour spread over
> many sites with no single symbol to name — so their Evidence is the test
> function, which is still `mod::Symbol`. This was nearly ruled a fifth form;
> it is not one.
>
> **`installed:` failures are a DIFFERENT finding with a DIFFERENT owner.** A
> library that moved under us is not a stale marker, and reporting both as
> *"the matrix disagrees with the tree"* would train a reader to re-baseline
> the matrix to silence a dependency upgrade.

### The two assertions

**1 — `GROUP BY Step` covers Appendix D exactly.**

> ⚠ **THE LITERAL 69 IS WRONG BY ONE THE MOMENT THIS STEP LANDS.** The ruling
> said *"GROUP BY Step must return exactly 69. Assert it."* Appendix D carried
> 69 rows when that was written; **this step adds 6.31 and makes it 70.** A
> hardcoded `69` would fail on the very commit that introduces it.
>
> **So the assertion is SET EQUALITY against Appendix D, in both directions**,
> which is strictly stronger than the count the ruling asked for: a count of
> 69 passes when one step is dropped and another added, and set equality does
> not. It is also this document's own lesson — *"the total is the row count"*,
> and *"edit the band here, not in the generator"*.

**2 — every `absent:` cell is removed by its owning step's Done-when.**

Without that clause the matrix **rots in the opposite direction from the
markers**. A marker goes stale by claiming something is built when it is not;
an `absent:` cell goes stale by claiming something is *missing* after it has
been built — and the referee catches that one, loudly, because the anchor
starts resolving. **The failure is the feature**; the step that builds the
thing must replace its cell with a positive anchor in the same commit.

> **Deletion steps invert the polarity, and 11.1 is the case.** *"Delete v1"*
> makes an ABSENCE true. So its not-built anchor is the POSITIVE form —
> `backend.core.state::ImproveGraphState` resolves today, and that is exactly
> why the row reads ☐ — and its Done-when flips the cell to `absent:`. Stated
> here because the first seed got it backwards and the referee caught it.

### `verify_built.py` becomes the referee, fail-CLOSED

The 24 hand-written checks stay. Appendix F's rows are read and evaluated
**alongside** them, under the same reporting and the same exit code.

**Fail-CLOSED, and that is a change of character for this script.** It has been
advisory — `build_board.py` calls it and the board renders either way. As the
referee for the one document that now owns build status, an internal error must
BLOCK, on the argument `CONTINUITY.md` §7 already makes and the commit-msg
guard already follows: *a check that cannot fail is worse than no check,
because it is recorded as evidence.*

**Each new check lands with a mutation proof, per §0.4** — break it, watch the
named test go red, restore from a baseline held OUTSIDE the tree, watch it go
green. Never `git checkout --`.

### The board shows the vertical — §55.2's colour rule is not touched

`board.html` renders the `Order` column **above the five lanes**, as the
sequence. The founder opens the board from the repo and needs the run of work
visible there, not only in a table inside a 4,000-line document.

**Lane and marker colours are unchanged.** `Order` is a POSITION IN A PLAN, so
it renders in the lane family, never in the marker family — §55.2's *"a lane
state and a marker state may never share a colour"* applies to this addition
exactly as to everything else. **The full C4 container picture is a later step
with its own number and is not this one.**

### Two §56 amendments land in the same commit

**`ARCHITECTURE.md` v1.63 → v1.64.**

1. **S-C05's four presentational fields become `default=""`.** They are
   REQUIRED `str` today, so a model omitting `progress` fails the whole turn's
   structured output — against §4.8's *never a hard failure to the Belt*. **An
   empty field is recorded as a FINDING**, which is the behaviour §50.1 wants:
   the block renders, and the gap is visible rather than fatal.
2. **Build status begins leaving the document.** §55.2 gains the pointer to
   Appendix F and the rule that a marker states rationale, not status.

> ⚠ **THE VERSION NUMBERS MOVED BY ONE AND THAT WAS NOT A CHOICE.** The ruling
> said v1.62 → v1.63 for these two. **G-63's fix consumed v1.63** — guard rule
> 2b obliged `ARCHITECTURE.md` into that commit, because `nodes_common.py` and
> `knowledge/tools.py` are both watched paths and §66's G-63 row was still
> saying *"NO FIX PROPOSED"*. These two are therefore **v1.64**.

**`REFACTORING_PROCEDURE.md` v1.6 → v1.7** — Appendix F, and this step.

### The marker migration is NOT in this step

**One at a time, by judgement, after this lands.** §58.5 goes first, because it
is the one that states both versions of the same fact in a single block.
Rationale stays; status moves. **Not a script** — a marker's prose has to be
read to know which half is which, and a regex that guessed would produce 69
edits nobody reviewed.

### ⚑ THE FORECAST, RECORDED SO IT CAN BE SCORED

**When the 69 markers migrate, 9–15 of them will disagree with the tree**, and
**the ⚠️ band will fail more often than the ☐ band.**

**The reasoning, so a wrong forecast is informative rather than just wrong.** A
`☐ not built` marker asserts an ABSENCE, and absences are stable — nothing
drifts into existence. A `⚠️ built with a known defect` marker names a SPECIFIC
defect on the same line, and that line goes stale two ways the ☐ line cannot:
the defect gets fixed in passing and nobody edits the marker, or the defect is
re-described in a later audit and the two descriptions diverge. **15 markers
are ⚠️ and 15 are ☐** as of this commit, so the bands are the same size and the
comparison is fair.

**Scoring it is part of the migration's Done-when**, not an optional look back.

> **What the seed already scored, and it is evidence for the forecast.** The
> 70 seeded anchors ran against the tree before this step was written: **66
> PASS, 3 EXTERNAL (Azure), 0 FAIL** — but that is the score AFTER eight
> corrections, and **five of the eight were wrong anchors in the seed rather
> than disagreements in the tree** (the `repo:` root ambiguity, twice a symbol
> that does not exist under the name the document used). **Two were real
> findings** and are recorded below.

### What the seed found on its first run — two real defects

**(a) G-52 was recorded closed at a step the git-log scan could not see —
RESOLVED 2026-09-15.** §66 read *"CLOSED 2026-09-13 at step 6.22"* while git
carried only `2e17f3f fix(tests): the stack ordering is observed on a real
graph — G-52 closed`, with **no `refactor(arch-v2): commit 6.22` subject**, so
Appendix D showed 6.22 unlanded and the pointer would have stopped on it.

**`2e17f3f` was checked against 6.22's Done-when before anything was changed,
rather than assumed from its subject line**: the new test is
`backend/tests/test_middleware_execution_order.py`, `pytest` was green at 896,
and the separating mutation gave **stubbed 5 passed, new 2 failed**. It even
corrected the step's own Done-when, which had specified a mutation that
separates nothing. **It satisfies the step in full**, so 6.22 takes `EXTERNAL`
with its commit cited and §66's closure claim STANDS. `EXTERNAL`'s definition
is widened in the reading conventions in the same pass, because *"not a code
change"* alone would have been a false statement about it.

**(b) Appendix A is a DUPLICATE that fell behind — registered as G-64, owned by
step 6.17.** It has **59 rows against Appendix D's 70**, missing 6.22–6.31 and
9.2.

> **⛑ THE FIRST READING OF THIS WAS WRONG, AND THE CORRECTION IS THE POINT.**
> It was reported as *"ten steps have no Appendix A row"*, against Appendix A's
> rule that *"a step with no reference section is not a step"* — which reads
> as ten undocumented decisions. **All eleven steps DO carry a `Reference §`
> row in their own section**, checked afterwards. Nothing is undocumented.
> **The COPY is incomplete**, which is a different defect with a different fix:
> *Facts have one owner*, the same class as G-58's watched-path list.
>
> **So the fix is not to type eleven rows** — that leaves the second copy in
> place and buys one commit of agreement. It lands on **6.17** because that
> step's boundary is *"a claim against the list in the same document"*, and
> both tables are in this file.

**Thirteen steps also carry no `Touches` row.** Recorded here, not registered:
unlike the `Reference §` case there is no second copy to disagree with, so it
is an absence rather than a drift.


---

## Step 6.16 — The board is generated, not written

*Original lines 3205–3374.*



**Not in the original spine. Added 2026-09-10.** The refactor board is hand-made
in a chat and **goes stale the moment a commit lands**. Four captions in this
repository have already outlived the lists they describe (`DECISIONS.md` Part
AR3) — the tracker row that carried two descriptions, the 6.9 row's badge,
CLAUDE.md §10.1's field count, §29.3's universal count. **A hand-written board
is the fifth waiting to happen**, and it is the one a founder reads.


**`Zone`** — one of seven: **UI · SUP · PHASE · COACH · GATE · STORE · OPS.**
Which container the step changes. A step may carry two; **the first is primary.**

**`Impact`** — one sentence: **what is true about the product if this step is
never done.** Not a restatement of the title. The shape is
*"Nothing ever pauses for a human, so no gate decides and the supervisor graph
is never the runtime"* — a consequence, in the product's terms.

> **`Impact` is the column that lets a reader judge whether a step is worth its
> slot, and it exists in no document today.** Every other field on the board is
> a projection of something already tracked; this one is new information and is
> **the bulk of this step's work** — 55 sentences, each of which has to be true
> and none of which can be derived. Write them from the step's own section,
> which usually already argues the consequence in prose.

> **⚠ THE ZONE-TO-BLOCK MAPPING IS NOT 1:1 — SETTLE IT FIRST.**
> `ARCHITECTURE_STATUS.md` carries **eight** Level 1 blocks; this column has
> **seven** zones. A 3→1 collapse and a 1→2 split:
>
> | Zone | Block |
> |---|---|
> | UI | 1 — API surface |
> | SUP | 2 — Supervisor graph |
> | PHASE | 3 — Phase subgraphs |
> | **COACH** | **4 + 5 + 6** — the coaching agent, the middleware stack, tools and knowledge |
> | GATE | 7 — Validation, gates and escalation |
> | **STORE** | **8, persistence half** |
> | **OPS** | **8, cross-cutting half** |
>
> Container 1 is drawn from the blocks and container 2 is coloured by zone, so
> **without a declared mapping the two cannot cross-highlight** — which is most
> of what a board is for. **Declare the table above in the generator as DATA,
> not as a comment**, so adding a block or a zone raises a `KeyError` rather
> than silently unmapping a step.

> ### ⛑ TWO OF THIS STEP'S PREMISES WERE STALE BY THE TIME IT WAS BUILT
>
> **Corrected 2026-09-11, while building it.** Recorded here rather than
> silently worked around, because this is the step about captions outliving
> their lists and its own specification had done exactly that.
>
> **1 — `ARCHITECTURE_STATUS.md` is ARCHIVED.** Sub-step 2 below and the
> generator's second source both name it. It moved to `docs/_archive/` on
> 2026-09-10 and its tables became the `> **BUILT:**` markers inside
> `ARCHITECTURE.md` (§55.2) — the very commit that also added this step.
> **The markers are read there instead**, and the parseable closer landed on
> them as a trailing `· **closes:** `[X.Y]`` / `[none]` token: twenty markers,
> every one tokened, `[none]` written explicitly so *"nothing closes this"* and
> *"nobody wrote it down"* stay distinguishable.
>
> **2 — THE ▶ CURSOR DOES NOT EXIST**, and sub-step 4's lane table names it
> twice: `BUILDING NOW | the ▶ cursor` and `DONE | Appendix D says done`.
> Both were deleted on 2026-09-10 — completion is the highest spine subject in
> git log, and the status column stopped carrying `done` because it was a
> second hand-maintained source for a fact git owns. **This step's own
> amendment note says so** about the fourth source and did not carry the
> correction down into its lane table. `BUILDING NOW` is now derived with the
> **same next-step rule `session-start-context.py` uses**, so the board and the
> session banner cannot disagree about what is next; `DONE` is `git log ∩
> Appendix D`.


**Every ☐ and ⚠ row already names its closing step in prose.** Move it to a
fixed position — a trailing **`[6.10]`** or equivalent — so the generator reads
a token rather than parsing a sentence.

**Rows with no closing step say so explicitly** — `[none]` — rather than being
silent. A silent row and an unparseable row look identical to a generator, and
the difference between "nothing closes this" and "nobody wrote it down" is
exactly what this project keeps losing.

> **This is the same move `▶` made and for the same reason.** A cursor in prose
> is a sentence a tool has to understand; a cursor in one cell is a token it can
> read. §55.1's bidirectional rule works because references are literal strings.


**It reads four documents and nothing else:**

| Source | What it takes |
|---|---|
| **Appendix D** | every step, its status, **zone**, **impact**, and the total |
| **`ARCHITECTURE_STATUS.md`** | the eight blocks, the control points, built states, **and each unbuilt row's closing step** |
| **`ARCHITECTURE.md` §66** | the gap register, for blocked reasons |
| **git log** | **which steps have landed** — the `refactor(arch-v2): commit X.Y` subjects |

> **⚑ AMENDED 2026-09-10 and the amendment reverses one of this step's own
> premises.** The fourth input read `BUILD_TRACKER.md` for *"the ▶ cursor"*.
> **That file is deleted and the cursor no longer exists**: completion is the
> highest spine subject in git log, and `next` is the lowest available Appendix
> D row above it.
>
> **The constraint below explicitly forbade reading git log**, on the grounds
> that it would *"report something no reviewer ratified"*. That reasoning does
> not survive contact with what replaced it. **A commit subject is the most
> reviewed artefact this project produces** — rule 1 of the commit-msg guard
> refuses a malformed one, so a spine subject cannot enter history without
> passing a check, which is more than any hand-typed `▶` ever had to do. The
> alternative the constraint was protecting fired wrong twice (2026-09-08 on
> step 7.1, 2026-09-10 on step 6.16) because it read English prose.
>
> **What the constraint still forbids stands**: no reaching into the CODE, and
> no figure on the board that traces to nothing. Git history is a ratified
> record, not an inference from the tree.

**Reading nothing else is a constraint, not a description of one.** A generator
that reached into the code would report something no reviewer ratified.
**Every figure on the board must trace to a line a human approved** — which is
the same rule §55.1 applies to references and the reason
the board can be trusted at a glance.

**Writes `docs/board.html`** — four containers:

| # | Container | Carries |
|---|---|---|
| **0** | **The timeline** | now → testing |
| **1** | **The nested architecture diagram** | **every ☐ and ⚠ carrying its step number** — so a reader looking at a hole sees which step fills it, without leaving the picture |
| **2** | **Five lanes** | QUEUED · BUILDING NOW · BLOCKED · READY · DONE |
| **3** | **A detail panel per task** | including its **impact** |


| Lane | Rule |
|---|---|
| **BLOCKED** | its precondition is unmet, **or** an open §66 gap names it — the gap is the displayed reason |
| **BUILDING NOW** | the ▶ cursor |
| **READY** | preconditions met |
| **DONE** | Appendix D says `done` |
| **QUEUED** | everything else, in Appendix D order |

**Nothing anywhere declares a lane.** A declared lane is a fifth caption to keep
current; a derived one cannot disagree with the table it came from.


*(Carried from the 2026-09-10 scoping message, which truncated before restating
it — flagged rather than assumed.)*

Beside the `CONTINUITY.md` regeneration and under the same rule: **a hook that
writes must never wedge a commit.** A generator that raises leaves the previous
board in place and logs; it does not block the commit that would have refreshed
it.


*(Carried from the same message.)*

`commit-msg-refactor-guard.py`'s rule 2b, so **a stale board is visible the same
way a stale `ARCHITECTURE_STATUS.md` is** — the board is a projection of
documents that move, and the guard is what notices when the projection did not
move with them.


---

## Step 6.18 — The executor ignores the tool its own planner names (G-49)

*Original lines 3383–3518.*



**A DIAGNOSIS STEP. Its deliverable is a cause, not a feature.** Registered as
**G-49** on 2026-09-10, found while running 6.13's `live-run`, and **reproduced
identically at `1714d75` on 6.12's code** — so it belongs to neither step and
has no owner until this one.

### What was observed, and it is precise

`POST /ask` on `IMPR-2026-ED8`, a Belt asking what the to-be process is:

- The **planner routes correctly** — *"routing to an UNREAD upload … call
  `load_evidence_series` on `uploads/IMPR-2026-ED8/complaints.csv`"*. The plan
  names a specific tool and a specific blob path.
- The **executor then calls `rag_lookup_evidence` roughly six times** —
  nineteen underlying searches, three per multi-query call — **and never calls
  `load_evidence_series` at all.**
- No `uploads/` blob is fetched in the entire turn. The 45s node timeout ends
  it: *"Node 'executor' exceeded its run timeout of 45.000s"*.

### Why this is a step of its own rather than a bug fix

**§17 gives the planner the routing decision and the executor the execution.**
Here the executor silently substitutes its own strategy — which is not a
degraded version of the split, it is the split not existing at runtime. **A fix
guessed at before the cause is known would most likely be prompt wording**, and
prompt wording is exactly what cannot be shown to have worked: the failure is
probabilistic and the same request must be replayable against a changed build.

**IT BLOCKS THE `live-run` HALF OF FOUR LANDED STEPS** — 6.7, 6.9, 6.12 and
6.13 — because all four verify through a path that cannot currently complete a
Define turn on this case. That is what makes this schedulable rather than
merely open: **four steps carry verification debt that only this step can
discharge.**

> **⚠ 6.9 IS ON THAT LIST AND SHOULD PROBABLY NOT BE.** Found by the three-way
> alignment audit, 2026-09-11: 6.9's **Verify is `pytest`** and **every clause
> of its Done-when is satisfied by the tree** — five SKILL.md files, both
> mandatory instructions, a test asserting the count and both instructions per
> file. It has no live clause at all. **Either its Done-when is missing a
> clause someone intended when they filed it under G-49, or it never belonged
> there.** Settle that here rather than carrying it a fifth time — and if it
> never belonged, say so in the commit body and take 6.9 off the G-49 register
> entry in the same pass.

### What the step must produce

1. **A reproduction that is not a story.** The request, the case, the build,
   and the observed tool sequence, runnable again after a change. The 2026-09-10
   revert-to-`1714d75` reproduction is the model.
2. **A cause, named at one of four layers** — and it is worth stating them up
   front because they need different fixes and only one is a prompt change:
   the tool is not bound at call time; the plan does not reach the executor's
   context; the model sees the plan and deprioritises it; or `load_evidence_series`
   is bound but unattractive next to three multi-query retrieval tools.
3. **A deterministic test that fails on today's build.** The `pytest` half runs
   **after** the `live-run`, which inverts this document's usual order, because
   **there is nothing to pin until the cause is known.** A test written first
   would pin the symptom — a timeout — and pass the day the timeout is raised.

> **THE FIX MAY NOT BELONG TO THIS STEP.** If the cause is structural — the
> executor needing a bound-tool ordering rule, or the planner's instruction
> needing to arrive as something other than prose — that is a change to §17 or
> §26 and lands as a §56 amendment plus its own step. **This step ends when the
> cause is established and the four blocked live-runs can be scheduled**, not
> necessarily when the behaviour changes.

> ### ✅ DIAGNOSED 2026-09-11 — LAYER 2: THE PLAN DOES NOT REACH THE EXECUTOR'S CONTEXT
>
> **The `live-run` ran first and it reproduced**, on `09960df`, unchanged from the
> 2026-09-10 record:
>
> | | 2026-09-10, on `1714d75` | 2026-09-11, on `09960df` |
> |---|---|---|
> | Request | `POST /ask`, `IMPR-2026-ED8`, *"what does our to-be process look like"* | identical |
> | Planner | routes to the unread upload, names `load_evidence_series` and the blob path | identical — `plan: business_case / Call load_evidence_series on uploads/IMPR-2026-ED8/complaints.csv before asking for anything further` |
> | Executor | ~6 `rag_lookup_evidence` calls, 19 underlying searches | 3 `rag_lookup_evidence` calls, **18 underlying searches** (6 queries per call, fused 3 ways) |
> | `uploads/` blob fetched | none | **none** — every blob request in the turn is a checkpoint, the store's case record, or the case JSON |
> | Ending | node timeout at **45.157s** | node timeout at **45.141s** |
>
> **THE CAUSE IS LAYER 2, and the other three are ruled out on evidence rather
> than on argument:**
>
> | Layer | Verdict | What decides it |
> |---|---|---|
> | 1 — the tool is not bound at call time | **RULED OUT** | `load_evidence_series` has been in `UNIVERSAL_TOOLS` since step 6.12 — six tools — and `_executor_tools` strips only the three `rag_lookup_*`, only on §26's `remaining_steps` off-ramp. The failing turn issued 18 searches, so its hop budget was non-zero and the whole universal set was bound. Pinned across all five phases by `test_load_evidence_series_is_bound_on_every_phase` |
> | **2 — the plan does not reach the executor's context** | **THE CAUSE** | `executor()` invokes the agent with `{"messages": prior}`. `plan = state.get("coaching_plan")` is read for the logger and for `step_log` and for **nothing else**. `system_prompt=PHASE_COACH_PROMPT[phase]` is a per-phase constant composed at import. `BeforeModelStateInjection` — the only middleware handed state — contains **no occurrence of `coaching_plan`, `focus_field` or `next_action`**. Measured at the boundary: the planner's imperative appears in none of the three channels the model reads — system prompt **7,770 chars**, injected block **797 chars**, messages **5 chars**. Pinned by `test_the_planners_instruction_reaches_the_model`, `xfail(strict=True)` |
> | 3 — the model sees the plan and deprioritises it | **EXCLUDED BY CONSTRUCTION** | a model cannot deprioritise what is not in its request. Layer 2 forecloses layer 3; there is nothing left to measure |
> | 4 — bound, but unattractive beside three multi-query retrieval tools | **PRESENT, AND NOT THE CAUSE** | the coach is not uninformed. The manifest reaches it every turn — the file, `NOT YET READ`, the `blob_path`, and the tool that opens it — **2,893 composed chars on the failing run** — and it still issued 18 searches. That is a real ranking problem, and it is why the manifest alone cannot carry the guarantee. **Ranking explains a preference; it does not explain the absence of an instruction** |
>
> **THE SHARP FORM OF IT.** This node's own comment says routing on an unread
> upload *"is the only point in the loop that is not the model's discretion"*.
> Because the plan has no transport into the request, **it is entirely the
> model's discretion** — the planner decides, logs that it decided, and the
> decision stops there. §19.1's manifest makes the coach AWARE; the planner's
> routing was meant to make it ACT; **the third leg of that guarantee was never
> connected.**
>
> One detail worth keeping, because it compounds layer 4: the static coach prompt
> names four tools — `rag_lookup_methodology`, `rag_lookup_case_history`,
> `propose_template`, `propose_diagram` — and names **neither**
> `rag_lookup_evidence` **nor** `load_evidence_series`. The only place the model
> is told which tool opens an upload is the manifest.
>
> **THE FIX IS NOT IN THIS STEP, AND THAT IS THIS STEP'S RULING.** The cause is
> structural: the plan needs a transport, and choosing one changes §17 — the
> planner/executor split — or §19.1 — the injected block, whose composition and
> token budget are **G-24, explicitly founder-owned**. It lands as **step 6.21 —
> the plan reaches the model**, `GATED` on that ruling, with the four candidate
> transports costed in its own section. Guessing one here is what the step
> forbids: *"a fix guessed at before the cause is known would most likely be
> prompt wording"*.
>
> **6.9 IS RULED OFF THE G-49 REGISTER — it never belonged.** Its `Verify` is
> `pytest`, it has no live clause anywhere, and every clause of its Done-when is
> satisfied by the tree. **One correction to the audit that raised it:** it
> recorded *"a test asserting the count and both instructions per file"* as
> satisfied, and only the count was. All five files do carry both instructions;
> nothing asserted it. `test_every_skill_md_carries_both_mandatory_instructions`
> now does — a missing assertion over correct content, which is the kind nobody
> notices because the tree is right.
>
> **THE THREE REMAINING LIVE-RUNS ARE RE-SCHEDULED, WITH A DATE.** 6.7, 6.12 and
> 6.13 re-run **on the first `live-run` after step 6.21 lands** — they exercise
> the same Define turn on `IMPR-2026-ED8`, which still cannot complete, so
> running them today would only re-measure this defect. **If 6.21 has not landed
> by 2026-09-25, the block is re-reported to the founder rather than carried
> quietly into a fifth step.** That date is the point of this clause: `owed` was
> what let this sit through four steps.


---

## Step 6.19 — `CoachingResponse` gains §50.1's four presentational fields (G-50)

*Original lines 3530–3593.*



**Registered as G-50 by the three-way alignment audit, 2026-09-11.** S-C05
ratifies **eight** fields and the built class carries **four**: `message`,
`fields_captured`, `citations`, `contradiction_flag`. **`explanation`,
`example`, `prompt` and `progress` do not exist.**

### Why this is not cosmetic

**§50.1 calls this contract *"schema-backed, not prompt-hoped"* and today it is
prompt-hoped.** The one presentational field the UI receives is `message` —
**the single free-text blob that section exists to forbid.** Its own reasoning:
*"prose one turn and structure the next erodes trust, and a prompt asking for
structure produces exactly that inconsistency; a schema field cannot be
skipped."*

**There is nothing structured for a gate UI to display.** Step 10.2 renders the
live gate document and 10.1 streams the turn; both assume one block per field
and neither can be built against a blob. **This step is upstream of both**, and
it is `READY` while they are not, which is the argument for doing it early
rather than folding it into 10.2.

**Five SKILL.md files already instruct the coach to fill these four fields** —
that is step 6.9's second mandatory instruction, and the files name
`CoachingResponse.explanation` and the rest explicitly. **So five live prompts
currently name four fields the response schema cannot receive.** The
instruction is not wrong; it is inert, and it has been since 6.9.

> **⚑ THIS IS WHAT ACTUALLY CLOSES WATCH 9, AND 6.9's SECTION CLAIMS TO.**
> That step's body reads *"without which `explanation`/`example`/`prompt`/
> `progress` stay empty for that phase"* — true, and it treats the SKILL.md
> instruction as sufficient. It is not: the fields must exist before an
> instruction to populate them can do anything. **6.9's claim on WATCH 9 is
> corrected when this lands**, and until then WATCH 9 is open with 6.9 marked
> done, which is the ambiguity the alignment audit exists to remove.

### The rebuild test failed inside the file that cites it

`core/substate.py`'s docstring reads *"the four fields below are transcribed
from that entry"* — against an entry defining eight. **S-C05 carries a rebuild
test** (*"reconstructable from this entry alone"*) and the built class asserts
conformance to it in prose while breaking it. **Correct the docstring in the
same commit**; a transcription claim that survives the transcription being
completed is the next stale caption.

**`message` is NOT replaced and the split is the point.** S-C05 is explicit:
`message` is the **transcript** entry, appended to `messages` and compressed by
§19.3's summarization; the four are the **render contract**, drawn one block
per field. **Collapsing them is what §50.1 forbids; dropping `message` would
leave the conversation history with nothing to append.** Eight fields, not
four renamed.

> **ADDING A FIELD HERE REQUIRES A §56 AMENDMENT** — S-C05 says so, the same as
> `SupervisorState` and `PhaseState`. **These four are already ratified**, so
> this step APPLIES a ratified definition rather than amending one, on the
> RATIFIED-NOT-YET-APPLIED precedent §23.2 set. No amendment is owed; the BUILT
> marker and the G-50 register entry move to closed.


---

## Step 6.20 — The write paths: `computation_results`, `phase_metrics`, `field_index`

*Original lines 3605–3711.*



**Found by the targeted state audit, 2026-09-11.** Three things §39.x.7
specifies are **read by the gate document and written by nothing**. Each is a
one-directional break: the reader exists, is correct, and always finds nothing.

| What | Specified | Built |
|---|---|---|
| `artifacts["computation_results"]` | `knowledge/computation.py`: *"the executor wraps it in §7's full shape and writes it"* (B6) | **no write site.** All five `assemble_*_gate_document` read `artifacts.get("computation_results", [])` and always get `[]` |
| `artifacts["phase_metrics"]` | §39.x.7, every phase: *"artifacts holds the N captured fields **+ `phase_metrics`**"* | **no write site.** Same five readers, same always-empty |
| `field_index` | §39.x.7: *"walks the §39.x.2 list"* | set to `0` by the input mapper and **never read or advanced by any node** |

> **THE GRADER IS THE REASON THIS IS NOT COSMETIC.** §35 and §41 have it answer
> *"was a hypothesis test actually run?"* by **scanning `computation_results`
> for `"tool": "t_test"`** rather than by reading the coach's prose — which is
> the whole anti-hallucination design. Against a list that is always empty,
> **the grader's answer is always "no"**, and a gate document records that a
> project did no analysis whatever the Belt and the coach actually did.

**The mechanism already exists and is already used.** `_mark_consumed` in
`phases/nodes_common.py` inspects the turn's tool calls after the fact to stamp
`consumed_at` — ruling AR-R4's *"a `@tool` receives only its arguments and
cannot reach `PhaseState`, so the node inspects the turn's tool calls
afterwards."* **The same inspection, over computation tools instead of
`load_evidence_series`, is what this step writes.** No new pattern.

**`field_index` needs its list before it can walk it.** Only Define has an
ordered `*_FIELD_ORDER`; Measure, Analyse, Improve and Control expose **tier
SETS only**, so the §39.x.2 sequence does not exist in code for four of the
five phases whose §39.x.7 tells `field_index` to walk it. **Define is the slice
being proven, and Define has the list** — so this step advances `field_index`
for Define and the other four get their ordered list with their own slice
(§39.x.2 already states the order; it is a transcription, not a decision).

### ⚑ THE RULING THIS STEP CARRIES: the five `{Phase}State` variants are NOT built

**Founder ruling, 2026-09-11.** `DefineState`, `MeasureState`, `AnalyseState`,
`ImproveState` and `ControlState` **do not exist and will not be built.**

- **They never existed.** The state audit found **zero occurrences in
  `backend/`** and no subclass of `PhaseState` anywhere. S-C03 assigns them to
  `core/substate.py` at **step 3.1** — a step that is DONE and whose Done-when
  (*"both modules import, and a field-count assertion passes"*) never mentioned
  them.
- **They were never specifiable.** **G-19** records exactly why: *"the
  phase-specific transient fields are never enumerated for any of the five."*
  A class whose fields nobody could name for two months is not a design that
  was missed — it is a design that was never made.
- **§7 already ruled against the one concrete case.** *"No new top-level
  `PhaseState` field, and no per-phase typed destinations"* — the grader
  answers by scanning one list, and typed per-phase destinations *"multiply
  schema surface for a question a scan already answers"*.

**What §39.x.7 becomes: a description of per-phase USAGE of the shared
24-field `PhaseState`** — which is what those tables always actually contained.
Every row in them already reads *"`artifacts` — holds the 10 captured
fields…"*: **usage of a shared field, not the declaration of a new one.** Only
the heading and one sentence per section ever claimed a variant class.

> **The thirteen references go.** Four section headings and their opening
> sentences, S-C03's purpose, §6's list, and two mapper docstrings. **G-19
> closes with the ruling** rather than staying open against a class that will
> not exist.

> **⚠ DEFINE HAS NO §39.1.7 AND GAINS ONE HERE.** Its 39.1.7 is the SKILL.md
> content; the state-parameters section exists for Measure, Analyse, Improve
> and Control only. **The phase this project is proving first is the one phase
> with no state contract at all** — so this step writes Define's, in the same
> shape as the other four, and that is what the `manual-UI` half checks
> against.


> ### ⇒ THREE CLAUSES STRUCK 2026-09-23 — ONE MOVED, TWO ALREADY SATISFIED
>
> | Clause | Why it is gone |
> |---|---|
> | *“a grader run … finds it in `computation_results`”* | **MOVED TO 7.2**, where §62.9 B3 already specifies it. It is **validation stack Layer 2d's** scan, not `DMAICGraderMiddleware`'s, and §36 forbids conflating the two — so this clause put a GATE check inside a step that builds the TURN path, and 6.20 could only ever have satisfied it by building the wrong grader. ARCHITECTURE.md v1.69(B) corrects §7 and §39.3.7, which is where the conflation entered |
> | *“Define's own §39.1.7 written”* | **ALREADY SATISFIED at §39.1.12**, 2026-09-11 |
> | *“G-19 closed”* | **ALREADY SATISFIED** — closed by ruling 2026-09-11; §66.6 carries it struck |
>
> **A Done-when clause that is already true is not harmless.** It makes a step
> look unfinished when it is not, and it invites a session to “do” it again —
> which for the two satisfied clauses means re-amending a section that is
> already correct.
>
> **AND THE SCORECARD HALF IS NOW UNBLOCKED.** `artifacts["phase_metrics"]`
> above was never blocked on code; it was blocked on **Define's entry shape
> never having been written down**. ARCHITECTURE.md **v1.69(A)** writes it into
> §39.1.9: five keys, assembled deterministically in `gate_apply` with no model
> call, so the single-authority invariant holds by construction.


---

## Step 6.21 — The plan reaches the model (G-49's fix)

*Original lines 3719–3836.*



**Step 6.18 named the cause at layer 2: the plan does not reach the executor's
context.** The planner decides, writes `CoachingPlan.next_action`, logs the
decision — and the executor invokes the agent with `{"messages": prior}`, so
nothing the planner decided is in the request. This step gives the decision a
transport. **It was GATED rather than READY because every candidate changes a ratified
section**, and two of them change what §17 means.

> ### ✅ RULED 2026-09-11 — OPTION C, and the scope is part of the ruling
>
> **The node executes the planner's named call itself when `coaching_plan`
> routes to an unread upload. The coach model is never offered that decision.**
> Scoped to that one case: every other tool stays model-chosen.
>
> A and B leave the guarantee probabilistic in front of a model that had already
> issued 18 evidence searches against the file the plan named; D stays
> unverified against the installed library. **C is the only candidate whose
> guarantee does not depend on how the model ranks an instruction.**
>
> §17's executor row gains the node-issued call and the planner's *"Never
> dispatches"* row is untouched — the planner still decides and still calls
> nothing (`ARCHITECTURE.md` v1.32, §56 entry). **§26's open question is
> answered in that amendment: a node-issued read costs NO hop**, because
> §3.7's budget counts `rag_lookup_*` and `load_evidence_series` is not one.

### The four candidates, and what each costs

| | Transport | What it changes | What it costs |
|---|---|---|---|
| **A** | The plan joins the injected block — `BeforeModelStateInjection` composes `focus_field` and `next_action` into the block it already prepends every turn | one composition point, already at the top of the prompt, already measured (§19.1) | **Lands inside G-24**, whose block composition and token budget the reference marks *"to be designed with founder"*. And it is still prose the model may rank below a tool it likes better — the failure mode layer 4 already demonstrates |
| **B** | The plan arrives as a message in the turn's `messages` — the executor appends the directive as a turn-level instruction | the model reads it as part of the conversation rather than as background facts, which is a stronger position than the block | a synthetic message enters the checkpointed transcript a Belt can be shown. §21's content-block rule applies to its construction |
| **C** | The node executes the routed call itself — `load_evidence_series` runs in `executor()` before the model does, and its result is put in front of the coach | **the planner's routing stops being advice.** Deterministic: the guarantee holds whatever the model prefers | a real §17 amendment. *"The executor consumes the plan and decides no strategy"* becomes *"the executor executes the plan's named call"*, and §26's hop accounting has to say whether a node-issued read costs a hop |
| **D** | Forced tool choice for the turn — bind `load_evidence_series` as required when the plan names it | the model cannot skip it | LangChain's forced-choice semantics bind **one model call**, not a turn, so a second call may drop it. **Unverified against the installed version — §16.3 applies before this is costed, not after** |

> **THE RULING IS THE FOUNDER'S AND THIS SECTION DOES NOT PRE-EMPT IT.** A and B
> keep §17 as written and leave the guarantee probabilistic. C makes it
> deterministic and amends §17. D is unverified. **What 6.18 established is that
> prompt wording is not a fix**: the instruction is not being outranked, it is
> not arriving.


> ### ✅ CLOSED 2026-09-15 — rid `20167cc9-ea86-4501-a827-0e19ebb2420a`
>
> | Evidence | |
> |---|---|
> | **The coach returned the source file's exact statistics** | mean **10.23%**, range **7.04–16.01%** — the computed values of `docs/_archive/SAMPLE_PROJECT/define_baseline_weekly.csv` |
> | Upload consumed | `executor: marked 1 upload(s) consumed` |
> | Hops | **0/5** — zero redundant searches, against three in the failure |
> | Duration | **~22s**, 19:11:45→19:12:07, inside `run_timeout=45` |
>
> **THE STATISTICS ARE THE LOAD-BEARING CLAUSE AND THE OTHERS ARE CORROBORATION.**
> A dispatch count, a `consumed_at` stamp and a hop count can all be produced by
> a read that failed — **G-63 is the proof, because every one of those looked
> right while `load_evidence_series` returned `no_such_column` and loaded
> nothing.** Values that match the file's own arithmetic cannot be produced
> that way. The data reached the model.
>
> **THE SPAN IS DELIBERATELY NOT CITED.** A LangSmith trace id is not offered
> and would add nothing: the span reports `status: "success"` on a read that
> loaded no data, which is **the open half of G-63's escape cause** and is step
> 8.0's to fix. Citing it would be citing the instrument this step's own defect
> proved unreliable. The request id is the anchor instead.
>
> **⛑ THE DONE-WHEN'S LAST CLAUSE IS NOT MET, AND IS NOT TREATED AS MET.** It
> required the live halves of 6.7, 6.12 and 6.13 *“run in the same pass”*.
> **TWO are genuinely owed and the third was never owed at all**: 6.12's clause
> could not be satisfied by any Define turn and is corrected and re-homed to
> Measure rather than carried. **Closing 6.21 against a false debt would have
> recorded a failure that never existed.**
> Closing 6.21 on its own evidence while silently absorbing three other steps'
> debts is precisely the shape this document exists to refuse.
>
> | Step | Its live half | Verdict |
> |---|---|---|
> | **6.7** | *“the Define and Measure opening turns that see-sawed both coach rather than cap”* | **STILL OWED.** The turn spent **0 of 5 hops**, so the coach never searched and the cap never engaged — zero hops exercises neither *coaching instead of capping* nor the cap itself. **And Measure's opening turn was not run at all**; this was a Define turn |
> | **6.12** | *“an upload resolves to that ask”* | **NOT A DEBT — THE CLAUSE WAS WRONG AND IS CORRECTED.** Define declares **0** ask shapes against Measure's **4** (AR-R2), so no Define turn could ever have satisfied it. Re-homed to Measure 2026-09-15; see 6.12's own correction block. **6.21 therefore inherited a FALSE DEBT**, and carried it from the moment this clause was written. The run did exercise the fifth clause — a tool consumed a bound upload without the coach retyping a figure |
> | **6.13** | *“a `live-run` confirms a Belt asking what the to-be process is now reaches the artefact”* | **STILL OWED.** 0/5 hops means **`rag_lookup_evidence` was never called**, so the evidence INDEX was not queried at all — the figures came from `load_evidence_series`, a direct blob read that bypasses it. The question asked was also not *“what the to-be process is”*. Its `azure-query` half is a separate method and was not run either |
>
> **What 6.21 itself proves is narrow and sufficient**: the planner's routed
> call is dispatched by the node, reaches the tool with a column the file has,
> and its result reaches the model. That is option C working, which is the
> whole of this step.

> **⛑ THE CASE THIS CLAUSE NAMED NO LONGER EXISTS. Repointed 2026-09-15.**
> It read `IMPR-2026-ED8`. **The store was reset to exactly one case that
> morning and that case is `IMPR-2026-0E5`**, so the clause instructed a run
> against a case that could not be opened — an unsatisfiable Done-when, which
> is worse than a demanding one because it fails for a reason that has nothing
> to do with the step.
>
> **ONLY THE FORWARD INSTRUCTIONS WERE REPOINTED.** Every `IMPR-2026-ED8` in
> 6.13's and 6.18's sections is a RECORD OF A TRACE THAT HAPPENED on that
> case, and those are untouched. Rewriting them would falsify the evidence the
> diagnosis rests on — the trace really did run on ED8, and a register that
> edits its own history to match the present is the drift this document exists
> to prevent.
>
> **`docs/_archive/SAMPLE_PROJECT/` is the data behind the new case**, and its
> dossier names `define_baseline_weekly.csv` as the file to upload first.


---

## Step 7.3 — The nine-step HITL gate

*Original lines 4149–4156.*

> **⚠ Done-when corrected 2026-09-07 — it named `IMPR-2026-E9D`, which cannot
> run it.** E9D is complete (`current_phase="complete"`), so `/ask` returns 409
> by design and no gate can be passed on it. **This is the exact trap WATCH 22
> flagged for "any later step whose Verify method is `live-run` or
> `azure-query`"**, sitting unfixed in the next stage's own step. Check the
> registry for a case in a coachable phase at run time rather than hard-coding
> one — `IMPR-2026-0CB` is in `define` today, and a reset case is the other
> option §17's sequence needs.

---

## Step 9.1 — The Azure batched reindex, case index only

*Original lines 4582–4592.*

> **⚠ NARROWED 2026-09-09 — the evidence half of this step moved to step 6.13.**
> This step used to carry `improve_evidence_index`'s `phase` and `uploaded_at`
> additions as well, on the assumption that they needed the expensive
> drop-and-rebuild and were therefore external and blocked. **That assumption
> was wrong**: adding a field to a live index is additive, needs no rebuild, and
> assigns `null` to existing documents (`DECISIONS.md` Part AQ3, verified
> against Microsoft Learn). The evidence index now gains all seven of its fields
> at **step 6.13**, in-repo and unblocked. **What remains here is the case index
> and the shared contextual-label re-ingest.** Leaving the old scope in place
> would have implied the evidence work was still external and still blocked,
> which this amendment makes false.

---

## Step 6.36 — The register's readers read either document

*Original lines 4688–4763.*



**No content moves in this step.** Every reader of §66's gap register and of
the `> **BUILT:**` markers learns to read **either** document — the procedure
first, `ARCHITECTURE.md` second — so that step 6.37 can move the content under
a guard that can still see what it is checking.

### The chicken and the egg, which is the whole reason for the phase

**Rule 8 of the commit-msg guard resolves a `Gap: G-nn` trailer against §66's
register, read from the git INDEX.** Step 6.37 stages an `ARCHITECTURE.md` with
§66 removed and a `REFACTORING_PROCEDURE.md` with §66 added. A rule 8 that
knows only `ARCHITECTURE.md` reads an empty register in that index, every
declared gap number fails to resolve, and the commit is refused.

**The guard blocks the edit that would teach it where to look.** `--no-verify`
is the obvious way out and is the wrong one: it is the escape hatch the guard's
whole design assumes is never taken for convenience, and taking it here would
move the register in the one commit no rule inspected.

So the readers are taught first, in a commit that moves nothing. This is the
ordering `_fact_owners.py` already used when the ownership registry moved:
teach the reader, then move the fact.

### The three readers, enumerated from the hooks and not guessed

§56's v1.57 entry set that precedent — *every generator in the repository was
enumerated from the hooks rather than guessed* — and it holds here.

| Reader | Parse | Source | Change |
|---|---|---|---|
| `commit-msg-refactor-guard.py` · rule 8 | `_GAP_ROW_RE` over §66's rows, tolerating `~~**G-52**~~` | the git **INDEX** | `_known_gaps()` — the **UNION** of both documents |
| `build_board.py` · `read_gaps` | `^\| \*\*G-nn\*\* \|`, strikethrough **excluded** | the working tree | preference — first definition of a G-number wins |
| `build_board.py` · `read_markers` | `^> \*\*BUILT:\*\* ` plus the heading it sits under | the working tree | preference — first definition of a § wins |

> ### ⛑ TWO READERS PREFER AND ONE UNIONS, AND THE ASYMMETRY IS DELIBERATE
>
> **A union everywhere would make a half-finished migration unverifiable.**
> Every gap would resolve from both halves and nothing would report that the
> move was incomplete — a stale row left behind in `ARCHITECTURE.md` could not
> be distinguished from the moved one.
>
> **Rule 8 is the exception because it asks a different question.** It asks
> *does this number exist at all*, and a gap registered in the document it has
> not been moved out of yet is still scheduled by something. Refusing that
> commit is the same deadlock one level down.
>
> **The two §66 parsers keep their own regexes.** The guard's tolerates a
> struck-through row because a closed gap is still a number that resolves;
> `build_board.py`'s excludes one because a closed gap must not render against
> a live defect. `_register_source.py` owns WHERE to look and in WHAT ORDER,
> never HOW to parse — centralising the parse would force one of the two to be
> wrong.

### Two readers the record named that are not readers

**`verify_built.py` does not read §66 or the markers.** It parses Appendix D
and Appendix F — both already in the procedure — through `appendix_d_steps()`
and `MATRIX_ROW_RE`. Its `ARCH` constant is assigned and **never used**, and
the docstring claiming *two probes open `ARCHITECTURE.md` by relative path* is
stale: no probe does.

**`drift-check.py` does not read the markers.** It reads the governed documents
named in `fact_owners.yaml` and checks per-symbol field counts and singleton
count nouns. It parses neither a marker nor a gap row.

**Both are recorded here rather than silently dropped**, because the next pass
that re-derives this list will otherwise re-add them from the same recollection.


---

## Step 6.37 — The repartition — the operational register moves to the procedure

*Original lines 4780–4846.*



**`ARCHITECTURE.md` keeps the architecture and nothing else** — design,
specification, reasoning. The gap register, the BUILT markers, the as-is → to-be
view per container and Appendix D's step register become **one operational
register in `REFACTORING_PROCEDURE.md`**, one row per architectural fact,
anchored to a § in the bible *and* a symbol in the tree.

**The invariant that makes it checkable**: every gap has a step or is
explicitly marked unscheduled; every step has a row; nothing exists in only one
place.

### What the 2026-09-18 audit found that this step must carry

Numbers measured at `1469d08`, not estimated.

| Finding | Number | What it means for the move |
|---|---|---|
| Markers in `ARCHITECTURE.md` | **70**, of which **69** match the reader's regex | the 70th is a prose-form `> **NOT BUILT, …**` at §39.1.11 that no reader has ever seen |
| Sections holding a marker | **70**, each holding exactly **one** | § adjacency is 1:1 and therefore recoverable — a moved row loses nothing provided it carries its § |
| Markers with no `closes:` field | **6** | §17, §39.1.11, §58.5, §63.6, §63.9, §69.7 — a move keyed on that field drops them |
| Gap rows in §66 | **88** rows, **86** numbers, G-01…G-86 with **no holes**; G-03 and G-42 are listed twice | the duplicates are deliberate cross-listings into §66.6 |
| Open gaps not visible to `build_board.py` | **13** struck rows | its regex excludes `~~`; the guard's does not — the two parsers range over different populations |
| Gaps closed in prose but not struck | **1** — G-19 | it renders on the board as a live gap; it is also why the header's *24 closed* and the row markup's *23* disagree |
| Open gaps with **no owning step** | **32** of 62, by the most generous reading | and the generous reading is wrong at least twice: G-80's *step 6.16* and G-81's *step 6.13* are the steps that BUILT the thing, not the steps that fix it |
| Open gaps rendering **nowhere** on the board | **G-80, G-81, G-82, G-86** among them | all four are registered in §66 and appear in no cell of the artefact the founder reads |

> ### ⛑ THE COLLAPSE IS RIGHT IN DIRECTION AND WRONG IN TWO PLACES — CORRECT BOTH BEFORE MOVING 69 MARKERS
>
> **(1) APPENDIX F IS NOT A THING THE REGISTER ABSORBS — IT IS THE REGISTER'S
> EXISTING SKELETON, AND IT IS ALREADY IN THIS DOCUMENT.** Ratified 2026-09-15,
> built at 6.31, it states of itself: *"THIS IS THE SINGLE LEADING DOCUMENT FOR
> BUILD STATUS"*, carries one row per Appendix D step, and is refereed by
> `verify_built.py`, which asserts `GROUP BY Step` as **set equality against
> Appendix D in both directions** and evaluates every `Evidence` anchor against
> the tree. Its header already declares the migration path: *"Rows may be ADDED
> for a claim a step makes beyond its own delivery — that is how the 69 `BUILT`
> markers migrate in."* **The work is to EXTEND it with `container`, the
> `to-be` / `as-is` split and a `gap` column — not to build something that
> absorbs it.** `ARCHITECTURE.md`'s own *Appendix F — The v2.2.16 registers* is
> a different, historical, explicitly unmaintained artefact and must not be
> confused with it.
>
> **(2) "ONE ROW PER FACT" CANNOT ALSO BE ONE ROW PER STEP, PER MARKER AND PER
> GAP — THE JOINS ARE MANY-TO-MANY IN BOTH DIRECTIONS.** Three populations, three
> keys: **75 steps**, **70 markers** keyed by §, **86 gaps** keyed by G-number.
> Measured: **§49's marker carries nine open gaps** and the board renders one of
> them (G-75); **13 open gaps attach to two or more markers**, one to five; **six
> markers close two steps each**. A flat table keyed on any one of the three
> loses the other two. **The row key must be the FACT, with step, marker-state
> and gap as attributes** — and Appendix F's `GROUP BY Step` invariant must then
> be restated as *every step has at least one row*, not set equality, or the
> extension breaks its own referee.
>
> **What the correction costs is visibility, and that is the point.** Under the
> invariant *every gap has a step or is explicitly marked unscheduled*, **32
> open gaps land as `unscheduled` on day one** — including G-82, which is on the
> founder's board. That converts an implicit backlog into a visible one, which
> is the register's whole argument for existing.


---

## Step 6.38 — The dual-read is removed — one register, one reader

*Original lines 4863–4883.*



**A permanent dual-read is two sources of truth, which is the condition the
repartition was performed to end.** Every reader collapses to
`REFACTORING_PROCEDURE.md`, `_register_source.py` is deleted, and
`test_register_dual_read.py` is replaced by the single-source assertions.

> **THE MATRIX ROW'S ANCHOR IS DELIBERATELY THE INVERSE OF THE USUAL ONE.**
> This step DELETES rather than builds, so presence proves *not yet done*:
> `repo:.claude/hooks/_register_source.py` passes while the scaffolding stands
> and **fails the moment the step lands**, which is what forces the row to be
> flipped to `✅` with `absent:`. An `absent:` anchor written today would be the
> unfailable class G-72 names.


---

## Step 6.41 — The symbol-anchor ratchet comes down (G-87)

*Original lines 4894–4930.*



**A bound that is raised whenever it is exceeded constrains regression and
nothing else.** `register facts carrying no symbol anchor` has moved **70 →
166** and will move again at 6.40, every rise legitimate and every rise
upward. **It cannot tell a register that is growing from one that is rotting**,
and the number reads as progress precisely because somebody keeps updating it.

### What this step owes, and what it must not do

**Anchors get attached to facts that can carry one.** A `> **BUILT:**` line
never had a symbol because its evidence was its prose; some of those facts name
a module, a class or a test in that prose and can be anchored mechanically.
**How many is the step's first measurement, not a number to promise here.**

> ### ⛑ LOWERING THE NUMBER IS NOT THE GOAL — MAKING IT ABLE TO FALL IS
>
> **The cheapest way to satisfy this step is the one that must not be taken**:
> deleting rows, or inventing anchors that resolve without proving anything.
> An anchor is evidence or it is decoration, and `matrix_anchors` evaluates
> every one against the tree — so a decorative anchor fails there, which is the
> structural reason this cannot be gamed quietly.
>
> **Some facts legitimately have no symbol and must say so.** A ratified
> design that is not built has nothing in the tree to point at. Those keep the
> em dash, and the step's real output is the SPLIT: how many are unanchored
> because nobody has done the work, against how many are unanchored because
> there is nothing yet to anchor to. **A single number conflates a backlog
> with a specification**, which is what G-87 records.


---

## Step 6.39 — The spec-entry population joins the register (assertion 5)

*Original lines 4942–4978.*



**The second of the two populations the register covers.** 6.37 moves the
**70** facts that carry a `> **BUILT:**` marker, all anchored in §1–§56. This
moves the **96** spec entries of Part XII, §57–§65 — the layer stating classes,
functions and interfaces *at the level the code could be rebuilt from*.

**The two layers barely overlap: only 4 of the 96 spec entries sit under a
section that also carries a marker.** Measured 2026-09-18 at `1469d08`.

### Why assertion 5 waits for this step, which is the condition rather than a preference

**Assertion 5 is *every gap row names a fact that exists, or says
`unscheduled`*.** It is deferred out of 6.37 and lands here because **it cannot
pass in between**:

> **26 open gaps reference only an `S-id` whose section carries no marker** —
> G-07, G-08, G-09, G-10, G-11, G-12, G-13, G-15, G-16, G-17, G-20, G-22, G-23,
> G-24, G-26, G-29, G-30, G-31, G-32, G-33, G-35, G-36, G-37, G-40 among them.
> After 6.37 the fact table holds the 70 marker facts and **not one of those 26
> can name a fact that exists**.

Enforcing assertion 5 at 6.37 would therefore force 26 gaps to `unscheduled`
**to satisfy a check rather than to state a truth** — and `unscheduled` would
stop meaning *nobody has scheduled this* and start meaning *the table does not
reach this yet*. **One word carrying two meanings is how a register stops being
read.** The condition is stated so the deferral is checkable and not a
preference: **assertion 5 turns on when the spec-entry rows exist, which is
this step.**


---

## Step 6.40 — Every section declares a row or declares itself not-markable (assertion 7)

*Original lines 4989–5029.*



**§66's header has always claimed the marker-to-row correspondence *"is
checkable"*. In one direction it is not, and this step is what makes it so.**

| Numbered sections in `ARCHITECTURE.md` | **285** |
|---|---|
| carrying a marker | **70** |
| declared `> **NOT-MARKABLE:`** | **17** |
| **carrying neither** | **198** — 185 of them sub-sections |

**Row→section and marker→row are checkable today and land at 6.37.** The
section→row direction has **no population to range over**: nothing distinguishes
the 198 from the 17, because the 17 are simply the ones somebody annotated.

> ### ⛑ WHY THIS IS ITS OWN STEP AND NOT A CLAUSE OF 6.37
>
> **A check written over all 285 sections reports 198 violations on its first
> run.** That is not a check, it is a backlog with an exit code, and it would be
> switched off within a week — the failure `section_title_sources` already
> records happening **twice** to the typed-title probe, and the reason the 31
> DONE steps below band A are excluded from the unbanded-step check by name.
>
> **The work is a judgement per section, not a row move.** Each of the 198 needs
> a decision: does this section make a buildable claim, or is it reading
> instructions, terminology, a topology overview, or an item marked at its
> canonical home? §16's own `NOT-MARKABLE` states the governing convention —
> *"One marker per item, never one per section that mentions it"* — and applying
> it 198 times is a document pass.
>
> **Bundled into 6.37 it would be unreviewable.** A red `verify_built` could not
> tell a bad judgement call from a mis-moved row, and 6.37 already moves 70
> markers, 17 declarations and the whole gap register.


---

## Step 6.35 — The hop cap matches the ceiling that was always in force (G-83)

*Original lines 5040–5092.*



**`COACH_HOP_BUDGET` goes 5 → 3.** The declared cap now matches the ceiling
that was always in force.

### Why five cost nothing to give up

§25's multi-query fusion makes one hop **a model call to generate variants,
then six searches, then RRF** — measured **~9.5s** on G-63's trace and
consistent with rid `ca6ba417`. A fifth hop lands near **47.5s** against the
executor's **40s** budget (6.34), so the turn died on the wall before the cap
could fire and `_HOP_BUDGET_SPENT` was **unreachable code**.

**Hops four and five could never be taken.** What changes is that the limit is
now REACHABLE: the coach receives `_HOP_BUDGET_SPENT` and composes, instead of
being cancelled mid-search and handed to 6.34's degraded path.

> ### ⛑ AN UNREACHABLE CAP IS UNFALSIFIABLE, AND THAT IS HOW FIVE SURVIVED
>
> Five was written at **6.7**, on top of a per-hop cost introduced at **5.2**
> that already excluded it. **No check compared the two**, and the existing cap
> tests could not: `test_executor.py` drives `COACH_HOP_BUDGET + 1` calls and
> asserts the last is refused, so it is **budget-RELATIVE and passes at any
> value**, including one no turn can reach. Those tests prove the MECHANISM.
> Nothing proved the NUMBER.
>
> **So the arithmetic is now a test.** `MEASURED_HOP_SECONDS = 9.5` and
> `HOP_BUDGET_COMPOSE_RESERVE = 10.0` sit beside the cap **with their
> provenance**, because a constant justified by a measurement nobody can find
> is a constant nobody can revise. `test_hop_cap.py` asserts a full-budget turn
> FITS, that **five would not**, and that **four would not either** — so the
> cap is the largest value that fits rather than a guess under it.

### The deferral, on a condition rather than as an open question

**Cutting per-hop cost is the other lever and it is DEFERRED TO STEP 9.0.**
Fusion runs six queries per hop; narrowing that would let more hops fit. It
waits for **9.0's knowledge-corpus ingest, which is the first moment recall can
be measured.**

**Cutting query breadth before there is a corpus to measure recall against
would trade an unmeasured quality for a measured latency** — the trade §52's
regression thresholds exist to prevent. **This is a scheduled condition, not an
open question**: when 9.0 lands, re-measure recall at six queries and at fewer,
and rule then.


---

## Step 6.34 — A node that runs out of time answers the Belt instead of failing (G-84)

*Original lines 5103–5187.*



**A slow turn reached the Belt as `500 Internal Server Error` carrying a stack
trace**, against §4.8's *never a hard failure to the Belt*. Observed on rid
`ca6ba417-3319-433d-8bfb-9240252dfc0a`: *"Node 'executor' exceeded its run
timeout of 45.000s (elapsed: 52.219s)"*.

### The options, and why the chosen one is not the obvious one

| | Approach | Cost | What it hides | Slow model day |
|---|---|---|---|---|
| **(a)** | Catch `NodeTimeoutError` **above** the node, in `core/graph.py`, the way `GraphRecursionError` is caught | small — one handler | **The turn's work.** The graph raised, so there is no child state: no `messages`, no `citations`, no `turn_count`, no `step_log`. The degraded answer is composed from the parent's view alone and the turn's retrieval is discarded | Survives, but degrades to a thinner answer each time and silently loses whatever the coach had gathered |
| **(b)** | **Budget the model loop INSIDE the node**, below the engine's wall, so the node's own paths run | small — one `wait_for` and one handler | Nothing. The node still holds `prior`, the dispatched read, and its hop count, and composes from them | **Survives, and degrades honestly.** The engine's wall goes back to being a backstop for a node that has stopped cooperating |
| **(c)** | Raise `EXECUTOR_RUN_TIMEOUT` | trivial | **Everything.** The 500 still happens, just later; §4.8 is still violated; and G-83 says a hop costs ~9.5s, so a larger wall moves the line without making the 5-hop cap reachable **or the failure visible** | **Fails.** A slow day is precisely when the new wall is crossed too, and there is still no graceful path |

> ### ✅ CHOSEN: (b), AND (c) IS DECLINED AS THE WHOLE FIX
>
> **(a) is the same shape as the defect.** The engine cancels the node from
> above its body; catching one frame further up is still above the body, and
> the thing that makes a degraded answer worth having — what the coach already
> retrieved — is gone by the time it is caught.
>
> **(b) puts the decision where the information is.** The node knows its hop
> count, holds its messages, and already composes a partial answer for two
> other failure modes. It is a third case of a pattern that exists.
>
> **THE WALL IS NOT RAISED IN THIS STEP.** 45s stands. Raising it trades
> Belt-facing latency for a failure that is now handled gracefully anyway, and
> **G-83 remains open**: a hop costs ~9.5s, three is the ceiling, and
> `COACH_HOP_BUDGET = 5` is still unreachable configuration. **That
> contradiction is not closed here and must not be read as closed** — whether
> to lower the cap to 3, cut per-hop cost, or raise the wall is a founder
> ruling about latency, not a bug fix.

### What was built

`EXECUTOR_SOFT_BUDGET = 40.0` in `nodes_common.py` wraps `agent.ainvoke` in
`asyncio.wait_for`. On expiry the node catches `asyncio.TimeoutError` **inside
its own body**, composes `_TIMEOUT_MESSAGE`, and returns normally — 200, a
partial and honest answer, and the engine's wall never reached.

**The five seconds of headroom are for composing, which makes no model call**:
marking uploads consumed, attaching a diagram, building the `step_log` entry.

**THE ORDER OF THE TWO NUMBERS IS THE WHOLE GUARANTEE**, and it is asserted at
import in `subgraph_common.py` rather than left as a convention. Invert them
and the fix silently stops working with no symptom until a slow turn 500s
again.

### Where the failure is recorded, and what reads it

`_executor_status` gains **`"partial_timeout"`**, ranked first so a turn that
also hit the cap is reported by the cause that actually ended it. It is written
to `step_log`, and `core/graph.py` turns every `step_log` entry into a
`history` key on `SupervisorState` — so a degraded turn is **checkpointed with
the turn**, not left in a log line nobody reads. **A degraded turn that leaves
no trace is the same error class this step closes**: the Belt got an answer, so
nothing else would notice the coach never finished.

### D7 — the escape, and a test that failed its own proof first

The escape cause was that **no test exercised a node that exceeds its wall,
because tests run fast**. `test_executor_timeout.py` injects the budget instead
of waiting for it: `EXECUTOR_SOFT_BUDGET` is read from the module global at
call time, so a test sets it to 10ms. **No `sleep(40)` anywhere** — a suite
that takes forty seconds to prove one branch is a suite people stop running,
which is the condition that let this through.

> **⛑ THE FIRST VERSION OF THE GUARD TEST PASSED ITS OWN MUTATION, AND THAT IS
> RECORDED RATHER THAN QUIETLY REWRITTEN.** It read
> `assert "asyncio.wait_for" in inspect.getsource(executor)`. Removing the
> guard left the phrase behind **in the comment explaining it**, so the test
> passed against an unguarded executor — **a check satisfied by prose ABOUT the
> mechanism rather than by the mechanism.** Same class as G-63's escape cause
> and G-76's grader test. It is now parsed with `ast`, which cannot read a
> comment, and asserts all three of: a `wait_for`, that it wraps
> `agent.ainvoke`, and that its timeout is the module's budget.


---

## Step 6.33 — The capture path accumulates — a field survives the next turn

*Original lines 5200–5343.*



> ### ⇒ EXTENDED 2026-09-21 — THE FIELD CHANGE LOG, SAME COMMIT
>
> **The step as ruled fixes the accumulator. The extension records its
> history.** Founder ruling: `PhaseState` gains **`field_log`** — one entry per
> change, carrying field, new value, prior value, turn, timestamp and the
> Belt's stated reason where given; the first capture of a field is an entry
> too, with no prior value. **Append-only BY DECLARATION** — the channel
> carries a reducer, proven by mutation — and **keyed by turn and field**, so a
> re-run of the same turn replaces its own entry rather than logging the change
> twice.
>
> **The `Touches` row above grew with it**, and the growth is the amendment's,
> not the step's: a new `PhaseState` field is a §56 amendment (CLAUDE.md
> *Amending the rules*, 3b), so `core/substate.py` carries the field and its
> reducer, `phases/nodes_common.py` writes the entries, `core/graph.py` and
> `core/conversation.py` carry them out on the turn's transport — the subgraph's
> state reaches the route no other way — and `storage/models.py` gives them a
> home beside the values they are a log of. **ARCHITECTURE.md v1.68 is the
> ruling; this row is its consequence.**
>
> **Out of scope and stated so**: the gate write, the UI, and `phase_metrics`.

**Every coached capture destroys the ones before it.** Two defects at opposite
ends of a path that otherwise works (G-78), found by the first live turn:

1. **The input mapper blanks the accumulator every turn.**
   `mappers_common.py:252-253` seeds `"draft": {}` **and** `"artifacts": {}`,
   so `artifacts` — documented at `nodes_common.py:1275` as *"the
   accumulation"* — accumulates within a single turn and is reset on the next.
   `artifacts` and `draft` are consequently always identical.
2. **The write replaces instead of merging.** `routes.py:661-665` builds
   `clean` from THIS turn's extraction and assigns
   `case.phases[phase].structured = clean`.

> ### ⛑ THIS IS THE DEFECT 6.11 FIXED ONE FIELD OVER
>
> The comment directly beneath those two mapper lines records that `uploads`
> was blanked *"from 3.1 to 6.11"* and that this *"was the entire reason
> `PhaseState.uploads` had no writer"*. **6.11 seeded `uploads` and left
> `draft` and `artifacts` blanked.** The fix is known because it has been
> applied here before, to the field beside these two.

### Why it is its own step and not a widening of 6.20

**6.20 does not touch `routes.py`**, where half the defect lives, and 6.20 is
in flight — widening a moving step adds scope to something already moving.
6.20 owns `computation_results`, `phase_metrics` and `field_index`; **this owns
the capture path 6.2 built and S-F04 B4 ratified**, which is supposed to work
today. Adjacent, not the same.

### Why it runs AHEAD of 10.0

**A Belt fills 26 fields across many turns.** While each capture wipes the
last, the gate document can never accumulate, `gate_attempts` has nothing to
count and **§33's gate is unreachable** — so 7.3 is blocked behind this, and
rendering the turn better (10.0) renders a document that is still being
emptied. Order: **6.20 → 6.33 → 10.0 → 7.3 → 10.2**.

> **6.33 LEFT THE VERTICAL ON 2026-09-21 AND THE REST CLOSED UP** — Appendix
> F's `Order` runs 6.20 → 10.0 → 7.3 → 10.2 as 1–4. **The sequence above is
> unchanged**; only the labels moved, because `Order` must be a contiguous run
> (`test_the_order_column_is_a_sequence_with_no_duplicates`). **What runs next
> is the founder's column and was not re-decided here.**

### The trap in the evidence, and it is why the log is not enough

**The log counts KEYS and the filter drops on VALUES.**
`nodes_common.py:1269` logs `len(captured)`; `clean` discards entries whose
value is `None`, `[]` or `{}`. So *"captured 1 field(s) -> artifacts"* and
*"nothing reached the gate document"* are **both true of the same turn**, which
is exactly what the 2026-09-15 run produced — and the reason it produced the
BENIGN branch: `clean` came out empty, `if clean` skipped the write, and the
two creation-form fields survived. **Had the capture carried a real value they
would have been destroyed.** A fix that makes the write succeed without fixing
the merge turns a silent no-op into silent data loss.


**And for the ratified extension, in the same commit:** `field_log` carries one
entry per change with field, new value, prior value, turn, timestamp and the
Belt's stated reason where given; the first capture of a field is an entry with
no prior value; the channel is **append-only by declaration** and the reducer is
proven by mutation — removed, the test goes red; entries are **keyed by turn and
field**, proven by resuming a turn and asserting one entry; and the `live-run`
changes one field across two turns with **both values present, each with its
date**.

> ### ✅ CLOSED 2026-09-21 — `live-run` on `IMPR-2026-0E5`, two turns
>
> | Evidence | |
> |---|---|
> | **One field changed across two turns, both values kept** | `business_case` captured at **13:42:01Z** as *"…about GBP 180,000 a year…"*, revised at **13:43:39Z** to *"…GBP 245,000 annually…"* — the second entry carrying the first as its `prior_value` |
> | **The accumulator survived the turn boundary** | `baseline_estimate`, captured in an earlier session, was still in `structured` after both turns. **It is the load-bearing half**: it is the value the old assignment destroyed, and it was not written by either turn |
> | The turn's own reconciliation | `captured 1 -> 1 field(s) into artifacts (0 empty, 1 changed)` — the log line whose count used to disagree with the write |
> | Request ids | `5415c73d-6b80-426a-b5f4-7daabef1ec4b` (capture) · the revision one turn later |
>
> **THE SURVIVING PRIOR FIELD IS THE CLAUSE THAT CANNOT BE FAKED.** A capture
> appearing in `structured` proves only that the write ran; it looked exactly
> like this before the fix, because a single turn's assignment also produces a
> populated `structured`. **A field the run never touched, still present after
> two turns that both wrote, can only come from a merge.**
>
> **`reason` IS `None` ON BOTH ENTRIES, AND THAT IS THE PREDICTED RESULT, NOT A
> FAILURE — REGISTERED AS G-89.** *"The Belt's stated reason where given"* is read from a `reason`
> key on the capture entry, which `CoachingResponse.fields_captured` permits
> because its entries are free-form dicts — and **nothing asks the coach to
> supply one**: S-C05's field description names `field_name`, `value` and
> `source`. The Belt's second message stated a reason in prose (*"the earlier
> figure left out the late-payment penalties"*) and it reached the coaching
> text, not the log. **The column will be empty in live use until a §56
> amendment to S-C05 asks for it**, and that is carried as G-89 rather than as
> a closed clause; the procedure amendment now being drafted owns the fix. It is proven only by a unit test that supplies one.
>
> **WHAT THE RUN DOES NOT PROVE.** The gate document was not assembled — this
> step does not touch the gate write, by ruling — so *"both surviving into the
> gate document"* is proven at `PhaseRecord.structured`, which is what gate
> assembly reads, and **not by a rendered gate document**. The five-turn clause
> is proven by `pytest`, not live: the live run is two turns.
>
> **A METHOD DEFECT, RECORDED BECAUSE IT NEARLY BECAME EVIDENCE — G-90.** Two reads
> during this run parsed a **404** and a **400** body as though they were data —
> `{"detail":"Not Found"}` has no `phases` key, so the first read reported
> *"structured: null"* and looked exactly like a case that had captured
> nothing. **This is G-66 in the verifier rather than in the UI**, and it was
> caught only by adding `-w "%{http_code}"`. Every live read in this document's
> future steps checks the status before it reads the body.


---

## Step 6.42 — The gate document records what Define established

*Original lines 5347–5406.*



**The gate document is assembled from a key nothing sets.** `routes.py:1375`
reads `validated = phase_data.get("_validated", {})` and hands the result to
`write_phase_gate` as the phase's `structured` record. **`validate_define` never
writes that key**, so the expression resolves to `{}` and the document is
written EMPTY — and the code's own comment has said so since step 4.2, carried
as a WATCH because the gate could not pass and repairing v1 code that 11.1
deletes was the wrong place to spend a structural step.

**6.33 is what makes it reachable.** While every capture destroyed the one
before it the gate could never accumulate enough to pass, so the empty write
was unreachable and correctly deferred. The capture path now accumulates; the
write is next on the path, and it is the last thing between a completed Define
and a recorded one.

> ### ⛑ AN EMPTY DOCUMENT AND A REFUSAL ARE NOT THE SAME OUTCOME
>
> The defect is not only that the document is empty. It is that **the phase
> ADVANCES anyway** — `write_phase_gate` succeeds, `next_phase` is returned and
> the Belt is moved to Measure, with the gate marked passed and nothing behind
> it. Measure's input mapper then composes its framing from a gate document
> with no fields, and `compose_phase_context` renders twelve *"not captured in
> define"* lines as though the Belt had skipped the phase.
>
> **So the fix is a REFUSAL, not a default.** Assembly that cannot produce a
> complete document must raise rather than write a partial one, which makes
> advancing to Measure with no record **impossible by construction** rather
> than merely unlikely. That is S-C06's failure-mode rule applied one level up:
> a missing prior gate document is an ordering fault, and a caller that papers
> over it hides a broken transition.

> ### ⛔ SOURCE-VERIFIED CONSTRAINT — re-fetched 2026-09-23
>
> `docs.langchain.com/oss/python/langgraph/interrupts`, verbatim:
>
> > *"When execution resumes … **the runtime restarts the entire node from the
> > beginning** — it does not resume from the exact line where `interrupt()`
> > was called."*
> >
> > *"**Do not perform non-idempotent operations before `interrupt()`**"* — and
> > specifically, do not create records without checking whether they exist,
> > because *"this will create duplicate records on each resume."*
>
> **This is why the write must be idempotent, and it is a documented property
> of the framework rather than a defensive habit.** The write lands in the
> route today and moves into a node at 7.3; **a node write is re-executed on
> every resume**, so a `write_phase_gate` that stamps a fresh `submitted_at`
> and replaces the record produces a different record each time the Belt
> resumes.


---

## Step 6.46 — The coaching script is guaranteed to reach the model, or its absence is recorded

*Original lines 5557–5596.*



**A turn coached without the script is indistinguishable from one coached with
it.** `DMAICSkillsMiddleware` (§19.2) discloses the phase's SKILL.md
progressively; whether the disclosure actually landed in the request is not
recorded anywhere, so a turn whose script never loaded produces a plausible
coaching answer and no trace of what was missing.

**This is the shape G-49 had and the class §55.2 exists for**: a mechanism that
is specified, built, and unobservable. The remedy is not a guarantee that
loading never fails — it is that **failing leaves a mark**, on the same
argument §56 amendment v1.64 used for the four presentational fields: making a
thing optional without recording its absence trades a loud failure for a silent
one, which is the worse of the two.

> ### ⇒ ADDED 2026-09-23 — THE §22 GUARD BECOMES LOAD-BEARING HERE
>
> **Once the script reaches the model every turn, its WORKED EXAMPLES do too.**
> §43.2 requires a field to be shown with an example before it is asked, and
> every one of those examples is a plausible, well-formed value for the field
> being coached — *"Between Jan–June 2026, 12% of invoices had pricing
> errors…"* is exactly what a `problem_statement` looks like.
>
> **§22's guard — an example is NEVER captured as the Belt's data — is
> dormant today because the examples do not arrive.** This step is what makes
> them arrive, so it is the step that owns the guard. Shipping the script
> without it would hand the coach a page of realistic values and no rule
> against recording them, and the resulting gate document would be
> well-formed, complete, and not the Belt's project.
>
> **Seven capability rows wait on this step** — rows 26 to 32 are §43.1 to
> §43.7, one per rule, all owned here. That is why it is not a logging step.


---

## Step 6.48 — A captured value carries its declared type

*Original lines 5634–5686.*



**Four of Define's thirteen gate-required fields are declared structured and
captured as prose.** Measured on `IMPR-2026-0E5`, 2026-09-23, after thirteen
live turns took the case to a complete capture set:

| Field | Declared | Captured |
|---|---|---|
| `team` | `list[dict]` — `{name, role, function}` (§39.1.4) | `str` |
| `process_map_sipoc` | `dict`, six keys (§41) | `str` |
| `project_scope` | `dict` — `{in_scope, out_scope}` (§39.1.2) | `str` |
| `metric_definitions` | `list[dict]` — `{name, unit, meaning}` (§63.8) | `str` |

**Pydantic rejects all four at assembly**: *"3 validation errors for
`DefineOutput` … Input should be a valid list … Input should be a valid
dictionary."* So a Belt who has answered every question cannot produce a gate
document, and **`GET /gate/review` returns a 500 on a complete case**.

> ### ⛑ THE TYPE CONTRACT IS DECLARED AT THE GATE AND ENFORCED NOWHERE ELSE
>
> `CoachingResponse.fields_captured` types `value` as **`Any`**, deliberately
> and correctly — S-C05 says so, because the field must carry both §7's strings
> and the cross-phase reference dicts. `nodes_common._captured_fields` then
> takes `entry.get("value")` verbatim: *"`value` stays whatever the model sent
> — `Any`, deliberately (§20)."*
>
> **So the shape a field must have is stated in the `{Phase}Output` schema and
> checked for the first time at assembly** — which, until 2026-09-23, had never
> run on real data. §7's law is *"all captured fields are `str`, with the
> enumerated exceptions"*, and **nothing on the capture path knows which fields
> are the exceptions.**
>
> **This is the class step 6.50 exists to catch and the reason it is not
> cosmetic**: every checker in this repository compares the tree to a document
> this project wrote, and every one of them passed while this was true.

**Not a prompt fix.** Asking the coach more firmly for a dict is the shape
§56's own record warns against — *"prompt wording is not a fix: the instruction
is not being outranked, it is not arriving."* The capture path has to know the
declared shape and either produce it or **report that it could not**, on the
same argument step 6.33 applied to an empty capture: the log and the write may
not disagree about what was stored.


---

## Step 6.49 — The checks card — twelve capability rows get the check that proves them

*Original lines 5695–5737.*



**Checks only. No code changes.** A row without a check is a claim, and a
register of claims is what Appendix H exists to replace. **This card does not
fix what the checks find** — clause 5 decides whether a finding becomes a step,
and a check that goes red is the input to that decision rather than a licence
to start work.

> ### ⇒ ROWS 33 AND 35 ARE IN THIS CARD DELIBERATELY
>
> | Row | Why it cannot wait |
> |---|---|
> | **33** — a checkpoint is written after every node of a Define turn | **7.3 cannot pause without a checkpointer that writes, and nobody has confirmed ours does.** `test_turn_graph.py` pins the PATHS a fake saver would write; it says nothing about the Azure one. §16 puts the checkpointer on the parent and `test_checkpointer.py` is its subject, but *"after every node"* has never been counted |
> | **35** — every Define turn leaves a LangSmith trace, with the model call, the tools and the middleware visible | §51 makes tracing the answer to *"what did the coach actually do"*, and G-63 is the standing proof that a span can report `status: "success"` on a read that loaded nothing. **A trace nobody has looked at is not observability** |
>
> **Both are about whether the machinery underneath the pause works.** Finding
> out at 7.3 that the checkpointer writes once per turn rather than once per
> node would be finding out while building the thing that depends on it.

> ### ✅ UNBLOCKED 2026-09-23 — the seed has landed, and the card is startable
>
> **The card was registered blocked**: ten of its twelve rows were among the
> twenty Appendix H had not yet written, and **a check cannot be written
> against a row whose capability nobody has stated** — writing one anyway
> would have meant choosing what the row requires and then checking my own
> answer. **The founder's seed states all ten**, so every row this card checks
> now has its capability in the founder's words, and the check is written
> against that sentence rather than against a reading of it.
>
> **Four of the twelve are built already and red anyway** — rows 5 and 6 at
> 6.33, rows 10 and 11 at 6.20. Their `Given by` reads *built at X · proven by
> 6.49*: the mechanism exists, and this card is what turns *"exists"* into
> *"proven on the product"*.


---

## Step 6.52 — A turn always answers inside its budget

*Original lines 5798–5865.*



**Admission (clause 5): row 2 is red, and it blocks every live-turn check
still to come.** Both live turns on `IMPR-2026-0E5` on 2026-09-24 hit the
executor's 45 s wall and reached the Belt as a 500.

| Trace | Where the 45 s went |
|---|---|
| `01a0d215-a216-75e2-ba80-1c80597f891f` | The grader failed the reply twice and was re-judging **the same text** (three inputs, 2,642 characters each, zero differing lines) |
| `01a0d28e-d4da-7901-a75e-44d86b102098` | Three knowledge lookups in a row, ~32 s; each held the event loop |

> ### ⇒ PART A FOUND TWO REASONS THE SOFT BUDGET NEVER FIRED (G-92)
>
> 1. **Its clock started late.** `asyncio.wait_for` wrapped only
>    `agent.ainvoke`; the engine's wall starts at node entry. 5.5 s and 4.9 s
>    had gone before the budget began, so the soft deadline fell AFTER the
>    wall (trace 01a0d215…: soft at 54.7 s, wall at 54.2 s).
> 2. **The lookups blocked the event loop.** Each `rag_lookup_*` is `async`
>    but ran synchronous `embed_query` + `search`, once per query, four to six
>    queries in a row. No timer can fire on a blocked loop: on trace
>    01a0d28e… the wall surfaced 0.1 s after `rag_lookup_case_history`
>    returned.
>
> **Escape:** `test_executor_timeout.py` proved the budget by
> re-implementing `wait_for` inside the test around an agent that awaited a
> millisecond sleep — never the real node, never the real wall, never a
> blocking tool.

### B1 — the soft budget holds

1. The soft deadline is anchored at executor-node **ENTRY**: what remains of
   `EXECUTOR_SOFT_BUDGET` since entry is what `wait_for` gets. The import-time
   assertion that soft < wall stays.
2. The lookups stop blocking the loop: each query's synchronous search runs in
   `asyncio.to_thread`, and a lookup's four to six queries run together under
   `asyncio.gather`. **Not in this step:** the aio `SearchClient` and async
   embeddings — follow-up work that needs its own step number.
3. Tests on the REAL executor node under the REAL `TimeoutPolicy`, with a
   setup delay and a tool that BLOCKS (`time.sleep`); a watchdog that no
   lookup holds the loop > 100 ms; a mutation proof per fix. The
   re-implementation in `test_executor_timeout.py` is retired.
4. Appendix F's 6.34 anchor moves from the constant to the new check.
5. Live: one open-question turn on `0E5` (two or more lookups) returns 200 in
   under 45 s; its trace id goes into Appendix H row 2.

### B2 — a judge judges each distinct reply once

1. **Grader:** one grading per distinct reply text. On FAIL, pass through with
   the Belt-visible warning (§19.8's end state). The verdict is written to
   `step_log` with `layer: "coaching_grader"`.
2. **Coherence:** one check per distinct reply. On reject, degrade and skip the
   grader, as today, without re-checking identical text.
3. Tests: each judge is called once per distinct text; a FAIL verdict is in
   `step_log`; any middleware retry changes its input or makes one call. Row
   13's strict-xfail marker comes off; row 12 stays xfail.

**Not this step — 6.53:** regeneration on a FAIL (`jump_to="model"`), gated on
the latency ruling for G-83. Until then a judge's iterations are one.


---

## Step 6.54 — The clients are built once, at startup, before any Belt waits for them

*Original lines 5876–5905.*



**The cause, measured (G-93).** The clients a Define turn uses were built lazily,
inside the first turn, and six lookup threads missing an empty `lru_cache`
together each built their own. Step 0 of this card measured one build apart:

| Build | Cost | Of which |
|---|---|---|
| Embeddings client | ~2.5 s | 2 TLS certificate-bundle loads, 1.72 s — construction; no login (API key) |
| Knowledge vectorstore (embeddings cached) | ~3.5 s | 4 certificate-bundle loads, 1.76 s, plus the index-definition read (network) |
| Six threads on an empty cache | **7.2 s each** | 24 certificate loads, 38.3 s summed |

Case and evidence searches also built a new `SearchClient` per call — 7–12 per
lookup, each with its own certificates to load.

**The fix.** Every client a turn uses is built in the app's startup, before it
accepts a request (`warm_turn_llms`, `retriever.warm_clients`), and the search
clients are closed on shutdown beside the blob client. Each cached builder is
single-flight: however many threads miss an empty cache, one builds. One
`SearchClient` per index for the process.


---

## Step 6.57 — The Belt's step is computed, not counted by the model

*Original lines 5955–5992.*



**Every coaching turn on `0E5` wrote `"Define · 13 of 13"`.** Define's coached
walk has twelve positions (§39.1.2); thirteen is the GATE's list — the twelve
plus `metric_definitions`, captured inside position 5 (§39.1.9). The only count
the coach was ever given was the gate block's *"STILL MISSING … (n of 13)"*, so
it counted that.

**Delivery alone did not hold — measured.** With the computed step at the very
top of the model's input (trace `01a0d3f3-6f67-7100-b04d-214e7fe1f720`, first turn in process: yes) the
model still wrote *"13 of 13"*: its own earlier structured replies put `of 13`
into that input **55 times**. So the count is COMPUTED, DELIVERED and WRITTEN:
the executor sets the reply's `progress` from the same function and re-renders
the stored structured-response message the next turn reads; what the model
wrote itself is kept in `step_log`. **The written step is the position AFTER
the turn's capture, on every turn (v1.74)** — computed before it, the label
lagged one step on every capture turn (dry run 2, `IMPR-2026-134`, turn 2).

| Reader | Uses |
|---|---|
| The coach's prompt, every model call | `define_progress` — *WHERE THE BELT IS*, above the gate list |
| The reply's `progress`, and the stored message | `define_progress` — written by the executor |
| `step_log`, node `define_position` | `define_progress` — plus `reply_progress` (the model's own) and `reply_matches` |
| `field_index` | `define_position − 1` |
| **Step 10.3's progress bar** | **MUST call the same function** — never count again |

**The gate list stays separate and says so:** *"THE GATE LIST — STILL MISSING
FOR THE DEFINE GATE (n of 13 gate fields; not the step count)"*.


---

## Step 6.63 — The control board is a true picture of the tree

*Original lines 6002–6047.*



**Founder rulings, 2026-09-25, verbatim:** *"The only progress view is the
repo's generated control-board.html. The published 'Control Board' artifact on
claude.ai is retired."* · *"Every number, label, diagram element and status
colour on the board is derived from the tree, never typed by hand."* ·
*"Headline: 'N of 35 capabilities proven · working on: <step name>'."*

**8D — why the board showed four disagreeing progress views, and why 6.56 was
absent (Claude Code, 2026-09-25):**

> D2 IS: four views disagreed — the published "Control Board" artifact (50 / 95,
> "NEXT: 1 Restore tracing", 14 of 35, hand-edited ◆ items, refreshed by hand
> 24 Sep from a OneDrive copy); the repo's board.html and control-board.html
> (55 / 98, then 55 / 99; 15 of 35); a typed caption inside control-board.html
> ("47 of 90 · 22 Sep 2026", `system_view.py`); CONTINUITY.md (55 of 99, a
> hand-typed 15 of 35, and "no row carries an Order number").
> D2 IS-NOT: the repo's generators disagree at no single commit (d624ff4,
> ea94caa, e95df13, 34e8032 checked); no count was wrong for its moment.
> D4 OCCURRENCE: (1) the page read was a hand-refreshed copy nothing
> republishes; (2) the denominator moves with every registration (95 → 99);
> (3) statuses typed rather than derived — the "47 of 90" caption, the task
> statuses in `stories.py` (6.54 and 6.46 "todo" after both landed),
> CONTINUITY's capability line; (4) 6.56 was ruled 24 Sep and registered 25 Sep;
> (5) the Order-column regex in `build_board.py` and `continuity_status.py`
> ignored the Zone cell and returned an empty plan.
> D4 ESCAPE: nothing compared two views, or a published copy against HEAD;
> `read_order` had no test against the real document and its empty result
> rendered as a legitimate sentence; nothing flagged a ruled step left
> unregistered or a typed status git log contradicted.
> D5: one function behind every progress number; statuses derived from named
> references; the Order regex fixed; the published copy retired.
> D7 PREVENT (owned by this step): a check fails the commit if any status on
> the board has no reference or its reference disagrees with the tree; the
> plan refuses an unregistered step, a missing estimate and a precondition
> naming no step; `read_order` is tested against the real Appendix F.


---

## Step 6.65 — Speed without losing quality

*Original lines 6086–6111.*



**Founder ruling 2026-09-25 — speed without losing quality; binds all future
prompts.** Keep every check; remove only repeats and waste. The rules are
CLAUDE.md §22: (a) the full suite runs once per commit, in one hook, in
parallel where results are identical; (b) the two binding documents are
searched, never read whole; (c) an 8D only for a real defect; (d) 3 live runs
per situation while building, 5 only in a final proof; (e) stop only when the
Belt's experience changes or a founder decision is needed; (f) a report is one
table plus decisions; (g) one timing log, one record per prompt.

**Built:** `.claude/hooks/timing.py` and `.claude/logs/timing.jsonl` (the
existing, gitignored hook-log area — appending never dirties the tree); the
guard's rules, the pre-commit writers and the test recorder time themselves;
rule 4 runs `-n auto` (pytest-xdist, pinned); the recorder and the G-95
tracing guard hold under xdist.


---

## Step 6.64 — The board's grouped views are restored, derived

*Original lines 6119–6167.*



**Founder feedback on 6.63, 2026-09-25:** *"the container view and the
epic/story/task plan were removed. The ruling was 'derived, not typed' — never
'remove the grouping'. Restore every view, derived from the tree."*

**What it builds:**

1. **The waterfall's grouping is a switch**, default *Container*. *Container*
   groups every registered step under the part of the system it changes;
   *Work package* is WP0–WP6 as 6.63 drew it; *Epic / story* is `stories.py`'s
   epic → story → task tree, every status derived.
2. **Container cards**: what is there (read from the code) and the open steps
   (from Appendix F), each with its derived colour and reference.
3. **Capabilities grouped by container**, through each row's owning steps.
4. **`test-results.json` is not rewritten when nothing changed**, and records
   the commit its results were run against.

**The container is the step's Appendix F `Layer`** (L0–L8), named by the
table's own `#### L<n> · <name>` headings. Appendix F's `Zone` cell reads `—`
on every step's own row (it is populated only on the rows that migrated a
marker in), so it cannot group the steps; the `Layer` is *"which part of the
system the step changes"* per the column table, and every step has one.

**8D (Claude Code, 2026-09-25):**

> D2 IS: 6.63's board shows the waterfall by work package only; the
> per-container view (what is there, open steps) and the epic → story → task
> plan are gone. IS-NOT: no number is wrong — every status on the page is still
> derived and checked.
> D4 OCCURRENCE: 6.63 deleted `system_view.py` because its content was TYPED,
> and the grouping went with the content — the ruling was read as removing
> the typed views rather than deriving them.
> D4 ESCAPE: rule 10 checks that every status on the page is TRUE, never that
> a view is PRESENT; a page that drops a grouping passes it.
> D5: the three groupings, derived; a check that the container view carries
> every registered step, under the container the tree gives it.
> D7: `check_board.py` refuses a container view that omits a registered step
> and `progress.validate` refuses a step with no container — both tested.


---

## Step 6.61 — The coaching move is decided in code

*Original lines 6180–6226.*



**The ruling, verbatim:** *"The coaching move is decided in code, never by the model. For every field in every phase and every agent, code determines this turn's move from the field's status: not yet taught -> teach (explain, show, ask); answered, judged insufficient -> challenge (say what is missing); answered, judged sufficient -> read back (the Belt's own words, then ask 'is this right?'); confirmed by the Belt -> store and advance. An LLM is used only to judge whether an answer is sufficient, and to write the coach's words. A value is stored only after the Belt confirms it, in the Belt's words; a tidied version may be proposed in the read-back and is stored only if the Belt confirms it. The coach's input is assembled by code each turn in labelled sections, each with one job: coaching rules (how to behave), phase script (what to teach), state (facts), this turn's move (authoritative), last turn's quality feedback, and the conversation. The rules and scripts contain no move-sequencing instructions. Feedback to the coach is never presented as a message from the Belt. Basis: Anthropic, 'Effective context engineering for AI agents' (distinct sections, high-signal context, no brittle logic in prompts) and 'Building effective agents' (workflows for well-defined tasks; evaluator-optimizer)."*

**Scope: ALL phases and ALL agents.** This step builds it for Define; the other
four phase scripts' move-sequencing text is **6.62**; the platform reference
(`AgentLean/AGENTIC_ARCHITECTURE_REFERENCE.md`) owes the back-port — recorded,
not made. **6.45 reads this step's field status** for its completeness predicate
(confirmed = complete). **The capture contract moves under the ruling here**:
`CAPTURE_CONTRACT`, S-C05's `fields_captured`, and the Define script's
*"Capture each confirmed value"* (SKILL.md:163).

**8D (Desktop), verbatim:**

> D0 Reproduced: Audit 3 (IMPR-2026-4E5), 10.0 proof (IMPR-2026-8D4).
> D1 Founder, Desktop, Claude Code.
> D2 IS: the coach sometimes waits after a read-back, sometimes moves on,
>    occasionally re-asks a field; stores its own paraphrase, not the Belt's
>    words, before the Belt confirms; does not challenge weak answers.
>    IS NOT: a storage fault (answers are stored); not a timing fault
>    (recomputing the instructions changed nothing, 0/9). Blast radius: every
>    phase and every agent built on this pattern.
> D3 None exists.
> D4 Occurrence: the move is decided nowhere reliable — the script says
>    "confirm and advance", the rules say "one move, then stop", the
>    planner's decision never reaches the coach. Escape: each part was
>    specified and tested alone; nothing measured the coach's behaviour
>    across repeated runs until the audits.
> D5 Code decides the move from field status; an LLM judges only "sufficient?";
>    every layer of the coach's input has one job.
> D6 Same turn, 5 runs, same move, per situation; the Belt's words preserved;
>    audit recorder attached, tracing off.
> D7 The ruling binds all phases and agents; every step touching coaching
>    behaviour carries a repeated-run consistency test in its Done-when.
>    Owner: 6.61.
> D8 Closed when the consistency test passes for every Define situation and
>    the rules and all five phase scripts carry no move-sequencing text.


---

## Step 10.0 — The coaching turn’s output reaches the Belt — four blocks and the grader’s warning

*Original lines 6484–6561.*



**The coach produces `explanation`, `example`, `prompt` and `progress` on every
turn and the API throws all four away.** `AskResponse` does not declare them,
and `routes.py` builds `answer=(reply.content if …)` and nothing else — so
§50.1's render contract, the one that section calls *"schema-backed, not
prompt-hoped"*, is prompt-hoped at the only boundary that matters. The Belt
reads one prose blob.

> ### ⛑ THIS IS THE FIRST STEP THAT NAMES `ui/index.html`
>
> **7,273 lines of Belt-facing product that no step builds and nothing
> verifies** — G-71. This step does not close that gap; it puts the first row
> against the file, which is what lets the next one be written.

> ### ⇒ WIDENED 2026-09-15, AFTER THE FIRST LIVE TURN
>
> **Scope was “the four fields”. It is now THE RESPONSE TRANSPORT**, on the
> founder's ruling, and it grew by exactly what shares this step's seam — not
> by everything the live turn found.
>
> **ADDED — `grader_warning` (G-76).** The grader fails a turn three times,
> logs *“passing the turn through with a Belt-visible warning”*, and returns a
> key **declared on no schema and read nowhere**. It is G-69's shape with no
> seam at all: the same schema edit, the same `routes.py` projection, the same
> UI pass. **Leaving it out would mean opening this seam twice.**
>
> **ADDED — the UI rebuilds render state from `conversation_history` (G-79).**
> `S.lastAsk` and `renderLiveViz()` are each called from one place inside
> `sendMessage`, so a visual the server has stored dies on a tab switch. This
> step already says the UI draws from the response; it must also draw from
> what the response was LAST time.
>
> **NOT ADDED — the capture path (G-78).** It is not transport: nothing is
> lost between the graph and the response. It is a state and persistence
> defect two layers down — a mapper that blanks an accumulator and a write
> that replaces instead of merging. **Folding a data-loss fix behind a
> rendering change would hide it in a step nobody would look in.** It has its
> own step and it runs BEFORE this one.

### Why this is a step and not a bug fix

**6.19 is landed and STAYS landed.** It did what it said: it added the four
fields to `CoachingResponse` under a §56 amendment, with the rebuild test and
the marker moved. **What it did not do is carry them to a reader.** The step
that declares a schema and the step that delivers its outcome are different
steps, and collapsing them would make 6.19 retroactively wrong — which it is
not.

**G-50's CLOSURE IS THE THING TO RE-EXAMINE, and this step owns that.** G-50
was *"`CoachingResponse` is built at four of eight fields"* and was closed on
6.19 because the class reached eight. **The condition G-50 described — §50.1's
render contract being prompt-hoped, the UI receiving one free-text field — is
still true today.** So either the gap was scoped to the class and closed
correctly, or it was scoped to the outcome and closed early. **Rule on it here,
in writing, rather than leaving two defensible readings in the register.**

### What to build

1. **`AskResponse` gains the four**, defaulted `""` to match S-C05 as amended
   at v1.64 — a missing block is a finding, never a failed turn (§4.8).
2. **`routes.py` projects them** from the `CoachingResponse` it already holds,
   beside `answer` rather than instead of it. `message` stays the transcript
   entry; the four are the render contract. **Collapsing them is what §50.1
   forbids**, and `message` carries the text `messages` and summarisation need.
3. **The UI draws one block per field**, in §50.1's order, with `example`
   visually distinct so a Belt cannot mistake an illustration for their own
   data (B6), and `progress` always visible.
4. **An empty block renders as absent, not as a gap in the layout** —
   `presentational_gaps()` already names which came back empty.


---

## Change log

*Original lines 6779–6836.*

**Same discipline as `ARCHITECTURE.md` §56: an amendment to this document
increments the version at the top and adds an entry here.** Added 2026-09-10,
and the reason is the gap it closes — **this document sat at `Version 1.2 ·
2026-08-22` while the architecture moved through five versions.** A plan that
never changes while the spec it implements moves is not stable; it is
unwatched, and that is how the two came to disagree in ways only a cross-check
could find.

**v1.7 (2026-09-15)** — **Step 6.31, and Appendix F: build status becomes a matrix with one row per step and an anchor in every row.** **(A) THE CONDITION.** `ARCHITECTURE.md` carried 69 `> **BUILT:**` markers, each mixing design rationale with today's status, and `verify_built.py` re-ran 24 hand-written checks — **two populations that nothing made converge**, with 45 markers backed by no check at all. §58.5 stated BOTH versions of the same fact inside ONE marker block after 6.19 landed. **(B) THE SPLIT.** Rationale stays in `ARCHITECTURE.md`; STATUS moves here, to **Appendix F** — seven columns, organised by layer, one row per Appendix D step. `CONTINUITY.md` **cites and does not move**, and its hand-written vertical becomes a generated projection of Appendix F's `Order` column. **(C) THE ANCHOR GRAMMAR, NEVER A LINE NUMBER.** `mod::Symbol`, `{a,b}`, `=v`, `absent:`, `installed:`, `repo:` and `azure:`. **`installed:` failures print as a DEPENDENCY finding**, because a library that moved is not a stale marker. A BEHAVIOUR anchors on the test that observes it — still `mod::Symbol`, and deliberately **not** a new form. **(D) THE ASSERTION IS SET EQUALITY, NOT THE COUNT THAT WAS ASKED FOR.** The ruling said *“GROUP BY Step must return exactly 69”*; **this step adds 6.31 and makes it 70**, so a literal would fail on the commit that introduced it. Set equality against Appendix D in both directions is stronger anyway — a count passes when one step is dropped and another added. **(E) TWO DEFECTS FOUND BY THE SEED'S FIRST RUN.** §66 records **G-52 as closed at step 6.22**, but git carries only `2e17f3f fix(tests):` and no `commit 6.22` subject — the row is unlanded and the pointer will stop on it, the exact trap Appendix D's own note describes. And **ten steps have no Appendix A row** (9.2, 6.22–6.30) against Appendix A's rule that a step without one *“is not a step”*; thirteen more carry no `Touches`. Recorded, not fixed. **(F) 6.21 JOINS THE VERIFICATION-OWED TABLE**, which it should have joined when it landed.

**v1.6 (2026-09-10)** — **6.14 and 6.15 gain the specifications they never
had.** Both existed as an Appendix D row and a title, with no section — found
by v1.5's work on Appendix A, where they were the two rows whose Reference §
had to be inferred rather than transcribed. **6.15 is complete**: the
count-check, its three recorded instances, the five claims to assert, and the
boundary against `verify_built.py` — that script compares a claim to the TREE,
this compares a claim to the LIST IN THE SAME DOCUMENT, and both failures have
occurred without either catching the other. **6.14 is deliberately INCOMPLETE
and says so in its own first block.** The mechanism is settled — 6.12 built it
for Measure — but the content is Black Belt domain judgment: which coached
fields in Define, Analyse, Improve and Control are answered by a file, the
expected shape of each, and §23.2.1's missing role for a measurement-system
study. **A wrong `expected_shape` does not fail loudly** — it produces an ask
the Belt cannot satisfy, or accepts a file answering a different question, and
the coach proceeds confidently either way. The section states what the founder
owes and stops there.

**v1.5 (2026-09-10)** — **Appendix A is complete in both directions for the
first time.** **(A) THE FOUR MISSING ROWS LAND** — 6.13, 6.14, 6.15, 6.16. The
matrix had 51 rows against Appendix D's 55 and had been four short since the
evidence-index migration was scheduled on 2026-09-09; **6.13 landed without ever
appearing in it.** 55 / 55 now, with no row in one table absent from the other.
**(B) §62's ELEVEN SPEC ENTRIES ARE CITED BACK BY THE STEPS THAT BUILD THEM** —
S-C26 by 7.1; S-C21, S-C24, S-F25 and S-F26 by 7.2; S-C25 and S-F27 by 7.3;
S-C20 by 7.4. **This was bookkeeping, not a judgment**, and the audit that
raised it overstated the problem: every §62 entry already declared its own
`Procedure:` step, and three of the eleven (S-C22, S-C23 at 6.5; S-F28 at 3.4)
are already built. What was missing was the REVERSE citation — §55.1's
bidirectional rule satisfied in one direction only, which is exactly the
condition that rule exists to make checkable.

**v1.4 (2026-09-10)** — **The alignment pass: three restatements removed, and
this document gains a generated block.** **(A) THREE PASSAGES THAT RESTATED
`ARCHITECTURE.md` ARE NOW CITATIONS** — §47's five requirements (a verbatim copy
of its table), §35's warnings-versus-failures rule, and §53.1's rewrite-in-place
rule, which already carried the citation it was restating. **(B) A 12-word
overlap check was then run over both files and found more**: 17 distinct shared
passages, of which 8 were unattributed copies. All 8 are now citations. **One of
them proves the whole rule** — this document's restatement of the `PhaseState`
census read *"exactly 19: two identity, three plumbing, fourteen content"*. **It
is 22.** The copy had been wrong since `rejection_feedback` landed and nobody
compared it to §6, because a restatement has no mechanism that makes anyone
look. **The check now stands at 9 shared passages, every one an attributed
quotation** — a quoted LangGraph changelog string, §24's three retired names
quoted because they ARE the `grep-absence` target, §26's own definition of
multi-hop, §52's sequencing rule, §45's named candidates, and the deleted
contradiction middleware quoted as deleted. **(C) A GENERATED STEP BOARD**, in
`<!-- BEGIN STEP BOARD -->

> **Note (2026-09-25).** The v1.4 entry above ends mid-sentence at
> "in `" because the pre-commit step-board splice starts at the first
> occurrence of the BEGIN marker, which this entry quoted; the rest of the
> v1.4 entry and the whole v1.3 entry were overwritten by the generated
> board at `ed9aa1b`. The v1.3 entry, recovered from `6bc69e4`, follows.

**v1.3 (2026-09-10)** — **The document collapse, Parts 1–5.** **(A) Completion
is read from git log**, not from a status column: `BUILD_TRACKER.md` is deleted,
guard rule 2 is gone and its number is not reused, and Appendix D's status
column carries only `BLOCKED` / `GATED` / `EXTERNAL` — empty for every
schedulable step, done or not. Step 9.0 carries `EXTERNAL`, which resolves the
out-of-band wrinkle on its own terms rather than by a completion claim the
tooling must be taught to ignore. **(B) The landed count is `git ∩ Appendix D`**
— it fell 31 → 30 because 9.0 shipped as `feat(knowledge): 871637f` and the
derived figure cannot see it. No work was lost. **(C) The build target is
`../ARCHITECTURE.md`**, corrected in the status line and the three-document
table; the root reference binds at platform level and is not what a step is
built against. **(D) The drift-defence table and the live-run debt moved here**
from the deleted tracker, the table corrected on the way because its copy still
listed the retired rule 2. **(E) `docs/` now holds this file, `CONTINUITY.md`
and `_archive/`.** `DECISIONS.md`, `ARCHITECTURE_STATUS.md` and
`REFACTORING_AGENT_IMPROVE.md` are archived; the built markers they carried are
now `> **BUILT:**` lines on the items they describe (ARCHITECTURE.md §55.2),
re-run by `.claude/hooks/verify_built.py`. **(F) Appendix A's cross-check was
re-run in both directions** for the first time since 2026-09-07 — **four
mismatches found and none silently fixed**, because a disagreement between the
plan and the spec is a founder decision. They are listed in the commit that
records this entry: Appendix A is four rows short (6.13–6.16 have no row at
all, not the two the brief expected); §62's fifteen spec entries are cited by
no step; §57, §59, §61 and §64 are cited only glancingly; and 38 of 44 open
gaps are never named here, so nothing schedules their closure.

---

## Appendix A — Traceability matrix

*Original lines 6860–6869.*

> **The converse was never checked until 2026-09-07, and it should have been.**
> A ratified section with no step is an undocumented omission, which is how §26
> went six steps unbuilt. The pre-Stage-7 coverage audit ran that direction:
> **eleven ratified sections had no step. Eight now do** (6.8, 6.9, 6.10, 7.0,
> 7.6, 8.0, 8.6, 8.7). **Three fold, ruled explicitly rather than left silent:**
> §11 `step_log` is enforced by §10.3 and built incidentally by every node; §28
> memory taxonomy is a map of mechanisms specified elsewhere; §29's universal
> seven is already assigned to 7.1 and 7.5 by S-F21/S-F22. §39, §42, §43 and
> §69 were covered by steps whose rows did not cite them — §69 is added to 5.3
> above. `DECISIONS.md` Part AM.

---

## Appendix D — Step index

*Original lines 7045–7070.*

> ### ✅ THE NUMBERING TRAP IS GONE — `Seq` REPLACED IT, 2026-09-11
>
> **This header used to warn: *"A NEW STEP MUST BE NUMBERED ABOVE THE LAST
> COMPLETED ONE, OR IT IS STRUCTURALLY INVISIBLE … it does not appear late, it
> disappears."*** That was true, and it cost a renumber on 2026-09-10 when
> 6.16 landed ahead of 6.15 and the session banner jumped straight to 7.0.
>
> **`Seq` is now the order and the step number is a stable identifier.** Two
> changes, and the second is the one that mattered:
>
> 1. All three readers sort by `Seq`, not by the number.
> 2. **The WATERMARK IS GONE.** They used to pick the lowest row *strictly
>    above the highest landed step*. Re-sequencing alone would have carried
>    that rule into `Seq` space unchanged — a row below the watermark would
>    still be skipped. **Completion is now PER-ROW**: `next` is the
>    lowest-`Seq` row that has neither landed nor been made unavailable.
>
> **So a step at ANY position is reachable the moment it is unblocked**, and
> **6.10 is reachable again without renumbering** — verified by unblocking it
> in a scratch copy and watching the pointer select it from `Seq` 280, well
> below the last completed step's 330.
>
> **`Seq` is spaced by 10** so a step can be inserted between two others
> without touching any other row — which is the whole point of the column.
> **Ordering is a schedule, not a taxonomy**, and now it is also not a
> renumbering exercise.


*(continued — original lines 7098–7100)*

> **The figure fell 31 → 30 on 2026-09-10 for that reason alone** — no work was
> lost, and the hand-maintained 31 had been counting 9.0 that the derived
> figure cannot see.

---

## The bands — what the Seq ranges mean

*Original lines 7229–7246.*

> **Step 6.22 is `EXTERNAL` for the SECOND reason, and it cites its commit.**
> It landed as **`2e17f3f fix(tests): the stack ordering is observed on a real
> graph — G-52 closed`**, not as a `refactor(arch-v2): commit 6.22` subject,
> so the git-log scan cannot see it and the pointer would have stopped on it
> forever. **Its Done-when is satisfied in full** and was checked before the
> status was applied, not assumed: the new test is
> `backend/tests/test_middleware_execution_order.py`, `pytest` was green at 896,
> and the separating mutation — removing position 8's `after_agent` AND
> `aafter_agent` while the class stays in `middleware=[...]` — gave **stubbed 5
> passed, new 2 failed**. The same commit corrected this step's own Done-when,
> which had specified a mutation that separates nothing. **§66's claim that
> G-52 closed at 6.22 therefore STANDS.**
>
> **⛑ AND IT RENDERS RED, WHICH IS WRONG — registered as G-65, not fixed here.**
> `EXTERNAL` maps to the BLOCKED lane, and §55.2 defines red as *"cannot
> proceed"*. **9.0 has rendered that way since it landed**; 6.22 now joins it.
> Two completed steps shown as blocked is a real defect on the one artefact a
> founder opens, and it is a lane-assignment fix, not a status-token one.


*(continued — original lines 7260–7266)*

> **This replaces two earlier notes, both now wrong.** The first said the hook
> "will still propose it" and left the trap documented rather than fixed. The
> second said `done` had been added to `_UNAVAILABLE_STATUSES` — **that fix was
> removed on 2026-09-10** when the status column stopped carrying `done` at
> all, because a `done` status was a second, hand-maintained source for a fact
> git already owns. **The same trap applies to any future out-of-band step**:
> give its row `EXTERNAL`, `BLOCKED` or `GATED`.

---

## 66.8 The Supplier/Customer cross-check — first run, 2026-08-23

*Original lines 8053–8115.*

**Run mechanically over all 73 entries as the conversion landed.** 28 entries
carry a SIPOC table; 58 directed edges were checked in both directions;
**36 did not close.**

**Five are substantive, and three of those confirm a gap this document already
names.** The cross-check found them without being told to look:

| Edge | What it means |
|---|---|
| S-F05 names S-F03 as Supplier; **S-F03's Customers are S-F04 and S-F09 only** | **G-01, decision point 1, detected mechanically.** The validation stack says the planner triggers it and the planner does not say it routes there — because that routing does not exist |
| S-F10 names S-F03 as Customer; **S-F03's Suppliers do not include it** | **G-42, detected mechanically.** A mapper cannot be named as a supplier of the planner because it has no stated execution site |
| S-F12 names S-F03 as Customer; **same** | **G-42**, on the other four phases |
| S-F09 names S-F04 as Customer; **the sample's Supplier cell names only `phase_planner`** | **F-04.** The multi-hop path feeds the coach call and is not accounted for. Not corrected — the sample is verbatim |
| S-F29 names S-F33 as Customer; **S-F33 has no SIPOC table at all** | **G-35.** The error handler routes to `degraded_coaching_response`, which is undefined and would be a sixth node §13 forbids without an amendment |

**The remaining 31 are structural, and they are the rule's problem rather than
the architecture's.** They fall into five classes:

| Class | Count | Finding |
|---|---|---|---|
| The calibrated sample names its neighbours in prose (`phase_planner`) rather than by entry ID, so the parser cannot match them | 11 | F-04 |
| Nested sub-components — Layers 2c and 2d inside the validation stack, gate assembly and the policy advisory inside `gate_apply`, RRF and the retriever layer inside the `rag_lookup_*` tools | 12 | F-07 |
| Request/response and build-time/run-time pairs — the API surface both triggers the graph and consumes its output; the supervisor graph both builds subgraphs and runs them | 6 | F-07 |
| Edges pointing at class entries, which carry no SIPOC table | 2 | F-05, F-06 |
| **Store-mediated data handoffs** — neither party invokes the other; the value travels through a Store key | 1 | **F-08 — see the note below** |

> **The conclusion was about the rule, not the result — and the rule has since
> been narrowed.** A check reporting 36 failures of which a handful matter would
> have been ignored by its third run, becoming the fourth instance of the
> pattern §55 names: a check whose output nobody reads.
>
> **RESOLVED 2026-08-24. §55.1 rule 3 now applies only to peer runtime call
> edges.** The re-run under the narrowed scope was **executed, not estimated**:
>
> | | Count |
> |---|---|
> | Non-closures, un-narrowed | 36 |
> | Out of scope — return paths | 13 |
> | Out of scope — nested sub-components | 11 |
> | Out of scope — build-time relations | 2 |
> | Out of scope — edges into class entries | 2 |
> | Out of scope — Store-mediated data handoff | 1 |
> | **In scope** | **7** |
>
> **Of the 7, two are one edge counted in both directions** — `phase_planner`
> ↔ `phase_executor` — and it fails only because the verbatim sample names its
> neighbours in prose rather than by entry ID. **Notation, not wiring.** The
> other **five are real, and every one traces to something already registered**:
> G-01, G-42 twice, F-04 and G-35. Signal-to-noise moves from 4-in-36 to
> 5-in-7.
>
> **Four of those five are now closed.** G-42's two edges and G-01 were all
> resolved on 2026-08-24 (§66.6), leaving F-04 and G-35 open on this run.
>
> **One detection is lost to the narrowing, and it is recorded rather than
> quietly absorbed.** **F-08** — the gate document written to one Store key by
> two claimed writers — was found on the S-F11 → S-F12 edge, which is a
> **Store-mediated data handoff and not a call**. The narrowed rule does not
> reach it and will not re-find it. **Data-handoff edges are outside rule 3 by
> construction**; checking them is a separate rule with its own scope, and none
> is proposed here. F-08 itself stays open at §66.7.
>
> The scope definition and its reasoning are in §55.1.

---

## ✅ THE SEED HAS LANDED — all 35 of Define's rows are written

*Original lines 8214–8233.*

**Handed over by the founder, 2026-09-23**, after the founder had checked
them: rows 1–17 and 22–24, the twenty that were pending. **They were not
drafted by an implementer, on purpose**: the rows are the definition of done
for the whole vertical, and an implementer drafting them would be choosing what
the product is required to do and then building against their own answer.

**ROWS 18 TO 21 ARRIVED AHEAD OF THE SEED** because the steps that give them
landed first — 6.48 plus the S-C05 amendment, then 6.20's scorecard half, then
6.42, all 2026-09-23. **Rows 25 to 35 arrived with the register's growth
24 → 35** the same day. **The twenty seed rows arrive 🔴**, including the four
whose mechanism is already built (5, 6, 10, 11): **a row is green on what its
check returns, never on the argument that the code exists**, and none of them
has a check yet.

**The project's status by clause 1 was `4 of 35`** when the seed landed, against a
register **35/35 written**: 4 green, 31 red, 0 unwritten. **Step 6.49 (the checks
card) moves it to `12 of 35`**, **6.52 B2 to `13 of 35`** (row 13), and **6.54 to `14 of 35`** (row 2). **Row 13 went red again on 2026-09-24 (G-96): `13 of 35`**, **6.46 takes it to `14 of 35`** (row 3), and **G-96's fix to `15 of 35`** (row 13 again) — see the notes after the table. The count did not move,
and that is the honest result — the seed turned twenty unstated requirements
into twenty visible, ordered pieces of red work. **Nothing was measured by
writing them down.**


*(continued — original lines 8292–8363)*

> ### ⇒ STEP 6.49 — WHAT THE TWELVE CHECKS RETURNED, 2026-09-24
>
> **Eight green, four red. `12 of 35`.** Rows 12 and 13 are `xfail(strict=True)` with the defect as the reason, as is the plan-order check, so the suite stays usable and **goes loud the day one starts passing**. Every check reads what the system wrote
> on `IMPR-2026-0E5` and constructs no input; the mutation proofs live beside them
> and hand each predicate the evidence the broken behaviour would have written.
>
> | Row | State | Evidence |
> |---|---|---|
> | **2** | 🟢 since 6.54 | **Both live turns on 2026-09-24 failed** with 500 — the executor's 45 s run timeout, one graph run each. Trace `01a0d215-a216-75e2-ba80-1c80597f891f` (06:23): the grader failed the reply twice and was re-judging **the same text** when time ran out. Trace `01a0d28e-d4da-7901-a75e-44d86b102098` (08:36): three knowledge lookups in a row — `rag_lookup_methodology` 12.2 s, `rag_lookup_evidence` 9.8 s, `rag_lookup_case_history` 10.4 s, about 32 s. **The executor soft budget (`nodes_common.py:647`) did not end either turn before the 45 s limit.** The case is not stuck: the second turn started cleanly on top of the first. Opt-in: `CAPABILITY_LIVE_TURN=1` **After 6.52 B1 (trace `01a0d2c0-457e-74e0-9934-88dff9573a5f`, 09:30): 200, not 500** — the executor node ended at 40.4 s, inside its wall, and two lookups ran in parallel. **Still red:** the Belt got the degraded *"I ran out of time"* answer, because coherence judged the coach's finished reply three times (7.2 s) and the budget ran out in the grader — B2's defect; and the whole turn took 50.8 s end to end **After 6.52 B2:** each judge makes one call — the open-question turn `01a0d2ca-4ca3-7951-b128-2b7e3e1651ed` (09:41) made one coherence call and one grader call, and still ended degraded: 7.4 s of setup before the first model call, two parallel lookups of 15.5 s and 10.7 s, and the grader's one call cut at the 40 s budget. A narrow question (`01a0d2cc…`, 09:43) returned a coached 200 in 29.7 s. **The row's check now refuses the out-of-budget message as a coached reply.** Open questions are a latency problem — G-83 **Green at 6.54:** row 2's own check, run live — trace `01a0d36b-49dc-7470-b924-9e30c9505235`, **first turn in process: yes**, coached, executor 14.6 s, no client built in the turn. The open-question proof on a restarted server: `01a0d366-bf6e-7020-9d5f-1bb5a972bcdf`, **first turn in process: yes**, two parallel lookups, coached in 24.1 s of executor time; a warm turn after it, `01a0d367-3d03-7ee3-b4c5-a191a60d8c97` (first turn in process: no), 23.8 s |
> | **10** | 🔴 | **Skipped: no calculation turn yet on 0E5.** No turn's `artifacts` carry a `computation_results` row. Red because a row that did not run is not green |
> | **12** | 🔴 | **10 of 10** turns on `0E5` in which layer 2a checked more than once — i.e. rejected — show **no model call after the rejection**: the loop re-checks the same reply rather than re-asking. `CoherenceMiddleware.aafter_agent` calls `self._check(belt_text, coach_text)` with an unchanged `coach_text` each iteration. Also: 2a judges the **coach's** reply, not the Belt's answer, so the row's premise and the mechanism ask different questions |
> | **13** | 🟢 since 6.52 B2 | The latest completed coaching turn's `step_log` has 6 entries and **none** with `layer: "coaching_grader"`. The grader runs (its hook is in every trace) and its verdicts are collected into `grader_log` (`nodes_common.py:996`, `:1072`), which `_build_executor` returns at `:1444` and **nothing ever reads** **Green at 6.52 B2:** the executor now writes `grader_log` into `step_log`; the first completed coaching turn after it (trace `01a0d2cc-a58b-7ed0-83aa-cf718340f376`, 09:43) carries `coaching_grader · failed`, from ONE grader call |
> | **33** | 🟢 | On the failed live turn: parent steps 62→63 contiguous with 61 before it; the subgraph wrote −1, 0, 1 (recording `planner`); the executor wrote −1…9. **Every node that finished has a checkpoint**, and `define_phase`, which raised, is correctly owed none. Also green on the last completed turn |
> | **35** | 🟢 | The failed live turn still left a trace: 44 runs, two model calls at the `model` node with their bound tools listed, eight middleware hooks, and both tools the turn called (`load_evidence_series`, `rag_lookup_methodology`) as tool runs **UNPROVEN SINCE 2026-09-24 ~13:10 UTC (G-95):** LangSmith refuses every trace (429, monthly quota). The register keeps the row green by founder ruling; its check SKIPS — not a pass — for turns after the refusal began, until one live turn is traced again **PROVEN AGAIN 2026-09-24 14:50 UTC** on the G-96 live turn, trace `01a0d3e5-6246-7de3-b768-2ee767a5130c` (first turn in process: yes): 39 runs, the model call with its tools, seven middleware hooks, and `load_evidence_series`, the one tool the turn called. The G-95 skip is removed from the check |
> | **3** | 🟢 since 6.46 | The script is in the system message on every model call and each turn records it: 0E5, 2026-09-24 13:13 (**first turn in process: yes**) — `coaching_script` delivered on both model calls, version 1.2, sha256 `a5aa86347681c4fd`; 13:14 (first turn in process: no) — delivered on its one call. Row 3's check reads the latest completed coaching turn and passes. **No trace ids: LangSmith refused both (G-95)** |
> | **28 · since 6.57** | 🔴 live-turn | The count is COMPUTED: trace `01a0d729-1b33-7591-99f9-e3391f0da1e5` (2026-09-25 06:03, first turn in process: yes) — `step_log` `define_position` 12 of 12, the stored reply's `progress` *"Define · Step 12 of 12"*; the model's own was *"Define · 13 of 13"* (`reply_matches: false`), overwritten. Whether the coach STATES it in the prose the Belt reads is the row's live-turn question — founder marks |
> | **26–32** | 🔴 live-turn | **Observed on the two 6.46 turns (13:13 first in process: yes; 13:14: no), from the checkpoints' STRUCTURED reply — no trace ids (G-95), so this does not meet the evidence standard and the rows stay red.** 26 §43.1: no calculation ran — not observable. 27 §43.2: an `example` WAS given before the `prompt` in both turns — but invented by the coach (*"Delivery delays occur in 15% of shipments…"*), not the script's worked example; nothing was captured from it. 28 §43.3: `progress` read *"Define · 13 of 13"* — a count over the gate's 13 fields, not *"Step n of 12"*. 29 §43.4: no missing-field list shown (`check_gate_status` does not exist). 30 §43.5: own voice, no link ✓. 31 §43.6: 13:13 critiqued the stored problem statement and named what to refine ✓; 13:14 accepted the Belt's business case and asked them to confirm its impact. 32 §43.7: the metric's meaning was not addressed |
> | 1, 5, 6, 8, 11, 17 | 🟢 | Read from the case record, the registry route, the evidence index and the recorded 2b verdict of 2026-09-15 |

> **ROW 18's CHECK READS THE CASE THE SYSTEM WROTE, AND BUILDS NO INPUT OF ITS
> OWN.** That is the whole of its design. A seeded version would have been
> **green throughout the entire life of the defect it exists to catch** —
> every fixture in the suite handed the capture path a correctly-typed value,
> which is why four structured Define fields sat as prose for months under
> 1,100 passing tests. **It SKIPS rather than passes when there is no case to
> read**: a row that could not be evaluated is not a green row.
>
> **Evidence, 2026-09-23** — red against `IMPR-2026-0E5` before the run,
> green after, on the same four prompts that returned prose the day before.
>
> **ROW 19 IS THE SAME DESIGN AND THE SAME REASON.** `GET /gate/review` had
> answered **500** on a complete real case since before the audit — first for
> the missing metric entry, then for the four prose fields. It now returns an
> eighteen-key document, `passed: true`, `missing_fields: []`. **Both rows read
> the case the system wrote; neither builds its own input.**
>
> ### ⇒ ROWS 20 AND 21 READ A SECOND CASE, AND THAT IS THE RULING
>
> **`IMPR-2026-1FF` — *"GATE PROOF — step 6.42, do not use for Define coaching
> proofs"*.** Founder ruling 2026-09-23, option B. **Submitting a gate ADVANCES
> the case out of Define**, so proving the write on `IMPR-2026-0E5` would have
> ended the Define proofs still owed — the ten checks, 6.46, 10.3 and 6.44 all
> need a live define case. `IMPR-2026-0E5` therefore stays in define.
>
> `1FF` was coached to **13 of 13 through real turns with the real model**,
> nothing constructed, and its gate was submitted **once**: `HTTP 200`,
> `passed: true`, an eighteen-key document, and **`field_log` intact at 13
> entries** — which is row 21, on the write that used to erase it.
>
> **A SUBMITTED CASE HAS ADVANCED AND CANNOT CARRY THE NEXT GATE PROOF.** `1FF`
> is now in `measure`. **Step 7.3 will need a fresh case**, and a scripted
> driver that runs real turns to the gate is worth building before then —
> noted here rather than built.
>
> **The uploads half of row 21 is proven by the mechanism test, not live**:
> `1FF` carries no uploads, because none were uploaded to it. The live half
> proves the change log; the fixture proves that a call naming neither
> `citations` nor `uploads` no longer erases them.

> ### ⇒ SEVEN OF THE ELEVEN NEW ROWS BELONG TO ONE STEP, AND THAT IS THE POINT
>
> **Rows 26–32 are §43.1–§43.7, one per rule, and all seven are owned by
> 6.46** — *the coaching script is guaranteed to reach the model, or its
> absence is recorded.* They are the SEVEN THINGS the script is supposed to
> make true, and every one of them is currently unobservable for the same
> reason: **`load_skill` is called zero times on a live turn** (measured
> 2026-09-23 at step 6.48), so the script that carries §43's method never
> reaches the coach.
>
> **So 6.46 is not a logging step.** It is the step seven capability rows wait
> on, and the register now shows that rather than leaving it as one row of
> plumbing among many.

---

## The run of work — superseded 2026-09-25

*Original lines 8421–8426.*

**The 2026-09-23 transcription that stood here is withdrawn.** The run of
work is Appendix F's `Order` column (founder rulings 2026-09-25: 6.61, 6.59,
6.58, 6.56, 6.45, 6.51, 10.3, 10.4, 6.43, 6.44, 7.1, 7.2, 7.3, 7.7, 7.4, 7.5,
7.8, 7.9, then 6.62; 10.0 landed at b5b6e77). A second copy here is what the 8D of 2026-09-25 found drifting.

**6.42 and everything before it has landed**, which is why the run starts here.

---

## Appendix E — Questions raised by this procedure · BOTH RESOLVED

*Original lines 8432–8464.*

*Both were raised by writing this document and both were ruled on 2026-08-21,
before any step executed. Recorded here so the resolution is visible at the
point the question arose.*

**1 — The four cross-agent tools · RESOLVED.** `search_resolve_cases`,
`search_resolve_knowledge`, `search_resolve_evidence` and `search_flow_vsm` sat
between §29.1 (which sanctions read-only cross-agent tools) and §29.2 (whose
universal seven excludes them) — permitted and unaccounted for at once.

**Ruled: a distinct third category, RATIFIED as present-but-not-bound.** Added
as **Reference §29.4** through the §56 amendment procedure; decision record
`docs/_archive/DECISIONS.md` §Q1. Kept because the three `search_resolve_*` tools are
verified read-only paths into a production system; unbound because §30's tool
ceiling would put Measure at 18 against a cap of 16, and there is no evidence
cross-agent retrieval helps DMAIC coaching until the §52 dataset exists. **Three
rules bind before any may be bound to a coach**, §27 compliance among them.
Applied at step 5.2.

**2 — The retired-name strings · RESOLVED, and worse than reported.** CLAUDE.md
§5.1 and the reference's Appendix D.1 named `search_methodology` and `search_evidence` as
the retired tool names.

**`search_methodology` exists nowhere in the codebase. `search_evidence` does
exist — as a live retriever function CLAUDE.md §7.2 requires to keep
existing.** So the constitution contradicted itself: §5.1 banned a name §7.2
mandated. A `grep-absence` check written from the old list would have passed on
a fiction while all three real retired names survived.

**Corrected directly** — the retired **tool** names are
`search_improve_knowledge`, `search_improve_cases`, `search_improve_evidence`;
the **retriever** layer keeps its names. Fixed in CLAUDE.md §5.1, §0.3 and the
no-go list, and in Reference §24 and Appendix D.1, which now carries a warning that
these strings are load-bearing for verification. Applied at step 5.2.

