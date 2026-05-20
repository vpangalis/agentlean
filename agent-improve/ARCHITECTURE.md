# Agent Improve â Architecture & Design Document

**Agentlean Platform Â· DMAIC Improvement Agent**
Version 0.1 Â· May 2026
Status: Scaffold created â implementation not yet started

---

## 1. Overview

Agent Improve is the second agent in the Agentlean platform, following Agent Resolve. Where Agent Resolve handles individual maintenance incident resolution using an 8D methodology, Agent Improve guides cross-functional teams through structured DMAIC (Define, Measure, Analyse, Improve, Control) Lean Six Sigma improvement projects.

**Core design principle:** Agent Improve must work for a team with no belt qualification at all. The AI guides the team through every step in plain language â no methodology jargon is presented to team members unless they explicitly ask.

| Property | Value |
|---|---|
| Backend port | 8020 (Agent Resolve: 8010, Agent Flow: 8030) |
| Local path | `C:\Users\mavep\OneDrive - Vassilis Pangalis Valuesims\_DEVELOPMENT\agent-improve` |
| GitHub | `vpangalis/agentlean` â `agent-improve/` folder |
| Stack | Python 3.11 Â· FastAPI Â· LangGraph Â· Azure OpenAI Â· Azure AI Search Â· Azure Blob |
| Venv | Dedicated `agent-improve\.venv` |
| Repo | Monorepo â `agent-improve/` inside `vpangalis/agentlean` |
| Status | Scaffold created Â· implementation not yet started |
| Azure migration | Deferred â stays on `valuesims-*` until all 3 agents built |
| Dockerization | Deferred until all 3 agents built |

---

## 2. Design Principles

### 2.1 Plain language first

| Technical term | Plain language (team-facing) |
|---|---|
| Y variable | The thing you are trying to improve |
| X variables | The factors that might be causing it |
| Data collection plan | Your plan for what data to gather and who gathers it |
| MSA / Gage R&R | Checking that your measurements are reliable |
| Process capability Cpk | How consistently your process performs today |
| Baseline | How bad the problem is right now, in numbers |

### 2.2 Every data request comes with a collection guide
When the Orchestrator asks for data it explains what to collect, the format, and provides a concrete column-by-column example â both in chat and in the data collection table tab.

### 2.3 Source citation is mandatory and transparent
Every AI suggestion carries: agent_origin, index_name, document_id, relevance_summary. Non-negotiable for railway maintenance regulatory traceability.

### 2.4 Phase gates are one-way doors
Once a phase gate passes and the phase record is written to blob, that phase is locked.

### 2.5 Multiple parallel cases from day one
Each case has a unique IMPR-YYYY-NNN number, its own blob file, and its own state.

---

## 3. Agent Architecture

| Agent | Responsibility | When active |
|---|---|---|
| **Orchestrator** | Guides team through DMAIC phases one question at a time. Calls `_reflect()` before returning. Plain language only. | Every team turn |
| **Validator** | Checks team input against Pydantic PhaseInput model. Returns structured pass/fail. | Every submission |
| **Analyst** | Phase-appropriate statistical reasoning: Histogram, Pareto, Fishbone, 5Why, Cpk, regression. | On gate pass or data request |
| **Upload Intelligence** | Classifies uploaded files by type and phase relevance. Validates format. | On every file upload |

### 3.1 Reflection
Every `orchestrate_{phase}.py` contains a private `_reflect()` called before returning. Scoped second LLM call â not a standalone graph node.

### 3.2 Escalation
If gate_attempts reaches GATE_MAX_ATTEMPTS (default 3), routes to `escalate.py`. Sets escalated=True in state. Gate quality bar does not lower.

### 3.3 Graph topology (per phase)
```
orchestrate_{phase} â validate_{phase}
  fail + attempts < max  â loop back to orchestrate_{phase}
  fail + attempts == max â escalate
  pass                   â analyse_{phase} â next phase
```

---

## 4. State Model â ImproveGraphState

| Field | Type | Description |
|---|---|---|
| case_id | str | e.g. IMPR-2024-047 |
| current_phase | str | define / measure / analyse_phase / improve / control |
| current_user | str | Name of active team member |
| phase_inputs | dict | Validated inputs for current phase |
| chat_history | list[dict] | role, user, text, timestamp |
| gate_attempts | int | Resets to 0 on phase advance |
| escalated | bool | UI shows banner when True |
| citations | list[dict] | Source citations this session |
| analyst_output | dict or None | Latest analyst output |
| uploaded_files | list[dict] | name, classification, phase, blob path |
| case_metadata | dict | Title, belt level, team, dates |

---

## 5. Folder Structure

