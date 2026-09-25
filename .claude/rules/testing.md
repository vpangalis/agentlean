---
paths:
  - "agent-improve/backend/tests/**"
---
# §12 — Evaluation and regression testing

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 12. EVALUATION AND REGRESSION TESTING

### 12.1 — The eval suite is built alongside the refactor

Not before it. The suite becomes load-bearing when the coach, retrieval
tools, and grader are wired.

**The dataset is authored jointly, not generated.**

### 12.2 — Minimum viable suite

| Dimension | Requirement |
|---|---|
| Size | 20–30 examples, 4–6 per DMAIC phase |
| Categories | Realistic coaching turns · edge cases · tool-calling scenarios · failure/ambiguous cases · historical production data |
| Metrics | Accuracy (field extraction) · relevance · reasoning quality · tool usage · safety (no invented methodology) |
| Evaluator order | Deterministic ($0) → LLM-judge relevance (~$0.01) → LLM-judge reasoning (~$0.02) |
| **Regression threshold** | **Block release if any metric drops >10% from baseline** |
| Run frequency | Every commit touching system prompts, graph structure, or model config |

**Rubrics and the eval dataset are complementary, not duplicative** —
rubrics (§8.2) grade in production; the eval dataset tests the whole
system in CI.

### 12.3 — Structured errors

All external service failures use one schema, `AgentImproveError` in
`core/errors.py` — read its fields there.

`severity` is what lets the circuit breaker distinguish "retry" from
"stop trying"; `retry_recommendation` is what the fallback chain reads
to choose backoff strategy (§4.8).

