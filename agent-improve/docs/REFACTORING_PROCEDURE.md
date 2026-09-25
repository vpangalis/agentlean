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
| 6.12 | `live-run` **(Measure)** | **Owed, and RE-HOMED 2026-09-15.** It was never runnable in Define — 0 ask shapes against Measure's 4 (AR-R2) — so this was a **defective clause, not a debt**, for as long as it named Define. Real, and owed against a MEASURE turn |
| 6.13 | `live-run` | **Attempted and FAILED**, cause isolated to code 6.13 did not touch — see its section |
| ~~6.21~~ | `live-run` | **DISCHARGED 2026-09-15**, rid `20167cc9-ea86-4501-a827-0e19ebb2420a`. See the closure in 6.21's own section |
| ~~6.33~~ | `live-run` | **DISCHARGED 2026-09-21**, rid `5415c73d-6b80-426a-b5f4-7daabef1ec4b` and the turn after it. **The row is written in the SAME COMMIT as the code**, which is what this table asks for and what 6.21's absence for eleven days cost. See the closure in 6.33's own section — including what the run does NOT prove |

> **THREE ROWS ABOVE ARE STILL OPEN, AND 6.21'S CLOSURE DID NOT DISCHARGE
> THEM.** 6.21's Done-when required the live halves of **6.7**, **6.12** and
> **6.13** *“run in the same pass”*. **That clause is NOT met**, and each is
> assessed on its own evidence in 6.21's closure rather than carried silently
> by the clause. **6.12's cannot be met by any Define turn at all**: Define
> declares **0** ask shapes against Measure's 4 (ruling AR-R2), so an upload
> has no ask to resolve to.
>
> **6.21 WAS THE CASE THIS TABLE EXISTS FOR, AND IT WAS MISSING FROM IT.** The
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

## ⚑ THE WORKING METHOD — ratified 2026-09-23

**Six clauses. They govern how a step is chosen, proved and closed**, and they
sit here rather than in a step because they bind on every step.

### 1 — The capability register is the unit of progress

**One row per thing a phase must be able to do, each with the single
executable check that proves it.** **Appendix H** holds it. A row is **green or
red and never partial**: a check that half-passes is two capabilities badly
written, not one capability half-built.

**The project's status is the count of green rows.** The step count stays and
is **demoted** — it measures how much work has been done, which is not the same
question as what the product can do, and for eleven months this document could
answer only the first. **46 of 91 steps landed and no Belt can complete a
phase** is the sentence that makes the distinction concrete.

### 2 — Every step declares NEEDS and GIVES

**Two required fields on every step row.** `NEEDS` — the capability rows that
must be green before the step is READY. `GIVES` — the rows it turns green.

**Order is COMPUTED from these, never assigned by `Seq`.** `Seq` remains what
it has been since 2026-09-11: a stable position, not a schedule. A step is
ready when its `NEEDS` are green, and the critical path is what falls out of
that — which is how a dependency that runs backwards becomes visible instead of
being discovered mid-build.

**Populated for the OPEN DEFINE steps only.** Every other step carries them
empty, deliberately: a guessed dependency is worse than a blank one, because it
computes an order somebody will trust.

### 3 — Test first, and the whole set

**A step's checks are written FAILING before the build.** A step is done when
its own checks pass **AND no previously-green capability check has gone red.**

> **THE WORKED EXAMPLE IS THIS PROJECT'S OWN, AND IT IS EIGHT DAYS OLD.** Step
> 6.33 landed on 2026-09-22 and built the field change log. **One file over,
> `storage/blob.py::write_phase_gate` replaces the whole `PhaseRecord`** — so
> the first gate write erases the log 6.33 had just built, along with the
> Belt's uploads. **Every test 6.33 wrote still passes.** A step that proves
> only its own clauses cannot see what it broke, and the register is what makes
> the second half of that sentence checkable.

### 4 — No build without a specification

**New status: `BLOCKED-ON-SPEC`.** It names the missing artefact and its owner.
**It is not the same as BLOCKED** — a BLOCKED step waits on other code, and
somebody can unblock it by building; a BLOCKED-ON-SPEC step waits on a decision
or on content that no amount of engineering produces.

| Step | Missing artefact | Owner |
|---|---|---|
| **7.2** | The Define rubric TEXT — what Layer 2d grades against | **founder** |
| **10.2** | The gate screen design — no spec entry points at it and *"conflict panel"* appears nowhere in ARCHITECTURE.md | **founder** |

**Writing either from the implementer's side is the trap.** A rubric written by
an implementer is a guess at what good coaching looks like, graded by a model,
at a gate that blocks a Belt — and it fails invisibly, because a plausible
rubric passes plausible work.

### 5 — Admission: a finding becomes a step only if it blocks a step in flight

**Everything else goes to the findings list and is reviewed when a stage
closes.** The register is not a place to put things so they are not forgotten;
it is the list of work that is going to happen.

**This clause exists because the alternative was measured.** The register
carries 77 gap rows and 91 steps against a Define slice that cannot complete,
and a founder reading the board cannot tell which four of those hundred and
sixty-eight items are in the way.

### 6 — A mutation proof neuters the PRODUCER, never the stored value

**Mutate the code that computes the thing. Never the value it is computed
into.** A value has more than one consumer, so changing one of them leaves the
others feeding the assertion and the check passes against a mutation that
changed nothing.

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

## ⚑ WHAT "DEFINE COMPLETE" MEANS — the definition the vertical is measured against

**Recorded once, here, so that every step below can be judged against it rather
than against its own Done-when alone.**

> **A Belt is coached through the twelve fields; what they say is kept and every
> change is dated; a complete case ASSEMBLES a gate document; the Belt sees it,
> approves it, and the record is written once and correctly.**

**Five clauses, and each is a thing that either works or does not.** Nothing in
that sentence is about how good the coaching is.

**What is QUALITY, and therefore follows rather than gates:**

| | Why it does not gate |
|---|---|
| **Grading the document** (Layer 2d, the rubric) | A gate that checks required fields, assembles and records is a WORKING gate. Grading makes it a good one |
| **The polished gate screen** (10.2) | The pause is proven through the route at 7.7. The screen is what makes it usable, not what makes it work |
| **Reading uploaded documents** (6.43) | A Belt can complete Define by typing. Reading their files makes the coaching better |
| **The planner's real predicate** (6.45) | The placeholder terminates. The real one asks better questions |

**This is not a demotion of any of the four.** It is the statement that the
vertical is finished when a Belt can go end to end — and that anything measured
against "is it good" cannot be the thing that decides whether it runs at all.

---

## ⚑ THE DEFINE CRITICAL PATH — sequenced 2026-09-23

**Seven steps, in this order.** Each carries `NEEDS` and `GIVES` in its own
section. **The order is the founder's ruling of 2026-09-23** and is recorded
here as the single ordered statement; Appendix F's `Order` column projects it.

| # | Step | What it makes true |
|---|---|---|
| 1 | **6.48** (`CO-1`) | A captured value carries its declared type |
| 2 | **6.20** | The metric entry, and the *"not addressed this phase"* marker |
| 3 | **6.42** | Submit uses assembly; the write MERGES; the write is idempotent |
| 4 | **10.3** | Progress counts the real field names |
| 5 | **6.44** | The contradiction stop moves into a node |
| 6 | **7.3** | The gate pauses, and the pause is resumable (**NARROWED** — see the step) |
| 7 | **7.7** | A route that answers the pause and resumes the run |

> **10.0 IS OFF THE CRITICAL PATH — BY RULING, 2026-09-23.** It was first
> taken off by OMISSION, because Part 3's seven steps did not name it, and
> that inference was flagged rather than relied on. **It is now ruled**, so
> the row's empty `Order` cell rests on a decision rather than on a reading.
>
> **10.2 IS OFF THE CRITICAL PATH**, ratified 2026-09-23. The pause is proven
> through the route at **7.7**; the screen is what makes it usable, not what
> makes it work. It is also `BLOCKED-ON-SPEC` (clause 4), so leaving it on the
> path made founder content a dependency of a working gate.

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

**Done when — the original five, VERIFIED IN MEASURE:** a coach request for data
is recorded with its expected shape; an upload resolves to that ask; a shape mismatch produces a
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
| **NEEDS** | A captured value is stored in the shape its schema declares (6.48) — the registry is `list[dict]`, and a prose registry yields no metric entry |
| **GIVES** | A complete Define case assembles a gate document · a metric's stated baseline and target are traceable to a registry name |
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
23-field `PhaseState`** — which is what those tables always actually contained.
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
pins that it reaches the last field; §39.x.7 describes per-phase usage with
all thirteen `{Phase}State` references gone; S-C03 amended; and the Define gate
document, viewed in the browser, shows a computed figure that the coach did not
retype.

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
| **Status** | **`BLOCKED-ON-SPEC`** — missing artefact: the validator's RETURN SHAPE (G-23, coupled to G-31). Owner: **founder**. Recorded 2026-09-23 |

> ### ⛔ WHY THIS STEP HAS NO DONE-WHEN, STATED RATHER THAN LEFT QUEUED
>
> **The validator's RETURN SHAPE is undecided, and it is coupled to G-31.**
> Layer 2b must report which gate-required fields are missing; what it returns
> — and whether `check_gate_status()` is that function, a caller of it, or a
> second answer to the same question — is **G-23, coupled to G-31**
> (`check_gate_status()` is named across this architecture and is **absent from
> the tree**).
>
> **A Done-when cannot be written over an undecided return shape.** It would
> have to assert on a structure nobody has chosen, and the test would then pin
> the guess rather than the decision — which is how a placeholder becomes the
> design by default. **The board now shows WHY this is queued, not merely
> that it is**, which is the whole point of recording a blocker in the row.
>
> **What is NOT blocked**: the forward-note below is independent of the return
> shape and stands whatever the founder rules.

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
| **Status** | **`BLOCKED-ON-SPEC`** — missing artefacts: the validator's return shape (G-23) **and the Define rubric TEXT** (G-40). Owner: **founder**. Recorded 2026-09-23 |

> ### ⛔ WHY THIS STEP HAS NO DONE-WHEN, STATED RATHER THAN LEFT QUEUED
>
> **Two decisions, and this step cannot be written over either.**
>
> | | Blocker |
> |---|---|
> | **G-23**, coupled to **G-31** | Inherited through 7.1 — Layer 2c runs on what 2b returns, so an undecided return shape is undecided here too |
> | **G-40** | **The Define rubric TEXT does not exist.** Layer 2d grades against `PHASE_RUBRIC`; what Define's criteria SAY is domain content, not engineering, and no amount of build work produces it |
>
> **G-40 is the harder of the two and the reason it must be a founder
> decision**: a rubric written by an implementer is a guess at what good
> coaching looks like, graded by a model, at a gate that blocks a Belt.
> **The failure mode is invisible and expensive** — a plausible rubric passes
> plausible work.
>
> **The grader clause that used to sit on 6.20 belongs HERE**, and moved on
> 2026-09-23: §62.9 B3 already specifies it — *“scan
> `artifacts["computation_results"]` for the relevant tool entry rather than
> asking the model”* — and that is Layer 2d's scan, not
> `DMAICGraderMiddleware`'s. ARCHITECTURE.md v1.69(B) corrects §7 and §39.3.7,
> which named “the grader” and put a gate check on the turn path.

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
| **Label** | **`7.3a`** — the 2026-09-23 split's own name for this half |
| **Reference §** | §33 · §33.1 · §33.2 · **§19.6** · **S-C25 · S-F27** |
| **Precondition** | **6.44** (the stop is in a node) **AND 6.42's idempotent write**. **NOT 7.1, NOT 7.2** — narrowed 2026-09-23 |
| **NEEDS** | A Belt contradicting a gate-approved value is stopped, and the run resumes from the stop (6.44) · the closing write is safe to perform twice (6.42) |
| **GIVES** | The gate pauses for a human and the pause is resumable · an approval is recorded once, with its actor |
| **Verify** | `manual-UI` |

> ### ⇒ NARROWED 2026-09-23 — THE PAUSE LEAVES THE RUBRIC BEHIND
>
> **This step is now the PAUSE half only.** The remaining steps of §33's
> nine-step gate that consume validation results are **step 7.8**.
>
> **Its precondition was `7.2`**, so the graph's ability to STOP for a human sat
> behind Layer 2d's ability to GRADE — and 7.2 is `BLOCKED-ON-SPEC` on the
> Define rubric text, founder content that does not exist. **That made founder
> content a critical-path dependency of a working gate, which it is not.**
>
> **A gate that checks required fields, assembles a document, stops for a human
> and records the answer is a WORKING gate.** Grading is what makes it a good
> one, and that is 7.2's job.
>
> **SOURCE-VERIFIED CONSTRAINT, re-fetched 2026-09-23** from
> `docs.langchain.com/oss/python/langgraph/interrupts`: *"To use `interrupt()`,
> you need: 1. A checkpointer to persist the graph state."* **ASSERT IT AT
> RUNTIME RATHER THAN ASSUME IT.** §16 already puts the checkpointer on the
> parent and §1.7 bans `InMemorySaver` everywhere — but a pause raised into a
> graph with no saver is the failure mode that looks like a hang, and the
> assertion costs one line.

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

> ### ⇒ RECORDED, NOT SCHEDULED — PROJECT MEMBERS AND SIGN-IN
>
> **A case is opened against a free-text name today.** Project membership and
> sign-in are **OUT OF SCOPE NOW** and are not a step.
>
> **The constraint they place on work in flight is binding anyway**: the gate
> approval record **carries an ACTOR value from the outset**, so an identity
> can be substituted later without changing the structure. The same constraint
> binds the change log's owner — `field_log` entries carry an actor for the
> same reason.
>
> **A field added later changes a shape; a field designed in from the start
> changes nothing.** `field_log` shipped at 6.33 without one, so that half is
> already a retrofit — which is the argument for not repeating it here.

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

**3 — THE CASE RECORD HAS ONE WRITER, OR THE WRITE CARRIES ITS ETag.** Added
2026-09-23. **This is the step that switches the output mapper on**, and the
output mapper writes the case record at the same moment the HTTP route does.
Azure Blob's default is **last-writer-wins**, and nobody chose it: a gate
approval landing while a coaching turn's `save_case` is in flight loses
whichever finished first, silently and without an error on either side.

**Two acceptable answers and the step must pick one out loud:**

| | |
|---|---|
| **The route stops writing** | §10's own rule — the case blob is written *“never mid-conversation”* — and step 10.2 is already scheduled to move the conversation into the checkpoint. The per-turn write would end where §10 says it should |
| **The write carries the ETag it read, and a 412 is handled** | Optimistic concurrency. The loser of the race **learns that it lost** instead of overwriting, and what it does next is a decision rather than an accident |

**What is NOT acceptable is reaching this step without answering**, which is
why it is a Done-when clause and not a note: today the collision is
unreachable because the output mapper never fires, and this step is what makes
it reachable. **A race that arrives with the feature that creates it is the
cheapest one to have prevented and the most expensive to diagnose.**

> **Why clause 1 is here and not left to a comment.** The guard lives in
> `backend/middleware/contradiction.py` — §19.6's file, not §33's — and a
> commented-out line in another section's module is exactly the kind of thing
> that survives a step nobody thought to check it against. **A gate condition
> is read when the step is closed; a comment is read when someone opens the
> file.** The two tests above make it fail loudly in between.

> ### ⛔ CLAUSE 1 AND STEP 6.44 DISAGREE — RECORDED 2026-09-23, NOT RESOLVED
>
> **Clause 1 requires position 6's `interrupt()` call to be RESTORED in
> middleware. Step 6.44 moves the stop OUT of middleware and into a node.**
> Both are founder-ratified, five weeks apart, and they cannot both be built.
>
> **Neither is edited here**, because a disagreement between two rulings is a
> decision and not a typo — the standing rule this document applies to every
> spec-versus-decision conflict it finds. **What is recorded is that the
> conflict exists and where**, so whichever step is built first does not
> silently settle it.
>
> **The substance, stated so the decision does not have to be re-derived**:
> `interrupt()` raised from `after_agent` is the shape G-15 ruled against —
> an exception from middleware is not resumable by construction, and clause 1's
> own measured defect was *“a fired interrupt parks the case forever.”* 6.44's
> node placement is the answer to that measurement. **Clause 1 may therefore be
> the older half of the same finding rather than a competing design** — but
> that is an argument, and this is a founder's call.

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

---

## Step 7.7 — The approve endpoint

| | |
|---|---|
| **Reference §** | §33 · §49 · §50 · S-F34 · S-F13 |
| **Touches** | `backend/gateway/routes.py` · `backend/gateway/schemas.py` · **`ui/index.html`** · `backend/tests/` |
| **Precondition** | **7.3** — the gate pauses and the pause is resumable. Not started |
| **NEEDS** | The gate pauses and the pause is resumable (7.3) |
| **GIVES** | A Belt approves a gate document and the approval reaches the paused run · the approval record names WHO approved it |
| **Verify** | `manual-UI` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**The gate can be reviewed and cannot be approved.** `GET /gate/review/{case}/{phase}`
serves the assembled document — the READ half, built at 3.4 — and §49's own
endpoint table names `/gate/approve` and `/gate/reject` as **unbuilt** (G-47).
So the nine-step HITL flow stops at step 4: the Belt sees what they are being
asked to approve and has nowhere to say yes.

**It depends on 7.3 and cannot be pulled forward.** An approval has to reach a
graph that is PAUSED — `interrupt()` is what creates the thing an approval
resumes, and until it exists there is no pause to deliver a decision to. An
approve endpoint built first would either write the gate directly, which is the
single-writer violation §5 B2 forbids, or hold the decision somewhere until the
interrupt arrives, which is a queue nobody designed.

**Done when:** the browser can approve a reviewed gate; the approval **reaches
the paused graph**; and a `live-run` closes Define from the screen.

---

## Step 7.8 — The gate steps that consume validation results

| | |
|---|---|
| **Label** | **`7.3b`** — the 2026-09-23 split's own name for this half |
| **Reference §** | §33 · §33.1 · §33.2 · §34 · §35 · S-C25 · S-F27 |
| **Touches** | `backend/phases/nodes_common.py` · `backend/validation/` · `backend/tests/` |
| **Precondition** | **7.2** — Layers 2c and 2d. `BLOCKED-ON-SPEC` on the Define rubric text |
| **NEEDS** | The gate pauses and the pause is resumable (7.3) · a graded verdict exists to consume (7.2) |
| **GIVES** | *(empty — this step is off the Define critical path; its rows arrive with the 23)* |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**The half of §33's nine-step gate that reads what the validation stack
produced** — the policy advisory's presentation, the rubric verdict reaching
the Belt, the tier split and the `warning` path. It is separated from the pause
because it depends on something the pause does not.

> ### ⇒ WHY THE SPLIT, AND WHAT IT COST TO LEAVE IT JOINED
>
> **7.3's precondition was `7.2`.** So the graph's ability to STOP for a human
> sat behind Layer 2d's ability to GRADE — and 7.2 is `BLOCKED-ON-SPEC` on the
> Define rubric text, which is founder content that does not exist.
>
> **That made founder content a critical-path dependency of a working gate**,
> which it is not. A gate that checks required fields, assembles a document,
> stops for a human and records the answer **is a working gate**. Grading is
> what makes it a good one, and that is 7.2's job.
>
> The pause half keeps the number **7.3** and is narrowed in place; this is the
> remainder. Nothing is renumbered.

**Done when:** the remaining steps of §33's nine-step gate that consume
validation results are built, against a rubric that exists.

# Part 7 — Stage 8: Reliability

---

## Step 7.9 — Define end to end, on one fresh case

