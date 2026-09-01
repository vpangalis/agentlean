# Instruction: convert AGENTIC_ARCHITECTURE_REFERENCE.md to the SDD spec-layer structure

Read `agent-improve/docs/SPEC_LAYER_GUIDE.md` in full first — it is the governing
document for this work. It defines the target structure, the three-layer entry
template (SIPOC + EARS + selective AI-ACT flag), the compliance/risk layer, the
governance rules, and the two calibrated reference samples. Everything below
implements it.

## Scope of THIS task: mechanical restructure + scaffolding + gap-marking.
NOT designing missing pieces. Where a definition is missing or too thin to meet
the rebuild test, you MARK it as a labeled gap — you do NOT invent it. The
founder and I review gaps together, one at a time, AFTER this conversion lands.

## What to do

1. **Add a new Part to `AGENTIC_ARCHITECTURE_REFERENCE.md` — the SPECIFICATION
   layer.** One document, not a separate file (SSOT — separate files re-create
   drift). Position it so the architecture Parts (why) precede the spec Part
   (how), per the volatility-separation rule in the guide.

2. **Preamble of the spec Part:** transcribe the two calibrated samples
   (`SupervisorState` for the class template, `phase_executor` for the
   function template) VERBATIM as the reference examples, exactly as approved
   in the 2026-08-23 conversation / reproduced in the guide. These define the
   format; do not paraphrase them.

3. **Convert existing definitions into spec entries** to the three-layer
   template:
   - Every class currently defined in an architecture section (SupervisorState
     §5, PhaseState §6, CoachingPlan §17, CoachingResponse §20, the five
     {Phase}Output §40, AzureBlobStore §52-equiv, etc.) → a canonical spec
     entry in the spec Part, in the class template shape.
   - Every function/node currently described (the five phase-subgraph nodes,
     the rag_lookup_* functions, check_gate_status, the input/output mappers,
     etc.) → a spec entry in the function template shape (SIPOC + EARS table +
     AI-ACT flag IF it is a high-risk surface).
   - **Selective flagging:** AI-ACT flags ONLY on high-risk-surface functions
     (coaching output, gate approval, anything that could feed a
     competence/employment/assessment decision). Pure orchestration/state/
     utility functions get NO flag. When unsure whether something is a
     high-risk surface, mark it `AI-ACT-REVIEW: uncertain` rather than
     guessing either way.

4. **Strip the now-redundant definitions from architecture sections and point
   them at the spec entry.** §5 keeps its *reasoning* (why seven fields, why the
   four were removed) but its field-definition table moves to / is owned by the
   spec entry, with §5 referencing it. Define-once rule: a
   schema/signature defined in the spec Part must not be re-defined in an
   architecture section.

5. **Scaffold the Compliance & Risk Part** (new dedicated Part) per guide §4:
   - EU AI Act compliance posture (the verified deadlines, the eight-obligation
     mapping table, the honest "classification depends on deployment" note).
   - The DORA-structured risk register table with its columns. Populate it with
     one row per AI-ACT-flagged function created in step 3. Each row's Risk ID
     traces to the function + behavior IDs it aggregates.

6. **Add the new trusted sources** (guide §5) to §55 / Appendix C as Tier 1 for
   compliance, with the compliance-source discipline note.

7. **Add the governance rules** (guide §6) — spec-before-code, flag-is-canonical,
   SIPOC cross-check, define-once, selective-flagging — to the governance Part,
   each with its stated check.

8. **Mark every gap explicitly.** Where an existing description is too thin to
   rebuild from, or a piece is missing entirely, insert a labeled placeholder:
   `SPEC-GAP: <what's missing> — to be designed with founder`. Do NOT fill it.
   The known big one: the **Level 2 (subgraph-internal) Command routing** —
   §13 draws it, §15 states the rule, but no routing code exists. Mark it
   `SPEC-GAP: Level 2 Command routing — to be designed` and list the three
   decision points from guide §9. There will be others; mark them all.

## Audit-first — REQUIRED

This restructures a signed-off document. Before rewriting ANYTHING, produce and
show me a conversion PLAN:
- Which architecture sections' definitions move into the spec Part, and what
  each spec entry will be named.
- The full list of spec entries you'll create (classes and functions), with
  which ones you intend to AI-ACT-flag and which you'll mark
  `AI-ACT-REVIEW: uncertain`.
- The complete list of `SPEC-GAP` placeholders you'll insert (this is the list
  the founder and I will work through together).
- Confirmation that no architecture *reasoning* is lost — only definitions
  move; the "why" prose stays and gains a reference to the spec entry.

I confirm the plan, THEN you execute. Route the whole thing through §56 (it
changes ratified sections). Apply to BOTH the root reference and the
`agent-improve/ARCHITECTURE.md` copy, and confirm they match on the changed
Parts after. Version bump and change-log entry.

## What this task must NOT do
- Must not invent any missing definition or routing logic — mark as SPEC-GAP.
- Must not touch code (this is a documentation restructure).
- Must not resolve the gate-rejection behavior or the Level 2 routing — those
  are founder-review gaps.
- Must not remove architectural reasoning — only relocate definitions.
