# -*- coding: utf-8 -*-
"""
The work, organised as Epic > Story > Task / Bug, each tagged with its component.
A STORY is functionality described from the Belt's side; its acceptance is one or more
capability rows (Appendix H IDs). A TASK is a procedure step. A BUG is something built
that is wrong. RANK is the single order in which open stories are worked.

STATUS IS DERIVED where a source owns it, by resolve() below:
  a story is DONE when every one of its rows is green in Appendix H
  a task is DONE when its step is committed (`refactor(arch-v2): commit X.Y`)
The status typed in each entry is kept only where neither source exists — a story
with no rows yet, a task that is not a procedure step, every bug — and the page
labels those HAND. Where a source exists, the typed value can still say WHICH kind
of not-done (todo / blocked); it can never say done.
"""
import derived
# task: (code, title, component, status)   status: done | now | next | todo | blocked
# bug:  (title, component, status, where found)
EPICS = [
 dict(id="E1", title="A Belt can complete Define and close its gate",
      why="The vertical. Done when every story below is done.",
      stories=[
  dict(id="S1", rank=None, status="done", rows=[18], comps=["Coach","Phase state"],
       title="What I tell the coach is kept in the shape the method needs",
       ask="My team is kept as a list of people with roles, my scope as in and out, my SIPOC as six parts.",
       tasks=[("6.48","Check each value against its declared type at capture","Phase state","done"),
              ("S-C05","Put each field's required shape on the response contract","Coach","done")],
       bugs=[]),
  dict(id="S2", rank=None, status="done", rows=[19], comps=["Gate"],
       title="When I have answered everything, a complete gate document can be built",
       ask="The preview shows me a full Define document, not an error.",
       tasks=[("6.20","Derive the Define metric entry at assembly","Gate","done")],
       bugs=[]),
  dict(id="S3", rank=None, status="done", rows=[20,21], comps=["Routes","Storage"],
       title="When I press Submit, my record is saved once and nothing I built is lost",
       ask="Submit saves exactly what the preview showed me; my change log, citations and uploads are still there afterwards.",
       tasks=[("6.42","Submit uses the same assembly as the preview; the save is safe to run twice \u2014 90948de","Routes","done")],
       bugs=[("write_phase_gate replaces the whole record and drops the change log and the uploads",
              "Storage","done","62d7f17")],
       note="Proven on the gate-proof case IMPR-2026-1FF: 13 change-log entries survived the write that used to erase them. Row 21's uploads half is proven by fixture only \u2014 1FF has no uploads. The next gate-proof case should carry one."),
  dict(id="S33", rank=2, status="todo", rows=[25], comps=["Phase state","Coach"],
       title="The baseline and target I give are stored as values Control can compare",
       ask="When I say the error rate is 12.8% and I want 3%, those are kept as 12.8 and 3, percent \u2014 not as a sentence.",
       tasks=[("6.51","A value check at capture for the discrete Define fields, with the shape on the field description as S-C05 did","Phase state","todo")],
       bugs=[("The baseline is stored as a sentence fragment, so Control cannot compare it with the target",
              "Phase state","todo","01e8f8a")],
       note="\u00a763.1 B7: both are discrete because Control parses them for target-versus-actual. Recording them is Define's own job \u2014 the first link of the measurement thread."),
  dict(id="S4", rank=4, status="todo", rows=[14], comps=["UI"],
       title="I can see how far through Define I am",
       ask="The progress bar reads 5 of 12 when I have done five, instead of 0 of 26 forever.",
       tasks=[("10.3","The page reads the v2 field names and counts them","UI","todo")], bugs=[]),
  dict(id="S5", rank=5, status="todo", rows=[7], comps=["Coach"],
       title="When I change an answer, my reason is kept with it",
       ask="If I correct the baseline, the record says why, not just that it changed.",
       tasks=[("6.44","Move the contradiction stop out of middleware into a node","Coach","todo")], bugs=[]),
  dict(id="S6", rank=6, status="todo", rows=[23,34], comps=["Gate","Routes","UI","Storage"],
       title="The human-in-the-loop gate: I review the gate document, approve it, and Define closes",
       ask="The run stops for me at the gate, I approve, and the case moves on with my approval recorded.",
       tasks=[("7.3","The gate pauses, and the pause survives a restart \u2014 the checkpointer holds it","Gate","todo"),
              ("7.7","A route that answers the pause and resumes the run","Routes","todo"),
              ("10.2","The gate screen","UI","blocked")],
       bugs=[], note="HITL. Needs a checkpointer that actually writes \u2014 row 33, proven first in S9. 10.2 is blocked on a design only you can give; until then the approval is proven through the route."),
 ]),
 dict(id="E2", title="The coach teaches the Lean Six Sigma method, not just asks questions",
      why="The difference between a coach and a chat window.",
      stories=[
  dict(id="S7", rank=3, status="todo", rows=[3], comps=["Coach","Skills"],
       title="Every field is explained, shown with an example, asked, and confirmed",
       ask="Before asking for my team, the coach tells me what a Define team is and shows me one.",
       tasks=[("6.46","The coaching script reaches the model every turn, and the turn records it","Skills","todo")],
       bugs=[("The coaching script was fetched zero times in four live turns",
              "Skills","todo","5dc10ff run")],
       note="Also removes the four duplicate shape lines from the skill file: the contract is authoritative. AND: once the script is in front of the model every turn, its worked examples are too \u2014 the \u00a722 guard that an example is never captured as the Belt's data becomes load-bearing, and belongs in this card."),
  dict(id="S8", rank=None, status="todo", rows=[27], comps=["Coach","Skills"],
       title="For every field, I am shown a good example before I am asked",
       ask="Before I write my SIPOC, the coach shows me a finished one and says what makes it good.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.2","Coach","todo")], bugs=[],
       note="\u00a743.2. Mostly delivered by S7's script; the check must also prove the example is never captured as data."),
  dict(id="S34", rank=None, status="todo", rows=[26], comps=["Coach"],
       title="When the coach runs a calculation, I am taught what it means first",
       ask="Before I get a savings figure, I am told what it measures and what the number will mean.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.1","Coach","todo")], bugs=[],
       note="\u00a743.1, the seven-step computation pattern. In Define it applies to calculate_expected_savings."),
  dict(id="S35", rank=None, status="todo", rows=[28], comps=["Coach","UI"],
       title="I always know where I am in the session",
       ask="The coach tells me I am on step 6 of 12, and why we are there.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.3","Coach","todo")], bugs=[],
       note="\u00a743.3, the A\u2192F flow. Stage E is empty for Define, which has no Tier 2. Pairs with S4's progress bar."),
  dict(id="S36", rank=None, status="todo", rows=[29], comps=["Coach","Gate"],
       title="I can see my gate document filling in as I go",
       ask="At any point the coach can show me which of my twelve fields are done and which are missing.",
       tasks=[("\u2014","The check_gate_status tool, bound to Define","Coach","todo")], bugs=[],
       note="\u00a743.4. Define shows one list, not two. The tool does not exist today."),
  dict(id="S37", rank=None, status="todo", rows=[30], comps=["Coach"],
       title="The coach teaches in its own voice and never hands me a link",
       ask="When I ask about the method, I get an explanation, not a URL.",
       tasks=[("\u2014","Rubric criterion and a live-turn check for \u00a743.5","Coach","todo")], bugs=[],
       note="\u00a743.5. Methodology comes from rag_lookup_methodology \u2014 which is empty until S21 fills the knowledge index."),
  dict(id="S38", rank=None, status="todo", rows=[31], comps=["Coach"],
       title="Weak answers are challenged, and the coach never writes my answer for me",
       ask="If I say 'costs are too high', I am asked how much and measured how. The problem statement is mine, not the coach's.",
       tasks=[("\u2014","Rubric criteria and a live-turn check for \u00a743.6","Coach","todo")], bugs=[],
       note="\u00a743.6. 'Not doing the Belt's work' is the one the section calls most easily rationalised away."),
  dict(id="S39", rank=None, status="todo", rows=[32], comps=["Coach","Skills"],
       title="I understand what my metric means, why it matters, and how to read it",
       ask="When my error rate first comes up, the coach explains what it is, why Define cares, and what a good value looks like.",
       tasks=[("\u2014","Bring Define's metric-literacy block to the full \u00a743.7 standard, plus a live-turn check","Skills","todo")], bugs=[],
       note="\u00a743.7 is applied in full to Measure only; Define inherits it 'at its review'. It reads the registry's meaning and never invents one."),
 ]),
 dict(id="E3", title="Every capability is proven, not assumed",
      why="Ten rows almost certainly work today. None of them has a check.",
      stories=[
  dict(id="S9", rank=1, status="todo", rows=[1,2,5,6,8,10,11,12,13,17,33,35], comps=["all"],
       title="Everything that already works is proven by a check",
       ask="A case opens, a turn replies, answers survive, changes are logged, uploads land, calculations and metrics are kept, coherence and grading run, required fields are checked.",
       tasks=[("6.49","Write one check per row, reading the live case; checks only, no code changes","all","todo")],
       bugs=[]),
 ]),
 dict(id="E4", title="Quality, once Define works end to end",
      why="Real, and none of it stops a Belt closing Define.",
      stories=[
  dict(id="S10", rank=None, status="todo", rows=[4], comps=["Phase state"],
       title="The coach asks for the right next field",
       ask="Field two comes only once field one is complete, not after a fixed number of turns.",
       tasks=[("6.45","A real is-this-field-complete predicate","Phase state","todo")], bugs=[]),
  dict(id="S11", rank=None, status="todo", rows=[9], comps=["Coach"],
       title="The coach can read what I upload",
       ask="If I attach a process map, the coach quotes from it.",
       tasks=[("6.43","A tool that returns an uploaded document's text","Coach","todo")], bugs=[]),
  dict(id="S12", rank=None, status="todo", rows=[15,16], comps=["UI"],
       title="I see the coaching properly, and I am told when something fails",
       ask="Explanation, example, prompt and citations appear; a failure says what happened and stays on screen.",
       tasks=[("10.0","Render the four coaching blocks","UI","todo"),
              ("10.4","A readable error when a turn fails","UI","todo")], bugs=[]),
  dict(id="S13", rank=None, status="todo", rows=[22], comps=["Gate"],
       title="The gate grades my document against the method",
       ask="The gate checks constraints and scores the document against the Define rubric, and can send it back.",
       tasks=[("7.1","The validator's result shape","Gate","blocked"),
              ("7.2","Constraints and the phase rubric","Gate","blocked"),
              ("7.8","The gate steps that use the grading","Gate","todo")],
       bugs=[], note="Blocked on two things only you can give: the result-shape ruling and the Define rubric text."),
  dict(id="S14", rank=None, status="todo", rows=[24], comps=["Supervisor","Storage"],
       title="Measure can read what Define decided",
       ask="When I move to Measure, it starts from my approved Define record.",
       tasks=[], bugs=[], note="Needs the graph to own its own boundary, with a version on the write — story S25. Stage 7."),
  dict(id="S31", rank=None, status="todo", rows=[], comps=["UI","Routes"],
       title="I see the coach's reply as it is being written",
       ask="The answer appears word by word instead of after a long silence.",
       tasks=[("10.1","/ask/stream — server-sent events","Routes","todo")], bugs=[]),
  dict(id="S32", rank=None, status="todo", rows=[], comps=["Gate"],
       title="When I am stuck after three attempts, someone is told",
       ask="If the gate keeps sending my work back, a person is brought in rather than the loop going on.",
       tasks=[("7.5","Escalation","Gate","todo")], bugs=[]),
 ]),
 dict(id="E5", title="The other four phases work the way Define does",
      why="The shared machinery is built; each phase needs its fields, its script and its gate. Not before Define is done.",
      stories=[
  dict(id="S15", rank=None, status="todo", rows=[], comps=["Phase state","Skills","Gate"],
       title="Measure coaches its fields in order and closes its gate",
       ask="After Define, I am taken through Measure the same way, and its gate uses tiers.",
       tasks=[("6.14","The skill shape pass for the remaining phases","Skills","blocked"),
              ("7.4","Two tiers of field, and the warning verdict","Gate","todo")], bugs=[],
       note="Measure's ordered field list (§39.2.2) has no owner yet."),
  dict(id="S16", rank=None, status="todo", rows=[], comps=["Phase state","Coach"],
       title="Analyse, Improve and Control do the same",
       ask="Each phase has its own coaching, its own gate, and links back to the metrics Define set.",
       tasks=[("6.10","Analyse's multi-hop retrieval","Coach","blocked")], bugs=[],
       note="Three phase specifications and their field lists (§39.3–§39.5) have no owner yet. Nor do the cross-phase reference dicts (§63.6)."),
  dict(id="S17", rank=None, status="todo", rows=[], comps=["Gate"],
       title="If I change something an earlier gate approved, what depended on it is re-checked",
       ask="Correcting my Define baseline during Measure reopens the parts that used it.",
       tasks=[("7.6","The re-approval cascade","Gate","todo")], bugs=[]),
 ]),
 dict(id="E6", title="The system stays up, and says so when it does not",
      why="Reliability. Stage 8 of the procedure.",
      stories=[
  dict(id="S18", rank=None, status="todo", rows=[], comps=["Routes","Coach","Storage"],
       title="A turn never hangs and never fails silently",
       ask="If something breaks, the turn ends cleanly, tells me, and I can carry on.",
       tasks=[("8.1","Structured errors","Routes","todo"),("8.2","Timeouts and compensating actions","Coach","todo"),
              ("8.3","Circuit breakers and a fallback chain","Coach","todo"),("8.4","Level 3 cache","Coach","blocked"),
              ("8.5","Graceful shutdown","Routes","blocked"),("8.6","Context recovery","Storage","todo")], bugs=[]),
  dict(id="S19", rank=None, status="todo", rows=[], comps=["all"],
       title="Full turn telemetry in LangSmith, for every phase",
       ask="When a Belt says the coach did something odd, we can see exactly what happened in that turn.",
       tasks=[("8.0","Turn telemetry and @traceable","all","todo")], bugs=[],
       note="The basic proof that a Define turn leaves a trace is row 35, in S9. This story is the full telemetry after Define."),
  dict(id="S20", rank=None, status="todo", rows=[], comps=["Storage","Coach"],
       title="My uploads are managed, and the coach has the capacity it needs",
       ask="I can remove a file I uploaded by mistake, and the coach does not run out of model quota mid-project.",
       tasks=[("8.7","delete_blob and the upload lifecycle","Storage","todo"),
              ("9.2","The premium deployment's quota","Coach","blocked")], bugs=[]),
 ]),
 dict(id="E7", title="The coach knows the method and the cases before mine",
      why="Two of the three search indexes are empty.",
      stories=[
  dict(id="S21", rank=None, status="todo", rows=[], comps=["Storage","Coach"],
       title="The coach consults the DMAIC body of knowledge, not only its script",
       ask="When I ask why a SMART statement needs a date, the answer comes from the method, cited.",
       tasks=[("9.0","Build the knowledge index","Storage","blocked")], bugs=[]),
  dict(id="S22", rank=None, status="todo", rows=[], comps=["Storage","Coach"],
       title="The coach can draw on similar past cases",
       ask="If someone ran a scrap project on a similar line, the coach can point me to what they found.",
       tasks=[("9.1","Build the case index","Storage","blocked")], bugs=[]),
 ]),
 dict(id="E8", title="The graph owns its own state",
      why="Framework conformance: the places the tree departs from what LangGraph and Azure document.",
      stories=[
  dict(id="S24", rank=None, status="todo", rows=[], comps=["Storage","Supervisor"],
       title="Nothing I did is lost if the system crashes mid-turn",
       ask="If the server restarts while the coach is answering, I lose at most that one step, and the case resumes.",
       tasks=[("6.47","Durable writes inside a node; persistence loss is never silent","Storage","todo")],
       bugs=[("§16 says the subgraph keeps its state across turns; the tree says it does not",
              "Supervisor","backlog","62d7f17")]),
  dict(id="S25", rank=None, status="todo", rows=[], comps=["Supervisor","Storage"],
       title="Each fact has one writer, and a write cannot overwrite a newer one",
       ask="Two things happening at once on my case can never silently undo each other.",
       tasks=[("—","The graph owns its boundary: call the output mapper, remove the route's write, version the blob write","Supervisor","todo")],
       bugs=[], note="The boundary finding. Required before a second writer exists, which is stage 7."),
  dict(id="S26", rank=None, status="todo", rows=[], comps=["Phase state"],
       title="Accumulating state can never be silently replaced",
       ask="The conversation, the change log and the evidence only ever grow, whatever code touches them.",
       tasks=[("—","Accumulating channels carry reducers","Phase state","todo")], bugs=[]),
 ]),
 dict(id="E9", title="The register tells the truth",
      why="Governance, from the founder's side: the documents can be trusted without re-auditing them.",
      stories=[
  dict(id="S28", rank=None, status="todo", rows=[], comps=["Governance"],
       title="As the founder, every claim in the documents can be checked",
       ask="A count, a citation or a claim about the code is verified by a machine, not by me re-reading it.",
       tasks=[("6.17","The count-check","Governance","todo"),("6.22","The middleware order-check","Governance","blocked"),
              ("6.23","The source-method check","Governance","todo"),("6.24","The drift hook reads the documents","Governance","todo"),
              ("6.28","Fact ownership at the commit gate","Governance","todo"),("6.29","Search index schema ownership","Governance","todo"),
              ("6.30","Commit claims carry a resolvable reference","Governance","todo"),("6.32","An out-of-band landing gets its lane","Governance","todo"),
              ("6.50","The conformance pass: the tree against the framework's documentation","Governance","todo")], bugs=[]),
  dict(id="S29", rank=None, status="todo", rows=[], comps=["Coach"],
       title="As the founder, I can see whether coaching quality is going up or down",
       ask="A fixed set of cases is run on every change and scored.",
       tasks=[("7.0","The evaluation suite","Coach","todo")], bugs=[]),
  dict(id="S30", rank=None, status="todo", rows=[], comps=["Governance"],
       title="As the founder, v1 is gone and the governance is closed",
       ask="One codebase, and a register with nothing open that nobody owns.",
       tasks=[("11.1","Delete v1","Governance","todo"),("11.2","Governance close-out","Governance","todo")], bugs=[]),
 ]),
]

