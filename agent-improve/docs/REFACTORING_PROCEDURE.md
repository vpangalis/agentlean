# Agent Improve — Refactoring Procedure
**AgentLean Platform · DMAIC Improvement Agent**
Version 1.2 · 2026-08-22
Status: **RATIFIED.** The ordered path from the v1 tree to the target in
`../../AGENTIC_ARCHITECTURE_REFERENCE.md`.

---

## ⚑ STATUS BANNER — 2026-08-27 · the phase specs are now RATIFIED INPUTS

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
> ruling at **`docs/DECISIONS.md` Part X**. **§0.2's WATCH 7 row and step 3.4's
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

`../../AGENTIC_ARCHITECTURE_REFERENCE.md` describes **the target**. `CLAUDE.md` states **the
rules**. This document is **the route** — the ordered, verifiable sequence of
commits that gets the codebase from where it is to where the reference says it
should be.

**It contains no design.** Every *what* and every *why* is a reference citation.
Where this document appears to state a design decision, the reference section named
in the step is authoritative and this document is a bug.

### The three-document division

| Document | Answers | Binding? |
|---|---|---|
| `agent-improve/CLAUDE.md` | **What the rule is** | **Yes** |
| `../../AGENTIC_ARCHITECTURE_REFERENCE.md` | **How the system is shaped, and why** | **Yes** |
| This document | **In what order it gets built, and how each step is proved** | **Yes** |

`../ARCHITECTURE.md` is **no longer the v2.2.16 design document** — since
2026-08-22 that path holds a copy of the root reference, Improve's own
architecture doc. **The old §15 migration sequence is replaced by this
document** and is available only at commit `8533879`.

### How to use it

1. **Find your position.** The session-start hook reports the last completed
   `refactor(arch-v2)` commit from git log and the next step from Appendix D.
2. **Read the step record.** Check its **Precondition** steps are done.
3. **Run the step's prompt** (each step carries one, ready to paste).
4. **Run the step's Verify method.** It either passes or the step is not done.
5. **Commit with the step's ID in the subject.** One step, one commit.

### The completion contract

**One step = one commit, strictly.** The subject line format is fixed, because
the session-start hook parses it:

```
refactor(arch-v2): commit 4.2 — <what changed>
```

A step is done when its **Verify** method passes and its **Done when**
condition is observably true. Not when the code is written. Not when it looks
right.

### Numbering

**The commit spine continues from 2.2**, the last completed step under the old
`ARCHITECTURE.md` §15 numbering. Steps here are `{stage}.{step}` and run
2.3 → 11.2. **The internal organisation is by Reference §53.1 stage**; the two
views are reconciled in **Appendix A**, which maps every step to the reference
section that specifies it.

Continuing the spine rather than renumbering was deliberate: the git history
and the session-start hook both key on these numbers, and renumbering would
break the only automated continuity signal the project has.

### Reading conventions

| Marker | Meaning |
|---|---|
| **BLOCKED** | Cannot start. The blocker is named, with what unblocks it |
| **GATED** | Can be written, must not be merged until the gate clears |
| **EXTERNAL** | Not a code change — an Azure or infrastructure operation |
| **PARALLEL** | Not on the critical path; runs alongside (Appendix C) |

### Verification vocabulary

**Every step names exactly one primary method from this fixed set.** A step
whose verification is "it looks right" is not a step.

| Method | What it means | Passes when |
|---|---|---|
| `pytest` | A named test file runs | Named tests green |
| `grep-absence` | A banned pattern is provably gone | **Raw `grep -rn` (never a gitignore-filtered tool — reference §55)** returns **zero** hits repo-wide, and the pattern string is verified to exist in the codebase before the change |
| `import-check` | Module imports and constructs without error | `python -c "import ..."` exits 0 |
| `live-run` | Headless invoke against real Azure | Named observable produced |
| `trace-check` | A named span appears in LangSmith | Span present with expected parent |
| `azure-query` | Index or blob state inspected directly | Named field/document count matches |
| `manual-UI` | **Requires Vassilis in a browser** | Named screen behaves as stated |

`manual-UI` is the only method that needs a human. Steps using it are flagged
so they can be batched into one session rather than interrupting the run.

---

# Part 0 — Preconditions and gates

---

## 0.1 What must be true before step 2.3

| Precondition | State as of 2026-08-21 |
|---|---|
| Reference signed off | ✔ Task 3 + 3B complete, verification log closed |
| `CLAUDE.md` current | ✔ v2.2.16, all citations resolve to reference sections |
| `../ARCHITECTURE.md` disposition settled | ✔ v2.2.16 original absorbed; path now holds Improve's copy of the reference (2026-08-22) |
| Working tree clean and pushed | Check before every step — `start.ps1` destroys unpushed commits |

## 0.2 Standing gates

These block **specific named steps**, not the whole procedure. **A gate must
never be allowed to stall steps that do not depend on it.**

| Gate | Blocks | Clears when |
|---|---|---|
| ~~**LangGraph < 1.2.6**~~ | ~~4.1, 4.2, 4.3, 4.4, 8.2~~ | **CLEARED 2026-08-21** — step 2.3 landed `langgraph` 1.2.11 |
| **`RunControl.request_drain()` UNCONFIRMED** | **8.5 only** | The API is confirmed against a real release or the LangGraph source — or a fallback drain is designed. Reference §45 |
| **Azure Cache for Redis not provisioned** | 8.4 only | The resource exists. Reference §46, Appendix B |
| **Two Azure index schema changes unapplied** | 5.2's `order_by` and `phase` filter; `rag_lookup_case_history`'s vector field | Step 9.1 lands |
| **WATCH 7 — Define gate non-functional** | Define phase end-to-end runs | Step **4.1** lands (Define subgraph; executor stops delegating to v1 `orchestrate_define`, which still writes v1 names). Accepted interim, not a bug — a consequence of running 3.4's Define portion (commit `4701a09`) ahead of 4.1. `validate.py` reads v2 names; `orchestrate.py` writes v1 names; gate reads all Tier-1 fields missing. **Do not add a v1→v2 shim** (CLAUDE.md §17) — the migration happens naturally when 4.1 replaces the orchestrator's role. Cross-phase Define briefs in analyse/improve/control stay on v1 names until then, deliberately. **⚑ RULED 2026-08-28 — ROUTE A. This row is superseded on two points and left as written per annotate-don't-rewrite.** (a) It **clears at step 6.2**, not 4.1 — step 4.1's own prompt has the executor still delegating to `orchestrate_define`, so 4.1 cannot clear it. 6.2 gives the executor its own capture path via `response_format=CoachingResponse`. (b) `orchestrate.py` is **never migrated**; it and `EXTRACTION_DEFINE`'s Define block carry the v1 names unchanged and are **deleted at 11.1** (Appendix B). The Define gate is accepted as inert until 6.2 — nothing else is blocked. See `CONTINUITY.md` §6 and `docs/DECISIONS.md` Part X. |

