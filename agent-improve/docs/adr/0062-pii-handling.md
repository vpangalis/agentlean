# ADR-0062 — Personal data in uploads and messages is detected and handled before a model sees it

Status: ACCEPTED (founder, 2026-09-28) · Requirement: T87

## Context
Belts upload process documents and data files that can contain e-mail addresses, phone numbers,
account numbers or customer names. LangChain 1.x provides `PIIMiddleware` (types, strategy
redact / mask / hash / block, custom detectors, `apply_to_input`). Define legitimately needs the
names of team members, the Champion and the process owner.

## Decision
1. Uploads: the upload pipeline detects e-mail, phone, IBAN / account and card numbers and masks
   them in the text that is interpreted and indexed; the original file stays in Blob for the Belt.
2. Coach input: `PIIMiddleware` on the executor masks the same types in tool results
   (`rag_lookup_evidence`, `load_evidence_series`), not in the Belt's own messages.
3. Person names are not masked: the team element needs them. Customer names inside evidence are
   masked only when the founder switches that on per case.
4. Every masking is recorded in `step_log` with type and count, never the value.

## Rejected
Blocking uploads with personal data (Belts would stop uploading); masking all names (breaks the
team element).
