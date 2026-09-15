# Agent Improve — Refactoring Procedure
**AgentLean Platform · DMAIC Improvement Agent**
Version 1.7 · 2026-09-15
Status: **RATIFIED.** The ordered path from the v1 tree to the target in
`../ARCHITECTURE.md`.

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

`../ARCHITECTURE.md` describes **the target**. `CLAUDE.md` states **the rules**.
This document is **the route** — the ordered, verifiable sequence of commits
that gets the codebase from where it is to where the architecture says it
should be.

> **Corrected 2026-09-10.** These three lines named
> `../../AGENTIC_ARCHITECTURE_REFERENCE.md` as the target, which the founder
> ruling of **2026-08-27** superseded: `agent-improve/ARCHITECTURE.md` is the
> authoritative build target for every step. The correction was carried as an
> open item in `BUILD_TRACKER.md` — *"Procedure framing … Annotate"* — from
> 2026-08-27 until that file was deleted, and is applied here rather than moved
> to another list. **The root reference still binds at the platform level** and
> is what a back-port owes once Improve settles (§0.12); it is simply not what
> a step here is built against.

**It contains no design.** Every *what* and every *why* is a reference citation.
Where this document appears to state a design decision, the reference section named
in the step is authoritative and this document is a bug.

### The three-document division

| Document | Answers | Binding? |
|---|---|---|
| `agent-improve/CLAUDE.md` | **What the rule is** | **Yes** |
| `../ARCHITECTURE.md` | **How the system is shaped, and why** — the build target | **Yes** |
| This document | **In what order it gets built, and how each step is proved** | **Yes** |
| `../../AGENTIC_ARCHITECTURE_REFERENCE.md` | The platform-level shape, across all three agents | Yes, at platform level — **not what a step is built against** |

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

**Push after every commit that passes the guard rules** — the hooks already
gate quality, so an unpushed commit buys no safety and carries only risk:
`start.ps1` does `git reset --hard origin/main` and destroys it. Ruled
2026-09-10, after 6.12 landed with `main` ten commits ahead.

### The drift defences on the spine

*Moved here from `BUILD_TRACKER.md` when that file was deleted, 2026-09-10, and
corrected on the way: its copy still listed the retired rule 2 as binding. The
authority is the guard's own docstring —
`.claude/hooks/commit-msg-refactor-guard.py` — and this table is a reader's
summary of it.* Activate per clone with `git config core.hooksPath .githooks`.

| # | Rule |
|---|---|
| 1 | Subject is exactly `refactor(arch-v2): commit X.Y — <what changed>` |
| ~~2~~ | **Retired 2026-09-10.** Required `BUILD_TRACKER.md` and this file staged together. The tracker is gone and completion is read from git log, so a landing step moves no row in either. The number is deliberately not reused |
| 2b | `ARCHITECTURE_STATUS.md` is staged whenever the commit touches a path it tabulates. **Binds on EVERY commit**, not only spine commits |
| 3 | **mypy** over the changed Python against the pinned `.venv` — new errors block; existing ones are baselined in `.claude/config/mypy-baseline.txt` |
| 4 | **pytest** green |
| 5 | **`CONTINUITY.md`** is staged and its CURRENT BUILD STATUS block is current |

Fail-closed; every refusal prints `git commit --no-verify`. **The baseline is
DEBT and should only ever shrink** — never widen it to silence a new error.

**Rule 5 is normally satisfied for you.** `.githooks/pre-commit` regenerates the
status block from git log, Appendix D and the two version lines, then stages it.
That writer is fail-SOFT, because a hook that writes must never wedge a commit;
rule 5 behind it is fail-CLOSED and catches the cases where it did not run —
`core.hooksPath` unset in a fresh clone, a `--no-verify` retry leaving a stale
block staged, or a hand-edited block.

### Verification owed, and by which steps

**A step whose `Verify` names `live-run` can be complete in code and incomplete
in proof.** Appendix D's status column cannot say so — it carries only what git
cannot supply, and "the code landed" is exactly what git does supply. So the
list lives here.

| Step | Owed | State |
|---|---|---|
| 6.7 | `live-run` | Owed — never run |
| 6.9 | `live-run` | Owed — never run |
| 6.12 | `live-run` | Owed — never run |
| 6.13 | `live-run` | **Attempted and FAILED**, cause isolated to code 6.13 did not touch — see its section |
| 6.21 | `live-run` | **Owed. The code LANDED as `a1a0a5d` and the proof did not**, so git counts the step DONE and the board renders it in the DONE lane while its Done-when is unmet. Added 2026-09-15 — it should have been added the day 6.21 landed |

> **6.21 IS THE CASE THIS TABLE EXISTS FOR, AND IT WAS MISSING FROM IT.** The
> four rows above were added when their steps landed; 6.21's was not, for
> eleven days. **A step whose `Verify` names `live-run` is exactly the step
> most likely to land on its code half alone**, because the code half is the
> half a session can finish unaided — so the row recording the debt is owed
> at the SAME COMMIT as the code, never later. **G-63's fix (2026-09-15) did
> not close 6.21 and said so in its own body**; the evidence is still the
> founder's live turn.

**All five run through the same path.** The
executor loops on `rag_lookup_evidence` instead of calling the
`load_evidence_series` its own planner named, so no Define turn on
`IMPR-2026-ED8` completes (`ARCHITECTURE.md`'s gap register, and 6.13's
section). The first three were recorded as owed on the assumption that running
them was merely pending. **It is not pending; it is blocked**, and until
2026-09-10 none of the three said so.

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
| **EXTERNAL** | **Off the spine, for either of two reasons.** (a) Not a code change — an Azure or infrastructure operation. (b) **A code change that LANDED UNDER ANOTHER SUBJECT**, so the `refactor(arch-v2): commit X.Y` scan cannot see it — and then **the row cites the commit**. Widened 2026-09-15: 6.22 landed as `2e17f3f fix(tests):` and (a) alone would have been a false statement about it |
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
| **WATCH 7 — Define gate non-functional** | Define phase end-to-end runs | Step **4.1** lands (Define subgraph; executor stops delegating to v1 `orchestrate_define`, which still writes v1 names). Accepted interim, not a bug — a consequence of running 3.4's Define portion (commit `4701a09`) ahead of 4.1. `validate.py` reads v2 names; `orchestrate.py` writes v1 names; gate reads all Tier-1 fields missing. **Do not add a v1→v2 shim** (CLAUDE.md §17) — the migration happens naturally when 4.1 replaces the orchestrator's role. Cross-phase Define briefs in analyse/improve/control stay on v1 names until then, deliberately. **⚑ RULED 2026-08-28 — ROUTE A. This row is superseded on two points and left as written per annotate-don't-rewrite.** (a) It **clears at step 6.2**, not 4.1 — step 4.1's own prompt has the executor still delegating to `orchestrate_define`, so 4.1 cannot clear it. 6.2 gives the executor its own capture path via `response_format=CoachingResponse`. (b) `orchestrate.py` is **never migrated**; it and `EXTRACTION_DEFINE`'s Define block carry the v1 names unchanged and are **deleted at 11.1** (Appendix B). The Define gate is accepted as inert until 6.2 — nothing else is blocked. See `CONTINUITY.md` §6 and `docs/_archive/DECISIONS.md` Part X. |

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

## 0.4 Mutation proofs — restore from OUTSIDE the tree, never from HEAD

**A check nobody has watched fail is a check nobody has tested.** Every gate in
this repository is therefore proven by breaking it: defeat the matcher, watch
the suite go red, restore, watch it go green. That is the standing method and
it is not optional for a step whose Done-when names a check.

**THE RESTORE IS THE PART THAT GOES WRONG.**

> **Never restore a mutation with `git checkout -- <path>`.** It restores from
> **HEAD**, not from the state you were in. While the fix is uncommitted — which
> is exactly when mutation proofs are run — HEAD is the state *before* the fix,
> so the "restore" silently reverts the fix and leaves the mutation's premise
> gone. Every subsequent mutation then runs against the old code.

**Copy the file to a path outside the tree first, and restore from that copy.**
Outside the tree, because a baseline inside it is scratch and CLAUDE.md §0.32
clause 2 forbids that; the scratchpad is the place.

```bash
cp .claude/hooks/<hook>.py "$SCRATCH/hook.baseline.py"   # once, after the fix
# ... mutate, run, then:
cp "$SCRATCH/hook.baseline.py" .claude/hooks/<hook>.py   # restore, every time
```

**Read which test failed, never just the count.** A restore that reverted the
fix still produces `1 failed` — the same shape as a successful proof — while
failing a *different* test. The count is not the evidence; the test name is.
Finish by confirming the restored file still carries the change, by grep, and
that the suite is fully green.

**Twice now, and both times it produced a false result.** ARCHITECTURE.md
v1.49(D): disabling only `after_agent` left `aafter_agent` overriding, the
middleware still fired, and the new test passed — a mutation that did nothing,
read as proof. v1.58: a `git checkout --` restore reverted the uncommitted fix
instead of the mutation, and the next mutation reported a different test
failing that would have been recorded as a pass of a check never exercised.
**A mutation that does not do what you think produces a result that means
nothing**, and it looks identical to one that does.

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

**The `langchain-core` jump is the risk.** The resolved `langchain` requires
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
blocks, per §21 — which states why the raw `content` field must not be
index­ed or substring-parsed.

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
(§5). `core/substate.py` holds `PhaseState` — §6 / S-C02 is authoritative for the
field census, its categories and the copy-down rule. The v1 `ImproveGraphState` is deleted in step 11.1, not
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

## Step 3.4 — `{Phase}PhaseInput` → `{Phase}Output` schemas, with validators and UI

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

**The five requirements are §47's "Five requirements", and are not restated
here.** Read them there. **Ratified policy is ABANDON, not COMPLETE** (§47).

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

**Done when:** a test asserts per-phase totals **9 / 16 / 13 / 9 / 13** and that
no phase exceeds 16.

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

## Step 6.4 — Retry middleware, positions 4–5 · and the factory hardcoded-retry removal

| | |
|---|---|
| **Reference §** | §19.4 · §19.5 · §21 |
| **Touches** | `phases/nodes_common.py` (`_build_executor`) · **`core/llm.py`** |
| **Precondition** | 6.3 |
| **Verify** | `grep-absence` |

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

**Done when:** `grep -rn "max_retries=3" backend/core/llm.py` returns zero
hits, **the constructor carries an explicit `max_retries=0`** (absence is not
zero — it inherits the SDK default), and both middlewares are present in the
stack.

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

**Done when:** the three v1 constant families return zero grep hits **in live
v2 code**, every `{PHASE}_COACH_PROMPT` contains the memory-hierarchy block and
the anti-hallucination guards, and all five SKILL.md files carry the
contradiction-check instruction.

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

| | |
|---|---|
| **Reference §** | §16 · §26 · §58.18 S-F09 B1 |
| **Touches** | `phases/nodes_common.py`, `core/substate.py` (comment) |
| **Precondition** | 6.6, **and the CLAUDE.md §3.7 amendment landed first** |
| **Verify** | `pytest`, then `live-run` |

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

**Done when:** `COACH_RECURSION_LIMIT` returns zero grep hits, the executor
reads `remaining_steps` and branches on it, the hop count is enforced and
written to `step_log`, and **the Define and Measure opening turns that
see-sawed both coach rather than cap, with no prompt wording changed**.

> **⚑ The live half is owed, not done.** Blocked on Azure 429s on
> `operational-premium` in westeurope — the same AI2 blocker that cut AK3's
> measurement short. The unit suite pins both guards deterministically, so
> what is owed is end-to-end confirmation of the mechanism, not the mechanism.

---

## Step 6.8 — `phase_context` is read (WATCH 19)

| | |
|---|---|
| **Reference §** | §6 · §9 · §19.1 · §58 S-C02 · S-F10 |
| **Touches** | `middleware/state_injection.py`, `gateway/routes.py` (case creation), `phases/mappers_common.py` |
| **Precondition** | 6.7 |
| **Verify** | `trace-check` |

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

**Done when:** `POST /cases` writes the case record to the Store; a coach turn's
trace shows the composed `phase_context` in the injected block; and the Define
and Measure opening turns are re-run and re-recorded as the new baseline.

---

## Step 6.9 — The four missing SKILL.md files, and §32 conformance

| | |
|---|---|
| **Reference §** | §32 · §43 · §37 |
| **Touches** | `skills/measure/`, `skills/analyse/`, `skills/improve/`, `skills/control/` |
| **Precondition** | 6.8 |
| **Verify** | `pytest` |

**Not in the original spine — it was a parallel workstream with no scheduled
slot, which is how four of five went unwritten through all of Stage 6.** Only
Define's exists. `DMAICSkillsMiddleware` (§19.2) loads them, so four phases are
running progressive disclosure against nothing.

**Each must carry the contradiction-check instruction** (§37, `DECISIONS.md`
§R1) — step 6.5's middleware reads `contradiction_flag` and nothing else sets
it — **and the `CoachingResponse`-population instruction** (WATCH 9), without
which `explanation`/`example`/`prompt`/`progress` stay empty for that phase.

**Done when:** five SKILL.md files exist, each carrying both mandatory
instructions, and a test asserts the count and both instructions per file.

---

## Step 6.10 — `analyse_executor_node` — §26's planned multi-hop

| | |
|---|---|
| **Reference §** | §26 · §58.18 S-F09 |
| **Touches** | `phases/analyse/nodes.py` |
| **Precondition** | 6.9 · **blocked on G-05 and G-35** |
| **Verify** | `pytest` + `live-run` |

**The half of §26 that 6.7 did not build.** 6.7 built the hop CAP — the budget
and the off-ramp. This is the planned three-hop dependent retrieval chain
itself: S-F09's decomposition call, the hop loop templating each answer into
the next question, and the dedicated synthesis call at temperature 0.1–0.2.

**`hop_results` and `synthesis_output` are the evidence it is unbuilt.** Both
are declared on `PhaseState`, both are read by nothing, and S-F09 is the node
the spec names as their writer. They were found by the same declared-but-unread
sweep that found `phase_context`.

**B1's entry guard is already live** — 6.7's `REMAINING_STEPS_FLOOR` is exactly
that guard, and this step consumes it rather than reimplementing it.