```
agent-improve/
  backend/
    app.py                        FastAPI app, port 8020
    escalate.py                   Cross-phase escalation node
    core/
      state.py                    ImproveGraphState (ONE TypedDict)
      graph.py                    LangGraph graph compilation
      llm.py                      get_llm() factory
      config.py                   Settings, GATE_MAX_ATTEMPTS
      prompts.py                  ALL prompt constants
      citations.py                Source + CitationRecord models
    phases/
      define/                     schema, orchestrate, validate, analyse
      measure/                    schema, orchestrate, validate, analyse
      analyse_phase/              schema, orchestrate, validate, analyse
      improve/                    schema, orchestrate, validate, analyse
      control/                    schema, orchestrate, validate, analyse
    knowledge/
      tools.py                    ALL @tool functions
      retriever.py                Azure Search clients
    storage/
      blob.py                     Case load/save, registry
      models.py                   CaseDocument, PhaseRecord, CitationRecord
    gateway/
      routes.py                   /cases /ask /upload /registry
      schemas.py                  API envelopes only
    upload/
      agent.py                    upload_intelligence node
      classifier.py               File classification
  ui/
    index.html
  CLAUDE.md
  ARCHITECTURE.md
  requirements.txt
  .env.example
  start.ps1
```

---

## 6. Storage

### registry.json
Lightweight index of all cases. Fields: case_id, title, belt_level, leader, current_phase, RAG_status. Used by management dashboard and case search.

### case_{id}.json
Full durable record: metadata, all phase records, conversation history, citations, uploaded file references. Loaded at session start, written on every gate pass.

---

## 7. Azure AI Search Indexes

### New (MVP)
| Index | Content |
|---|---|
| improve_case_index | One doc per case per gate pass â phase summaries, RAG status |
| improve_knowledge_index | DMAIC methodology, GB/BB training, Excel toolkit content |

### Cross-agent read-only (Agent Resolve)
| Tool | Index | Phases |
|---|---|---|
| search_resolve_cases() | case_index_v3 | Analyse, Improve |
| search_resolve_knowledge() | knowledge_index_v2 | All phases |
| search_resolve_evidence() | evidence_index_v1 | Measure |

### Future (Agent Flow)
| Tool | Index |
|---|---|
| search_flow_vsm() | vsm_index |
| search_flow_logs() | process_log_index |

---

## 8. UI Structure

### Four screens
1. **Landing** â New case / Open case / Recent cases list
2. **Case creation** â Case number, title, belt level, team, initial uploads
3. **Case search** â Find by number/title/leader, join by name
4. **Phase workspace** â Five tabs per phase

### Five tabs per phase
1. Phase overview â welcome, DMAIC strip, explanation cards, tool pills, session history
2. AI guide â live Orchestrator conversation, plain language, citation pills, suggestion chips
3. Step-by-step plan â numbered plain-language questions with status indicators
4. Data collection table â four-column table for data collectors
5. Live diagram â phase-specific visual (5W2H map, data flow, fishbone tree, etc.)

### Three upload moments
1. At case creation â background documents
2. During conversation â data files (persistent upload button always visible)
3. At gate submission â evidence files (unlocks when gate criteria met)

---

## 9. Phase Gate Requirements

| Phase | Key requirements |
|---|---|
| Define | All 7 five-W-2H elements Â· baseline metric Â· target Â· process owner Â· charter approved |
| Measure | Y variable Â· data plan with owners Â· sample size confirmed Â· MSA documented Â· data collected |
| Analyse | Root cause identified Â· statistical evidence Â· process owner agrees Â· FMEA updated |
| Improve | Solution selected Â· pilot plan Â· pilot results confirm Â· implementation plan approved |
| Control | Control chart configured Â· monitoring owner Â· response plan Â· training Â· sponsor sign-off |

---

## 10. CLAUDE.md Hard Rules Summary

- ImproveGraphState is the ONLY TypedDict
- One node per file, file name = function name
- Nodes return dict slices only
- get_llm() always â never direct AzureChatOpenAI
- All prompts in core/prompts.py
- All @tool functions in knowledge/tools.py
- All PhaseInput models in phases/{phase}/schema.py
- Source/CitationRecord only in core/citations.py
- CaseDocument only in storage/models.py
- _reflect() in every orchestrate node â no exceptions
- No jargon in team-facing strings
- Every data request includes a concrete column example
- Every cross-agent suggestion includes a visible source citation

---

## 11. Resolved Decisions

| Decision | Resolution |
|---|---|
| Monorepo vs separate repo | Monorepo â agent-improve/ inside vpangalis/agentlean |
| Python venv | Dedicated â agent-improve\.venv |

---

## 12. Out of Scope for MVP

- Agent Flow
- Azure migration (valuesims-* â agentlean-*)
- Dockerization
- search_flow_vsm() active queries
- Management dashboard drill-down
- Email/push notifications
- PDF report export

---

## 13. Change Log

| Date | Version | Change |
|---|---|---|
| May 2026 | 0.1 | Initial architecture. Scaffold created. All decisions resolved. |