UNSTORIED = [
 ("Project members and sign-in", "a case is opened against a free-text name; the change log and the approval already carry an actor, so identity can be added later. A future epic, not yet written."),
]

# What on the system map belongs to which story. Non-green components by their text,
# unowned markers by section. Owned markers and open steps resolve through the tasks.
CHIP_STORY = [
 ("progress counter","S4"),("errors — a raw exception","S12"),("four coaching blocks","S12"),
 ("/ask/stream","S31"),("POST /gate submit","S3"),("the gate write merges","S3"),("an approve endpoint","S6"),
 ("a route that can answer a pause","S6"),("a gate document screen","S6"),
 ("output mapper","S25"),("phase advancement","S25"),
 ("field/gate decision","S10"),("is this field complete","S10"),("field_log.reason","S5"),
 ("mw2 skills","S7"),("mw8 contradiction","S5"),("read an artefact","S11"),("check_gate_status","S36"),
 ("request_human_approval","S6"),("Define phase rubric","S13"),
 ("writes during a node","S24"),("no connection string","S24"),("resume from a checkpoint","S24"),
 ("whether a checkpoint","S24"),("a version on the write","S25"),("knowledge index","S21"),("case index","S22"),
 ("2b field presence","S13"),("gate_review","S6"),("gate_apply","S3"),("2c constraints","S13"),
 ("2d the phase rubric","S13"),("five phase rubrics","S13"),("Store copy Measure reads","S14"),
 ("compares the tree against the framework","S28"),
]
MARKER_STORY = [
 ("§43.1","S34"),("§43.2","S8"),("§43.3","S35"),("§43.4","S36"),("§43.5","S37"),("§43.6","S38"),("§43.7","S39"),("§39.2 ","S15"),("§39.2.2","S15"),("§39.3 ","S16"),("§39.3.2","S16"),
 ("§39.4 ","S16"),("§39.4.2","S16"),("§39.5 ","S16"),("§39.5.2","S16"),
 ("§63.6","S16"),("§63.9","S2"),("§50.1","S12"),
]

