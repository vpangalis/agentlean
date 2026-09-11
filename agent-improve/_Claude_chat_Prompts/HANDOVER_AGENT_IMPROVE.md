# Agent Improve — Build Handover Document
Generated: 2026-05-26 from live repo vpangalis/agentlean

---

## PLATFORM CONTEXT

**Agentlean** — multi-agent AI platform for improvement projects (industry-agnostic).
- Founder/developer: Vassilis Pangalis (vp@agentlean.eu / vp@valuesims.com)
- Monorepo: `vpangalis/agentlean` on GitHub
- Local path: `C:\Users\mavep\OneDrive - Vassilis Pangalis Valuesims\_DEVELOPMENT\AgentLean`
- **Three agents:** Agent Resolve (port 8010, production), Agent Improve (port 8020, in build), Agent Flow (port 8030, future)
- Azure infrastructure stays as `valuesims-*` until all 3 agents are built (names immutable)

---

## AGENT IMPROVE — CURRENT STATE

### Infrastructure
- Local: `C:\Users\mavep\OneDrive - Vassilis Pangalis Valuesims\_DEVELOPMENT\AgentLean\agent-improve`
- Dedicated venv: `agent-improve\.venv` (Python 3.11) — always activate this, NOT the root venv
- Start server: `cd agent-improve && .\.venv\Scripts\Activate.ps1 && uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload`
- Kill orphaned processes: `Get-Process -Name "python","uvicorn" | Stop-Process -Force`
- UI: `http://127.0.0.1:5500/agent-improve/ui/index.html` (Live Server) or `http://127.0.0.1:8020`
- Azure Search indexes: `improve_case_index`, `improve_knowledge_index` (255 docs)
- Azure Blob container: `agent-improve-cases` on `valuesimsdata`
- GitHub token stored in root `.env` as `GITHUB_TOKEN`

### Key .env mappings (different from root)
- `AZURE_BLOB_CONNECTION_STRING` (not AZURE_STORAGE_CONNECTION_STRING)
- `AZURE_SEARCH_API_KEY` (not AZURE_SEARCH_ADMIN_KEY)

---

## BACKEND — COMPLETE AND WORKING

### Architecture: Conversational, blob-based state
State lives in Azure Blob, NOT in LangGraph execution. One node is called per conversational turn.

**Flow per /ask request:**
1. `routes.py` loads case from blob → builds `ImproveGraphState`
2. Calls `orchestrate_{phase}(state)` directly (not full graph)
3. Node runs 3 LLM calls: Extraction → Orchestrator → Reflection (`_reflect()`)
4. `routes.py` syncs `state["chat_history"]` → `case.conversation_history`
5. `routes.py` syncs `state["phase_inputs"][phase]` → `case.phases[phase].structured`
6. `blob_client.save_case(case)`
7. Returns `AskResponse` with `answer`, `captured_fields`, `gate_status`, `suggestion_chips`

### File structure
```
agent-improve/
  backend/
    app.py                          — FastAPI app, static file serving at /
    gateway/
      routes.py                     — ask(), gate(), cases(), registry() endpoints
      schemas.py                    — AskRequest, AskResponse, GateRequest, etc.
    core/
      state.py                      — ImproveGraphState TypedDict
      config.py                     — Azure config
      llm.py                        — LLM client
      graph.py                      — LangGraph graph (11 nodes, @lru_cache)
      prompts.py                    — ALL LLM prompts (ORCHESTRATOR_SYSTEM_BASE, EXTRACTION_MAP, etc.)
      citations.py                  — Citation helpers
    phases/
      define/
        orchestrate.py              — orchestrate_define() — COMPLETE
        validate.py                 — validate_define() — COMPLETE
        schema.py                   — DefinePhaseInput Pydantic model
        analyse.py                  — STUB (pending)
      measure/                      — orchestrate + validate COMPLETE, analyse STUB
      analyse_phase/                — orchestrate + validate COMPLETE, analyse STUB
      improve/                      — orchestrate + validate COMPLETE, analyse STUB
      control/                      — orchestrate + validate COMPLETE, analyse STUB
    storage/
      blob.py                       — BlobClient: load_case, save_case, load_registry
      models.py                     — CaseDocument, PhaseData Pydantic models
    knowledge/
      retriever.py                  — Azure Search retriever
      tools.py                      — 6 @tool functions
    escalate.py                     — Escalation after 3 gate failures
  ui/
    index.html                      — SINGLE FILE UI (all CSS + JS embedded)
  scripts/
    create_indexes.py
    ingest_knowledge.py
    debug_ask.py
```

