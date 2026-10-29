# ADR-0095: A process description, file or picture becomes the SIPOC draft — one plain SIPOC tool, called by code on an upload and offered to the coach at element 12

Status: PROPOSED (Claude Code, 2026-10-16; revised 2026-10-29 from the founder's rulings on the wave-3 report, item 1, and the 22:00 follow-up; for ruling)
Requirements: R10 (amendment ACCEPTED 2026-10-29), R17 (amended 2026-10-29), R18, W5
Extends: ADR-0074, ADR-0085 and ADR-0094 (to a structured SIPOC value and to pictures); ADR-0069 and ADR-0115 (tools per turn)
Depends on: ADR-0078 (steps with performance), ADR-0088 (durations), ADR-0104 (the upload interpretation binds structured output)

## Decision

1. **One ask at element 12:** "Upload any process file or picture, or describe the process."
   - Read: Word, PDF, plain text, Excel or CSV, and pictures (PNG, JPG, WebP: a whiteboard photo, a diagram
     screenshot).
   - Visio, BPMN and PowerPoint: the reply asks for a PDF or a picture of the map. No reader for them now.
2. **One plain SIPOC tool** — a function with no prompt loop of its own.
   - It makes one structured reading call, which returns the SIPOC fields: suppliers, inputs, process steps (with
     any times and problems given), outputs, customers and process metrics.
   - Text is read through the existing extraction role. A picture is read through the existing vision role in that
     same single call, sent as its true type.
   - Only the output schema is new: no new model role and no new prompt file.
3. **Code, not the model, finds the gaps and checks the numbers.**
   - The checks: the six columns; four to eight steps; units, shortest ≤ average ≤ longest, and the step sum against
     the lead time (`duration_questions`).
   - Code draws the flow with every gap marked.
   - The tool returns the draft and its gaps. Nothing is stored before Confirm (W5).
4. **Who calls it.** Both callers use the same function.
   - On an upload at element 12, code calls it every time. It is that upload's one interpretation call (ADR-0074):
     no model decision and no extra round trip.
   - The coach is offered it only at element 12 (the turn-tools layer), and may call it on a typed description or
     on the answer to a gap. Other elements carry no tokens for it.
5. **Only the gaps are asked.**
   - R-G's four parts become the gap questions, asked only when missing. A full answer to the one ask gets no
     further question.
   - Times, how often and problems are optional (R17 amended). The coach asks: "Do you know roughly how long each
     step takes? If not, leave it — Measure will measure it." "Leave it" counts as answered.
6. **The read-back and Gate F are drawn from the same structured value.** The draft held pending is what Confirm
   stores.
7. **A file that does not describe a process** gets a plain reply asking for a description or a map.
8. **`read_upload` opens pictures** (ADR-0115's tool), for a picture the Belt names later.

## Consequences

- Element 12's block in the Define skill shrinks to three sentences: call the tool with what the Belt gave; ask only
  the gaps it returns; the times question. The four-part script and the gap-finding text leave the skill; the gap
  questions live in code with the tool.
- Cost: one reading call per upload or description.
- On a typed description the coach's call adds a round trip: judgment, coach → tool, the tool's reading call, coach
  reply, grader. That is five calls, against today's SIPOC read-back of 23–35 s and the node's 40 s limit.

## Rejected

- A new graph node, subgraph or subagent for the SIPOC (founder rule, 2026-10-29: new capability comes as tools or
  skills).
- A second model call per upload.
- A Visio reader now.
- A new model role or prompt file.

## Tests

- End to end:
  - a Word description;
  - a picture;
  - a typed description;
  - a file that is not a process;
  - Confirm with "leave it" for the times.
- Live: a real whiteboard photo and a diagram screenshot. Then the founder walks element 12.
