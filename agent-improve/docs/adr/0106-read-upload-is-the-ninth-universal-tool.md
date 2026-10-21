# ADR-0106: read_upload(blob_path) is the ninth universal tool

Status: ACCEPTED (founder and Desktop, 2026-10-21 evening; drafted by Claude Code from the ruling)
Requirements: R1; DEF-057 (G-82, G-49, G-63), DEF-110
Depends on: ADR-0069 "Answer turns bind no tools" (the turn types); ruling 3 (evidence and artefact are two buckets)

## Context

The coach must read an uploaded document and quote a line from it (DEF-057, e.g. an uploaded process map). The probe
of 2026-10-21 (`test_define_e2e.py::test_probe_def057_what_rag_lookup_evidence_gives_the_coach`) showed that
`rag_lookup_evidence` returns an evidence upload's whole indexed text, but searches evidence only: a process map is an
artefact (`upload/classifier.ARTEFACT_PURPOSES`), so the coach cannot reach it at all. `.claude/rules/tools.md` §5.2
asks for this review before a ninth universal tool.

## Decision

1. **`read_upload(blob_path)` is the ninth universal tool.**
2. It reads only files of the current case.
3. It returns the file's text, labelled evidence or artefact, capped in length.
4. It is built like `load_evidence_series`: the text is re-read from the case's own blob, nothing is stored.
5. It is offered on upload and teaching turns only (ADR-0069's turn types).

## Notes

Note (founder, 2026-10-21): the 16-tool ceiling counts the tools ONE model call offers, per turn type (ADR-0069) — "never offer more than 16 tools in one model call" replaces "never exceed 16 tools on a phase executor" in .claude/rules/tools.md. Reason: the limit protects tool choice, which depends on what one call offers; with read_upload Measure registers 17 (eight universal ratified, nine with this one, plus eight computation tools), and no turn type offers more than six.
