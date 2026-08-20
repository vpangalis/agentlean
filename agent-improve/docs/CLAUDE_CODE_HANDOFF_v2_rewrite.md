# Handoff: REFACTORING_AGENT_IMPROVE.md v2 Rewrite

**Paste this alongside CONTINUITY.md at the start of the session.** CONTINUITY.md
tells you where the project stands. This brief tells you what to do with the
output of today's review session (2026-08-19).

## Context

A full section-by-section review of `agent-improve/docs/REFACTORING_AGENT_IMPROVE.md`
was completed in Claude.ai chat. Every finding — contradictions, stale claims,
missing schema fields, corrected code examples — was logged in `DECISIONS.md`
and `REVIEW_DECISIONS.md`, not applied to the live document (that chat session
had no filesystem access). Your job is to reconcile that log into the actual
document and produce a genuinely rewritten v2.

## Task 1 — Audit first, read-only (per CLAUDE.md's own audit-first discipline)

Before writing anything:

1. Read `DECISIONS.md` and `REVIEW_DECISIONS.md` in full — today's session added
   roughly 15 new entries dated 2026-08-19 (search for that date). Build a list
   of every ratified fix: what section it touches, what the fix is.
2. Cross-reference each entry against the current text of
   `REFACTORING_AGENT_IMPROVE.md` — confirm it's still unapplied (it should be;
   nothing was written back this session), and confirm you understand the fix
   well enough to apply it without re-litigating the decision. If anything is
   genuinely ambiguous, flag it back to me rather than guessing.
3. Report the audit findings before writing anything — a list of what will
   change and where. I sign off before Task 2 starts.

**Known high-priority items to confirm are in your list** (not exhaustive —
verify against the actual logs, this is a sanity check, not the full set):

- `PhaseState` missing `hop_results` and `synthesis_output` fields (§18)
- §44's "Correct Implementation for Agent Improve" code block: wrong parent
  class name (`DMAICState` → must be `SupervisorState`), wrong cross-phase
  mechanism (shared key names → must be Store-mediated boundary mappers).
  This one matters — it's the block someone would copy as the reference
  implementation, and as written it contradicts §17/§19/§52a.
- `improve_evidence_index` missing `phase` and `uploaded_at` fields
- The Handler-Shaped Durability / disconnect-policy decision for Step 6
  (idempotency keys, Azure Blob lease, `step_log` deterministic keys instead
  of timestamps) — this is new scope for Step 6, not yet in the document at all
- Several "correction added at top of section, stale text below never updated"
  instances (§72, §74, §75, §77, §78 all had this pattern) — check each
  section's *entire* body agrees with its own stated conclusion, not just
  the summary box
- Citation/attribution fixes (Anthropic harness-design post scope, `BaseStore.search()`
  filter support, `langchain_classic` memory-class migration timing)

## Task 2 — Mechanical consistency sweep

This is the part that benefits from your filesystem access and doesn't need
architectural judgment, just thoroughness:

1. Every `class` definition and every `@tool`/function signature that appears
   more than once in the document — confirm all occurrences agree, or confirm
   divergent ones are clearly labeled as illustrative/superseded (the document
   has an established pattern of "here's the course version, here's what we
   corrected" — that's fine when labeled, not fine when not).
2. Cross-check every schema described in the document against the actual code
   in `agent-improve/backend` where it already exists — this is the check that
   couldn't be done from chat. Flag any place the document and the real
   codebase have drifted from each other, in either direction.
3. Field counts, cross-references (`§X`), and "N fields" claims — verify the
   arithmetic. Several stale counts were already caught this session (e.g. a
   "15 fields" header that should say "17"); there may be others uncaught.

## Task 3 — The Bible: v2 architecture reference, end to end

Once Tasks 1 and 2 are applied and clean, restructure into a single
comprehensive reference document — "the Bible." This is not a shortened or
condensed v1. Detail is the point.

- **What gets removed is narrative scaffolding, not substance.** No more
  "here's what the Edureka course taught, here's what we corrected and why."
  That reasoning trail did its job during the learning process; a reference
  document states the ratified design directly instead of re-deriving it in
  front of the reader every time. If specific provenance is worth preserving
  for history, it goes in `EDUCATIONAL.md` or a changelog appendix — not the
  main body.
- **What must NOT be removed:** field-level schema detail, function
  signatures, validation logic, the reasoning behind non-obvious decisions
  (e.g. why static edges vs `Command` routing, why the Store and not shared
  state keys), and every cross-check this session's review performed. If a
  section says "PhaseState has 17 fields," the Bible lists all 17, typed,
  with what writes them and what reads them — not a pointer elsewhere.
  Comprehensive and end-to-end means a reader should be able to build against
  this document alone, without needing to reconstruct anything from memory
  or from a different file.
- **One definition per concept, in one place**, not spread across many
  sections the way v1 ended up. `PhaseState`, `SupervisorState`, the
  `rag_lookup_*` tools, the checkpointer/store split — each gets a single
  canonical section, fully specified there; everything else cross-references
  it rather than re-declaring a partial or divergent copy.
- **Organize by what the document is *for*** — an end-to-end architecture
  reference someone builds against — rather than by the order concepts
  happened to get discovered in during the course. Propose a structure
  before writing the full thing: a section-by-section outline, confirmed
  with me, then written in full.
- **Do not seek sign-off yet — Task 3B is required before the Bible counts as done.**

## Task 3B — Trusted-source cross-check (required, not optional)

Before the Bible is presented for sign-off, every architectural and technical
claim in it must be checked against current authoritative sources — not
assumed correct because it was correct when originally written. This
directly extends what `/verify-current-version` and §45's Tier 1 source list
already do; use both as the starting point rather than reinventing the check.

- **Sources to check against, in priority order:** `anthropic.com/engineering`
  (the current post index, not just the Tier 1 list as of August 2026 — check
  whether anything newer has shipped since), `docs.langchain.com` /
  `reference.langchain.com` (LangChain/LangGraph API surface),
  `docs.langchain.com/langsmith` (LangSmith), and `github.com/langchain-ai/*`
  release notes and open issues for anything the Bible asserts as current
  behavior.
- **Check every claim that could have drifted**, not just the ones that felt
  uncertain when written: API signatures and parameter names (e.g.
  `SummarizationMiddleware`'s `trigger`/`keep`), deprecation status of
  anything referenced (`create_react_agent`, classic memory classes, etc.),
  version floors stated as requirements (e.g. "LangGraph 1.2.6 fixed X"),
  and any named GitHub issue cited as an open bug — confirm it's still open,
  not fixed since.
- **Produce a verification log alongside the Bible**, same shape as what
  this session's chat review used: claim → source checked → verdict
  (confirmed / corrected / now-stale-and-fixed). This log is a deliverable,
  not scratch work — it's what makes "bullet proof and cross-checked" mean
  something concrete rather than being an adjective.
- **Refresh the §45 Tier 1 list itself** while you're at it — check the
  `anthropic.com/engineering` index for anything published after the August
  2026 cutoff that list was built against.
- Anything the cross-check finds wrong gets corrected in the Bible directly
  before sign-off — this pass is a gate, not a follow-up appendix.

**Only once Task 3B is complete does the Bible go to me for sign-off.**

## Task 4 — The Refactoring Procedure (only after the Bible is approved)

A separate document. Its job: take the actual current state of the
`agent-improve` codebase — not the document, the real code — and produce a
concrete, ordered migration plan to bring it into compliance with the Bible.

- **Diff against reality first.** Read the actual current files in
  `agent-improve/backend` (and wherever else is relevant) and identify,
  concretely, where they already match the Bible, where they partially
  match, and where they don't exist yet.
- **Every step traces to a specific Bible section.** No step should exist
  that isn't implementing or correcting something the Bible actually
  specifies — this procedure is not a place to introduce new design
  decisions.
- **Every step has a verification method.** State how you'll know the step
  succeeded before moving to the next one — a test, a smoke check, a
  specific behavior to confirm. "Bullet proof and cross-checked" means this
  isn't a checklist of intentions, it's a sequence where each step is
  provably done before the next starts.
- **Respect and reconcile with the existing step numbering** (Step 3.1
  onward, per `CONTINUITY.md`) rather than inventing a parallel numbering
  scheme — either the procedure extends that sequence or explicitly
  supersedes it with a stated reason.
- Order matters: dependencies between steps (e.g. schema changes before the
  code that reads the new fields) should be explicit, not assumed.

## Boundaries

- Don't make new architectural decisions unilaterally — everything in Task 1
  is already ratified; anything genuinely new that comes up during Tasks 2/3
  gets flagged back, not decided silently.
- Minimum footprint, staged by name, no `git add -A` — per CLAUDE.md.
- This is a documentation task. If it surfaces something that implies an
  actual code change is needed (not just a doc fix), flag it — don't fix code
  as a side effect of a doc rewrite.