### Critical bug fixed in routes.py (this session)
AI turns and extracted fields were generated but not written back to blob.
Fix: after `state.update(result)`, routes.py now syncs:
```python
case.conversation_history = state.get("chat_history") or []
for phase_key, phase_data in updated_phase_inputs.items():
    if phase_key in case.phases and phase_data:
        clean = {k: v for k, v in phase_data.items() if not k.startswith("_") and v is not None}
        if clean:
            case.phases[phase_key].structured = clean
blob_client.save_case(case)
```

### Prompts fix (this session)
`EXTRACTION_MAP` templates use `.replace("{conversation}", conversation)` NOT `.format()`.
Python `.format()` treated JSON braces as format placeholders → KeyError.
All 5 orchestrate files fixed to use `.replace()`.

### Orchestrator behaviour fix
Added rule to `ORCHESTRATOR_SYSTEM_BASE`: if team member asks about a tool/methodology
(e.g. "what is 5W2H"), answer briefly in 2-3 sentences then return to current step.
Previously the orchestrator refused all off-topic questions.

---

## UI — SINGLE FILE: `agent-improve/ui/index.html`

### Four screens
1. **Landing** — hero, two action cards, recent cases from GET /registry
2. **Create** — case number (auto), title, dept, date, belt level (3 cards), team, documents
3. **Search** — search by case_id/title/leader, join with name
4. **Workspace** — 3-column grid: left nav (200px), main (flex), right panel (244px)

### Workspace layout
```
topbar (48px)
workspace (grid: 200px | flex | 244px)
  pnav         — DMAIC phase navigator, progress bar
  main         — vtabs + 5 views (overview/chat/steps/diagram/history)
  rpanel       — captured fields, gate checklist, submit button
```

### Tab views
- **overview** — phase header, DMAIC strip, 4 info cards (what AI asks / what gets captured / gate / duration), tool pills, continue button
- **chat** — message list, input container (chips + YOUR REPLY + gate row)
- **steps** — numbered step list, reads from blob structured + lastAsk
- **diagram** — Define: card grid (Option B), other phases: placeholder
- **history** — daily summary cards, expandable, reads from case.conversation_history

### Tool briefing system
Clicking any tool pill opens a dedicated tab with:
- Tool header card (purple background)
- Why you need this now (purple left-border box)
- Filled example card (teal header, grid of Q/A pairs) — STATIC, hardcoded for all 18 tools
- How to complete yours (numbered steps)
- Other tools in this phase
- Start with AI guide button → pre-loads first guided question

All 18 tools across 5 phases have complete `exampleSummary` and `exampleFields` data.

### Chat input container (bottom of chat view)
3 zones in one unified rounded box:
1. `chips-row` — suggestion chips (purple, no label)
2. `reply-box` — "YOUR REPLY" label + textarea + paperclip + send button (purple circle)
3. `gate-row` (outside box) — field count hint + "Submit for gate review" button (purple)

### Right panel
Reads from `S.lastAsk.captured_fields` OR `S.case.phases[phase].structured` (blob).
Shows: CAPTURED FIELDS section, What's needed to move forward (gate status), Submit button.
Updates after every AI response.

### State object (JS global `S`)
```javascript
S = {
  screen: 'landing',        // landing|create|search|workspace
  case: null,               // full CaseDocument from GET /cases/{id}
  user: '',                 // team member name
  phase: 'define',          // current phase
  tab: 'overview',          // current tab
  lastAsk: null,            // last AskResponse from POST /ask
  localChat: [],            // local array of chat turns
  teamMembers: [],          // for case creation
  beltLevel: 'green',
  currentTool: null,        // currently open tool briefing
}
```

