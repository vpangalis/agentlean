# ADR-0061 — An offline evaluation set built from real failures

Status: ACCEPTED (founder, 2026-09-28) · Requirement: T86 · Serves: T50, T75, T85

## Context
T50 blocks a release on a regression, but there is nothing to measure a regression against.
Anthropic's eval guidance: start with 20–50 tasks drawn from real failures, combine code-based,
model-based and human grading, read the transcripts, and measure consistency with pass^k for
customer-facing behaviour.

## Decision
1. Tasks live in the repo (`evals/define/*.jsonl`): one task = a starting case state, the Belt's
   message(s), and what must be true afterwards. Sources: run-through transcripts, defects,
   the 13 elements' acceptance criteria, prompt-attack cases (T75).
2. Graders: code first (the right move, the value stored or not stored, the criterion named);
   then the model rubric (`COACHING_QUALITY_RUBRIC`) at temperature 0.1; a human reads a sample.
3. Each task runs k = 3 times; the reported metric is pass^3 (all three pass).
4. Runs are deliberate (live calls, within the live-call budget): before a release, and on
   changes to prompts, skills, the graph or model settings. LangSmith holds the development copy;
   the repo files are the source of truth, so the set works inside the intranet.
5. Retrieval tasks (T85) record hit rate at top-10 and top-20.

## Rejected
Generated tasks without real failures behind them; model grading alone.
