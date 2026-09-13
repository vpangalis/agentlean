---
name: add-computation-tool
description: |
  Add a per-phase computation tool — a statistical or Lean Six Sigma calculation the
  coach can call. Use when a phase needs a calculation it cannot currently make.
  Carries the registry entry, the phase binding, the per-executor cap the addition can
  breach, the seven-step coaching pattern the tool must be taught inside, and the
  rubric criterion that makes it count at the gate.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash, Edit
version: "1.0"
---

# add-computation-tool

## The cap is the first question, not the last

**A phase executor binds at most 16 tools.** The universal set, plus the phase's
computation tools, plus `load_skill`, must fit — and Measure sits nearest the
edge. Count before you design:

```bash
python .claude/hooks/verify_built.py | grep -iE "tool bind|computation"
```

If the addition breaches the cap, **the answer is a placement, not a higher
ceiling**: which tool leaves, or which phase it belongs to instead.

## The five places

| Where | What |
|---|---|
| `backend/knowledge/computation.py` | the function, and its registry entry |
| `COMPUTATION_TOOLS_BY_PHASE` | which phases may call it |
| `backend/knowledge/tool_args.py` | a Pydantic args schema; never bare kwargs |
| the phase SKILL.md | the seven-step block that teaches it |
| the rubric | the criterion that makes using it count at the gate |

## The docstring is load-bearing

§5.4 — the model chooses a tool by reading its docstring. It states what the
tool computes, when a coach should reach for it, and what it needs. It is not a
restatement of the signature. **A tool the coach never calls is usually a tool
whose docstring never said when to.**

## A tool is taught, not just bound

A computation the Belt does not understand is a number they cannot defend at a
gate. The phase SKILL.md teaches it in the ratified shape: explain the statistic
in plain language, show a worked example, say what data it needs and in what
shape, run it, read the result back, state what it does and does not prove, then
ask the Belt what they conclude.

## Never

- Never parameterise the computation tools into mode-argument groups. One tool,
  one calculation, one docstring the model can choose on
- Never return a bare number; return the value with what it means
- Never bind tools onto the model directly. They go to `create_agent(tools=)`,
  or the entire middleware stack is bypassed silently (§4.4)

## After

```bash
cd agent-improve && .venv/Scripts/python.exe -m pytest backend/tests -q
python .claude/hooks/verify_built.py
```

Both counts are BUILT markers. If a marker disagrees with the tree, the tree
moved and the document is now a claim — resolve which, and never just
re-baseline.
