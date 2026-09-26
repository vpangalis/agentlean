# Architecture decision records

> **PROPOSED — not ratified.** Drafted by the architecture sort (founder, 2026-09-26) from
> [ARCHITECTURE.md](../../ARCHITECTURE.md), which is unchanged. Each record cites the section
> it came from. Nothing here overrides ARCHITECTURE.md until the founder rules.

Format: Nygard — title, status, context, decision, consequences. A record is never
deleted: a replaced decision is marked `SUPERSEDED by NNNN` and kept.

The measurable qualities these decisions serve are the technical requirements T1–Tn in
[platform.md](../requirements/platform.md).

| # | Decision | Status |
|---|---|---|
| [0001](0001-coaching-move-decided-in-code.md) | The coaching move is decided in code, never by a model | PROPOSED |
| [0002](0002-value-stored-only-after-confirmation.md) | A value is stored only after the Belt confirms it | PROPOSED |
| [0003](0003-coach-input-in-labelled-sections.md) | The coach's input is labelled sections, one job each | PROPOSED |
| [0004](0004-define-thirteen-elements.md) | Define coaches thirteen elements, all gate-required | PROPOSED |
| [0005](0005-prompt-facts-at-the-top.md) | The coach's prompt puts facts at the top | SUPERSEDED by 0003 |
| [0006](0006-define-twelve-fields-option-a.md) | Define has twelve fields, all gate-required (Option A) | SUPERSEDED by 0004 |
| [0007](0007-validation-layer-is-planner-judgment.md) | The answer check is the planner's judgment, naming the failed criterion | PROPOSED |
| [0008](0008-define-gate-is-a-report.md) | The Define gate is a readable report, approved or rejected at a pause | PROPOSED |
| [0009](0009-one-resume-route.md) | One resume route: POST /gate/decision | PROPOSED |
| [0010](0010-define-rubric-layer-2d.md) | The Define rubric is validation layer 2d | PROPOSED |
| [0011](0011-gate-write-in-final-node.md) | The gate write moves into the graph's final node | PROPOSED |
| [0012](0012-hooks-test-the-staged-tree.md) | Commit hooks test what is staged, not the working tree | PROPOSED |
| [0013](0013-guard-binds-every-code-commit.md) | Types, tests and feature landing bind every code commit | PROPOSED |
| [0014](0014-live-call-budget.md) | Live model calls are budgeted per prompt | PROPOSED |
| [0015](0015-two-level-state.md) | Two levels of state: a routing supervisor and one state per phase | PROPOSED |
| [0016](0016-captured-fields-are-strings.md) | Every captured field is a string | PROPOSED |
| [0017](0017-checkpointer-on-the-parent-only.md) | The checkpointer and the store attach to the parent graph only | PROPOSED |
| [0018](0018-azure-blob-checkpointer.md) | A custom Azure Blob checkpointer with conditional writes | PROPOSED |
| [0019](0019-store-for-cross-phase-artifacts.md) | The Store carries artifacts across phases | PROPOSED |
| [0020](0020-step-log-audit-trail.md) | `step_log` is the audit trail, with deterministic keys | PROPOSED |
| [0021](0021-one-compiled-graph.md) | One compiled graph is the only runtime path | PROPOSED |
| [0022](0022-five-node-phase-cycle.md) | A phase subgraph is a cycle of five nodes | PROPOSED |
| [0023](0023-routing-static-or-command.md) | A node routes by static edges or by `Command`, never both | PROPOSED |
| [0024](0024-thread-id-is-the-case.md) | The thread id is the case id | PROPOSED |
| [0025](0025-planner-executor-split.md) | Planner and executor are separate nodes, joined by a structured plan | PROPOSED |
| [0026](0026-create-agent-with-middleware.md) | The executor is `create_agent` with middleware | PROPOSED |
| [0027](0027-middleware-stack.md) | A fixed middleware stack around the coach | PROPOSED |
| [0028](0028-coaching-response-schema.md) | `CoachingResponse` is the executor's only output schema | PROPOSED |
| [0029](0029-model-roles-and-tiers.md) | Model roles and tiers are owned by one factory | PROPOSED |
| [0030](0030-three-indexes.md) | Three search indexes with separate purposes | PROPOSED |
| [0031](0031-multi-query-rrf.md) | Multi-query retrieval fused by Reciprocal Rank Fusion | PROPOSED |
| [0032](0032-hop-cap-counted-in-executor.md) | Multi-hop retrieval is capped by a count in the executor | PROPOSED |
| [0033](0033-retrieval-failure-semantics.md) | Retrieval failures are errors, not empty results | PROPOSED |
| [0034](0034-no-mcp-data-channel.md) | No MCP: tools are in-process, with a small universal set | PROPOSED |
| [0035](0035-computation-tools-per-phase.md) | Computation tools are pure, bound per phase, under a ceiling | PROPOSED |
| [0036](0036-phase-skills.md) | Phase knowledge lives in SKILL.md files, disclosed progressively | PROPOSED |
| [0037](0037-gate-review-and-apply.md) | The gate is two nodes: review pauses, apply writes | PROPOSED |
| [0038](0038-checkpoint-commits-after-approval.md) | Nothing is committed to the case before approval | PROPOSED |
| [0039](0039-four-layer-validation.md) | A four-layer validation stack with one shared cap of three | PROPOSED |
| [0040](0040-two-tiers-and-warning.md) | Two tiers of field, and a warning verdict | PROPOSED |
| [0041](0041-two-graders.md) | Two graders: coherence and coaching quality | PROPOSED |
| [0042](0042-contradiction-and-reapproval.md) | A contradiction of an approved value triggers re-approval | PROPOSED |
| [0043](0043-native-reliability-primitives.md) | Reliability uses LangGraph's primitives, not a hand-written saga | PROPOSED |
| [0044](0044-fallback-chain-and-breakers.md) | A four-level fallback chain and three-state circuit breakers | PROPOSED |
| [0045](0045-geo-redundancy-deferred.md) | Geographic redundancy is deferred | PROPOSED |
| [0046](0046-disconnect-abandons.md) | A dropped client abandons the turn | PROPOSED |
| [0047](0047-one-error-schema.md) | One structured error schema for every external failure | PROPOSED |
| [0048](0048-tracing-is-a-switch.md) | Tracing is a switch, required in production | PROPOSED |
| [0049](0049-eval-gates-release.md) | The evaluation suite gates a release | PROPOSED |
| [0050](0050-config-fails-fast.md) | Configuration fails fast at start-up | PROPOSED |
| [0051](0051-facts-have-one-owner.md) | Facts have one owner; documents cite, never copy | PROPOSED |
| [0052](0052-commit-gates-govern.md) | The commit gates govern; rule files are advisory | PROPOSED |
| [0053](0053-phase-is-atomic.md) | A phase is one atomic unit: schema, validator, skill | PROPOSED |
| [0054](0054-head-is-truth.md) | The tree at HEAD is the only source of truth | PROPOSED |
| [0055](0055-eu-ai-act-posture.md) | EU AI Act posture: a limited-risk assistant with a human decision | PROPOSED |
| [0056](0056-dora-risk-register.md) | Operational risks are kept in a DORA-structured register | PROPOSED |
