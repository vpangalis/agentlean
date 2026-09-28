# ADR-0070 — Visuals drawn from the structured read-back

Status: ACCEPTED (founder, 2026-09-28)
Requirements: C1 and C2 (reports and visuals from confirmed values), R2 (teach before asking), W5 (uploads strengthen answers), T69 (at most 4 model calls per turn)
Refines: ADR-0069 (answer turns bind no tools; upload turns count as teaching turns). ADR-0069 stays in force; this ADR replaces its point 2 and adds points on upload turns and on how the tool restriction is built.

## Context

ADR-0069 point 2 said diagrams and templates shown after a Confirm are produced in code from the
stored values. The founder corrected it on 2026-09-28: the Belt should see the visual while the value
is still being read back, and the confirmed picture and the report picture must never differ.

## Decision

1. **Visuals.** On every read-back the coach returns its values in structured form, and the program
   draws the matching visual (baseline→target chart, 5W2H mind map, SIPOC diagram, etc.) in the same
   reply, marked "not yet confirmed". After Confirm the same visual is drawn from the stored values
   into the gate document. No AI call is spent on drawing. (C2, R2)
   The coach reply and the gate document use one and the same drawing function per visual, so the
   confirmed picture and the report picture can never differ. (C1, C2)
2. **Upload turns.** Recognising, parsing and screening the file are code; interpreting the fields,
   checking the process for correctness and the structured read-back are the AI's calls; the diagram
   is drawn by the program.
3. **The tool restriction** is built with LangChain's documented dynamic tool selection: a
   `wrap_model_call` middleware that sets `request.override(tools=[])` on answer turns (turn type
   decided in code from state), not a hand-built switch.
   Source: https://docs.langchain.com/oss/python/langchain/tools

## Verification

- The run-through checks that the read-back replies at elements 5, 7, 8 and 12 carry their visual,
  and that the gate document shows the same visuals.