> ### ⛔ On `request_drain` specifically
>
> **No step in this document may be written against `RunControl.request_drain()`
> until it is confirmed to exist.** Step 8.5 exists as a placeholder that names
> the requirement and the gate, not as work to schedule. If confirmation fails,
> 8.5 is rewritten as a real fallback drain design (Reference §45 names the
> candidates) — it is **not** re-cited to another plausible API name.

## 0.3 What "current codebase" means

Measured 2026-08-21. **These numbers are the baseline the steps below act on**;
if they have moved, re-measure before starting.

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


| Fact | Value |
|---|---|
| Backend Python files | 55 (7,924 lines) |
| `ui/index.html` | 7,172 lines, single file |
| Graph nodes | 11, flat, one `set_entry_point` |
| Phase nodes | All sync `def` |
| Route handlers | All sync `def` — no `async def` in `gateway/routes.py` |
| `response.content.strip()` sites | **20** |
| LLM roles in `_ROLE_MAP` | 6, over 3 deployment settings |
| Checkpoints ever written | **0** |

---

# Part 1 — Stage 2: Foundation hygiene

*No new architecture. These are the corrections that everything else assumes,
and each is independently valuable if the refactor stalls.*

---

## Step 2.3 — Dependency upgrade

| | |
|---|---|
| **Reference §** | §53 (dependency floor) · §16 (why ≥1.2.6) |
| **Touches** | `requirements.txt` · `.venv` |
| **Precondition** | 0.1 |
| **Verify** | `import-check` |

**The floor is a rule; the target is a measurement.** The floor is
**≥1.2.6** — LangGraph 1.2.6 (2026-06-18) carries *"nested subgraph inherits
parent `checkpoint_ns` (regression in 1.2.3)"*, which §16 depends on.

**Resolve the exact target by running `/verify-current-version` as this step's
first action.** As of 2026-08-21 that resolved to `langgraph` 1.2.11,
`langchain` 1.3.16, `langchain-classic` 1.0.8. **If the skill resolves
different values, the skill wins** — Reference §53's table is a snapshot and says
so.

**The `langchain-core` jump is the risk.** `langchain` 1.3.16 requires
`langchain-core>=1.6.0`; installed is 1.3.3. Three minors. Expect this to be
where surprises land, not in `langgraph`.

**Change:** upgrade, let pip resolve adjacent packages, then repin all of them.
Sweep for imports from `langgraph.prebuilt` (CLAUDE.md §4.4) and fix any found.

**Done when:** `python -c "import langgraph, langchain; print(langgraph.__version__)"`
reports ≥1.2.6, `pytest backend/tests/` is green, and the app starts.

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