| | |
|---|---|
| **Reference §** | §39.1 · Appendix H |
| **Touches** | *(none — a proof)* |
| **Precondition** | every other step on the Define path (Appendix F's `Order` 1–19) |
| **NEEDS** | Every Define capability row's owning step landed |
| **GIVES** | The vertical — a Belt completes Define and closes its gate |
| **Verify** | `live-run` |
| **Status** | **RULED — founder 2026-09-25** |

**Done when:** every Define capability row in Appendix H is green **on one
fresh case that carries an upload**, from its own check, in one run.

---

## Step 7.6 — The re-approval cascade (§37)

| | |
|---|---|
| **Reference §** | §37 · §9.5 |
| **Touches** | `phases/gate_assembly.py`, `phases/nodes_common.py` |
| **Precondition** | **7.3 AND 8.2 — both HARD** (8.2 recorded 2026-09-23) |
| **Verify** | `pytest` |

> ### ⛔ 8.2 IS A PRECONDITION, NOT A NOTE — RECORDED 2026-09-23
>
> **§37's own words:** *“a cascade that marks phases provisional but leaves
> published values in place is worse than no cascade.”* Marking a phase
> provisional is a COMPENSATING ACTION, and compensating actions are step
> **8.2**. **Today 7.6 is reachable first** — its only recorded precondition
> was 7.3 — so the order the spine permits is the order §37 names as worse
> than not building it at all.
>
> **Why “worse than no cascade” and not merely incomplete**: a phase marked
> provisional while its values stay published tells a reader the document is
> under review AND shows them the figures as though they stood. A reviewer who
> trusts the mark stops checking; a reviewer who trusts the figures never sees
> the mark. **No cascade at least leaves one consistent story.**
>
> Recorded as a precondition rather than a note **because a note does not
> block** — the board reads the row, and a hazard that renders as prose beside
> a schedulable step is a hazard the schedule ignores.

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
| **Precondition** | 7.6 — **the executor slice ran ahead of it on 2026-09-24, by founder ruling** |
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

> ### ⇒ MEASURED 2026-09-24 (6.46 Part A, item 0)
>
> **No contextual labels exist anywhere yet.** None of the three indexes has a
> label field, and the knowledge chunks carry no preamble in their text either —
> they start mid-sentence (*"').
A Mobile Computer that has 1 broken video
> screen…"*). `improve_knowledge_index_v3` 1,184 documents, `improve_evidence_index`
> 2 (G-97), `improve_case_index` 0 (G-94). All three vectors are 3,072-dimensional;
> the case index's is still `embedding`. **The case index defines a semantic
> ranker (`improve-case-semantic`) that no query uses** — every search is hybrid
> keyword + vector, with no `query_type` set.

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

## Step 6.36 — The register's readers read either document

| | |
|---|---|
| **Reference §** | §55.1 · §55.2 · §66 · §0.32 · Appendix D · Appendix F |
| **Touches** | `.claude/hooks/_register_source.py` **(new)** · `.claude/hooks/commit-msg-refactor-guard.py` · `.claude/hooks/build_board.py` · `backend/tests/test_register_dual_read.py` **(new)** · Appendix D · Appendix F |
| **Precondition** | **6.31** — Appendix F is the leading document for build status. Landed |
| **Verify** | `pytest`, the board regenerated byte-identically, plus a mutation proof per reader per §0.4 |
| **Status** | **RULED — founder 2026-09-18. Built** |

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

### Done when

`_register_source.py` states the two locations, their order and the step that
deletes it; rule 8 resolves a gap number from **either** document and
`build_board.py` prefers the procedure; `test_register_dual_read.py` proves
**both paths for each of the three readers** with injected documents, because
neither the present state nor the post-6.37 state exercises both; a mutation
proof per reader per §0.4, with the test name recorded and not only the count;
the regenerated board is **byte-identical** to the regeneration at the same
commit before the change — this step changes plumbing, not output; and the
dual-read is marked TEMPORARY in the code with **step 6.38** named as its
removal, a number asserted to resolve in Appendix D.

---

## Step 6.37 — The repartition — the operational register moves to the procedure

| | |
|---|---|
| **Reference §** | §55.1 · §55.2 · §66 · Appendix D · Appendix F |
| **Touches** | `../ARCHITECTURE.md` (§66 out, 70 markers out, §56 amendment) · Appendix F · Appendix D · `backend/tests/test_operational_register.py` **(new)** |
| **Precondition** | **6.36** — the readers resolve from either document |
| **Verify** | `pytest`, `verify_built.py`, and the board regenerated byte-identically at a fixed commit |
| **Status** | **RULED — founder 2026-09-18. Not built** |

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

### Done when

§66 and all 70 markers are gone from `ARCHITECTURE.md`, which carries no status
of any kind; the operational register in this document carries one row per
fact with `container`, `to-be`, `as-is`, `state`, `gap` and `step`; the 70th
marker's prose form is normalised rather than dropped; G-19's closure is
expressed in the row's own state and not in prose; every gap has a step or the
word `unscheduled`; `verify_built.py`'s matrix checks are restated for the new
row key and still fail closed; a test asserts the §-to-row correspondence in
both directions — the rule §66's header has always claimed is *checkable* and
which **nothing has ever checked**; and the board regenerated at a fixed commit
before and after the move is byte-identical.

---

## Step 6.38 — The dual-read is removed — one register, one reader

| | |
|---|---|
| **Reference §** | §55.1 · §66 |
| **Touches** | `.claude/hooks/_register_source.py` **(deleted)** · `.claude/hooks/commit-msg-refactor-guard.py` · `.claude/hooks/build_board.py` · `backend/tests/test_register_dual_read.py` |
| **Precondition** | **6.37** — the register has moved |
| **Verify** | `pytest`, the board regenerated byte-identically |
| **Status** | Not built |

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

### Done when

`_register_source.py` is absent; no reader names `ARCHITECTURE.md` as a
register source; `grep -rn "REMOVED_BY_STEP" .claude/` returns nothing; the
Appendix F row is flipped to `✅ absent: repo:.claude/hooks/_register_source.py`;
and the board is byte-identical across the change.

---

## Step 6.41 — The symbol-anchor ratchet comes down (G-87)

| | |
|---|---|
| **Reference §** | §55.1 · §55.2 · Appendix F · G-87 |
| **Touches** | Appendix F · `.claude/hooks/verify_built.py` · `backend/tests/test_anchor_ratchet.py` **(new)** |
| **Precondition** | **6.40** — both populations and every section declared, so the denominator stops moving |
| **Verify** | `pytest`, `verify_built.py`, plus a mutation proof per §0.4 |
| **Status** | **RULED — founder 2026-09-18. Not built** |

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

### Done when

The unanchored count is **split** into *anchorable, not yet anchored* and
*nothing to anchor to*, each pinned separately; the first number is **lower
than at 6.40** and the check fails if it rises; `matrix_anchors` still
evaluates every anchor that exists, so none of the new ones is decorative; a
mutation proof shows the ratchet red on a fact whose anchor was removed; and
`pytest` green.

---
## Step 6.39 — The spec-entry population joins the register (assertion 5)

| | |
|---|---|
| **Reference §** | §55.1 · §66 · §57–§65 · Appendix F |
| **Touches** | Appendix F · the gap register · `.claude/hooks/verify_built.py` · `backend/tests/test_spec_entry_rows.py` **(new)** |
| **Precondition** | **6.37** — the marker population has moved and the row shape exists |
| **Verify** | `pytest`, `verify_built.py`, plus a mutation proof per §0.4 |
| **Status** | **RULED — founder 2026-09-18. Not built** |

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

### Done when

All 96 spec entries carry a row keyed on their `S-id` and their §; the 26 gaps
above name a real fact rather than `unscheduled`; **assertion 5 is live in
`verify_built.py` and fails closed**; a mutation proof shows it red on a gap
naming a fact that does not exist; and `pytest` green.

---

## Step 6.40 — Every section declares a row or declares itself not-markable (assertion 7)

| | |
|---|---|
| **Reference §** | §55.1 · §55.2 · Appendix F |
| **Touches** | `../ARCHITECTURE.md` (the `NOT-MARKABLE` declarations) · `.claude/hooks/verify_built.py` · `backend/tests/test_not_markable_coverage.py` **(new)** |
| **Precondition** | **6.39** — both populations are in the register |
| **Verify** | `pytest`, `verify_built.py`, plus a mutation proof per §0.4 |
| **Status** | **RULED — founder 2026-09-18. Not built** |

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

### Done when

Every one of the 285 numbered sections either owns a row or carries a
`NOT-MARKABLE` declaration with its reason; **assertion 7 is live and fails
closed**; the four redirect-form declarations still name a resolvable target;
a mutation proof shows it red on a section stripped of both; and `pytest` green.

---

## Step 6.35 — The hop cap matches the ceiling that was always in force (G-83)

| | |
|---|---|
| **Reference §** | §26 · §25 · §3.7 · §44 · S-F09 · G-83 |
| **Touches** | `backend/phases/nodes_common.py` · `backend/tests/test_hop_cap.py` **(new)** · `backend/tests/test_executor.py` · `.claude/hooks/verify_built.py` · `../ARCHITECTURE.md` (§26, §56 amendment) |
| **Precondition** | **6.34** — the node budget the cap must fit inside. Landed |
| **Verify** | `pytest`, plus two mutation proofs per §0.4 |
| **Status** | **RULED — founder 2026-09-18. Built** |

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

**Done when:** `COACH_HOP_BUDGET == 3`; a full-budget turn's worst case fits
`EXECUTOR_SOFT_BUDGET` **and a test asserts it**; the same test REJECTS five and
rejects four, so the cap is provably the ceiling; `MEASURED_HOP_SECONDS` cites
its traces; `verify_built.py`'s *hop caps* expectation reads `3 / 2 / 50`;
§26 is amended under §56 with a version bump; the deferral is recorded against
9.0's condition; two mutation proofs per §0.4; and `pytest` green.

---

## Step 6.34 — A node that runs out of time answers the Belt instead of failing (G-84)

| | |
|---|---|
| **Reference §** | §4.8 · §44 · §45 · §3.7 · G-84 |
| **Touches** | `backend/phases/nodes_common.py` · `backend/phases/subgraph_common.py` · `backend/tests/test_executor_timeout.py` **(new)** |
| **Precondition** | none — **READY** |
| **Verify** | `pytest`, plus three mutation proofs per §0.4 |
| **Status** | **RULED — founder 2026-09-17. Built** |

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

**Done when:** an agent outliving the budget yields a 200 with
`_TIMEOUT_MESSAGE` and `structured_response is None`; the message names what
happened and leaks no internals; `partial_timeout` is written to `step_log` and
outranks the other outcomes; the soft budget is asserted below the wall at
import AND the headroom is pinned by a test; the guard is verified by `ast`
rather than by grep; **three mutation proofs per §0.4** — remove the guard,
remove the handler, invert the two limits — each shown red then green; and
`pytest` green.

---

## Step 6.33 — The capture path accumulates — a field survives the next turn

| | |
|---|---|
| **Reference §** | §6 · §7 · §11 · §20 · §39.1 · S-C02 · S-F04 · G-78 |
| **Touches** | `backend/core/substate.py` · `backend/core/graph.py` · `backend/core/conversation.py` · `backend/phases/mappers_common.py` · `backend/phases/*/mappers.py` · `backend/phases/nodes_common.py` · `backend/storage/models.py` · `backend/gateway/routes.py` · `backend/tests/` |
| **Precondition** | none — **READY**. Independent of 6.20, which is in flight |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-15. EXTENDED — founder 2026-09-21** |

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

**Done when:** the input mapper seeds `artifacts` from the case record rather
than blanking it, on the same argument 6.11 used for `uploads`; the write
MERGES into `structured` rather than replacing it, so a field captured on turn
1 is still present after turn 5; a capture whose value is empty is **reported
rather than silently dropped**, so the log and the write can no longer disagree;
a test drives **five successive turns** and asserts all five fields are present
at the end — a single-turn test passes today and proves nothing; and a
`live-run` on `IMPR-2026-0E5` captures fields across at least two turns with
both surviving into the gate document.

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

| | |
|---|---|
| **Reference §** | §33 · §40 · §50 · §63.9 · S-F07 · S-F28 · G-78 |
| **Touches** | `backend/gateway/routes.py` · `backend/phases/gate_assembly.py` · `backend/tests/` |
| **Precondition** | **6.33** — the capture path accumulates. Landed |
| **NEEDS** | A complete Define case assembles a gate document (6.20) |
| **GIVES** | An approved phase is recorded once and correctly · the record of a phase survives the write that closes it · the closing write is safe to perform twice |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

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

**Done when:** the document is assembled from the captured field set rather
than from `_validated`; assembly **REFUSES** rather than writing a partial or
empty document, so advancing to Measure with no record is impossible by
construction; a test asserts a twelve-field case yields a complete document
**and fails when the source is emptied**; and a `live-run` on `IMPR-2026-0E5`
produces a document carrying all twelve.

---

## Step 6.43 — The coach can read an uploaded document

| | |
|---|---|
| **Reference §** | §29.1 · §32 · §50 · S-F57 · G-82 |
| **Touches** | `backend/knowledge/tools.py` · `backend/gateway/routes.py` · `skills/` · `backend/tests/` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**An artefact is reachable only as a 160-character summary, and no tool can
read one** (G-82). The Belt uploads a to-be process map; it is classified an
artefact, so it never enters `improve_evidence_index`, and the only tool that
reads a file directly — `load_evidence_series` — computes statistics over a
numeric column. **A prose document has no numeric column.** So the coach can
see that a map exists and cannot read a word of it.

**The label is wrong in the same place.** `routes.py:48` maps `"Process map"`
to **`"as-is process map"`**, unconditionally — while `classifier.py:36`
carries the reason it must not: *"a to-be map is a design, not an
observation."* Every uploaded map is therefore recorded as a statement about
the present, including the ones that are proposals about the future, and
§29.1's evidence/artefact split exists precisely to keep those apart.

> ### ⇒ THE SUMMARY TRUNCATION IS NOT LIFTED, AND THAT IS THE EARLIER RULING
>
> **Discovery and access stay distinct.** The 160-character summary is how the
> coach learns a document EXISTS without carrying its contents into every
> prompt; lifting it would put whole documents into the context window on turns
> that never needed them, which is what §19.3's compression exists to avoid.
> **The fix is a tool the coach CALLS when it decides it needs the text**, not
> a wider window. A per-kind usage instruction is what makes that decision
> teachable rather than hoped for.

**Done when:** a tool returns the text of a named uploaded artefact; a per-kind
usage instruction tells the coach when to reach for it; the label that calls
every uploaded map an as-is map is corrected; and a `live-run` quotes from a
process map the Belt uploaded. **The summary truncation is NOT lifted.**

---

## Step 6.44 — The contradiction stop moves from middleware into a node

| | |
|---|---|
| **Reference §** | §37 · §19.6 · §17 · S-C05 · S-C10 · S-F13 · G-15 · G-89 |
| **Touches** | `backend/middleware/contradiction.py` · `backend/phases/nodes_common.py` · `backend/phases/subgraph_common.py` · `backend/core/substate.py` · `backend/tests/` |
| **Precondition** | **the §37 correction** — ARCHITECTURE.md v1.69. Landed with this amendment |
| **NEEDS** | An approved phase is recorded once and correctly (6.42) — a stop that writes twice is only visible once a write exists to duplicate |
| **GIVES** | A Belt contradicting a gate-approved value is stopped, and the run resumes from the stop |
| **Verify** | `pytest` + a resume test |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**§37 specified a stop mechanism its own ruling forbids.** The section said
`ContradictionDetectionMiddleware` *"raises `HITLInterrupt`"*; that class is
**deliberately never defined** (G-15, ruling v1.21(D)), because a pause must be
resumable and an exception raised from `after_agent` is not. ARCHITECTURE.md
v1.69 corrects the text to name LangGraph's own `interrupt()`. **This step
builds where it is raised**, which the correction deliberately left open.

**Detection does not move.** The coach already sets `contradiction_flag` in the
response call that runs every turn — no additional model call, which is §37's
own mechanics and DECISIONS §R1's ruling. What moves is the STOP: a node can
`interrupt()` and be resumed; middleware cannot.

> ### ⛑ THE NODE WRITES NOTHING, AND THAT IS THE WHOLE OF THE RESUME PROBLEM
>
> **A resumed graph re-executes the node it paused in.** A stop node that also
> wrote state would write it twice — once before the pause and once on resume —
> and for a contradiction that means the same flag recorded twice against one
> event. §11's deterministic key exists for exactly this class and `field_log`
> now enforces it (step 6.33), but **the cheaper answer is a node with nothing
> to write**: it reads the flag, it pauses, and every durable write stays in
> the nodes that already own one.

**`CoachingResponse` gains a `reason` field in this step — G-89's named
owner.** The field change log declares a `reason` column that nothing
populates, because S-C05's `fields_captured` description names `field_name`,
`value` and `source` and no more. This step is already inside that schema and
inside the contradiction path, where the Belt's stated reason for changing a
value is exactly what a reviewer needs. **It is a §56 amendment to S-C05 and
carries one**; it is a clause here rather than a step of its own because a
one-field schema change with no reader of its own is not a step.

> ### ⛔ SOURCE-VERIFIED CONSTRAINT — re-fetched 2026-09-23
>
> `docs.langchain.com/oss/python/langgraph/interrupts` documents `interrupt()`
> in **node functions** and in **tools** (`@tool`-decorated, for approval
> workflows inside a tool). **Middleware is not mentioned anywhere on that
> page.**
>
> **So the move into a node is not a preference between two supported
> placements.** It is the difference between a documented one and one the
> framework's own documentation does not describe — which is what G-15 ruled
> on argument in September 2026 and what the source now says independently.

**Done when:** detection stays where it is — the coach sets the flag in the
reply it already writes, no extra model call; the planner routes on that flag;
the stop lives in a node that writes nothing; a resumed turn is **proven to
write once rather than twice**; `CoachingResponse` carries `reason` under a §56
amendment, closing G-89; and §37 no longer names a stop mechanism that was
ruled never to exist.

---

## Step 6.45 — The planner decides on field completeness

| | |
|---|---|
| **Reference §** | §17 · §39.1.2 · S-F13 · S-C04 |
| **Touches** | `backend/phases/nodes_common.py` · `backend/tests/` |
| **Precondition** | **6.33** — the accumulator is real. Landed |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**S-F13's DP1 predicate is a placeholder and says so in its own docstring.**
`nodes_common.py:326` reads `turn_count` and routes on whether the phase has
coached at all — *"the smallest rule that TERMINATES"*, in the docstring's own
words, against a DP1 that is supposed to read the per-phase field ordering and
decide **"field complete"**.

**It could not have been built before 6.33.** The real predicate asks whether
the field under coaching has been captured, and until the capture path
accumulated, `artifacts` was blanked every turn — so the honest answer was
always "no" and a predicate reading it would have re-asked the same field
forever. **The 4.1 predicate did exactly that** and ran until
`GraphRecursionError`, which is why the placeholder exists at all.

**Done when:** the real S-F13 DP1 predicate replaces the turn-count
placeholder; a test proves a field is **re-asked while incomplete and not
re-asked once complete**; and the placeholder's self-disclaiming comment is
gone — because a comment describing code that no longer exists is the drift
this document's §55 rules are written against.

> **2026-09-25 (founder):** the completeness predicate reads **6.61's field
> status** — a field is complete when its status is *confirmed by the Belt*. 6.61
> runs first (Appendix F `Order`).

---

## Step 6.46 — The coaching script is guaranteed to reach the model, or its absence is recorded

| | |
|---|---|
| **Reference §** | §32 · §19.2 · §43 · S-C12 |
| **Touches** | `backend/middleware/skills.py` · `backend/phases/nodes_common.py` · `backend/tests/` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

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

**Done when:** a turn coached without the script is **distinguishable from one
coached with it, in the record** — so the question *"did this coaching turn
have its methodology"* is answerable after the fact rather than by re-running
it; and **no value the coach offered as an EXAMPLE is captured as the Belt's
data** (§22), proven on a turn where the example and the Belt's own answer
differ.

---

## Step 6.47 — Durable writes inside a node, and persistence loss is never silent

| | |
|---|---|
| **Reference §** | §10 · §10.2 · §16 · §47 · S-C06 |
| **Touches** | `backend/storage/blob.py` · `backend/core/store.py` · `backend/phases/nodes_common.py` · `backend/tests/` |
| **Precondition** | none — **READY** |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**Two failures of the same kind.** An intermediate write made inside a node is
a no-op, so state a node believes it persisted is not there; and an
unconfigured connection string reports itself **in a log line** —
`storage_configured()` returns `False` and callers degrade — so a deployment
with no storage runs, answers, and loses everything, looking healthy
throughout.

**The second is the one that decides the shape of the first.** A write that
cannot succeed must fail where it is made, not where its absence is eventually
noticed. §47's disconnect policy already turns on this distinction: what it
guarantees is *"no node runs, and no checkpoint is written, after the client is
gone"* — a guarantee about WHEN writes stop, which is meaningless if a write
can quietly not happen at all.

**Done when:** intermediate node writes are no longer a no-op; and an
unconfigured connection string **fails loudly rather than in a log line**.

## Step 6.48 — A captured value carries its declared type

| | |
|---|---|
| **Label** | **`CO-1`** — the 2026-09-23 ruling's own name for this step |
| **Reference §** | §7 · §20 · §41 · §63.8 · S-C05 · S-C32 · S-C33 · S-F28 |
| **Touches** | `backend/phases/gate_registry.py` · `backend/phases/nodes_common.py` · `backend/gateway/routes.py` · `skills/dmaic-define-phase/` (SKILL.md **and** coaching_script.md, §56.1's atomic unit) · `backend/tests/` |
| **Precondition** | none — **READY** |
| **NEEDS** | *(nothing — it is the head of the critical path)* |
| **GIVES** | **Capability row 18**, container 4 — *"captured values carry their declared type"*. Check: team, scope, the SIPOC map and the registry arrive structured, not as prose, on a live run — `backend.tests.test_declared_types::test_row_18_captured_values_carry_their_declared_type` |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

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

**Done when:** a value the Belt states is stored in the shape its schema
declares, for all four structured Define fields; a capture that cannot be
coerced into its declared shape is **REPORTED by field name and not silently
stored as prose**; a test drives each of the four and fails when the coercion
is removed; and a `live-run` on `IMPR-2026-0E5` produces a case whose thirteen
captured values all satisfy `DefineOutput`'s declared types.

## Step 6.49 — The checks card — twelve capability rows get the check that proves them

| | |
|---|---|
| **Reference §** | §43 · §47 · §51 · §55.1 · Appendix H |
| **Touches** | `backend/tests/` · `agent-improve/docs/REFACTORING_PROCEDURE.md` (Appendix H) |
| **Precondition** | **Appendix H's seed for rows 1, 2, 5, 6, 8, 10, 11, 12, 13 and 17** — landed 2026-09-23 |
| **NEEDS** | *(nothing in code — the rows it checks are already built or already false)* |
| **GIVES** | Capability rows **1, 2, 5, 6, 8, 10, 11, 12, 13, 17, 33 and 35** — each gets the single executable check that proves it |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

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

**Done when:** each of the twelve rows carries **one executable check**, named
`module::test_name` in its Appendix H row; every check runs in `pytest`; each
one that reads product state **reads what the system wrote and constructs no
input**, on rows 18–21's rule; a row whose check cannot be evaluated **SKIPS
rather than passes**; and each row is marked 🟢 or 🔴 on what its check
actually returns — **no row is marked green by argument**.

---

## Step 6.51 — The baseline and the target are values Control can compare

| | |
|---|---|
| **Reference §** | §7 · §39.1.2 · §63.1 B7 · §39.5.3 · S-C05 |
| **Touches** | `backend/core/substate.py` · `backend/phases/gate_registry.py` · `backend/tests/` |
| **Precondition** | **6.48** — the capture site already validates a declared TYPE; this adds a value check beside it. Landed |
| **NEEDS** | Captured values carry their declared type (row 18, green) |
| **GIVES** | Capability row **25** — the baseline and target are stored as values Control can compare |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**Control computes target-versus-actual, and it cannot subtract a sentence.**
§63.1 B7 requires `baseline_estimate` and `target_value` to be values with
units. The measurement thread §39.1.2 defends — *"do NOT simplify these away"*
— exists so that Control can extract and compare them; a baseline that reads as
prose breaks the comparison three phases later, where nobody is looking.

> ### ⛑ THE LIVE BUG THIS CLOSES, MEASURED ON `IMPR-2026-0E5`
>
> The case carries **`baseline_estimate: "Rework hours range from 6.1 to 25.1,
> averaging 12.78."`** against **`target_value: "3%"`**. Both are `str`, so
> **step 6.48's type check passes them both** — the declared type is satisfied
> and the values still cannot be compared: one is a sentence about hours, the
> other a percentage, and they are not measuring the same thing.
>
> **That pair reached a gate document.** It is in the `phase_metrics` entry
> 6.20 derived, mirrored exactly as the invariant requires — **the mirror is
> correct and the number is unusable**, which is precisely the gap a type check
> cannot see.

**The shape goes on the field description, as S-C05 did at 6.48.** That is the
one channel the model reads on every turn, with nothing to fetch and nothing to
choose, and it is the pattern that turned four prose fields structured on their
first attempt. **Plus a value check at capture**, beside the type check, on the
same argument: a contract that is only described is a contract nothing enforces.

**What "a value with a unit" means is the decision this card carries.** A
number and a unit, parseable, comparable to another value of the same unit —
and a Belt who says *"about 12%"* must not be refused for the "about". §7's law
keeps the Belt's own words; this asks that the words contain a figure Control
can find.

**Done when:** `baseline_estimate` and `target_value` are stored as values that
parse as a number with a unit; the shape is on the field description **and**
checked at capture; a capture that carries no parseable value is **REPORTED by
field name and not stored**, so the coach asks again (§4.8); a test drives the
`IMPR-2026-0E5` pair and fails on it; and a `live-run` produces a baseline and
target that Control could compare.

## Step 6.52 — A turn always answers inside its budget

| | |
|---|---|
| **Reference §** | §4.8 · §19.7 · §19.8 · §44 · §45 · G-84 · G-92 |
| **Touches** | `backend/phases/nodes_common.py` · `backend/knowledge/fusion.py` · `backend/middleware/grader.py` · `backend/middleware/coherence.py` · `backend/tests/` |
| **Precondition** | **6.49** — row 2's check exists and is red on two live turns. Landed |
| **NEEDS** | *(nothing — 6.34's soft budget and the three lookups exist; this makes them hold)* |
| **GIVES** | Capability row **2** (a turn returns a coached reply) and row **13** (the coaching rubric scores the turn) |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-24. Part A reviewed; Part B building** |

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

**Done when:** a slow turn — setup delay plus a blocking lookup — ends in the
node's own degraded answer and a `partial_timeout` entry, never the engine's
`NodeTimeoutError`; no lookup holds the event loop; each judge sees a given
reply once and the grader's verdict is in `step_log`; each fix has a mutation
proof that goes red; and a live open-question turn on `0E5` returns 200 in
under 45 s, recorded by trace id against row 2.

---

## Step 6.54 — The clients are built once, at startup, before any Belt waits for them

| | |
|---|---|
| **Reference §** | §44 · §45 · §51 · G-93 |
| **Touches** | `backend/app.py` · `backend/core/llm.py` · `backend/knowledge/retriever.py` · `backend/tests/` |
| **Precondition** | **8.0's executor slice** — the spans that found the cause. Landed |
| **NEEDS** | *(nothing — the clients exist; this decides WHEN they are built, and how many times)* |
| **GIVES** | Capability row **2** — an open question is coached inside its budget on the FIRST turn in a process |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-24** |

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

**Done when:** six threads on an empty cache produce exactly one build of each
client; a started app leaves no client for a turn to build; mutation proofs
for the lock and the warm-up; and on a restarted server the FIRST turn — an open
question on `0E5` — is coached inside its budget, recorded with its trace id
and *"first turn in process: yes"*.

---

## Step 6.56 — The coaching proof: positions 1–8 of Define, one traced run

| | |
|---|---|
| **Reference §** | §43.1–§43.7 · §22 · §39.1.2 · §51 |
| **Touches** | `scripts/coaching_proof_656.py` (new) |
| **Precondition** | **G-96** and **6.57** committed — landed (`8ceb91b`, `4f6e5c8`, lag fix `d624ff4`) |
| **NEEDS** | A turn's coherence verdict, grade, script step and computed position recorded in `step_log` (G-96, 6.57) |
| **GIVES** | The live-turn evidence the founder marks rows **26–32** from, and the calculation turn row **10**'s check reads |
| **Verify** | `live-run` — ONE traced run |
| **Status** | **RULED — founder 2026-09-24, accepted as proposed and extended to position 8. Traced run HELD (founder, 2026-09-25)** |

**Rows 26–32 are live-turn rows** (§43.1–§43.7): no fixture can show whether a
coach teaches a calculation before running it, shows an example before asking,
or challenges a weak answer. This step is the one traced run they are marked
from.

| | The run |
|---|---|
| **Driver** | `scripts/coaching_proof_656.py` — outside pytest; the app IN-PROCESS; a NEW case titled *"COACHING PROOF — step 6.56, do not use for other proofs"* |
| **Belt** | Scripted, a fictional project whose values differ from every worked example (§22); the answer each turn is chosen by `define_position`, not by a turn counter |
| **Probes** | **Weak answer** at position 4 (row 31) · **example differs** on every capture — the record says whether any captured value matches a worked example (row 27) · the **savings** turn after position 8 (rows 26 and 10) |
| **Never** | submits a gate · retries a turn on an error or a 429 |
| **Limits** | positions 1–8, **hard cap 15 turns**, stop on the first error; in traced mode it stops if a turn made more than one trace |
| **Record** | one JSON line per turn: position before/after, the Belt's message, status, seconds, trace id, fields captured, example refused/matched, tools, calculation rows, coherence (verdict, reason, step), grade, progress written vs the model's |
| **Tracing** | OFF unless `--traced` — `init_tracing()` ignores `LANGSMITH_TRACING=false` (G-101), so the driver uses the test suite's switch and a send counter; a dry run that sends anything aborts |

**Dry runs, 2026-09-25, untraced — 0 LangSmith sends each:** `IMPR-2026-206`
and `IMPR-2026-134` (titled *"COACHING PROOF DRY RUN"*), 11 turns each,
positions 1 → 9, one `computation_results` row each; row 10's check passes on
the second. **They found:** 6.57's lag (fixed, `d624ff4`), G-99's breadth (9
coherence rejections in 22 turns) and G-100 (the savings figure 100× too
large).

**Done when:** ONE traced run, positions 1–8, ≤ 15 turns, delivers the per-turn
evidence table with trace ids; rows 26–32 are left for the founder to mark;
row 10's check runs on the proof case.

---

## Step 6.57 — The Belt's step is computed, not counted by the model

| | |
|---|---|
| **Reference §** | §43.3 · §39.1.2 · §39.1.9 · §19.1 · §50.1 |
| **Touches** | `backend/phases/define/schema.py` · `backend/middleware/state_injection.py` · `backend/phases/nodes_common.py` · `backend/core/substate.py` · `backend/tests/` |
| **Precondition** | none — **READY** |
| **NEEDS** | *(nothing — the field order exists; this decides who computes the count)* |
| **GIVES** | The count behind capability row **28** — *"Step n of 12"* on every coaching turn, the same number the planner walks and step 10.3's bar shows |
| **Verify** | `pytest` + `live-run` |
| **Status** | **RULED — founder 2026-09-24** |

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

**Done when:** the position is computed from `DEFINE_FIELD_ORDER` with position
5 waiting for `metric_definitions`; it is delivered on every model call and
recorded every turn; the gate list is labelled as the gate list; mutation —
remove the delivered count, and the tests fail; and ONE traced turn shows
*"n of 12"*.

---

## Step 6.61 — The coaching move is decided in code

| | |
|---|---|
| **Reference §** | §17 · S-C04 · §19.1 · S-C11 B7 · §20 · S-C05 B7 · §22 · §32 · §43 |
| **Touches** | `backend/phases/nodes_common.py` · `backend/middleware/state_injection.py` · `backend/core/prompts.py` · `backend/core/substate.py` · `skills/dmaic-define-phase/` · `backend/tests/` |
| **Precondition** | none — **READY** (ruled 2026-09-25) |
| **NEEDS** | *(nothing)* |
| **GIVES** | The same move for the same situation, every run — the premise of rows 26–32 — and a stored value that is the Belt's confirmed words |
| **Verify** | `pytest` + a repeated-run consistency proof (tracing off, audit recorder attached) |
| **Status** | **RULED — founder 2026-09-25 (ARCHITECTURE.md v1.75)** |

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

**Done when:** for each Define situation — opening, good answer, weak answer,
read-back awaiting confirmation, Belt confirms, Belt corrects the read-back,
*"where do we stand?"* — the same turn run **5 times gives the same move 5/5**;
the stored value is the Belt's confirmed words (AD5's business case keeps the
suppliers and the stops); nothing is stored before confirmation; the planner's
model makes one judgment (sufficient, with a reason); the coach's input is the
six labelled sections, the move section authoritative, feedback never as a
Belt message; the coaching rules and the Define script carry no move-sequencing
text; tests red before and green after. **D8 closes with 6.62.**

---

## Step 6.62 — The other four phase scripts carry no move-sequencing

| | |
|---|---|
| **Reference §** | §32 · §43 · v1.75 |
| **Touches** | `skills/dmaic-measure-phase/` · `skills/dmaic-analyse-phase/` · `skills/dmaic-improve-phase/` · `skills/dmaic-control-phase/` (SKILL.md **and** coaching_script.md, §56.1's atomic unit) · `backend/tests/` |
| **Precondition** | **6.61** — the move is decided in code, so the scripts can stop sequencing it |
| **NEEDS** | The coaching move is decided in code (6.61) |
| **GIVES** | 6.61's D8 — all five phase scripts free of move-sequencing |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-25** |

**Counted 2026-09-25** (lines carrying confirm / advance / move-on wording):
measure 13, analyse 8, improve 10, control 14. **Done when:** none of the four
carries a move-sequencing instruction, and a test that scans all five SKILL.md
files for it is red before and green after.

---

## Step 6.58 — A percent convention for the computation tools

| | |
|---|---|
| **Reference §** | §69.1 · §69.2 S-F37 · §60.6 B2, B3 · G-100 |
| **Touches** | `backend/knowledge/computation.py` (`_num`) · `ARCHITECTURE.md` §69.1 · `backend/tests/` |
| **Precondition** | none — **READY** (ruled 2026-09-25) |
| **NEEDS** | *(nothing)* |
| **GIVES** | A calculation that cannot be 100× wrong on a percentage — the number row **26**'s teaching turn is about |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-25** |

**G-100.** `calculate_expected_savings` read *"23%"* as 23 and returned
£6,804,000 where the answer is £68,040 — `_num` drops a `%` without rescaling,
by design. **The ruled convention, for every tool that reads a rate:**
*"23%"* → **0.23**; a bare *"23"* where a rate is expected → a **reformatting
request** (§60.6 B3), never a guess. §69.1 is amended to state it once for all
twenty.

**Done when:** the D0 inputs of G-100 — *"23%"*/*"5%"*, *"23"*/*"5"*,
*"0.23"*/*"0.05"* — give 68040, a reformatting request, and 68040; §69.1 states
the convention; a mutation that restores the old `_num` fails the test.

---

## Step 6.59 — The coherence judge rules on the Belt's words, not the coach's

| | |
|---|---|
| **Reference §** | §19.7 · S-C13 · §19.8 · G-99 · G-102 |
| **Touches** | `backend/middleware/coherence.py` · `backend/middleware/grader.py` · `backend/validation/schemas.py` · `ARCHITECTURE.md` §19.7 · `backend/tests/` |
| **Precondition** | none — **READY** (ruled 2026-09-25) |
| **NEEDS** | A reply's script step is derived and every verdict is recorded (G-96, landed) |
| **GIVES** | Rows **13** and **12**'s premise: a turn is graded unless its reply really is a restatement |
| **Verify** | `pytest` + a replay of `IMPR-2026-AD5` (tracing off) |
| **Status** | **RULED — founder 2026-09-25** |

**G-99.** The coherence audit (`IMPR-2026-AD5`, 6 turns, 0 traces) recorded
4 rejections as *"parroting"* where the reply quoted the SCRIPT (turns 1, 3),
summarised values captured on EARLIER turns (5), or read back with no question
(4) — 9 of 22 turns in the two dry runs before it. **The ruling:** the judge's
input separates three things — the **script text** for the step, the **values
already captured**, and the **Belt's words THIS turn**; a parroting verdict must
**quote** the Belt's words this turn, and code checks that quote is in them —
**otherwise the verdict is void**, recorded as void, and does not degrade the
turn.

**Also owned here — G-102:** the grader reads `CoachingResponse.message` only
(`grader.py`, `_coach_text`), so it fails *"show a concrete example"* on turns
whose `example` block carries one. Every judge reads the reply the Belt sees.

**Done when:** replaying AD5's six turns (tracing off), no verdict without a
verbatim quote from the Belt's words this turn degrades a turn; a real parrot
is still rejected; the grader is given all four blocks; mutations: remove the
quote check → a script-quoting reply degrades again.

---

## Step 6.53 — A coherence rejection asks the coach again

| | |
|---|---|
| **Reference §** | §19.7 · §34.2 · S-C13 B2 · §44 · G-104 |
| **Touches** | `backend/middleware/coherence.py` · `backend/middleware/grader.py` · `backend/tests/` |
| **Precondition** | **the latency ruling (founder)** — see below |
| **NEEDS** | The judge's verdicts are trustworthy (6.59) |
| **GIVES** | Row **12** — layer 2a rejects AND re-asks |
| **Verify** | `pytest` + `live-run` |
| **Status** | **GATED — founder: the latency ruling** |

**Today a rejection re-asks nothing.** `coherence.py` makes one check
(`self.attempts = 1`); `max_retries` is stored and never used. **G-104:** the
judge's own prompt says *"the coach retries on that feedback"* — untrue until
this step.

> ### ⛑ THE LATENCY RULING — the question, written down for the first time
>
> **"G-83's latency ruling" is cited by 6.52's card, `grader.py`,
> `stories.py` and G-92, and no document states it.** G-83 itself is CLOSED
> (the hop cap, 6.35). The question, as the record implies it: **can a turn
> afford one more coach call plus one more judgement, inside the executor's
> 40 s soft budget?** Measured: a regeneration is one coach model call
> (~5–10 s at today's prompt size, ASSUMED from the audit's 9.4–14.5 s turns)
> plus one coherence call (~1–2 s); open questions already reach 24 s of
> executor time (6.54, trace `01a0d366…`).
>
> | Option | What happens on a rejection | Cost |
> |---|---|---|
> | **A** | Re-ask once if the remaining budget exceeds a threshold, else pass the reply through | Up to ~12 s on rejected turns |
> | **B** | Never re-ask in the turn; the rejection reason is given to the coach at the START of the next turn | 0 s; the Belt sees the rejected reply once |
> | **C** | Re-ask once, always; the budget is raised to hold it | Up to ~12 s on every rejected turn, and a wall change |
> | **D** | Keep today's behaviour; retire the retry from §19.7 | 0 s; row 12 is re-scoped |

**Done when:** the ruled option is built; a rejected reply is followed by a new
model call (row 12's own check); G-104's prompt line is true.

---

## Step 6.60 — The script already delivered is not fetched again

| | |
|---|---|
| **Reference §** | §19.2 · §32 · S-C12 · G-106 |
| **Touches** | `backend/middleware/skills.py` · `backend/tests/` |
| **Precondition** | **6.46** — the script is in the system message on every call. Landed |
| **NEEDS** | *(nothing)* |
| **GIVES** | One model call fewer on a phase's first turn |
| **Verify** | `pytest` |
| **Status** | **PROPOSED — Claude Code, 2026-09-25 (G-106's owner); founder to rule** |

**G-106.** On the audit's turn 1 the coach called `load_skill("dmaic-define-phase")`
— the phase whose script v1.71 already places in the system message — a whole
model call for text it had. **Done when:** `load_skill` for the phase being
coached returns at once, naming the delivered script's version and hash,
without a second copy entering the conversation.

---

## Step 6.50 — The conformance pass — the tree against the framework's own documentation

| | |
|---|---|
| **Reference §** | §0.24 · §16 · §16.3 · §55.1 · §55.2 · §66 |
| **Touches** | `.claude/hooks/` (new) · `agent-improve/docs/REFACTORING_PROCEDURE.md` (§66) |
| **Precondition** | **none** — it is a check, not a change |
| **Verify** | `pytest` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**Four checkers guard this project and all four compare the tree to OUR
documents.**

| Checker | What it compares |
|---|---|
| `commit-msg-refactor-guard.py` | the commit against **our rules** |
| `verify_built.py` | the tree against **our architecture's claims** |
| `fact-ownership-guard.py` / `drift-check.py` | a document against **our fact owners** |
| `build_board.py` | the board against **our register** |

**Nothing compares the code to what the framework itself documents.** That is
the entire gap, and it is not a gap in coverage — each of the four does its own
job well. It is a gap in *direction*: every one of them closes the loop between
two artefacts this project wrote. **A mechanism used against LangGraph's or
LangChain's documented behaviour satisfies all four**, because our documents
can be internally consistent and externally wrong at the same time.

**The evidence is that five findings came out of one afternoon of reading the
documentation, and none of the four had caught any of them.** Four checkers,
running on every commit for weeks, against defects a person found by reading.

> ### ⇒ THIS IS §0.24's OTHER HALF, AND THE HALF NOBODY RE-RUNS
>
> §0.24 already requires confirming that the framework does not provide a
> thing **before** hand-rolling it, and `/verify-current-version` is the
> mandatory checkpoint before an architectural decision is finalised. **Both
> are forward-looking and both are discharged once, by a person, at the moment
> of the decision.** Nothing looks again.
>
> **A decision confirmed correct in August is not a fact about the tree in
> September** — the library moves, the tree moves, and the confirmation is a
> sentence in a commit body that no longer resolves against anything. This
> step is the standing sweep that §0.24's per-decision discipline cannot be:
> it does not replace `/verify-current-version`, it re-runs what
> `/verify-current-version` concluded.

### The five mechanisms the first run must cover

**Each has already produced a defect, which is why these five and not a survey
of the framework.**

| Mechanism | What the documented default is | The defect it already produced |
|---|---|---|
| **Reducers on accumulating channels** | **An update OVERRIDES** unless the channel declares a reducer | G-78 — `artifacts` was documented as *"the accumulation"* and built from a constant, so every capture destroyed the one before it. Fixed at 6.33, where `field_log` was declared with a reducer for exactly this reason |
| **Where a pause may be called from, and what re-runs on resume** | `interrupt()` is resumable by construction; an exception raised from a middleware hook is not, and the node a pause lands in **re-executes on resume** | G-15 — §37 specified a stop that *"raises `HITLInterrupt`"* against a ruling that the class must never exist. Corrected in text at v1.69; step 6.44 moves the stop into a node |
| **Subgraph invocation, config inheritance and checkpoint namespacing** | A subgraph invoked directly inside a node is statically discovered and namespaced through the parent's saver; invoked behind an indirection it is not | G-44 — and see the open question below, which is this same mechanism and is **not** resolved |
| **The write strategy on the case document** | Azure Blob is **last-writer-wins** unless the write carries an ETag | G-88 — `_ensure_case_record` replaces the whole record every turn, so `asks_by_phase`, written by another writer, is erased before anything reads it. The cross-process version of the same race arrives with step 7.3, whose clause 3 is where it must be answered |
| **Durability of writes inside a node** | A write made mid-node is not guaranteed to survive the node | Step 6.47's first half — intermediate node writes are a no-op, so state a node believes it persisted is not there |

> ### ⛑ THE WORKED EXAMPLE IS ALREADY OPEN, AND IT IS §16's OWN CLAIM
>
> **§16 states that the wrapper's inner invoke *"persists `PhaseState` across
> Belt turns"*** (the G-44 rule), *"verified against current LangChain subgraph
> documentation, 2026-08-24."*
>
> **The tree behaves otherwise, and two places in it say so.**
> `gateway/routes.py` carries *"what it does not yet do is SURVIVE across
> turns: the input mapper rebuilds the child state on every invoke … so the
> cap of 3 still cannot accumulate"*, and
> `test_the_coach_sees_the_prior_conversation_on_turn_two` pins a turn-two
> coach seeing exactly three messages — which it could not, if the subgraph's
> own `messages` channel had persisted and reduced across the turn boundary.
> **Step 6.33 was designed around the same behaviour**: `field_log` is seeded
> from the case record precisely because a reducer cannot carry it across a
> turn.
>
> **WHICH IS WRONG IS NOT DECIDED HERE, AND THAT IS THE POINT.** §16 may mean
> persistence WITHIN a run, the tree may be defeating a mechanism that would
> otherwise work, or the documentation may have moved since August. **All three
> are conformance findings and none is a typo.** It is recorded as the example
> because it is exactly what this pass would emit on its first run — and
> because it was found while building 6.33, by reading, which is the method
> this step exists to replace.

### It runs at a cadence, and it reports

**A check that runs when somebody gets suspicious is not a check** — it is the
reading that produced the five findings, with no guarantee it happens twice.
The cadence is **monthly, and additionally after any LangChain / LangGraph /
LangSmith upgrade**, which is the second trigger and the sharper one: an
upgrade can change documented behaviour underneath a tree that did not move, so
the commit that raises a pin is the commit most likely to invalidate a
conformance conclusion. `upgrade-langchain-stack` is where that trigger binds.

**It REPORTS; it does not fix.** Each disagreement becomes a numbered finding
in §66, with the documented requirement and the tree's behaviour stated side by
side — **the same discipline `reconcile-docs` applies to our own documents, and
for the same reason**: a pass that fixes what it finds decides, silently, which
side was wrong. **On these five mechanisms that is a design decision every
time**, as the worked example above shows.

**Done when:** a pass exists that, **for each framework mechanism this system
relies on**, states what the documentation requires and what the tree does, and
**emits a finding with a number wherever they differ**; its first run covers
the five mechanisms above; it runs at a named cadence rather than on suspicion;
and it **reports without fixing**.

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
against the schema alone; **a turn the grader FAILs
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
| **Status** | **`BLOCKED-ON-SPEC`** — missing artefact: the gate screen DESIGN; no spec entry points at it. Owner: **founder**. **OFF the critical path** (2026-09-23). Recorded 2026-09-23 |

> ### ⛔ THIS STEP HAS NO ARCHITECTURAL SOURCE AT ALL, AND THAT IS A FINDING
>
> **No spec entry points at it, and “conflict panel” appears nowhere in
> `ARCHITECTURE.md`.** The two § citations above are the closest things to a
> source and neither specifies this step: §50 is the Belt-facing surface in
> general, §43.4 gives the worked case for why a blended progress count
> misleads. **The panel itself — what it shows, when it appears, what the Belt
> can do in it, and what happens to the phases it marks provisional — is
> specified nowhere.**
>
> **So a Done-when cannot be written, and writing one anyway is the trap.** It
> would be a description of a screen somebody imagined, and the test behind it
> would pin that imagining as the design. **That is how an unspecified feature
> acquires a specification nobody ratified.**
>
> **RECORDED AS A FINDING, NOT PAPERED OVER.** This is §55.2's shape in the
> other direction: not a claim nothing re-runs, but a step nothing specifies.
> It needs a DESIGN — a ratified section in `ARCHITECTURE.md` that this row can
> cite — before it can carry a Done-when. **Until then it is not schedulable**,
> and the row now says why rather than sitting in the queue looking ready.
>
> **G-71 is the other half**: `ui/index.html` is 7,273 lines of Belt-facing
> product that no step builds and nothing verifies. A step with no source is
> harder to see inside a file with no coverage.

Three §50 surfaces: the live gate document updating on every capture; the
conflict-resolution panel, which **must surface which downstream phases become
provisional *before* the Belt confirms**; and **separate Tier 1 / Tier 2
progress bars, never one blended count** — §43.4 gives the worked case for why a blended count misleads.

---

---

## Step 10.3 — The workspace reads the v2 field names, and progress counts them

| | |
|---|---|
| **Reference §** | §50 · §50.1 · §39.1.2 · §13 · G-71 |
| **Touches** | **`ui/index.html`** · `backend/tests/` |
| **Precondition** | **6.33** — the capture path accumulates. Landed |
| **NEEDS** | A Belt's captured value survives the next turn (6.33, landed) |
| **GIVES** | A Belt can see how far through Define they are, and the count moves when they answer |
| **Verify** | `manual-UI` + a count test |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**The workspace checks for fields the backend stopped writing.**
`GATE_CHECKS.define` in `ui/index.html` reads `structured.what`,
`structured.scope_in`, `structured.scope_out`, `structured.sipoc`,
`structured.hard_benefits`, `structured.current_cost` and
`structured.project_milestones` — **v1 names**. The v2 set is
`problem_statement`, `project_scope`, `process_map_sipoc`, `business_case`,
`team` and the rest of §39.1.2's twelve. **Exactly one key overlaps**:
`goal_statement`.

**So the progress indicator counts a set the coach does not fill.** A Belt can
complete every coached field and watch the bar stay where it was, because the
bar is counting a vocabulary that was renamed underneath it. Before 6.33 this
was invisible — nothing accumulated, so nothing was expected to move.

> ### ⛑ THE 5W2H FIELDS ARE A DECISION, NOT A MAPPING
>
> `structured.what` is not a renamed `problem_statement`. It is one element of
> Define's **5W2H** problem statement — what, where, when, who, why — which
> `SKILL.md` coaches as a technique inside position 1 and which §39.1.2's
> twelve do not carry as separate fields. **There are two honest answers and
> the step must pick one out loud**: the elements get a home in the captured
> set, or they are recorded as **deliberately absent with the reason**, so the
> next reader is not left to infer that seven fields went missing.
>
> **A silent drop is the one outcome that is not allowed here**, and it is the
> class §55.2 exists for: a thing specified in one place, quietly not carried
> in another, with nothing that disagrees.

**Done when:** the page's field list is the v2 set; the counter counts that
set — **and the Define step it shows is `define_progress` (6.57), the same
function the coach's prompt, the reply's `progress` and `field_index` use;
the bar never counts again**; Define's 5W2H fields have a home **or are recorded as deliberately absent
with the reason**; a `manual-UI` pass shows the bar advancing turn by turn; and
**renaming one field back makes the count wrong** — the mutation that proves
the test reads the list rather than a constant.

---

## Step 10.4 — The error contract — a failed turn is readable

| | |
|---|---|
| **Reference §** | §4.8 · §49 · §50 · §12.3 · G-70 |
| **Touches** | **`ui/index.html`** · `backend/gateway/routes.py` · `backend/gateway/schemas.py` · `backend/tests/` |
| **Precondition** | **8.1** — structured errors. Not started |
| **Verify** | `manual-UI` |
| **Status** | **RULED — founder 2026-09-23. Not started** |

**A failed turn reaches the Belt as a raw exception in a three-second toast**
(G-70). `/ask`'s bare `except Exception` returns
`HTTPException(500, f"Graph error: {e}")`, and the UI lands on
`toast('Error: ' + resp.detail)` with `dur=3000`. **The Belt sees a stack
fragment for three seconds and then nothing**, with no way to tell a timeout
from a rate limit from a lost connection — and §4.8's rule is that a failure is
*never a hard failure to the Belt*.

**This closes G-70's Belt-facing half only.** The backend half is §12.3's
`AgentImproveError` and step 8.1, which is why 8.1 is the precondition rather
than a note: a readable condition needs a typed condition behind it, and
inventing one in the UI would put the vocabulary in the layer least able to own
it.

**Done when:** a backend failure reaches the Belt as a **stated condition**
rather than a raw exception in a three-second toast.

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
| **DONE** | 56 | **2.3**, **2.4**, **2.5**, **2.6**, **2.7**, **3.1**, **3.2**, **3.3**, **3.4**, **3.5**, **4.1**, **4.2**, **4.3**, **4.4**, **5.1**, **5.2**, **5.3**, **5.4**, **6.1**, **6.2**, **6.3**, **6.4**, **6.5**, **6.6**, **6.7**, **6.8**, **6.9**, **6.11**, **6.12**, **6.13**, **6.16**, **6.18**, **6.21**, **6.19**, **6.20**, **6.34**, **6.33**, **6.35**, **6.42**, **10.0**, **6.49**, **6.46**, **6.52**, **6.54**, **6.48**, **6.57**, **6.25**, **6.26**, **6.27**, **6.31**, **6.36**, **6.37**, **6.39**, **6.40**, **6.38**, **6.41** |
| **BUILDING NOW** | 1 | **6.43** — The coach can read an uploaded document |
| **BLOCKED** | 10 | **6.14** (BLOCKED), **6.10** (BLOCKED), **6.56** (GATED), **6.53** (GATED), **8.4** (BLOCKED), **8.5** (GATED), **9.0** (EXTERNAL), **9.1** (EXTERNAL), **9.2** (EXTERNAL), **6.22** (EXTERNAL) |
| **QUEUED** | 39 | **10.3**, **6.51**, **8.0**, **6.44**, **7.3**, **7.7**, **10.2**, **7.1**, **7.2**, **7.8**, **7.9**, **7.4**, **7.0**, **7.5**, **7.6**, **8.1**, **6.45**, **6.47**, **10.4**, **6.50**, **8.2**, **6.58**, **6.59**, **6.60**, **6.61**, **6.62**, **8.3**, **8.6**, **8.7**, **10.1**, **6.17**, **6.23**, **11.1**, **6.24**, **6.28**, **6.29**, **6.30**, **6.32**, **11.2** |

*106 rows. DONE is git history — the `refactor(arch-v2): commit X.Y` subjects, intersected with this table, so a step that landed under another subject is not counted. BLOCKED is Appendix D's status column, the only thing git cannot say. Regenerated 2026-09-25.*
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
| D | 470–620 | CROSS-CUTTING | Reliability, transport and cleanup. Nothing here is needed for a slice to work |

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
| 351 | **Commit 6.34** | A node that runs out of time answers the Belt instead of failing (G-84) |  | OPS | SHARED | A slow turn reaches the Belt as a 500 carrying a stack trace, against §4.8, and every remaining live-run verification runs through that path. |
| 352 | **Commit 6.33** | The capture path accumulates — a field survives the next turn |  | PHASE | SHARED | Every coached capture destroys the ones before it, so a Belt filling 26 fields across many turns can never reach a gate. |
| 354 | **Commit 6.42** | The gate document records what Define established |  | GATE | SHARED | A completed Define is recorded as an empty document and the phase advances anyway, so Measure is framed as though the Belt skipped Define. |
| 353 | **Commit 6.35** | The hop cap matches the ceiling that was always in force (G-83) |  | COACH | SHARED | The declared retrieval budget is larger than any turn can spend, so the cap never fires and the coach is cancelled mid-search instead of composing. |
| 355 | **Commit 10.0** | The coaching turn’s output reaches the Belt — four blocks and the grader’s warning |  | UI | SHARED | The coach produces `explanation`, `example`, `prompt` and `progress` every turn and the API discards all four, so §50.1’s render contract stays prompt-hoped and the Belt reads one prose blob. |
| 356 | **Commit 6.43** | The coach can read an uploaded document |  | COACH | SHARED | The Belt uploads a process map and the coach can see that it exists without reading a word of it. |
| 358 | **Commit 6.51** | The baseline and the target are values Control can compare |  | COACH | SHARED | Control cannot compute target-versus-actual, because the baseline is a sentence and the target is a percentage of something else. |
| 357 | **Commit 10.3** | The workspace reads the v2 field names, and progress counts them |  | UI | SHARED | The Belt completes every coached field and the progress bar does not move, because it counts a vocabulary that was renamed underneath it. |
| 360 | **Commit 8.0** | Turn telemetry and `@traceable` |  | OPS | SHARED | Nothing is traced, so every investigation needs a hand-built harness and no limit can be set from measured data. **The executor slice ran on 2026-09-24 ahead of its precondition 7.6, by founder ruling** — spans on the executor's setup, the lookups and every direct Azure call, to measure why open questions miss the budget (G-93). |
| 365 | **Commit 6.44** | The contradiction stop moves from middleware into a node |  | COACH | SHARED | A Belt who contradicts a gate-approved value is never stopped, because the stop is specified as a mechanism that was ruled never to exist. |
| 370 | **Commit 7.3** | Nine-step HITL gate |  | GATE | SHARED | Nothing pauses for a human at a gate, so no gate decides, `gate_attempts` cannot accumulate, and the supervisor graph can never become the runtime. |
| 375 | **Commit 7.7** | The approve endpoint |  | GATE | SHARED | The Belt can read the gate document they are being asked to approve and has nowhere to say yes. |
| 380 | **Commit 10.2** | Live gate document + conflict panel |  | UI | SHARED | A Belt cannot see the document being built, so the gate is the first time anyone looks at it whole. |
| 390 | **Commit 7.1** | `DMAICGateValidator` + Layer 2b |  | GATE | SHARED | Nothing checks a gate document against its phase's rules, so a gate passes on presence rather than on correctness. |
| 400 | **Commit 7.2** | Layers 2c, 2d + `validation_stack` |  | GATE | SHARED | Cross-phase consistency and statistical validity go unchecked, so Measure can contradict Define and both pass. |
| 406 | **Commit 7.9** | Define end to end, on one fresh case |  | GATE | SHARED | No run has ever taken one case through Define and closed its gate, so every green row is proven on a different case. |
| 405 | **Commit 7.8** | The gate steps that consume validation results |  | GATE | SHARED | The nine-step gate stops at the pause: nothing presents the advisory, the rubric verdict or the tier split to the Belt. |
| 410 | **Commit 7.4** | Two tiers + `warning` verdict |  | GATE | SHARED | Every finding blocks equally, so a missing nice-to-have stops a project exactly as a missing baseline does. |
| 420 | **Commit 7.0** | The evaluation suite |  | GATE | SHARED | Coaching quality has no baseline, so no later change can be shown to have improved or regressed it. |
| 430 | **Commit 7.5** | Escalation |  | GATE | SHARED | A project failing its gate three times has nowhere to go, so it loops instead of reaching a human. |
| 440 | **Commit 7.6** | The re-approval cascade |  | GATE | SHARED | A contradiction against an approved value never reopens the field it contradicts, so the gate document keeps a figure the Belt has withdrawn. |
| 450 | **Commit 6.14** | SKILL.md shape pass — Define, Analyse, Improve, Control | BLOCKED | COACH | PHASE | Four of five phases cannot ask for a file in a shape they can validate, so 6.12's ask-binding works for Measure alone. |
| 460 | **Commit 6.10** | `analyse_executor_node` — §26's multi-hop | BLOCKED | COACH | PHASE | Analyse cannot chain retrieval, so root-cause work needing a second hop returns a first-hop answer and stops. |
| 471 | **Commit 6.45** | The planner decides on field completeness |  | COACH | SHARED | The coach asks one question per turn regardless of whether the field is already answered, because the routing predicate counts turns rather than reading what is captured. |
| 473 | **Commit 6.46** | The coaching script is guaranteed to reach the model, or its absence is recorded |  | COACH | SHARED | A turn coached with no methodology looks exactly like one coached with it, so nobody can tell which turns had it. |
| 475 | **Commit 6.47** | Durable writes inside a node, and persistence loss is never silent |  | STORE | SHARED | A deployment with no storage configured runs, answers and loses everything, looking healthy throughout. |
| 478 | **Commit 6.48** | A captured value carries its declared type |  | COACH | SHARED | A Belt answers every question and the gate document cannot be assembled, because four structured fields are stored as prose. |
| 479 | **Commit 6.50** | The conformance pass — the tree against the framework's own documentation |  | OPS | SHARED | Every checker compares the code to documents this project wrote, so a mechanism used against the framework's documented behaviour satisfies all four and is caught only by somebody reading the docs by chance. |
| 472 | **Commit 6.49** | The checks card — twelve capability rows get the check that proves them |  | OPS | SHARED | Twelve rows of the register are claims: nobody can say whether a checkpoint is written per node, or whether a Define turn leaves a readable trace. |
| 474 | **Commit 6.52** | A turn always answers inside its budget |  | COACH | SHARED | A Belt who asks an open question gets a 500 after 45 seconds, because the node's own budget starts late and the knowledge lookups hold the event loop so no timer can fire. |
| 476 | **Commit 6.54** | The clients are built once, at startup, before any Belt waits for them |  | COACH | SHARED | The first open question after a restart spends ~20 s building clients the app could have built before it opened, and the Belt gets the out-of-time answer. |
| 487 | **Commit 6.61** | The coaching move is decided in code |  | COACH | SHARED | The coach sometimes waits after a read-back, sometimes moves on and sometimes re-asks, and stores its own paraphrase before the Belt has confirmed it. |
| 488 | **Commit 6.62** | The other four phase scripts carry no move-sequencing |  | COACH | PHASE | Four phase scripts still tell the coach when to move on, which is now decided in code. |
| 483 | **Commit 6.58** | A percent convention for the computation tools |  | COACH | SHARED | A savings figure 100× too large reaches the Belt, because a tool reads 23% as 23. |
| 484 | **Commit 6.59** | The coherence judge rules on the Belt's words, not the coach's |  | COACH | SHARED | Four turns in six are marked as parroting and go ungraded, though none repeats the Belt. |
| 485 | **Commit 6.53** | A coherence rejection asks the coach again | GATED | COACH | SHARED | A rejected reply goes to the Belt unchanged, and the judge is told the coach will retry when it will not. |
| 486 | **Commit 6.60** | The script already delivered is not fetched again |  | COACH | SHARED | The first turn of a phase spends a model call fetching a script the coach already has. |
| 482 | **Commit 6.56** | The coaching proof: positions 1–8 of Define, one traced run | GATED | OPS | SHARED | Seven capability rows describe how the coach teaches, and none can be marked, because no traced run has walked a case through the positions they describe. |
| 481 | **Commit 6.57** | The Belt's step is computed, not counted by the model |  | COACH | SHARED | The Belt is told they are on step 13 of 13 of a twelve-step walk, because the only count the coach was given was the gate's. |
| 477 | **Commit 10.4** | The error contract — a failed turn is readable |  | UI | SHARED | A failed turn reaches the Belt as a stack fragment in a three-second toast, with no way to tell a timeout from a rate limit. |
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
| 580 | **Commit 6.36** | The register's readers read either document |  | OPS | SHARED | The commit that moves the gap register cannot pass the guard that resolves gap numbers against it, so the repartition cannot be committed at all. |
| 581 | **Commit 6.37** | The repartition — the operational register moves to the procedure |  | OPS | SHARED | The architecture and its build status stay in one document, so every status edit is a diff against the specification and the two go on disagreeing. |
| 582 | **Commit 6.39** | The spec-entry population joins the register (assertion 5) |  | OPS | SHARED | Ninety-two spec entries carry no row, so twenty-six open gaps can name no fact and the gap invariant is satisfied by an escape hatch rather than by a fact. |
| 583 | **Commit 6.40** | Every section declares a row or declares itself not-markable (assertion 7) |  | OPS | SHARED | One hundred and ninety-eight sections are neither marked nor declared unmarkable, so the section-to-row direction of the bidirectional rule has no population to range over. |
| 584 | **Commit 6.38** | The dual-read is removed — one register, one reader |  | OPS | SHARED | Both documents stay readable as the register, which is the two-sources-of-truth condition the repartition was performed to end. |
| 585 | **Commit 6.41** | The symbol-anchor ratchet comes down |  | OPS | SHARED | The bound on unanchored facts only ever rises, so the register counts a backlog it has no mechanism to reduce and the count reads as progress. |
| 586 | **Commit 11.2** | Governance close-out |  | OPS | SHARED | The refactor has no end, so procedure and architecture drift apart again with nothing marking the handover. |

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

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L0 |  | — | **6.16** | The board is generated, not written | ✅ | `repo:.claude/hooks/build_board.py` | §55.1, §66, Appendix D |
| L0 |  | — | **6.17** | The count-check — a written count against the list it describes | ☐ | `absent: repo:.claude/hooks/count_check.py` | §55.1, §6 / S-C02, §29.2 |
| L0 |  | — | **6.22** | The order-check — the middleware stack's ordering test observes execution (G-52) | ⛔ | `backend.tests.test_middleware_execution_order::test_this_observes_a_real_graph_and_not_a_stub` | — |
| L0 |  | — | **6.23** | The source-method check — verification against the installed object, not the page (G-54) | ☐ | `repo:agent-improve/docs/_archive/BIBLE_VERIFICATION_LOG.md` | — |
| L0 |  | — | **6.24** | The drift hook learns to read the documents (G-56) | ☐ | `repo:.claude/hooks/fact-ownership-guard.py` | — |
| L0 |  | — | **6.25** | Scratch leaves the tree | ✅ | `absent: repo:scratch` | — |
| L0 |  | — | **6.26** | The guard's tree rules get a test suite (G-57) | ✅ | `backend.tests.test_commit_guard_tree_rules::test_a_scratch_directory_segment_is_caught` | — |
| L0 |  | — | **6.27** | The watched-path contract has one owner (G-58) | ✅ | `backend.tests.test_commit_guard_tree_rules::test_the_watch_list_and_ss552_state_the_same_paths` | — |
| L0 |  | — | **6.28** | Fact-ownership moves to the commit gate (G-59, G-60) | ☐ | `absent: repo:.claude/hooks/ownership_gate.py` | — |
| L0 |  | — | **6.29** | Search index schema ownership — ruled (G-60) | ☐ | `absent: repo:.claude/config/search_index_owner.yaml` | — |
| L0 |  | — | **6.30** | A commit body's code claims carry a resolvable reference (G-62) | ☐ | `absent: repo:.claude/hooks/code_ref_gate.py` | — |
| L0 |  | — | **6.31** | The build matrix — one row per step, anchored to a symbol | ✅ | `verify_built::matrix_covers_appendix_d` | — |
| L0 |  | — | **6.32** | An out-of-band landing gets the lane it earned (G-65) | ☐ | `absent: backend.tests.test_board_lanes` | §55.2 · Appendix D · G-65 |
| L0 |  | — | **6.36** | The register's readers read either document — **the scaffolding that made 6.37 committable at all. REMOVED AT 6.38**, which is what its own code said would happen: a permanent dual-read is two sources of truth | ✅ | `backend.tests.test_register_single_source::test_the_scaffolding_is_gone` | §55.1 · Appendix G |
| L0 |  | — | **6.37** | The repartition — the operational register moves to the procedure | ☐ | `absent: backend.tests.test_operational_register` | §55.1 · §55.2 · §66 · Appendix F |
| L0 |  | — | **6.39** | The spec-entry population joins the register (assertion 5) | ✅ | `backend.tests.test_spec_entry_rows::test_assertion_5_is_clean_on_the_real_register` | §55.1 · §66 · Appendix F |
| L0 |  | — | **6.40** | Every section declares a row or declares itself not-markable (assertion 7) | ✅ | `backend.tests.test_not_markable_coverage::test_assertion_7_is_clean_on_the_real_documents` | §55.1 · §55.2 · Appendix F |
| L0 |  | — | **6.41** | The symbol-anchor ratchet comes down (G-87) | ✅ | `backend.tests.test_anchor_ratchet::test_the_three_categories_partition_the_unanchored_rows` | §55.2 · Appendix F |
| L0 |  | — | **6.38** | The dual-read is removed — one register, one reader | ✅ | `absent: repo:.claude/hooks/_register_source.py` | §55.1 · §66 |
| L0 |  | — | **6.50** | The conformance pass — the tree against the framework's own documentation | ☐ | — | §0.24, §16, §55.1, §66 |
| L0 |  | — | **6.49** | The checks card — twelve capability rows get the check that proves them | ✅ | `backend.tests.test_capability_rows::test_row_33_a_checkpoint_is_written_after_every_node` | §43, §47, §51, §55.1 |
| L0 |  | — | **11.2** | Governance close-out | ☐ | `absent: repo:agent-improve/docs/HANDOVER.md` | §55 |

#### L1 · API surface

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L1 | 3 | — | **10.0** | The coaching turn’s output reaches the Belt — four blocks and the grader’s warning | ✅ | `backend.tests.test_coaching_blocks::test_the_response_carries_four_blocks_and_the_warning` | §50.1, §49, S-C05 |
| L1 | 9 | UI | **10.3** | The workspace reads the v2 field names, and progress counts them | ☐ | — | §50, §50.1, §39.1.2, G-71 |
| L1 |  | — | **10.2** | Live gate document + conflict panel | ☐ | `absent: repo:agent-improve/ui/gate_document.js` | §50, §43.4 |
| L1 | 10 | UI | **10.4** | The error contract — a failed turn is readable | ☐ | — | §4.8, §12.3, §49, G-70 |
| L1 |  | UI | **10.1**, **7.3** | **11 routes are served; this section's table names 4 of them** — `POST /ask`, `GET /cases/{id}`, `GET /registry`, `POST /upload`. **Seven are in the tree and in no ratified table** (**G-47**), and **five table rows are unbuilt**: `/ask/stream` (step 10.1), `/gate/approve` and `/gate/reject` (step 7.3, which has no `interrupt()` to resume from), `GET /cases`, and `/gate/submit` in the three-route shape this table ratifies. **Corrected 2026-09-11:** this line read *"11 of 12 routes exist … names 8 of the 11 — six are in the tree and in no ratified table"*, and **8 + 6 = 14 against 11 built routes**, so the marker contradicted itself; neither figure was derivable and the `12` traced to nothing. `verify_built.py` now pins the route SET, not the count, so the named/unnamed split is re-derived rather than restated | ⚠️ | `repo:agent-improve/backend/gateway/routes.py` | §49 |
| L1 |  | UI | **6.19** | **these four fields do not exist** (**G-50**) | ☐ | — | §50.1 |
| L1 |  | UI | — | **S-C36** · `CitationRecord` and `CitationBundle` | — | — | §65.1 |
| L1 |  | UI | — | **S-C37** · The API envelopes | — | — | §65.2 |
| L1 |  | UI | — | **S-F34** · The API surface | — | — | §65.3 |
| L1 |  | UI | — | **S-F35** · The upload handler | — | — | §65.4 |
| L1 |  | UI | — | **S-F36** · The `improve_case_index` write path | — | — | §65.5 |

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

| L1 |  | — | **10.1** | `/ask/stream` SSE | ☐ | `absent: backend.gateway.routes::ask_stream` | §49 |

#### L2 · Supervisor graph

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L2 |  | — | **2.4** | `set_entry_point` → `add_edge(START, …)` | ✅ | `absent: backend.core.graph::set_entry_point` | §12 |
| L2 |  | — | **3.1** | `SupervisorState` and `PhaseState` | ✅ | `backend.core.state::SupervisorState` | §5, §6, §7 |
| L2 |  | — | **4.3** | Supervisor graph | ✅ | `backend.core.graph::get_graph` | §12, §15 |
| L2 |  | SUP | **7.3** | **the supervisor graph compiles exactly as §15 and S-F01 specify** — five phase-subgraph nodes plus escalation, checkpointer and store on the parent, neither on the subgraphs, pinned by `test_supervisor_graph.py`. **It is deliberately NOT the runtime yet**, and step 4.3 said so when it built it: `get_graph()` returns the one-turn per-phase graph until `gate_review` raises `interrupt()`, because §15's static chain advances on `END` and until the interrupt exists `END` means only *"the graph ran"*. **The swap is one line at 7.3** | ✅ | — | §15 |
| L2 |  | SUP | — | **`SupervisorState` is 7 of 7, exact** — names, types and both `operator.add` reducers transcribed verbatim into `core/state.py`. Nothing present-and-unspecified, nothing specified-and-absent; `SUPERVISOR_STATE_FIELDS` sits beside the class as a census and `test_state.py` asserts it. Re-run by `verify_built.py`'s *state field counts* check | ✅ | `backend.core.state::SupervisorState` | §57.2 |
| L2 |  | SUP | — | **S-C01** · `SupervisorState` | — | — | §58.1 |
| L2 |  | SUP | — | **S-F01** · The supervisor graph — static edges | — | — | §58.10 |
| L2 |  | SUP | — | **S-F02** · `build_phase_subgraph(phase, llm)` | — | — | §58.11 |
| L2 |  | SUP | — | **S-F03** · `phase_planner` node | — | — | §58.12 |
| L2 |  | SUP | — | **S-F04** · `phase_executor` node | — | — | §58.13 |
| L2 |  | SUP | — | **S-F05** · `validation_stack` node | — | — | §58.14 |
| L2 |  | SUP | — | **S-F06** · `gate_review_node` | — | — | §58.15 |
| L2 |  | SUP | — | **S-F07** · `gate_apply_node` | — | — | §58.16 |
| L2 |  | SUP | — | **S-F08** · The escalation subgraph | — | — | §58.17 |
| L2 |  | SUP | — | **S-F09** · `analyse_executor_node` | — | — | §58.18 |
| L2 |  | SUP | — | **S-F10** · `define_input_mapper` | — | — | §58.19 |
| L2 |  | SUP | — | **S-C02** · `PhaseState` | — | — | §58.2 |
| L2 |  | SUP | — | **S-F11** · `define_output_mapper` | — | — | §58.20 |
| L2 |  | SUP | — | **S-F12** · The Measure, Analyse, Improve and Control mapper pairs | — | — | §58.21 |
| L2 |  | SUP | — | **S-F13** · Level 2 `Command` routing | — | — | §58.22 |
| L2 |  | SUP | — | **S-C03** · Per-phase use of `PhaseState` | — | — | §58.3 |
| L2 |  | SUP | — | **S-C04** · `CoachingPlan` | — | — | §58.4 |
| L2 |  | SUP | — | **S-C05** · `CoachingResponse` | — | — | §58.5 |
| L2 |  | SUP | — | **S-C06** · `AzureBlobStore` | — | — | §58.6 |
| L2 |  | SUP | — | **S-C07** · `AzureBlobCheckpointSaver` | — | — | §58.7 |
| L2 |  | SUP | — | **S-C08** · `ImproveBlobClient` | — | — | §58.8 |
| L2 |  | SUP | — | **S-C09** · `storage/models.py` — the record models | — | — | §58.9 |

#### L3 · Phase subgraphs

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L3 |  | — | **3.3** | Boundary mappers | ✅ | `backend.phases.mappers_common::PHASE_ORDER` | §9 |
| L3 |  | — | **4.1** | Define phase subgraph | ✅ | `backend.phases.subgraph_common::build_phase_subgraph` | §12, §13, §14 |
| L3 |  | — | **4.4** | Remaining four subgraphs | ✅ | `backend.phases.mappers_common::PHASE_ORDER {define,measure,analyse,improve,control}` | §12, §13 |
| L3 |  | — | **6.8** | `phase_context` is read (WATCH 19) | ✅ | `backend.middleware.state_injection::BeforeModelStateInjection` | §6, §9, §19.1 |
| L3 |  | — | **6.20** | The write paths — `computation_results`, `phase_metrics`, `field_index` | ☐ | `backend.phases.nodes_common::_advance_field_index` | §7, §39.x.7, S-C02, S-C03 |
| L3 |  | — | **6.33** | The capture path accumulates — a field survives the next turn, and the field change log records what it said before | ✅ | `backend.phases.mappers_common::captured_for_phase` | §6, §7, §11, §20, S-F04 |
| L3 |  | — | **6.42** | The gate document records what Define established | ☐ | — | §33, §40, §50, S-F07, S-F28 |
| L3 | 11 | — | **6.43** | The coach can read an uploaded document | ☐ | — | §29.1, §32, S-F57, G-82 |
| L3 | 8 | — | **6.51** | The baseline and the target are values Control can compare | ☐ | — | §7, §39.1.2, §63.1 |
| L3 | 12 | — | **6.44** | The contradiction stop moves from middleware into a node | ☐ | — | §37, §19.6, S-C10, G-15, G-89 |
| L3 | 7 | — | **6.45** | The planner decides on field completeness | ☐ | — | §17, §39.1.2, S-F13 |
| L3 |  | — | **6.46** | The coaching script is guaranteed to reach the model, or its absence is recorded | ✅ | `backend.tests.test_coaching_script::test_step_log_records_that_the_script_was_delivered` | §32, §19.2, S-C12 |
| L3 |  | — | **6.47** | Durable writes inside a node, and persistence loss is never silent | ☐ | — | §10, §16, §47, S-C06 |
| L3 |  | — | **6.48** | A captured value carries its declared type | ☐ | — | §7, §20, §41, S-C05, S-C33 |
| L3 | 1 | — | **6.61** | The coaching move is decided in code | ☐ | — | §17, §19.1, §20, §22, §32, §43 |
| L3 | 2 | — | **6.62** | The other four phase scripts carry no move-sequencing | ☐ | — | §32, §43 |
| L3 | 5 | — | **6.58** | A percent convention for the computation tools | ☐ | — | §69.1, §69.2, §60.6 |
| L3 | 4 | — | **6.59** | The coherence judge rules on the Belt's words, not the coach's | ☐ | — | §19.7, §19.8, S-C13 |
| L3 |  | — | **6.53** | A coherence rejection asks the coach again | ☐ | — | §19.7, §34.2, S-C13 |
| L3 |  | — | **6.60** | The script already delivered is not fetched again | ☐ | — | §19.2, §32, S-C12 |
| L3 | 6 | — | **6.56** | The coaching proof: positions 1–8 of Define, one traced run | ☐ | — | §43.1–§43.7, §22, §51 |
| L3 |  | — | **6.57** | The Belt's step is computed, not counted by the model | ✅ | `backend.tests.test_define_position::test_the_reply_carries_the_computed_step_not_the_models_count` | §43.3, §39.1.2, §39.1.9, §19.1 |
| L3 |  | PHASE | — | **the typing law is enforced by schema, not by convention** — all five `{Phase}Output` declare captured fields as `str` or `dict`, and `test_gate_documents.py` pins both the `dict` fields and their Tier-1 placement | ✅ | — | §7 |
| L3 |  | PHASE | **7.3** | five nodes, identical node-name sets across all five phases, re-run by `verify_built.py`'s *phase subgraph nodes* check. ⚠ `gate_review` is a pass-through until 7.3 | ✅ | — | §13 |
| L3 |  | PHASE | — | every node is `async def` since 2.5 — all five `orchestrate_*`, all five `validate_*`, `escalate`, and all eleven route handlers | ✅ | — | §14 |
| L3 |  | PHASE | **6.20** | **Define has NO state-parameters section.** §39.2.7–§39.5.7 give Measure, Analyse, Improve and Control one each; **39.1.7 is the SKILL.md content**, so the phase this project is proving first is the one phase with no state contract at all. Found by the targeted state audit, 2026-09-11. **Step 6.20 writes it**, in the same shape as the other four | ⚠️ | — | §39.1 |
| L3 |  | PHASE | **6.20** | **the list EXISTS and nothing walks it.** `DEFINE_FIELD_ORDER` carries all 12 fields in this order — **the only phase whose ordered list is in code at all** — but `field_index` is set to `0` by the input mapper and **never read or advanced by any node**, so the planner indexes into nothing, which is the condition G-38 was closed for. (The gate list is 13; `field_index` indexes the 12 above, by design.) | ⚠️ | — | §39.1.2 |
| L3 |  | PHASE | — | `skills/dmaic-define-phase/SKILL.md` exists and is §32-conformant as of 6.9; its opening script is **byte-identical to `skills/dmaic-define-phase/coaching_script.md`**, which is where the script lives as of 2026-09-13 — §56.1's atomic unit, re-run by `verify_built.py`'s *phase scripts byte-matching their SKILL.md* check, now a FILE-to-FILE comparison | ✅ | — | §39.1.7 |
| L3 |  | PHASE | — | **this list does not exist in code.** `measure/schema.py` exposes tier SETS only — no `MEASURE_FIELD_ORDER` — so the 10-field sequence this table states has no runtime form and `field_index` has nothing to index into. **Only Define's list is built.** ⚠ **NO STEP OWNS THIS**: 6.20 covers Define's, and group C's phase slices (6.14, 6.10) do not create ordered lists. It is a transcription of the table above, not a decision | ☐ | — | §39.2.2 |
| L3 |  | PHASE | **6.20** | **10 captured fields land in `artifacts` as specified; three rows of this table do not hold.** Verified row-by-row by the targeted state audit, 2026-09-11: **`artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by the gate-document assembler and WRITTEN BY NOTHING** — the executor merges only `CoachingResponse.fields_captured`, so both always read `[]`; **`field_index` never advances**; and `gate_attempts` is written but resets every turn because nothing interrupts (WATCH 18). `citations` / `uploads` hold. `validator_feedback` accumulates across the ≤3 validation retries, and `draft`/`belt_edits`/`final` are `dict` and never `str` | ⚠️ | — | §39.2.7 |
| L3 |  | PHASE | — | `skills/dmaic-measure-phase/SKILL.md` exists and is §32-conformant as of 6.9; its opening script is **byte-identical to `skills/dmaic-measure-phase/coaching_script.md`**, which is where the script lives as of 2026-09-13 — §56.1's atomic unit, re-run by `verify_built.py`'s *phase scripts byte-matching their SKILL.md* check, now a FILE-to-FILE comparison | ✅ | — | §39.2.10 |
| L3 |  | PHASE | — | **this list does not exist in code.** `analyse/schema.py` exposes tier SETS only — no `ANALYSE_FIELD_ORDER` — so the 9-field sequence this table states has no runtime form and `field_index` has nothing to index into. **Only Define's list is built.** ⚠ **NO STEP OWNS THIS**: 6.20 covers Define's, and group C's phase slices (6.14, 6.10) do not create ordered lists. It is a transcription of the table above, not a decision | ☐ | — | §39.3.2 |
| L3 |  | PHASE | **6.20** | **9 captured fields land in `artifacts` as specified; three rows of this table do not hold.** Verified row-by-row by the targeted state audit, 2026-09-11: **`artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by the gate-document assembler and WRITTEN BY NOTHING** — the executor merges only `CoachingResponse.fields_captured`, so both always read `[]`; **`field_index` never advances**; and `gate_attempts` is written but resets every turn because nothing interrupts (WATCH 18). `citations` / `uploads` hold. **`hop_results` / `synthesis_output` say *"populated here"* and are never populated** — only `[]` / `None` at the mapper; that is step 6.10, ⛔ blocked on G-05 and G-35 | ⚠️ | — | §39.3.7 |
| L3 |  | PHASE | — | `skills/dmaic-analyse-phase/SKILL.md` exists and is §32-conformant as of 6.9; its opening script is **byte-identical to `skills/dmaic-analyse-phase/coaching_script.md`**, which is where the script lives as of 2026-09-13 — §56.1's atomic unit, re-run by `verify_built.py`'s *phase scripts byte-matching their SKILL.md* check, now a FILE-to-FILE comparison | ✅ | — | §39.3.10 |
| L3 |  | PHASE | — | **this list does not exist in code.** `improve/schema.py` exposes tier SETS only — no `IMPROVE_FIELD_ORDER` — so the 9-field sequence this table states has no runtime form and `field_index` has nothing to index into. **Only Define's list is built.** ⚠ **NO STEP OWNS THIS**: 6.20 covers Define's, and group C's phase slices (6.14, 6.10) do not create ordered lists. It is a transcription of the table above, not a decision | ☐ | — | §39.4.2 |
| L3 |  | PHASE | **6.20** | **9 captured fields land in `artifacts` as specified; three rows of this table do not hold.** Verified row-by-row by the targeted state audit, 2026-09-11: **`artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by the gate-document assembler and WRITTEN BY NOTHING** — the executor merges only `CoachingResponse.fields_captured`, so both always read `[]`; **`field_index` never advances**; and `gate_attempts` is written but resets every turn because nothing interrupts (WATCH 18). `citations` / `uploads` hold. `uploads` carries pilot data as specified | ⚠️ | — | §39.4.7 |
| L3 |  | PHASE | — | `skills/dmaic-improve-phase/SKILL.md` exists and is §32-conformant as of 6.9; its opening script is **byte-identical to `skills/dmaic-improve-phase/coaching_script.md`**, which is where the script lives as of 2026-09-13 — §56.1's atomic unit, re-run by `verify_built.py`'s *phase scripts byte-matching their SKILL.md* check, now a FILE-to-FILE comparison | ✅ | — | §39.4.10 |
| L3 |  | PHASE | — | **this list does not exist in code.** `control/schema.py` exposes tier SETS only — no `CONTROL_FIELD_ORDER` — so the 12-field sequence this table states has no runtime form and `field_index` has nothing to index into. **Only Define's list is built.** ⚠ **NO STEP OWNS THIS**: 6.20 covers Define's, and group C's phase slices (6.14, 6.10) do not create ordered lists. It is a transcription of the table above, not a decision | ☐ | — | §39.5.2 |
| L3 |  | PHASE | **6.20** | **12 captured fields land in `artifacts` as specified; three rows of this table do not hold.** Verified row-by-row by the targeted state audit, 2026-09-11: **`artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by the gate-document assembler and WRITTEN BY NOTHING** — the executor merges only `CoachingResponse.fields_captured`, so both always read `[]`; **`field_index` never advances**; and `gate_attempts` is written but resets every turn because nothing interrupts (WATCH 18). `citations` / `uploads` hold. **`final` → `SupervisorState.final_output` never happens** — `control_output_mapper` returns `advance()`, which by contract returns orchestration values ONLY, so the project's terminal artifact is never written. ⚠ no step owns this clause | ⚠️ | — | §39.5.7 |
| L3 |  | PHASE | — | `skills/dmaic-control-phase/SKILL.md` exists and is §32-conformant as of 6.9; its opening script is **byte-identical to `skills/dmaic-control-phase/coaching_script.md`**, which is where the script lives as of 2026-09-13 — §56.1's atomic unit, re-run by `verify_built.py`'s *phase scripts byte-matching their SKILL.md* check, now a FILE-to-FILE comparison | ✅ | — | §39.5.10 |
| L3 |  | PHASE | — | **22 of 22, exact and in the same order** as this entry's definition — verified field-by-field by the targeted state audit, 2026-09-11. Step 3.1's Done-when still says *"7 and 19"*; **the number is stale and the substance is not** — four ratified amendments moved it (v1.7 17→19, v1.9's `remaining_steps`, then `asks`, `uploads`, `hop_results`). Re-run by `verify_built.py`'s *state field counts* check | ✅ | — | §58.2 |
| L3 |  | PHASE | — | **Measure phase, complete specification** · schema and validator exist in v2 form; the known defect is the one its §39.2.7 row records — captured fields land as specified, three do not | ⚠️ | `backend.phases.measure.schema::MeasureOutput` | §39.2 |
| L3 |  | PHASE | — | **Analyse phase, complete specification** · schema and validator exist in v2 form; the known defect is the one its §39.3.7 row records — captured fields land as specified, three do not | ⚠️ | `backend.phases.analyse.schema::AnalyseOutput` | §39.3 |
| L3 |  | PHASE | — | **Improve phase, complete specification** · schema and validator exist in v2 form; the known defect is the one its §39.4.7 row records — captured fields land as specified, three do not | ⚠️ | `backend.phases.improve.schema::ImproveOutput` | §39.4 |
| L3 |  | PHASE | — | **Control phase, complete specification** · schema and validator exist in v2 form; the known defect is the one its §39.5.7 row records — captured fields land as specified, three do not | ⚠️ | `backend.phases.control.schema::ControlOutput` | §39.5 |

#### L4 · Coaching agent

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L4 |  | — | **2.6** | `content_blocks` · 20 sites | ✅ | `backend.tests.test_middleware::test_injection_uses_content_blocks_not_string_concatenation` | §21 |
| L4 |  | — | **6.1** | Planner / Executor split | ✅ | `backend.phases.nodes_common::planner` | §17, §20 |
| L4 |  | — | **6.2** | `create_agent` executor | ✅ | `backend.core.substate::CoachingResponse` | §18, §20 |
| L4 |  | — | **6.6** | Prompts | ✅ | `backend.core.prompts::DEFINE_COACH_PROMPT` | §22 |
| L4 |  | — | **6.35** | The hop cap matches the ceiling that was always in force (G-83) | ✅ | `backend.phases.nodes_common::MEASURED_HOP_SECONDS =9.5` | §26, §25, §3.7 |
| L4 |  | — | **6.7** | The hop cap, as §26 specifies it (WATCH 26) | ✅ | `backend.phases.nodes_common::COACH_HOP_BUDGET =3` | §16 · §26 |
| L4 |  | — | **6.9** | The four missing SKILL.md files + §32 conformance | ✅ | `repo:agent-improve/skills/dmaic-define-phase/SKILL.md` | §32, §43, §37 |
| L4 |  | — | **6.12** | Ask-binding: an upload answers a request | ✅ | `backend.phases.nodes_common::_unconsumed_for_open_ask` | §29.1, §32, §43, §50 |
| L4 |  | — | **6.18** | The executor ignores the tool its planner names (G-49) | ✅ | `backend.phases.nodes_common::_dispatch_routed_read` | §17, §26, S-F04, S-F13, S-F57 |
| L4 |  | — | **6.21** | The plan reaches the model (G-49's fix) | ✅ | `backend.phases.nodes_common::_dispatch_routed_read` | §17, §26, §19.1 / S-C11, S-F13, S-F57 |
| L4 |  | — | **6.19** | `CoachingResponse` gains §50.1's four presentational fields (G-50) | ✅ | `backend.core.substate::CoachingResponse {message,explanation,example,prompt,progress,fields_captured,citations,contradiction_flag}` | §20, S-C05, §50.1 |
| L4 |  | — | **6.14** | SKILL.md shape pass — Define, Analyse, Improve, Control | ⛔ | `backend.upload.asks::SHAPES_BY_PHASE.define {}` | §32, §43, §23.2.1 |
| L4 |  | — | **6.10** | `analyse_executor_node` — §26's multi-hop | ⛔ | `absent: backend.phases.nodes_common::analyse_executor_node` | §26, §58.18 |
| L4 |  | COACH | — | **the split holds at runtime for the one decision the | ✅ | — | §17 |
| L4 |  | COACH | **6.19** | `create_agent` with `system_prompt=` and `response_format=CoachingResponse`, both parameter names verified against the installed signature. ⚠ the response schema itself is four of eight fields (§58.5, G-50) | ✅ | — | §18 |
| L4 |  | COACH | — | eleven roles resolve to a deployment and grader temperature is 0.1, pinned by `test_llm.py`; the factory's retry is explicitly 0 (§19.4 owns retry). ⚠ **§21's own role map versus the 11-role factory is carried forward unresolved** from v1.22 | ✅ | — | §21 |
| L4 |  | COACH | **11.1** | the five `{PHASE}_COACH_PROMPT` carry the memory-hierarchy block and the anti-hallucination guards (6.6). The v1 `EXTRACTION_{PHASE}` family survives only in `core/prompts.py` and the five v1 `orchestrate.py`, which **step 11.1 deletes wholesale** | ✅ | `backend.core.prompts::PHASE_COACH_PROMPT` | §22 |
| L4 |  | COACH | **6.10** | `analyse_executor_node` is step 6.10, ⛔ blocked on G-05 and G-35. The **caps are built**: the five-hop cap and the `remaining_steps` floor of 2 both landed at 6.7, and `recursion_limit=50` is a backstop rather than the cap (WATCH 26) | ☐ | — | §26 |
| L4 |  | COACH | **6.14** | five SKILL.md files, §32-conformant as of 6.9, each byte-matching its §39.x opening script. ⚠ their **ask shapes** are Measure only — the other four are step 6.14, ⛔ blocked on founder content | ✅ | — | §32 |
| L4 |  | COACH | — | **all 8 fields exist** — step 6.19, 2026-09-14 (**G-50 CLOSED**) | ✅ | — | §58.5 |
| L4 |  | COACH | — | The seven-step computation pattern · a grader criterion: the coach educates on the concept, explains why it matters, then runs the tool | ⚠️ | `backend.core.prompts::COACHING_QUALITY_RUBRIC` | §43.1 |
| L4 |  | COACH | — | Show before asking · a grader criterion: a concrete example of a completed answer before the Belt is asked for theirs. **Observed failing a live turn 2026-09-15** | ⚠️ | `backend.core.prompts::COACHING_QUALITY_RUBRIC` | §43.2 |
| L4 |  | COACH | — | The A→F session flow · six stages with a visible progress count. **No SKILL.md carries the count** and nothing checks for it | ☐ | `absent: backend.tests.test_session_flow` | §43.3 |
| L4 |  | COACH | — | The live gate document preview · depends on `check_gate_status()`, which is **absent from the tree** — G-31 is the gap that specifies it | ☐ | `absent: backend.knowledge.tools::check_gate_status` | §43.4 |
| L4 |  | COACH | — | No external URLs · a grader criterion: methodology is retrieved via `rag_lookup_methodology`, never recalled from training data | ⚠️ | `backend.core.prompts::COACHING_QUALITY_RUBRIC` | §43.5 |
| L4 |  | COACH | — | What the coach must not do · the four `must not` criteria — vague fields, invented data, doing the Belt's work, drifting off phase | ⚠️ | `backend.core.prompts::COACHING_QUALITY_RUBRIC` | §43.6 |
| L4 |  | COACH | — | Metric literacy — the metric, and the statistic · a grader criterion: methodology is referenced when guiding, not opinion | ⚠️ | `backend.core.prompts::COACHING_QUALITY_RUBRIC` | §43.7 |

> **6.21 IS ✅ AS OF 2026-09-15, AND THE HAND-SET ⚠️ IS WITHDRAWN.** Its
> `live-run` ran — rid `20167cc9-ea86-4501-a827-0e19ebb2420a`, the coach
> returning the source file's exact statistics. The cell is derived again, and
> agrees with git. **The three debts its Done-when named are NOT discharged**
> and keep their own rows; see the closure in 6.21's section.
>
> *What follows is why the cell was hand-set, kept because the condition
> recurs:*
> **6.21 WAS ⚠️ RATHER THAN ✅, AND IT WAS THE ONE ROW WHERE `State` WAS NOT
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

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L5 |  | — | **6.3** | Middleware 1–3 | ✅ | `backend.middleware.skills::DMAICSkillsMiddleware` | §19.1–§19.3 |
| L5 |  | — | **6.4** | Retry middleware 4–5 + factory retry removal | ✅ | `installed: langchain.agents.middleware::ModelRetryMiddleware` | §19.4, §19.5, §21 |
| L5 |  | — | **6.5** | Middleware 6–8 | ✅ | `backend.middleware.coherence::CoherenceMiddleware` | §19.6–§19.8 |
| L5 |  | COACH | — | also injects `phase_context` (6.8) and the UPLOAD MANIFEST (6.12). Its `wrap_model_call` encloses §19.4's retry, so the block is composed once per turn, not once per attempt | ✅ | — | §19.1 |
| L5 |  | COACH | — | mounted and working; all five SKILL.md files exist, load and are §32-conformant as of 6.9 | ✅ | — | §19.2 |
| L5 |  | COACH | — | LangChain core as shipped; trigger 100k tokens, keep 20 | ✅ | — | §19.3 |
| L5 |  | COACH | — | `max_retries=2` → three attempts. The only model-retry layer; §21's factory is pinned to 0 | ✅ | — | §19.4 |
| L5 |  | COACH | — | `max_retries=2`, `on_failure="continue"`. Costs no graph steps (measured at 6.4) | ✅ | — | §19.5 |
| L5 |  | COACH | **7.3**, **7.6** | built, ENFORCEMENT DELIBERATELY SUSPENDED · detection runs every turn and the flag still rides on the response; **the `interrupt()` call is GUARDED until step 7.3**. **Founder ruling, 2026-09-11.** §33's mechanism is correct and nothing can resume it — §49's `/gate/approve` and `/gate/reject` are step 7.3. **Measured in the real runtime shape before the ruling was taken:** turn 1 pauses cleanly and returns `__interrupt__` with no `structured_response`; turn 2's message is neither processed nor resumed; **every later turn on that case returns nothing, permanently.** The blast radius is the CASE, not the turn; the checkpoint is Azure Blob, so it survives a restart; and the trigger — a Belt revising a figure they committed earlier — is the INTENDED one, which is to say ordinary coaching. **§37's cascade (7.6) loses nothing**, because the flag is still set. **THREE TESTS PIN THIS, and step 7.3 moves all three** (its Done-when clause 1): `test_ContradictionDetectionMiddleware_does_not_call_interrupt` asserts **zero live `interrupt(...)` call sites, parsed with `ast`** — the same technique as `verify_built.py`'s probe, but in `pytest`, which is a GATE where that probe is only advisory; `test_position_6_is_GUARDED_and_does_not_park_the_case` pins the behaviour and 7.3 rewrites it to assert RESUMPTION; and `test_the_guarded_import_is_kept_for_7_3` stops a tidying pass dropping the unused import and turning 7.3's one uncommented line into a line plus a re-import. `test_interrupt_from_after_agent_is_RESUMABLE_end_to_end` keeps G-15's measurement under test via a local subclass that still interrupts, so **the mechanism stays verified while the policy is suspended** and 7.3 can still trust it. **Both tripwires were proved to trip**: the line was un-guarded exactly as 7.3 would, both failed, and the file was restored. **⛑ This line has twice said the opposite of the truth**: until 2026-09-11 it read *"nothing consumes the flag"* — wrong, the flag was consumed and the graph suspended — and was corrected that morning to *"raises a real `interrupt()`"*, which was true, and had been true for six steps during which a reachable path could brick a live case | ⚠️ | — | §19.6 |
| L5 |  | COACH | — | validation Layer 2a; can stand the grader down | ✅ | — | §19.7 |
| L5 |  | COACH | — | coaching-quality grading, per turn | ✅ | — | §19.8 |
| L5 |  | COACH | — | **S-C10** · `ContradictionDetectionMiddleware` | — | — | §61.1 |
| L5 |  | COACH | — | **S-C11** · `BeforeModelStateInjection` | — | — | §61.2 |
| L5 |  | COACH | — | **S-C12** · `DMAICSkillsMiddleware` | — | — | §61.3 |
| L5 |  | COACH | — | **S-C13** · `CoherenceMiddleware` | — | — | §61.4 |
| L5 |  | COACH | — | **S-C14** · `DMAICGraderMiddleware` | — | — | §61.5 |
| L5 |  | COACH | — | **S-C15** · `HITLInterrupt` | — | — | §61.6 |

#### L6 · Tools and knowledge

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L6 |  | — | **5.1** | Retrieval failure semantics | ✅ | `backend.core.errors::KnowledgeSearchError` | §27 |
| L6 |  | — | **5.2** | Three `rag_lookup_*` + RRF | ✅ | `backend.knowledge.tools::RAG_LOOKUP_TOOLS` | §24, §25, §23 |
| L6 |  | — | **5.3** | 20 computation tools | ✅ | `backend.knowledge.computation::COMPUTATION_TOOLS_BY_PHASE` | §30, §31, §69 |
| L6 |  | — | **5.4** | Per-phase tool binding | ✅ | `backend.knowledge.fusion::RRF_K =60` | §30 |
| L6 |  | — | **9.0** | Knowledge-index rebuild | ⛔ | `azure: improve-knowledge-index` | §23, §23.1 |
| L6 |  | — | **9.1** | Azure batched reindex — case index only | ⛔ | `azure: improve-cases-index.content_vector` | §23.2, §23.3, §23.5 |
| L6 |  | COACH | **9.1** | all three indexes exist and the evidence index carries §23.2's seven fields as of 6.13. **The case index has no `content_vector`**, so case-history retrieval is keyword-only and misses paraphrase — step 9.1, ⛔ EXTERNAL | ⚠️ | — | §23 |
| L6 |  | COACH | — | three `rag_lookup_*` tools, and `rag_lookup_evidence` returns §24's structured record rather than rendered text since 6.13 | ✅ | — | §24 |
| L6 |  | COACH | — | `RRF_K = 60`, unit-tested in `test_fusion.py`. Not a tuning knob — 60 is the constant from the original RRF paper | ✅ | — | §25 |
| L6 |  | COACH | — | a 4xx raises `KnowledgeSearchError` with `severity="permanent"`, and a genuine no-match returns `[]` — the distinction this section exists to make | ✅ | — | §27 |
| L6 |  | COACH | **7.1**, **7.5** | **six of the ratified eight universal tools** are built; `check_gate_status` (7.1) and `request_human_approval` (7.5) cannot be built until the things they call exist. The upload channel is built (6.11–6.13) | ⚠️ | — | §29 |
| L6 |  | COACH | **7.1**, **7.5** | **the twenty and the partition are | ⚠️ | — | §30 |
| L6 |  | COACH | — | all twenty computation tools carry an `args_schema=`, re-run by `verify_built.py` | ✅ | — | §31 |
| L6 |  | COACH | — | **the absence holds and is pinned** — neither | ✅ | — | §69.7 |
| L6 |  | COACH | — | **S-C16** · `Hop` | — | — | §59.1 |
| L6 |  | COACH | — | **S-C17** · `Plan` — the hop decomposition plan | — | — | §59.2 |
| L6 |  | COACH | — | **S-C18** · `SynthesisOutput` | — | — | §59.3 |
| L6 |  | COACH | — | **S-C19** · `QueryVariants` | — | — | §59.4 |
| L6 |  | COACH | — | **S-F14** · `rag_lookup_methodology` | — | — | §59.5 |
| L6 |  | COACH | — | **S-F15** · `rag_lookup_evidence` | — | — | §59.6 |
| L6 |  | COACH | — | **S-F16** · `rag_lookup_case_history` | — | — | §59.7 |
| L6 |  | COACH | — | **S-F17** · `reciprocal_rank_fusion` | — | — | §59.8 |
| L6 |  | COACH | — | **S-F18** · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence` | — | — | §59.9 |
| L6 |  | COACH | — | **S-F19** · `propose_template` | — | — | §60.1 |
| L6 |  | COACH | — | **S-F20** · `propose_diagram` | — | — | §60.2 |
| L6 |  | COACH | — | **S-F21** · `check_gate_status` | — | — | §60.3 |
| L6 |  | COACH | — | **S-F22** · `request_human_approval` | — | — | §60.4 |
| L6 |  | COACH | — | **S-F23** · `load_skill(name)` | — | — | §60.5 |
| L6 |  | COACH | — | **S-F24** · The 20 computation tools | — | — | §60.6 |
| L6 |  | COACH | — | **S-F57** · `load_evidence_series(blob_path, column)` | — | — | §60.7 |
| L6 |  | COACH | — | **S-F37** · Define — 1 tool | — | — | §69.2 |
| L6 |  | COACH | — | **S-F38** · –S-F45 · Measure — 8 tools | — | — | §69.3 |
| L6 |  | COACH | — | **S-F39** · `calculate_cpk` — **Process capability (Cpk)** — can the process meet spec as it runs today, given both where it sits and how much it varies | — | — | §69.3 |
| L6 |  | COACH | — | **S-F40** · `calculate_dpmo` — **Defect rate per million chances (DPMO)** — defects scaled so processes of different volume and complexity compare fairly | — | — | §69.3 |
| L6 |  | COACH | — | **S-F41** · `calculate_yield_rty` — **End-to-end yield (RTY, rolled throughput yield)** — the share of work that clears every step first time, with no rework anyw | — | — | §69.3 |
| L6 |  | COACH | — | **S-F42** · `calculate_ftq` — **First-time quality at one step (FTQ)** — the share that step gets right without rework | — | — | §69.3 |
| L6 |  | COACH | — | **S-F43** · `calculate_grr` — **Measurement trust (Gage R&R)** — how much of the variation you can see is the process, and how much is the measuring | — | — | §69.3 |
| L6 |  | COACH | — | **S-F44** · `calculate_sample_size_proportion` — **How many to sample, for a percentage** — the count needed to pin a proportion within a stated margin | — | — | §69.3 |
| L6 |  | COACH | — | **S-F45** · `calculate_sample_size_mean` — **How many to sample, for an average** — the count needed to detect a difference of a stated size | — | — | §69.3 |
| L6 |  | COACH | — | **S-F46** · –S-F50 · Analyse — 5 tools | — | — | §69.4 |
| L6 |  | COACH | — | **S-F47** · `chi_square_test` — **Are two categories related? (chi-square test)** — association between two categorical variables | — | — | §69.4 |
| L6 |  | COACH | — | **S-F48** · `anova` — **Do three or more groups differ? (ANOVA, analysis of variance)** | — | — | §69.4 |
| L6 |  | COACH | — | **S-F49** · `pearson_correlation` — **Do two numbers move together? (Pearson correlation)** — strength and direction, not cause | — | — | §69.4 |
| L6 |  | COACH | — | **S-F50** · `linear_regression` — **How much does Y change when X changes? (simple linear regression, OLS)** — fits Y = a + bX | — | — | §69.4 |
| L6 |  | COACH | — | **S-F51** · Improve — 1 tool | — | — | §69.5 |
| L6 |  | COACH | — | **S-F52** · –S-F56 · Control — 5 tools | — | — | §69.6 |
| L6 |  | COACH | — | **S-F53** · `imr_chart_limits` — **Control limits for one-at-a-time measurements (I-MR, individuals and moving range)** | — | — | §69.6 |
| L6 |  | COACH | — | **S-F54** · `p_chart_limits` — **Control limits for a pass/fail rate (p-chart)** — for when the batch size changes between periods | — | — | §69.6 |
| L6 |  | COACH | — | **S-F55** · `c_chart_limits` — **Control limits for defect counts (c-chart)** — for when the area of opportunity is constant | — | — | §69.6 |
| L6 |  | COACH | — | **S-F56** · `post_improvement_cpk` — **Capability after the fix (post-improvement Cpk)** — the same capability figure on the new data, set against the baseline | — | — | §69.6 |
| L6 |  | COACH | — | **§69.1 conventions** · the header fields factored out of all twenty computation-tool entries — each is a separately named `@tool` with its own `args_schema=`, and mode-argument grouping is BANNED. **Twenty `@tool` decorators in `computation.py`, measured** | ✅ | `backend.knowledge.tool_args` | §69.1 |

#### L7 · Validation, gates, escalation

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L7 |  | — | **3.4** | `{Phase}Output` schemas + validators + UI | ✅ | `backend.phases.define.schema::DefineOutput` | §7, §40, §41, §53.1 |
| L7 | 15 | — | **7.3** | Nine-step HITL gate | ☐ | `backend.phases.nodes_common::gate_review` | §33 |
| L7 | 16 | — | **7.7** | The approve endpoint | ☐ | — | §33, §49, S-F34 |
| L7 | 13 | — | **7.1** | `DMAICGateValidator` + Layer 2b | ☐ | `absent: backend.validation.gate_validator::DMAICGateValidator` | §34, §35 |
| L7 | 14 | — | **7.2** | Layers 2c, 2d + `validation_stack` | ☐ | `absent: backend.validation.stack::validation_stack` | §34, §36 |
| L7 | 20 | — | **7.9** | Define end to end, on one fresh case | ☐ | — | §39.1, App. H |
| L7 | 19 | — | **7.8** | The gate steps that consume validation results | ☐ | — | §33, §34, §35, S-F27 |
| L7 | 17 | — | **7.4** | Two tiers + `warning` verdict | ☐ | `absent: backend.validation.tiers::WARNING` | §35 |
| L7 |  | — | **7.0** | The evaluation suite | ☐ | `absent: backend.evals` | §52 |
| L7 | 18 | — | **7.5** | Escalation | ☐ | `absent: backend.phases.escalate_v2::escalate` | §38 |
| L7 |  | — | **7.6** | The re-approval cascade | ☐ | `absent: backend.validation.cascade::reopen_field` | §37, §9.5 |
| L7 |  | GATE | **7.3** | **nothing pauses for a human — and since 2026-09-11 that is a RULING, not an oversight** · **the GATE interrupt is not built** — the `gate_review` node exists and passes through, and raises `interrupt()` at step 7.3. That is why `gate_attempts` cannot accumulate (WATCH 18), the supervisor graph is not yet the runtime (WATCH 23) and §47's reconciliation sweep cannot be written (WATCH 13). | ☐ | — | §33 |
| L7 |  | GATE | **7.2** | Layer 2a is live as `CoherenceMiddleware` and Layer 2b delegates to the v1 `validate_{phase}`; Layers 2c and 2d are step 7.2. **`GATE_MAX_ATTEMPTS=3` cannot fire**: with no `interrupt()` the subgraph reruns from the mapper each turn, so every submission reports attempt 1 (WATCH 18) | ⚠️ | — | §34 |
| L7 |  | GATE | **7.4** | the tier SETS exist on all five gate schemas and `tier_of()` reads them, but **nothing produces a `warning` verdict**: every finding still blocks equally, so a missing nice-to-have stops a project the way a missing baseline does — step 7.4 | ☐ | — | §35 |
| L7 |  | GATE | **7.1** | the **coaching** grader is live (§19.8) and the **gate** grader is not — `DMAICGateValidator` is step 7.1. The two are not redundant, and today only one of them runs | ⚠️ | — | §36 |
| L7 |  | GATE | **7.6**, **7.3** | the flag is set and §19.6 raises on it, but **the re-approval cascade this section specifies does not exist**: a contradiction against an approved value never reopens the field it contradicts — step 7.6. Position 6's `interrupt()` is guarded until 7.3 | ☐ | — | §37 |
| L7 |  | GATE | **7.5** | `escalate.py` exists and is **v1** — it takes `ImproveGraphState`, the class step 11.1 deletes. The v2 escalation path is step 7.5 | ☐ | — | §38 |
| L7 |  | GATE | — | five `{Phase}Output` schemas with their tier sets and assembly functions, in one registry (`gate_registry.py`), field counts pinned by `test_gate_documents.py` | ✅ | — | §40 |
| L7 |  | GATE | — | the structured `dict` fields are declared `dict` and Tier 1, and **no FMEA field exists on any schema** — both asserted | ✅ | — | §41 |
| L7 |  | GATE | — | `post_improvement_metrics` is pinned as the only Tier-1 cross-phase reference, asserted in `test_gate_documents.py` | ✅ | — | §42 |
| L7 |  | GATE | **7.0** | **no `backend/evals/` exists**, so coaching quality has no baseline and no later change can be shown to improve or regress it — step 7.0, whose dataset needs founder time | ☐ | — | §52 |
| L7 |  | GATE | — | **the three dicts exist and the four | ⚠️ | — | §63.6 |
| L7 |  | GATE | **6.20** | **the field is on all five schemas and DEFINE NOW WRITES IT** — `define_phase_metrics` derives one entry per registry metric at assembly, deterministically and with no model call (§39.1.9). **Measure, Analyse, Improve and Control still write nothing**, by the 2026-09-23 fence, so the keyed trail exists for one phase of five | ⚠️ | `backend.phases.define.schema::define_phase_metrics` | §63.9 |
| L7 |  | GATE | **7.3** | `gate_review` is a **pass-through** — no `interrupt()` is raised and `gate_apply` applies nothing. Define's own instance of §33's *nothing pauses for a human*. **Normalised at 6.37 from a prose-form marker no reader had ever matched** | ☐ | — | §39.1.11 |
| L7 |  | GATE | — | **S-C20** · `CriterionVerdict` | — | — | §62.1 |
| L7 |  | GATE | — | **S-F27** · The policy advisory | — | — | §62.10 |
| L7 |  | GATE | — | **S-F28** · Gate document assembly | — | — | §62.11 |
| L7 |  | GATE | — | **S-C21** · `GraderVerdict` | — | — | §62.2 |
| L7 |  | GATE | — | **S-C22** · `CoachingGraderVerdict` | — | — | §62.3 |
| L7 |  | GATE | — | **S-C23** · `CoherenceResult` | — | — | §62.4 |
| L7 |  | GATE | — | **S-C24** · `ConstraintCheckResult` / `ConstraintVerdict` | — | — | §62.5 |
| L7 |  | GATE | — | **S-C25** · `PolicyAdvisoryResult` | — | — | §62.6 |
| L7 |  | GATE | — | **S-C26** · `DMAICGateValidator` | — | — | §62.7 |
| L7 |  | GATE | — | **S-F25** · Layer 2c — the constraint check | — | — | §62.8 |
| L7 |  | GATE | — | **S-F26** · Layer 2d — the gate grader | — | — | §62.9 |
| L7 |  | GATE | — | **S-C27** · `DefineOutput` | — | — | §63.1 |
| L7 |  | GATE | — | **S-C28** · `MeasureOutput` | — | — | §63.2 |
| L7 |  | GATE | — | **S-C29** · `AnalyseOutput` | — | — | §63.3 |
| L7 |  | GATE | — | **S-C30** · `ImproveOutput` | — | — | §63.4 |
| L7 |  | GATE | — | **S-C31** · `ControlOutput` | — | — | §63.5 |
| L7 |  | GATE | — | **S-C32** · The three cross-phase reference dicts | — | — | §63.6 |
| L7 |  | GATE | — | **S-C33** · The three structured dict fields | — | — | §63.7 |
| L7 |  | GATE | — | **S-C38** · `metric_definitions` — the project metric registry | — | — | §63.8 |
| L7 |  | GATE | — | **S-C39** · `phase_metrics` — the per-phase placeholder | — | — | §63.9 |

#### L8 · Persistence and cross-cutting

| Layer | Order | Zone | Step | Fact — what the § specifies | State | Symbol | § |
|---|---|---|---|---|---|---|---|
| L8 |  | — | **2.3** | Dependency upgrade | ✅ | `installed: langgraph =1.2.11` | §53, §16 |
| L8 |  | — | **2.5** | Async conversion | ✅ | `backend.phases.subgraph_common::build_phase_subgraph` | §14, §49 |
| L8 |  | — | **2.7** | LLM factory · 6 roles → 11 | ✅ | `backend.core.llm::get_llm` | §21, §54 |
| L8 |  | — | **3.2** | `AzureBlobStore` | ✅ | `backend.core.store::AzureBlobStore` | §9, §10 |
| L8 |  | — | **3.5** | `storage/blob.py` — class → functions, sync → aio | ✅ | `backend.storage.blob::download_bytes` | §54, §10, §49 |
| L8 |  | — | **4.2** | `thread_id` + disconnect policy | ✅ | `backend.core.checkpointer::AzureBlobCheckpointSaver` | §16, §47, §49, §8 |
| L8 |  | — | **6.11** | The upload path (G-36) | ✅ | `backend.upload.parsers::PARSERS {document,pdf,spreadsheet,text}` | §29.1, §6, §10, §23.2, §65.4 |
| L8 |  | — | **6.13** | The evidence index migration | ✅ | `backend.knowledge.tools::rag_lookup_evidence` | §23.2, §23.2.1, §23.4, §24, §6 / S-C02, S-C09 |
| L8 |  | — | **6.34** | A node that runs out of time answers the Belt instead of failing (G-84) | ✅ | `backend.tests.test_turn_budget::test_a_slow_turn_answers_before_the_wall` | §4.8, §44, §45 |
| L8 |  | — | **6.52** | A turn always answers inside its budget | ✅ | `backend.tests.test_judges_once::test_the_graders_verdict_reaches_step_log` | §4.8, §19.7, §19.8, §44, §45 |
| L8 |  | — | **6.54** | The clients are built once, at startup, before any Belt waits for them | ✅ | `backend.tests.test_client_warmup::test_the_started_app_leaves_no_client_for_a_turn_to_build` | §44, §45, §51 |
| L8 |  | — | **8.0** | Turn telemetry and `@traceable` | ☐ | `absent: backend.core.tracing::traced_turn` | §51, §44 |
| L8 |  | — | **8.1** | Structured errors | ☐ | `absent: backend.errors::StructuredError` | §48 |
| L8 |  | — | **8.2** | Timeouts + compensating actions | ☐ | `absent: backend.core.timeouts::NODE_TIMEOUTS` | §45 |
| L8 |  | — | **8.3** | Circuit breakers + fallback chain | ☐ | `absent: backend.core.resilience::CircuitBreaker` | §46 |
| L8 |  | — | **8.6** | Context recovery (§44 Step 2) | ☐ | `absent: backend.core.recovery::recover_context` | §44 |
| L8 |  | — | **8.7** | `delete_blob` + upload lifecycle | ☐ | `absent: backend.storage.blob::delete_blob` | §10, §58 S-C08 |
| L8 |  | — | **8.4** | Level 3 cache | ⛔ | `absent: backend.core.cache::response_cache` | §46 |
| L8 |  | — | **8.5** | Graceful shutdown | ⛔ | `absent: backend.gateway.lifespan::drain` | §45 |
| L8 |  | — | **9.2** | Premium deployment's quota — the coach's own model call (G-53) | ⛔ | `azure: operational-premium.rateLimits =200000` | — |
| L8 |  | — | **11.1** | Delete v1 | ☐ | `backend.core.state::ImproveGraphState` | §54, App. D |
| L8 |  | STORE | — | both primitives are wired and distinct: the checkpointer on the parent graph (§16), the Store passed to nodes (§9). **Passing only a checkpointer is the mistake this section names, and the tree does not make it** | ✅ | — | §8 |
| L8 |  | STORE | — | `AzureBlobStore(BaseStore)` at 3.2 and **ten boundary mappers** — an input and an output pair per phase — at 3.3, whose only dependency is `BaseStore` | ✅ | — | §9 |
| L8 |  | STORE | — | `storage/blob.py` is module-level `async` functions since 3.5; the class is gone and `grep -rn "class ImproveBlobClient"` returns zero | ✅ | `absent: backend.storage.blob::ImproveBlobClient` | §10 |
| L8 |  | OPS | — | written by every node through one deterministic key helper. **Built incidentally rather than by a step**, which Appendix A ruled explicitly in the 2026-09-07 coverage audit | ✅ | — | §11 |
| L8 |  | STORE | — | `AzureBlobCheckpointSaver` on the parent graph keyed by `case_id`, live since 4.2; phase subgraphs carry no checkpointer of their own and the engine assigns `checkpoint_ns`. ⚠️ the ETag / `ConcurrentTurnError` guard on `latest.json` is **optimistic, not the specified lease** — a concurrent turn is LOST rather than interleaved, and a failed write orphans a history blob (WATCH 15, post-refactor) | ✅ | — | §16 |
| L8 |  | OPS | **8.2** | **Step 0 only.** `TimeoutPolicy(run_timeout=45)` is on the executor node and has been observed firing. Steps 1–6 are step 8.2, and `error_handler=` / `phase_error_recovery` is blocked on G-35 and G-06 (WATCH 16) | ☐ | — | §44 |
| L8 |  | OPS | **8.3**, **8.4** | circuit breaker (3 fails / 30s → OPEN) and the fallback chain are both step 8.3. ⛔ the L3 Redis cache is blocked — the resource is not provisioned (step 8.4) | ☐ | — | §46 |
| L8 |  | STORE | **7.3** | ABANDON: a disconnect mid-turn commits nothing, verified at 4.2 and pinned by `test_abandon.py`. ⚠ §47's reconciliation sweep needs `interrupt()`-paused threads to exist — step 7.3 | ✅ | — | §47 |
| L8 |  | OPS | **8.1** | `core/errors.py` carries the exception types, but **S-C34's structured payload — `severity` and `retry_recommendation` — is not produced**, so §46's circuit breaker and fallback chain have nothing to read — step 8.1 | ☐ | — | §48 |
| L8 |  | OPS | **8.0** | **`@traceable` on the executor slice only** — 4 backend files since 2026-09-24 (retriever, fusion, executor setup, `get_llm`), pulled forward by founder ruling; **zero** on the five `validate.py` files and on field extraction, which §51 names. This is the block that compounds: with no tracing every investigation needs a hand-built harness, and WATCH 28's *"set the limits from measured data"* cannot run at all — which is why it is scheduled at 8.0, ahead of the step that consumes it | ☐ | — | §51 |
| L8 |  | OPS | — | fail-fast environment validation at startup | ✅ | — | §53 |
| L8 |  | OPS | — | **S-C34** · `AgentImproveError` | — | — | §64.1 |
| L8 |  | OPS | — | **S-C35** · `CircuitBreaker` | — | — | §64.2 |
| L8 |  | OPS | — | **S-F29** · `phase_error_recovery` | — | — | §64.3 |
| L8 |  | OPS | — | **S-F30** · `degraded_mode_response` | — | — | §64.4 |
| L8 |  | OPS | — | **S-F31** · `synthesise_partial` | — | — | §64.5 |
| L8 |  | OPS | — | **S-F32** · `delete_or_flag_stale_in_case_index` | — | — | §64.6 |
| L8 |  | OPS | — | **S-F33** · `degraded_coaching_response` node | — | — | §64.7 |
---

### The Define path — estimate and epic (founder, 2026-09-25)

**Priority is the `Order` column above; dependency is each step's own card.**
Founder ruling 2026-09-25: *"Card wins on every Depends-on … Depends-on = card
only. Priority = Appendix F Order column."* So this table carries only what
neither place holds — the estimate, in working days, and the epic from
`tools/control_board/stories.py` (*proposed* where `stories.py` does not yet
list the step). **Off the path:** 10.1, 10.2 (the gate screen), 6.53 (gated),
6.60.

| Step | Estimate (days) | Epic |
|---|---|---|
| **6.61** | *not yet estimated — founder* | E2 *(proposed)* |
| **6.62** | *not yet estimated — founder* | E2 *(proposed)* |
| **10.0** | 3 | E4 |
| **6.59** | 2 | E2 *(proposed)* |
| **6.58** | 1 | E2 *(proposed)* |
| **6.56** | 1 | E2 *(proposed)* |
| **6.45** | 2 | E4 |
| **6.51** | 3 | E1 |
| **10.3** | 2 | E1 |
| **10.4** | 2 | E4 |
| **6.43** | 2 | E4 |
| **6.44** | 2 | E1 |
| **7.1** | 3 | E4 |
| **7.2** | 3 | E4 |
| **7.3** | 4 | E1 |
| **7.7** | 1 | E1 |
| **7.4** | 2 | E5 |
| **7.5** | 2 | E4 |
| **7.8** | 2 | E4 |
| **7.9** | 2 | E1 *(proposed)* |

**Founder inputs — milestones, not slips.** A step waiting on one shows as
waiting, never as late.

| Milestone | What | Blocks |
|---|---|---|
| **G-23** | The gate validator's return shape | 7.1 |
| **G-40 (F1)** | The Define rubric text | 7.2 |
| **Latency** | The latency ruling — question and options on 6.53's card | 6.53 |
| **F2** | The gate screen design | 10.2 (off the path) |

**Done, off the step list:** the coherence audit — `IMPR-2026-AD5`, six turns,
0 traces, 2026-09-25. Its findings are G-102 to G-106.

## Appendix G — The SPEC-GAP register

> **MOVED HERE FROM `ARCHITECTURE.md` §66 AT STEP 6.37.** The bible holds the
> architecture; this document holds the whole operational management of the
> refactoring. **Gaps keep their OWN register, keyed by G-number** (founder
> ruling 2026-09-18) rather than collapsing into the fact table: a gap listed
> inside another row's cell cannot carry its own state, and *every gap has a
> step or is marked unscheduled* is only checkable when each gap owns a row.
>
> **`Attaches to`** is the former `Marked at` column, renamed for what it
> always held — the facts the gap bears on. **`Step`** is new: the step that
> closes it, or **`unscheduled`**, which is a statement and not a placeholder.
>
> **OWNERSHIP IS A DECLARATION, NEVER A PROSE MENTION**, and the distinction
> is worth 16 rows. A step is the owner when Appendix D's row, Appendix F's
> `Item`, or the gap's own row in emphasis (`**Step 6.28**`) says so. A bare
> mention is a citation: **G-80's *"step 6.16"* names the step that BUILT the
> generator** and G-81's names the step whose coverage was lost, and neither
> gap appears anywhere in this document. Counting prose put 32 rows at
> `unscheduled`; counting declarations puts **48**.
>
> **Assertion 5 — *every gap names a fact that exists* — turns on at 6.39**,
> when the spec-entry rows land. Until then 26 gaps reference an `S-id` with
> no row, and forcing those to `unscheduled` would make one word mean two
> different things.

*Supersedes: none — new. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §S1.*
**Status: OPEN — this is a working register, not a ratified statement.**

**Every gap marked inline in Part XII has a row here, and every row here has an
inline marker.** That bidirectional correspondence is checkable and is one of
the §55.1 governance rules.

**86 gaps identified. Twenty-four are closed or resolved. 62 are open.** *(G-55 and G-56 registered 2026-09-13 at brief step 7, both converted from CLAUDE.md prose that was retired with it — §19.4's citation ratchet and §18.1's live half. **An open item stated only in prose is not scheduled by anything**, which is the reason for the conversion rather than the deletion. §18.1's other half turned out to have been closed on 2026-09-03 and is counted among the sixteen.)*  *(G-54 registered 2026-09-12 immediately after withdrawing C-3: the failure was a SOURCE METHOD, not a typo, and the same method produced every other verdict in that log.)* *(G-52 and G-53 registered 2026-09-12 while correcting §19's hook surface — the ordering test that cannot observe order, and the premium deployment's rate limit. Both carry a step number, because a gap without one does not render on the board and so is not scheduled by anything.)* *(G-50 and G-51 registered 2026-09-11 by the three-way alignment audit — `CoachingResponse` built at four of S-C05's eight fields, and `storage/models.py` defining eleven models where S-C09 names six; reasoning in that commit body per §56.2.)* *(G-49 registered 2026-09-10 — the executor's tool selection, found at step 6.13 and reproduced on 6.12's code. `docs/_archive/DECISIONS.md` Part AU2.)* *(G-14 closed 2026-09-03 at procedure step 5.2 — `docs/_archive/DECISIONS.md` Part AC.)* *(G-21
closed 2026-09-01 at procedure step 3.5 — `docs/_archive/DECISIONS.md` Part Y.)* *(Two were
added and resolved in the same pass on 2026-08-26 — G-45 and G-46, the metric
registry's two spec entries. Registering a gap you are about to close in the
same commit looks like bookkeeping theatre and is not: §55.1 requires every
referenced spec to resolve to an entry, and the register is where that is
checkable. A reference that resolves only because nobody looked is exactly the
failure §55 exists to name.)* *(This line
read "Eight … 36" until 2026-08-26: G-38's closure on 2026-08-25 was recorded in
§66.6 and in the changelog but never counted here. Corrected in the same pass
that closed G-25 — the count and the table now agree, which is the §55.1
bidirectional rule applied to the summary as well as the rows.)* None was
filled by the 2026-08-23 conversion pass — that was the pass's binding
constraint; G-03 and G-42 were resolved together on 2026-08-24 (DECISIONS
§T1), and **G-43 was raised and closed the same day as a false alarm**
(DECISIONS §U1). **Its narrower successor G-44 was registered in its place and
resolved the same day** — the wrapper node's inner `subgraph.ainvoke` does
persist `PhaseState`, provided it is called directly inside the node function
and never behind a tool (§16).

### 66.1 Group A — founder ruling required

**EMPTY. No founder rulings are currently outstanding.** G-01 and G-02, the two
that stood here since the conversion pass, were resolved together on 2026-08-24
(§66.6). The group is kept rather than deleted because it is where the next one
lands.

| # | Gap | Attaches to | Step |
|---|---|---|---|

### 66.2 Group B — cross-check defects

**The same defect class as `route_after_phase` (DECISIONS §R2): specified code
reading state a schema does not declare.** Each fix is a design choice, and
adding a `PhaseState` field is a §56 amendment. **G-03, G-42 and G-04 have been
resolved out of this group** (§66.6); G-05, G-06, G-07 and G-08 remain.

| # | Gap | Attaches to | Step |
|---|---|---|---|
| ~~**G-03**~~ | **RESOLVED 2026-08-24** — `PhaseState` gains `case_id` and `current_phase`, copied down by the input mapper and read-only in the subgraph. See §66.6 and DECISIONS §T1 | — | closed |
| **G-05** | `extracted_entity` is read off `PhaseState` (§26); undeclared, and no writer is named anywhere | S-C02, S-F09 | **6.10**, **6.20** |
| **G-47** | **§49's endpoint table and S-F34's copy of it are not what `gateway/routes.py` serves.** Six routes exist in the tree and in neither table — `/health`, `/summarise`, `/context`, `POST /gate`, `/gate/review/{case}/{phase}`, `/files/{case}/{file}`. **`POST /gate` is a shape disagreement rather than an omission**: the spec ratifies three gate routes and the tree serves one. `/ask/stream` is the opposite case and is excluded — ratified, unbuilt, owned by step 10.1. **This is a spec-versus-tree cross-check, not the state-schema class the rest of this group holds**, and it is here because that is what the group's title covers. Raised 2026-09-08 while scoping 6.11, when `/upload` was found to be in the tree and in neither table; that row was ratified into both (Part AP5) and the remaining six registered rather than fixed in passing — which of them are ratified, which are v1 residue dying at 11.1, and whether `/gate` becomes three are founder questions | §49, S-F34 | **unscheduled** |
| **G-49** | **THE EXECUTOR DOES NOT CALL THE TOOL ITS OWN PLANNER NAMES.** Given a plan reading *"call `load_evidence_series` on `uploads/IMPR-2026-ED8/complaints.csv` before asking for anything further"*, the executor issues ~6 `rag_lookup_evidence` calls (19 underlying searches, 3 per multi-query) and **never calls `load_evidence_series` at all**, until the 45s per-node timeout ends the turn. No `uploads/` blob is fetched in the whole turn. **Found at step 6.13, reproduced identically at `1714d75` on 6.12's code**, so it belongs to neither step. **It blocks the `live-run` half of 6.7, 6.12 and 6.13** — three steps whose remaining verification runs through this path, and no Define turn on `IMPR-2026-ED8` completes. §17's planner/executor split gives the planner the routing decision and the executor the execution; here the executor silently substitutes its own. **DIAGNOSED at step 6.18, 2026-09-11 — THE CAUSE IS LAYER 2: THE PLAN DOES NOT REACH THE EXECUTOR'S CONTEXT.** `executor()` invokes the agent with `{"messages": prior}`; `coaching_plan` is read for the logger and for `step_log` and for nothing else; `system_prompt` is a per-phase constant; and `BeforeModelStateInjection` — the only middleware handed state — never mentions `coaching_plan`, `focus_field` or `next_action`. Measured at the boundary, the planner's imperative reaches none of the three channels the model reads (system prompt 7,770 chars, injected block 797 chars, messages 5 chars), and `test_the_planners_instruction_reaches_the_model` pins it `xfail(strict=True)`. **Layer 1 is ruled out** — `load_evidence_series` is in `UNIVERSAL_TOOLS` and bound in all five phases. **Layer 3 is excluded by construction** — a model cannot deprioritise what is not in its request. **Layer 4 is present and is not the cause** — the manifest reaches the coach every turn with the file, `NOT YET READ`, the `blob_path` and the tool that opens it, 2,893 composed chars on the failing run, and 18 evidence searches followed anyway: ranking explains a preference, not a missing instruction. **THE FIX IS NOT 6.18's — it is step 6.21, `GATED` on a founder ruling on the transport** (four candidates costed in that step; two of them amend §17). **6.9 IS RULED OFF THIS LIST, 2026-09-11 — it never belonged:** its Verify is `pytest`, it has no live clause, and its Done-when is satisfied by the tree. One correction the ruling turned up — the audit recorded *"a test asserts the count and both instructions per file"* as satisfied and only the count was; `test_every_skill_md_carries_both_mandatory_instructions` now pins both. The three live-runs re-run on the first `live-run` after 6.21 lands, **re-reported to the founder if that has not happened by 2026-09-25**. Reproduction re-run on `09960df`: the identical failure at 45.141s against 2026-09-10's 45.157s. `DECISIONS.md` Part AU2 | S-F04, S-F13, S-F57, §17, §26 | **6.18**, **6.21** |
| ~~**G-50**~~ | **CLOSED 2026-09-14 at step 6.19. RE-EXAMINED at step 10.0 (2026-09-25), as its card required: UPHELD, with its scope stated — G-50 is the CLASS (`CoachingResponse` built at four of eight fields), which 6.19 closed. The OUTCOME — §50.1's render contract reaching the Belt — was a different gap, G-69, and step 10.0 closes it.** `CoachingResponse` carries all eight ratified fields: `explanation`, `example`, `prompt` and `progress` join `message`, `fields_captured`, `citations` and `contradiction_flag`. **§50.1's render contract is schema-backed at last** — the UI can draw one block per field without parsing prose, where the only presentational field it received was `message`, the single free-text blob that section forbids. The four are transcribed from S-C05 rather than designed here, on the RATIFIED-NOT-YET-APPLIED precedent §23.2 set, and the class docstring's conformance claim — *“the four fields below are transcribed from that entry”* against an entry defining eight — is corrected with them. **`verify_built.py`'s expectation moved 4 → 8 in the same commit**, which its own comment required: *“or this check passes the day it lands.”* Twenty test constructions updated; 941 pass | S-C05, §20, §50.1, §32 | closed |
| **G-51** | **`storage/models.py` DEFINES ELEVEN MODELS AND S-C09 NAMES SIX.** Unnamed: `AnalystOutputRecord`, `CaseRegistry`, `ChartRecord`, `CitationRecord`, `TeamMemberRecord`. **The same shape as Part AP6 one level up** — AP6 found six `UploadRecord` fields in the tree and in no document; nothing then checked the model LIST. `CaseRegistry` is the sharpest: `GET /registry`, which §49 ratifies, returns it. Found 2026-09-11 by the three-way alignment audit | S-C09, §10, §23.3 | **unscheduled** |
| **G-48** | **`backend/upload/**` makes a plain model call for a typed result and is on none of the four paths `pattern-2` permits.** §4.6 scopes the builder-style structured-output call to *"a plain model invocation inside a tool, middleware, or validator"*, plus the phase planner; `deprecated_patterns.yaml` excludes exactly `knowledge/**`, `middleware/**`, `phases/**/validate.py`, `phases/**/orchestrate.py` and the planner's site. **The upload interpretation is structurally the same call** — not an agent, no model-tools loop for `response_format=` to attach to — and the hook blocks it, so the call parses JSON by hand. **The cost is already recorded**: the prompt was written for the binding, the call was switched to parsing, and the prompt was not — so every summary was the degradation fallback and 781 green tests could not see it, because none crossed that boundary (Part AP6). A schema binding cannot drift out of contract with its own parser; a hand-written one can, and did. **Registered OPEN and deliberately not fixed here** — §8 forbids amending a rule in passing during a feature change, and the ruling waits on reading what `9fce8fc` recorded when it scoped `pattern-2`. The registry's own comment already says twice that "the exclusion list simply predated the files"; this would be the third instance | §4.6, `deprecated_patterns.yaml` | **unscheduled** |
| **G-06** | `extraction_error` and `extraction_incomplete` are written into `PhaseState` by `phase_error_recovery` (§45); neither is declared | S-C02, S-F29 | **8.2** |
| **G-07** | `state["structured_response"]` is read by `ContradictionDetectionMiddleware` (§19.6). Whether middleware observes `PhaseState` or `create_agent`'s internal agent state is unstated | S-F04, S-C10 | **unscheduled** |
| **G-08** | `validation_stack.get_acknowledged_gaps()` (§40) is attribute access on a node, and §14 requires nodes to be module-level async functions. Where acknowledged gaps are produced and how they reach assembly is unspecified | S-F05, S-F07, S-F28 | **unscheduled** |
| ~~**G-52**~~ | **CLOSED 2026-09-13 at step 6.22.** `backend/tests/test_middleware_execution_order.py` invokes the REAL compiled agent — `GenericFakeChatModel`, no network — and records which `after_agent` hooks fire in what sequence: **8 → 7 → 6**, contradiction, coherence, grader. The stubbed test is **renamed** to `test_the_declared_middleware_list_is_the_ratified_layering`, which is what it actually checks; the old name claimed execution it never observed, and a name that claims more than the body delivers tells the next reader the ground is covered. **The Done-when's specified demonstration did not hold and the step records why** — reversing positions 6 and 8 fails BOTH tests, so it separates nothing; removing position 8's hooks while leaving the declared list intact passes the stubbed test 5/5 and fails the new one. | §19, §19.1, §19.6, §19.7, §19.8 | closed |
| **G-53** | **AZURE RETURNS 429 ON THE PREMIUM DEPLOYMENT, SO NO LIVE RUN REACHES A COACHED TURN.** `operational-premium` (gpt-4o, westeurope) rate-limits the coach's own model call; `ModelRetryMiddleware` exhausts its two retries, the answer becomes the 429 text, `CoherenceMiddleware` correctly fails it three times and stands the grader down per S-C13 B3. **Not a defect — a quota condition** — but it blocks every remaining `live-run` verification, and it means the HEALTHY path is still unobserved: coherence passing on its first attempt and `DMAICGraderMiddleware` actually grading have been seen in no trace. Four runs on 2026-09-12, all degraded identically. Resolving the quota is **step 9.2**; it is EXTERNAL, like §9.0 and §9.1, because the action is a provisioning change and not a code change. | §19.4, §19.7, §19.8, §21 | **9.2** |
| ~~**G-54**~~ | **CLOSED 2026-09-13 at step 6.23.** All nine entries in `BIBLE_VERIFICATION_LOG.md` carry a `Source method` row and every one with an installed object was re-run against it: **C-1** `retries` absent and `max_retries` present; **C-2** `prompt` absent and `system_prompt` present; **C-3** withdrawn (`vars(AgentMiddleware)`); **S-1** partly withdrawn, two of three reasons stand; **S-2** installed 1.2.11 / 1.3.16 / 1.0.8, and the class of fact now has an owner in `requirements.txt` (§55.4), so the entry should not be cited for a version again; **E-1** `set_node_defaults` present on `StateGraph`; **E-3** `TimeoutPolicy` carries `run_timeout`, `idle_timeout`, `refresh_on`. **NO VERDICT MOVED**, so nothing propagated — the two that were wrong had already been caught. **Two entries are NOT fully settled by introspection and say so rather than being marked verified**: **E-2** claims an ORDER, which is behaviour and needs a runtime test; **E-4** is about which posts an external index published, for which a page is the right source. | §9, §16.3, §25, §53, §55.1 | closed |
| **G-55** | **1,128 PARENTHETICAL `(§x)` CITATIONS PREDATE §19.2's RULE THAT A CODE IS NEVER RENDERED BARE.** 310 in CLAUDE.md as it then stood, 818 in this file. **RULED 2026-09-13: NO SWEEP. The ratchet stands** — every rule touched from 2026-09-11 names what its citations point at, and the back-catalogue stands as written. A single pass would be a diff across nearly every rule in the constitution, for a gain that arrives anyway as rules are amended. **Revisit when the platform reference is authored FROM Agent Improve** (§53's forward-document ruling): that pass rewrites citations wholesale, so the sweep costs nothing done alongside it and a diff of its own before then. Carried at **step 11.2**, governance close-out, which is where the handover is marked. Was CLAUDE.md §19.4's open item; retired from prose at brief step 7 because an open item that renders nowhere is not scheduled. | §19.1, §19.2, §55.1, §56 | **11.2** |
| **G-59** | **THE OWNERSHIP CHECK CANNOT COVER THE PATH MOST EDITS TAKE, AND THE FIX IS RATIFIED BUT NOT BUILT.** `fact-ownership-guard.py` runs on `PreToolUse` with matcher `Write|Edit|MultiEdit` and reads `content` / `new_string` — **fields a Bash envelope does not carry**. In auto mode Bash is the primary edit path, so the guard did not run on the great majority of this session's edits. **Widening the matcher is NOT the fix**: `extract()` would return `""` and the guard would early-exit, giving a check that always passes — CONTINUITY §7's *a check that cannot fail*, recorded as coverage. **Static shell parsing cannot recover the content either**: measured in one session, files were written via heredoc Python, an external script, `sed -i`, `printf >>`, `cp` and `git checkout`, and four of those six carry no content in the command string at all. **RULED 2026-09-14 (§55.5): move the check to the COMMIT GATE**, over the staged governed documents — the index holds the final content whatever mechanism produced it, it also catches writes by a peer session or by hand, and it costs **2.52 s once per commit** against a measured **~2.8 s per Bash call** if the guards ran there. The cost admitted: it catches the restatement at commit rather than at write. **Step 6.28** | §55, §55.4, §55.5 | **6.28** |
| **G-60** | **SEARCH INDEX SCHEMAS ARE AN OWNERSHIP CLASS WITH NO REGISTERED OWNER.** CLAUDE.md's *Facts have one owner* table names eight classes; `fact_owners.yaml` registers **five**. Three are unregistered, and G-56 names only two of them — gate tier splits and tool inventory. **This is the third, and it was in no gap until now.** It is the hardest of the three: the table gives the owner as *“the index definition, confirmed by query”*, so the owner is a **live Azure resource**, not a file the guard can parse — a derive step would need a network call on the write path, which is not viable at the measured cost. **Needs a ruling before it needs engineering**, exactly as G-56's two do; the candidates are a cached schema snapshot with a staleness rule, or ruling the class out of mechanical ownership and leaving it to §7.3's read-the-live-definition instruction. **STEP 6.29** — the ruling is the step's work, and the registry row is one line after it. **Given a step number on 2026-09-14 rather than a name and a date**: *ruling first, engineering second* with no owner, no deadline and no consequence is the shape *live-run owed* had when four of them stacked up over six days. A step renders on the board and is picked up by the cursor; a sentence does not | §55.4, §7.3, §23 | **6.28**, **6.29** |
| **G-63** | **THE NODE-ISSUED READ NAMES NO COLUMN, SO IT LOADS NOTHING — AND THE 45s TIMEOUT IS ITS CONSEQUENCE, NOT ITS CAUSE.** Step 6.21's option C works as a TRANSPORT: on trace `01a09ff4-db43-7532-bec0-89329f886482` (2026-09-14 12:46:59) the node dispatched `load_evidence_series` on the path the plan named, before the model, with no error. **But it dispatched `column="(not specified)"`**, and the tool answered `{"ok": false, "reason": "no_such_column", "columns": ["date","complaints","reason"]}` — **so no evidence was loaded.** The coach, holding no data, issued three `rag_lookup_evidence` calls at ~9.5s each and the executor hit its wall at **45.156s**. **THE CAUSE IS AT THE ARGUMENT LAYER, NOT THE TRANSPORT LAYER.** `_routed_column` derives the column from an open ask's `expected_shape.columns`; **Define populates no ask shapes**, which `_unconsumed_for_open_ask`'s own docstring already records — *“With Define carrying no ask shapes the two agreed by accident”*. So **every Define routed read is a placeholder read by construction**, and always has been. **The framing hypothesis is RULED OUT as the cause and kept as a separate finding**: the question was whether the result lands *“already answered, do not search”* or merely present, the §19.1/G-24 seam applied to the plan's RESULT. There was no result to frame — `ok:false`. Separately, the tool's message told the coach to *“Ask the Belt which of those holds the value you need”* and the coach searched instead; that behaviour is real and has **no evidence independent of this defect**. **OCCURRENCE CAUSE FIXED 2026-09-15; THE GAP STAYS OPEN ON ITS ESCAPE HALF.** `_routed_column` now returns `None` rather than a placeholder, the column comes from the ask or from the file’s own header (`knowledge/tools.py::first_numeric_column`), and **when neither answers the node does not dispatch** — the manifest carries the file instead, which is the pre-6.21 behaviour. The `xfail(strict=True)` probe is replaced by seven tests asserting on the DISPATCHED CALL rather than on a constant, so a later move to Define ask shapes or a plan-carried column passes them unchanged. **The span reported `status: "success"` throughout**, which is the escape cause: nothing distinguishes a routed read that loaded data from one that did not — **and THAT half is not fixed.** A routed read that reports its own outcome is **step 8.0**’s turn telemetry, and this row is what keeps it scheduled. **STEP 6.21 IS ALSO NOT CLOSED BY THE FIX**: its Done-when owes a `live-run` on `IMPR-2026-ED8` carrying the 6.7 / 6.12 / 6.13 live halves, and that evidence does not exist yet | §17, §26, §24, S-F13, §19.1 | **8.0** |
| **G-64** | **APPENDIX A IS A HAND-MAINTAINED DUPLICATE OF A FACT EVERY STEP SECTION ALREADY OWNS, AND IT HAS FALLEN ELEVEN ROWS BEHIND.** `REFACTORING_PROCEDURE.md` Appendix A maps each step to its reference sections. **Every step section ALSO carries its own `| **Reference §** |` row**, and that row is the one a reader of the step actually sees. Appendix A restates it. **Found 2026-09-15 by step 6.31’s matrix seed**: Appendix A has **59 rows against Appendix D’s 70**, missing 6.22–6.31 and 9.2. **THE FIRST READING OF THIS FINDING WAS WRONG AND IS RECORDED AS SUCH** — it was reported as *“ten steps have no reference section”*, which would breach Appendix A’s own rule that *“a step with no reference section is not a step”*. **All eleven DO have one.** Nothing is undocumented; the COPY is incomplete, which is a different defect with a different fix. **This is `Facts have one owner`, the same class as G-58** — the watched-path list stated in §55.2 and hardcoded in the guard — and it drifts the same way: the copy is updated when someone remembers. **THE FIX IS NOT TO TYPE ELEVEN ROWS.** Appendix A becomes a projection of the step sections’ own `Reference §` rows, or is asserted against them by set equality in both directions — **the check shape already exists** as `verify_built.py::matrix_covers_appendix_d`, built at 6.31, and should be generalised rather than rewritten. Filling the rows by hand would leave the second copy in place and buy one commit of agreement | §55.1, §55.4, Appendix A, Appendix D | **unscheduled** |
| **G-65** | **A COMPLETED STEP THAT LANDED OUT OF BAND RENDERS RED ON THE BOARD.** `EXTERNAL`, `BLOCKED` and `GATED` all map to the BLOCKED lane in `build_board.py::assign_lanes`, and **§55.2 ratifies red as *“cannot proceed”*.** But `EXTERNAL` also marks a step whose work is DONE and simply landed under a subject the git-log scan cannot see. **9.0 has rendered this way since it landed** as `feat(knowledge): 871637f`, and **6.22 joins it 2026-09-15** (`2e17f3f`). **Two finished steps shown as blocked, on the one artefact a founder opens.** §55.2’s own colour ruling is the thing being broken: *“a lane state and a marker state may never share a colour”* was written because a reader cannot hold *where it sits* and *whether it works* off one hue — and this is the same error in the lane axis alone. **NOT A STATUS-TOKEN PROBLEM**, so widening the vocabulary again would not fix it: `EXTERNAL` is now true on its own terms for both cases (procedure reading conventions, 2026-09-15). **It is a LANE-ASSIGNMENT fix** — a row whose status cites a landing commit belongs in DONE, and the pointer skips DONE already. **Registered rather than fixed at 6.31** because that commit is a 70-row restructure and a lane change needs its own mutation proof | §55.2, Appendix D, `build_board.py` | **6.32** |
| **G-66** | **A BACKEND ERROR RENDERS AS “No cases yet — create your first one.”** `loadRegistry` does `fetch(...).then(r=>r.json())` with **no `r.ok` check**, then branches on `!data.length`. A 503 `{"detail":"Storage not configured"}` is a valid JSON OBJECT, so `data.length` is `undefined`, falsy, and the empty-state message renders — **byte-identical to a genuinely empty registry**. The `catch` arm that says *“is the backend running?”* is reached only on a network-level failure, never on a 4xx or 5xx. **Systemic: 10 of 12 `fetch` calls ignore `r.ok`**; only the case refresh and the gate review check it. `openWorkspace` is the worst of them — a 404 body becomes `S.case` and the workspace renders around `{detail: …}`. **Found 2026-09-15 by the UI audit, from the founder being unable to see IMPR-2026-0E5 while `verify_store` resolved it from the same `load_registry`.** The registry may or may not have held the case — **the defect is that the UI cannot tell you which**, and one read-only `curl -i /registry` separates them. FIXED 2026-09-15 | §49, §50.1, §55.1, `ui/index.html` | **unscheduled** |
| **G-67** | **THE NEW-CASE FORM DISPLAYS AN ID THAT IS DISCARDED ON SUBMIT.** `initCreate` writes `IMPR-{year}-{Math.random().toString(36).substr(2,3).toUpperCase()}` into the form. **No endpoint is called on mount**, so an abandoned form reserves nothing and writes nothing — abandoned forms are NOT how empty cases accumulate. **But `submitCreateCase` does not send `case_id` either**, and `POST /cases` mints its own from `str(uuid.uuid4())[:3].upper()`. So the id the Belt is shown is never the id the case gets. **`IMPR-2026-GTN` is the proof**: `uuid4()` is HEX, and `G`, `T`, `N` are not hex digits — that string can only have come from the browser's base36. A false affordance on the one screen where identity is established. NOT FIXED | §49, §50.1, §55.1, `ui/index.html` | **unscheduled** |
| **G-68** | **THE CASE ID SPACE IS 4,096 VALUES AND A COLLISION IS A 500.** `str(uuid.uuid4())[:3].upper()` is three hex characters — 16³. **By the birthday bound, collision probability passes 50% at about 75 cases**, and roughly 1% is reached by the ninth case. `blob.create_case` raises `ValueError` when the path exists; `POST /cases` has no handler for it, so it surfaces as an unhandled 500 and the UI shows `toast('Error creating case: ' + detail)`. **This has a SHELF LIFE rather than being theoretical** — it is not a question of whether but of how many cases, and the failure arrives as an opaque server error on the Belt's first action. NOT FIXED, and deliberately so: it is a data-shape change and the live turn comes first | §49, `gateway/routes.py`, `storage/blob.py` | **unscheduled** |
| ~~**G-69**~~ | **CLOSED 2026-09-25 at step 10.0.** The four blocks reach the Belt: `AskResponse` declares them, the route projects them from the reply message, the UI draws them (step 10.0). **§50.1'S FOUR PRESENTATIONAL FIELDS NEVER LEAVE THE BACKEND — 6.19 SHIPPED THE SCHEMA AND NOT THE OUTCOME.** Step 6.19 added `explanation`, `example`, `prompt` and `progress` to `CoachingResponse` and closed G-50 on that basis. **`AskResponse` carries none of them.** `routes.py` builds `answer=(reply.content if reply is not None else "Processing…")` and discards the other four, so the API surface still emits the single free-text blob §50.1 exists to forbid. The UI reads `resp.answer` alone and renders one bubble; its only `explanation`/`example` references are `s.explainer.*`, a STATIC per-section explainer baked into the HTML and unrelated to the coach. **The fields are produced every turn and thrown away at the boundary.** **G-50's closure should be re-examined against this**: the schema half landed, the render contract did not, and §50.1 remains prompt-hoped — which is the condition G-50 named. **6.19 is landed and stays landed**; a new step delivers the outcome. Found 2026-09-15 by the UI audit | §20, §50.1, S-C05, §49 | closed |
| **G-70** | **A FAILED TURN SURFACES AS A THREE-SECOND TOAST AND NOTHING ELSE.** The executor's `TimeoutPolicy(run_timeout=45)` fires, LangGraph raises, `/ask`'s bare `except Exception` returns `HTTPException(500, f"Graph error: {e}")`. The UI lands on `toast('Error: ' + resp.detail)` with `dur=3000`. **After 45 seconds of a typing indicator the Belt gets three seconds of a raw Python exception string**, their own message left in the transcript with no reply and no error marker, no retry affordance and nothing persisted — scroll away and the failure is gone. **There is no client-side timeout at all**: `AbortController` appears zero times, so a server hanging past 45s spins the indicator indefinitely. **This and step 8.0's telemetry gap are one blind spot seen from both ends** — the span reported `status: success` and the Belt saw a toast. NOT FIXED | §44, §4.8, §50, §51 | **unscheduled** |
| **G-71** | **THE UI HAS NO STEP, NO `Touches` AND NO ANCHOR.** `agent-improve/ui/index.html` is **7,273 lines** and is the entire Belt-facing product. **No Appendix D row builds it, no step's `Touches` names it, and no Appendix F anchor covers it.** Zone `UI` has exactly two rows, 10.1 and 10.2, and both are FUTURE work — so every line of the UI a Belt uses today was written outside the spine and is verified by nothing. **This is why the UI was the only layer with no audit behind it**: there was no row to hang one on. Found 2026-09-15 by the UI audit, which is the first reading of that file against the ratified tables | §49, §50, §55.1, Appendix D, Appendix F | **unscheduled** |
| **G-72** | **A `repo:` ANCHOR CAN NAME A PATH UNDER A DIRECTORY THAT DOES NOT EXIST, MAKING `absent:` PERMANENTLY TRUE.** Appendix F's row for step 10.2 carries `absent: repo:agent-improve/frontend/gate_document.js`. **There is no `agent-improve/frontend/` directory** — the UI is `agent-improve/ui/`. So the cell passes today and **would keep passing after 10.2 ships**, because 10.2 will ship into `ui/`. **This is the SECOND instance of the unfailable-`absent:` class in one day.** The first was step 6.31's own row naming a module that could never import, which is why `MalformedAnchor` exists — but that guard validates MODULE names and does not reach a path anchor. **An `absent:` anchor is where an unfailable check hides**: a positive anchor that cannot resolve fails loudly, a negative one goes quiet. **Fix the CLASS, not the row.** FIXED 2026-09-15 | §55.1, §55.2, Appendix F | **unscheduled** |
| **G-73** | **THE CREATE SCREEN LISTS THE BELT’S FILES BACK TO THEM AND THEN DISCARDS THEM.** `handleCreateFiles(input)` renders `input.files` into `#create-uploaded` as a list of filenames — **and stores the FileList nowhere.** `submitCreateCase` contains no `FormData`, no `/upload` call and no reference to the input at all, so it posts `POST /cases` and navigates away. **The Belt gets positive visual confirmation that their evidence is attached, and nothing is ever uploaded.** Worse than a missing feature: a missing attach control teaches the Belt to upload later, and a list of their own filenames teaches them it is already done. The files are unrecoverable — the FileList dies with the screen. **§29.1 makes `/upload` the ONLY channel through which external data enters the system**, and this screen presents a second one that goes nowhere. Found 2026-09-15 | §29.1, §49, §50, `ui/index.html` | **unscheduled** |
| ~~**G-74**~~ | **THE CHAT UPLOAD REPORTED SUCCESS ON EVERY SERVER FAILURE. CLOSED 2026-09-15 by `04644e5`.** `handleChatFile` did `fetch(…).then(r=>r.json())` and then unconditionally appended *“I’ve received the file … Let me process it.”* — so a **422 refusal**, the path §6.11 built specifically to tell a Belt their file could not be read, rendered as the coach confirming receipt. The Belt then waited for coaching on a file the system had rejected and never stored. **Closed by the G-66 sweep rather than on its own merits**: `apiJSON` throws on a non-2xx, so the confirmation line is now unreachable on failure and the refusal reason surfaces instead. **Registered although already closed, deliberately** — §55.1 requires a defect found by an audit to be recorded whether or not the fix happened to land first, and a defect that leaves no trace is one nobody can check did not return | §29.1, §4.8, §50, `ui/index.html` | closed |
| **G-75** | **THE BOARD DISPLAYS ONE GAP PER MARKER AND SILENTLY DROPS THE REST — IN APPENDIX F’S OWN RENDERER.** `build_board.py` computes `gnums(m)`, the full list of open gaps whose refs match a marker, and **both render sites then take `.split(", ")[0]`** — the highest-numbered one — and discard the others with no `+N more` and no indication anything was dropped. Measured 2026-09-15: **seven gaps registered, three displayed.** §49’s marker carries G-47, G-66, G-67, G-68, G-69 and G-71 and **renders G-71 alone**. **THIS IS THE FAILURE CLASS APPENDIX F EXISTS FOR, SITTING INSIDE APPENDIX F’S RENDERER.** §66’s header states that a gap without a step *“does not render on the board and so is not scheduled by anything”* — a gap WITH a step that still does not render fails the same way, and the board is the artefact a founder reads to decide what is scheduled. **A register that is complete and a board that under-reports it are indistinguishable to the reader**, which is the `1 of 5 SKILL.md files written` shape one level up. Not a data defect — `read_gaps` returns all seven and is correct | §55.1, §55.2, §66, Appendix F | **unscheduled** |
| ~~**G-76**~~ | **CLOSED 2026-09-25 at step 10.0.** The grader's warning reaches the Belt on the response and on screen, in the founder's wording (step 10.0). **THE GRADER'S BELT-VISIBLE WARNING IS VISIBLE TO NOBODY — A FAILING QUALITY GATE SHIPS SILENTLY.** §19.8's grader runs every turn. On `max_iterations` (3) it logs *“passing the turn through with a Belt-visible warning”* and returns `{"grader_warning": MAX_ITERATIONS_WARNING}` — `grader.py:152`, **the only write in the tree**. It is **declared on NO state schema** (absent from `core/substate.py` and `core/state.py`), **carried on no response model**, and **read in zero places** across `backend/` and `ui/index.html`. **It does not die at `routes.py:668` with §50.1's four fields (G-69)** — it never reaches the route at all; it is returned as an UNDECLARED key into `create_agent`'s internal state and goes nowhere. Observed on the 2026-09-15 live turn: the coach failed its own rubric three times, the turn returned 200, and the founder saw nothing. **SECOND ESCAPE CAUSE, and it is the G-63 shape exactly**: `test_max_iterations_passes_through_with_a_belt_visible_warning` asserts `out == {"grader_warning": …}` — it checks the middleware RETURNS a dict and never that a Belt sees anything. A test named for the contract, asserting the source. The STRUCTURAL escape is **G-77**, registered separately because it outlives this fix | §19.8, §34, §36, §49, S-C05 | closed |
| **G-77** | **AN UNDECLARED STATE KEY IS INVISIBLE TO THE F-15 PAIRING CHECK, SO “WRITTEN AND NEVER READ” GOES UNCAUGHT FOR ANY MIDDLEWARE THAT RETURNS ONE.** `verify_built.py`'s F-15 pass walks the fields DECLARED on `SupervisorState` and `PhaseState` plus `artifacts` keys, and asserts a writer and a reader for each — *“one check for a pattern that recurred seven times”*. **A key that is returned from a middleware without being declared anywhere is in neither population**, so the check cannot see it and reports green. `grader_warning` (G-76) is the first confirmed instance and was found by a live run, not by any check. **REGISTERED SEPARATELY FROM G-76 DELIBERATELY**: fixing `grader_warning` closes one field and leaves the blind spot open for the next middleware that returns an ad-hoc key — and §19 mounts eight of them. **The escape cause outlives the defect**, which is the whole reason §20 splits D4 in two | §55.2, §19, F-15, `verify_built.py` | **unscheduled** |
| **G-78** | **EVERY COACHED FIELD CAPTURE DESTROYS THE ONES BEFORE IT, AND THE GATE DOCUMENT CANNOT ACCUMULATE.** Two defects at the ends of one working path. **(a) THE INPUT MAPPER BLANKS THE ACCUMULATOR EVERY TURN** — `mappers_common.py:252-253` seeds `"draft": {}` AND `"artifacts": {}`, so `artifacts`, documented at `nodes_common.py:1275` as *“the accumulation”*, accumulates within a single turn and is reset on the next. `artifacts` and `draft` are therefore always identical. **This is the defect 6.11 fixed one field over**: the comment directly beneath those two lines records that `uploads` was blanked *“from 3.1 to 6.11”* and that this *“was the entire reason `PhaseState.uploads` had no writer”*. **(b) THE WRITE REPLACES INSTEAD OF MERGING** — `routes.py:661-665` builds `clean` from THIS TURN's extraction and assigns `case.phases[phase].structured = clean`. Any turn that captures a field wipes every field captured before it. **OBSERVED 2026-09-15 on the benign branch**: the turn captured one field whose value was falsy, `clean` came out empty, `if clean` skipped the write, and the two creation-form fields survived — had the capture carried a real value they would have been destroyed. **THE LOG AND THE WRITE DISAGREE AND NOTHING RECONCILES THEM**: `nodes_common.py:1269` logs `len(captured)`, which counts KEYS, while the filter drops on VALUES — so *“captured 1 field(s) -> artifacts”* and *“nothing reached the gate document”* are both true of the same turn. **NOT step 6.20**, which owns `computation_results`, `phase_metrics` and `field_index`; this is the capture path 6.2 built and S-F04 B4 ratified. **A Belt fills 26 fields across many turns and this makes accumulation impossible, so §33's gate is unreachable** | §6, §7, §20, §39.1, S-C02, S-F04 | **unscheduled** |
| ~~**G-79**~~ | **CLOSED 2026-09-25.** At step 10.0 a page reload redraws every past turn from `conversation_history`, the four blocks included; the follow-up fix redraws the DIAGRAM too — `selectTab('chat')` calls `renderLiveViz()` after the re-appended turns (a tab switch and a reload both land there), and `lastVizSource()` reads the visual stored on the turn when `S.lastAsk` is gone. Found by the founder's manual check on IMPR-2026-8D4. **Not closed by it — WHICH visual shows:** `detectCurrentWorkProduct` routes on v1 field names, so in Define it always answers 'problem' and the 5W2H mindmap shows on every step; the UI's v2 names are 10.3's. **A RENDERED VISUAL IS PERSISTED AND NEVER RENDERED FROM STORAGE.** The 5W2H mindmap IS stored: `visualisation` is in `conversation.py`'s `V1_PRESENTATION_KEYS`, copied onto the turn by `message_to_turn`, and NOT in `_TRANSPORT_KEYS`, so `strip_transport` leaves it on the persisted turn in `case.conversation_history`. **The UI never reads it back.** `S.lastAsk` is assigned in exactly ONE place — `ui/index.html:6069`, inside `sendMessage` — and is never rebuilt from `conversation_history`; `renderLiveViz()` is called from exactly ONE place, `ui/index.html:6091`, also inside `sendMessage`. `selectTab('chat')` calls `renderChat()`, which rebuilds the chat DOM and destroys `#viz-live`, re-appends `S.localChat` **and never calls `renderLiveViz()`**. So the diagram survives the server and dies on a tab switch. **COUPLED TO G-78, and the coupling matters**: `renderLiveViz` branches on `detectCurrentWorkProduct(getStructured())`, and while G-78 stands no coached field reaches `structured` — so even a correct re-render call routes off the two creation-form fields and would draw the WRONG visual. **Fixing the render call alone is not sufficient** | §50, §50.1, §49, `ui/index.html` | closed |
| **G-80** | **A GENERATED ARTEFACT IS CHECKED AT ITS INPUTS AND NEVER AT ITS OUTPUT.** `docs/board.html` is produced by `build_board.py` and every check around it reads the DOCUMENTS it is generated from — Appendix D, the markers, §66, git log. **Nothing read the rendered file.** So the board shipped visibly broken for two commits while `build_board.py` exited 0 and printed *“72 steps, 69 markers”*, `verify_built.py` reported 26 checks with zero disagreements, and `pytest` was green — found only when the founder opened it (the unescaped `data-b` attribute, fixed 2026-09-15). **DISTINCT FROM G-71, AND THE TEST IS WHETHER ONE FIX CLOSES BOTH — IT DOES NOT.** G-71 is *no owner*: `ui/index.html` has no step, no `Touches` and no anchor, and its fix is to give the UI steps, which 10.0 begins. **This artefact HAS an owner** — step 6.16 built the generator, Appendix F anchors it at `repo:.claude/hooks/build_board.py`, and guard rule 2b watches the file. Its defect is that **the owner verifies the wrong thing**: inputs, not output. Giving the UI a step would not add an output check here, and adding one here would not give the UI a step. **A gap whose fix closes half of it is two gaps.** **PARTIALLY MITIGATED, and the limit is stated rather than claimed as closure**: `test_no_board_attribute_carries_unescaped_markup` now reads the rendered file — for ONE failure class, malformed attributes. A board that renders cleanly and says something FALSE still passes everything. §55.2's *“a marker nothing re-runs is a claim”* applied to the artefact rather than to the marker | §55.1, §55.2, Appendix D, Appendix F, `build_board.py` | **unscheduled** |
| **G-81** | **A FIX THAT REMOVES A WASTEFUL PATH CAN DELETE THE ONLY COVERAGE ANOTHER STEP WAS RELYING ON, AND NOTHING NOTICES.** Before G-63 was fixed, the Define turn issued **three redundant `rag_lookup_evidence` calls** because the routed read had loaded nothing and the coach searched to compensate. **Those wasteful searches were the only thing exercising the evidence index end to end**, and step 6.13's live half depended on that path being walked. The fix removed the waste — the 2026-09-15 run spent **0 of 5 hops** — and **deleted 6.13's coverage with it**. So the same fact, *0/5 hops*, is simultaneously the proof that 6.21 worked and the proof that 6.13 was not exercised. **THE COVERAGE WAS ACCIDENTAL AND NOBODY KNEW IT EXISTED**, which is why its removal was invisible: it was not a test, it was a side effect of a defect, and no step recorded a dependency on it. **THIS WILL RECUR.** Every efficiency fix in a retrieval-driven system removes calls, and any verification that was riding on those calls goes with them — silently, because the suite stays green and the step that lost its coverage is not the step being changed. **The general rule this registers: a fix that REMOVES calls must name what was depending on those calls, and a `live-run` debt that was being satisfied incidentally is not satisfied at all.** Registered 2026-09-15 from the first live turn after G-63 | §24, §26, §55.1, G-63 | **unscheduled** |
| **G-82** | **AN ARTEFACT IS REACHABLE ONLY AS A 160-CHARACTER SUMMARY, AND NO TOOL CAN READ ONE.** Observed on rid `ca6ba417-3319-433d-8bfb-9240252dfc0a`: `to_be_process_map.txt` classified **artefact** (`auto_detect_purpose` → *Process map* → `ARTEFACT_PURPOSES`, derived not declared), so by ruling 3 it was **captured and not indexed**. **THE ROUTE IS NOT BROKEN AND THAT IS THE POINT** — traced end to end: `routes.py:1041` persists `summary`, `models.py:149` carries it through `to_phase_state_entry`, `mappers_common.py:137-138` builds the entries, the mapper seeds `uploads` (6.11), and `state_injection.py:298` puts it in the prompt. **The coach HAD the artefact and searched anyway**, three times. **WHY IT COULD NOT USE IT:** the manifest truncates at **`summary[:160]`**, and its only usage instruction is *“To use any of these numbers, call `load_evidence_series` with the blob_path above”* — **numbers**, via a tool that returns n/mean/sigma from a numeric column. A to-be process map has no numeric column, so `first_numeric_column` returns `None` and G-63's fix correctly declines to dispatch. `UNIVERSAL_TOOLS` is six and **not one of them reads an artefact's text**. So the coach holds a 160-char fragment, is told the only way to open it is a numeric reader, and falls back to `rag_lookup_evidence` — the one index artefacts are guaranteed absent from. **A file the Belt uploaded, correctly classified and correctly stored, that the coach can see and cannot read** | §24, §29.1, §29.2, S-F57, G-63 | **unscheduled** |
| ~~**G-83**~~ | **CLOSED 2026-09-18 at step 6.35** — the cap is now **3**, which fits the node budget at the measured per-hop cost, and `test_hop_cap.py` asserts the arithmetic so the constant is falsifiable. **Per-hop cost is deferred to step 9.0**, when recall can first be measured. Original finding: **THE FIVE-HOP CAP HAD NEVER BEEN REACHABLE. THE 45s TIMEOUT BINDS AT THREE, AND THE TWO LIMITS DISAGREE.** `COACH_HOP_BUDGET = 5` (`nodes_common.py:590`) against `EXECUTOR_RUN_TIMEOUT = 45` (`subgraph_common.py:73`). **Each hop is not one search.** §25's multi-query fusion makes it **one MODEL CALL to generate variants** (`fusion.py:~236`, `await … ainvoke`) **plus six searches plus RRF** — the log reads *“Generated 5 query variant(s)”* then *“6 quer(ies) -> 2 unique doc(s)”*. **Measured: ~9.5s per hop on G-63's trace (2026-09-14), and on `ca6ba417` three hops plus the coach's own calls reached 52.219s against a 45s wall.** At 9.5s four hops consume 38s and leave too little to compose; at the observed rate three is the ceiling. **SO THE BUDGET'S 5 IS DEAD CONFIGURATION** — the turn dies at 3 and `_HOP_BUDGET_SPENT` is unreachable code. **AND IT WAS DEAD THE DAY IT WAS WRITTEN**: fusion landed at step **5.2** (Seq 160) and the cap at step **6.7** (Seq 250), so the cap was built on top of a per-hop cost that already made it unreachable. **This bears on 6.7 and 6.13.** 6.7's live half asks that the opening turns *coach rather than cap* — a condition **trivially true, because capping is impossible**, which makes the clause unfalsifiable rather than satisfied. And 6.13's index path now costs ~9.5s a query against a wall that allows three | §25, §26, §3.7, §44, S-F09 | closed |
| ~~**G-84**~~ | **CLOSED 2026-09-17 at step 6.34.** The node now budgets its own model loop at `EXECUTOR_SOFT_BUDGET = 40.0`, below the engine's 45s wall, catches `asyncio.TimeoutError` inside its own body and returns a 200 with a partial answer; `partial_timeout` is written to `step_log` and reaches the parent as a `history` key. The wall was NOT raised — **G-83's cap contradiction stays open**. Original finding: **AN EXECUTOR TIMEOUT WAS A 500 TO THE BELT, AGAINST §4.8'S *NEVER A HARD FAILURE*.** On rid `ca6ba417` the Belt asked a coaching question and received **`POST /ask HTTP/1.1” 500 Internal Server Error`** with *“Node 'executor' exceeded its run timeout of 45.000s”*. **OCCURRENCE:** the timeout is enforced by `TimeoutPolicy(run_timeout=…)` at `subgraph_common.py:129`, which fires from the ENGINE and cancels the node **from above its own body** — so none of the node's graceful paths run. Those paths exist and are thorough: `except GraphRecursionError` at `nodes_common.py:1202` turns a runaway loop into a partial answer, the hop cap yields `_CAP_MESSAGE`, and the `remaining_steps` floor off-ramps into a composed answer with no retrieval. **Every failure the node can SEE is degraded; the one enforced above it is not.** It propagates to `routes.py`'s bare `except Exception` and becomes `HTTPException(500, f"Graph error: {e}")`. **NO path degrades it** — `grep` for timeout handling across `backend/` returns the policy line and nothing else. **ESCAPE:** the same file that promises *“a Belt mid-session never sees a stack trace”* (`nodes_common.py:1204`) adds the policy that guarantees they will, ~1,000 lines away, and **no test exercises a node that times out** — tests run fast, so the one failure mode that needs wall-clock to reproduce is the one the suite cannot reach. Compounded by **G-70**: what the Belt then sees is a three-second toast carrying the raw exception string | §4.8, §44, §45, §48, §50 | closed |
| **G-85** | **NOTHING DETECTS A RETRIEVAL HOP THAT RETURNED NOTHING NEW.** On rid `ca6ba417`, `rag_lookup_evidence` ran **three times** and each run logged *“6 quer(ies) -> 2 unique doc(s), returning 2”* — **eighteen searches, the same two documents, three rounds**, ~9.5s a round, and the turn then died on the wall. **`PhaseState.hop_results` is the field for exactly this and it is inert**: declared at `substate.py:371`, listed in `PHASE_STATE_CONTENT_FIELDS` at `substate.py:420`, initialised to `[]` at `mappers_common.py:272` — and **written by no node and read by no node**. So no hop can compare itself with the one before it, and a coach that searches the same corpus with rephrased queries pays full price each time for a result it already holds. **The hop budget counts CALLS, not PROGRESS** — it would stop a sixth identical search and cannot stop a second. **The escape is G-77's shape**: `hop_results` is declared, so F-15 should see it; it is unpaired in BOTH directions and is carried as a known exemption for step 6.10, which means the one signal that would have caught this is booked as somebody else's future work | §24, §25, §26, S-C02, F-15 | **unscheduled** |
| **G-86** | **APPENDIX F'S `State` COLUMN IS DOCUMENTED AS DERIVED AND IS IN FACT HAND-MAINTAINED, WITH NOTHING CHECKING IT.** Appendix F's header states *“`State` is DERIVED, not typed — ⛔ from Appendix D's status cell, then ✅ if git carries the step's spine subject, else ☐”*. **Nothing derives it.** The emitter that seeded the column at 6.31 was a one-off, and `verify_built.py`'s two matrix checks validate the `Evidence` anchor and the step-set — **neither reads the `State` glyph**. **Found 2026-09-17 on the matrix's OWN row**: 6.31 landed as `663a378` on 2026-09-15 and its cell still read `☐ not built` two days later, while the board — which DOES derive from git log — showed it DONE. **So the artefact built to stop a document disagreeing with the tree was itself disagreeing with the tree, in the column that says it cannot.** Corrected by hand at 6.34, which is the defect repeating rather than the fix. **THE CHECK IS CHEAP AND IS DELIBERATELY NOT BUILT HERE**: `matrix_states_agree_with_git` is the same shape as `matrix_covers_appendix_d` and belongs with a ruling on what to do about ⚠️, **the one state a human legitimately sets** and which git cannot derive — so a naive derivation would overwrite the judgement calls the column exists to carry | §55.1, §55.2, Appendix D, Appendix F | **unscheduled** |
| **G-62** | **A COMMIT BODY MAY ASSERT A CODE FACT WITH NOTHING TO RESOLVE IT AGAINST.** **FOUNDER RULING 2026-09-14, overriding §56.3's *ruled to stay untested*.** The accepted reasoning stands — a gate cannot judge whether a prose claim is TRUE — **but it can gate the SHAPE**: a commit body asserting a fact about code carries a git-resolvable reference, a path with a line range or a commit sha. **It never judges correctness.** Worked case in the register: **v1.31(C)** asserted *“Rule 2b blocked the commit adding rule 6 … a watched path staged without this file is exactly what 2b exists to stop”* — a claim about what the guard did, carrying no reference, **and wrong**: that was the board being regenerated, the first false trigger, read as the rule working. It stood six weeks and cost `ef59aa8`. A `path:line` beside it would not have made it true, but it would have made it checkable. **KNOWN LIMIT, recorded with the ruling: it does not catch a citation that RESOLVES AND IS WRONG.** §55.2 cited `build_board.py`'s four inputs accurately and drew a false conclusion from them; a shape gate passes that unchanged. **Step 6.30** | §56.3, §20.5.1, §55.2 | **6.30** |
| **G-61** | **FOUR DISMISSED HAZARDS REST ON ARGUMENT ALONE, AND NOTHING RE-RUNS THE ARGUMENT.** The §55.2 shape: a risk named in prose and cleared in prose. The full-structure audit found 52 dismissal-shaped statements; most are prose, §55.2's own is tested, and two naming `DMAICGateValidator` are forward-noted onto step 7.1. These four carry no owner: **(a)** §23.3 *“Safe by construction — each tool addresses its own index”*, the `embedding` / `content_vector` asymmetry — **step 9.1**, which applies the rename and either dissolves the claim or leaves a test binding each tool to its vector field name. **(b)** §23.2 *“it can only change at a rebuild … and cannot drift silently”* — **step 9.1**, same reindex. **(c)** §15 *“Why that is safe, rather than a simplification that ignores gate failure”* — the supervisor has no conditional edge because a subgraph reaches `END` only through `gate_apply`, which runs only after Belt approval. Testable as a graph property: assert `END`'s only predecessor is `gate_apply`. **Step 7.3**, which builds the approval path the claim depends on. **(d)** §56.3 *“a claim resolves through git, or is not made”* — **RULED: STAYS UNTESTED, NO STEP.** A gate reads the index and cannot read a sentence; §0.32 clause one is stated as ungateable in the rule itself, and §20.5.1 already carries the discipline that catches it. Recording it as owned by a step would claim coverage that cannot exist. **§19.6 WAS ON THIS LIST AND IS WITHDRAWN** — its *“every turn, by construction”* sits inside a record of three defects fixed on 2026-08-22 and describes the OLD behaviour, not a live safety claim. The audit misread a diagnosis as a dismissal | §55.2, §23.2, §23.3, §15, §56.3 | **7.3**, **9.1** |
| ~~**G-58**~~ | **THE WATCHED-PATH CONTRACT HAD TWO OWNERS. CLOSED 2026-09-14 at step 6.27.** §55.2 tabulated the paths that oblige an `ARCHITECTURE.md` re-check and `commit-msg-refactor-guard.py` hardcoded the same set as `STATUS_WATCHED` — one fact, two copies, against CLAUDE.md's *Facts have one owner* rule. **It drifted twice, in opposite directions**: the board was added to both on 2026-09-11 and removed from only the guard on 2026-09-14, so between `258d0dd` and this step the document said thirteen paths and the gate enforced twelve — **the second drift was created by the commit that fixed the first**, which is the shape the ownership rule exists to stop. Closed by an EQUALITY TEST rather than a runtime read: parsing a prose section inside the hook would put a document on the critical path of every commit and fail closed on a reformat, and §55.2's block is authored for a reader, not a data file. Both mutation directions proven — a path added to §55.2 fails the test, a path added to `STATUS_WATCHED` fails the test | §55.2, §55.4, §56.3 | closed |
| ~~**G-57**~~ | **CLOSED 2026-09-13 at step 6.26.** `backend/tests/test_commit_guard_tree_rules.py` — 41 tests — pins what rules 7 and 8 RANGE OVER and not only what they match: the ratchet (`--diff-filter=AR`, so a modification is invisible to both), the rename into a scratch name, the index-versus-disk read of both registers, and that a declared number must resolve. **Two of its assertions go red on a REFORMAT rather than on a rule change** — Appendix D and §66 parsing into more than fifty entries each, with a struck-through `~~**G-52**~~` row asserted to still parse, because a closed gap is still a number that resolves. **The mutations are recorded with their results**: emptying `SCRATCH_SEGMENTS` gives 8 failed / 33 passed; pointing the Appendix D regex at `**Step X.Y**`, a shape the table does not use, gives 1 failed / 40 passed; dropping the filter from `AR` to `A` gives 1 failed / 40 passed. **What it deliberately does not pin is whether a file belongs to the step it declares** — rule 8 checks a number is declared and exists, and stating that limit in the test file is what stops a green suite being read as evidence the numbers are honest | §0.32, §56.3, §55.1 | closed |
| **G-56** | **NO DRIFT CHECK CAN SEE THE GOVERNING DOCUMENTS.** `deprecated_patterns.yaml` excludes `agent-improve/*.md` and `agent-improve/**/*.md`, so CLAUDE.md, ARCHITECTURE.md and everything under `docs/` are outside every pattern the drift hook enforces. **The exclusion is correct as written and that is the problem**: architecture markdown deliberately shows a superseded form beside its replacement, so a registry guarding CODE must not match it — which leaves the documents guarded by nothing. Every defect worked between 2026-09-12 and 2026-09-13 was in a document. The countermeasure is a hook that reads OWNERSHIP rather than patterns — `fact-ownership-guard.py` denying a write that restates an owned fact, which needs no pattern list and so needs no exclusion. **Step 6.24.** Was the live half of CLAUDE.md §18.1; its other half — `pattern-2`'s §4.6 scoping — **was closed at step 5.2 on 2026-09-03 and the document never said so**, which is why it read as owed for ten days. | §55, §55.1, §56 | **6.24** |
| ~~**G-42**~~ | **RESOLVED 2026-08-24** — the mapper runs inside the parent's uniquely-named node function for that phase, which is the documented LangGraph pattern for parent and subgraph with different state schemas. See §66.6, S-F10 and DECISIONS §T1. *Original statement:* **the boundary mappers have no execution site.** §9 defines them as "two plain functions per phase"; §13 states a phase subgraph contains **exactly five nodes**, none of which is a mapper, and forbids a sixth without a §56 amendment; §12 embeds each subgraph as a node of the parent. Whether a mapper runs inside the subgraph, inside the parent's node wrapper, or somewhere else is stated nowhere — and every phase boundary depends on it | S-F10, S-F11, S-F12 | closed |
| **G-88** | **AN ASK NEVER SURVIVES THE TURN THAT CREATED IT, FOR TWO INDEPENDENT REASONS, AND NEITHER IS FIXED HERE.** **(a) THE MIRROR READS A KEY THAT IS NOT ON THE SCHEMA IT READS FROM.** `gateway/routes.py::_mirror_asks` does `(result or {}).get("asks")`, where `result` is the return of `graph.ainvoke` on the **PARENT** graph — and `SupervisorState` is seven fields (§5), none of them `asks`. The parent's phase node returns `messages` and `history` and nothing else, so the child's `asks` reach no caller. The lookup yields `None`, the function returns at its own guard, and **`write_asks` has never once been called.** This is the `route_after_phase` class this group is named for: specified code reading state a schema does not declare. **(b) AND THE RECORD IS WHOLESALE-REPLACED EACH TURN REGARDLESS.** `_ensure_case_record` runs at the top of every `/ask` and calls `write_case_record(store, id, case_record_from_document(case))`, which `store.put`s a record built from the case blob alone — framing, uploads, and since step 6.33 the captured values and the field log. `asks_by_phase` is **written by `write_asks` and rebuilt by nothing**, so even a mirror that ran would be erased before the next turn's input mapper read it. **The two stack**: fixing (a) alone leaves the write destroyed one turn later, and fixing (b) alone leaves nothing to preserve. **NEITHER IS FIXED.** Found 2026-09-21 while step 6.33 chose a home for `field_log` — the choice turned on this exact question, and `PhaseRecord.field_log` was taken partly because the Store record is not safe to write mid-turn until (b) is fixed. **Does not block Define**, which declares zero ask shapes (ruling AR-R2), so no Define turn can create an ask to lose. **Scheduled for stage three with 6.12's re-homed `live-run`.** | S-C02, S-F10, §6, §9, §10.2 | **stage 3** |
| **G-89** | **`field_log.reason` IS DECLARED AND NOTHING WILL EVER POPULATE IT — THE DECLARED-AND-NEVER-POPULATED CLASS, CAUGHT AT BIRTH THIS TIME.** Step 6.33's ratified entry shape carries *"the Belt's stated reason where given"*, read from a `reason` key on the capture entry — which `CoachingResponse.fields_captured` PERMITS, its entries being free-form dicts, and which **nothing asks the coach to supply**: S-C05's field description names `field_name`, `value` and `source`, and no more. **Both entries from the 2026-09-21 `live-run` carry `None`**, and the Belt's second message stated a reason in prose — *"the earlier figure left out the late-payment penalties"* — which reached the coaching text and not the log. **This is `computation_results` and `phase_metrics`' class** (read by five gate assemblers, written by nothing) and `field_index`' class (set to `0`, advanced by nothing) — a field that lands in a schema and not in the path that fills it. **What is different is that it is registered on the day it was built rather than found months later**, which is the whole of §55.2's argument. **The fix is one clause on `CoachingResponse`** — add `reason` to the `fields_captured` description so the coach is asked — **and it is a §56 amendment to S-C05, deliberately NOT made in commit 6.33.** **OWNER: the procedure amendment now being drafted**, which carries it with 6.42 and §39.1.9. Until then the column is honestly empty: a column that exists and is empty says *"nobody was asked"*, where a column that does not exist says nothing at all and the next reader rediscovers why. | S-C05, S-C02, §6, §20 | **the procedure amendment** |
| **G-90** | **THE VERIFICATION TOOLING PARSES AN ERROR BODY AS DATA, SO A FAILED READ IS INDISTINGUISHABLE FROM AN EMPTY RESULT — G-66'S SHAPE, ONE LAYER UP.** During step 6.33's `live-run` a read of the case document was issued against `/case/{id}`; the served route is `/cases/{id}`, so the response was a **404** carrying `{"detail":"Not Found"}`. The reader did `json.load(...)` and walked `(c.get("phases") or {}).get("define")` — **a valid JSON object with no `phases` key, so the walk yielded `{}` and the check reported `structured: null`.** That is byte-identical to what a case which had genuinely captured nothing would report, and it was believed until `-w "%{http_code}"` was added. A **400** was read the same way one turn later, reporting `phase_inputs: null` for a turn that never ran at all. **This is G-66 exactly** — *"a 503 `{"detail": …}` is a valid JSON OBJECT, so `data.length` is `undefined`, falsy, and the empty-state message renders"* — with the verifier in the UI's place, and it is the more dangerous seat of the two: **the UI misleads a Belt, and this misleads a step's own evidence.** G-66 was fixed in `ui/index.html` on 2026-09-15; **nothing generalised it**, because the tooling side is ad-hoc `curl` in step prose rather than a file anybody owns. **NOT FIXED.** Interim containment, with its removal condition: **every live read written into this document from 2026-09-21 checks the status before it reads the body** — 6.33's own section carries that instruction, and it retires when a checked reader exists that a step can call instead of writing its own. | §49, §55.1, G-66 | **unscheduled** |
| ~~**G-91**~~ | **THE PLAN AND ITS GENERATOR LIVED OUTSIDE THE REPOSITORY. CLOSED 2026-09-23** by the commit carrying `Gap: G-91`: the generator is tracked under `agent-improve/tools/control_board/`, runs in `.githooks/pre-commit` after `build_board.py`, derives rows proven, story and task status and NEXT from Appendix H, git log and rank, and fails VISIBLY — a warning from the hook, and a BUILT FROM line on the page that goes stale when a build fails. **Still open, and not this gap:** Appendix F's `Order` is hand-set (Appendix I says so). As registered: The epics, stories and rank (`stories.py`) and the generator that renders the control board from them were kept in the Desktop session's workspace. **Appendix I names `stories.py` as the plan's single source** (founder ruling, 2026-09-23), and at that moment the pointer did not resolve: `git ls-files` returned nothing for it, tracked or untracked. So the plan could drift from Appendix H and from git log with nothing to notice. The control board's rows-proven count, its story and task statuses and its NEXT were all TYPED, and they stayed right only while somebody remembered to retype them. **Registered first, in its own commit, because §0.32's guard refused the generator's files for want of a number that schedules them** — which was accurate, since nothing did. **Closes when** the generator is tracked under `agent-improve/tools/control_board/`, runs in the pre-commit hook, and derives from Appendix H and git log what it used to declare | §0.32, §55.1, Appendix H, Appendix I | closed |
| ~~**G-92**~~ | **CLOSED 2026-09-24 at step 6.52.** The budget is measured from node entry and no lookup holds the event loop: the real executor node, under the real `TimeoutPolicy` with a setup delay and a blocking tool, answers before the wall (`test_turn_budget.py`), and live turn `01a0d2c0…` returned 200 where two had returned 500. **Not closed by it:** open questions still end in the degraded answer — a latency problem, G-83. As registered: **G-84'S GUARANTEE DOES NOT HOLD: THE SOFT BUDGET NEVER ENDS A TURN BEFORE THE ENGINE'S WALL.** G-84 closed at 6.34 on the claim that the node budgets its own model loop at `EXECUTOR_SOFT_BUDGET = 40.0`, below the 45 s wall, so the engine's `TimeoutPolicy` is only a backstop. **On 2026-09-24 both live turns on `IMPR-2026-0E5` hit the wall with a 500** — traces `01a0d215-a216-75e2-ba80-1c80597f891f` and `01a0d28e-d4da-7901-a75e-44d86b102098`. Two causes, found in 6.52 Part A: **(1)** the budget's clock started at `agent.ainvoke`, ~5 s after node entry, so its deadline fell after the wall's; **(2)** the three `rag_lookup_*` tools ran synchronous `embed_query` + `search` on the event loop, four to six in a row, so no timer could fire until each returned. **Escape:** 6.34's proof re-implemented `wait_for` inside the test around an agent that awaited a millisecond sleep — never the real node, never the real wall, never a blocking tool | §4.8, §44, §45, G-84 | closed |
| ~~**G-93**~~ | **CLOSED 2026-09-24 at step 6.54.** Every client a turn uses is built at startup, once; on a restarted server the FIRST turn — an open question with two parallel lookups — was coached in 24.1 s of executor time, zero client builds in its trace (`01a0d366-bf6e-7020-9d5f-1bb5a972bcdf`, first turn in process: yes). As registered: **OPEN QUESTIONS DO NOT FIT THE BUDGET — CAUSE: COLD START.** Since 6.52 a turn never 500s, but an open question that makes two or more knowledge lookups ended in the degraded *"I ran out of time"* answer (row 2 red). **Cause, measured at step 8.0's executor slice: the clients are built lazily inside the first turn, and 6 threads build the same client at once** — the cached `get_embeddings` (~5 s) and knowledge search client (~10.6 s) were each built SIX times in parallel on one cache miss, and first-time `get_llm` builds cost 2–3 s each. Not throttling (54 HTTP attempts, zero 429s, zero retries) and not serialised embeddings (six queries start within 0.02 s). **Traces:** `01a0d357-f9fc-7123-be14-fb5bc4229bb1` — COLD, first turn in process: executor 40.1 s, degraded. `01a0d358-c1ef-7aa0-9c81-6370593dff71` and `01a0d359-3a3d-7db0-a970-eaf830885902` — WARM: executor 23.6 s and 21.6 s, coached 200s. Every degraded live turn before this was a first turn in a fresh process | §44, §45, §51, G-83 | closed |
| ~~**G-95**~~ | **CLOSED 2026-09-24 in the commit that registers it.** **THE TEST SUITE AND THE NEW SPANS EXHAUSTED LANGSMITH'S MONTHLY TRACE QUOTA — EVERY TRACE IS NOW REFUSED.** From 2026-09-24 ~13:10 UTC LangSmith answered every ingest with **429 `"Monthly unique traces usage limit exceeded"`**, real Belt turns included. Root traces: **19 on 09-23, 4,897 on 09-24** — 827 test graph runs and **~4,070 standalone spans** (`dispatch_routed_read` 610, `build_executor` 598, `fusion.search_query` 360, `calculate_cpk` 162, `get_llm` 156 …), the first at 12:06. **Two causes:** (1) `init_tracing()` sets `LANGCHAIN_TRACING_V2=true` for the WHOLE process, so since 6.49's row checks started the app inside pytest, every later test traced; (2) step 8.0's executor slice (`a2067db`) put `@traceable` spans on functions that also run with no turn around them — unit tests and 6.54's startup warm-up — and a span with no enclosing run is a ROOT trace. **Fixed in the commit carrying this row:** tests never trace (a session fixture, and a `pytest_sessionfinish` guard that fails the suite if any run is created — counted at the client, nothing sent); spans are `child_span` / `child_trace`, recording only inside an already-traced run (`get_current_run_tree()`, https://docs.langchain.com/langsmith/access-current-span). **Row 35 stays green in the register but is UNPROVEN** until one live turn is traced again (quota reset or a paid plan — founder). **For 6.50:** `init_tracing` sets the legacy `LANGCHAIN_TRACING_V2`; the documented name is `LANGSMITH_TRACING` (https://docs.langchain.com/langsmith/annotate-code), and the installed SDK reads `*_TRACING_V2` FIRST | §51, 6.49, 8.0 | closed |
| ~~**G-96**~~ | **CLOSED 2026-09-24 (founder ruling, Option A; ARCHITECTURE.md v1.72).** **LAYER 2A REJECTS THE COACHING SCRIPT'S OWN CONFIRM STEP AS "PARROTING", AND NOTHING RECORDS THAT THE TURN WAS DEGRADED.** 2026-09-24 13:14, 0E5 (first turn in process: no; trace refused, G-95): the Belt gave its business case; the coach reflected it back — the script's ④ **Confirm** — and coherence answered *"The coach's response is parroting the Belt's own words back, which is a failure"*, degraded the turn and stood the grader down (S-C13 B3). The turn has no grade and no record of why, so row 13 is red on it. §19.7's "is it parroting" and §43's Confirm ask opposite things of the same reply. **A second cause, found while fixing it:** the judge read `CoachingResponse.message` only, and the 13:14 reply's confirmation question was in `prompt`. **Fixed:** the judge is told the script step the reply performs (④ Confirm for a captured field, with the field's SKILL.md block), reads the whole reply, and is given the ruling's definition — parroting is a restatement with no confirmation question and nothing added; every verdict is recorded in `step_log` (node `coherence`). **Real judge, the 13:14 reply, ten runs each:** with the step 10/10 coherent; step removed 0/10; a true parrot at the same step 10/10 rejected. **Live:** the same Belt message on 0E5, trace `01a0d3e5-6246-7de3-b768-2ee767a5130c` (first turn in process: yes) — coherent, `script_step` position 1 `business_case` confirm, graded; row 13 green | §19.7, §43, S-C13 | closed |
| **G-94** | **OPEN QUESTIONS SEARCH AN EMPTY CASE INDEX.** `improve_case_index` holds **0 documents** (read 2026-09-24), yet `rag_lookup_case_history` is bound on every Define turn and the coach calls it on almost every open question: trace `01a0d366…` (first turn in process: yes) — 6 queries, 0 hits each, *"No similar improvement cases found"*. A whole lookup (~3–5 s warm, the variant model call included) spent on a search that cannot return anything. The G-85 class: a mechanism wired to an empty source. **Proposed: step 6.55** — not built: stop offering the lookup while the index is empty (or say so to the coach), and give the index a writer, a sample case and tests (brief item 9) | §23, §29.2, G-85 | **proposed 6.55** |
| **G-97** | **ONE EVIDENCE FILE IS IN THE INDEX TWICE.** `improve_evidence_index` holds 2 documents for 0E5, both `kind=evidence`: the same `define_baseline_weekly.csv` uploaded 22 s apart (2026-09-15 17:10:40 and 17:11:02), the SAME content digest (`bb4e2a7b34…`). The case record points at one; the other is an orphan a search can still return | §23.2, §29.1 | **decide at 6.43 Part A** |
| **G-98** | **THE EVIDENCE UPLOAD'S INTERPRETATION IS UNAVAILABLE.** Both evidence documents for 0E5 carry *"[!] INTERPRETATION UNAVAILABLE"* as their description: the upload's interpretation step did not produce one, and the index holds that placeholder where a summary should be | §29.1 | **decide at 6.43 Part A** |
| **G-99** | **LAYER 2a REJECTS A STOCK-TAKING SUMMARY AS "PARROTING" AT THE TEACHING STEP.** 2026-09-24 15:05, 0E5, trace `01a0d3f3-6f67-7100-b04d-214e7fe1f720` (first turn in process: yes): the Belt asked where the charter stands; the coach summarised the charter — values the Belt gave on EARLIER turns — and named what to push on. Coherence (with G-96's step context: position 5, `metric_definitions`, explain/show/ask — the planner's focus) answered *"primarily a restatement of the Belt's words … constitutes parroting"*, degraded the turn and stood the grader down. **G-96's record worked** — the reason is in `step_log` — but row 13 is red on any such turn. The ruling's definition (a restatement with no confirmation question and nothing added) arguably fits a summary; whether a stock-take is a step of its own is a founder question | §19.7, §43.3, S-C13 | **unscheduled — founder** |
| **G-100** | **`calculate_expected_savings` READS "23%" AS 23 AND RETURNS A SAVING 100× TOO LARGE.** Dry runs of the 6.56 driver, 2026-09-25 (untraced): baseline 23%, target 5%, £9 per late invoice, 42,000 invoices a year — both runs recorded **£6,804,000**; the right figure is 18% × 42,000 × £9 = **£68,040**. The coach passed `"23"`/`"5"` (IMPR-2026-206) and `"23%"`/`"5%"` (IMPR-2026-134). **D0, the tool called directly, no model:** `"23%"`/`"5%"` → 6804000; `"23"`/`"5"` → 6804000; `"0.23"`/`"0.05"` → 68040. **The layer is the TOOL:** `_num` (`knowledge/computation.py`) drops a `%` without rescaling, by design — *"a bare `%` does not change the value, because whether the Belt is working in percent or in fractions is their unit choice and the tool must not silently rescale it"* — and then multiplies a percentage-point gap by a unit count, which is a guess about units that §60.6 B3 forbids: *"unable to parse its input — return a clear reformatting request to the Belt rather than raising or guessing"*. §69.1 binds all twenty: *"each tool parses what it needs at the point of use and — per §60.6 B3 — returns a clear reformatting request rather than raising or guessing when it cannot"*. §69.2 S-F37 states the inputs and *"states the multiplication used"* but no percent convention, so the gap is in the SPEC as well as the code. **Secondary:** the coach passed bare numbers on one run (the % already gone), and relayed £6.8M for a £62,000-a-year problem without comment — and ran it without teaching the concept first (§43.1 step 1; row 26). **Also seen:** every `computation_results` row carries `"turn": 0` | §69.1, §69.2 S-F37, §60.6 B3, §43.1 | **proposed: step 6.58 — a percent convention for the computation tools (§69.1 amendment, `_num`, S-F37), founder** |
| **G-101** | **`init_tracing()` IGNORES `LANGSMITH_TRACING=false` — AN OPERATOR CANNOT START THE APP UNTRACED.** `core/tracing.py:44` reads only whether a key exists (`api_key = (settings.LANGCHAIN_API_KEY or "").strip()`); with one, `:61` sets `os.environ["LANGCHAIN_TRACING_V2"] = "true"` for the whole process, and `app.py:74` calls it at startup. No tracing switch the operator sets — `LANGSMITH_TRACING`, `LANGCHAIN_TRACING_V2`, `LANGSMITH_TRACING_V2` — is read first, so `LANGSMITH_TRACING=false uvicorn …` still traces every turn. **Found 2026-09-25 building the 6.56 driver** (read in the code, not by a traced run — no trace was spent proving it): the driver's dry runs had to run the app IN-PROCESS with `conftest._no_tracing`'s switch to be untraced. **Why it matters now:** tracing is on a capped budget (founder, 2026-09-24: $10/month) and the only way to run the server untraced is to remove the API key. G-95's row already flagged the legacy name for 6.50 (*"`init_tracing` sets the legacy `LANGCHAIN_TRACING_V2`; the documented name is `LANGSMITH_TRACING`"*); this is the other half — it OVERRIDES an explicit off | §51, G-95 | **unscheduled — founder** |
| **G-102** | **THE GRADER READS ONLY `message`.** `grader.py` `_coach_text` returns `CoachingResponse.message` alone, so the judge of the coach's process never sees `explanation`, `example` or `prompt`. Coherence audit, `IMPR-2026-AD5` (0 traces): turns 2 and 6 failed *"show a concrete example"* with an example in the `example` block | §19.8, S-C14 | **6.59** |
| ~~**G-103**~~ | **CLOSED 2026-09-25 at step 10.0.** `grader_warning` is read: the executor carries it on the reply message and the route projects it onto `AskResponse` (step 10.0). **`grader_warning` IS READ BY NOTHING.** `DMAICGraderMiddleware` returns `{"grader_warning": MAX_ITERATIONS_WARNING}` on a FAIL (`grader.py`); no route, node or UI reads the key — the *"Belt-visible warning"* of §19.8 is invisible | §19.8, §50.1 | closed |
| **G-104** | **THE COHERENCE PROMPT CLAIMS A RETRY THAT DOES NOT EXIST.** `_PROMPT` tells the judge *"the coach retries on that feedback"*; `coherence.py` checks once (`self.attempts = 1`) and `max_retries` is never used. Row 12 records the same absence | §19.7, S-C13 B2 | **6.53** |
| **G-105** | **THE PLANNER IS A TURN LATE ON WEAK ANSWERS.** Audit turn 3: the Belt answered *"A few people from finance will help out."* and the plan said `next_action: ask for it`; turn 4 — the full answer — was planned as *"challenge a weak answer"*. The coach did not challenge the weak answer (row 31) | §17, S-F13 | **6.45** |
| **G-106** | **THE COACH FETCHES THE SCRIPT IT ALREADY HAS.** Audit turn 1: a model call to `load_skill("dmaic-define-phase")` although v1.71 places that script in the system message on every call | §19.2, §32, S-C12 | **6.60 (proposed)** |

### 66.3 Group C — schemas named but never defined

| # | Gap | Attaches to | Step |
|---|---|---|---|
| **G-09** | `CoherenceResult` | S-C23, S-C13 | **unscheduled** |
| **G-10** | `ConstraintCheckResult`, plus the `ConstraintVerdict` / `ConstraintCheckResult` naming split between `CLAUDE.md` §2 and reference §21 | S-C24, S-F25 | **unscheduled** |
| **G-11** | `GraderVerdict` — only "carries a `list[CriterionVerdict]`" is stated | S-C21, S-F26 | **unscheduled** |
| **G-12** | `CoachingGraderVerdict` | S-C22, S-C14 | **unscheduled** |
| **G-13** | `PolicyAdvisoryResult`, and how a non-blocking advisory is surfaced without reading as a rejection of the Belt's correction | S-C25, S-F27 | **unscheduled** |
| ~~**G-14**~~ | ~~`QueryVariants`~~ **CLOSED 2026-09-03, procedure step 5.2.** **One field, `variants: list[str]`** — a `rationale` field was considered and rejected as generated every retrieval, read by nothing, and paid for in tokens on the hot path. **The original query is NOT among the variants and is always searched anyway**, as ranked list zero: the Belt's own phrasing is the highest-signal formulation and must not be at the mercy of a generation call, and putting it in the schema would let the model spend one of its slots restating what it was given. *Consequence:* the fan-out is `1 + len(variants)`, so **4–6 lists reach RRF, not 3–5**, and the original's list is one vote among them — deliberately not weighted higher, because RRF's premise is that agreement across phrasings is the signal. **Count model-chosen, bounded 3–5 by `min_length`/`max_length`**, so a violation is a parse failure at the boundary rather than a silent narrowing; §25 says "3–5", which is a range, and forcing exactly five produces padding, which produces near-duplicate lists that inflate one document's fused score without adding evidence. File: `knowledge/fusion.py` (S-C19 sanctions it or `tool_args.py`). Record: `docs/_archive/DECISIONS.md` Part AC | S-C19 | closed |
| **G-15** | `HITLInterrupt` — and whether an exception raised from `after_agent` yields a resumable graph-level interrupt at all. **ANSWERED 2026-09-07 (ruling AJ4), landed here 2026-09-10: it is DELIBERATELY NEVER DEFINED.** The nine-step HITL gate (step 7.3) pauses with LangGraph's own `interrupt()`, which is resumable by construction; an exception raised from `after_agent` is not, and defining one would create a second, non-resumable pause mechanism competing with the framework primitive §0.24 requires preferring. **The gap stays OPEN as a naming problem rather than a design one** — §19.6 and S-C15 still raise `HITLInterrupt(**flag)` in prose, and those call sites need rewriting to `interrupt()` at step 7.3 | S-C15, S-C10 | **unscheduled** |
| **G-16** | `CitationRecord` / `CitationBundle` — and the three different citation shapes stated in §50, §6 and §23 | S-C36 | **unscheduled** |
| **G-17** | `CaseDocument` · `PhaseRecord` · `RegistryEntry` · `PhaseSummaryRecord`, and whether `PhaseRecord` duplicates the gate document | S-C09 | **unscheduled** |
| **G-18** | All `gateway/schemas.py` envelopes, for all seven endpoints, plus the gate interrupt and resume payloads and the SSE event shape. **G-02 now depends on this** — the `/gate/reject` payload must carry a mandatory reason | S-C37, S-F06, S-F34, S-F13 | **unscheduled** |
| ~~**G-19**~~ | Per-phase `PhaseState` variants — the transient fields are never enumerated, and whether they count against §6's ceiling is undecided  **✅ CLOSED 2026-09-11 by ruling** — the five variants are not built and will not be; §39.x.7 describes per-phase USE of the shared 23-field `PhaseState` (S-C03). The fields were never enumerable because the classes were never designed. | S-C02, S-C03, §6, §39.x.7 | closed |

### 66.4 Group D — described in prose, no interface

| # | Gap | Attaches to | Step |
|---|---|---|---|
| **G-20** | `AzureBlobCheckpointSaver` — the on-blob format is complete; the `BaseCheckpointSaver` method set is absent | S-C07 | **unscheduled** |
| ~~**G-21**~~ | ~~`ImproveBlobClient` — the class interface, and how registry updates sequence against case writes~~ **CLOSED 2026-09-01, procedure step 3.5.** **There is no class interface** — §54 holds `storage/blob.py` to module-level functions only, so the gap asked for something that may not exist here. Thirteen module-level names replace the class (S-C08 carries the table); `write_phase_gate` awaits the case write **before** the registry update, because the case blob is the system of record. Lifecycle is one loop-keyed cached `aio` client closed by `aclose()`. **Deletion is NOT covered and is a new gap** — nothing removes `uploads/{case_id}/{file}` (WATCH 10) | S-C08 | closed |
| **G-22** | `CircuitBreaker` — thresholds and state machine complete, interface absent | S-C35 | **unscheduled** |
| **G-23** | `DMAICGateValidator` — static method names, signatures and return shapes; must be designed with G-31 | S-C26 | **unscheduled** |
| **G-24** | Constructor arguments for all four remaining custom middlewares — `(...)` is literal in §19 in every case | S-C11, S-C12, S-C13, S-C14 | **unscheduled** |
| **G-26** | Retriever-layer signatures, `RETRIEVAL_EXCEPTIONS` membership, and the `_fail()` contract | S-F18 | **unscheduled** |
| ~~**G-27**~~ | ~~Boundary mappers for Measure, Analyse, Improve and Control — including what each `phase_context` contains~~ **CLOSED 2026-08-31, procedure step 3.3.** All ten mappers built. `phase_context` ruled: the prior phase's **Tier-1 fields + `phase_metrics` + `acknowledged_gaps`**, rendered as `field: value` lines; **Tier 2 excluded** — a Belt may consciously proceed without a Tier-2 field, so carrying one invites the next planner to read a permitted absence as a finding. `acknowledged_gaps` travels precisely so "decided to proceed without this" stays distinguishable from "nobody asked" | S-F12 | closed |
| **G-28** | Gate assembly for Measure, Analyse, Improve and Control — 55 field assignments, each selecting a tier access pattern, and an omission is silent | S-F28, S-F07 | **unscheduled** |
| **G-29** | `propose_template` — an open "etc." type list and no `fill_data` schema | S-F19 | **unscheduled** |
| **G-30** | `propose_diagram` — types and schemas are said to live in `core/diagrams.py`, **which does not exist** | S-F20 | **unscheduled** |
| **G-31** | `check_gate_status()` — return shape unspecified, and a zero-argument signature that must nonetheless know the phase and read `artifacts` | S-F21 | **unscheduled** |
| **G-32** | `request_human_approval` — how a tool raises a graph-level interrupt from inside the executor's tool loop | S-F22 | **unscheduled** |
| **G-33** | `load_skill(name)` — in neither the universal eight nor any phase count. **ANSWERED 2026-09-04 (ruling AH4), landed here 2026-09-10: `load_skill` is MIDDLEWARE-REGISTERED and therefore outside §30's totals**, so it consumes none of the per-phase budget and the collision does not arise while it is never bound as a tool. **THE ARITHMETIC IN THIS ROW WAS FALSE IN THE DANGEROUS DIRECTION**: it read *"if bound, Measure goes to 16 against a cap of 16"* — legal by a hair. With the universal EIGHT (§60.7, 2026-09-09) binding it takes Measure to **17 against a cap of 16**, illegal on the day it happens. The gap stays OPEN because the answer is a placement, not a ceiling: whoever revisits §30's cap must settle it BEFORE a ninth universal tool. Pinned by `test_the_three_tool_counts_that_must_not_drift` | S-F23, S-F02, S-C12 | **unscheduled** |
| **G-34** | The escalation subgraph — no node list, no state schema, no exit contract | S-F08 | **unscheduled** |
| **G-35** | `synthesise_partial()`, `delete_or_flag_stale_in_case_index()` (delete **or** flag stale — the name carries the undecided choice), and the `degraded_coaching_response` node, which is not one of §13's permitted five. **STILL OPEN** — but §64.3 now carries a *design note* on making the `improve_case_index` write idempotent and encapsulated so the compensating action covers only the non-idempotent residue. **An input to step 8.2, not a ratification and not a closure** | S-F31, S-F32, S-F33, S-F09, S-F29 | **6.10**, **6.20**, **8.2** |
| **G-36** | ~~No upload endpoint exists, no file owns the upload handler~~ — **both answered; the endpoint is in §49 and S-F34 (Part AP5) and the handler has steps 6.11 / 6.12.** STILL OPEN on the code: §29.1's sole external channel, and step 6.11 is where it closes or is re-scoped | S-F35, S-F34 | **6.11** |
| **G-37** | **Nothing writes `improve_case_index`** — the schema is defined, cleanup of it is required, and no writer is named | S-F36 | **unscheduled** |

### 66.5 Group E — content the build sequence defers

| # | Gap | Attaches to | Step |
|---|---|---|---|
| **G-39** | `turn_count`'s increment contract, load-bearing in §11's deterministic `step_log` key | S-C02 | **unscheduled** |
| **G-40** | Prompt constants — `{PHASE}_COACH_PROMPT`, `{PHASE}_PLANNER_PROMPT`, five `PHASE_RUBRIC`s and four `{PHASE}_CONSTRAINTS` sets are named with coverage lists and no text. Only `COACHING_QUALITY_RUBRIC` is written out | S-F26 | **unscheduled** |

### 66.6 Closed

| # | Gap | Resolution |
|---|---|---|---|
| **G-41** | The two calibrated samples' verbatim text was in no file in the repository — `SPEC_LAYER_GUIDE.md` §7 gave their skeletons and deferred the full text to the 2026-08-23 conversation | **CLOSED 2026-08-23.** The approved verbatim text was supplied at `agent-improve/docs/_archive/SPEC_SAMPLES.md` and transcribed into §57.2 and §57.3 (archived to docs/_archive/; canonical: ARCHITECTURE.md §57.1; ARCHITECTURE.md §57) | closed |
| **G-03** | `PhaseState` declared no case identity and no phase identifier, while three specified functions read one or both off it | **RESOLVED 2026-08-24**, ruling A2. Two fields added — `case_id`, `current_phase` — copied down by the input mapper at phase entry, read-only in the subgraph, never written back up. Chosen over reading `case_id` from config and phase from a build constant, **because mixing sources is what made the defect latent.** S-C02; DECISIONS §T1 | closed |
| **G-42** | The boundary mappers had no stated execution site: §9 made them plain functions, §13 permits exactly five nodes and none is a mapper, §12 embeds each subgraph as a parent node | **RESOLVED 2026-08-24**, as the same fix. The mapper runs **inside the parent's uniquely-named node function** for that phase — the documented LangGraph pattern where parent and subgraph share no state keys — so it adds no sixth node. Carries the call-order namespace stability condition. S-F10, S-F12; DECISIONS §T1 | closed |
| **G-43** | Raised 2026-08-24: subgraph state might not persist across Belt turns, because §16 compiles phase subgraphs with no checkpointer argument | **RESOLVED 2026-08-24 — FALSE ALARM. Design confirmed correct.** Every `.invoke`/`.ainvoke` in this document is either the single parent-graph entry point or an LLM call; **no subgraph is invoked standalone, outside the parent.** Checkpointer placement is the prescribed pattern — parent compiles with the checkpointer, subgraphs compile bare and inherit persistence through an auto-managed `checkpoint_ns`. The `checkpointer=True` clause whose absence raised the alarm applies to **independently-persisted** subgraphs, which Agent Improve deliberately does not use; **omitting it is correct, not a defect.** What remains is the already-known **⚠ WIRED, INERT** checkpointer — `thread_id` is not yet passed at `ainvoke` in the current *code* — which is already scheduled as the `thread_id`-through-`ainvoke` step (§16, §47, §53.1). **G-43 folds entirely into that step and adds no new work.** **What it did NOT verify is the wrapper-internal invoke prescribed by G-42/S-F10 — that distinct case was tracked as G-44 and is itself now resolved (below).** DECISIONS §U1 | closed |
| **G-04** | `remaining_steps` read off `PhaseState` twice (§26), undeclared — the `.get(..., 10)` default returned 10 forever and the 5-hop cap never fired | **RESOLVED 2026-08-24.** Declared as a LangGraph managed value (`remaining_steps: RemainingSteps`) on `PhaseState`; the engine now populates it live. The 10 was a bug artifact and is gone; the 5-hop business rule, enforced by the `<= 2` entry guard, is unchanged and now actually fires. Verified against current LangGraph docs/source. See S-C02, §26. | closed |
| **G-01** | Level 2 (subgraph-internal) `Command` routing was undesigned: §13 drew the branching, §15 stated the rule, and no `Command(goto=…)` existed anywhere | **RESOLVED 2026-08-24.** Three decision points, at S-F13: the **planner** owns field/gate routing and the executor returns plainly (§17); the validation exit increments `gate_attempts` **once at entry** and branches pass / retry / escalate; the gate exit is approve → `END`, reject → planner. Verified against current LangGraph docs. **DP1's predicate depended on G-38, closed 2026-08-25 for Define** (§39.1.2); **the escalation exit's node name still depends on G-34** (open). See S-F13, §13, §15 | closed |
| **G-02** | What a Belt REJECT does was unstated — `POST /gate/reject` existed in §49's table and in §33.1's frontend sequence with no defined behaviour | **RESOLVED 2026-08-24, founder ruling.** Reject **loops to the planner for another coaching turn**; the Belt **MUST supply a reason**, carried as `rejection_feedback` — a new `PhaseState` field (S-C02) — so the re-coach addresses what was actually objected to rather than repeating the refused turn. **The `/gate/reject` payload gains a mandatory reason, which depends on G-18** (open). See S-F13 DP3, §33, S-C02 | closed |
| **G-44** | Raised 2026-08-24 as the narrow successor to G-43: the S-F10 wrapper node's inner `subgraph.ainvoke` is a third case neither §16's bare-node claim nor G-43's standalone-invoke check covered. | **RESOLVED 2026-08-24.** Pattern B (wrapper node invoking the subgraph) is correct and is in fact forced — `SupervisorState` and `PhaseState` share no keys, so `add_node(subgraph)` is unavailable. The inner invoke persists `PhaseState` across turns **provided** it is called directly inside the node function with inherited config and is never relocated inside a tool. Verified against current LangChain subgraph docs; local repro owed. See §16. | closed |
| **G-25** | **The 20 computation tools** — no signature, no `args_schema`, no return shape for any of them; and no defined shape for §7's required "reformatting request" | **RESOLVED 2026-08-26.** **§69** specifies all twenty as **S-F37–S-F56** — inputs, `result` keys and methodology preconditions per tool — with the repeated header fields and the string-valued `result` rule stated once at §69.1. The "reformatting request" shape is settled there as a **returned value, not a raised error** (§60.6 B3), so a tool that cannot parse its input hands the Belt something to act on rather than failing the turn. Two boundaries are stated rather than left to be rediscovered: `post_improvement_cpk` stays a separate `@tool` from `calculate_cpk` despite sharing the formula (§30's no-mode-argument rule), and **Measure deliberately has no chart-limit tool** (§69.7). §60.6 stays as the group entry and its rebuild test now reads *met*. See §69, S-F24 | closed |
| **G-45** | **`metric_definitions` had no spec entry.** Registered and resolved in one pass: §39.2 (Measure) and §50 both refer to the project metric registry, and until §63.8 existed those were dangling references — a spec citing a structure this document never defined | **RESOLVED 2026-08-26.** **§63.8 — S-C38** defines it: `list[dict]` of `{name, unit, meaning}`, Define-owned, with `name` as the traceability key and four EARS behaviors. Registered here rather than left implicit because §55.1 requires every referenced spec to resolve, and a reference that resolves only because nobody checked is the failure §55 names. See §63.8, §39.1 | closed |
| **G-46** | **`phase_metrics` had no spec entry.** Same class as G-45 and raised by the same pass: §39.2, §40 and §50 all refer to a per-phase metric placeholder that no entry defined | **RESOLVED 2026-08-26.** **§63.9 — S-C39** defines it: `list[dict]` on all five schemas, `name` equal to a registry `name` by key equality, per-phase content tables for the five, five EARS behaviors, and the `"none this phase"` rule that keeps an empty list from meaning two different things. **§40's same-field-on-all-five rule now binds three fields**, not two. See §63.9, §40 | closed |
| **G-38** | `field_index` had no ordering source — the per-phase field list it indexes into was stated nowhere, and §13's "advance to the next field" depended on it. **G-01 depended on it too**: S-F13 DP1's predicate could not be implemented without it | **CLOSED 2026-08-25.** §39.1.2 states Define's ordered field list — **twelve** coached fields, `business_case` through `issues_and_barriers` (the list grew from ten at the 2026-08-26 Option A finalization, which added `target_value` and brought `secondary_metrics` into the coached walk) — and **that list IS the `field_index` sequence.** DP1's predicate is now implementable for Define. **The closure is Define-only by design:** §39.1.8 gives the other four phases the same section shape at §39.2–§39.5, and their lists remain blocked on G-27 and G-28. Resolution reconciled the v1-code divergence toward the v2 names (F-11). See §39.1.2, S-F13, S-C02 | closed |

| ~~**G-87**~~ | **CLOSED 2026-09-18 at step 6.41.** One bound became three — **50** built-and-unanchored (a BACKLOG, whose rise is unambiguously bad), **16** ratified-but-unbuilt (a SPECIFICATION, whose rise is normal) and **96** never assessed. Four facts anchored, each verified individually; §10's reads `absent: backend.storage.blob::ImproveBlobClient` and the evaluator answers *“absent, as claimed”*, so the anchor proves the sentence rather than resolving near it. *Original statement:* **THE UNANCHORED-FACT BOUND ONLY EVER RISES, SO IT IS A COUNTER AND NOT A RATCHET.** `register facts carrying no symbol anchor` pins how many register rows carry an em dash where a symbol belongs. It was introduced at **6.31**'s successor 6.37 at **70**, rose to **166** at 6.39 when the 96 spec entries arrived, and rises again at 6.40. **Every movement so far has been upward and each was legitimate**, which is the problem: a bound that is raised whenever it is exceeded constrains regression and nothing else. **It cannot distinguish a register that is growing from one that is rotting**, and the number reads as progress because it keeps being updated. **The check is not wrong and is deliberately not weakened** — it does catch a new row parked at an em dash, which is what it was built for. What is missing is the other direction: nothing lowers it, and no step owned that work until this gap. Founder observation 2026-09-18, registered rather than left in a commit body, on §66's own argument that a gap without a step is scheduled by nothing | Appendix F, verify_built.py | **6.41** |

### 66.7 Findings — recorded, not gaps

**A gap is something missing. A finding is something present and wrong, or
present and inconsistent.** These were surfaced by the conversion pass and the
Supplier/Customer cross-check, whose first run is recorded at §66.8; by the
Define finalization of 2026-08-26 (**F-12**); and by the multi-criteria ruling
of the same day (**F-13**, **F-14**). **None was fixed by the pass that raised
it**; each needs a §56-routed decision of its own. **F-12, F-13 and F-14 are all
owed to phase reviews that have not happened yet** — two to Control's, one to
Analyse's.

| # | Finding |
|---|---|
| **F-01** | **The drift registry cannot see this document.** `.claude/config/deprecated_patterns.yaml` excludes `agent-improve/*.md` and `agent-improve/**/*.md` from patterns 2–8. **This file moved to the monorepo root in v1.2 and the exclusion was never updated**, so the platform governance document is now guarded as if it were code — while the registry's own header names `AGENTIC_ARCHITECTURE_REFERENCE.md` among the documents that must be able to name a deprecated construct in order to prohibit it. **Fourth instance of the pattern §55 names:** a correct rule paired with a check that cannot see what it governs |
| **F-02** | **§33 step 9 still reads "Supervisor reads `gate_passed`, static edge advances."** v2.2.20 of `CLAUDE.md` deliberately tightened its equivalent step to "the parent's static edge advances," on the ground that "routes onward" was the last phrasing from which the deleted `route_after_phase` design could be re-derived. **The reference's own step 9 was not tightened with it**, so the two binding documents now differ on the sentence that DECISIONS §R2 exists to police |
| **F-03** | **The calibrated `phase_executor` sample cites "(§35)" for the four-layer validation stack, twice** — once in its Art. 15 row and once in its DORA row. §34 is the four-layer stack; §35 is the two-tier field rule. Transcribed verbatim and not corrected, because the sample is the approved standard |
| **F-04** | **The calibrated `phase_executor` sample's Supplier cell names only `phase_planner`.** `analyse_executor_node` (S-F09) produces `synthesis_output` that the coach call reads, which makes it a second supplier on multi-hop turns. Not corrected — verbatim |
| **F-05** | **Middleware is invisible to the Supplier/Customer cross-check.** Per the approved judgment call, the five custom middlewares are class entries without SIPOC tables — yet `phase_executor`'s Customer cell names `ContradictionDetectionMiddleware` as its first consumer. The cross-check cannot close on that edge. Either middleware needs SIPOC cells, or the rule needs to state that it ranges over nodes and functions only |
| **F-06** | **The 20 computation tools are likewise invisible**, for the same reason: S-F24 is one entry with behaviors and no SIPOC. They are named in `phase_executor`'s Input cell via `tools=` and nowhere else in the cross-check |
| **F-07** | **The cross-check rule does not model two structures it meets constantly.** *Request/response pairs*: the API surface both triggers the graph and consumes its output, so each is the other's Supplier and Customer, and a strict reading reports a mismatch. *Nesting*: Layers 2c and 2d, gate assembly, the policy advisory, RRF and the retriever layer are sub-components of their own callers, so their Supplier and Customer are the same entry. Both are correct designs that the rule as written flags. **Recommendation: state the rule as ranging over peer node-to-node edges, and exclude nested sub-components and return paths explicitly** — otherwise it produces noise that trains people to ignore it, which is the §55 failure mode |
| **F-08** | **The gate document is written to the same Store key twice** — by `gate_apply_node` (§33.2) and again by the phase's output mapper (§9). The write is idempotent by key so nothing breaks, but **neither section names which is authoritative**, and a future change to one will not obviously require a change to the other |
| **F-09** | **`BeforeModelStateInjection` is named after the hook it must not use.** Its hook is `before_agent`; §19, §19.1 and `CLAUDE.md`'s no-go list each correct the `before_model` reading separately. The class name reproduces the error every time it is read |
| **F-10** | **`degraded_mode_response` reads counts that `check_gate_status()` produces** (§46 body vs §29.2), and both are unspecified (G-31). They should be designed together, or the Belt sees two different completion counts |
| **F-11** | **The built `DefinePhaseInput` had diverged from the v2 architecture names.** It carried granular 5W2H fields (`what`, `where`, `when`, `who_affected`, `why_it_matters`, `how_much_baseline`, `how_goal`), `scope_in`/`scope_out` as separate strings, and **both** `target_date` and `estimated_completion_date` — a duplicate date. **Resolved by the §39.1 rebuild**, in favour of the v2 names: one composed `problem_statement`, `project_scope` as a dict, one `target_date`. **Recorded so the rebuild is not later read as having introduced those names** — it retired them. The 5W2H survive as the coaching method (§39.1.3), never as stored fields |
| **F-12 — RESOLVED 2026-08-27** | ~~**Control has no `actual_close_date`.**~~ **Closed at the Control phase review (§39.5):** `actual_close_date` is added to `ControlOutput` as **Tier 2**, 16 → 17 fields, §35's Control row to 3/9. **Tier 2 is the ruling, not an oversight** — a slipped date does not invalidate the improvement, the same logic that makes Define's `target_date` a planning parameter. **The original finding, for the record:** Define's finalization (2026-08-26) makes `target_date` a required field and states explicitly that it is the **planned** completion date — a project-management parameter that may slip without invalidating the improvement. **The pattern it belongs to is target-vs-actual**, the same one `target_value` uses: Define states the target, Control captures what actually happened, and the delta is the finding. `target_value` has its Control counterpart in `post_improvement_metrics` (S-C31); **`target_date` has none.** Recorded as a forward dependency, **not built here** — Control's field list is settled at its own phase review (§39.5, blocked on G-27/G-28), and adding a field to `ControlOutput` outside that review is exactly the one-phase-at-a-time change §40 warns about. **When Control is specified, `actual_close_date` must be on the agenda alongside the schedule-variance question it implies** (is a slipped date a Control finding, or only a record?) |

| **F-13 — RESOLVED 2026-08-26** | ~~**Analyse's `causal_hypothesis` does not say WHICH criterion a root cause explains.**~~ **Closed at the Analyse phase review (§39.3):** the cross-phase reference shape (§63.6, S-C32) gains **`references_metric_name`**, and the grader now matches it against the referenced phase's `phase_metrics` `name` rather than reading a bare scalar (S-C32 B1, B5). The key is on **all three** reference dicts for a uniform resolution path; Analyse populates it now, Improve and Control at §39.4 and §39.5. **The original finding, for the record:** Harmless while a project tracks one measurement criterion; ambiguous the moment it tracks two. `causal_hypothesis` is a cross-phase reference dict (§7, §42) carrying `references_phase` / `references_field` / `references_value`, and the grader verifies the link by deterministic lookup — but with `baseline_estimate` naming *"Error rate: 12.3%. Cycle time: 2.6 days."*, a root cause referencing "the baseline" resolves to a string containing both, and **"explains 60% of the problem" stops having a single referent.** `practical_significance` inherits the same ambiguity. **Recorded, not built** — Analyse's field list is settled at its own phase review (§39.3, blocked on G-27/G-28), and adding a sub-key to one phase's reference dict outside that review is the one-phase-at-a-time change §40 warns against. Raised by the multi-criteria ruling, 2026-08-26 |
| **F-14 — RESOLVED 2026-08-27** | ~~**Control's target-vs-actual becomes one comparison per criterion.**~~ **Closed at the Control phase review (§39.5.3):** `phase_metrics` is the authoritative store of all N comparisons, one entry per registry metric with `baseline` / `target` / `actual` / `delta` / `met`; `post_improvement_metrics` remains the primary metric's Tier-1 link, carrying `references_metric_name`; the single-authority invariant binds the two (`core/metrics.py`, unit-tested); and **the grader grades every entry, not only the primary**. **The original finding, for the record:** *(§39.4 landed 2026-08-27, leaving Control the last unspecified phase — this is now the one open finding blocking §39.5.)* *(Still open — but its reference shape is now defined: `post_improvement_metrics` carries `references_metric_name` from 2026-08-26, unpopulated until §39.5. What remains is Control's own decision about how N comparisons are presented and graded, not how they are addressed.)* `post_improvement_metrics` (S-C31) is the AFTER end of the measurement thread and is graded by lookup against Measure's `baseline_mean` (§63.5 B2). With N criteria that is **N comparisons, not one** — and a Control phase reporting a single improvement delta across several metrics is the same failure `MEASURE_RUBRIC` now catches at the Measure gate, arriving one phase later. Pairs with **F-12**, which owes Control an `actual_close_date`: both are Control-side consequences of Define-side decisions, and **both should be settled in the same Control review** rather than discovered separately. **Recorded, not built.** Raised by the multi-criteria ruling, 2026-08-26 |

| **F-15** | **DECLARED, AND READ BY NOTHING — four instances, and the fourth was found by looking.** WATCH 19's shape, registered here 2026-09-10 because it stopped being an incident and became a pattern. **(1)** The Store's `case` namespace had no writer — §9 and S-F10 named readers, nothing wrote it; closed at step 6.8. **(2)** `PhaseState.uploads` had no writer: the boundary mapper hardcoded `[]` from 3.1 to 6.11, so no upload could reach a gate document; closed at 6.11. **(3)** §6 declares an *"evidence context"* reader of `uploads` and nothing read it, until 6.12's upload manifest (`DECISIONS.md` Part AS3). **(4)** `knowledge/retriever.py::get_evidence_vectorstore()` is defined, correct, and **called by nothing** — both live evidence paths use a raw `SearchClient` (Part AT). **The first three were each found while building something adjacent, never by a check.** The fourth was found by 6.13's audit reading a sub-step that instructed a change to it. **§55.1's bidirectional rule covers references between documents; nothing applies it between a declaration and its reader** — that absent check is the finding, and step **6.17** (the count-check, renumbered from 6.15 on 2026-09-11 when 6.16 landed ahead of it) is the nearest thing scheduled to it |

### 66.8 The Supplier/Customer cross-check — first run, 2026-08-23

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

# Part XIII — Compliance and Risk

*The EU AI Act and DORA obligations this architecture is designed to satisfy,
and the register that aggregates them. **This Part is scaffolding placed
2026-08-23**: the posture is stated, the obligations are mapped to mechanisms
that already exist, and the classification question is left open because it is a
legal determination.*

---


## Appendix H — The capability register

> **THE UNIT OF PROGRESS.** The working method's clause 1. One row per thing a
> phase must be able to do, each with **the single executable check that proves
> it**. The project's status is the count of green rows; the step count is
> demoted to what it has always actually measured, which is effort.

### The contract

| Column | Holds |
|---|---|
| `ID` | Stable. Cited by every step's `NEEDS` and `GIVES`, so it may never be reused or renumbered |
| `Capability` | What a phase must be able to DO, in the product's terms. Never a component, never a file |
| `Check` | **ONE executable check**, named as `module::test_name`. Not a description of how one would test it |
| `State` | 🟢 green · 🔴 red. **No third value** |
| `Given by` | The step whose `GIVES` names this row |

**Green or red, and never partial.** A check that half-passes is two
capabilities badly written, not one capability half-built — so the fix for
"it mostly works" is to split the row, never to invent an amber.

**ONE check per row, and it must be executable.** A row proved by two checks
can be green in one and red in the other, which is the partial state under
another name. A row whose `Check` reads *"a live run shows…"* is a row nobody
can run, and an unrunnable check is indistinguishable from a passing one.

> ### ⛑ ONE EXCEPTION, RULED 2026-09-23 — THE `live-turn` METHOD
>
> **Rows 26–32 are checked by WATCHING A LIVE TURN**, and the reason is
> §43's own: *a structural probe cannot tell whether the method is sound.*
> Whether a calculation was TAUGHT before its number was given, whether an
> example was offered before a field was asked, whether a weak answer was
> CHALLENGED rather than completed for the Belt — none of these is visible to
> a check that reads state. A probe can confirm a tool ran; it cannot confirm
> the coaching was coaching.
>
> **The paragraph above still binds on every other row**, and this exception
> is deliberately narrow: it is available only where a structural probe would
> answer a DIFFERENT question from the one the row asks, and the row must say
> so in its own `Check` cell.
>
> **The cost is stated rather than hidden.** A `live-turn` row cannot go green
> in CI and cannot go green without a person. It is **🔴 until somebody
> watches a turn and records what they saw**, with the case id and the date —
> the same evidence standard a `live-run` step carries. A `live-turn` row that
> is green with no such record is the unrunnable check this contract warns
> about, wearing the exception as cover.
>
> **Tightened by founder ruling, 2026-09-23: once row 35 is green, the record
> carries the LangSmith TRACE ID of the turn that was watched**, as well as the
> case id and the date. A person's observation becomes a pointer anyone can
> reopen — the turn is re-readable by the next reviewer, and the claim *"I
> watched it"* stops being the only evidence that it happened.

> ### ⛑ EVERY LIVE PROOF STATES *"FIRST TURN IN PROCESS: YES/NO"* — ruled 2026-09-24
>
> **A live turn's timing depends on whether it is the first in its process.** At
> step 8.0's executor slice, every degraded open question on record turned out
> to be a first turn in a fresh process, paying for client builds a later turn
> never sees (G-93, closed at 6.54). A proof that does not say which it was
> cannot be compared with another. **Every live proof — a `live-run` step, a
> `live-turn` row, a trace cited as evidence — records its trace id AND
> *"first turn in process: yes"* or *"no"*.**

**A row is about the PRODUCT, not the tree.** *"A Belt's captured value
survives the next turn"* is a capability; *"`merge_field_log` has a reducer"*
is an implementation detail that might be one way of delivering it. The
register has to stay true across a rewrite of the thing beneath it.

### How it differs from Appendix F, which it does not replace

| | Appendix F | This register |
|---|---|---|
| Asks | Does the TREE match what the architecture SPECIFIES? | Can the PRODUCT do the thing? |
| A row is | A specified fact, anchored to a symbol | A capability, anchored to a check |
| Answers | Is it built? | Does it work? |

**Both are needed and neither substitutes.** Appendix F would report every row
green for a Define slice in which no Belt can pass a gate — it did, for weeks —
because each specified fact was built exactly as specified. The capabilities
were never the thing being counted.

### ✅ THE SEED HAS LANDED — all 35 of Define's rows are written

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

**Two kinds of `Given by` in the seed, and they are not the same claim.**

| `Given by` reads | Means |
|---|---|
| **6.xx** | The step that BUILDS the capability, and whose check turns the row green |
| **built at X · proven by 6.49** | The mechanism landed at X; **the row stays red until 6.49 writes the check** that proves it on the product (rows 5, 6, 10, 11) |

**Row 24 has NO owning step**, the one departure from *"one owning step
each"*, and it is deliberate: Measure reading Define's record waits on the
graph owning its own boundary (**the boundary finding, stage 7**), and no step
exists for that yet. A step invented to fill the cell would be ordering work
nobody has specified. **Row 22 is BLOCKED-ON-SPEC** (clause 4) — its owner 7.2
waits on the Define rubric text, founder.

**`NEEDS` and `GIVES` on the Define steps are written as capability
STATEMENTS** rather than as `CAP-n` references, because an implementer
inventing the IDs would have been inventing the rows. **Each statement now
binds to exactly one row**, and that binding is the first thing each step's
card is checked against when it starts.

| ID | Capability | Check | State | Given by |
|---|---|---|---|---|
| **1** | A case can be created and opened — the case list returns it and it opens | `backend.tests.test_capability_rows::test_row_1_a_case_can_be_created_and_opened` | 🟢 | **6.49** |
| **2** | A turn returns a coached reply — one POST, one graph run, a message back | `backend.tests.test_capability_rows::test_row_2_a_turn_returns_a_coached_reply` | 🟢 | **6.49** · **6.54** |
| **3** | The coach follows the Define script for the current field — the turn records that the script reached the model | `backend.tests.test_capability_rows::test_row_3_the_coach_follows_the_define_script` | 🟢 | **6.46** |
| **4** | The Belt is asked for the right next field — field two is asked only once field one is complete | *pending — 6.45 writes it* | 🔴 | **6.45** |
| **5** | A captured field survives the next turn — turn two captures the team and the business case is still there | `backend.tests.test_capability_rows::test_row_5_a_captured_field_survives_the_next_turn` | 🟢 | built at **6.33** · proven by **6.49** |
| **6** | Every change is kept, dated, with its prior value — a correction leaves both values readable in `field_log` | `backend.tests.test_capability_rows::test_row_6_every_change_is_kept_dated_with_its_prior_value` | 🟢 | built at **6.33** · proven by **6.49** |
| **7** | The Belt's reason for a change is recorded — `field_log.reason` is non-empty after a correction | *pending — 6.44 writes it* | 🔴 | **6.44** |
| **8** | The Belt can upload evidence — the file lands and is indexed | `backend.tests.test_capability_rows::test_row_8_the_belt_can_upload_evidence` | 🟢 | **6.49** |
| **9** | The coach can read an uploaded document — a turn quotes a line from the upload | *pending — 6.43 writes it* | 🔴 | **6.43** |
| **10** | Calculations are recorded — `computation_results` carries its five keys | `backend.tests.test_capability_rows::test_row_10_calculations_are_recorded` | 🔴 | built at **6.20** · proven by **6.49** |
| **11** | The metric entry mirrors the primary scalars — `phase_metrics` equals `baseline_estimate` and `target_value`. **Row 25 is the other half**: the mirrored values must be usable | `backend.tests.test_capability_rows::test_row_11_the_metric_entry_mirrors_the_primary_scalars` | 🟢 | built at **6.20** · proven by **6.49** |
| **12** | Vague or contradictory answers are caught inside the turn — layer 2a rejects and re-asks | `backend.tests.test_capability_rows::test_row_12_vague_answers_are_caught_inside_the_turn` | 🔴 | **6.49** |
| **13** | The coach's own process is graded every turn — the coaching rubric scores the turn | `backend.tests.test_capability_rows::test_row_13_the_coaching_rubric_scores_the_turn` | 🟢 | **6.49** · **6.52** · **G-96** (red 2026-09-24 13:14, green again on trace `01a0d3e5-6246-7de3-b768-2ee767a5130c`) |
| **14** | Progress shows the real field count — the bar reads *5 of 12*, not *0 of 26* | *pending — 10.3 writes it* | 🔴 | **10.3** |
| **15** | The coaching blocks render — explanation, example, prompt and citations are visible | *pending — 10.0 writes it* | 🔴 | **10.0** |
| **16** | A failed turn gives a readable error — a backend failure says what happened and stays on screen | *pending — 10.4 writes it* | 🔴 | **10.4** |
| **17** | Required fields are checked before the gate — layer 2b refuses a case missing a required field | `backend.tests.test_capability_rows::test_row_17_required_fields_are_checked_before_the_gate` | 🟢 | **6.49** |
| **18** | Captured values carry their declared type — container 4. Team, scope, the SIPOC map and the registry arrive structured, not as prose, on a live run | `backend.tests.test_declared_types::test_row_18_captured_values_carry_their_declared_type` | 🟢 | **6.48** + the S-C05 amendment (ARCHITECTURE.md v1.70) |
| **19** | A complete case ASSEMBLES a gate document | `backend.tests.test_define_phase_metrics::test_row_19_a_complete_case_assembles_a_gate_document` | 🟢 | **6.20**, the scorecard half |
| **20** | The document is WRITTEN, and safe to write twice | `backend.tests.test_gate_write::test_row_20_the_document_is_written_and_safe_to_write_twice` | 🟢 | **6.42** |
| **21** | The gate write preserves the change log and the uploads | `backend.tests.test_gate_write::test_row_21_the_gate_write_preserves_the_change_log_and_the_uploads` | 🟢 | **6.42** |
| **22** | Constraints and the phase rubric grade the gate document — 2c and 2d run at the gate and can fail it | *pending — 7.2 writes it* | 🔴 | **7.2** — BLOCKED-ON-SPEC: the Define rubric text, founder |
| **23** | The Belt sees the gate document and approves it — the run pauses and an answer resumes it | *pending — 7.7 writes it* | 🔴 | **7.7**, which needs **7.3** |
| **24** | Measure can read Define's record — Measure starts without `PriorGateDocumentMissing` | *pending — no step yet* | 🔴 | **none yet** — waits on the graph owning its own boundary (the boundary finding, stage 7) |
| **25** | The baseline and target are stored as values Control can compare — each parses as a number with a unit, not a sentence (§63.1 B7) | *pending — 6.51 writes it* | 🔴 | **6.51** |
| **26** | A calculation is TAUGHT before its number is given — a turn that runs `calculate_expected_savings` explains the concept first (§43.1) | *`live-turn` — see the contract exception* | 🔴 | **6.46** |
| **27** | Every field is shown with an example BEFORE it is asked (§43.2), and the example is never captured as the Belt's data (§22) | *`live-turn`* | 🔴 | **6.46** |
| **28** | The Belt always knows where they are in the session — every coaching turn states *Step n of 12* (§43.3) | *`live-turn`* | 🔴 | **6.46** |
| **29** | The Belt can see the gate document filling in — `check_gate_status` returns captured and missing fields and the coach shows them (§43.4) | *`live-turn`* | 🔴 | **6.46** |
| **30** | The coach teaches in its own voice and never hands over a link (§43.5) | *`live-turn`* | 🔴 | **6.46** |
| **31** | Weak answers are CHALLENGED; the coach never writes the Belt's answer for them (§43.6) | *`live-turn`* | 🔴 | **6.46** |
| **32** | The Belt understands what their metric means, why it matters and how to read it — from the registry's `meaning`, never invented (§43.7) | *`live-turn`* | 🔴 | **6.46** |
| **33** | A checkpoint is written after EVERY NODE of a Define turn | `backend.tests.test_capability_rows::test_row_33_a_checkpoint_is_written_after_every_node` | 🟢 | **6.49** |
| **34** | A paused case survives a restart and resumes where it stopped | *pending — 7.3 writes it* | 🔴 | **7.3** |
| **35** | Every Define turn leaves a LangSmith trace, with the model call, the tools and the middleware visible | `backend.tests.test_capability_rows::test_row_35_every_define_turn_leaves_a_langsmith_trace` | 🟢 | **6.49** |
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

## Appendix I — The plan: epics, stories and rank

> **THE SINGLE SOURCE IS `agent-improve/tools/control_board/stories.py`** —
> nine epics, 37 stories, each with its capability rows, its steps and one
> rank. Founder ruling, 2026-09-23. **This appendix is a POINTER, not a copy**:
> a second table of 37 stories is the duplication this document has paid for
> three times over, and the file is the thing the generator reads.

### The rule

**Appendix F's `Order` column is DERIVED from story rank. It is no longer
maintained by hand.**

**Two hand-maintained orderings of one run of work will disagree**, and this
document's own history is the evidence: `Order` has been corrected twice in two
weeks — once when two rows collided on the same number, once when a step left
the critical path by inference rather than by ruling. That is the failure the
`Seq` watermark had, that two copies of the `PhaseState` census had, and that
Appendix D and `BUILD_TRACKER.md` had before guard rule 2 was deleted for it.
**One is written and the other is computed, or they drift.**

### ✅ THE FILE IS IN THE TREE, AND THE PRE-COMMIT HOOK READS IT — 2026-09-23

**`agent-improve/tools/control_board/stories.py` resolves**, and
`build_control_board.py` reads it on every commit — `.githooks/pre-commit`
runs it after `build_board.py` and stages `docs/control-board.html`. What that
page shows from the plan is now DERIVED, not typed:

| On the control board | Derived from |
|---|---|
| Capability rows proven | **Appendix H** — the count of 🟢 rows, not the stories that claim them |
| A story is DONE | **Appendix H** — every one of its rows is 🟢 |
| A task is DONE | **git log** — `refactor(arch-v2): commit X.Y`, the rule `build_board.py` uses |
| NEXT | **rank** — the top-ranked story that is not done, and its first open step |

**What is still typed, and labelled `HAND` on the page:** the status of a
story with no rows yet, of a task that is not a procedure step, and of every
bug — no source owns those. The component inventory stays `RELAYED`, from the
tree audit at `208e4a7`.

> ### ⧗ NOT YET LIVE — Appendix F's `Order` is still hand-set
>
> **The rule above is ratified; its derivation is not built.** `build_board.py`
> reads `Order` from Appendix F (`read_order()`), and nothing computes that
> column from `stories.py`'s rank. **The two agree today**: ranks 1–6 are
> S9, S33, S7, S4, S5 and S6, and S6's two steps (7.3 and 7.7) take `Order` 6
> and 7. They agree because both were written from the same ruling, **not
> because anything enforces it**. The control board's NEXT and order strip
> read rank, and the step board reads `Order`, so an edit to one shows up as
> the two boards disagreeing. It closes when `Order` is computed from rank, or
> checked against it at the commit gate.

### The run of work — superseded 2026-09-25

**The 2026-09-23 transcription that stood here is withdrawn.** The run of
work is Appendix F's `Order` column (founder rulings 2026-09-25: 6.61, 6.62,
10.0, 6.59, 6.58, 6.56, 6.45, 6.51, 10.3, 10.4, 6.43, 6.44, 7.1, 7.2, 7.3, 7.7, 7.4, 7.5,
7.8, 7.9). A second copy here is what the 8D of 2026-09-25 found drifting.

**6.42 and everything before it has landed**, which is why the run starts here.

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
