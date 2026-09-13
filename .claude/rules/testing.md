---
paths:
  - "agent-improve/backend/tests/**"
---
# §12 — Evaluation and regression testing

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 12. EVALUATION AND REGRESSION TESTING

### 12.1 — The eval suite is built alongside the refactor

Not before it. Establishing a baseline against the current system
would produce a baseline of "bad." The suite becomes load-bearing when
the coach, retrieval tools, and grader are wired — that is when output
quality changes. Infrastructure steps (graph structure, state schemas,
checkpointer) do not affect coaching quality.

**The dataset is authored jointly, not generated.** Coaching quality
judgments are domain judgments; a generated dataset measures agreement
with a model rather than correctness.

### 12.2 — Minimum viable suite

| Dimension | Requirement |
|---|---|
| Size | 20–30 examples, 4–6 per DMAIC phase |
| Categories | Realistic coaching turns · edge cases · tool-calling scenarios · failure/ambiguous cases · historical production data |
| Metrics | Accuracy (field extraction) · relevance · reasoning quality · tool usage · safety (no invented methodology) |
| Evaluator order | Deterministic ($0) → LLM-judge relevance (~$0.01) → LLM-judge reasoning (~$0.02) |
| **Regression threshold** | **Block release if any metric drops >10% from baseline** |
| Run frequency | Every commit touching system prompts, graph structure, or model config |

**Rubrics and the eval dataset are complementary, not duplicative.**
Rubrics (§8.2) define what good looks like *for the grader*, in
production, at every gate. The eval dataset tests whether the whole
system produces good outcomes, in CI, at every commit.

### 12.3 — Structured errors

All external service failures use one schema, in `core/errors.py`:

```python
class AgentImproveError(BaseModel):
    error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
    severity: str                # "transient" | "permanent"
    retry_recommendation: str    # "retry_after_backoff" | "do_not_retry" | …
    affected_identifier: str
    message: str
    timestamp: datetime
```

`severity` is what lets the circuit breaker distinguish "retry" from
"stop trying"; `retry_recommendation` is what the fallback chain reads
to choose backoff strategy (§4.8).