def _not_done(typed):
    return "todo" if typed == "done" else typed


def resolve():
    """Overwrite each story's and task's status from its source; mark what stays typed.

    Returns (register, committed) so the page counts from the same read it rendered from.
    """
    reg, committed = derived.register(), derived.committed_steps()
    for ep in EPICS:
        for st in ep["stories"]:
            if st["rows"]:
                missing = [r for r in st["rows"] if r not in reg]
                if missing:
                    raise RuntimeError("%s cites rows not in Appendix H: %s" % (st["id"], missing))
                st["status"] = "done" if all(reg[r] for r in st["rows"]) else _not_done(st["status"])
                st["src"] = "H"
            else:
                st["src"] = "hand"
            tasks = []
            for code, title, comp, status in st["tasks"]:
                if derived.is_step(code):
                    tasks.append((code, title, comp, "done" if code in committed else _not_done(status), "git"))
                else:
                    tasks.append((code, title, comp, status, "hand"))
            st["tasks"] = tasks
    return reg, committed


def next_story():
    """NEXT is the top-ranked story that is not done. Call after resolve()."""
    ranked = sorted((x for ep in EPICS for x in ep["stories"] if x["rank"] and x["status"] != "done"),
                    key=lambda x: x["rank"])
    return ranked[0] if ranked else None


def step_index():
    idx = {}
    for ep in EPICS:
        for st in ep["stories"]:
            for t in st["tasks"]:
                if t[0] != "—":
                    idx.setdefault(t[0], st["id"])
    return idx

def story_for_chip(text):
    for key, sid in CHIP_STORY:
        if key in text: return sid
    return None

def story_for_marker(section, owner):
    for key, sid in MARKER_STORY:
        if section.startswith(key): return sid
    idx = step_index()
    for part in [x.strip() for x in owner.replace("+", "·").split("·")]:
        if part in idx: return idx[part]
    return None
