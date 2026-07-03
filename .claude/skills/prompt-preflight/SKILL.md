---
name: prompt-preflight
description: |
  Assemble the preflight block that must sit at the top of every Claude Code
  implementation prompt for the AgentLean v2.2 refactor. The preflight block
  contains current git HEAD, current refactor step from agent-improve/ARCHITECTURE.md
  §15, applicable CLAUDE.md rule numbers for the files being modified, current
  state hash of those files, and the target state description. Fire this skill
  BEFORE generating ANY Claude Code prompt, WHENEVER the prompt will modify
  files in agent-improve/, agent-resolve/, agent-flow/, or the .claude/
  scaffold. If the skill cannot determine any required field, it refuses to
  produce a preflight block. Fire this skill deliberately — it is a discipline
  checkpoint before Claude Code executes anything.
disable-model-invocation: true
allowed-tools: Read, Grep, Bash
version: "0.1"
---

# /prompt-preflight

## Purpose

You are being invoked to assemble a PREFLIGHT BLOCK that must sit at the top of
a Claude Code implementation prompt. The user is about to generate a prompt for
Claude Code (in another window / another workflow) that will modify files in
this repository. The preflight block ensures Claude Code executes against the
current, verified state — not against stale assumptions.

If the preflight block cannot be assembled (missing information, contradictory
state), you must refuse to produce it and tell the user what is missing. Do
not fabricate.

## What to ask the user

If the user has not already stated it, ask them these questions in one turn:

  "1. Which file(s) will the Claude Code prompt modify? (relative paths)
   2. What is the target state — one sentence, prose, no code?
   3. Is this the start of a new refactor step from ARCHITECTURE.md §15,
      or a follow-on within a step already in progress?"

Do not proceed without concrete answers to all three.

## What to gather

For the preflight block, collect:

### 1. Current git state

Run:
  git rev-parse HEAD
  git rev-parse --abbrev-ref HEAD
  git status --short

If the working tree is dirty (git status --short returns any lines that are
not just untracked files matching common patterns like _Artifacts/, .bak,
_Claude_chat_Prompts/), warn the user in the preflight block. A dirty tree
means Claude Code will layer changes on top of uncommitted work, which the
audit-first discipline is meant to prevent.

### 2. Current refactor step

Read agent-improve/ARCHITECTURE.md (path is relative to monorepo root).
This is the per-agent architecture doc — governance is not at the monorepo
root.

If missing, refuse to produce the preflight block with reason "architecture
doc not found at agent-improve/ARCHITECTURE.md".

- Last completed step: derive from git log, not from doc markers.
    git log --oneline --grep='^refactor(arch-v2):' -n 20
  Parse each commit subject with regex:
    r'refactor\(arch-v2\):\s*(?:step\s+|commit\s+)?(\d+\.\d+)'
  Extract all matched X.Y values. Compare using tuple comparison (split on
  ".", cast each component to int, compare tuples). Take the highest as the
  last completed step.

- Next step: parse agent-improve/ARCHITECTURE.md §15 for lines matching
    r'\*\*Commit (\d+\.\d+)\*\*'
  Take the lowest X.Y strictly greater than the last completed step.

- If parsing fails, report last completed from git and mark next as
  "undetermined (inspect §15 manually)".

- If the user's task is outside the §15 migration sequence (e.g. a bugfix,
  a documentation edit, a scaffold amendment), flag it — the preflight
  block should still be produced, but with an explicit "OUT OF SEQUENCE"
  marker so it's obvious in the eventual Claude Code prompt that this
  work is not part of the refactor.

### 3. Applicable CLAUDE.md rule numbers

Read agent-improve/CLAUDE.md (or agent-resolve/CLAUDE.md if the modified
files are under agent-resolve/). Use Grep to search efficiently for rule
numbers matching the modified files.

Based on the file(s) being modified, identify which CLAUDE.md rules apply:

  - Files under agent-improve/backend/core/     → §1, §2, §4
  - Files under agent-improve/backend/phases/   → §3, §4, §5, §6
  - Files under agent-improve/backend/knowledge/ → §5, §7
  - Files under agent-improve/backend/storage/  → §8
  - Files under agent-improve/backend/gateway/  → §1 (esp §1.5), §3
  - Files under agent-improve/backend/ containing prompts → §6
  - Files under .claude/                        → §15 (development-time governance — expected in v2.2)
  - New Pydantic schema files                   → §2, §5.3

List the specific rule numbers, not just section headers. If the file path
does not map to any of these, note it and ask the user to specify which
rules apply.

### 4. Current state hash

For each file being modified, compute:

  Using Bash: python -c "import hashlib; print(hashlib.sha256(open('<path>', 'rb').read()).hexdigest())"

  (Use `python`, not `python3` — this Windows venv provides `python`.)

If a file does not yet exist (new file), record "new file (does not yet exist)".

### 5. Target state description

Take the user's one-sentence target state and include it verbatim.

## The preflight block format

Output plain text, exactly this format, ready to paste at the top of the
Claude Code prompt:

  ── PROMPT PREFLIGHT — do not modify below ──
  Generated: <ISO timestamp>
  Git HEAD: <sha>
  Branch: <name>
  Working tree: [clean | dirty — <count> files uncommitted]
  agent-improve/ARCHITECTURE.md §15 — last completed step: <e.g. 2.2>
  agent-improve/ARCHITECTURE.md §15 — next step: <e.g. 3.1>
  This prompt targets: <the user's answer to Q3>
  [OUT OF SEQUENCE — if applicable]

  Files to be modified:
    - <path> (sha256: <hash> | new)
    - <path> (sha256: <hash> | new)

  Applicable CLAUDE.md rules:
    - <rule number> — <one-line description>
    - <rule number> — <one-line description>

  Target state:
    <verbatim from user>

  Verification required in the prompt itself:
    - Claude Code must re-check file hashes match before Stage 2
    - Claude Code must cite the CLAUDE.md rules above at the top of its output
    - Claude Code must not modify files outside the "Files to be modified" list

  ── END PREFLIGHT ──

## When to refuse

Refuse to produce a preflight block if any of these are true:

  - You cannot determine the current refactor step from
    agent-improve/ARCHITECTURE.md §15 (file missing, §15 not parseable)
  - agent-improve/CLAUDE.md is missing or unreadable
  - The working tree is dirty AND the user has not acknowledged this
  - Any file to be modified is inside .claude/ AND the user has not
    explicitly stated why (the .claude/ scaffold is governed by §15
    amendments in v2.2, not casual edits)

In a refusal, name each specific reason. Do not proceed with a partial
preflight.

## The preflight is not the prompt

You are producing the preflight BLOCK only. The user takes this block and
pastes it at the top of their Claude Code prompt. The rest of the prompt —
the task description, stages, verification steps, commit message — is the
user's responsibility.