### Key JS functions
- `showScreen(id)` — navigate between 4 screens
- `openWorkspace(caseId)` — load case from blob, render workspace
- `selectPhase(phase)` — switch active phase, re-render all tabs
- `selectTab(tab)` — switch tab, sync right panel
- `openToolBriefing(toolName, phase)` — open tool briefing tab
- `sendMessage()` — POST /ask, append turns, update all panels
- `updateRightPanel(resp)` — update right panel from AskResponse
- `renderDiagram()` — re-render live diagram (called after every response)
- `renderSteps()` — update step-by-step from blob + lastAsk
- `renderHistory()` — daily summary cards from case.conversation_history
- `toggleSession(el)` — expand/collapse session card (uses data-sid attribute)

### CSS variables
```css
--brand: #534AB7        /* purple */
--brand-bg: #EEEDFE
--brand-mid: #AFA9EC
--teal: #0F6E56
--teal-bg: #E1F5EE
--teal-mid: #5DCAA5
--green: #1D9E75
--amber: #BA7517
--red: #E24B4A
--blue: #185FA5
--bg: #F1EFE8           /* warm off-white page background */
--surface: #FFFFFF
--surface2: #F8F7F4
--border: #E4E2DC
--text: #1A1917
--text2: #5C5A55
--text3: #99978F
```

### Critical CSS fixes applied this session
- `.tb-card { flex-shrink: 0 }` — `overflow:hidden` on flex items inside column sets `min-height:0` (CSS Flexbox §4.5), causing card bodies to collapse to 0. `flex-shrink:0` prevents this.
- `.view { overflow-y: auto }` — the tab views scroll internally

---

## ACTIVE TEST CASE

**Case ID:** `IMPR-2026-E9D`
**Title:** Reduce Customer complaint rate in call center
**Belt:** Green | **Leader:** Vassilis | **Dept:** Customer Service
**Phase:** define (in progress)
**Conversation:** 12 turns (6 user, 6 AI) as of handover

### Captured fields in blob (define.structured)
```json
{
  "what": "increase in customer complaints",
  "where": "inbound support line, specifically agents handling billing queries",
  "who_affected": "customers calling about billing issues",
  "when": "beginning of February 2026",
  "why_it_matters": "drop in customer satisfaction and financial impact",
  "how_much_baseline": "28 complaints per week",
  "how_goal": 45,              ← WRONG, should be ~20 (target to reduce TO)
  "primary_metric": "customer satisfaction score",
  "primary_metric_unit": "%",
  "process_owner": "Anna Kovac",
  "team_members": "Anna Kovac billing support team of about 12 agents",
  "secondary_metric": "revenue loss due to churn"
}
```

**Note:** `how_goal = 45` is incorrect. Vassilis said 45 is the CURRENT number, target is under 20.
The AI has been told but extraction may need correcting. Vassilis's last message:
"The target is to reduce complaints to under 20 per week within 6 months."

**Vassilis's last reply to AI (turn 13, not yet sent):**
"The sponsor is the Head of Customer Service, Maria Papadaki. The team includes Anna Kovac as team leader, 3 senior billing agents, and 1 data analyst from the BI team."

---

## PENDING WORK (in priority order)

### 1. Complete Define phase gate pass [NEXT]
Continue conversation with case IMPR-2026-E9D.
- Vassilis needs to send the sponsor/team message above
- Then click "Submit for gate review"
- `validate_define()` checks against `DefinePhaseInput` Pydantic model
- If gate passes: `case.current_phase` advances to `measure`, nav updates
- Verify the phase transition works end-to-end

### 2. Fix how_goal extraction
`how_goal = 45` should be `20`. The extraction is storing the current value not the target.
Check `EXTRACTION_DEFINE` prompt in `core/prompts.py` — the `how_goal` field description
may be ambiguous. Should say "the TARGET number to achieve, not the current value".

### 3. Implement analyse.py nodes (Analyst agent)
All 5 `phases/{phase}/analyse.py` files are stubs.
The Analyst runs when: user uploads a data file, or explicitly requests analysis.
Returns `analyst_output` stored in blob, rendered in Live diagram tab.

**Define analyst:** baseline trend confirmation, simple statistics
**Measure analyst:** histogram, Cpk calculation, MSA check
**Analyse analyst:** fishbone generation, Pareto chart, 5Why structuring
**Improve analyst:** impact/effort matrix scoring
**Control analyst:** control chart generation, Cpk monitoring

