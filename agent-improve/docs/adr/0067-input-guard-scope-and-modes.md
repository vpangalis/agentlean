# ADR-0067 — What the input guard screens for, how it answers, and how it runs without Content Safety

Status: ACCEPTED (founder, 2026-09-28)
Requirements: R20, T71, T72, T91, T92, T93, T94
Refines: ADR-0057 (input guard node). ADR-0057 stays in force for placement and fail-closed; this ADR adds scope, replies, limits and modes.

## Context

ADR-0057 placed a guard node at the front of the main graph and made it fail closed. It never said
what the guard screens for, and business.md held no security need at all. The build also added a
development exception that no ADR records. Two further facts surfaced in review:

- Azure OpenAI already filters every model call. By default it filters hate, sexual, violence and
  self-harm; Prompt Shields can be switched on as an optional filter. A refused call returns HTTP 400
  with code `content_filter`
  (https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/content-filter).
- Prompt Shields accepts at most 10,000 characters per prompt, and up to five documents totalling
  10,000 characters (https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview).

## Decision

**1. Scope: the guard screens for four threats, and nothing else.**

| Threat | Screened where | Check |
|---|---|---|
| A. Rewriting the coach's rules: overriding instructions, fake system or assistant turns, persona role-play, encoded instructions | Every Belt message | Fixed rules, then Prompt Shields user-prompt check |
| B. Hidden instructions in a file: text addressed to the AI, including text hidden by formatting, comments, hidden cells or sheets, or metadata | Every upload, before indexing or any model call | Prompt Shields document check, in chunks of at most 10,000 characters |
| C. Gaming the gate: text telling the grader or validator to pass | Covered by A and B | Additionally, all Belt answers and upload text reach every model (coach, planner, validator, grader) inside a labelled data block |
| D. Flooding | Every message and upload | Fixed limits (point 3) |

Not the guard's job, because blocking these at the door also blocks ordinary questions: other
cases' data (T79, T53, T73), system prompt disclosure (T73), harmful content (the Azure deployment
filter, T92), personal data (T87), and "write it for me" requests (coaching rules R1 and C3).

**2. The reply to a block uses no model.** Handing a manipulative message to a model, even to
suggest a rephrasing, gives the attack what it wants. The reply is assembled in code from:
- a fixed text per threat, from one message catalogue owned by the guard (`core/guard_messages.py`
  or a data file next to it; wording changed only by the founder);
- the element the Belt is working on, taken from the state;
- that element's sample answer from the phase's SKILL.md (the C3 sample), marked as a sample.

Example: "This message was blocked for security reasons: it reads like an instruction to change how
the coach works. You were working on **Business case**. Describe your situation instead, for
example: *'Invoice errors cost us about €40k a year in rework.'* (sample only)".

The same reply goes to every sender, whatever their role. Every block is recorded in `step_log`
with the signed-in person, time, threat and rule, which makes it part of the decision trail (R19),
readable by the project lead. There is no notification. The guard has no skill and no coaching
session, and the phase skills do not change.

**3. Limits.**

| Limit | Value | Over the limit |
|---|---|---|
| Message length | 10,000 characters (the Prompt Shields limit) | Refused with the limit named; the typed text stays in the box |
| Upload notice | above 5 MB | Accepted, with a notice: the coach reads only the text, so remove pictures and pages it doesn't need |
| Upload maximum | 25 MB | Refused with the same advice |
| Turns per person | 10 per minute | "Please wait a moment before sending the next message"; the text stays in the box |

**4. Azure filter refusals.** A model call refused with `content_filter` is never retried and
never sent to the fallback model (`ModelRetryMiddleware` and `ModelFallbackMiddleware` treat it as
non-retryable). The Belt gets a guidance reply built the same way as point 2, and the refusal goes to
`step_log`. Prompt Shields is also switched on, in block mode, in the Azure OpenAI deployment's
content filter, as a second layer for text that reaches a model without passing the guard (for
example retrieved manual chunks or tool results).

**5. Modes.**
- Strict is the default. Development mode applies only when it is set explicitly.
- Production start without Content Safety configured refuses to run (with T67).
- Configured but unreachable: block, in every mode (fail closed, ADR-0057).
- In development mode without Content Safety, the fixed rules run alone, and each skipped
  Prompt Shields check is recorded as `shield: skipped` in `step_log`.

## Consequences

- The guard's scope is testable. T71 and T72 carry the attack cases; T91 carries the benign cases
  that must pass: at least 50 in the eval set (Lean vocabulary such as "attack the root cause",
  "kill the waste", "execute the pilot", "bypass the approval step", "ignore the outliers", a
  teammate called Dan, German answers, pasted tables, questions about other projects).
- A production misconfiguration shows up at start-up instead of as a silently weaker guard.
- Long uploads cost one Prompt Shields call per 10,000 characters.
- ARCHITECTURE.md §1 (Overview) decisions row, §3.2 (node table) and the upload pipeline
  description change in place.

## Rejected

- **A model-written rephrasing suggestion.** It feeds the blocked text to a model.
- **A security skill or coaching session for the guard.** The guard is deterministic and not an
  agent (the founder's concept).
- **Blocking "other cases" or "system prompt" wording at the door.** It blocks ordinary questions;
  output checks cover the risk.
- **Relying only on the Azure deployment filter.** It gives no product-specific guidance reply, no
  decision-trail record, and does not screen uploads before indexing.