| | |
|---|---|
| **Reference §** | §12 · CLAUDE.md §3.1, §14 no-go list |
| **Touches** | [`core/graph.py:73`](../backend/core/graph.py#L73) |
| **Precondition** | 2.3 |
| **Verify** | `grep-absence` |

**Change:** replace the single `builder.set_entry_point("orchestrate_define")`
with `builder.add_edge(START, "orchestrate_define")`, importing `START` from
`langgraph.graph`.

**Done when:** `grep -rn "set_entry_point" backend/` returns zero hits and the
graph still compiles.

**Rollback:** trivial, single line.

**Prompt:**
> CLAUDE.md §3.1: entry is declared with `add_edge(START, ...)`;
> `set_entry_point` is superseded and on the no-go list. In
> `agent-improve/backend/core/graph.py`, replace the `set_entry_point` call
> with `add_edge(START, ...)` and add the `START` import. Change nothing else.
> Confirm `grep -rn "set_entry_point" agent-improve/backend/` returns nothing.

---

## Step 2.5 — Async conversion

| | |
|---|---|
| **Reference §** | §14 (node contract) · §49 (async by default) · CLAUDE.md §1.4 |
| **Touches** | 11 node functions across `phases/*/orchestrate.py`, `phases/*/validate.py` · `escalate.py` · all handlers in `gateway/routes.py` |
| **Precondition** | 2.4 |
| **Verify** | `live-run` |

**Why this precedes everything architectural:** per-node timeouts (§45) are
unavailable on sync nodes — a hard LangGraph constraint, not a preference. Every
reliability step in Stage 8 depends on this being done first.

**Change:** convert all 11 phase nodes and `escalate` to `async def`; convert
every handler in `gateway/routes.py` to `async def`; `await` all LLM calls
(`llm.ainvoke`) and Azure SDK calls where an `aio` variant exists.

**Do not** change dispatch logic here — routes still dispatch manually until
4.2. This step converts signatures and call sites only.

**Done when:** a `/ask` request against case `IMPR-2026-E9D` returns a coaching
response with no `RuntimeWarning: coroutine was never awaited` in the log.

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

| | |
|---|---|
| **Reference §** | §21 (typed content blocks) · CLAUDE.md §4.5 |
| **Touches** | 20 sites — see below |
| **Precondition** | 2.5 |
| **Verify** | `grep-absence` |

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
blocks. String-indexing or substring-parsing the raw content field breaks the
moment a provider returns a multi-part response.

**Done when:** `grep -rn "\.content\.strip()\|\.content\[" backend/` returns
zero hits, and a `/ask` turn still returns coaching text.

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

| | |
|---|---|
| **Reference §** | §21 (roles, temperature, factory) · §54 (where classes live) |
| **Touches** | [`core/llm.py`](../backend/core/llm.py) · every `get_llm(...)` call site |
| **Precondition** | 2.6 |
| **Verify** | `pytest` |

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

**Done when:** `pytest backend/tests/test_llm.py` (new) asserts all 11 roles
resolve to a deployment and that grader temperature is 0.1.

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

# Part 2 — Stage 3: State and persistence

---

## Step 3.1 — `SupervisorState` and `PhaseState`

| | |
|---|---|
| **Reference §** | §5 · §6 · §7 |
| **Touches** | `core/state.py` (rewrite) · `core/substate.py` (new) |
| **Precondition** | 2.7 |
| **Verify** | `import-check` |

**Change:** `core/state.py` holds `SupervisorState` — exactly seven fields
(§5). `core/substate.py` holds `PhaseState` — exactly 19: two identity
(`case_id`, `current_phase`, copied down by the input mapper and read-only in
the subgraph), three plumbing, fourteen content (§6). The v1 `ImproveGraphState` is deleted in step 11.1, not
here; both coexist until the last v1 consumer is gone.

**`gate_attempts` must be on `PhaseState`** — holding it in route scope is what
produced the v1 "attempts always reset to 0" bug (§6).

**Done when:** both modules import, and a field-count assertion passes: 7 and
19.

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

| | |
|---|---|
| **Reference §** | §9 · §10 |
| **Touches** | `core/store.py` (new) |
| **Precondition** | 3.1 |
| **Verify** | `live-run` |

**Change:** `AzureBlobStore(BaseStore)` at `core/store.py`, namespace
`("projects", case_id, <kind>)`, blob prefix
`store/projects/{case_id}/{kind}/{key}.json` (§9).

**Done when:** a headless script writes a gate document to
`store/projects/IMPR-2026-E9D/artifacts/define.json` and reads it back
identically.

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

| | |
|---|---|
| **Reference §** | §9 (boundary mappers) |
| **Touches** | `phases/{phase}/mappers.py` × 5 (new) |
| **Precondition** | 3.2 |
| **Verify** | `pytest` |

**An input mapper's only dependency is `BaseStore`** (§9). Reading context off
parent state, or handing a mapper a blob client, is a violation: the first
creates a parent field to keep in sync, the second puts untracked I/O in a
translation function.

**Done when:** unit tests show Define's input mapper composing `phase_context`
from the case record, and Measure's composing it from Define's stored gate
document.

**Prompt:**
> CLAUDE.md §10.2 (boundary mappers). Create `mappers.py` in each of the five
> `agent-improve/backend/phases/{phase}/` directories, each with an input mapper
> and an output mapper as §10.2 specifies. **The only dependency is
> `BaseStore`** — no blob client, no parent state reads. Define's input mapper
> reads the case record; the other four read the prior phase's artifacts. Write
> unit tests with a fake store for Define and Measure.

---

## Step 3.4 — `{Phase}PhaseInput` → `{Phase}Output`, with validators and UI

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


| | |
|---|---|
| **Reference §** | §7 (field typing law) · §40 (the five schemas) · §41 (structured dicts) · §53.1 (rewrite in place) |
| **Touches** | `phases/{phase}/schema.py` × 5 · `phases/{phase}/validate.py` × 5 · `ui/index.html` |
| **Precondition** | 3.3 |
| **Verify** | `manual-UI` |

**Rewritten in place** — `{Phase}PhaseInput` becomes `{Phase}Output` in the
same file. No parallel schema, no deprecation window, no retirement step
(§53.1). There is no production consumer to protect.

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

**Done when:** case `IMPR-2026-E9D` opens in the workspace, the right-hand
captured-fields panel renders without blanks, and the Define gate document
preview shows the SIPOC with six keys including `process_metrics`.

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

# Part 3 — Stage 4: The graph

> **Ordering note — a deliberate departure from Reference §53.1's list order.**
>
> §53.1 lists `thread_id` wiring **before** phase subgraphs. That order cannot
> execute. The v1 graph chains all five phases with conditional edges, so a
> single `ainvoke` would run the entire DMAIC sequence — there is no turn
> boundary to halt on. That is precisely why `gateway/routes.py` dispatches one
> node manually today.
>
> **One invoke equals one Belt turn only once a phase subgraph with a real
> boundary exists.** So 4.1 builds the subgraph and 4.2 wires `thread_id`
> through it. The §53.1 list states the *shape* of the sequence; resolving the
> executable order is this document's job (§53.1: *"the ordered procedure … is a
> separate document"*).

---

## Step 3.5 — `storage/blob.py`: `ImproveBlobClient` class → functions, sync → aio

| | |
|---|---|
| **Reference §** | §54 (where classes live) · §10 (concern 2) · §49 (async by default) · CLAUDE.md §2, §1.4 · **S-C08** |
| **Touches** | `storage/blob.py` · every `blob_client.*` call site in `gateway/routes.py` |
| **Precondition** | 3.2 |
| **Verify** | `live-run` |

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

**Done when:** `/ask` and `/cases` both answer against case `IMPR-2026-E9D`
with the case document read and written through the new functions, no
`RuntimeWarning: coroutine was never awaited` and no unclosed-session warning
in the log, and `grep -rn "class ImproveBlobClient" agent-improve/backend/`
returns zero hits.

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

| | |
|---|---|
| **Reference §** | §12 (topology) · §13 (five nodes) · §14 (node contract) |
| **Touches** | `phases/define/graph.py` (new) · `phases/define/nodes.py` (new) |
| **Precondition** | 3.4 · **gate: LangGraph ≥1.2.6** |
| **Verify** | `import-check` |

**Five nodes: `planner`, `executor`, `validation_stack`, `gate_review`,
`gate_apply`** (§13). `policy_advisory` and `revise` are BANNED as node names.

**The subgraph compiles with NO checkpointer and NO store** (§16) — both attach
to the parent graph only.

At this step the five nodes are **structurally correct and behaviourally
minimal**: the planner returns a stub `CoachingPlan`, the executor still calls
the v1 orchestrate logic. Stages 5–7 fill them. This keeps the step small
enough to verify.

**Done when:** `build_phase_subgraph("define", llm)` returns a compiled graph
with exactly those five node names, asserted in a test.

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

| | |
|---|---|
| **Reference §** | §16 (`thread_id`) · §47 (all five requirements) · §49 (one runtime) · §8 |
| **Touches** | `gateway/routes.py` · `core/graph.py` · `core/store.py` |
| **Precondition** | 4.1 · **gate: LangGraph ≥1.2.6** |
| **Verify** | `azure-query` |

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

| # | Requirement |
|---|---|
| **1** | **Deliberate handler shape** — inline `await` streaming, or an explicit ABANDON policy calling `t.cancel()` in `gen()`'s `finally`. **Never a bare `asyncio.create_task` with no disconnect handling** — a handler that has not chosen has chosen COMPLETE by accident |
| **2** | **Deterministic `step_log` keys** — `f"{phase}:{turn_count}:{step_name}"`, never a raw timestamp as identity |
| **3** | **Azure Blob lease as the per-thread concurrency guard** — two tabs on one `case_id` means two writers on one `thread_id` |
| **4** | **A reconciliation sweep that EXCLUDES `interrupt()`-paused threads** — a thread paused at a gate is indistinguishable from an abandoned one by "no recent activity" alone |
| **5** | **`thread_id` / `case_id` derived from the authenticated session, never client-supplied** — `case_id` is the tenancy boundary |

**Ratified policy is ABANDON, not COMPLETE** (§47). A silently-completed gate
approval the Belt never saw is unacceptable in a system whose premise is that
the Belt approves what gets committed.

**Change:** routes stop dispatching nodes manually and call
`await graph.ainvoke(state, config={"configurable": {"thread_id": case_id}, "recursion_limit": 50})`.
`get_graph()` is used, not discarded.

**Done when:** `azure-query` shows
`checkpoints/{case_id}/latest.json` exists after one `/ask` turn — **the
first checkpoint this system has ever written** — and a second turn produces a
`history/{checkpoint_id}.json` entry. Killing the client mid-turn leaves **no
checkpoint written after the disconnect** (ABANDON verified).

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

| | |
|---|---|
| **Reference §** | §12 · §15 (routing) · §38 (escalation) · **S-F01** |
| **Touches** | `core/graph.py` (rewrite) |
| **Precondition** | 4.2 |
| **Verify** | `pytest` |

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

**Done when:** a test asserts the parent graph has five phase subgraph nodes
plus escalation, that it compiles **with** checkpointer and store, and that each
subgraph compiles with neither.

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

| | |
|---|---|
| **Reference §** | §12 · §13 |
| **Touches** | `phases/{measure,analyse,improve,control}/graph.py`, `nodes.py` |
| **Precondition** | 4.3 |
| **Verify** | `pytest` |

Same five-node structure, built from the parameterised builder. **No subgraph
imports another subgraph's nodes** (§12).

**Done when:** all five compile with identical node-name sets, asserted in one
parameterised test.

---

# Part 4 — Stage 5: Retrieval and tools

---

## Step 5.1 — Retrieval failure semantics

| | |
|---|---|
| **Reference §** | §27 |
| **Touches** | `knowledge/retriever.py` |
| **Precondition** | 4.4 |
| **Verify** | `pytest` |

**Partly done already** — Appendix E records that `knowledge/retriever.py`
already carries the correct `phase_relevance` filter and `fields=` declaration.
This step completes the failure semantics: `[]` only when the search ran and
matched nothing; `KnowledgeSearchError` when it failed.

**Never wrap a retrieval call in a bare `except Exception` that returns `[]`** —
that is what hid the `phase` filter bug, by reporting a broken index as a silent
corpus (§27).

**Done when:** tests show a forced Azure failure raises `KnowledgeSearchError`
with `severity="permanent"` on a 4xx, and that a genuine no-match returns `[]`.

---

## Step 5.2 — Three `rag_lookup_*` tools with multi-query + RRF

| | |
|---|---|
| **Reference §** | §24 · §25 · §23 (index field names) |
| **Touches** | `knowledge/tools.py` (rewrite) · `knowledge/fusion.py` (new) |
| **Precondition** | 5.1 |
| **Verify** | `live-run` |

**The retired tool names are `search_improve_knowledge`,
`search_improve_cases` and `search_improve_evidence`** — corrected in CLAUDE.md
§5.1 and the reference's Appendix D.1 on 2026-08-21. **`grep-absence` must target those
three strings.**

**Only the tool layer is retired.** `knowledge/retriever.py`'s
`search_knowledge` / `search_cases` / `search_evidence` functions keep their
names — §27 depends on them. **Do not grep-absence `search_evidence`**; it is
supposed to survive.

**The four cross-agent tools stay, unbound** — `search_resolve_cases`,
`search_resolve_knowledge`, `search_resolve_evidence`, `search_flow_vsm`.
Ratified as a distinct third category in **Reference §29.4** (2026-08-21,
`docs/DECISIONS.md` §Q1). **Do not delete them and do not bind them to the
executor in this step.** Binding one is an amendment, and §29.4 names three
rules that bind first — §27 compliance among them.

**Blocked partially by 9.1:** until the reindex lands,
`rag_lookup_evidence` takes **no** `order_by` and no `phase` filter, and
`rag_lookup_case_history` must use `embedding`, not `content_vector` (§23).
**Write against the live schema** (CLAUDE.md §7.2, §7.3).

**Done when:** a live query through `rag_lookup_methodology` returns documents
whose `phase_relevance` is the requested phase or `general`, and the fusion
module's RRF is unit-tested at k=60.

---

## Step 5.3 — The 20 computation tools

| | |
|---|---|
| **Reference §** | §30 · §31 |
| **Touches** | `knowledge/computation.py` (new) · `knowledge/tool_args.py` (new) |
| **Precondition** | 5.2 |
| **Verify** | `pytest` |

**All 20 are pure functions** — no LLM call, deterministic, unit-tested (§30).
**Each is a separate named tool**; parameterised grouping is BANNED.

**Done when:** 20 named tools exist, each with an `args_schema=`, and a test
suite covers each with a known-answer case.

---

## Step 5.4 — Per-phase tool binding

| | |
|---|---|
| **Reference §** | §30 |
| **Touches** | `knowledge/computation.py` (`COMPUTATION_TOOLS_BY_PHASE`) |
| **Precondition** | 5.3 |
| **Verify** | `pytest` |

**Done when:** a test asserts per-phase totals 8 / 15 / 12 / 8 / 12 and that no
phase exceeds 16.

---

# Part 5 — Stage 6: The coaching agent

---

## Step 6.1 — Planner / Executor split

| | |
|---|---|
| **Reference §** | §17 · §20 (`CoachingPlan`) |
| **Precondition** | 5.4 |
| **Verify** | `trace-check` |

**Never fuse them** (§17). The planner produces a typed `CoachingPlan` via
structured output and never dispatches to tools; the executor consumes it and
never decides strategy.

**Done when:** a LangSmith trace for one turn shows a `planner` span followed by
an `executor` span, with the plan visible as the planner's output.

---

## Step 6.2 — `create_agent` executor with `CoachingResponse`

| | |
|---|---|
| **Reference §** | §18 · §20 |
| **Precondition** | 6.1 |
| **Verify** | `live-run` |

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

**Done when:** one turn returns `result["structured_response"]` as a
`CoachingResponse` and the coaching prose is still present in `messages`.

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

| | |
|---|---|
| **Reference §** | §19.1 (state injection) · §19.2 (skills) · §19.3 (summarization) |
| **Precondition** | 6.2 |
| **Verify** | `trace-check` |

**`BeforeModelStateInjection` MUST be first, on `before_agent`** — not
`before_model`, which re-injects the same project facts on every model call
within a turn (§19.1).

---

## Step 6.4 — Retry middleware, positions 4–5 · and the factory's hardcoded retry

| | |
|---|---|
| **Reference §** | §19.4 · §19.5 · §21 |
| **Touches** | `phases/{phase}/graph.py` · **`core/llm.py`** |
| **Precondition** | 6.3 |
| **Verify** | `grep-absence` |

```python
ModelRetryMiddleware(max_retries=2),                        # wrap_model_call
ToolRetryMiddleware(max_retries=2, on_failure="continue"),  # wrap_tool_call
```

> **`max_retries`, not `retries`.** `retries=` does not exist and raises at
> construction. This exact keyword sat in the canonical stack undetected from
> adoption until 2026-08-21 (`BIBLE_VERIFICATION_LOG.md` C-1). (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

**This step also removes `max_retries=3` from the `AzureChatOpenAI`
constructor in `core/llm.py`**, deferred from step 2.7. **Sequenced here
deliberately, not standalone:** the hand-rolled retry is only safe to remove
once the middleware that replaces it exists, and removing it earlier would
leave a window with no retry at all. CLAUDE.md §8.7 bans hand-written retry
plumbing — that ban only becomes satisfiable at this step.

**Done when:** `grep -rn "max_retries=3" backend/core/llm.py` returns zero
hits, and both middlewares are present in the stack.

---

## Step 6.5 — Middleware positions 6–8

| | |
|---|---|
| **Reference §** | §19.6 (contradiction) · §19.7 (coherence) · §19.8 (grader) |
| **Precondition** | 6.4 |
| **Verify** | `pytest` |

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

| | |
|---|---|
| **Reference §** | §22 |
| **Touches** | `core/prompts.py` (rewrite) |
| **Precondition** | 6.5 |
| **Verify** | `grep-absence` |

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

**Done when:** those three v1 constant families return zero grep hits, every
`{PHASE}_COACH_PROMPT` contains the memory-hierarchy block, and all five
SKILL.md files carry the contradiction-check instruction.

---

# Part 6 — Stage 7: Validation and gates

---

## Step 7.1 — `DMAICGateValidator` and Layer 2b

| | |
|---|---|
| **Reference §** | §34 · §35 |
| **Touches** | `validation/gate_validator.py`, `validation/schemas.py` (new) |
| **Precondition** | 6.6 |
| **Verify** | `pytest` |

**`DMAICGateValidator` is the one permitted class exception** — a namespace of
`@staticmethod` deterministic checks holding no state (§54).

---

## Step 7.2 — Layers 2c and 2d, and the `validation_stack` node

| | |
|---|---|
| **Reference §** | §34 · §36 |
| **Precondition** | 7.1 |
| **Verify** | `pytest` |

**The cap is 3, SHARED across all four layers**, with accumulated
`validator_feedback` — not three per layer (§34).

**Layer 2d is NOT `DMAICGraderMiddleware`** (§36). Two graders; confusing them
is a violation.

---

## Step 7.3 — The nine-step HITL gate

| | |
|---|---|
| **Reference §** | §33 · §33.1 · §33.2 |
| **Precondition** | 7.2 |
| **Verify** | `manual-UI` |

**`gate_apply_node` writes the gate document TWICE** — to the store and to
`PhaseState.final` (§33.2). Both are required; a crash between the store write
and the checkpoint commit would otherwise leave the two disagreeing.

**The checkpoint commits only after Belt approval** (§33.3).

**Done when:** Vassilis passes the Define gate on `IMPR-2026-E9D` in the
browser: the interrupt presents validated fields, an edit is accepted, approval
writes `store/projects/IMPR-2026-E9D/artifacts/define.json`, and the phase
advances to Measure.

---

## Step 7.4 — Two tiers and the `warning` verdict

| | |
|---|---|
| **Reference §** | §35 |
| **Precondition** | 7.3 |
| **Verify** | `pytest` |

**A gate MAY pass with warnings. A gate may NEVER pass with failures.** Only
Tier 1 criteria may produce `fail`. A Tier 2 gap the Belt proceeds past MUST be
recorded in `acknowledged_gaps` (§35).

---

## Step 7.5 — Escalation

| | |
|---|---|
| **Reference §** | §38 |
| **Touches** | `escalate.py` (rewrite) |
| **Precondition** | 7.4 |
| **Verify** | `pytest` |

---

# Part 7 — Stage 8: Reliability

---

## Step 8.1 — Structured errors

| | |
|---|---|
| **Reference §** | §48 |
| **Touches** | `core/errors.py` |
| **Precondition** | 7.5 |
| **Verify** | `pytest` |

`AgentImproveError` already exists at `core/errors.py:15`. This step aligns it
with §48's six fields and makes `severity` / `retry_recommendation` actually
drive the breaker and the fallback chain.

---

## Step 8.2 — Per-node timeouts and compensating actions

| | |
|---|---|
| **Reference §** | §45 |
| **Precondition** | 8.1 · **gate: LangGraph ≥1.2.6** · **requires async nodes (2.5)** |
| **Verify** | `pytest` |

`TimeoutPolicy(run_timeout=45)` on every phase executor node; `error_handler=`
on **every node with external writes** (§45). Consider `set_node_defaults` for
the graph-wide case — but note `cache_policy` and `error_handler` defaults apply
to regular nodes only, and a handler must never catch itself (§45).

**Retries run BEFORE the handler.** When a node raises — including
`NodeTimeoutError` — the retry policy decides first and `error_handler` runs
only after retries are exhausted (§45).

**Hand-written Saga orchestrators are BANNED** — this is the native
replacement, and it is what the drift hook's `pattern-4-custom-saga` guards.

---

## Step 8.3 — Circuit breakers and the fallback chain

| | |
|---|---|
| **Reference §** | §46 |
| **Touches** | `core/reliability.py` (new) |
| **Precondition** | 8.2 |
| **Verify** | `pytest` |

**Three-state, two instances.** Two-state breakers are not permitted — this is
a long-running service and must recover without a restart (§46).

Levels 1, 2 and 4 of the chain land here. **Level 3 (cache) is step 8.4 and is
BLOCKED.**

---

## Step 8.4 — Level 3 response cache · **BLOCKED**

| | |
|---|---|
| **Reference §** | §46 |
| **Blocker** | **Azure Cache for Redis is not provisioned** |

Session-scoped, never global. Invalidation follows source volatility, and **a
gate approval must invalidate the affected entries** (§46).

**Do not start until the resource exists.** Steps 8.5 onward do not depend on
it; the chain degrades from Level 2 straight to Level 4 in the meantime, which
is correct behaviour, not a bug.

---

## Step 8.5 — Graceful shutdown · **GATED**

| | |
|---|---|
| **Reference §** | §45 |
| **Gate** | **`RunControl.request_drain()` is UNCONFIRMED — MAY NOT EXIST** |

**The requirement is ratified: a deployment rollout must not kill mid-coaching
sessions.** The mechanism is not.

**This step must not be written until the API is confirmed** against a real
release or the LangGraph source. Confirmation means the symbol found in the
installed package, in source at a named version, or in the reference with a
version stamp — **not a blog post and not a recollection** (§45).

**If confirmation fails, this step is rewritten as a real fallback drain
design**, not re-cited to another plausible API name. Reference §45 names the
candidates: a readiness probe that fails while in-flight turns complete, or a
shutdown hook that stops accepting new `ainvoke` calls and awaits the current
node.

---

# Part 8 — Stage 9: Azure schema changes

---

## Step 9.0 — Knowledge-index rebuild · **DONE out-of-band (commit `871637f`, 2026-08-25)**

| | |
|---|---|
| **Reference §** | §23 · §23.1 (corpus, classification) |
| **Touches** | `improve_knowledge_index` → `improve_knowledge_index_v3` · `scripts/ingest_knowledge.py` |
| **Verify** | `azure-query` — DONE |

**Not in the original spine; executed ahead of sequence and recorded here for
continuity.** Rebuilt the methodology corpus: BB eBook only (8D removed as
cross-framework contamination; tools-suite sheets removed as thin/redundant);
pdfplumber extraction fixing cid/footer/%-bullet garble; **LLM phase
classification at ingest** (operational-model, temp 0.0, six-label closed set)
replacing keyword `detect_phase`; text-embedding-3-large / 3072d preserved;
per-page 1200/150 chunking preserved.

**Live state:** `improve_knowledge_index_v3` (1,184 docs, 259 `general`) is LIVE
via `.env` (local only — reversible one-line rollback to
`improve_knowledge_index`, kept intact). §23.1 doc counts re-synced in the
commit.

**Interaction with Step 9.1:** this rebuild touched `improve_knowledge_index`
only. Step 9.1's reindex targets `improve_evidence_index` and
`improve_case_index` — **different indexes, still outstanding.** 9.1 is
unaffected and unchanged.

**Residual (WATCH register):** CLAUDE.md §7.2 still states "218 carry
`general`" — now 259 — pending a §0.x rule amendment (WATCH 3/8).

**Updates Step 5.1's premise:** 5.1 says "retriever.py already carries the
correct `phase_relevance` filter." Still true, but the *tags it filters on* are
now LLM-generated, not keyword. The retriever code is unchanged; the corpus
underneath it is rebuilt.

---

## Step 9.1 — The batched reindex · **EXTERNAL**

| | |
|---|---|
| **Reference §** | §23.2 · §23.3 · §23.5 |
| **Touches** | Azure AI Search — `improve_evidence_index`, `improve_case_index` |
| **Precondition** | 5.2 |
| **Verify** | `azure-query` |

**Both changes are RATIFIED and NOT YET APPLIED. Batch them** so the corpus
rebuilds once (§23.3).

| Index | Change |
|---|---|
| `improve_evidence_index` | Add `phase` (from `metadata.upload_phase`) and `uploaded_at` (from `metadata.timestamp`), both top-level, both **server-set** |
| `improve_case_index` | Rename `embedding` → `content_vector`. Delete + recreate — the index holds 0 documents, so no data migration |

**Normalise the HNSW profile name while the index is being recreated.**
`improve_case_index` uses `improve-vector-profile` where the other two use
`default` — safe by construction, but the opportunity to fix it does not recur
cheaply (§23.3).

**Done when:** `azure-query` confirms `phase` and `uploaded_at` are filterable
/ sortable on `improve_evidence_index`, `content_vector` exists on
`improve_case_index` at 3072 dimensions, and both re-ingest cleanly.

**Then unblock:** `rag_lookup_evidence` gains `order_by=["uploaded_at desc"]`
and the optional default-off `phase` filter; `rag_lookup_case_history` switches
to `content_vector`. **Update CLAUDE.md §7.2's table in the same commit** — it
says so explicitly.

---

# Part 9 — Stage 10: API and UI

---

## Step 10.1 — `/ask/stream` SSE

| | |
|---|---|
| **Reference §** | §49 |
| **Precondition** | 7.5 |
| **Verify** | `manual-UI` |

No streaming endpoint exists today. **Requirement 1 of §47 binds here** — the
handler shape must be deliberate, and streaming is the shape §47 prefers.

---

## Step 10.2 — The live gate document, conflict panel, and tier bars

| | |
|---|---|
| **Reference §** | §50 · §43.4 |
| **Touches** | `ui/index.html` |
| **Precondition** | 10.1 |
| **Verify** | `manual-UI` |

Three §50 surfaces: the live gate document updating on every capture; the
conflict-resolution panel, which **must surface which downstream phases become
provisional *before* the Belt confirms**; and **separate Tier 1 / Tier 2
progress bars, never one blended count** — a Belt at 6/6 required and 0/5
recommended can pass the gate, and a blended 55% implies otherwise.

---

# Part 10 — Stage 11: Cleanup and governance

---

## Step 11.1 — Delete v1

| | |
|---|---|
| **Reference §** | §54 · Appendix D |
| **Verify** | `grep-absence` |

Delete `ImproveGraphState`, the five `orchestrate.py` files, the five v1
`analyse.py` stubs, and every retired name in Appendix D.1.

> **⚑ This is where the v1 Define vocabulary dies (ruled 2026-08-28, Route A).**
> The v1 Define field names were carried unmigrated to this point on purpose —
> `orchestrate.py`, `EXTRACTION_DEFINE`'s Define block, the three cross-phase
> briefs, Measure's metric seeding, `gateway/routes.py:433`, `upload/agent.py`
> and the 78 `ui/index.html` sites. **The UI half is step 10.2's rebuild, not
> this step** — check it has landed before deleting the backend writers, or the
> workspace renders blank panels with no error (the failure step 3.4 names).

**Done when:** every name in Appendix D.1 returns zero grep hits in
`backend/`.

---

## Step 11.2 — Governance close-out

| | |
|---|---|
| **Reference §** | §55 |
| **Verify** | `pytest` |

Re-check that `deprecated_patterns.yaml`'s four CLAUDE.md citations still
resolve, that the path exclusion on `agent-improve/**/*.md` is still correct
now that the documents are stable, and that the session-start hook's step
parsing still matches this document's format.

---

# Appendices

---

## Appendix A — Traceability matrix

**Every step maps to the reference section that specifies it.** A step with no
reference section is not a step — it is an undocumented decision.

| Step | Reference § | Verify |
|---|---|---|
| 2.3 | §53, §16 | `import-check` |
| 2.4 | §12 | `grep-absence` |
| 2.5 | §14, §49 | `live-run` |
| 2.6 | §21 | `grep-absence` |
| 2.7 | §21, §54 | `pytest` |
| 3.1 | §5, §6, §7 | `import-check` |
| 3.2 | §9, §10 | `live-run` |
| 3.3 | §9 | `pytest` |
| 3.4 | §7, §40, §41, §53.1 | `manual-UI` |
| 3.5 | §54, §10, §49 | `live-run` |
| 4.1 | §12, §13, §14 | `import-check` |
| 4.2 | §16, §47, §49, §8 | `azure-query` |
| 4.3 | §12, §15 | `pytest` |
| 4.4 | §12, §13 | `pytest` |
| 5.1 | §27 | `pytest` |
| 5.2 | §24, §25, §23 | `live-run` |
| 5.3 | §30, §31 | `pytest` |
| 5.4 | §30 | `pytest` |
| 6.1 | §17, §20 | `trace-check` |
| 6.2 | §18, §20 | `live-run` |
| 6.3 | §19.1–§19.3 | `trace-check` |
| 6.4 | §19.4, §19.5, §21 | `grep-absence` |
| 6.5 | §19.6–§19.8 | `pytest` |
| 6.6 | §22 | `grep-absence` |
| 7.1 | §34, §35 | `pytest` |
| 7.2 | §34, §36 | `pytest` |
| 7.3 | §33 | `manual-UI` |
| 7.4 | §35 | `pytest` |
| 7.5 | §38 | `pytest` |
| 8.1 | §48 | `pytest` |
| 8.2 | §45 | `pytest` |
| 8.3 | §46 | `pytest` |
| 8.4 | §46 | **BLOCKED** |
| 8.5 | §45 | **GATED** |
| 9.1 | §23.2, §23.3, §23.5 | `azure-query` |
| 10.1 | §49 | `manual-UI` |
| 10.2 | §50, §43.4 | `manual-UI` |
| 11.1 | §54, App. D | `grep-absence` |
| 11.2 | §55 | `pytest` |

### Coverage check against Reference §53.1

| §53.1 line | Steps |
|---|---|
| Checkpointer wired (⚠ inert) | **4.2** closes it |
| `SupervisorState` / `PhaseState` split | 3.1 |
| `thread_id` + disconnect policy | 4.2 |
| Phase subgraphs with private state | 4.1, 4.3, 4.4 |
| `AzureBlobStore` | 3.2, 3.3 |
| Planner / executor nodes | 6.1 |
| Three `rag_lookup_*`, multi-query + RRF | 5.2 |
| 20 computation tools | 5.3, 5.4 |
| Eight-middleware stack | 6.3, 6.4, 6.5 |
| Four-layer validation + nine-step HITL | 7.1–7.4 |
| Reliability | 8.1–8.5 |

**Every §53.1 line has at least one step.** Steps 2.3–2.7, 9.1, 10.1–10.2 and
11.1–11.2 have no §53.1 line — they are prerequisites and close-out that the
reference's shape-level list does not enumerate.

---

## Appendix B — Disposition of the 55 backend files

> *Four shared modules have been added to the `New` row since this appendix was
> written — `phases/mappers_common.py` (3.3), `core/conversation.py` (4.2),
> `phases/nodes_common.py` and `phases/subgraph_common.py` (4.4). **None was in
> the original file plan**, and each was flagged at the step that added it
> rather than slipped in. They share one shape: the plan enumerates
> `phases/{phase}/…` five times over, and the five copies it implies are the
> thing that drifts. The count in this heading is the original 55 and is left
> as the historical figure.*

| Disposition | Files |
|---|---|
| **Rewrite** | `core/state.py` · `core/graph.py` · `core/llm.py` · `core/prompts.py` · `core/errors.py` · `gateway/routes.py` · `knowledge/tools.py` · `escalate.py` · `phases/{phase}/schema.py` × 5 · `phases/{phase}/validate.py` × 5 |
| **Delete** | `phases/{phase}/orchestrate.py` × 5 · `phases/{phase}/analyse.py` × 5 (v1 stubs) |
| **New** | `core/substate.py` · `core/store.py` · `core/reliability.py` · `core/diagrams.py` · `middleware/` × 5 · `validation/` × 4 · `knowledge/{computation,tool_args,fusion}.py` · `phases/{phase}/{graph,nodes,mappers}.py` × 15 · **`phases/mappers_common.py`** (added at 3.3 — the ten mappers differ only in which Store key they read and what `phase_context` holds; five copies of a twenty-key `PhaseState` skeleton is how field twenty-one lands in four of them, which is not hypothetical: it is what `fix(state)` 1d6f0ab corrected) · **`phases/nodes_common.py`** and **`phases/subgraph_common.py`** (added at 4.4 — §12 specifies ONE parameterised builder and §13's five nodes are identical across all five phases; five copies would make "identical node-name sets" a convention rather than a fact, and would put §47's key format and §34's do-not-validate-a-coaching-turn rule in five places to be kept in step by hand) · **`core/conversation.py`** (added at 4.2 — the case document's v1 turn dicts and `messages` need converting in both directions, by `gateway/routes.py` and by the phase nodes, and neither may import the other) |
| **Keep, minor edits** | `core/checkpointer.py` · `core/citations.py` · `core/config.py` · `knowledge/retriever.py` · `storage/blob.py` · `storage/models.py` · `gateway/schemas.py` |
| **Untouched** | `app.py` · `core/logging_setup.py` · `core/request_context.py` · `core/tracing.py` · `upload/classifier.py` · all `__init__.py` |
| **Edit only for `content_blocks` (2.6)** | `upload/agent.py` |

---

## Appendix C — The two parallel workstreams

**Neither is a step, and neither blocks one.** Both encode Black Belt domain
judgment and both inform the design as it lands (§53.1).

| Workstream | Reference § | Cadence |
|---|---|---|
| **The five SKILL.md files** | §32, §43 | Should lead step 6.6 — the coach prompts reference skill content. **Each must carry the contradiction-check instruction** (§37, `DECISIONS.md` §R1); without it step 6.5's middleware never fires |
| **The evaluation dataset** | §52 | Becomes load-bearing once 6.2 lands. Before that there is no coaching quality to measure |

**Open item on §52:** the >10% regression threshold is currently an asserted
number. Two Anthropic engineering posts added to Appendix C on 2026-08-21 bear
on it directly, one specifically on separating real regressions from
infrastructure noise. **Read both before finalising §52.**

---

## Appendix D — Step index

> **Machine-readable. The session-start hook parses this table.**
> Format is fixed: `| **Commit X.Y** | <title> | <status> |`. Do not reformat
> without updating `.claude/hooks/session-start-context.py` in the same commit
> (CLAUDE.md §0.2 applies to hooks that read documents, not only to rule
> numbers).

| Step | Title | Status |
|---|---|---|
| **Commit 2.3** | Dependency upgrade | done |
| **Commit 2.4** | `set_entry_point` → `add_edge(START, …)` | done |
| **Commit 2.5** | Async conversion | done |
| **Commit 2.6** | `content_blocks` · 20 sites | done |
| **Commit 2.7** | LLM factory · 6 roles → 11 | done |
| **Commit 3.1** | `SupervisorState` and `PhaseState` | done |
| **Commit 3.2** | `AzureBlobStore` | done |
| **Commit 3.3** | Boundary mappers | done |
| **Commit 3.4** | `{Phase}Output` schemas + validators + UI | done |
| **Commit 3.5** | `storage/blob.py` — class → functions, sync → aio | done |
| **Commit 4.1** | Define phase subgraph | done |
| **Commit 4.2** | `thread_id` + disconnect policy | done |
| **Commit 4.3** | Supervisor graph | done |
| **Commit 4.4** | Remaining four subgraphs | done |
| **Commit 5.1** | Retrieval failure semantics | pending |
| **Commit 5.2** | Three `rag_lookup_*` + RRF | pending |
| **Commit 5.3** | 20 computation tools | pending |
| **Commit 5.4** | Per-phase tool binding | pending |
| **Commit 6.1** | Planner / Executor split | pending |
| **Commit 6.2** | `create_agent` executor | pending |
| **Commit 6.3** | Middleware 1–3 | pending |
| **Commit 6.4** | Retry middleware 4–5 + factory retry removal | pending |
| **Commit 6.5** | Middleware 6–8 | pending |
| **Commit 6.6** | Prompts | pending |
| **Commit 7.1** | `DMAICGateValidator` + Layer 2b | pending |
| **Commit 7.2** | Layers 2c, 2d + `validation_stack` | pending |
| **Commit 7.3** | Nine-step HITL gate | pending |
| **Commit 7.4** | Two tiers + `warning` verdict | pending |
| **Commit 7.5** | Escalation | pending |
| **Commit 8.1** | Structured errors | pending |
| **Commit 8.2** | Timeouts + compensating actions | pending |
| **Commit 8.3** | Circuit breakers + fallback chain | pending |
| **Commit 8.4** | Level 3 cache | **BLOCKED** |
| **Commit 8.5** | Graceful shutdown | **GATED** |
| **Commit 9.0** | Knowledge-index rebuild | done |
| **Commit 9.1** | Azure batched reindex | pending |
| **Commit 10.1** | `/ask/stream` SSE | pending |
| **Commit 10.2** | Live gate document + conflict panel | pending |
| **Commit 11.1** | Delete v1 | pending |
| **Commit 11.2** | Governance close-out | pending |

> **✅ FIXED 2026-08-31 — this whole note is now historical.** `done` was added
> to `_UNAVAILABLE_STATUSES` in `.claude/hooks/session-start-context.py`, so a
> `done` row is never proposed as "next" and the trap described below cannot
> occur. Verified by reproduction: with the old set, `last=8.3` returned 9.0;
> with the new set it returns 9.1. **The note is kept, not deleted** — it states
> why the row is `done` while git history cannot show it, which is still true
> and still worth reading. What is no longer true is the "will still propose
> it" claim and the closing paragraph's reason for not fixing it.
>
> **⚠ Step 9.0 is `done` but the session-start hook will still propose it.**
> The hook skips only `BLOCKED` and `GATED` rows when picking "next", so a
> `done` row stays selectable. For every other done step that is harmless —
> git history advances `last` past it. **9.0 is the exception: it landed as
> `feat(knowledge): …` (`871637f`), not as a `refactor(arch-v2): commit 9.0`
> subject, so it will never appear in the hook's git-log scan and `last` can
> never advance past it on its own.**
>
> **Concretely: once 8.3 lands, the hook says "next 9.0"** — because 8.4 is
> BLOCKED and 8.5 GATED, so both are skipped and 9.0 becomes the lowest
> available row. It said 9.1 before this row was added. **Read Step 9.0's own
> heading — it says DONE out-of-band — and go to 9.1.**
>
> Left as a documented wrinkle rather than fixed, because the fix is a change
> to `.claude/hooks/session-start-context.py`'s `_UNAVAILABLE_STATUSES` (add
> `done`), and that is a hook-semantics change outside this reconciliation's
> scope. **The same trap applies to any future out-of-band step recorded
> here.**

---

## Appendix E — Questions raised by this procedure · BOTH RESOLVED

*Both were raised by writing this document and both were ruled on 2026-08-21,
before any step executed. Recorded here so the resolution is visible at the
point the question arose.*

**1 — The four cross-agent tools · RESOLVED.** `search_resolve_cases`,
`search_resolve_knowledge`, `search_resolve_evidence` and `search_flow_vsm` sat
between §29.1 (which sanctions read-only cross-agent tools) and §29.2 (whose
universal seven excludes them) — permitted and unaccounted for at once.

**Ruled: a distinct third category, RATIFIED as present-but-not-bound.** Added
as **Reference §29.4** through the §56 amendment procedure; decision record
`docs/DECISIONS.md` §Q1. Kept because the three `search_resolve_*` tools are
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

---

*End of document.*