> **⚠ `Hop` CANNOT EXPRESS A NON-METHODOLOGY TARGET, AND THAT IS A SCHEMA GAP
> RATHER THAN A PROHIBITION** (recorded 2026-09-08). `Hop` carries
> `hop_number` and `hop_question` — **no index or tool field** — and S-F09's
> reference implementation hardcodes `rag_lookup_methodology` in the loop. So a
> *planned* hop can only ever hit `improve_knowledge_index`.
>
> **§26 does not forbid the others.** Its opening defines multi-hop as *"what
> the executor's ReAct loop does when it makes several `rag_lookup_*` calls in
> one Belt turn"* — a glob over all three tools — and its three-query-type
> table is **excluding non-retrieval question types, not enumerating permitted
> indexes**: the table's own framing is *"three query types exist, and only the
> first is a retrieval problem"*, and two of its three Source cells are `The
> Belt` and `artifacts` already in state, which are not indexes at all.
>
> **Build this step as specified — methodology hops — and do not widen `Hop`
> here.** An evidence hop retrieves nothing useful until 6.11 makes tabular
> uploads parseable and indexable; widening the schema first would produce a
> planned hop against an index that has no document to find. Revisit after 6.11.

**Done when:** `analyse_executor_node` exists and is wired for
`retrieval_strategy == "multi_hop"`; `hop_results` and `synthesis_output` are
written into state and read by the coach call; a live Analyse turn shows three
dependent hops and one synthesis call in the trace.

---

## Step 6.11 — The upload path (G-36)

| | |
|---|---|
| **Reference §** | §29.1 · §6 · §10 · §23.2 · §65.4 S-F35 · §50 |
| **Touches** | `backend/upload/` (parsers, classifier), `gateway/routes.py`, `phases/mappers_common.py`, `storage/models.py`, **`ARCHITECTURE.md` — §49 / S-F34, S-C09 and S-C02** (Part AP5) |
| **Precondition** | **none.** Was `6.10`; 6.10 was marked ⛔ BLOCKED on 2026-09-08 and the cursor moved here, so a precondition on it would park the queue on an unresolvable step. **The dependency runs the other way** — AP4 records that widening `Hop` before 6.11 would produce a planned hop against an index holding no document to find |
| **Verify** | `live-run` + `azure-query` |

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

**Done when:** xlsx, csv, pdf and docx parse to columns / rows / types / ranges
deterministically; `PhaseState.uploads` is written with the §6 entry shape and
reaches a gate document; the case-record inventory carries the same set;
evidence and artefact route to different destinations; an unparseable file is
refused with a Belt-readable reason; `azure-query` confirms a parsed
spreadsheet is retrievable by `rag_lookup_evidence`; **`/upload` is named in
§49's endpoint table and `UploadRecord` in S-C09's model list**; and
**`ask_id` and `version` are declared on both the S-C02 upload entry shape and
`UploadRecord`, written `None`, and labelled reserved for 6.12 in the spec text
and the commit body**.

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

| | |
|---|---|
| **Reference §** | §29.1 · §32 · §43 · §50 · §6 / S-C02 · §23.2.1 · §60.7 S-F57 · §65.4 S-F35 |
| **Touches** | `backend/upload/` (asks), `core/substate.py`, `middleware/state_injection.py`, `phases/nodes_common.py`, `phases/mappers_common.py`, `gateway/routes.py`, `knowledge/tools.py`, `storage/models.py`, `storage/blob.py`, **Measure's SKILL.md** |
| **Precondition** | 6.11 · the two §56 amendments of `b90b9f2` |
| **Verify** | `live-run` |

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

**Done when — the original five:** a coach request for data is recorded with its
expected shape; an upload resolves to that ask; a shape mismatch produces a
coaching turn rather than a rejection; a second file against one ask is recorded
as a revision rather than a second upload; and a computation tool consumes a
bound upload without the coach retyping a figure.

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

| | |
|---|---|
| **Reference §** | §23.2 · §23.2.1 · §23.4 · §24 · §6 / S-C02 · S-C09 |
| **Touches** | Azure AI Search — `improve_evidence_index` · `gateway/routes.py` · `knowledge/retriever.py` · `knowledge/tools.py` |
| **Precondition** | 6.12 |
| **Verify** | `azure-query` + `live-run` |

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

**Done when:** `azure-query` confirms all seven fields are present and
filterable on `improve_evidence_index`; every pre-existing upload **that survives
the ruling-3 supersession sweep** carries a `role` — the §23.2.1 sentinel where
it predates 6.12 — a `kind` and a `content_digest` after the backfill, **the
document with no blob record included, backfilled from the index's own
`metadata`**; an artefact does not surface on an unfiltered evidence query (Part
AP2 ruling 3's second binding condition, and a test rather than an observation);
`rag_lookup_evidence` returns §24's structured record rather than rendered text;
and a `live-run` confirms a Belt asking what the to-be process is now reaches the
artefact.

---

## Step 6.14 — The SKILL.md shape pass: Define, Analyse, Improve, Control

| | |
|---|---|
| **Reference §** | §32 · §43 · §23.2.1 |
| **Touches** | `skills/dmaic-{define,analyse,improve,control}-phase/SKILL.md` · `backend/upload/asks.py` (`SHAPES_BY_PHASE`) · `ARCHITECTURE.md` §23.2.1 (the vocabulary extension) |
| **Precondition** | 6.12 |
| **Verify** | `pytest` |
| **Status** | **BLOCKED — awaiting founder domain content for the ask shapes** |

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

> ### ⛔ THIS SPECIFICATION IS INCOMPLETE BY DESIGN. It needs founder content before it can be built.
>
> **Everything below the "What the founder owes" heading is a SHAPE, not a
> plan.** The mechanism is settled — 6.12 built it for Measure and it works —
> but **the content is Black Belt domain judgment and inventing it would be the
> worst possible way to fill this section.** A wrong `expected_shape` does not
> fail loudly: it produces an ask the Belt cannot satisfy, or accepts a file
> that answers a different question, and either way the coach proceeds
> confidently. Written 2026-09-10 to stop the step existing as a title with
> nothing behind it (it had an Appendix D row and no section for two days).

### What this step is

**6.12 did Measure only, and said so.** `SHAPES_BY_PHASE` in
`backend/upload/asks.py` carries `MEASURE_SHAPES` and four empty dicts. The
planner derives an ask when it routes to a field with a declared shape, so a
phase with no declared shapes **opens no asks at all** — Define, Analyse,
Improve and Control currently cannot ask a Belt for data, and nothing says so
to the Belt or to the coach.

**Scheduled rather than assumed**, because four-fifths of a content pass
silently owed is this project's recurring failure and 6.12 chose not to repeat
it.

### The mechanism, which is NOT in question

Settled at 6.12 and unchanged here:

- A shape is keyed by **the coached field it answers**, and carries `role`,
  `columns`, `unit`, `period` and `rule`.
- **The ASK is keyed on `role`, never on field** (§6 / S-C02) — several fields
  may draw on one dataset, and per-field asks would open several requests for
  one upload.
- `role` must come from **§23.2.1's ratified vocabulary**. A role invented in
  code is a value no query filters on and no reviewer can see.
- **The SKILL.md prose and the declared shape must agree**, and that agreement
  is asserted, not assumed — `test_the_measure_skill_table_and_MEASURE_SHAPES_agree`
  is the pattern to copy per phase.

### What the founder owes, and it is the whole content of this step

**1 — WHICH COACHED FIELDS IN EACH OF THE FOUR PHASES ARE ANSWERED BY A FILE.**
Measure has three of ten (§39.2.2). The equivalent list for Define (§39.1.2),
Analyse (§39.3.2), Improve (§39.4.2) and Control (§39.5.2) is a judgment about
what a Belt actually brings to a coaching session, and it is not derivable from
the schemas — a field can be data-bearing and still be something the Belt
states rather than uploads.

**2 — FOR EACH SUCH FIELD, THE EXPECTED SHAPE.** `columns` as descriptions
rather than literal headers (a real export says `invoice_id`, not
`identifier`), `unit` — `None` where it comes from `metric_definitions`, since
the primary metric's unit is a project value and hardcoding it makes the
SKILL.md wrong for every project whose metric differs — `period`, and the
`rule` that makes a file usable rather than merely present. Measure's *"one row
per observation, never pre-aggregated"* is the model: **a rule that rules
something out.**

**3 — THE §23.2.1 VOCABULARY EXTENSION, ONCE, WITH COMPLETE INFORMATION.**
6.12 found the vocabulary has **no role for a measurement-system study** — GR&R
is not a capability study — and used `other evidence` as an honest placeholder
rather than inventing a row. The four-phase pass is where every missing role is
visible at the same time, which is why the extension was deferred to here
rather than taken four times. **Extending §23.2.1 is a governance event** (§56
amendment, and §23.5 requires it to land in `ARCHITECTURE.md` first).

> **What must NOT happen here:** shapes reverse-engineered from the schema field
> names, roles chosen to fit the existing vocabulary rather than the document,
> or a phase given an empty dict "for now". The third is how Measure-only became
> a four-phase debt in the first place.

### Done when

`SHAPES_BY_PHASE` carries a non-empty, founder-ratified shape set for all five
phases; each of the four SKILL.md files coaches those exact fields in
`field_index` order (§39.x.2) with the shape stated in its Uploads section;
**one test per phase asserts the SKILL.md table and the declared shapes agree**
— no model, no network; every `role` used resolves to a row in §23.2.1, with
any new row landed in `ARCHITECTURE.md` first as a §56 amendment; and
`other evidence` appears only where the founder ruled it the honest answer.

---

## Step 6.17 — The count-check: a written count against the list it describes

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

| | |
|---|---|
| **Reference §** | §55.1 · §6 / S-C02 · §29.2 |
| **Touches** | `backend/tests/test_document_counts.py` (new) |
| **Precondition** | none — **READY** |
| **Verify** | `pytest` |

### The defect this closes

**A caption that outlived its own list, three times, and every one was found by
editing the thing beside it rather than by any check.**

| # | Where | What it said | What was true |
|---|---|---|---|
| 1 | The tracker row (Part AP6) | a stale count | the list beneath it |
| 2 | The 6.9 row's badge | "1 of 5 SKILL.md files" | all five existed |
| 3 | `CLAUDE.md` §10.1's caption (Part AR3) | *"Nineteen author-populated fields — two identity, three plumbing, fourteen content — plus one engine-managed value, twenty declared"* | the list directly beneath carried **fifteen** content fields, and §0.17's own table said 21 / 22 |

Instance 3 is the one that names the class: **the file disagreed with itself
four hundred lines apart**, and had done since `rejection_feedback` landed at
2.2.23. **Nothing in this project verifies that a count written in prose matches
the list it describes** — and all three were in documents whose §55.1 rule is
that references resolve.

> **§55.1 is bidirectional for REFERENCES and silent on COUNTS.** *"Every gap
> marked inline has a row here, and every row here has an inline marker"* is
> checkable and checked. *"Twenty-one author-populated fields"* is a claim about
> a list two paragraphs down, and nothing looks.

> ### ⇒ THIS STEP ALSO OWNS **G-64** — assigned 2026-09-15
>
> **Appendix A has 59 rows against Appendix D's 70**, and the eleven it lacks
> are 6.22–6.31 and 9.2. **It is not that those steps are undocumented** —
> every one carries its own `| **Reference §** |` row, which is the row a
> reader of the step actually sees. **Appendix A RESTATES that row**, and the
> restatement is what fell behind.
>
> **It lands here because of the boundary this section draws.** Appendix A and
> the step sections are **both inside this document**, so the disagreement is
> a claim against the list in the same document — this step's subject exactly,
> and not `verify_built.py`'s, which compares a claim against the TREE.
>
> **The fix is not to type eleven rows.** That leaves the second copy in place
> and buys one commit of agreement. Appendix A becomes a projection of the
> step sections' own `Reference §` rows, or is asserted against them by set
> equality in both directions — and **that check already exists** as
> `verify_built.py::matrix_covers_appendix_d` (6.31). Generalise it; do not
> write a second one.

### Not the same check as `verify_built.py`, and the boundary is the point

`.claude/hooks/verify_built.py` (§55.2) compares a claim in `ARCHITECTURE.md`
against **the tree** — *are there really twenty computation tools?* **This step
compares a claim against the LIST IN THE SAME DOCUMENT** — *does the sentence
saying "twenty-one" sit above twenty-one rows?*

**Both failures have occurred and neither catches the other.** A caption can be
wrong while the tree is right (instance 3: the code had 21 fields, the prose
said 19), and the tree can drift while the prose stays internally consistent.

### What to assert

**Hand-written assertions, one per counted claim, in one test file. No model,
no network** — the AR3 class of check, and the same class as 6.12's
`test_the_measure_skill_table_and_MEASURE_SHAPES_agree`.

The two named in this step's Reference §, and the ones AR3 lists:

- **§6 / S-C02's author-populated sentence against S-C02's field-table rows**,
  and against `PHASE_STATE_AUTHOR_POPULATED_FIELDS` in `core/substate.py` —
  which already exists precisely so the count in §6 and the count in the code
  cannot drift apart silently, and is asserted by `test_state.py`. This step
  adds the third corner: the PROSE.
- **§29.2's universal count against the S-F entries that define those tools** —
  the count moved from seven to eight on 2026-09-09 and was carried through 17
  occurrences by hand.
- **`CLAUDE.md` §10.1's caption against the field list beneath it**, and
  §0.17's table against both.
- **§30's per-phase tool totals against `COMPUTATION_TOOLS_BY_PHASE`.**
- **§66's "N gaps identified, M closed, K open" against the register's rows** —
  that line has been corrected by hand at least twice.

> **A count with no list is out of scope.** This check compares a written figure
> to an enumeration in the same document. Where a figure describes the tree
> instead, it belongs in `verify_built.py`, and the two must not both claim it —
> a fact checked in two places is the condition the 2026-09-10 document collapse
> exists to remove.

### Done when

`pytest` carries one assertion per counted claim above; **each failure message
names the sentence and the list it disagrees with**, so a failure is actionable
without reading the test; a deliberate off-by-one introduced into any counted
sentence fails the suite (mutation-checked, per the 5.3 and 5.4 precedent); and
no assertion duplicates one `verify_built.py` already makes.

---


## Step 6.22 — The order-check: the middleware stack's ordering test observes execution (G-52)

| | |
|---|---|
| **Reference §** | §19 · §19.1 · §19.6 · §19.7 · §19.8 · G-52 |
| **Touches** | `backend/tests/test_middleware.py` · a new integration test |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus the new test failing when the declaration order is reversed |

### The defect this closes

**`test_the_declared_middleware_list_is_the_ratified_layering` asserts the rule
against itself.** It runs under the `stub_coach` fixture, which replaces
`create_agent` — so no graph is built, no hook fires, and the assertion reduces
to `reversed(declared) == [contradiction, coherence, grader]`. That is the
ratified order restated, not observed.

**The cost is measured, not hypothetical.** CLAUDE.md §8.1 carried the
declaration order backwards from step 6.5 until 2026-09-12, ARCHITECTURE.md §19
carried it backwards until v1.22, and the package docstring and this test's own
module docstring carried the false ordering sentence until `886b987`. The suite
was green for every one of those days. **A test that cannot fail for the reason
it exists is indistinguishable from no test**, and this is the second instance
of that shape in this repository — §55.2 records the first, eleven marker checks
that all passed against four wrong markers because every one counted a
population rather than pinning a value.

### What to build

An integration test that invokes the **real** compiled agent and records which
hooks fire in what sequence. The harness written on 2026-09-12 while correcting
§8.1 already does it and is the starting point:

- instrument each middleware's own hook at **class level, before the agent is
  built**, so LangChain's `m.__class__.after_agent is not
  AgentMiddleware.after_agent` discrimination is unchanged and every hook body
  still runs;
- collapse each hook's async twin with its sync name — the base class delegates,
  so an instrumented class reports both for one entry;
- assert `before_agent` fires 1 → 2 and `after_agent` fires 8 → 7 → 6.

**It must not need a live model.** The observed defect is in the graph
LangChain builds, which is decided at construction and needs no completion —
`GenericFakeChatModel` is enough, and G-53 means a live model is not reliably
available anyway. Keep the existing stubbed test: it pins the declaration list,
which is a different and still-useful property. **The new one pins what fires.**

### Done when

`pytest` is green; the new test is in `backend/tests/`; and a mutation the
DECLARED LIST cannot see makes the new test fail while the stubbed one passes.

> **⚑ THE DEMONSTRATION THIS STEP ORIGINALLY SPECIFIED DOES NOT HOLD, and that
> is recorded rather than quietly swapped.** It said *"reversing positions 6 and
> 8 makes the NEW test fail while the existing stubbed one still passes"*. Run
> on 2026-09-13: **both fail.** The stubbed test asserts
> `reversed(declared) == [contradiction, coherence, grader]`, so reversing the
> declaration breaks it too. The mutation is visible to both and separates
> nothing.
>
> **What separates them is a mutation that leaves the list intact.** Removing
> position 8's `after_agent` AND `aafter_agent` — the class stays in
> `middleware=[...]`, so the declared list is unchanged — gives:
>
> ```
> test_the_declared_middleware_list_is_the_ratified_layering   5 passed
> test_middleware_execution_order.py                           2 failed
> ```
>
> **And the first attempt at that mutation was itself wrong**: disabling only
> `after_agent` left `aafter_agent` overriding, the middleware still fired, and
> the new test passed — a green result that meant nothing. A mutation that does
> not do what you think produces a passing test that proves nothing, which is
> the same trap one layer down.
>
> **What the stubbed test genuinely cannot catch** is LangChain changing its
> composition semantics. It asserts our BELIEF about reversal rather than
> verifying it: if `after_*` began firing in declaration order, the stubbed test
> would still pass and the runtime would be wrong. That cannot be demonstrated
> by editing this repository, which is why the mutation above is the evidence
> offered instead.


## Step 6.23 — The source-method check: verification against the installed object, not the page (G-54)

| | |
|---|---|
| **Reference §** | §9 · §16.3 · §25 · §53 · §55.1 · G-54 |
| **Touches** | `docs/_archive/BIBLE_VERIFICATION_LOG.md` · possibly §9, §25, §53 if a verdict moves |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus each re-verified entry carrying the introspection that settles it |

### The defect this closes

**Every verdict in the verification log was reached by reading a page.** Four of
its five `Source` cells name `reference.langchain.com` or
`docs.langchain.com`; not one names an introspection of the installed package.
That is the method, not an oversight in one entry.

**C-3 is the proven instance and it is instructive rather than embarrassing.**
Its Source cell named a MODULE's API page while its Claim was about a CLASS's
member list. The page lists what the module exports; the verdict read that as
what the class exposes, stamped **CORRECTED**, and overwrote a statement that
had been right. It then propagated to CLAUDE.md §8.1 — *the machinery carried a
wrong verdict exactly as fast as it would have carried a right one*. Withdrawn
2026-09-12, ARCHITECTURE.md v1.35.

**What is still exposed.** C-1 (`retries=` vs `max_retries=`) and C-2 (`prompt=`
vs `system_prompt=`) happen to be pinned by
`test_retry_kwargs_against_the_installed_classes` and `test_executor.py`'s
signature assertions — **by accident of what those steps needed, not by
anything the log did**. S-1 is pinned by nothing: it asserts
`BaseStore.search()`'s parameter surface from two documentation pages, and §9's
ruling to keep `improve_case_index` on Azure AI Search already rests on the one
reason that survived that entry. If its surface has moved again, the decision
rests on less than §9 says it does.

### What to build

**1 — Re-verify each entry against the installed package.** One introspection
per claim, run against the pinned venv and recorded verbatim in the entry:
`inspect.signature()` for a parameter claim, `vars()` for a member-list claim,
`importlib.metadata.version()` for a version claim. **Never the page a second
time** — that is what produced the error.

> **THE COROLLARY, AND IT BOUNDS STEP 1: INTROSPECTION SETTLES MEMBERSHIP,
> NEVER ORDER OR BEHAVIOUR.** `vars()` and `inspect.signature()` answer *is this
> name there, and what does it take*. They are silent about *what happens
> first*, *what happens when this raises*, and *how these compose*.
>
> **An entry claiming an ORDER is settled by a runtime test, not a signature** —
> one that exercises the path and observes what happened. **Until such a test
> exists the entry is marked as resting on a page, not verified.** Marking it is
> a result; leaving it looking verified because the classes exist is the defect
> this step closes, one layer down.
>
> **E-2 is the worked example.** It claims retries decide first and
> `error_handler` runs only after they are exhausted. `RetryPolicy` exists and
> carries `max_attempts` — and none of that settles it. What would: a test that
> raises inside a node and counts attempts before the handler fires. E-2 is
> therefore the one entry in the log still marked as resting on a page.
>
> **§19's middleware order is the same shape settled the other way**, which is
> why G-52 and G-54 are one lesson from two ends. No `vars()` could establish
> that `after_*` fires innermost-first; `test_middleware_execution_order.py`
> invokes the real compiled graph and observes it.

**2 — Correct in place, never delete.** C-3's pattern: strike the withdrawn
text, state what is actually true, and say why the entry got it wrong. A
verification log that removes its own errors cannot be used to judge what its
other verdicts are worth.

**3 — Add a `Source method` column** to every entry's table, so the distinction
is visible at a glance and a future entry cannot omit it silently. Two values
to start: `introspection — <the expression>` and `documentation page — NOT
RE-CHECKED`. **The second is a finding, not a placeholder.**

**4 — If a verdict moves, follow it.** S-1's is the one that can: it feeds §9
and §25. A re-verification that changes a verdict and leaves the sections
citing it alone would be the same failure one layer down.

### Done when

Every entry in `BIBLE_VERIFICATION_LOG.md` carries a `Source method` cell; every
one whose method was a documentation page has been re-run against the installed
package with the expression recorded; any verdict that moved has been propagated
to the sections citing it; and `pytest` is green.


## Step 6.24 — The drift hook learns to read the documents (G-56)

| | |
|---|---|
| **Reference §** | §55 · §55.1 · §56 · G-56 |
| **Touches** | `.claude/hooks/fact-ownership-guard.py` (new) · `.claude/config/fact_owners.yaml` (new) · `.claude/settings.json` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus a test edit writing an owned value into a document being DENIED |

### The gap this closes

**`deprecated_patterns.yaml` excludes `agent-improve/*.md` and
`agent-improve/**/*.md`.** CLAUDE.md, ARCHITECTURE.md and everything under
`docs/` sit outside every pattern the drift hook enforces.

**The exclusion is correct and that is what makes this hard.** Architecture
markdown deliberately shows a superseded form beside its replacement — a
registry that guards code must not match that, or every correction that shows
its work would be blocked. So the documents are excluded for a good reason and
guarded by nothing as a result.

**The cost is measured, not hypothetical.** Every defect worked between
2026-09-12 and 2026-09-13 was in a document: §8.1's inverted ordering rule,
§7.3's tabled schema, §16.1's dependency blocker, §9's conceded reason, C-3's
and S-1's verdicts. Not one was in code, and not one could have been caught by
the mechanism that exists.

### What to build

**A hook that reads OWNERSHIP rather than patterns**, which is why it needs no
exclusion. `fact-ownership-guard.py` reads `.claude/config/fact_owners.yaml` —
the table stated under *Facts have one owner* in CLAUDE.md — and denies a write
that states an owned value in prose:

> this fact is owned by `<owner>` — cite it, do not restate it.

A pattern list has to name what is wrong. An ownership list names what is
*owned*, and everything else is free, so a document that quotes a superseded
form to correct it is untouched while a document that restates a field count is
denied.

**The registry's exclusion stays exactly as it is.** This adds a second hook on
the same event; it does not widen the first.

### Done when

A test edit writing an owned value — a field count, a version pin, a middleware
position — into a `.md` under `agent-improve/` is DENIED with its owner named;
an edit quoting a superseded form beside its replacement is ALLOWED;
`deprecated_patterns.yaml`'s exclusions are unchanged; and `pytest` is green.

## Step 6.25 — Scratch leaves the tree

| | |
|---|---|
| **Reference §** | §0.32 · §56.3 · §55.1 |
| **Touches** | `.gitignore` · `docs/_archive/audit-2026-07-03.md` (new) · `docs/_archive/HANDOVER_AGENT_IMPROVE.md` (new) · `docs/_archive/response-to-audit-2026-08-19.md` |
| **Precondition** | none — **READY** |
| **Verify** | `git status --porcelain` reports no untracked path inside the tree; every citation in the archive document resolves to a tracked path |

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

### Done when

`git status --porcelain` shows no untracked path inside the tree; both cited
files are tracked under `docs/_archive/` and their citations name the new
paths; the uncited files exist outside the tree and are not deleted;
`.gitignore` matches the directories that actually exist, proven with
`git check-ignore -v`; and `pytest` is green.

## Step 6.26 — The guard's tree rules get a test suite (G-57)

| | |
|---|---|
| **Reference §** | §0.32 · §56.3 · G-57 |
| **Touches** | `backend/tests/test_commit_guard_tree_rules.py` (new) |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus each rule failing when its own matcher is defeated |

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

### Done when

Every case blocks when it should and passes when it should; defeating a
matcher — emptying the scratch segment set, or pointing the register regex at a
pattern the table does not use — turns the suite red rather than leaving it
green; `pytest` is green; and G-57 is closed in §66 with the count updated.

## Step 6.27 — The watched-path contract has one owner (G-58)

| | |
|---|---|
| **Reference §** | §55.2 · §55.4 · G-58 · CLAUDE.md *Facts have one owner* |
| **Touches** | `backend/tests/test_commit_guard_tree_rules.py` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus BOTH mutation directions failing (procedure §0.4) |

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

### Done when

Both mutation directions fail:

| Mutate | Expect |
|---|---|
| add or remove a path in **§55.2** | the equality test fails |
| add or remove a path in **`STATUS_WATCHED`** | the equality test fails |

`pytest` green with neither mutation in place, and the restore verified per
§0.4 — from a baseline outside the tree, reading the test NAME rather than the
failure count.

## Step 6.28 — Fact-ownership moves to the commit gate (G-59, G-60)

| | |
|---|---|
| **Reference §** | §55.4 · §55.5 · G-59 · G-60 |
| **Touches** | `.claude/hooks/commit-msg-refactor-guard.py` · `.claude/settings.json` · `.claude/config/fact_owners.yaml` |
| **Precondition** | none for G-59 — **READY**. G-60's row needs a ruling first |
| **Verify** | `pytest`, plus a Bash-written restatement being caught that the `PreToolUse` guard misses |

### The gap this closes

**The guard runs on the path fewest edits take.** `fact-ownership-guard.py` is
registered on `PreToolUse` with matcher `Write|Edit|MultiEdit`, and `extract()`
reads `content` or `new_string`. **A Bash envelope carries neither.** In auto
mode Bash is the primary edit path, so a document restating an owned value lands
unchecked whenever the edit came through `sed`, a heredoc, or a script.

**Widening the matcher is the wrong fix and must not be done.** `extract()`
would return `""`, the guard would early-exit on `if not content`, and every
Bash call would pass — a check that cannot fail, recorded as coverage.

**Shell parsing cannot recover the content.** Measured across one session, files
were written six ways — heredoc Python, an external script, `sed -i`,
`printf >>`, `cp`, `git checkout` — and **four carry no content in the command
string at all**. Recovering it means predicting the effect of an arbitrary
program.

### What to build

**The same ownership logic, run at the commit gate over the staged governed
documents.** `_fact_owners.py` already separates derivation from the hook, so
this is a second caller rather than a reimplementation.

| | |
|---|---|
| Sound where parsing is not | the index holds the final content whatever wrote it |
| Complete where `PreToolUse` is not | it also catches a peer session's writes and hand edits |
| Cheaper | **2.52 s once per commit**, against a measured **~2.8 s per Bash call** |

**Admitted cost, stated rather than discovered later:** it catches the
restatement at commit rather than at write, so the author fixes it minutes
later instead of immediately. That is the trade §55.5 ratifies.

**Whether the `PreToolUse` registration stays is part of this step.** Keeping it
gives immediate feedback on the paths it does cover, at 2.52 s per governed
write; removing it leaves one enforcement point and one story. Decide it here
and record the reason — do not leave both running by default.

**G-60 rides along once ruled.** Search index schemas are the third unregistered
ownership class and the only one whose owner is a live Azure resource rather
than a parseable file. The ruling comes first; the registry row is one line
after it.

### Done when

A restatement of an owned value written **through Bash** into a governed
document is caught at commit; the same restatement through `Write` is caught by
whichever layer the step rules stays; `pytest` green; and the `PreToolUse`
registration's fate is recorded either way, with its reason.

## Step 6.29 — Search index schema ownership, ruled (G-60)

| | |
|---|---|
| **Reference §** | §55.4 · §7.3 · §23 · G-60 |
| **Touches** | `.claude/config/fact_owners.yaml` — one row, after the ruling |
| **Precondition** | none — **READY.** The work is the ruling |
| **Verify** | the row exists, or the class is recorded as deliberately unowned with its reason |

### Why this is a step and not a sentence

**It was a sentence — *“ruling first, engineering second”* — with no owner, no
deadline and no consequence.** That is the shape *live-run owed* had when four
of them stacked up over six days before anyone noticed they were blocked rather
than pending. A step renders on the board and the cursor reaches it. A sentence
in a register row does neither.

### The ruling to make

CLAUDE.md's *Facts have one owner* table names **eight** classes;
`fact_owners.yaml` registers **five**. G-56 covers two of the three missing —
gate tier splits and tool inventory. **This is the third**, and it is the
hardest, because the table gives its owner as *“the index definition, confirmed
by query”*: **a live Azure resource, not a file the guard can parse.** A derive
step would need a network call on the write path, which is not viable at the
measured cost of the existing derive (2.52 s).

| Candidate | What it costs |
|---|---|
| Cached schema snapshot + staleness rule | a second copy of a live fact — the thing ownership exists to prevent — bounded by how stale it may be |
| Rule the class OUT of mechanical ownership | honest, cheap, and leaves §7.3's *read the live definition* instruction as the whole control |

**Either is acceptable; leaving it undecided is not.** Whichever is chosen, the
row or the exclusion is written in the same commit as the ruling.

### Done when

`fact_owners.yaml` carries the row, **or** §55.4 records the class as
deliberately outside mechanical ownership with the reason — and the count of
registered owners against CLAUDE.md's eight classes is stated wherever that
table is, so the gap cannot silently reopen.

## Step 6.30 — A commit body's code claims carry a resolvable reference (G-62)

| | |
|---|---|
| **Reference §** | §56.3 · §20.5.1 · G-62 |
| **Touches** | `.claude/hooks/commit-msg-refactor-guard.py` · `backend/tests/test_commit_guard_*.py` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus a body asserting a code fact with no reference being refused, and the same body with a `path:line` passing |

### The ruling

**Founder ruling 2026-09-14, overriding §56.3's *ruled to stay untested*.** The
reasoning §56.3 gave is accepted and unchanged: **a gate cannot judge whether a
prose claim is TRUE.** The ruling is that it can gate the **SHAPE**.

> **A commit body that asserts a fact about code carries a git-resolvable
> reference — a path with a line range, or a commit sha. It never judges
> correctness.**

### The worked case

**v1.31(C)**, in this repository's own changelog:

> *“Rule 2b blocked the commit adding rule 6 — `git commit --only` still lets
> the pre-commit hook stage `docs/board.html`, and a watched path staged
> without this file is exactly what 2b exists to stop.”*

A claim about what the guard did, carrying **no reference**, and **wrong**: that
was the board being regenerated — the first false trigger — recorded as the rule
working. **It stood six weeks and cost `ef59aa8`.** A `path:line` beside it
would not have made it true. It would have made it checkable, by pointing the
next reader at `build_board.py`'s inputs instead of at a conclusion.

> **The example first offered for this step was wrong and is recorded as such.**
> It was *“the executor times out at 45s while nothing in the repository
> enforces any timeout”*. **The timeout is enforced**:
> `backend/phases/subgraph_common.py:73` sets `EXECUTOR_RUN_TIMEOUT = 45`, line
> 129 attaches `timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT)`, and
> `verify_built.py` re-runs it. What **step 8.2** owns and has not built is the
> bounded **request** timeout at the HTTP layer — a different timeout at a
> different layer. **A step whose purpose is to gate unresolvable citations must
> not open with one.**

### The known limit, recorded with the ruling

**It does not catch a citation that RESOLVES AND IS WRONG.** §55.2 cited
`build_board.py`'s four inputs accurately and drew a false conclusion from them;
a shape gate passes that unchanged. **State this in the rule's own message**, so
a passing commit is not read as a verified one — the same discipline
`check_step_or_gap` carries about numbers that resolve but do not fit.

### Done when

A body asserting a code fact with no reference is refused, naming the sentence;
the same body with `path:line` or a sha passes; a body asserting nothing about
code is untouched; the rule's message states the limit; `pytest` green; and both
mutation directions are shown per §0.4.

## Step 6.31 — The build matrix: one row per step, anchored to a symbol

| | |
|---|---|
| **Reference §** | §55.1 (governance rules) · §55.2 (the BUILT markers this replaces) · §56 (amendment procedure) · Appendix D · Appendix F |
| **Touches** | `docs/REFACTORING_PROCEDURE.md` (Appendix F, new) · `../ARCHITECTURE.md` (§55.2, and the marker migration that follows) · `.claude/hooks/verify_built.py` · `.claude/hooks/build_board.py` · `docs/CONTINUITY.md` |
| **Precondition** | **6.16** — the board is generated. Landed |
| **Verify** | `pytest` + `grep-absence` |
| **Status** | **RULED — founder 2026-09-15. Building** |

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

**Done when:** `Appendix F` exists with **one row per Appendix D step and no
others**, asserted as SET EQUALITY in both directions by a check in
`verify_built.py` that fails closed; every row carries an `Evidence` anchor
that the evaluator classifies as `PASS`, `EXTERNAL` or `DEPENDENCY`, and **zero
rows are `FAIL` or `MALFORMED`**; `verify_built.py` reports the matrix rows
alongside its 24 checks and exits non-zero on any disagreement; **each new
check has a recorded mutation proof per §0.4**, naming the test that went red;
`board.html` renders the `Order` column above the lanes, in lane colours;
`CONTINUITY.md`'s vertical is generated from `Order` inside the pre-commit
region and its hand-written four-item list — **wrong at HEAD, since 6.19 and
the §39.1 subsections both landed** — is gone; both §56 amendments are applied
with their version bumps; and `pytest` is green.

---

## Step 6.32 — An out-of-band landing gets the lane it earned (G-65)

| | |
|---|---|
| **Reference §** | §55.2 (the colour ruling) · Appendix D (the status column) · G-65 |
| **Touches** | `.claude/hooks/build_board.py` (`assign_lanes`) · `.claude/hooks/continuity_status.py` (`build_step_board`) · `backend/tests/` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus a mutation per §0.4 |

**Two finished steps render red on the board.** `assign_lanes` maps `EXTERNAL`,
`BLOCKED` and `GATED` alike to the BLOCKED lane, and §55.2 ratifies red as
*"cannot proceed"*. **9.0 has rendered that way since it landed** as
`feat(knowledge): 871637f`; **6.22 joined it on 2026-09-15** as `2e17f3f`. Both
are done, both are shown as blocked, on the one artefact a founder opens.

**It is NOT a status-token problem and widening the vocabulary again will not
fix it.** `EXTERNAL` is now true on its own terms for both of its cases
(reading conventions, 2026-09-15). **The lane is what is wrong**: a row whose
status cites a landing commit belongs in DONE, and the pointer already skips
DONE without needing the row to be unavailable.

**Done when:** a row whose status is `EXTERNAL` **and whose text cites a commit
sha that resolves in git** is assigned the DONE lane by `assign_lanes` and
counted DONE by `build_step_board`; 9.0 and 6.22 both render green; a row with
`EXTERNAL` and **no** resolvable sha still renders BLOCKED, because that is a
step genuinely off the spine; the landed COUNT is unchanged, since it is git
∩ Appendix D and these rows are not in git under a spine subject — **so the
count and the lanes may legitimately disagree, and the step states which is
which rather than reconciling them**; `pytest` green; mutation proof per §0.4.

---

## Step 6.16 — The board is generated, not written

| | |
|---|---|
| **Reference §** | §55.1 · §66 · Appendix D · `ARCHITECTURE_STATUS.md` |
| **Touches** | `docs/REFACTORING_PROCEDURE.md` (Appendix D's two new columns) · `docs/_archive/ARCHITECTURE_STATUS.md` (the closer token) · `.claude/hooks/build_board.py` **(new)** · `.githooks/pre-commit` · `.claude/hooks/commit-msg-refactor-guard.py` (watched paths) · `docs/board.html` **(generated)** |
| **Precondition** | none — **READY** |
| **Verify** | `grep-absence` + a commit that moves a step |

**Not in the original spine. Added 2026-09-10.** The refactor board is hand-made
in a chat and **goes stale the moment a commit lands**. Four captions in this
repository have already outlived the lists they describe (`DECISIONS.md` Part
AR3) — the tracker row that carried two descriptions, the 6.9 row's badge,
CLAUDE.md §10.1's field count, §29.3's universal count. **A hand-written board
is the fifth waiting to happen**, and it is the one a founder reads.

### 1 — Appendix D gains two columns

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

### 2 — `ARCHITECTURE_STATUS.md` gets a parseable closer — **read as: the BUILT markers do**

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

### 3 — The generator: `.claude/hooks/build_board.py`

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

### 4 — Lane assignment is DERIVED, never declared

| Lane | Rule |
|---|---|
| **BLOCKED** | its precondition is unmet, **or** an open §66 gap names it — the gap is the displayed reason |
| **BUILDING NOW** | the ▶ cursor |
| **READY** | preconditions met |
| **DONE** | Appendix D says `done` |
| **QUEUED** | everything else, in Appendix D order |

**Nothing anywhere declares a lane.** A declared lane is a fifth caption to keep
current; a derived one cannot disagree with the table it came from.

### 5 — Wired into `.githooks/pre-commit`, fail-SOFT

*(Carried from the 2026-09-10 scoping message, which truncated before restating
it — flagged rather than assumed.)*

Beside the `CONTINUITY.md` regeneration and under the same rule: **a hook that
writes must never wedge a commit.** A generator that raises leaves the previous
board in place and logs; it does not block the commit that would have refreshed
it.

### 6 — `docs/board.html` joins the watched paths

*(Carried from the same message.)*

`commit-msg-refactor-guard.py`'s rule 2b, so **a stale board is visible the same
way a stale `ARCHITECTURE_STATUS.md` is** — the board is a projection of
documents that move, and the guard is what notices when the projection did not
move with them.

**Done when:** a commit that moves a step in Appendix D produces a `board.html`
whose lane for that step has moved, **with no human edit anywhere**; every ☐ and
⚠ in container 1 shows a step number or `[none]`; and `grep-absence` confirms no
hand-written board survives.

---

## Step 6.18 — The executor ignores the tool its own planner names (G-49)

| | |
|---|---|
| **Reference §** | §17 (planner/executor split) · §26 · §58.18 S-F04 · S-F13 · §60.7 S-F57 |
| **Touches** | `phases/nodes_common.py` (the executor's tool binding and system prompt) · `backend/tests/test_executor.py` |
| **Precondition** | none — **READY**. It needs no unbuilt step; the failing path is fully built |
| **Verify** | `live-run`, then `pytest` — **in that order, and that is unusual** |

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

**Done when:** the reproduction is recorded and re-runnable; the cause is named
at one of the four layers above with the evidence that distinguishes it from
the other three; a test that fails on the unfixed build exists; the G-49
register entry carries the cause and its `live-run`-blocking claim is narrowed
to the steps it actually blocks; and **the `live-run` halves of 6.7, 6.12 and
6.13 are either run or explicitly re-scheduled with a date** — 6.9 per the
ruling taken above.

---

## Step 6.19 — `CoachingResponse` gains §50.1's four presentational fields (G-50)

| | |
|---|---|
| **Reference §** | §20 · §58.5 S-C05 · §50.1 · §32 · §43 |
| **Touches** | `core/substate.py` (`CoachingResponse`) · `phases/nodes_common.py` (the executor node's write path) · `gateway/schemas.py` · `backend/tests/test_executor.py` · the five `skills/dmaic-{phase}-phase/SKILL.md` only if their wording proves wrong |
| **Precondition** | none — **READY**. The schema is the whole of it; no unbuilt step gates it |
| **Verify** | `pytest` |

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

**Done when:** `CoachingResponse.model_fields` is exactly S-C05's eight; the
executor node writes all four from the turn and a test asserts each is
non-empty on a turn that coaches; `gateway/schemas.py` carries them to the API
boundary; `verify_built.py`'s `CoachingResponse fields (S-C05)` check expects
all eight and passes; the class docstring no longer claims to transcribe four;
and S-C05's BUILT marker plus §50.1's are both updated, with **G-50 closed in
§66 and the register counts moved**.

---

## Step 6.20 — The write paths: `computation_results`, `phase_metrics`, `field_index`

| | |
|---|---|
| **Reference §** | §7 · §39.2.7 · §39.3.7 · §39.4.7 · §39.5.7 · §58.2 S-C02 · §58.3 S-C03 |
| **Touches** | `phases/nodes_common.py` (the executor's artifacts write) · `core/substate.py` (comment only) · `ARCHITECTURE.md` §39.x.7 and S-C03 (the ruling) · `backend/tests/test_state.py` |
| **Precondition** | 6.19 — `fields_captured` must carry what the coach captured before the ledger around it is worth filling |
| **Verify** | `pytest`, then `manual-UI` on the Define slice |

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
22-field `PhaseState`** — which is what those tables always actually contained.
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

**Done when:** the executor writes `artifacts["computation_results"]` in §7's
five-key shape from the turn's computation-tool calls, and
`artifacts["phase_metrics"]` per §39.x.7, both asserted by tests that fail on
today's build; `field_index` advances through `DEFINE_FIELD_ORDER` and a test
pins that it reaches the last field; **a grader run on a turn that called a
computation tool finds it in `computation_results`** — the clause that makes
this step about the product rather than about a dict key; §39.x.7 describes
per-phase usage with all thirteen `{Phase}State` references gone and **Define's
own §39.1.7 written**; S-C03 amended; **G-19 closed**; and the Define gate
document, viewed in the browser, shows a computed figure that the coach did not
retype.

---

# Part 6 — Stage 7: Validation and gates

---

## Step 6.21 — The plan reaches the model (G-49's fix)

| | |
|---|---|
| **Reference §** | §17 (planner/executor split) · §26 · §19.1 / S-C11 (the injected block) · §58.18 S-F13 · §60.7 S-F57 |
| **Touches** | depends on the ruling below — `phases/nodes_common.py` in every case, `middleware/state_injection.py` for transport A, `backend/tests/test_executor.py` always |
| **Precondition** | **6.18** — the diagnosis. Written, not started |
| **Verify** | `live-run`, then `pytest` |
| **Status** | **RULED — option C, founder 2026-09-11. Building** |

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

**Done when:** `test_the_planners_instruction_reaches_the_model`'s
`xfail(strict=True)` marker is **removed** — it is strict precisely so this
cannot be skipped; the ruled transport is applied and its ratified section
amended under §56 with a version bump; a `live-run` of `POST /ask` on
**`IMPR-2026-0E5`** — a Belt question whose answer is in an uploaded file —
completes a turn in which `load_evidence_series` is called on the named blob
path and at least one upload is stamped `consumed_at`; `pytest` is green; and
the `live-run` halves of **6.7**, **6.12** and **6.13** are run in the same
pass, which is what discharges their verification debt (step 6.18's
re-schedule).

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

## Step 7.0 — The evaluation suite (§52)

| | |
|---|---|
| **Reference §** | §52 |
| **Touches** | `backend/evals/` (new) |
| **Precondition** | 6.10 |
| **Verify** | `pytest` |

**Not in the original spine.** §52 is ratified and there is no `evals/`
directory; CONTINUITY carried it as a parallel workstream, which is the same
no-scheduled-slot failure that lost §26 and §32.

**It is numbered 7.0 — before 7.1 — on §52's own sequencing rule**, not on
preference. §52: *"the suite becomes load-bearing when the coach, retrieval
tools and grader are wired — that is when output quality changes."* All three
are wired as of Stage 6. **Stage 7 is the first stage that changes coaching
behaviour**, so a suite built after it has no pre-change baseline to compare
against, and §52's >10% regression threshold stays *"asserted, not measured"*
exactly as it is today.

**The dataset is authored jointly, not generated** (§52) — coaching-quality
judgments are domain judgments, so this step needs founder time rather than
only build time.

> **⚠ The baseline must be taken AFTER 6.8.** Any dataset captured before
> `phase_context` reaches the coach records the behaviour of a coach missing
> its framing, which is why this sits behind 6.8 rather than in front of it.

**Done when:** `backend/evals/` holds the jointly-authored dataset, the suite
runs in CI, and the >10% regression threshold is measured against a baseline
captured on a post-6.8 coach.

---

## Step 7.1 — `DMAICGateValidator` and Layer 2b

| | |
|---|---|
| **Reference §** | §34 · §35 · **S-C26** |
| **Touches** | `validation/gate_validator.py`, `validation/schemas.py` (new) |
| **Precondition** | 6.7 |
| **Verify** | `pytest` |

**`DMAICGateValidator` is the one permitted class exception** — a namespace of
`@staticmethod` deterministic checks holding no state (§54).

---

> ### ⚠ FORWARD-NOTE, 2026-09-14 — two claims in this document are waiting on this step
>
> **ARCHITECTURE.md carries two “cannot disagree” claims that name
> `DMAICGateValidator`, and neither has ever been exercised**, because the
> component does not exist yet:
>
> | Where | The claim |
> |---|---|
> | L9624, S-F21 B2 | *“derive it the same way Layer 2b does, so the prompt and `DMAICGateValidator` cannot disagree”* |
> | L10193, S-C26 B4 | *“produce the same answer, derived the same way, so the prompt and the gate cannot disagree”* |
>
> **Both are the §55.2 shape**: a hazard named and argued away in prose, with
> nothing re-running the argument. §55.2's version of that cost `ef59aa8`.
>
> **This step discharges them or withdraws them — not both, and not neither.**
> Add to this step's Done-when: a test that derives the missing-field set BOTH
> ways — through the prompt path and through `DMAICGateValidator` — and asserts
> they agree, with a mutation showing it goes red when one side changes. If
> that test is not written here, **the two claims are withdrawn from
> ARCHITECTURE.md in this same commit** and replaced with what is actually
> true: two components intended to agree, with nothing checking that they do.
>
> `drift-check.py` currently reports `PENDING (owner not built, not checked):
> DMAICGateValidator` — so the checker knows it is absent and the prose does
> not. Raised by the full structure audit; §55.5 is the governing ruling.

## Step 7.2 — Layers 2c and 2d, and the `validation_stack` node

| | |
|---|---|
| **Reference §** | §34 · §36 · **S-C21 · S-C24 · S-F25 · S-F26** |
| **Precondition** | 7.1 |
| **Verify** | `pytest` |

**The cap is 3, SHARED across all four layers**, with accumulated
`validator_feedback` — not three per layer (§34).

**Layer 2d is NOT `DMAICGraderMiddleware`** (§36). Two graders; confusing them
is a violation.

---

> ### ⚠ ATTACHED 2026-09-14 — §15's safety argument is owned by this step (G-61)
>
> §15 states the supervisor has no conditional edge at a phase boundary, and
> argues: *“Why that is safe, rather than a simplification that ignores gate
> failure”* — because a phase subgraph reaches `END` only through `gate_apply`,
> and `gate_apply` runs only after Belt approval.
>
> **That is a graph property, so it is testable**: assert `END`'s only
> predecessor is `gate_apply`. It is attached here because this step builds the
> approval path the argument depends on — until the nine-step gate exists, the
> second half of the claim has nothing behind it. Add the assertion to this
> step's Done-when, or withdraw the argument and state what is actually true.

## Step 7.3 — The nine-step HITL gate

| | |
|---|---|
| **Reference §** | §33 · §33.1 · §33.2 · **§19.6** · **S-C25 · S-F27** |
| **Precondition** | 7.2 |
| **Verify** | `manual-UI` |

> ### ⛔ THIS STEP ALSO UN-GUARDS MIDDLEWARE POSITION 6. Added 2026-09-11.
>
> **It now owns TWO interrupts, not one.** §33's `gate_review` interrupt is
> this step's subject; the second arrived by founder ruling on 2026-09-11 and
> is easy to lose because it lives in another section's file.
>
> **`ContradictionDetectionMiddleware.after_agent` has a commented-out
> `interrupt(self._payload(flag))`.** It was guarded because a fired interrupt
> with no resume path does not pause a turn — **measured: it parks the CASE
> permanently**, every later turn returning nothing, checkpointed to Azure Blob
> so it survives a restart. **The routes this step builds — `/gate/approve`
> and `/gate/reject` — are exactly what makes it safe again.**
>
> **THREE CHECKS WILL FAIL WHEN YOU DO IT, AND ALL THREE SHOULD** — in
> `backend/tests/test_middleware.py` unless noted:
>
> | Check | Today | At 7.3 |
> |---|---|---|
> | `test_ContradictionDetectionMiddleware_does_not_call_interrupt` | 0 live call sites | **1** |
> | `test_position_6_is_GUARDED_and_does_not_park_the_case` | asserts suspension | **rewrite to assert RESUMPTION** |
> | `verify_built.py` — `interrupt() call sites (§33)` | 0 | **2** (this one **and** `gate_review`'s) |
>
> **None is optional and none may be silenced to land the step.** They exist
> so position 6 cannot be re-enabled by accident — and, equally, so that
> re-enabling it cannot be forgotten. `test_the_guarded_import_is_kept_for_7_3`
> keeps the `interrupt` import in place meanwhile, so restoring is one
> uncommented line rather than a line plus a re-import.
>
> **Un-guard only after the resume path can actually resume**, which for
> position 6 means a route accepting the two options S-C05 B2's payload
> offers: `update_approved_value` and `keep_approved_value`.

**`gate_apply_node` writes the gate document TWICE** — to the store and to
`PhaseState.final` (§33.2). Both are required; a crash between the store write
and the checkpoint commit would otherwise leave the two disagreeing.

**The checkpoint commits only after Belt approval** (§33.3).

**WATCH 13 lands here too** — §47 requirement 4's reconciliation sweep for
abandoned threads. It was deferred from 4.2 because *"it cannot be written
before `interrupt()` exists"*, and this is the step that creates `interrupt()`.
**A sweep and the thing it must not sweep are one design**; scheduling them
apart is how the sweep gets forgotten.

**Done when — CLAUSE 1 IS A GATE CONDITION, ADDED 2026-09-11 BY FOUNDER RULING:**

**1 — The guard on middleware position 6 is REMOVED and its `interrupt()` call
RESTORED, with a resume route PROVING it.** Proof is a live contradiction
raised and resumed end to end — a Belt revises a value approved in an earlier
phase, position 6 interrupts, and a route this step builds resumes the thread
with one of S-C05 B2's two options (`update_approved_value` /
`keep_approved_value`), after which **the next turn on that case is answered
normally.** That last part is the whole clause: the defect being closed is not
"the interrupt does not fire", it is **"a fired interrupt parks the case
forever"** — measured 2026-09-11 — so a restored call with no demonstrated
resume re-opens it rather than closing it. In the same commit:
`test_ContradictionDetectionMiddleware_does_not_call_interrupt` expects **1**,
`test_position_6_is_GUARDED_and_does_not_park_the_case` is rewritten to assert
resumption instead of suspension, and `verify_built.py`'s `interrupt() call
sites (§33)` expectation moves **0 → 2**. **Three checks will fail until this
clause is done, and none may be silenced to land the step.**

**2 — The gate itself.** Vassilis passes the Define gate **on a case the
registry shows in `define`** in the browser: the interrupt presents validated
fields, an edit is accepted, approval writes
`store/projects/{case_id}/artifacts/define.json`, and the phase advances to
Measure. The reconciliation sweep exists and excludes `interrupt()`-paused
threads.

> **Why clause 1 is here and not left to a comment.** The guard lives in
> `backend/middleware/contradiction.py` — §19.6's file, not §33's — and a
> commented-out line in another section's module is exactly the kind of thing
> that survives a step nobody thought to check it against. **A gate condition
> is read when the step is closed; a comment is read when someone opens the
> file.** The two tests above make it fail loudly in between.

> **⚠ Done-when corrected 2026-09-07 — it named `IMPR-2026-E9D`, which cannot
> run it.** E9D is complete (`current_phase="complete"`), so `/ask` returns 409
> by design and no gate can be passed on it. **This is the exact trap WATCH 22
> flagged for "any later step whose Verify method is `live-run` or
> `azure-query`"**, sitting unfixed in the next stage's own step. Check the
> registry for a case in a coachable phase at run time rather than hard-coding
> one — `IMPR-2026-0CB` is in `define` today, and a reset case is the other
> option §17's sequence needs.

---

## Step 7.4 — Two tiers and the `warning` verdict

| | |
|---|---|
| **Reference §** | §35 · **S-C20** |
| **Precondition** | 7.3 |
| **Verify** | `pytest` |

**The rule is §35's — the grader's three verdict statuses, what may produce a
`fail`, and what `acknowledged_gaps` must record. Read it there.**

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

## Step 7.6 — The re-approval cascade (§37)

| | |
|---|---|
| **Reference §** | §37 · §9.5 |
| **Touches** | `phases/gate_assembly.py`, `phases/nodes_common.py` |
| **Precondition** | 7.3 |
| **Verify** | `pytest` |

**Not in the original spine.** §37 has two halves and only one was scheduled:
`ContradictionDetectionMiddleware` landed at 6.5, and **the re-approval cascade
it exists to trigger was never given a step.** Detecting a contradiction that
invalidates an approved upstream field, and then not reopening that field's
gate, leaves the case document internally inconsistent while every individual
value looks valid.

**§3.6's node-level error handlers depend on this** — CLAUDE.md names gate
reopening as one of two correctness-critical consumers of `error_handler=`: *"when
the re-approval cascade fires, the affected phase's handler must run, or state
and index disagree silently."*

**Evidence supersession routes in here, and does NOT get its own mechanism**
(founder ruling, 2026-09-08). When a Belt uploads evidence that supersedes what
an approved value rests on — a corrected extract, a longer period, a re-run
GR&R — **that is a material contradiction of a gate-committed value, which is
exactly what §37 already handles.** The trigger is different; the cascade is the
same. Building a second path would give one concept two mechanisms that could
disagree about whether a phase is provisional.

**What 6.11 and 6.12 owe this step:** the ask-binding makes supersession
detectable — a second file against the same ask is a revision (6.12), and the
deterministic parse gives the comparable shape (6.11). Without both, "this
upload supersedes that one" is a filename guess.

**Done when:** a contradiction against an approved upstream field reopens that
phase's gate, the reopening is recorded in `step_log` and the registry, **a
superseding upload against a committed value fires the same cascade rather than
a separate path**, and a test drives both triggers end to end.

---

## Step 8.0 — Turn telemetry and `@traceable` (§51)

| | |
|---|---|
| **Reference §** | §51 · §44 |
| **Touches** | `core/tracing.py`, `core/logging_setup.py`, all five `phases/*/validate.py`, `phases/nodes_common.py` |
| **Precondition** | 7.6 |
| **Verify** | `trace-check` |

**Not in the original spine, and it is the largest single hole the audit
found.** §51 is ratified and mandatory. **There are zero `@traceable`
decorators in the backend.** §51 requires one on every function that extracts
fields, **validates gate criteria — all four layers of §34**, scores
completeness, makes routing decisions outside LangGraph, or calls an Azure
service directly. None of the five `validate.py` files carries one. §51's
five-field log line is 3 of 5: `request_id`, `case_id` and `phase` are present,
**`node_name` and `duration_ms` are not.**

**It is numbered 8.0 — before 8.1 — because step 8.2 cannot be done honestly
without it.** WATCH 28's ratified resolution method is *"resolve by measurement,
not derivation"*: `run_timeout` and the retry policy come from an observed
distribution of model-call latency, retry count, seconds lost to backoff, tool
time and step count. **Those are components, and nothing records them today.**
A step that must set a number from data cannot precede the step that collects
the data.

**Two consumers beyond 8.2, both already owed:**
- WATCH 26's open question — the hop distribution across the five phases falls
  out of the same step-count telemetry.
- §51's own P50/P99-as-quality-signal claim, which is currently unmeasurable.

**Done when:** `@traceable` is on every function §51 names, the log line carries
all five fields, and one coaching turn's LangSmith trace shows the five
telemetry components broken out per turn rather than as a single duration.

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

**Three-state, two instances — §46**, which states why two-state breakers are
not permitted here.

Levels 1, 2 and 4 of the chain land here. **Level 3 (cache) is step 8.4 and is
BLOCKED.**

---

## Step 8.4 — Level 3 response cache

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

## Step 8.5 — Graceful shutdown

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

## Step 8.6 — Context recovery (§44 Step 2)

| | |
|---|---|
| **Reference §** | §44 · §45 |
| **Touches** | `phases/nodes_common.py`, `core/checkpointer.py` |
| **Precondition** | 8.3 |
| **Verify** | `pytest` |

**Not in the original spine.** §44's failure pipeline is seven steps; the audit
found six of them scheduled and **Step 2 — context recovery, "save partial
results, resume" — with no step at all.** Steps 0 and 3–6 land at 8.1–8.3;
Step 1 is §48 at 8.1.

**It is a native primitive at LangGraph ≥1.2.6** (§44), which
`agent-improve/.venv` already satisfies at 1.2.11 — so this is wiring, not
design.

**Done when:** a node that fails mid-turn resumes from its saved partial result
rather than restarting the turn, and a test drives the failure and the resume.

---

## Step 8.7 — `delete_blob`, and the upload lifecycle (WATCH 10)

| | |
|---|---|
| **Reference §** | §10 · §58 S-C08 |
| **Touches** | `storage/blob.py`, `gateway/routes.py` |
| **Precondition** | 8.6 |
| **Verify** | `azure-query` |

**Not in the original spine — WATCH 10 said "owed as its own step" and that
step was never created**, which is precisely the failure mode this audit
exists to catch.

`DELETE /files/{case_id}/{file_id}` removes the upload record from the case
document and **leaves the blob at `uploads/{case_id}/{file}` in place forever.**
`storage/blob.py` owns that prefix (§10, S-C08) and exposes no deleter. **This
is not a regression from 3.5** — the pre-3.5 route probed for a `delete_blob`
that never existed, so the branch never ran; 3.5 preserved the behaviour and
dropped the dead probe, which is what made the gap visible.

**A new SPEC-GAP is owed with it:** S-C08's *Paths owned* names
`uploads/{case_id}/{file}` and **no behaviour governs its deletion** — G-21
does not cover it.

**Done when:** `delete_blob` exists, the DELETE route calls it, an
`azure-query` confirms the blob is gone, and the S-C08 gap is registered in §66.

---

## Step 9.0 — Knowledge-index rebuild

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

> ### ⚠ ATTACHED 2026-09-14 — two dismissed hazards are owned by this step (G-61)
>
> Both rest on argument alone and nothing re-runs the argument — the §55.2
> shape, which cost `ef59aa8`.
>
> | Where | The claim |
> |---|---|
> | §23.3 | *“Safe by construction — each tool addresses its own index”* — the `embedding` / `content_vector` asymmetry |
> | §23.2 | *“it can only change at a rebuild … and cannot drift silently”* |
>
> **This step applies the case-index rename**, which either dissolves (a) — the
> asymmetry is gone — or leaves it needing a test that binds each tool to its
> own vector field name. (b) is a claim about Azure's rebuild semantics and is
> discharged by the reindex being observed, or withdrawn. **Discharge or
> withdraw; do not carry them forward unexamined.**

## Step 9.1 — The Azure batched reindex, case index only

| | |
|---|---|
| **Reference §** | §23.2 · §23.3 · §23.5 |
| **Touches** | Azure AI Search — `improve_evidence_index`, `improve_case_index` |
| **Precondition** | 5.2 |
| **Verify** | `azure-query` |

**Both changes are RATIFIED and NOT YET APPLIED. Batch them** so the corpus
rebuilds once (§23.3).

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

| Index | Change |
|---|---|
| ~~`improve_evidence_index`~~ | ~~Add `phase` and `uploaded_at`~~ — **MOVED to step 6.13**, along with the five fields ratified 2026-09-09 |
| `improve_case_index` | Rename `embedding` → `content_vector`. Delete + recreate — the index holds 0 documents, so no data migration |
| **Both, plus `improve_knowledge_index`** | **Contextual chunk labels** — a short generated preamble per chunk situating it in its parent document, embedded with the chunk (**added 2026-09-08**) |

**Contextual chunk labels join this batch, and the reason is arithmetic.**
Anthropic measures a **~35% reduction in retrieval failure** from contextual
embeddings, at roughly **$1 per million document tokens** at ingest — a
one-time cost against a permanent recall improvement. **It is a schema change on
the same indexes**, so it either rides this rebuild or pays for a second one.
Batching it here is the whole reason this step exists (§23.3).

> **This is the step's third rider and the batch is now the point.** A reindex is
> the expensive, disruptive operation; the changes riding it are individually
> cheap. Anything else needing a schema change before production should be
> proposed here rather than scheduled separately.

**Normalise the HNSW profile name while the index is being recreated.**
`improve_case_index` uses `improve-vector-profile` where the other two use
`default` — safe by construction, but the opportunity to fix it does not recur
cheaply (§23.3).

**Done when:** `content_vector` exists on
`improve_case_index` at 3072 dimensions, **contextual labels are present on
re-ingested chunks across all three indexes**, and all three re-ingest
cleanly.

**Then unblock:** `rag_lookup_case_history` switches to `content_vector`.
*(`rag_lookup_evidence`'s `order_by=["uploaded_at desc"]` and its optional
default-off `phase` filter unblock at **6.13**, not here.)* **Update CLAUDE.md §7.2's table in the same commit** — it
says so explicitly.

---

# Part 9 — Stage 10: API and UI

---


## Step 9.2 — The premium deployment's quota, on the coach's own model call (G-53)

| | |
|---|---|
| **Reference §** | §19.4 · §19.7 · §19.8 · §21 · G-53 |
| **Touches** | Azure provisioning — no code in this repository |
| **Precondition** | **EXTERNAL** — a quota change, like §9.0 and §9.1 |
| **Verify** | `live-run`: one turn on a real case reaching a coached answer |

### The condition this clears

**`operational-premium` (gpt-4o, westeurope) returns 429 on the coach's own
model call.** Measured across four consecutive runs on 2026-09-12, all
degrading identically: `ModelRetryMiddleware` exhausts its two retries, the
answer becomes `Model call failed after 3 attempts with RateLimitError`,
`CoherenceMiddleware` correctly rejects that three times, and the grader is
stood down per S-C13 B3.

**Every middleware behaved correctly.** That is why this is a quota condition
and not a defect: the stack degraded exactly as §19.4, §19.7 and S-C13 B3
specify. Nothing here is a code change.

### Why it is registered rather than tolerated

**It blocks every remaining `live-run` verification.** Steps 6.7, 6.12 and 6.13
already owe live-run halves, and 6.21's Done-when requires a real turn on
`IMPR-2026-ED8`. None of them can be discharged while the coach's model call
cannot complete.

**And it leaves the healthy path unobserved.** Coherence passing on its first
attempt, and `DMAICGraderMiddleware` actually grading rather than standing
down, have been seen in **no trace to date** — only the degraded path has. The
ordering evidence for §19 survives this, because position 6 fires third either
way, but the grader's own behaviour is unevidenced.

### Done when

One live turn on a real case reaches a coached answer: `CoherenceMiddleware`
passes on attempt 1, `DMAICGraderMiddleware` returns a verdict rather than
logging `SKIPPED`, and the turn captures at least one field into `artifacts`.

## Step 10.0 — The coaching turn’s output reaches the Belt — four blocks and the grader’s warning

| | |
|---|---|
| **Reference §** | §50.1 · §49 · §20 · S-C05 (§58.5) · G-69 |
| **Touches** | `backend/gateway/schemas.py` · `backend/gateway/routes.py` · **`ui/index.html`** · `backend/tests/` |
| **Precondition** | **6.19** — the fields exist on `CoachingResponse`. Landed |
| **Verify** | `pytest` + `manual-UI` |
| **Status** | **RULED — founder 2026-09-15. Not started** |

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

**Done when:** `AskResponse` declares all four **and `grader_warning`**; a
turn's response carries them end to end, asserted against the ROUTE rather than
against the schema alone; **a turn that exhausts the grader's iterations
carries its warning to the Belt, asserted on the RESPONSE and not on the
middleware's return value** — the existing test asserts the latter and is the
G-63 shape (G-76); **the UI rebuilds its render state from
`conversation_history` rather than only from the last send, so a visual
survives a tab switch (G-79)**; the UI renders four blocks and `pytest` is
green; a `manual-UI` pass confirms
the Belt sees four blocks rather than one blob; the Appendix F row's anchor
moves off `absent:` to a positive one; **and G-50's closure is re-examined on
the record — upheld with its scope stated, or reopened with this step named as
what closes it.** One or the other, never silence.

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
progress bars, never one blended count** — §43.4 gives the worked case for why a blended count misleads.

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

**FIVE §56 amendments are QUEUED HERE**, from steps 6.3, 6.4 and 6.5. Every one
is a case where the reference describes an API or a mechanism the installed
library does not have. **None is a design change**; all six are the document
catching up to code that had to be written against measured reality.

| # | Section | What it says | What is true |
|---|---|---|---|
| 1 | **§19.1** / S-C11 B1 | `BeforeModelStateInjection` is `before_agent` **and** "prepends at the top of the prompt" | Those are two different hooks. `before_agent(state, runtime)` returns a **state update** and cannot reach the prompt; the prompt is reached through `wrap_model_call`, where `ModelRequest` carries `system_message` and `.override()`. The build composes on `before_agent` (once per turn, as B1 requires) and prepends on `wrap_model_call`, which is a pure read. **§19.1's wording needs to describe the split**; the behaviour it mandates is unchanged and is met |
| 2 | **§19.3** | `SummarizationMiddleware(model="azure/operational-model", …)` | That string has LangChain construct the model itself, **bypassing the factory** — CLAUDE.md §4.1: *"Never instantiate `AzureChatOpenAI` directly. Always use `get_llm()`."* The signature accepts `BaseChatModel`, and §21 already ratifies a `summarizer` role on the operational tier, so the build passes `get_llm("summarizer")`. **The example needs correcting**; the tier it names is right |

| 3 | **§21** | Content blocks, stated for responses we **read** | The rule binds on messages we **write** too — step 6.3 shipped two middlewares that built a `SystemMessage` by f-string over an existing `.content`, and nothing forbade it. CLAUDE.md **§4.5 now states it** (v2.2.31, §0.25) and the no-go list carries it, but §21 is the platform section that owns the topic and **binds on all three agents**, so the rule is currently written for one and true for three. Defect record: `docs/_archive/DECISIONS.md` Part AH2 |

| 4 | **§19** | Two separate claims: *"declaration order is execution order for hooks of the same kind"*, and positions 4-5 *"compete for no slot with anything else"* | **Both follow from one missing distinction: the middleware list is NESTING order, outermost-first; the position numbers are EXECUTION order, and for `after_*` hooks they are opposite.** LangChain's model is *"first in list as outermost layer"* — `before_*` fires on the way in, outermost-first; `after_*` on the way out, innermost-first. That sentence explains why 6-8 are layered grader-outermost, why position 1's wrap encloses position 4's retry (measured: 3 model calls, 1 composition), and why position 1 must be declared first. **Teach the distinction; do not patch the sentences** — and note that list position is the only lever LangChain offers: no priority, no ordering attribute, and `hook_config` governs `can_jump_to`, not sequence |
| 5 | **§19.6** | ``raise HITLInterrupt(**flag)`` | **Does not interrupt.** Measured: a custom exception propagates out and hits `error_handler`; `interrupt()` (§33) yields a resumable interrupt. `HITLInterrupt` is deliberately never defined — a class whose documented use does not interrupt is a trap (G-15) |

All five are recorded as **WATCH 27**. None blocks any step — the code is
already written the correct way in every case.

---

# Appendices

---

---

## Change log

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
<!-- Generated by .githooks/pre-commit, from git log + Appendix D.
     DO NOT HAND-EDIT — it is rewritten on the next commit.
     Step 6.16's board generator reads THIS block. -->

## Step board

| State | Count | Steps |
|---|---|---|
| **DONE** | 38 | **2.3**, **2.4**, **2.5**, **2.6**, **2.7**, **3.1**, **3.2**, **3.3**, **3.4**, **3.5**, **4.1**, **4.2**, **4.3**, **4.4**, **5.1**, **5.2**, **5.3**, **5.4**, **6.1**, **6.2**, **6.3**, **6.4**, **6.5**, **6.6**, **6.7**, **6.8**, **6.9**, **6.11**, **6.12**, **6.13**, **6.16**, **6.18**, **6.21**, **6.19**, **6.25**, **6.26**, **6.27**, **6.31** |
| **BUILDING NOW** | 1 | **6.20** — The write paths — `computation_results`, `phase_metrics`, `field_index` |
| **BLOCKED** | 8 | **6.14** (BLOCKED), **6.10** (BLOCKED), **8.4** (BLOCKED), **8.5** (GATED), **9.0** (EXTERNAL), **9.1** (EXTERNAL), **9.2** (EXTERNAL), **6.22** (EXTERNAL) |
| **QUEUED** | 25 | **10.0**, **8.0**, **7.3**, **10.2**, **7.1**, **7.2**, **7.4**, **7.0**, **7.5**, **7.6**, **8.1**, **8.2**, **8.3**, **8.6**, **8.7**, **10.1**, **6.17**, **6.23**, **11.1**, **6.24**, **6.28**, **6.29**, **6.30**, **6.32**, **11.2** |

*72 rows. DONE is git history — the `refactor(arch-v2): commit X.Y` subjects, intersected with this table, so a step that landed under another subject is not counted. BLOCKED is Appendix D's status column, the only thing git cannot say. Regenerated 2026-09-15.*
<!-- END STEP BOARD -->

## Appendix A — Traceability matrix

**Every step maps to the reference section that specifies it.** A step with no
reference section is not a step — it is an undocumented decision.

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
| 5.3 | §30, §31, §69 | `pytest` |
| 5.4 | §30 | `pytest` |
| 6.1 | §17, §20 | `trace-check` |
| 6.2 | §18, §20 | `live-run` |
| 6.3 | §19.1–§19.3 | `trace-check` |
| 6.4 | §19.4, §19.5, §21 | `grep-absence` |
| 6.5 | §19.6–§19.8 | `pytest` |
| 6.6 | §22 | `grep-absence` |
| 6.7 | §16 · §26 | `pytest` + `live-run` |
| 6.8 | §6, §9, §19.1 | `trace-check` |
| 6.9 | §32, §43, §37 | `pytest` |
| 6.10 | §26, §58.18 | `pytest` + `live-run` |
| 6.11 | §29.1, §6, §10, §23.2, §65.4 | `live-run` + `azure-query` |
| 6.12 | §29.1, §32, §43, §50 | `live-run` |
| 6.13 | §23.2, §23.2.1, §23.4, §24, §6 / S-C02, S-C09 | `azure-query` + `live-run` |
| 6.14 | §32, §43, §23.2.1 | `pytest` |
| 6.17 | §55.1, §6 / S-C02, §29.2 | `pytest` |
| 6.18 | §17, §26, S-F04, S-F13, S-F57 | `live-run` |
| 6.19 | §20, S-C05, §50.1 | `pytest` |
| 6.20 | §7, §39.x.7, S-C02, S-C03 | `pytest` + `manual-UI` |
| 6.21 | §17, §26, §19.1 / S-C11, S-F13, S-F57 | `live-run` + `pytest` |
| 6.16 | §55.1, §66, Appendix D | `grep-absence` + a commit that moves a step |
| 7.0 | §52 | `pytest` |
| 7.1 | §34, §35 | `pytest` |
| 7.2 | §34, §36 | `pytest` |
| 7.3 | §33 | `manual-UI` |
| 7.4 | §35 | `pytest` |
| 7.5 | §38 | `pytest` |
| 7.6 | §37, §9.5 | `pytest` |
| 8.0 | §51, §44 | `trace-check` |
| 8.1 | §48 | `pytest` |
| 8.2 | §45 | `pytest` |
| 8.3 | §46 | `pytest` |
| 8.4 | §46 | **BLOCKED** |
| 8.5 | §45 | **GATED** |
| 8.6 | §44 | `pytest` |
| 8.7 | §10, §58 S-C08 | `azure-query` |
| 9.0 | §23, §23.1 | `azure-query` — DONE out-of-band |
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

**Neither is a step, and neither blocks one.** Both encode Black Belt domain judgment and inform the design as it lands (§53.1).

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

> **Machine-readable. THREE hooks parse this table.**
> Format is fixed:
> `| <seq> | **Commit X.Y** | <title> | <status> | <zone> | <scope> | <impact> |`.
> Do not reformat without updating `.claude/hooks/session-start-context.py`,
> `.claude/hooks/continuity_status.py` AND `.claude/hooks/build_board.py` in
> the same commit (CLAUDE.md §0.2 applies to hooks that read documents, not
> only to rule numbers).
>
> **`Zone` and `Impact` were added 2026-09-11 by step 6.16**, and they were
> appended rather than inserted **deliberately**: the two older readers match
> `| **Commit X.Y** | <what> | <status>` and stop at the status cell, so
> columns 4 and 5 are invisible to them and neither needed a change. **Adding
> a column anywhere left of `status` would have silently broken both** — the
> row would not vanish, it would parse with the wrong cell as its status,
> which is worse.
>
> **`Zone`** — one of seven: `UI` `SUP` `PHASE` `COACH` `GATE` `STORE` `OPS`.
> Which container the step changes. The zone↔block mapping is **not 1:1** and
> is declared as data in `build_board.py`, so adding a block or a zone raises a
> `KeyError` rather than silently unmapping a step. It caught a real error on
> its first run: §19.6–§19.8 were labelled `GATE` while sitting in the
> middleware block, which `GATE` does not span.
>
> **`Impact`** — one sentence: **what is true about the product if this step is
> never done.** A consequence in the product's terms, never a restatement of
> the title. It is the only column that is new information rather than a
> projection of something already tracked, and it is what lets a reader judge
> whether a step is worth its slot.
>
> **A STEP'S BODY HEADING MAY NOT CARRY A STATUS TOKEN.** Ratified
> 2026-09-11. Four headings carried `· **BLOCKED**`, `· **GATED**`,
> `· **DONE out-of-band**` and `· **EXTERNAL**` — **a second, hand-maintained
> source for the one fact this column exists to own.** A heading and a cell
> that can disagree will. `verify_built.py`'s *step titles* check now fails
> on a status token in a heading, and on a row whose words are not in its
> own section heading.
>
> **The status column carries only what git cannot say** — `BLOCKED`, `GATED`,
> `EXTERNAL`. It is EMPTY for every schedulable step, done or not: completion
> is the highest `refactor(arch-v2): commit X.Y` in git log, and a status cell
> claiming it would be a second, hand-maintained source for a fact git already
> owns. Both readers match the cell with `[A-Za-z]*` — **the star is
> load-bearing**, because with `+` an empty cell fails to match and the row
> vanishes from the parse entirely.
>
> **A step that lands under any other subject is invisible to this scheme.**
> Give it `EXTERNAL` (or `BLOCKED` / `GATED`) so the pointer does not stop on
> it forever — that is what 9.0 carries, having landed as
> `feat(knowledge): 871637f`.

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

> **The two new columns, ratified 2026-09-11 with the Define-slice ruling.**
>
> **`Seq`** — execution order. **Column ONE, deliberately**: both older readers
> search for `| **Commit X.Y** |` unanchored, so a column to their LEFT does
> not disturb them, while a column inserted between `Commit` and `status`
> would have parsed the wrong cell AS the status — worse than a row vanishing,
> because it would still match. Verified by running both readers before and
> after the column was added, with the values in their original order, and
> confirming byte-identical output.
>
> **`Scope`** — `SHARED` or `PHASE`. Which of the two a step is **tells you how
> much of slices 2–5 is already paid for by proving slice 1**: shared machinery
> is built once and runs for every phase; `PHASE` work recurs. Of the 27 steps
> not yet landed, **25 are SHARED and 2 are PHASE** — which is the argument for
> the vertical-slice order, stated as a number rather than as a hope.

> **The total is the row count.** Why a row was added is in the commit that
> added it.
>
> **The LANDED count is `git ∩ this table`, not the number of spine commits.**
> Git history carries five commits from before this table existed — 0.1, 1.1,
> 1.2, 2.1, 2.2, under ARCHITECTURE.md §15's old numbering — and the table
> starts at 2.3, so counting every spine commit against a total drawn from here
> would measure two different populations. **A step that landed under any other
> subject is therefore not counted either**: 9.0 shipped as
> `feat(knowledge): 871637f` and is invisible to the scan by construction.
> **The figure fell 31 → 30 on 2026-09-10 for that reason alone** — no work was
> lost, and the hand-maintained 31 had been counting 9.0 that the derived
> figure cannot see.

### The bands — what the Seq ranges mean

**Machine-readable: `.claude/hooks/build_board.py` renders the board from this
table.** Ranges are inclusive. **Edit the band here, not in the generator** —
hardcoding a Seq range in code would make the plan a thing only a developer can
restate, which is the opposite of what the board is for.

| Band | Seq | Name | Delivers |
|---|---|---|---|
| A | 330–380 | THE LOOP | One Belt turn, end to end: it completes, it has fields to render, its writes land, it can be watched, it pauses at a gate, and the Belt sees it |
| B | 390–440 | GATE QUALITY | What the validator catches, and what happens when it does. **Deliberately after A** — running the loop is what tells you what the validator must catch |
| C | 450–460 | PHASES 2–5 | The remaining four phases, one slice each, on machinery A and B already proved |
| D | 470–580 | CROSS-CUTTING | Reliability, transport and cleanup. Nothing here is needed for a slice to work |

| Seq | Step | Title | Status | Zone | Scope | Impact — what is true about the product if this step is never done |
|---|---|---|---|---|---|---|
| 10 | **Commit 2.3** | Dependency upgrade |  | OPS | SHARED | Every later step is written against APIs the installed version may not have, and the checkpoint-namespace regression §16 names is live. |
| 20 | **Commit 2.4** | `set_entry_point` → `add_edge(START, …)` |  | SUP | SHARED | The graph declares its entry with a superseded call, so CLAUDE.md §3.1's no-go list has a standing exception in the one file it most matters. |
| 30 | **Commit 2.5** | Async conversion |  | OPS | SHARED | Blocking calls sit inside an async graph, so one slow Azure call stalls every concurrent coaching session rather than just its own. |
| 40 | **Commit 2.6** | `content_blocks` · 20 sites |  | COACH | SHARED | Twenty sites parse the raw content field, so a provider response-shape change breaks coaching text silently instead of loudly. |
| 50 | **Commit 2.7** | LLM factory · 6 roles → 11 |  | OPS | SHARED | Five of the eleven specified roles have no deployment, so grader, coherence, synthesis, intent and constraint calls all run at another role's model and temperature. |
| 60 | **Commit 3.1** | `SupervisorState` and `PhaseState` |  | SUP | SHARED | Neither level has typed state, so every node reads and writes an untyped dict and a misspelled field is a silent no-op. |
| 70 | **Commit 3.2** | `AzureBlobStore` |  | STORE | SHARED | Gate documents have nowhere durable to live, so a phase's approved output exists only inside the turn that produced it. |
| 80 | **Commit 3.3** | Boundary mappers |  | PHASE | SHARED | Parent and subgraph share state keys directly - the coupling that stops a phase running on its own and makes checkpoint namespaces collide. |
| 90 | **Commit 3.4** | `{Phase}Output` schemas + validators + UI |  | GATE | SHARED | No phase has a canonical gate document, so what a gate approves is whatever the UI happened to render that day. |
| 100 | **Commit 3.5** | `storage/blob.py` — class → functions, sync → aio |  | STORE | SHARED | The system of record is reached through a sync class inside an async app, so every case read blocks the event loop. |
| 110 | **Commit 4.1** | Define phase subgraph |  | PHASE | SHARED | Define has no subgraph, so there is no node structure for a coaching turn to run inside and no per-phase state to carry. |
| 120 | **Commit 4.2** | `thread_id` + disconnect policy |  | STORE | SHARED | Nothing is checkpointed, so a dropped connection loses the turn and a returning Belt starts the phase again from nothing. |
| 130 | **Commit 4.3** | Supervisor graph |  | SUP | SHARED | There is no Level-1 graph, so nothing advances a project from Define to Measure and DMAIC order is whatever the caller asks for. |
| 140 | **Commit 4.4** | Remaining four subgraphs |  | PHASE | SHARED | Only Define can be coached; Measure, Analyse, Improve and Control have no runnable graph at all. |
| 150 | **Commit 5.1** | Retrieval failure semantics |  | COACH | SHARED | A failed Azure search is indistinguishable from a genuine no-match, so the coach teaches from silence and presents it as evidence. |
| 160 | **Commit 5.2** | Three `rag_lookup_*` + RRF |  | COACH | SHARED | The coach cannot retrieve methodology, evidence or case history, so every answer is model recall with no source behind it. |
| 170 | **Commit 5.3** | 20 computation tools |  | COACH | SHARED | The coach cannot compute a sigma level, a Cpk or a t-test, so it either transcribes the Belt's arithmetic or invents its own. |
| 180 | **Commit 5.4** | Per-phase tool binding |  | COACH | SHARED | Every phase is handed every tool, and selection quality degrades past the tractable range in all five at once. |
| 190 | **Commit 6.1** | Planner / Executor split |  | COACH | SHARED | One model call decides strategy and executes it, so there is no point at which a routing decision can be inspected or corrected. |
| 200 | **Commit 6.2** | `create_agent` executor |  | COACH | SHARED | Nothing structured comes out of a coaching turn, so no field is ever captured and every gate is inert by construction. |
| 210 | **Commit 6.3** | Middleware 1–3 |  | COACH | SHARED | The coach sees no project facts, loads no skill and never compresses - it forgets the case, then exceeds the context window. |
| 220 | **Commit 6.4** | Retry middleware 4–5 + factory retry removal |  | OPS | SHARED | Retries are hardcoded in the factory where nothing can see or tune them, and a transient tool failure ends the whole turn. |
| 230 | **Commit 6.5** | Middleware 6–8 |  | GATE | SHARED | Nothing detects a contradiction, checks coherence or grades the turn, so coaching quality is entirely unmeasured. |
| 240 | **Commit 6.6** | Prompts |  | COACH | SHARED | The five coach prompts carry no memory hierarchy and no anti-hallucination guards - the content-level defence a schema cannot provide. |
| 250 | **Commit 6.7** | The hop cap, as §26 specifies it (WATCH 26) |  | COACH | SHARED | Retrieval has no budget, so a coach can see-saw between searches until the recursion backstop ends the turn with no answer. |
| 260 | **Commit 6.8** | `phase_context` is read (WATCH 19) |  | PHASE | SHARED | The composed project context is declared and read by nothing, so the coach opens every phase as though the project had just started. |
| 270 | **Commit 6.9** | The four missing SKILL.md files + §32 conformance |  | COACH | SHARED | Four of five phases run progressive disclosure against nothing, so the coach has no phase-specific method to follow. |
| 280 | **Commit 6.11** | The upload path (G-36) |  | STORE | SHARED | No external data can enter the system, so every figure the coach uses is one the Belt typed into a chat box. |
| 290 | **Commit 6.12** | Ask-binding: an upload answers a request |  | COACH | SHARED | An upload binds to its filename rather than the request that prompted it, so feeding a file to a computation tool means the coach transcribing numbers out of chunks. |
| 300 | **Commit 6.13** | The evidence index migration |  | STORE | SHARED | Evidence and artefacts share one bucket with no role, kind or version identity, so a proposed future is retrievable later as a fact about the present. |
| 310 | **Commit 6.16** | The board is generated, not written |  | OPS | SHARED | The board a founder reads is hand-drawn and stale from the first commit after it is drawn. |
| 330 | **Commit 6.18** | The executor ignores the tool its planner names (G-49) |  | COACH | SHARED | The planner's routing decision is advisory, so a Belt asking a question whose answer is in an uploaded file gets a timeout instead - and four landed steps keep verification debt nothing else can discharge. |
| 335 | **Commit 6.21** | The plan reaches the model (G-49's fix) |  | COACH | SHARED | The planner's routing decision stays advisory, so the guarantee that an uploaded file is read is whatever the model felt like doing - and the live halves of three landed steps can never be run. |
| 340 | **Commit 6.19** | `CoachingResponse` gains §50.1's four presentational fields (G-50) |  | COACH | SHARED | Every coaching turn arrives as one prose blob, so there is nothing structured for a gate UI to display and five SKILL.md files keep instructing the coach to fill fields that do not exist. |
| 350 | **Commit 6.20** | The write paths — `computation_results`, `phase_metrics`, `field_index` |  | PHASE | SHARED | Three things §39.x.7 specifies are read by the gate document and written by nothing, so a computed figure never reaches a gate and the coach cannot tell which field it is on. |
| 355 | **Commit 10.0** | The coaching turn’s output reaches the Belt — four blocks and the grader’s warning |  | UI | SHARED | The coach produces `explanation`, `example`, `prompt` and `progress` every turn and the API discards all four, so §50.1’s render contract stays prompt-hoped and the Belt reads one prose blob. |
| 360 | **Commit 8.0** | Turn telemetry and `@traceable` |  | OPS | SHARED | Nothing is traced, so every investigation needs a hand-built harness and no limit can be set from measured data. |
| 370 | **Commit 7.3** | Nine-step HITL gate |  | GATE | SHARED | Nothing pauses for a human at a gate, so no gate decides, `gate_attempts` cannot accumulate, and the supervisor graph can never become the runtime. |
| 380 | **Commit 10.2** | Live gate document + conflict panel |  | UI | SHARED | A Belt cannot see the document being built, so the gate is the first time anyone looks at it whole. |
| 390 | **Commit 7.1** | `DMAICGateValidator` + Layer 2b |  | GATE | SHARED | Nothing checks a gate document against its phase's rules, so a gate passes on presence rather than on correctness. |
| 400 | **Commit 7.2** | Layers 2c, 2d + `validation_stack` |  | GATE | SHARED | Cross-phase consistency and statistical validity go unchecked, so Measure can contradict Define and both pass. |
| 410 | **Commit 7.4** | Two tiers + `warning` verdict |  | GATE | SHARED | Every finding blocks equally, so a missing nice-to-have stops a project exactly as a missing baseline does. |
| 420 | **Commit 7.0** | The evaluation suite |  | GATE | SHARED | Coaching quality has no baseline, so no later change can be shown to have improved or regressed it. |
| 430 | **Commit 7.5** | Escalation |  | GATE | SHARED | A project failing its gate three times has nowhere to go, so it loops instead of reaching a human. |
| 440 | **Commit 7.6** | The re-approval cascade |  | GATE | SHARED | A contradiction against an approved value never reopens the field it contradicts, so the gate document keeps a figure the Belt has withdrawn. |
| 450 | **Commit 6.14** | SKILL.md shape pass — Define, Analyse, Improve, Control | BLOCKED | COACH | PHASE | Four of five phases cannot ask for a file in a shape they can validate, so 6.12's ask-binding works for Measure alone. |
| 460 | **Commit 6.10** | `analyse_executor_node` — §26's multi-hop | BLOCKED | COACH | PHASE | Analyse cannot chain retrieval, so root-cause work needing a second hop returns a first-hop answer and stops. |
| 470 | **Commit 8.1** | Structured errors |  | OPS | SHARED | Failures arrive as free text, so the circuit breaker and the fallback chain have nothing to read to tell retry from stop. |
| 480 | **Commit 8.2** | Timeouts + compensating actions |  | OPS | SHARED | A node failing mid-turn leaves its partial writes in place, so the next turn resumes from a state nobody wrote deliberately. |
| 490 | **Commit 8.3** | Circuit breakers + fallback chain |  | OPS | SHARED | A failing dependency is retried until it takes the rest of the system down with it. |
| 500 | **Commit 8.6** | Context recovery (§44 Step 2) |  | STORE | SHARED | A mid-turn failure loses the work the turn had already done, so the Belt is asked to repeat it. |
| 510 | **Commit 8.7** | `delete_blob` + upload lifecycle |  | STORE | SHARED | An upload can be created and never removed, so a superseded or mistaken file stays retrievable as evidence forever. |
| 520 | **Commit 10.1** | `/ask/stream` SSE |  | UI | SHARED | Every coaching turn arrives as one block after a long wait - the interaction §50 was written to replace. |
| 530 | **Commit 8.4** | Level 3 cache | BLOCKED | OPS | SHARED | Identical requests re-run end to end. A cost item rather than a correctness one, and the resource is not provisioned. |
| 540 | **Commit 8.5** | Graceful shutdown | GATED | OPS | SHARED | A deploy landing mid-turn drops that turn instead of draining it. |
| 550 | **Commit 9.0** | Knowledge-index rebuild | EXTERNAL | STORE | SHARED | The methodology corpus is not retrievable, so `rag_lookup_methodology` has nothing to search. |
| 560 | **Commit 9.1** | Azure batched reindex — case index only | EXTERNAL | STORE | SHARED | The case index carries no content vector, so case-history retrieval stays keyword-only and misses paraphrase. |
| 562 | **Commit 9.2** | Premium deployment's quota — the coach's own model call (G-53) | EXTERNAL | OPS | SHARED | `operational-premium` returns 429, so every live run degrades to the retry message and no `live-run` verification in any remaining step can reach a coached turn. |
| 565 | **Commit 6.17** | The count-check — a written count against the list it describes |  | OPS | SHARED | A written count and the list it describes can disagree indefinitely - the failure five captions in this repository have already had. |
| 567 | **Commit 6.22** | The order-check — the middleware stack's ordering test observes execution (G-52) | EXTERNAL | OPS | SHARED | The one test pinning §19's order replaces `create_agent`, so it asserts the rule against itself and stayed green through a three-week document split it existed to prevent. |
| 569 | **Commit 6.23** | The source-method check — verification against the installed object, not the page (G-54) |  | OPS | SHARED | Every verdict in the verification log was reached by reading a page; one of them overwrote a correct statement and propagated the error to a second document. |
| 571 | **Commit 6.24** | The drift hook learns to read the documents (G-56) |  | OPS | SHARED | The governing documents are excluded from every drift pattern, so the six defects worked on 2026-09-12 and 2026-09-13 were all in files nothing guards. |
| 572 | **Commit 6.25** | Scratch leaves the tree |  | OPS | SHARED | Working material sits untracked inside the tree and tracked documents cite it, so a citation resolves for whoever has the folder on disk and for nobody else. |
| 573 | **Commit 6.26** | The guard's tree rules get a test suite (G-57) |  | OPS | SHARED | The two rules that keep scratch and unnumbered files out of the tree are proven by hand and re-run by nothing, so they can stop matching without reporting it. |
| 574 | **Commit 6.27** | The watched-path contract has one owner (G-58) |  | OPS | SHARED | The same twelve paths are stated in §55.2 and hardcoded in the guard, so the document and the gate can disagree about which paths oblige a re-check — and did. |
| 575 | **Commit 6.28** | Fact-ownership moves to the commit gate (G-59, G-60) |  | OPS | SHARED | The ownership guard runs on a tool path most edits do not take, so a document restating an owned value lands unchecked whenever the edit came through Bash. |
| 576 | **Commit 6.29** | Search index schema ownership — ruled (G-60) |  | OPS | SHARED | An ownership class with no owner is a class nothing guards, and this one is named in CLAUDE.md's table as though it were covered. |
| 577 | **Commit 6.30** | A commit body's code claims carry a resolvable reference (G-62) |  | OPS | SHARED | A claim about code can enter the permanent record with nothing to check it against, and the record is what the next session reads as fact. |
| 578 | **Commit 6.31** | The build matrix — one row per step, anchored to a symbol |  | OPS | SHARED | Build status is stated in a document and re-run in a generator, the two describe different populations, and 45 of the 69 markers are backed by no check at all. |
| 579 | **Commit 6.32** | An out-of-band landing gets the lane it earned (G-65) |  | OPS | SHARED | Two completed steps show as red on the board a founder reads, and red is ratified to mean "cannot proceed". |
| 570 | **Commit 11.1** | Delete v1 |  | OPS | SHARED | Two implementations of every phase stay in the tree, and the dead one is still the one writing the v1 field names. |
| 580 | **Commit 11.2** | Governance close-out |  | OPS | SHARED | The refactor has no end, so procedure and architecture drift apart again with nothing marking the handover. |

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

> **Step 9.0 is `EXTERNAL`, and that is what keeps the pointer off it.**
> It landed as `feat(knowledge): 871637f`, not as a `refactor(arch-v2): commit
> 9.0` subject, so the git-log scan cannot see it and `last` can never advance
> past it on its own. Without a status it would become the lowest available row
> once 8.3 lands — 8.4 is BLOCKED and 8.5 GATED — and the pointer would stop
> there permanently.
>
> **`EXTERNAL` is true on its own terms** (an Azure-side knowledge-index
> rebuild is exactly what this document's reading conventions define it to
> mean), so the row stays unavailable on its merits rather than on a completion
> claim the tooling has to be taught to ignore.
>
> **This replaces two earlier notes, both now wrong.** The first said the hook
> "will still propose it" and left the trap documented rather than fixed. The
> second said `done` had been added to `_UNAVAILABLE_STATUSES` — **that fix was
> removed on 2026-09-10** when the status column stopped carrying `done` at
> all, because a `done` status was a second, hand-maintained source for a fact
> git already owns. **The same trap applies to any future out-of-band step**:
> give its row `EXTERNAL`, `BLOCKED` or `GATED`.

---

## Appendix F — The build matrix

> **THIS IS THE SINGLE LEADING DOCUMENT FOR BUILD STATUS.** Ratified
> 2026-09-15 by founder ruling, built at step 6.31. `ARCHITECTURE.md` keeps
> the *rationale* — why a thing is shaped the way it is — and this table keeps
> *whether it exists today*. **A `> **BUILT:**` marker that still states a
> status is mid-migration, not authoritative.**

> **Machine-readable. `.claude/hooks/verify_built.py` is the REFEREE and it
> fails CLOSED.** It reads every row, evaluates the `Evidence` anchor against
> the tree, and exits non-zero on any disagreement. Format is fixed:
> `| L<n> | <order> | **<step>** | <item> | <state> | \`<anchor>\` | <§> |`.
> `.claude/hooks/build_board.py` reads the `Order` column to render the
> vertical.

**One row per Appendix D step, and `GROUP BY Step` is asserted as SET EQUALITY
against Appendix D in both directions.** Not a count: a count passes when one
step is dropped and another added. Rows may be ADDED for a claim a step makes
beyond its own delivery — that is how the 69 `BUILT` markers migrate in — but
no step may be missing and no row may name a step Appendix D does not have.

### The columns

| Column | Owns | Source |
|---|---|---|
| **Layer** | which part of the system the step changes | declared here — the organising axis |
| **Order** | the near-term execution sequence | **hand-set, and the only column that is.** Sparse |
| **Step** | the identifier | Appendix D |
| **Item** | what the step delivers | joined from Appendix D's title |
| **State** | ✅ built · ⚠️ built with a known defect · ☐ not built · ⛔ blocked | §55.2's vocabulary, unchanged |
| **Evidence** | the anchor that proves the State | declared here — see the grammar below |
| **§** | the ratified section carrying the rationale | joined from Appendix A |

> **`Order` IS NOT Appendix D's `Seq`.** `Seq` is the global schedule and the
> board renders it as four bands. `Order` is the **short vertical actually
> being worked**, which is what `CONTINUITY.md` carried by hand until this
> step. A number means *"in the run of work being done now"*; every other row
> is empty, and that emptiness is the point.

> **`State` is DERIVED, not typed** — `⛔` from Appendix D's status cell, then
> `✅` if git carries the step's spine subject, else `☐`. **`⚠️` is the one
> state a human sets**, and it arrives with the marker migration: a defect is
> a judgement about built code, and nothing derives it.

### The anchor grammar — never a line number

**A line number is invalidated by an edit to any line above it, and it fails by
pointing at the wrong line rather than at nothing.**

| Form | Passes when |
|---|---|
| `mod::Symbol` | the module imports and the attribute exists |
| `mod::Symbol {a,b}` | its member set is exactly `{a,b}` — dict keys, model fields, or `.name` of its elements |
| `mod::Symbol =v` | `str(value) == v` |
| `mod` | a bare dotted module imports |
| `absent: <anchor>` | the anchor does **not** hold — **this is what proves a ☐ row** |
| `installed: <anchor>` | it holds in the **installed library**; a failure is a **DEPENDENCY** finding, never a marker one |
| `repo:<path>` | the path exists, resolved from the **repository root** |
| `azure:<resource>` | never, from here — reported **EXTERNAL**, owed rather than passed |

> **`repo:` is explicit because the ambiguity is real: `.claude/` sits ABOVE
> `agent-improve/`.** A bare relative path resolves against whichever root the
> caller passed and reports a present file as absent — which it did, five
> times, on the evaluator's first run.

> **A BEHAVIOUR IS ANCHORED ON THE TEST THAT OBSERVES IT.** Steps 2.6, 6.22,
> 6.26 and 6.27 deliver behaviour spread across many sites with no single
> symbol to name, so their `Evidence` is the test function — **still
> `mod::Symbol`, and deliberately not a fifth form.**

> ### ⚑ EVERY `absent:` CELL IS REMOVED BY ITS OWNING STEP'S DONE-WHEN
>
> **Without this the matrix rots in the OPPOSITE direction from the markers.**
> A marker goes stale claiming a thing is built when it is not. An `absent:`
> cell goes stale claiming a thing is missing after it has been built — and
> **the referee catches that one loudly, because the anchor starts resolving.**
> The failure is the feature. The step that builds the thing replaces its cell
> with a positive anchor in the same commit, or its own gate refuses it.
>
> **DELETION STEPS INVERT THE POLARITY.** Step 11.1 *"Delete v1"* makes an
> ABSENCE true, so its not-built anchor is the POSITIVE form —
> `backend.core.state::ImproveGraphState` resolves today, which is exactly why
> the row reads ☐ — and its Done-when flips the cell to `absent:`. The first
> seed had this backwards and the referee caught it.

### Layers — nine, not eight

The eight Level-1 blocks describe the **runtime**. Thirteen steps change
`.claude/`, `.githooks/` or these documents and touch no runtime file at all;
without a home of their own they all fall into block 8 and *"Persistence and
cross-cutting"* becomes a junk drawer holding 33 of 70 rows. **L0 is that
home.**


#### L0 · Governance and build tooling

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L0 |  | **6.16** | The board is generated, not written | ✅ | `repo:.claude/hooks/build_board.py` | §55.1, §66, Appendix D |
| L0 |  | **6.17** | The count-check — a written count against the list it describes | ☐ | `absent: repo:.claude/hooks/count_check.py` | §55.1, §6 / S-C02, §29.2 |
| L0 |  | **6.22** | The order-check — the middleware stack's ordering test observes execution (G-52) | ⛔ | `backend.tests.test_middleware_execution_order::test_this_observes_a_real_graph_and_not_a_stub` | — |
| L0 |  | **6.23** | The source-method check — verification against the installed object, not the page (G-54) | ☐ | `repo:agent-improve/docs/_archive/BIBLE_VERIFICATION_LOG.md` | — |
| L0 |  | **6.24** | The drift hook learns to read the documents (G-56) | ☐ | `repo:.claude/hooks/fact-ownership-guard.py` | — |
| L0 |  | **6.25** | Scratch leaves the tree | ✅ | `absent: repo:scratch` | — |
| L0 |  | **6.26** | The guard's tree rules get a test suite (G-57) | ✅ | `backend.tests.test_commit_guard_tree_rules::test_a_scratch_directory_segment_is_caught` | — |
| L0 |  | **6.27** | The watched-path contract has one owner (G-58) | ✅ | `backend.tests.test_commit_guard_tree_rules::test_the_watch_list_and_ss552_state_the_same_paths` | — |
| L0 |  | **6.28** | Fact-ownership moves to the commit gate (G-59, G-60) | ☐ | `absent: repo:.claude/hooks/ownership_gate.py` | — |
| L0 |  | **6.29** | Search index schema ownership — ruled (G-60) | ☐ | `absent: repo:.claude/config/search_index_owner.yaml` | — |
| L0 |  | **6.30** | A commit body's code claims carry a resolvable reference (G-62) | ☐ | `absent: repo:.claude/hooks/code_ref_gate.py` | — |
| L0 |  | **6.31** | The build matrix — one row per step, anchored to a symbol | ☐ | `verify_built::matrix_covers_appendix_d` | — |
| L0 |  | **6.32** | An out-of-band landing gets the lane it earned (G-65) | ☐ | `absent: backend.tests.test_board_lanes` | §55.2 · Appendix D · G-65 |
| L0 |  | **11.2** | Governance close-out | ☐ | `absent: repo:agent-improve/docs/HANDOVER.md` | §55 |

#### L1 · API surface

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L1 | 3 | **10.0** | The coaching turn’s output reaches the Belt — four blocks and the grader’s warning | ☐ | `absent: backend.gateway.schemas::CoachingBlocks` | §50.1, §49, S-C05 |
| L1 | 5 | **10.2** | Live gate document + conflict panel | ☐ | `absent: repo:agent-improve/ui/gate_document.js` | §50, §43.4 |

> **⛑ 10.2's ANCHOR WAS THE SECOND UNFAILABLE `absent:` — G-72.** It read
> `absent: repo:agent-improve/frontend/gate_document.js`, and **there is no
> `agent-improve/frontend/`** — the UI is `agent-improve/ui/`. The cell passed,
> and would have kept passing after 10.2 shipped, because 10.2 ships into
> `ui/`. Repointed at `ui/`, where the parent now exists, so the cell flips the
> day the file appears.
>
> **THE LIMIT, STATED RATHER THAN HIDDEN:** the UI is a SINGLE 7,273-line
> `ui/index.html`, so if 10.2 ships inside that file rather than beside it,
> this anchor still will not flip and 10.2's Done-when must replace the cell —
> which is the standing rule for every `absent:` cell. **The UI cannot be
> symbol-anchored at all**, and that is G-71, not a property of this row.

| L1 |  | **10.1** | `/ask/stream` SSE | ☐ | `absent: backend.gateway.routes::ask_stream` | §49 |

#### L2 · Supervisor graph

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L2 |  | **2.4** | `set_entry_point` → `add_edge(START, …)` | ✅ | `absent: backend.core.graph::set_entry_point` | §12 |
| L2 |  | **3.1** | `SupervisorState` and `PhaseState` | ✅ | `backend.core.state::SupervisorState` | §5, §6, §7 |
| L2 |  | **4.3** | Supervisor graph | ✅ | `backend.core.graph::get_graph` | §12, §15 |

#### L3 · Phase subgraphs

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L3 |  | **3.3** | Boundary mappers | ✅ | `backend.phases.mappers_common::PHASE_ORDER` | §9 |
| L3 |  | **4.1** | Define phase subgraph | ✅ | `backend.phases.subgraph_common::build_phase_subgraph` | §12, §13, §14 |
| L3 |  | **4.4** | Remaining four subgraphs | ✅ | `backend.phases.mappers_common::PHASE_ORDER {define,measure,analyse,improve,control}` | §12, §13 |
| L3 |  | **6.8** | `phase_context` is read (WATCH 19) | ✅ | `backend.middleware.state_injection::BeforeModelStateInjection` | §6, §9, §19.1 |
| L3 | 2 | **6.20** | The write paths — `computation_results`, `phase_metrics`, `field_index` | ☐ | `absent: backend.phases.nodes_common::_advance_field_index` | §7, §39.x.7, S-C02, S-C03 |

#### L4 · Coaching agent

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L4 |  | **2.6** | `content_blocks` · 20 sites | ✅ | `backend.tests.test_middleware::test_injection_uses_content_blocks_not_string_concatenation` | §21 |
| L4 |  | **6.1** | Planner / Executor split | ✅ | `backend.phases.nodes_common::planner` | §17, §20 |
| L4 |  | **6.2** | `create_agent` executor | ✅ | `backend.core.substate::CoachingResponse` | §18, §20 |
| L4 |  | **6.6** | Prompts | ✅ | `backend.core.prompts::DEFINE_COACH_PROMPT` | §22 |
| L4 |  | **6.7** | The hop cap, as §26 specifies it (WATCH 26) | ✅ | `backend.phases.nodes_common::COACH_HOP_BUDGET =5` | §16 · §26 |
| L4 |  | **6.9** | The four missing SKILL.md files + §32 conformance | ✅ | `repo:agent-improve/skills/dmaic-define-phase/SKILL.md` | §32, §43, §37 |
| L4 |  | **6.12** | Ask-binding: an upload answers a request | ✅ | `backend.phases.nodes_common::_unconsumed_for_open_ask` | §29.1, §32, §43, §50 |
| L4 |  | **6.18** | The executor ignores the tool its planner names (G-49) | ✅ | `backend.phases.nodes_common::_dispatch_routed_read` | §17, §26, S-F04, S-F13, S-F57 |
| L4 | 1 | **6.21** | The plan reaches the model (G-49's fix) | ⚠️ | `backend.phases.nodes_common::_dispatch_routed_read` | §17, §26, §19.1 / S-C11, S-F13, S-F57 |
| L4 |  | **6.19** | `CoachingResponse` gains §50.1's four presentational fields (G-50) | ✅ | `backend.core.substate::CoachingResponse {message,explanation,example,prompt,progress,fields_captured,citations,contradiction_flag}` | §20, S-C05, §50.1 |
| L4 |  | **6.14** | SKILL.md shape pass — Define, Analyse, Improve, Control | ⛔ | `backend.upload.asks::SHAPES_BY_PHASE.define {}` | §32, §43, §23.2.1 |
| L4 |  | **6.10** | `analyse_executor_node` — §26's multi-hop | ⛔ | `absent: backend.phases.nodes_common::analyse_executor_node` | §26, §58.18 |

> **6.21 IS ⚠️ RATHER THAN ✅, AND IT IS THE ONE ROW WHERE `State` IS NOT
> DERIVED.** Git carries `a1a0a5d refactor(arch-v2): commit 6.21`, so the
> derivation says ✅ and the board's DONE lane agrees. **Its Done-when is not
> met**: it requires a `live-run` on `IMPR-2026-0E5` carrying the live halves
> of 6.7, 6.12 and 6.13, and that evidence does not exist. See *Verification
> owed*.
>
> **This is the gap between "the code landed" and "the step is done" that
> Appendix D's status column cannot express** — it carries only what git
> cannot supply, and *the code landed* is exactly what git does supply. ⚠️ is
> the honest cell until the run reports, and **the run is what flips it**, not
> another commit.

#### L5 · Middleware

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L5 |  | **6.3** | Middleware 1–3 | ✅ | `backend.middleware.skills::DMAICSkillsMiddleware` | §19.1–§19.3 |
| L5 |  | **6.4** | Retry middleware 4–5 + factory retry removal | ✅ | `installed: langchain.agents.middleware::ModelRetryMiddleware` | §19.4, §19.5, §21 |
| L5 |  | **6.5** | Middleware 6–8 | ✅ | `backend.middleware.coherence::CoherenceMiddleware` | §19.6–§19.8 |

#### L6 · Tools and knowledge

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L6 |  | **5.1** | Retrieval failure semantics | ✅ | `backend.core.errors::KnowledgeSearchError` | §27 |
| L6 |  | **5.2** | Three `rag_lookup_*` + RRF | ✅ | `backend.knowledge.tools::RAG_LOOKUP_TOOLS` | §24, §25, §23 |
| L6 |  | **5.3** | 20 computation tools | ✅ | `backend.knowledge.computation::COMPUTATION_TOOLS_BY_PHASE` | §30, §31, §69 |
| L6 |  | **5.4** | Per-phase tool binding | ✅ | `backend.knowledge.fusion::RRF_K =60` | §30 |
| L6 |  | **9.0** | Knowledge-index rebuild | ⛔ | `azure: improve-knowledge-index` | §23, §23.1 |
| L6 |  | **9.1** | Azure batched reindex — case index only | ⛔ | `azure: improve-cases-index.content_vector` | §23.2, §23.3, §23.5 |

#### L7 · Validation, gates, escalation

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L7 |  | **3.4** | `{Phase}Output` schemas + validators + UI | ✅ | `backend.phases.define.schema::DefineOutput` | §7, §40, §41, §53.1 |
| L7 | 4 | **7.3** | Nine-step HITL gate | ☐ | `backend.phases.nodes_common::gate_review` | §33 |
| L7 |  | **7.1** | `DMAICGateValidator` + Layer 2b | ☐ | `absent: backend.validation.gate_validator::DMAICGateValidator` | §34, §35 |
| L7 |  | **7.2** | Layers 2c, 2d + `validation_stack` | ☐ | `absent: backend.validation.stack::validation_stack` | §34, §36 |
| L7 |  | **7.4** | Two tiers + `warning` verdict | ☐ | `absent: backend.validation.tiers::WARNING` | §35 |
| L7 |  | **7.0** | The evaluation suite | ☐ | `absent: backend.evals` | §52 |
| L7 |  | **7.5** | Escalation | ☐ | `absent: backend.phases.escalate_v2::escalate` | §38 |
| L7 |  | **7.6** | The re-approval cascade | ☐ | `absent: backend.validation.cascade::reopen_field` | §37, §9.5 |

#### L8 · Persistence and cross-cutting

| Layer | Order | Step | Item | State | Evidence | § |
|---|---|---|---|---|---|---|
| L8 |  | **2.3** | Dependency upgrade | ✅ | `installed: langgraph =1.2.11` | §53, §16 |
| L8 |  | **2.5** | Async conversion | ✅ | `backend.phases.subgraph_common::build_phase_subgraph` | §14, §49 |
| L8 |  | **2.7** | LLM factory · 6 roles → 11 | ✅ | `backend.core.llm::get_llm` | §21, §54 |
| L8 |  | **3.2** | `AzureBlobStore` | ✅ | `backend.core.store::AzureBlobStore` | §9, §10 |
| L8 |  | **3.5** | `storage/blob.py` — class → functions, sync → aio | ✅ | `backend.storage.blob::download_bytes` | §54, §10, §49 |
| L8 |  | **4.2** | `thread_id` + disconnect policy | ✅ | `backend.core.checkpointer::AzureBlobCheckpointSaver` | §16, §47, §49, §8 |
| L8 |  | **6.11** | The upload path (G-36) | ✅ | `backend.upload.parsers::PARSERS {document,pdf,spreadsheet,text}` | §29.1, §6, §10, §23.2, §65.4 |
| L8 |  | **6.13** | The evidence index migration | ✅ | `backend.knowledge.tools::rag_lookup_evidence` | §23.2, §23.2.1, §23.4, §24, §6 / S-C02, S-C09 |
| L8 |  | **8.0** | Turn telemetry and `@traceable` | ☐ | `absent: backend.core.tracing::traced_turn` | §51, §44 |
| L8 |  | **8.1** | Structured errors | ☐ | `absent: backend.errors::StructuredError` | §48 |
| L8 |  | **8.2** | Timeouts + compensating actions | ☐ | `absent: backend.core.timeouts::NODE_TIMEOUTS` | §45 |
| L8 |  | **8.3** | Circuit breakers + fallback chain | ☐ | `absent: backend.core.resilience::CircuitBreaker` | §46 |
| L8 |  | **8.6** | Context recovery (§44 Step 2) | ☐ | `absent: backend.core.recovery::recover_context` | §44 |
| L8 |  | **8.7** | `delete_blob` + upload lifecycle | ☐ | `absent: backend.storage.blob::delete_blob` | §10, §58 S-C08 |
| L8 |  | **8.4** | Level 3 cache | ⛔ | `absent: backend.core.cache::response_cache` | §46 |
| L8 |  | **8.5** | Graceful shutdown | ⛔ | `absent: backend.gateway.lifespan::drain` | §45 |
| L8 |  | **9.2** | Premium deployment's quota — the coach's own model call (G-53) | ⛔ | `azure: operational-premium.rateLimits =200000` | — |
| L8 |  | **11.1** | Delete v1 | ☐ | `backend.core.state::ImproveGraphState` | §54, App. D |
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

---

*End of document.*
