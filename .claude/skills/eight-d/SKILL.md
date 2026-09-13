---
name: eight-d
description: |
  Work a defect, a modification or an adaptation as an 8D before proposing a fix.
  Carries the nine disciplines, the six the commit gate requires, the three clauses
  that carry the weight, and a worked example including its empty disciplines. Use
  BEFORE proposing any fix, and when writing the body of a commit whose subject is a
  fix or names a registered defect — rule 6 of the commit-msg guard blocks it
  otherwise. Also use when a report says what broke and not why nothing caught it.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash
version: "1.0"
---

# eight-d

**Founder ruling 2026-09-11, CLAUDE.md §20.** Every defect, modification or
adaptation is worked as an 8D **before a fix is proposed**. The 8D is the work,
not the write-up: it is what you do first, and the commit body is its record.

*Moved out of the root file on 2026-09-13 (brief step 10). The rules bind
always and stay there in seven lines; this reference is what you read while
working one, and it loads when you ask for it.*

### 20.1 — The nine disciplines

> **MOVES TO THE `eight-d` SKILL AT STEP 10.** This table and §20.4's below are
> the reference a person reads while working a defect, which is what a skill is
> for — loaded on invocation rather than carried in every session. They stay
> here until that skill exists, because the gate in §20.4 is live now.

| | Discipline | What it answers |
|---|---|---|
| **D0** | **prepare** | Is there a reproduction that is not a story — the request, the case, the build, re-runnable |
| **D1** | **team** | Who is working it, and who rules on what |
| **D2** | **describe, with IS / IS-NOT** | What happens, where, since when, how you know — **and the nearest thing it is NOT**, which is what bounds it |
| **D3** | **interim containment, WITH its removal condition** | What protects the Belt while the real fix is built, and what retires it |
| **D4** | **root cause, in TWO parts** | **Occurrence** — why it happened. **Escape** — why nothing detected it |
| **D5** | **chosen permanent fix** | Which change, and why that one rather than the others costed |
| **D6** | **verification** | What proves the fix works — and what would have failed before it |
| **D7** | **prevention of recurrence** | What stops the **class**, not this instance. Usually a check, a schema, or a gate |
| **D8** | **closure conditions** | What has to be true to call it closed — here, the step's Done-when |

### 20.4 — Enforced at the commit, as rule 6

`.claude/hooks/commit-msg-refactor-guard.py` blocks a fix commit whose body does
not answer the six.

| | |
|---|---|
| **Required labels** | `D2 IS:` · `D2 IS-NOT:` · `D4 OCCURRENCE:` · `D4 ESCAPE:` · `D5 FIX:` · `D7 PREVENT:` — each starting a line, each followed by a colon |
| **Why these six and not all nine** | D6 is the step's `Verify` and guard rules 3 and 4 already run it; D8 is its Done-when; D0 and D1 are process the commit does not need to carry |
| **What counts as a fix** | the subject's type is `fix` or `hotfix`; **or** the subject names a registered defect (`G-49`, `F-15`, `WATCH 26`); **or** the body already carries a `D<n>` label |
| **Declining on the record** | `8D: NOT A FIX — <why>` — valid only for the middle trigger. It cannot exempt a `fix(` subject or a body that already carries D-labels |
| **What it checks** | that each discipline is ANSWERED, never that the answer is right. An empty one passes as `NONE — <reason>`; bare `NONE` does not |


## The three clauses that carry the weight

**D4 IS NOT COMPLETE WITH ONLY AN OCCURRENCE CAUSE.** *"Why did nothing detect
this"* is a different question from *"why did it happen"*, and it is the
expensive one. An occurrence cause with no escape cause is the shape that lets
the same CLASS return through the same blind spot.

**D3 RECORDS ITS OWN REMOVAL CONDITION, OR IT BECOMES PERMANENT.** A containment
with no stated retirement is a workaround that outlives the memory of why it
exists.

**AN EMPTY DISCIPLINE IS A FINDING AND SAYS SO.** Write `NONE — <why it is
empty>`. An omitted discipline reads as forgotten; an empty one that explains
itself is a result. Bare `NONE` does not pass the gate.

## Worked example — G-49, empty disciplines included

The value of this example is D3, D5 and D7, which are all empty and all say why.

| | G-49 — the executor ignores the tool its planner names |
|---|---|
| **D2 IS** | A Define turn with an unread upload issues 18 evidence searches across 3 multi-query calls and never calls the tool the plan names |
| **D2 IS-NOT** | **Not the hop cap** — §3.7 fired correctly. **Not retrieval quality** — the searches returned documents |
| **D3** | **NONE — and that is the finding.** Nothing protects the Belt today; the same question still times out |
| **D4 OCCURRENCE** | The plan has no transport into the model's request. The agent is invoked with `{"messages": prior}` and the plan reaches no channel the model reads |
| **D4 ESCAPE** | **No test asserted what the model RECEIVES.** Every executor test stubs `create_agent` and asserts on what the node returns |
| **D5** | **NOT CHOSEN — the founder's ruling.** Four transports costed; the choice is a decision, not a default |
| **D7** | **NONE — nothing here stops the class.** The class is *a decision that is recorded and never delivered* |

## How to use this

1. Reproduce first. D0 is a re-runnable reproduction, not a story.
2. Write D2 IS and D2 IS-NOT before looking for a cause — IS-NOT is what bounds
   the search.
3. Answer D4 in both halves. If the escape cause is *"nothing checks this"*,
   that is the finding and D7 is a check.
4. Write the body. The six labels below must each start a line and carry a
   colon; the guard checks presence, never correctness.

```
D2 IS:          D2 IS-NOT:      D4 OCCURRENCE:
D4 ESCAPE:      D5 FIX:         D7 PREVENT:
```

**Declining on the record.** If the subject names a registered defect but the
commit fixes nothing — a registration, a schedule, a verbatim move — write
`8D: NOT A FIX — <why>`. It cannot exempt a `fix(` subject or a body that
already carries D-labels.

## Checking your own body before you commit

```bash
python .claude/hooks/commit-msg-refactor-guard.py <path-to-message-file>
```

Run it on the message file before committing. It reports which disciplines are
missing and why each is required, and it is the same code that will block the
commit.
