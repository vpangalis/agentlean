---
name: upgrade-langchain-stack
description: |
  Re-resolve the LangChain / LangGraph / LangSmith pins against live PyPI and upgrade.
  Use when a floor needs raising, a CVE lands, or a needed API is absent from the
  installed version. Carries the venv trap, the floor rule, the langgraph.prebuilt
  import sweep, the langchain.mcp exclusion, and the verification that must follow —
  against the installed objects rather than the release notes.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash, Edit, WebFetch
version: "1.0"
---

# upgrade-langchain-stack

## The venv trap — read this first

**Use `agent-improve/.venv`, never the repo-root venv.** Probing the wrong one
put a false dependency blocker into two governing documents and left it there
for three weeks. Every command below runs against the pinned interpreter:

```bash
agent-improve/.venv/Scripts/python.exe -m pip list
```

`session-start-context.py` prints the resolved versions at session start. If the
number it shows and the number you are reasoning about differ, stop.

## The floor is the rule; the pin is a fact

`agent-improve/requirements.txt` **owns every pin** (ARCHITECTURE.md §55.4). The
floors are rules and live in the documents:

- `langgraph >= 1.2.6` — 1.2.6, 2026-06-18, carries *"nested subgraph inherits
  parent checkpoint_ns (regression in 1.2.3)"*, the fix the subgraph design
  depends on. Node-level `TimeoutPolicy` and `error_handler` need 1.2+
- `langchain-core >= 1.6.0` — required by `langchain` 1.x as resolved

**Never upgrade to a version written in a document.** Re-resolve against live
PyPI, then repin in `requirements.txt` and nowhere else.

## The sweep, every time

```bash
grep -rn "langgraph.prebuilt" agent-improve/backend/
```

Deprecated in 1.0 to 1.1; the functionality moved to `langchain.agents`. The
package is present as a transitive dependency and that is **not** a violation —
§4.4 bans the import, not the presence.

```bash
grep -rn "langchain.mcp\|langchain_mcp" agent-improve/backend/
```

**`langchain.mcp` is excluded.** It absorbed the standalone MCP adapters in
langchain 1.4.0, so an upgrade can make a banned capability importable without
anyone adding a dependency. §29.1: there is no MCP, and uploaded data is the
only external channel.

## Verify against the installed objects

Invoke `verify-current-version`. Its rule: a documentation page is evidence
ABOUT an API; the installed object IS the API. Two verification errors in this
repository came from reading a page instead, both registered as G-54.

```python
>>> import inspect
>>> inspect.signature(SomeClass.method).parameters
>>> 'attr' in vars(SomeClass)
```

The second line matters: `vars()` asks what the CLASS exposes. Reading a
module's API page and concluding the same thing is how C-3 overwrote a correct
statement.

## After the upgrade

```bash
cd agent-improve && .venv/Scripts/python.exe -m pytest backend/tests -q
.venv/Scripts/python.exe -m mypy .
python .claude/hooks/verify_built.py
```

**mypy earns its place here above all.** langgraph, langchain, langchain-core,
langsmith, langchain-openai and pydantic all ship `py.typed`, so it checks every
call against the REAL installed signatures rather than against `Any`. A renamed
keyword fails there and nowhere else — which is exactly how `retries=` versus
`max_retries=` sat wrong inside the canonical block for months.