### 4. Live diagram for Measure/Analyse/Improve/Control phases
Currently `buildMeasureDiagram()` and `buildLockedDiagram()` are placeholders.
Each phase needs its own card grid layout (same Option B pattern as Define).

### 5. Gate pass → phase transition UI
When gate passes, `S.phase` advances and the left nav updates.
Currently: `selectPhase(resp.next_phase)` is called in `submitGateReview()`.
Test this flow when Define gate passes.

### 6. `why_it_matters` extraction quality
The extracted value "drop in customer satisfaction and financial impact" is too vague.
Should capture the actual numbers: "satisfaction score 78%→61%, €35k/month revenue loss".
The extraction prompt needs a stronger instruction to capture specific numbers.

### 7. Session history — field delta per session
Currently shows: date, participants, message counts, first AI question.
Enhancement: show how many fields were captured THAT day (delta from previous day).
Needs: snapshot of structured data per turn saved to blob.

### 8. Step-by-step tab — improve keyword matching
Current matching: `qLow.includes(k)` — fragile for edge cases.
Better: map each step index to a specific field key from DefinePhaseInput.

---

## KNOWN PATTERNS AND DECISIONS

### Two-Claude workflow
- This Claude instance (claude.ai): architecture, decisions, diagnosis, UI design, commit via MCP browser
- Claude Code (Sonnet) in VS Code: file changes, investigations, reports back

### MCP browser tool
- Tab ID: 2092565436 (GitHub tab)
- Token: stored in `window._ghToken` (set at start of session)
- Pattern: `fetch('https://api.github.com/repos/vpangalis/agentlean/contents/{path}', {headers: {'Authorization': `token ${window._ghToken}`}})`
- Push: PUT with `btoa(unescape(encodeURIComponent(content)))` and `sha`

### Commit discipline
- Stage by name (not `git add -A`)
- Message format: `type(agent-improve): description`
- Always include `Co-Authored-By: Claude <noreply@anthropic.com>`

### CSS Flexbox collapse pattern (learned this session)
When a flex item has `overflow:hidden`, its `min-height` silently becomes `0` (spec §4.5).
Fix: always add `flex-shrink:0` to cards/panels inside flex column containers.
This caused the tool briefing card bodies to be invisible despite content being in DOM.

### Server restart after pull
`--reload` flag sometimes doesn't pick up changes. When in doubt:
```powershell
Get-Process -Name "python","uvicorn" | Stop-Process -Force
uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload
```

### DefinePhaseInput required fields (from schema.py)
```python
what, where, when, who_affected, why_it_matters,
how_much_baseline, how_goal, primary_metric, primary_metric_unit,
process_owner, sponsor, belt_level, target_date,
secondary_metric, team_members
```
Gate passes when ALL of these are non-null in structured.
`sponsor` is still missing from the blob — that's why gate hasn't passed yet.

---

## HOW TO START THIS SESSION

1. Open PowerShell, activate venv, start server:
```powershell
cd "C:\Users\mavep\OneDrive - Vassilis Pangalis Valuesims\_DEVELOPMENT\AgentLean\agent-improve"
.\.venv\Scripts\Activate.ps1
git pull origin main --rebase
uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload
```

2. Open browser at `http://127.0.0.1:5500/agent-improve/ui/index.html`

3. Open case `IMPR-2026-E9D` (click it on landing screen, enter name "Vassilis")

4. Go to AI guide tab and send:
"The sponsor is the Head of Customer Service, Maria Papadaki. The team includes Anna Kovac as team leader, 3 senior billing agents, and 1 data analyst from the BI team."

5. After AI responds, click "Submit for gate review" and check if gate passes.

6. Set GitHub token in MCP browser tab console:
```javascript
window._ghToken = '<REDACTED 2026-08-20 — read from env, never paste a PAT into a doc>'
```

> **Security note (2026-08-20):** a live classic PAT was pasted here in
> plaintext. It has been removed from this file, but removing it from disk
> does **not** revoke it. Revoke it at
> `https://github.com/settings/tokens` — the credential stays valid until
> you do. This file is untracked, so the token never entered git history.
